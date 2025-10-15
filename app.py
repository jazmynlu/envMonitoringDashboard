from dash import Dash
from layouts import get_layout
from data_loaders import initialize_dashboard, C_to_F, lux_to_footcandles
from dash import Input, Output, State
import pandas as pd
import plotly.express as px 
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import timedelta, datetime
import psychrolib
import numpy as np
import json
from scipy import integrate
import logging
from logging.handlers import RotatingFileHandler

#%% Adding Logger
app = Dash(__name__)
app.title = "DGG Dashboard"
application = app.server

#%% Setting up error logger
logger = logging.getLogger(__name__)

console_handler = logging.StreamHandler()
rotating_file_handler = RotatingFileHandler('logs/errors.log', maxBytes=2000)

console_handler.setLevel(logging.WARNING)
rotating_file_handler.setLevel(logging.ERROR)

logging_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

console_handler.setFormatter(logging_format)
rotating_file_handler.setFormatter(logging_format)

logger.addHandler(console_handler)
logger.addHandler(rotating_file_handler)

#%% Initializing Dashbaord
dfs, date_config, img_str, cropped_img, init_param = initialize_dashboard(df_filepath = 'setup/df_config.txt', 
                         setdates_filepath = 'setup/set_dates.txt',
                         image_path='galleryInfo/2025 - DGG Exhibition Level Blueprint (LACMA).jpg')

app.layout = get_layout(date_config, img_str, cropped_img, dfs['circle_coords'], dfs['all_coords'], init_param['x_vals'], init_param['y_vals'])

#%% Updates Tabs
@app.callback(
    [Output('tab-map-view-content', 'style'),
     Output('tab-map-daily-view-content', 'style'),
     Output('tab-time-series-content', 'style'),
     Output('tab-ts-single-content', 'style'),
     Output('tab-psychrometric-content', 'style'),
     #Output('tab-curtains-content', 'style'),
     Output('tab-hvac-content', 'style'),
     Output('tab-weather-content', 'style')],
    Input('graph_type', 'value')
)
def display_tab_content(tab):
    return [
        {'display': 'block'} if tab == 'tab-map-view' else {'display': 'none'},
        {'display': 'block'} if tab == 'tab-map-daily-view' else {'display': 'none'},
        {'display': 'block'} if tab == 'tab-time-series' else {'display': 'none'},
        {'display': 'block'} if tab == 'tab-ts-single' else {'display': 'none'},
        {'display': 'block'} if tab == 'tab-psychrometric' else {'display': 'none'},
        #{'display': 'block'} if tab == 'tab-curtains' else {'display': 'none'},
        {'display': 'block'} if tab == 'tab-hvac' else {'display': 'none'},
        {'display': 'block'} if tab == 'tab-weather' else {'display': 'none'}
    ]

#%% Updates units
@app.callback(
    Output('unit-system-switch-label', 'children'),
    Input('unit-system-switch','on'))
def update_units(on):
    if on:
        return ' Metric Units'
    else:
        return ' Imperial Units'

@app.callback(
    Output("slct_dtype_tab-map-daily-view", 'options'),
    Output("slct_dtype_tab-map-daily-view", 'value'),
    Input('unit-system-switch','on'))
def update_daily_map_options(on):
    if on:
        return ["Temperature , °C", "RH , %", "Light , lux"], "Temperature , °C"
    else:
        return ["Temperature , °F", "RH , %", "Light , fc"], "Temperature , °F"
#%% Updating Figure for Tab 1 - Daily DGG Map View
@app.callback(
    Output(component_id='DGG_map', component_property='figure'),
    Input(component_id='slct_dtype_tab-map-view-content', component_property='value'),
    Input(component_id='date_range_tab-map-view-content', component_property='start_date'),
    Input(component_id='date_range_tab-map-view-content', component_property='end_date'),
    Input('unit-system-switch','on'),
    State(component_id='base_fig_store', component_property='data')
)
def update_DGG_map(value, start_date,end_date,on,base_fig_json):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    if on:
        if 'Temperature' in value:
            dff = dfs['all_data_pruned']['Temperature , °C'].copy()
            T_del_title = r'ΔT (°C)'
            T_avg_title = r'Avg. T (°C)'
        elif 'Relative Humidity' in value:
            dff = dfs['all_data_pruned']['RH , %'].copy()
        elif 'Light' in value:
            dff = dfs['all_data_pruned']['Light , lux'].copy()
            L_max_title = 'Max. Light (lux)'
            L_avg_title = 'Avg. Light (lux)'

    else:
        if 'Temperature' in value:
            dff = dfs['all_data_pruned']['Temperature , °F'].copy()
            T_del_title = r'ΔT (°F)'
            T_avg_title = r'Avg. T (°F)'
        elif 'Relative Humidity' in value:
            dff = dfs['all_data_pruned']['RH , %'].copy()
        elif 'Light' in value:
            dff = dfs['all_data_pruned']['Light , fc'].copy()
            L_max_title = 'Max. Light (fc)'
            L_avg_title = 'Avg. Light (fc)'
        
    dff = dff[(dff['Date-Time (PST/PDT)']<end_date)&(dff['Date-Time (PST/PDT)']>start_date)]
    dff['Date'] = dff['Date-Time (PST/PDT)'].dt.date
    fig_dict = json.loads(base_fig_json)
    figure = go.Figure(fig_dict)

    if "Temperature" in value:
        grouped = dff.groupby("Date")
        max_min_temp = (grouped.max()-grouped.min()).drop('Date-Time (PST/PDT)',axis=1)
        average_T = (grouped.mean()).drop('Date-Time (PST/PDT)',axis=1)
        if "Range" in value:
            plot_values=max_min_temp.mean(axis=0)
            color_scale = 'viridis'
            title = T_del_title
        else:
            plot_values=average_T.mean(axis=0)
            color_scale = 'Aggrnyl'
            title = T_avg_title
        sensor_names = plot_values.index
        if on:
            hover_text = [
                f"<b>Sensor:</b> {sensor}<br>"
                f"<b>Avg T:</b> {average_T.mean(axis=0)[sensor]:.2f} °C<br>"
                f"<b>Avg ΔT:</b> {max_min_temp.mean(axis=0)[sensor]:.2f} °C"
                for sensor in sensor_names]
        else:
            hover_text = [
                f"<b>Sensor:</b> {sensor}<br>"
                f"<b>Avg T:</b> {average_T.mean(axis=0)[sensor]:.2f} °F<br>"
                f"<b>Avg ΔT:</b> {max_min_temp.mean(axis=0)[sensor]:.2f} °F"
                for sensor in sensor_names]
        colors = plot_values.replace({np.nan:'#FFFFFF'})
        colorbar=dict(title=title, x=1.05, xanchor = 'left')

            
    elif "Humidity" in value:
        grouped = dff.groupby("Date")
        max_min_dailyRH = (grouped.max()-grouped.min()).drop('Date-Time (PST/PDT)',axis=1)
        average_RH = (grouped.mean()).drop('Date-Time (PST/PDT)',axis=1)
        if "Range" in value:
            plot_values=max_min_dailyRH.mean(axis=0)
            color_scale = 'Cividis'
            title = r'ΔRH (%)'
        else:
            plot_values=average_RH.mean(axis=0)
            color_scale = 'YlGnBu'
            title = r'Avg. RH (%)'
        sensor_names = plot_values.index
        hover_text = [
            f"<b>Sensor:</b> {sensor}<br>"
            f"<b>Avg RH:</b> {average_RH.mean(axis=0)[sensor]:.2f}%<br>"
            f"<b>Avg $ΔRH$:</b> {max_min_dailyRH.mean(axis=0)[sensor]:.2f}%"
            for sensor in sensor_names]
        colors = plot_values.replace({np.nan:'#FFFFFF'})
        colorbar=dict(title=title, x=1.05, xanchor = 'left')

    
    else:
        grouped = dff.groupby("Date")
        max_light = (grouped.max()-grouped.min()).drop('Date-Time (PST/PDT)',axis=1)
        average_light = (grouped.mean()).drop('Date-Time (PST/PDT)',axis=1)
        if "Max" in value:
            plot_values=max_light.mean(axis=0)
            color_scale = 'solar'
            title = L_max_title
        else:
            plot_values = average_light.mean(axis=0)
            color_scale = 'solar'
            title = L_avg_title
        sensor_names = plot_values.index
        if on:
            hover_text = [
                f"<b>Sensor:</b> {sensor}<br>"
                f"<b>Max Light:</b> {max_light.mean(axis=0)[sensor]:.2f} lux<br>"
                f"<b>Avg Light:</b> {average_light.mean(axis=0)[sensor]:.2f} lux"
                for sensor in sensor_names]
        else:
            hover_text = [
                f"<b>Sensor:</b> {sensor}<br>"
                f"<b>Max Light:</b> {max_light.mean(axis=0)[sensor]:.2f} fc<br>"
                f"<b>Avg Light:</b> {average_light.mean(axis=0)[sensor]:.2f} fc"
                for sensor in sensor_names]            
        colors = np.log10(plot_values)
        colors = colors.replace({np.nan:'#FFFFFF'})
        colorbar = dict(title=title, x=1.05, xanchor = 'left',
                        tickvals=np.log10([1,10,100,1000,10000,20000]), #positions in log-space
                        ticktext=[1,10,100,1000,10000,20000] ) #positions in linear space

    figure.data[0].marker.color = colors
    figure.data[0].marker.colorscale = color_scale
    figure.data[0].marker.colorbar = colorbar
    figure.data[0].marker.cauto = True
    figure.data[0].text = hover_text
    figure.data[0].hovertemplate = "%{text}<extra></extra>"
    return figure


#%% Updating Figure for Tab 2 - DGG Map View
@app.callback(
    Output(component_id='DGG_map_tab-map-daily-view', component_property='figure'),
    Input(component_id='date_tab-map-daily-view', component_property = 'date'),
    Input(component_id='slct_dtype_tab-map-daily-view', component_property = 'value'),
    Input(component_id='time_slider_tab-map-daily-view', component_property = 'value'),
    Input('unit-system-switch','on'),
    State(component_id='base_fig_store2', component_property='data')
)
def update_DGG_dailymap(date,value,time,on,base_fig_json):
    datetime_base = datetime.combine(pd.to_datetime(date),datetime.min.time()) #convert datetime at midnight
    target_time = pd.to_datetime(datetime_base+timedelta(minutes = time))
    
    dff = dfs['all_data_pruned'][value].copy()
    try:
        daily_data = dff[dff['Date-Time (PST/PDT)']==target_time].drop(['Date-Time (PST/PDT)'],axis=1).reset_index(drop=True)
    except ValueError:
        logging.error('Time and Date selected out of range')
    sensor_names = daily_data.columns
    fig_dict = json.loads(base_fig_json)
    figure = go.Figure(fig_dict)
    
    if 'Temperature' in value:
        if on:
            figure.data[0].marker.cmin = init_param['min_temp']
            figure.data[0].marker.cmax = init_param['max_temp'] 
            title = 'T (°C)'
            hover_text = [
                 f"<b>Sensor:</b> {sensor}<br>"
                 f"<b>Temp:</b> {daily_data.loc[0,sensor]:.2f}°C<br>"
                 for sensor in sensor_names]
        else:
            figure.data[0].marker.cmin = C_to_F(init_param['min_temp'])
            figure.data[0].marker.cmax = C_to_F(init_param['max_temp'] )
            title = 'T (°F)'
            hover_text = [
                 f"<b>Sensor:</b> {sensor}<br>"
                 f"<b>Temp:</b> {daily_data.loc[0,sensor]:.2f}°F<br>"
                 for sensor in sensor_names]
            
        figure.data[0].marker.colorscale = 'Aggrnyl'
        colors = daily_data.iloc[0,:].copy()
        colors = colors.replace({np.nan:'#FFFFFF'})
        colorbar = dict(title=title, x=1.05, xanchor = 'left')
    elif 'RH' in value:
        figure.data[0].marker.colorscale = 'YlGnBu'
        figure.data[0].marker.cmin = init_param['min_RH']
        figure.data[0].marker.cmax = init_param['max_RH']
        title = 'RH (%)'
        hover_text = [
            f"<b>Sensor:</b> {sensor}<br>"
            f"<b>RH:</b> {daily_data.loc[0,sensor]:.2f}%<br>"
            for sensor in sensor_names]
        colors = daily_data.iloc[0,:].copy()
        colors = colors.replace({np.nan:'#FFFFFF'})
        colorbar = dict(title=title, x=1.05, xanchor = 'left')
    else:
        if on:
            hover_text = [
                f"<b>Sensor:</b> {sensor}<br>"
                f"<b>Light:</b> {daily_data.loc[0,sensor]:.2f} lux<br>"
                for sensor in sensor_names]
            title = 'Light (lux)'
        else:
            hover_text = [
                f"<b>Sensor:</b> {sensor}<br>"
                f"<b>Light:</b> {daily_data.loc[0,sensor]:.2f} fc<br>"
                for sensor in sensor_names]
            title = 'Light (fc)'
        colors = np.log10(daily_data.iloc[0,:].replace(0, 1e-6))
        colors = colors.replace({np.nan:'#FFFFFF'})
        figure.data[0].marker.colorscale = 'solar'
        figure.data[0].marker.cmin = 0
        figure.data[0].marker.cmax = np.log10(init_param['max_lt'])
        
        colorbar = dict(title=title, x=1.05, xanchor = 'left',
                        tickvals=np.log10([1,10,100,1000,10000,20000,50000]), #positions in log-space
                        ticktext=[1,10,100,1000,10000,20000,50000]) #positions in linear space

    figure.data[0].marker.color = colors
    figure.data[0].marker.colorbar = colorbar
    figure.data[0].text = hover_text
    figure.data[0].hovertemplate = "%{text}<extra></extra>"
    return figure

#%% Connects DGG Map in first two tabs to time series selection in tab 3
@app.callback(
    Output(component_id = 'sensor_select_tab-timeseries', component_property='value'),
    Input(component_id = 'DGG_map', component_property='selectedData'),
    Input(component_id = 'DGG_map_tab-map-daily-view', component_property = 'selectedData'))
def select_sensors_on_map_ts(selected_map1, selected_map2):
    if not selected_map1 and not selected_map2:
        return ['30 S']
    if not selected_map1:
        selected_map1 = {"points":[]}
    if not selected_map2:
        selected_map2 = {"points":[]}
    if len(selected_map1) > len(selected_map2):
        return [pt["customdata"][0] for pt in selected_map1["points"]]
    else:
        return [pt["customdata"][0] for pt in selected_map2["points"]]
    
    
#%% Connects DGG Map in first two tabs to time series selection in tab 4
@app.callback(
    Output(component_id = 'sensor_select_tab-ts-single', component_property='value'),
    Input(component_id = 'DGG_map', component_property='selectedData'),
    Input(component_id = 'DGG_map_tab-map-daily-view', component_property = 'selectedData'))
def select_sensors_on_map_ts_single(selected_map1, selected_map2):
    if not selected_map1 or "points" not in selected_map1:
        selected_map1 = {"points": []}
    if not selected_map2 or "points" not in selected_map2:
        selected_map2 = {"points": []}
    if not selected_map1["points"] and not selected_map2["points"]:
        return "30 S"
    if selected_map1["points"] and not selected_map2["points"]:
        return selected_map1["points"][0]["customdata"][0]
    if selected_map2["points"] and not selected_map1["points"]:
        return selected_map2["points"][0]["customdata"][0]
    if selected_map1["points"] and selected_map2["points"]:
        return selected_map1["points"][0]["customdata"][0]
#%% Connects DGG Map in first two tabs to time series selection in tab 5
@app.callback(
    Output(component_id = 'sensor_select_tab-psychrometric', component_property='value'),
    Input(component_id = 'DGG_map', component_property='selectedData'),
    Input(component_id = 'DGG_map_tab-map-daily-view', component_property = 'selectedData'))
def select_sensors_on_map_psychro(selected_map1, selected_map2):
    if not selected_map1 and not selected_map2:
        return ['30 S']
    if not selected_map1:
        selected_map1 = {"points":[]}
    if not selected_map2:
        selected_map2 = {"points":[]}
    if len(selected_map1) > len(selected_map2):
        return [pt["customdata"][0] for pt in selected_map1["points"]]
    else:
        return [pt["customdata"][0] for pt in selected_map2["points"]]
#%% Connects DGG Map in first two tabs to time series selection in tab 6
@app.callback(
    Output(component_id = 'sensor_select_tab-hvac', component_property='value'),
    Input(component_id = 'DGG_map', component_property='selectedData'),
    Input(component_id = 'DGG_map_tab-map-daily-view', component_property = 'selectedData'))
def select_sensors_on_map_hvac(selected_map1, selected_map2):
    if not selected_map1 or "points" not in selected_map1:
        selected_map1 = {"points": []}
    if not selected_map2 or "points" not in selected_map2:
        selected_map2 = {"points": []}
    if not selected_map1["points"] and not selected_map2["points"]:
        return "30 S"
    if selected_map1["points"] and not selected_map2["points"]:
        return selected_map1["points"][0]["customdata"][0]
    if selected_map2["points"] and not selected_map1["points"]:
        return selected_map2["points"][0]["customdata"][0]
    if selected_map1["points"] and selected_map2["points"]:
        return selected_map1["points"][0]["customdata"][0]
    
#%% Updating Figure for Tab 3 - Timeseries
@app.callback(
    [Output(component_id='DGG_timeseries_temp', component_property='figure'),
    Output(component_id='DGG_timeseries_rh', component_property='figure'),
    Output(component_id='DGG_timeseries_dp', component_property='figure'),
    Output(component_id='DGG_timeseries_light', component_property='figure')],
     [Input(component_id='date_range_tab-timeseries', component_property='start_date'),
     Input(component_id='date_range_tab-timeseries', component_property='end_date'),
     Input(component_id='sensor_select_tab-timeseries', component_property='value'),
     Input('unit-system-switch','on'),
     Input(component_id='sensor_movement-timeseries', component_property='on')]
)
def update_DGG_timeseries(start_date,end_date,sensors, units, switch):
    figures = {}
    if switch:
        dtypes = dfs['all_data_pruned']
    else:
        dtypes = dfs['all_data']
 
    for d in dtypes.keys():
        dff = dtypes[d].copy()
        dff = dff[(dff['Date-Time (PST/PDT)']<end_date)&(dff['Date-Time (PST/PDT)']>start_date)]

        figures[d]=px.line(        
            data_frame = dff,
            x='Date-Time (PST/PDT)',
            y=sensors,
           labels = {
               'Date-Time (PST/PDT)': 'Date',
               'value': d,       
               'variable': 'Sensor'
            })
        x_shade = dff['Date-Time (PST/PDT)'].values
        n = len(x_shade)
        if units:
            if 'T' in d:
                y_shade_bottom = np.full(n, 16)
                y_shade_top = np.full(n, 25)
            elif 'RH' in d:
                y_shade_bottom = np.full(n, 40)
                y_shade_top = np.full(n, 60)
            elif 'Dew Point' in d:
                y_shade_bottom = np.full(n, 2.4)
                y_shade_top = np.full(n, 16.7)
            elif 'Light' in d:
                y_shade_bottom = np.full(n, 0)
                y_shade_top = np.full(n, 250)
            figures[d].add_trace(go.Scatter(
                    x=np.concatenate([x_shade, x_shade[::-1]]),
                    y=np.concatenate([y_shade_bottom, y_shade_top[::-1]]),
                    fill='toself',
                    fillcolor='skyblue',
                    line=dict(color='skyblue'),
                    opacity=0.3,
                    name='Bizot Standard',
                    hoverinfo='skip',
                    showlegend=True
                ))
            figures[d].update_layout(
                xaxis=dict(
                    title_text=""
                ),
                margin=dict(l=40,r=20,t=5,b=5)
            )
            
        else:
            if 'T' in d:
                y_shade_bottom = np.full(n, 60.8)
                y_shade_top = np.full(n, 77)
            elif 'RH' in d:
                y_shade_bottom = np.full(n, 40)
                y_shade_top = np.full(n, 60)
            elif 'Dew Point' in d:
                y_shade_bottom = np.full(n, 36.32)
                y_shade_top = np.full(n, 62.06)
            elif 'Light' in d:
                y_shade_bottom = np.full(n, 0)
                y_shade_top = np.full(n, 23.2258)
            figures[d].add_trace(go.Scatter(
                    x=np.concatenate([x_shade, x_shade[::-1]]),
                    y=np.concatenate([y_shade_bottom, y_shade_top[::-1]]),
                    fill='toself',
                    fillcolor='skyblue',
                    line=dict(color='skyblue'),
                    opacity=0.3,
                    name='Bizot Standard',
                    hoverinfo='skip',
                    showlegend=True
                ))
            figures[d].update_layout(
                xaxis=dict(
                    title_text=""
                ),
                margin=dict(l=40,r=20,t=5,b=5)
            )
    if units:
        return figures['Temperature , °C'], figures['RH , %'], figures['Dew Point , °C'], figures['Light , lux']
    else:
        return figures['Temperature , °F'], figures['RH , %'], figures['Dew Point , °F'], figures['Light , fc']
#%% Updating Figure for Tab 4 (Time Series Single)
@app.callback(
     [Output(component_id='DGG_timeseries_single', component_property='figure'),
      Output(component_id='DGG_rh_range', component_property='figure'),      
      Output(component_id='DGG_light_plt',component_property='figure'),],
     [Input(component_id='date_range_tab-ts-single', component_property='start_date'),
     Input(component_id='date_range_tab-ts-single', component_property='end_date'),
     Input(component_id='sensor_select_tab-ts-single', component_property='value'),
     Input('unit-system-switch','on'),
     Input(component_id='sensor_movement-ts-single', component_property='on')]
)
def update_DGG_timeseries_single(start_date,end_date,sensor, on, switch):
    if switch:
        dtypes = dfs['all_data_pruned']
    else:
        dtypes = dfs['all_data']
        
    dates = pd.DataFrame(dtypes['RH , %']['Date-Time (PST/PDT)'])
    dates = dates[(dates['Date-Time (PST/PDT)']<np.datetime64(end_date))&(dates['Date-Time (PST/PDT)']>np.datetime64(start_date))]

    single_df = dates.copy()
    if on:
        units = ['Temperature , °C', 'RH , %', 'Dew Point , °C', 'Light , lux']
        left_yaxis = 'Temperature and Dew Point (°C)'
        for d in units:
            dff = dtypes[d][['Date-Time (PST/PDT)',sensor]].rename(columns={sensor:d})
            single_df=single_df.merge(dff, how='inner',on='Date-Time (PST/PDT)')
        integral_result = integrate.trapezoid(single_df['Light , lux'], dx=0.25)
        value = f'Cumulative Light Exposure between {start_date} and {end_date} is {integral_result:.2f} lux-hours'
    else:
        units = ['Temperature , °F', 'RH , %', 'Dew Point , °F', 'Light , fc']
        left_yaxis= 'Temperature and Dew Point (°F)'
        for d in units:
            dff = dtypes[d][['Date-Time (PST/PDT)',sensor]].rename(columns={sensor:d})
            single_df=single_df.merge(dff, how='inner',on='Date-Time (PST/PDT)')
        integral_result = integrate.trapezoid(single_df['Light , fc'], dx=0.25)
        value = f'Cumulative Light Exposure between {start_date} and {end_date} is {integral_result:.2f} fc-hours'
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    
    fig.add_trace(
        go.Scatter(
            x=single_df["Date-Time (PST/PDT)"],
            y=single_df[units[0]],
            name=units[0],
            line=dict(color = 'firebrick')
        ),
        secondary_y=False
    )
    fig.add_trace(
        go.Scatter(
            x=single_df["Date-Time (PST/PDT)"],
            y=single_df[units[2]],
            name=units[2],
            line = dict(color = 'steelblue')
        ),
        secondary_y=False
    )
    fig.add_trace(
        go.Scatter(
            x=single_df["Date-Time (PST/PDT)"],
            y=single_df[units[1]],
            name="Relative Humidity , %",
            line = dict(color = 'limegreen')
        ),
        secondary_y=True
    )

    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(
        title_text=left_yaxis,
        color = 'black',
        range = [0,80],
        secondary_y=False,
        automargin=True
    )
    fig.update_yaxes(
        title_text="Relative Humidity (%)",
        color = 'limegreen',
        range=[0,80],
        secondary_y=True,
        automargin=True
    )
    fig.update_layout(
        hovermode="x unified" ,  # nice combined hover
        xaxis=dict(
            title_text=""
        ),
        margin=dict(l=40,r=20,t=5,b=5)
    )
    
    rh_24_hour_average = dates.merge(dfs['moving_24hour_average']['RH , %'], how='inner',on='Date-Time (PST/PDT)')
    rh_24_hour_range = dates.merge(dfs['moving_24hour_range']['RH , %'], how='inner',on='Date-Time (PST/PDT)')
    
    fig2 = go.Figure()
    
    fig2.add_trace(go.Scatter(
        x=single_df['Date-Time (PST/PDT)'],
        y=single_df['RH , %'],
        name = 'RH , %',
        mode='lines',
        line=dict(color='grey')
    ))
    fig2.add_trace(
        go.Scatter(
            x=rh_24_hour_average["Date-Time (PST/PDT)"],
            y=rh_24_hour_average[sensor],
            name="24 hr average",
            line = dict(color = 'purple', dash='dash')
        )
    )
    fig2.add_trace(
        go.Scatter(
            x=rh_24_hour_range["Date-Time (PST/PDT)"],
            y=rh_24_hour_range[sensor],
            name="24 hr range",
            line = dict(color = 'black')
        )
    )
    date_values = dates['Date-Time (PST/PDT)'].values
    n = len(date_values)
    y_shade_bottom_1 = np.full(n, 40)
    y_shade_top_1 = np.full(n, 60)
    fig2.add_trace(go.Scatter(
            x=np.concatenate([date_values, date_values[::-1]]),
            y=np.concatenate([y_shade_bottom_1, y_shade_top_1[::-1]]),
            fill='toself',
            fillcolor='skyblue',
            line=dict(color='skyblue'),
            opacity=0.3,
            name='Bizot Standard',
            hoverinfo='skip',
            showlegend=True
        ))
    y_shade_bottom_2 = np.full(n, 0)
    y_shade_top_2 = np.full(n, 10)
    fig2.add_trace(go.Scatter(
            x=np.concatenate([date_values, date_values[::-1]]),
            y=np.concatenate([y_shade_bottom_2, y_shade_top_2[::-1]]),
            fill='toself',
            fillcolor='skyblue',
            line=dict(color='skyblue'),
            opacity=0.3,
            name='Daily Fluctuation Range',
            hoverinfo='skip',
            showlegend=True
        ))    
    fig2.update_layout(
        hovermode="x unified",   # nice combined hover
        xaxis=dict(
            title_text=""
        ),
        margin=dict(l=40,r=275,t=5,b=5),
    )
    fig2.update_xaxes(title_text="Date")
    fig2.update_yaxes(title_text="Relative Humidity (%)",
                      automargin=True)
    
    fig3 = go.Figure()
    
    fig3.add_trace(go.Scatter(
        x=single_df['Date-Time (PST/PDT)'],
        y=single_df[units[3]],
        name = units[3],
        mode='lines',
        line=dict(color='orange')
    ))
    fig3.update_xaxes(title_text="Date")
    fig3.update_yaxes(title_text=units[3],
                      automargin=True)
    fig3.update_layout(title = dict(text=value, x=0.5, xanchor = 'center'))
    return fig, fig2, fig3

#%% Updating Figure for Tab 5 - Psychrometric View
@app.callback(
    Output(component_id='DGG_psycrhometric', component_property='figure'),
    [Input(component_id='sensor_select_tab-psychrometric', component_property='value'),
     Input(component_id='date_range_tab-psychrometric', component_property='start_date'),
     Input(component_id='date_range_tab-psychrometric', component_property='end_date'),
     Input('unit-system-switch','on')]
)
def update_DGG_psychrometric(sensors, start_date, end_date, on):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    rh_data = dfs['all_data']['RH , %'].copy()
    if on:
        psychrolib.SetUnitSystem(psychrolib.SI)
        temp_data = dfs['all_data']['Temperature , °C'].copy()
        pressure = init_param['pressure']
        t_array = init_param['t_array']
        t_shade = init_param['t_shade']
        xaxis_title='Dry-bulb Temperature (°C)'
        yaxis_title="Humidity Ratio [kg₍H₂O₎/kg₍dry air₎]"
        xrange = [0,45]
        hovertemplate=(
            "Temp: %{x:.2f} °C<br>"
            "HumRatio: %{y:.2f} lb/lb<br>"
            "RH: %{customdata[0]:.1f}%<br>"
            "Time: %{customdata[1]}<extra></extra>"
        )
    else:
        psychrolib.SetUnitSystem(psychrolib.IP)
        temp_data = dfs['all_data']['Temperature , °F'].copy()
        pressure = init_param['pressure']/6895
        t_array = C_to_F(init_param['t_array'])
        t_shade = C_to_F(init_param['t_shade'])
        xaxis_title='Dry-bulb Temperature (°F)'
        yaxis_title="Humidity Ratio [lb₍H₂O₎/lb₍dry air₎]"
        xrange=[32,113]
        hovertemplate=(
            "Temp: %{x:.2f} °F<br>"
            "HumRatio: %{y:.2f} lb/lb<br>"
            "RH: %{customdata[0]:.1f}%<br>"
            "Time: %{customdata[1]}<extra></extra>"
        )
    
    rh_data = rh_data[(rh_data['Date-Time (PST/PDT)'] < end_date) & (rh_data['Date-Time (PST/PDT)'] > start_date)]
    temp_data = temp_data[(temp_data['Date-Time (PST/PDT)'] < end_date) & (temp_data['Date-Time (PST/PDT)'] > start_date)]
    time_data = temp_data['Date-Time (PST/PDT)']

    figure = go.Figure()

    for rh in init_param['rh_array']:
        hr_array = [psychrolib.GetHumRatioFromRelHum(t, rh, pressure) for t in t_array]
        figure.add_trace(go.Scatter(
            x=t_array,
            y=hr_array,
            mode='lines',
            line=dict(width=0.5, color='grey'),
            hoverinfo='skip',
            showlegend=False
        ))
    for rh, (x, y, text) in init_param['labels'].items():
        if not on:
            x=C_to_F(x)
        figure.add_annotation(
            x=x,
            y=y/1000,
            text=text,
            showarrow=False,
            font=dict(size=10),
            xanchor='left'
        )
    figure.add_trace(go.Scatter(
        x=np.concatenate([t_shade, t_shade[::-1]]),
        y=np.concatenate([init_param['hr_40'], init_param['hr_60'][::-1]]),
        fill='toself',
        fillcolor='skyblue',
        line=dict(color='skyblue'),
        opacity=0.4,
        hoverinfo='skip',
        name='Bizot Standard'
    ))
    # Axis and layout settings
    figure.update_layout(
        title='Psychrometric Chart',
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        xaxis=dict(range=xrange,showline=True, mirror=True, linecolor='black'),
        yaxis=dict(range=[0, .030],showline=True, mirror=True, linecolor='black'),
        plot_bgcolor='white'
    )

    for sensor in sensors:
        temp_array = np.array(temp_data[sensor])
        relh_array = np.array(rh_data[sensor])/100  # relative humidity fraction
        time_array = np.datetime_as_string(time_data, unit='s')
        time_array = np.char.replace(time_array, 'T', ' ')

    
        # vectorized computation of humid ratio
        humidr_array = np.array([psychrolib.GetHumRatioFromRelHum(t, rh, pressure) for t, rh in zip(temp_array, relh_array)])
    
        # vectorized customdata
        custom_post = np.column_stack((relh_array*100, time_array))
    
        figure.add_trace(go.Scatter(
            x=temp_array,
            y=humidr_array,
            mode='markers',
            name=sensor,
            customdata=custom_post,
            hovertemplate=hovertemplate
        ))
    return figure

#%% Updating Figure for Tab 6 - HVAC Psychrometric Comp
@app.callback(
    Output(component_id='HVAC_comp', component_property='figure'),
    Input(component_id='sensor_select_tab-hvac', component_property='value'),
    Input('unit-system-switch','on')
)
def update_HVAC_comp(sensor, on):

    rh_data_pre = dfs['preHVAC']['RH , %'][sensor]/100
    time_pre = dfs['preHVAC']['RH , %']['Date-Time (PST/PDT)'].copy()
    time_pre[np.isnan(rh_data_pre)]=pd.NaT
    
    rh_data_post = dfs['postHVAC']['RH , %'][sensor]/100
    time_post = dfs['postHVAC']['RH , %']['Date-Time (PST/PDT)'].copy()
    time_post[np.isnan(rh_data_post)]=pd.NaT
    
    truncated_weather = dfs['weather_data'].iloc[::15]
    rh_data_wunderground = truncated_weather['Humidity']/100
    

    time_wunderground = truncated_weather['Date-Time']
    
    if on:
        psychrolib.SetUnitSystem(psychrolib.SI)
        temp_data_pre = dfs['preHVAC']['Temperature , °C'][sensor]
        temp_data_post = dfs['postHVAC']['Temperature , °C'][sensor]
        temp_data_wunderground = truncated_weather['Temperature']
        pressure = init_param['pressure']
        t_array = init_param['t_array']
        t_shade = init_param['t_shade']
        xaxis_title='Dry-bulb Temperature (°C)'
        yaxis_title="Humidity Ratio [kg₍H₂O₎/kg₍dry air₎]"
        xrange=[0, 45]
        hovertemplate=(
            "Temp: %{x:.2f} °C<br>"
            "HumRatio: %{y:.2f} kg/kg<br>"
            "RH: %{customdata[0]:.1f}%<br>"
            "Time: %{customdata[1]}<extra></extra>"
        )
    else:
        psychrolib.SetUnitSystem(psychrolib.IP)
        temp_data_pre = C_to_F(dfs['preHVAC']['Temperature , °C'][sensor])
        temp_data_post = dfs['postHVAC']['Temperature , °F'][sensor]
        temp_data_wunderground=C_to_F(truncated_weather['Temperature'])
        pressure = init_param['pressure']/6895
        t_array = C_to_F(init_param['t_array'])
        t_shade = C_to_F(init_param['t_shade'])
        xaxis_title='Dry-bulb Temperature (°F)'
        yaxis_title="Humidity Ratio [lb₍H₂O₎/lb₍dry air₎]"
        xrange=[32,113]
        hovertemplate=(
            "Temp: %{x:.2f} °F<br>"
            "HumRatio: %{y:.2f} lb/lb<br>"
            "RH: %{customdata[0]:.1f}%<br>"
            "Time: %{customdata[1]}<extra></extra>"
        )
    

    figure = go.Figure()

    # Creates psychrolib template
    for rh in init_param['rh_array']:
        hr_array = [psychrolib.GetHumRatioFromRelHum(t, rh, pressure) for t in t_array]
        figure.add_trace(go.Scatter(
            x=t_array,
            y=hr_array,
            mode='lines',
            line=dict(width=0.5, color='grey'),
            hoverinfo='skip',
            showlegend=False
        ))
    
    # Adds the relative humidity labels to psychrolib template
    for rh, (x, y, text) in init_param['labels'].items():
        if not on:
            x = C_to_F(x)
        figure.add_annotation(
            x=x,
            y=y/1000,
            text=text,
            showarrow=False,
            font=dict(size=10),
            xanchor='left'
        )
    # Plots Bizot Standard
    figure.add_trace(go.Scatter(
        x=np.concatenate([t_shade, t_shade[::-1]]),
        y=np.concatenate([init_param['hr_40'], init_param['hr_60'][::-1]]),
        fill='toself',
        fillcolor='skyblue',
        line=dict(color='skyblue'),
        opacity=0.4,
        hoverinfo='skip',
        name='Bizot Standard'
    ))
    # Axis and layout settings
    figure.update_layout(
        title='Psychrometric Chart',
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        xaxis=dict(range=xrange,showline=True, linecolor='black',mirror=True),
        yaxis=dict(range=[0, .030],showline=True, linecolor='black',mirror=True),
        plot_bgcolor='white'
    )
    
    # Outside Hobo
    wunderground_humidr_array = []
    custom_post = []
    for t, rh, dt in zip(temp_data_wunderground, rh_data_wunderground, time_wunderground):
        hum_ratio = psychrolib.GetHumRatioFromRelHum(t, rh, pressure)
        wunderground_humidr_array.append(hum_ratio)
        custom_post.append([rh * 100, str(dt)])

    figure.add_trace(go.Scatter(
        x=temp_data_wunderground,
        y=wunderground_humidr_array,
        mode='markers',
        name='KCALOSAN1069 Weather Station',
        customdata=custom_post,
        hovertemplate=hovertemplate
    ))
    
    # Pre-HVAC
    pre_humidr_array = []
    custom_pre = []
    for t, rh, dt in zip(temp_data_pre, rh_data_pre, time_pre):
        hum_ratio = psychrolib.GetHumRatioFromRelHum(t, rh, pressure)
        pre_humidr_array.append(hum_ratio)
        custom_pre.append([rh * 100, str(dt)])  

    figure.add_trace(go.Scatter(
        x=temp_data_pre,
        y=pre_humidr_array,
        mode='markers',
        name='pre-HVAC',
        customdata=custom_pre,  # plain Python list of lists
        hovertemplate=hovertemplate
    ))

    # Post-HVAC
    post_humidr_array = []
    custom_post = []
    for t, rh, dt in zip(temp_data_post, rh_data_post, time_post):
        hum_ratio = psychrolib.GetHumRatioFromRelHum(t, rh, pressure)
        post_humidr_array.append(hum_ratio)
        custom_post.append([rh * 100, str(dt)])

    figure.add_trace(go.Scatter(
        x=temp_data_post,
        y=post_humidr_array,
        mode='markers',
        name='post-HVAC',
        customdata=custom_post,
        hovertemplate=hovertemplate
    ))
    
    return figure

#%% Updating Figure for Tab 7 - Outside Weather
@app.callback(
    [Output(component_id='T_DP_RH', component_property='figure'),
     Output(component_id='solar_radiation', component_property='figure'),
     Output(component_id='wind_speed', component_property='figure'),
     Output(component_id='precipitation', component_property='figure'),
     Output(component_id='pressure', component_property='figure')],
     [Input(component_id='date_range_tab-weather', component_property='start_date'),
     Input(component_id='date_range_tab-weather', component_property='end_date'),
     Input('unit-system-switch','on')]
)
def update_weather_tab(start_date, end_date, on):
    weather_data_df = dfs['weather_data'][(dfs['weather_data']['Date-Time']<end_date)&(dfs['weather_data']['Date-Time']>start_date)]
    figure_T = make_subplots(specs=[[{"secondary_y": True}]])
    
    if on:
        # Left axis = Temperature
        figure_T.add_trace(
            go.Scatter(
                x=weather_data_df["Date-Time"],
                y=weather_data_df['Temperature'],
                name="Air Temperature (°C)",
                line=dict(color = 'firebrick')
            ),
            secondary_y=False
        )
        figure_T.add_trace(
            go.Scatter(
                x=weather_data_df["Date-Time"],
                y=weather_data_df['Dew Point'],
                name="Dew Point (°C)",
                line = dict(color = 'steelblue')
            ),
            secondary_y=False
        )
        figure_T.update_yaxes(title_text="Temperature and Dew Point (°C)",
                              range=[0,100])
    else:
        # Left axis = Temperature
        figure_T.add_trace(
            go.Scatter(
                x=weather_data_df["Date-Time"],
                y=C_to_F(weather_data_df['Temperature']),
                name="Air Temperature (°F)",
                line=dict(color = 'firebrick')
            ),
            secondary_y=False
        )
        figure_T.add_trace(
            go.Scatter(
                x=weather_data_df["Date-Time"],
                y=C_to_F(weather_data_df['Dew Point']),
                name="Dew Point (°F)",
                line = dict(color = 'steelblue')
            ),
            secondary_y=False
        )
        figure_T.update_yaxes(title_text="Temperature and Dew Point (°C)",
                              range=[20,120])

    # Right axis = RH
    figure_T.add_trace(
        go.Scatter(
            x=weather_data_df["Date-Time"],
            y=weather_data_df['Humidity'],
            name="Relative Humidity (%)",
            line = dict(color = 'limegreen')
        ),
        secondary_y=True
    )

    # X-axis
    figure_T.update_xaxes(title_text="Date")


    
    figure_T.update_yaxes(
        title_text="Relative Humidity (%)",
        color = 'limegreen',
        range=[0,100],
        secondary_y=True
    )

    figure_T.update_layout(hovermode="x unified",
                           legend=dict(
                               orientation = "h",
                               yanchor = "bottom",
                               y=1.02,
                               xanchor = "right",
                               x=1),
                           margin=dict(l=40,r=20,t=5,b=5)
                           )
    
    figure_solar_radiation = make_subplots(specs=[[{"secondary_y": True}]])
    figure_solar_radiation.add_trace(go.Scatter(
        x = weather_data_df['Date-Time'],
        y = weather_data_df['Solar Radiation'],
        mode = 'lines',
        name = 'Solar Radiation (watts/m2)',
        line = dict(color = 'gold')),
        secondary_y=False)
    figure_solar_radiation.update_yaxes(
        title_text = 'Solar Radiation (W/m²)',
        color = 'gold')

    figure_solar_radiation.add_trace(go.Scatter(
        x = weather_data_df['Date-Time'],
        y = weather_data_df['UV Index'],
        mode = 'lines',
       line = dict(color = 'darkviolet'),
        name = 'UV Index'),
        secondary_y=True)
    figure_solar_radiation.update_yaxes(
        title_text = 'UV Index', 
        color = 'darkviolet',
        secondary_y=True)
    figure_solar_radiation.update_layout(hovermode="x unified",
                           legend=dict(
                               orientation = "h",
                               yanchor = "bottom",
                               y=1.02,
                               xanchor = "right",
                               x=1),
                           margin=dict(l=40,r=20,t=5,b=5))
    
    figure_wind_speed = make_subplots(specs=[[{"secondary_y": True}]])
    figure_wind_speed.add_trace(go.Scatter(
            x = weather_data_df["Date-Time"],
            y = weather_data_df['Wind Gust'],
            mode = 'markers',
            name = 'Wind Gust (mph)'
        ), secondary_y = False)
    figure_wind_speed.add_trace(go.Scatter(
            x = weather_data_df["Date-Time"],
            y = weather_data_df['Wind Speed'],
            mode = 'lines',
            name = 'Wind Speed (mph)'
        ), secondary_y=False)
    figure_wind_speed.add_trace(go.Scatter(
        x = weather_data_df['Date-Time'],
        y = weather_data_df['Wind Direction'],
        mode = 'markers',
        name = 'Wind Direction',
        marker = dict(
            symbol = 'star',
            color = 'goldenrod')
        ), secondary_y=True)
    figure_wind_speed.update_yaxes(title_text='Wind Direction',
                                    categoryorder = 'array',
                                    categoryarray=['North','NNE', 'NE','ENE','East',
                                                     'ESE','SE','SSE','South','SSW','SW',
                                                     'West','WNW','NW','NNW'],
                                    color = 'goldenrod',
                                    secondary_y=True)
    figure_wind_speed.update_yaxes(title_text='Wind (mph)', secondary_y=False)
    figure_wind_speed.update_layout(hovermode="x unified",
                           legend=dict(
                               orientation = "h",
                               yanchor = "bottom",
                               y=1.02,
                               xanchor = "right",
                               x=1),
                           margin=dict(l=40,r=20,t=5,b=5))


    figure_precipitation = go.Figure()
    figure_precipitation.add_trace(go.Scatter(
        x = weather_data_df['Date-Time'],
        y = weather_data_df['Precip. Rate'],
        mode = 'lines',
        name = 'Precip. Rate (in)'))
    
    figure_precipitation.add_trace(go.Scatter(
        x = weather_data_df['Date-Time'],
        y = weather_data_df['Precip. Accum'],
        mode = 'lines',
        name = 'Precip. Accum (in)'))
    figure_precipitation.update_layout(hovermode="x unified",
                           legend=dict(
                               orientation = "h",
                               yanchor = "bottom",
                               y=1.02,
                               xanchor = "right",
                               x=1),
                           margin=dict(l=40,r=20,t=5,b=5))    
    figure_precipitation.update_yaxes(
        title_text="Precipitation (in.)",
        range=[0,3])
                                   
    figure_pressure = go.Figure()
    figure_pressure.add_trace(go.Scatter(
        x = weather_data_df['Date-Time'],
        y = weather_data_df['Pressure'],
        mode = 'lines',
        name = 'Pressure (inHg)'))
    figure_pressure.update_yaxes(
        title_text = 'Pressure (inHg)')
    figure_pressure.update_layout(hovermode="x unified",
                           margin=dict(l=40,r=20,t=5,b=5)) 
    
    return figure_T, figure_solar_radiation, figure_wind_speed, figure_precipitation, figure_pressure, 

#%%
if __name__ == '__main__':
    app.run(debug=True,use_reloader=True, port=7080) #local development
    #application.run(host='0.0.0.0', port='8080')
