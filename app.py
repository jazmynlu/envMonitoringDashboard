# -- Loading Packages ---------------------------------------------------------------------------------
import pandas as pd
import plotly.express as px 
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, callback, State
import pickle
from datetime import date, timedelta, datetime
import psychrolib
import numpy as np
from PIL import Image
import base64
import io
import json

app = Dash(__name__)

print('Welcome to the David Geffen Gallery HOBO Environmental Monitoring Dashboard!')

# -- Import and clean data (importing csv into pandas)-------------------------------------------------

data_display = input('Enter 0 for before HVAC data, 1 for after HVAC data: ')

print ('Loading Data...')

# Organizing Data into dataframes
dtypes = {'Temperature , °C':pd.DataFrame({'Date-Time (PST/PDT)':[]}), 
          'RH , %':pd.DataFrame({'Date-Time (PST/PDT)':[]}), 
          'Light , lux':pd.DataFrame({'Date-Time (PST/PDT)':[]})}

# Set date ranges here!
if data_display == '1':
    with open('Data/postHVACdata_08082025.pkl', 'rb') as file:
        dtypes = pickle.load(file)
    fmin_date_allowed=date(2025, 7, 30)
    fmax_date_allowed=date(2025, 8, 6)
    finitial_visible_month=date(2025, 8, 4)
    fdate=date(2025, 8, 4)
    fstart_date=date(2025, 8, 4)
    fend_date=date(2025, 8, 7)
elif data_display == '0':
    with open('Data/preHVACdata.pkl','rb') as file:
        dtypes = pickle.load(file)
    fmin_date_allowed=date(2025, 1, 8)
    fmax_date_allowed=date(2025, 6, 10)
    fdate = date(2025,3,26)
    finitial_visible_month=date(2025, 3,26)
    fstart_date=date(2025, 3, 26)
    fend_date=date(2025, 4, 1)

flattened_df = pd.concat(dtypes.values(), ignore_index=True)
flattened_df = [df.assign(source=key) for key,df in dtypes.items()]

max_temp = dtypes['Temperature , °C'].iloc[:,1:].max().max()
min_temp = dtypes['Temperature , °C'].iloc[:,1:].min().min()
max_RH = dtypes['RH , %'].iloc[:,1:].max().max()
min_RH = dtypes['RH , %'].iloc[:,1:].min().min()
max_lt = dtypes['Light , lux'].iloc[:,1:].max().max()
min_lt = dtypes['Light , lux'].iloc[:,1:].min().min()
#Coordinates for map
with open('galleryInfo/DGG_coords.pkl', 'rb') as f: 
    circle_coords = pickle.load(f)

# Prepare data for Map plotting
x_vals = []
y_vals = []

for i in circle_coords.keys():
    x_vals.append(circle_coords[i][0])
    y_vals.append(circle_coords[i][1])

# Prepare data for psychrometric calculations
psychrolib.SetUnitSystem(psychrolib.SI)
pressure = 101325

t_array = np.arange(4, 45, 0.1)
rh_array = np.arange(0, 1.1, 0.1)

labels = {
    0.0: (37, 0.5, '0% RH'),
    0.2: (37, 8, '20% RH'),
    0.4: (37, 17, '40% RH'),
    0.6: (35, 23, '60% RH'),
    0.8: (33, 27, '80% RH'),
    1.0: (30, 28.5, '100% RH')
}

t_shade = np.arange(16, 25.1, 0.1)
hr_40 = [psychrolib.GetHumRatioFromRelHum(t, 0.4, pressure) * 1000 for t in t_shade]
hr_60 = [psychrolib.GetHumRatioFromRelHum(t, 0.6, pressure) * 1000 for t in t_shade]

# Load Image of Map
print('Loading Images...')
image_path = 'galleryInfo/2025 - DGG Exhibition Level Blueprint (LACMA).jpg'
Image.MAX_IMAGE_PIXELS = None
img = Image.open(image_path)

# Crop the image
crop_box = (3000, 1000, 14000, 7500)
cropped_img = img.crop(crop_box)
# Resize image to smaller width while keeping aspect ratio
target_width = 2000
target_height = int(target_width * cropped_img.height / cropped_img.width)
resized_img = cropped_img.resize((target_width, target_height), Image.Resampling.LANCZOS)

# Convert resized PIL image to numpy array for Plotly
resized_array = np.array(resized_img)

# Convert numpy image to base64 string for Plotly
buffered = io.BytesIO()
resized_img.save(buffered, format="PNG")
img_str = "data:image/png;base64," + base64.b64encode(buffered.getvalue()).decode()

print('Done!')
print('Starting App...')

def create_base_fig(img_str):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=x_vals,
        y=y_vals,
        mode='markers',
        marker=dict(color='red', size=10),
        name='Overlay Points'
    ))

    fig.update_layout(
        images=[dict(
            source=img_str,
            xref="x",
            yref="y",
            x=0,
            y=0,
            sizex=cropped_img.width,
            sizey=cropped_img.height,
            sizing="stretch",
            opacity=1.0,
            layer="below"
        )],
        xaxis=dict(
            range=[0, cropped_img.width],
            scaleanchor="y",
            scaleratio=1,
            visible=False
        ),
        yaxis=dict(
            range=[cropped_img.height, 0],
            visible=False
        ),
        margin=dict(l=0, r=0, t=0, b=0)
    )
    return fig

# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div([
    html.Div(
        className="app-header",
        children=[html.Div('David Geffen Gallery HOBO Environmental Monitoring Dashboard', className='app-header--title')]
    ),
    dcc.Tabs(id="graph_type", value='tab-1', 
        parent_className = 'custom-tabs',
        className='custom-tabs-container',
        children=[
            dcc.Tab(label='DGG Map View', value='tab-1',className = 'custom_tab',
            selected_className='custom-tab--selected'),
            dcc.Tab(label = "Daily DGG Map View", value = 'tab-2',className = 'custom_tab',
            selected_className='custom-tab--selected'),
            dcc.Tab(label='Time Series', value='tab-3',className = 'custom_tab',
            selected_className='custom-tab--selected'),
            dcc.Tab(label='Psychrometric View', value='tab-4',className = 'custom_tab',
            selected_className='custom-tab--selected')
        ]
    ),
    # Render all tab content here, but hide/show them dynamically
    html.Div([
        html.Div(id='tab-1-content', children=[
            dcc.Store(id = 'base_fig_store', data=create_base_fig(img_str).to_json()),
            html.Div(children=[
                dcc.DatePickerRange(
                    id='date_range_tab1',
                    min_date_allowed=fmin_date_allowed,
                    max_date_allowed=fmax_date_allowed,
                    initial_visible_month=finitial_visible_month,
                    start_date=fstart_date,
                    end_date=fend_date),
                dcc.Dropdown(id="slct_dtype_tab1",
                            options=["Daily Max - Min: Temperature (C)", "Daily Average: Temperature (C)", 
                                    "Daily Max - Min: Relative Humidity (%)", "Daily Average: Relative Humidity (%)",
                                    "Daily Max: Light (lux)", "Daily Average: Light (lux)"],
                            value="Daily Max - Min: Temperature (C)",
                            style = {'width':'75%', 
                                     'height':'50px',     
                                     'color':'darkblue',
                                     'fontSize': '20px', 
                                     'fontWeight':'bold'})
                ],
                style={'display':'flex', 'flexDirection':'row', 'gap':'20px', 'margin':'0 auto', 'width':'100%'}
            ),
            dcc.Graph(id='DGG_map',
                config={'displayModeBar': True,  'responsive': True, 'autosizable': True},
                style = { 'margin':'0 auto', 'width':'75%', 'pad':'20px'})
            ], style={'display': 'block'}),  # tab 1 is visible initially

        html.Div(id='tab-2-content', children=[
            dcc.Store(id = 'base_fig_store2', data=create_base_fig(img_str).to_json()),
            html.Div(children=[
                dcc.DatePickerSingle(
                    id='date_tab2',
                    min_date_allowed=fmin_date_allowed,
                    max_date_allowed=fmax_date_allowed,
                    initial_visible_month=finitial_visible_month,
                    date=fdate),
                dcc.Dropdown(id="slct_dtype_tab2",
                            options=["Temperature , °C", "RH , %", "Light , lux"],
                            value="Temperature , °C",
                            style = {'width':'75%', 
                                     'height':'50px',     
                                     'color':'darkblue',
                                     'fontSize': '20px', 
                                     'fontWeight':'bold'})],              
                style={'display':'flex', 'flexDirection':'row', 'gap':'20px', 'margin':'0 auto', 'width':'100%'}),
            html.Div(
                dcc.Slider(
                    id='time_slider_tab2',
                    min=0,
                    max=1439,  # total minutes in a day
                    step=15,
                    value=0, 
                    marks={i*60: f"{i:02d}:00" for i in range(0, 24)}),  # hourly labels),
            style = {'width':'75%','margin':'0 auto'}),
            html.Div(children=[
            dcc.Graph(id='DGG_map_tab2',
                config={'displayModeBar': True,  'responsive': True, 'autosizable': True},
                style = { 'margin':'0 auto', 'width':'75%', 'pad':'20px'})]),

            ], style={'display': 'none'}),  # hidden initially
                  
        html.Div(id='tab-3-content', children=[
            html.Div(children=[
                dcc.DatePickerRange(
                    id='date_range_tab3',
                    min_date_allowed=fmin_date_allowed,
                    max_date_allowed=fmax_date_allowed,
                    initial_visible_month=finitial_visible_month,
                    start_date=fstart_date,
                    end_date=fend_date),
                dcc.Dropdown(
                    list(circle_coords.keys()),
                    ['30 S'],
                    id='sensor_select_tab3',
                    multi=True,
                    style={'width': "40%",
                           'height':'50px',     
                            'color':'darkblue',
                            'fontSize': '20px', 
                            'fontWeight':'bold'})],
                style={'display':'flex', 'flexDirection':'row',
                       'gap':'20px', 'margin':'0 auto', 'width':'100%'}    
                ),
            dcc.Graph(id='DGG_timeseries_temp', figure={}),
            dcc.Graph(id='DGG_timeseries_rh', figure={}),
            dcc.Graph(id='DGG_timeseries_light', figure={})], 
        style={'display': 'none'}),  # hidden initially

        html.Div(id='tab-4-content', children=[
            html.Div(children=[

            dcc.DatePickerRange(
                id='date_range_tab4',
                min_date_allowed=fmin_date_allowed,
                max_date_allowed=fmax_date_allowed,
                initial_visible_month=finitial_visible_month,
                start_date=fstart_date,
                end_date=fend_date),
            dcc.Dropdown(
                list(circle_coords.keys()),
                ['30 S'],
                id='sensor_select_tab4',
                multi=True,
                style={'width': "40%",
                       'height':'50px',     
                        'color':'darkblue',
                        'fontSize': '20px', 
                        'fontWeight':'bold'})],
            style={'display':'flex', 'flexDirection':'row'}    
            ),
            dcc.Graph(id='DGG_psycrhometric', figure={}, style = { 'margin':'0 auto', 'width':'75%', 'pad':'20px'}),
        ], style={'display': 'none'})
    ])
])

@callback(
    [Output('tab-1-content', 'style'),
     Output('tab-2-content', 'style'),
     Output('tab-3-content', 'style'),
     Output('tab-4-content', 'style')],
    Input('graph_type', 'value')
)
def display_tab_content(tab):
    return [
        {'display': 'block'} if tab == 'tab-1' else {'display': 'none'},
        {'display': 'block'} if tab == 'tab-2' else {'display': 'none'},
        {'display': 'block'} if tab == 'tab-3' else {'display': 'none'},
        {'display': 'block'} if tab == 'tab-4' else {'display': 'none'}
    ]

## Updating Figure for Tab 1
@app.callback(
    Output(component_id='DGG_map', component_property='figure'),
    Input(component_id='slct_dtype_tab1', component_property='value'),
    Input(component_id='date_range_tab1', component_property='start_date'),
    Input(component_id='date_range_tab1', component_property='end_date'),
    State(component_id='base_fig_store', component_property='data')
)
def update_DGG_map(value, start_date,end_date,base_fig_json):
    print(f'Data type: {value}')
    print(f'Dates selected: {start_date, end_date}')
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    if 'Temperature' in value:
        dff = dtypes['Temperature , °C'].copy()
    elif 'Relative Humidity' in value:
        dff = dtypes['RH , %'].copy()
    elif 'Light' in value:
        dff = dtypes['Light , lux'].copy()
    dff = dff[(dff['Date-Time (PST/PDT)']<end_date)&(dff['Date-Time (PST/PDT)']>start_date)]
    dff['Date'] = dff['Date-Time (PST/PDT)'].dt.date
    all_dates = dff['Date'].unique()
    daily_data = [dff[dff['Date'] == d] for d in all_dates]

    fig_dict = json.loads(base_fig_json)
    figure = go.Figure(fig_dict)

    if "Temperature" in value:
        max_min_temp = pd.DataFrame()
        average_T = pd.DataFrame()
        for d in daily_data:
            d = d.drop(['Date-Time (PST/PDT)','Date'],axis=1)
            max_min_temp = pd.concat([max_min_temp, d.max()-d.min()],axis=1)
            average_T = pd.concat([average_T,d.mean()],axis=1)
        if "Daily Max - Min" in value:
            plot_values=max_min_temp.mean(axis=1)
            color_scale = 'viridis'
            title = r'ΔT (°C)'
        else:
            plot_values=average_T.mean(axis=1)
            color_scale = 'Aggrnyl'
            title = r'Avg. T (°C)'
        sensor_names = plot_values.index
        hover_text = [
            f"<b>Sensor:</b> {sensor}<br>"
            f"<b>Avg T:</b> {average_T.mean(axis=1)[sensor]:.2f} °C<br>"
            f"<b>Avg ΔT:</b> {max_min_temp.mean(axis=1)[sensor]:.2f} °C"
            for sensor in sensor_names]
        colors = plot_values.replace({np.nan:'#FFFFFF'})
        colorbar=dict(title=title, x=1.05, xanchor = 'left')

            
    elif "Humidity" in value:
        max_min_dailyRH = pd.DataFrame()
        average_RH = pd.DataFrame()
        for d in daily_data:
            d = d.drop(['Date-Time (PST/PDT)','Date'],axis=1)
            max_min_dailyRH = pd.concat([max_min_dailyRH, d.max()-d.min()],axis=1)
            average_RH = pd.concat([average_RH,d.mean()],axis=1)
        if "Daily Max - Min" in value:
            plot_values=max_min_dailyRH.mean(axis=1)
            color_scale = 'Cividis'
            title = r'ΔRH (%)'
        else:
            plot_values=average_RH.mean(axis=1)
            color_scale = 'YlGnBu'
            title = r'Avg. RH (%)'
        sensor_names = plot_values.index
        hover_text = [
            f"<b>Sensor:</b> {sensor}<br>"
            f"<b>Avg RH:</b> {average_RH.mean(axis=1)[sensor]:.2f}%<br>"
            f"<b>Avg $ΔRH$:</b> {max_min_dailyRH.mean(axis=1)[sensor]:.2f}%"
            for sensor in sensor_names]
        colors = plot_values.replace({np.nan:'#FFFFFF'})
        colorbar=dict(title=title, x=1.05, xanchor = 'left')

    
    else:
        max_light = pd.DataFrame()
        average_light = pd.DataFrame()
        for d in daily_data:
             d = d.drop(['Date-Time (PST/PDT)','Date'],axis=1)
             max_light = pd.concat([max_light,d.max()],axis=1)
             average_light = pd.concat([average_light,d.mean()],axis=1)
        if "Daily Max" in value:
            plot_values=max_light.mean(axis=1)
            color_scale = 'solar'
            title = 'Max Light (lux)'
        else:
            plot_values = average_light.mean(axis=1)
            color_scale = 'solar'
            title = 'Avg. Light (lux)'
        sensor_names = plot_values.index
        hover_text = [
            f"<b>Sensor:</b> {sensor}<br>"
            f"<b>Max Light:</b> {max_light.mean(axis=1)[sensor]:.2f} lux<br>"
            f"<b>Avg Light:</b> {average_light.mean(axis=1)[sensor]:.2f} lux"
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


## Updating Figure for Tab 2
@app.callback(
    Output(component_id='DGG_map_tab2', component_property='figure'),
    Input(component_id='date_tab2', component_property = 'date'),
    Input(component_id='slct_dtype_tab2', component_property = 'value'),
    Input(component_id='time_slider_tab2', component_property = 'value'),
    State(component_id='base_fig_store2', component_property='data')
)
def update_DGG_dailymap(date,value,time,base_fig_json):
    datetime_base = datetime.combine(pd.to_datetime(date),datetime.min.time()) #convert datetime at midnight
    target_time = pd.to_datetime(datetime_base+timedelta(minutes = time))
    
    dff = dtypes[value].copy()
        
    daily_data = dff[dff['Date-Time (PST/PDT)']==target_time].drop(['Date-Time (PST/PDT)'],axis=1).reset_index(drop=True)
    sensor_names = daily_data.columns
    fig_dict = json.loads(base_fig_json)
    figure = go.Figure(fig_dict)
    
    if 'Temperature' in value:
        figure.data[0].marker.colorscale = 'Aggrnyl'
        figure.data[0].marker.cmin = min_temp
        figure.data[0].marker.cmax = max_temp
        title = 'T (°C)'
        hover_text = [
             f"<b>Sensor:</b> {sensor}<br>"
             f"<b>Temp:</b> {daily_data.loc[0,sensor]:.2f}°C<br>"
             for sensor in sensor_names]
        colors = daily_data.iloc[0,:].copy()
        colors = colors.replace({np.nan:'#FFFFFF'})
        colorbar = dict(title=title, x=1.05, xanchor = 'left')
    elif 'RH' in value:
        figure.data[0].marker.colorscale = 'YlGnBu'
        figure.data[0].marker.cmin = min_RH
        figure.data[0].marker.cmax = max_RH
        title = 'RH (%)'
        hover_text = [
            f"<b>Sensor:</b> {sensor}<br>"
            f"<b>RH:</b> {daily_data.loc[0,sensor]:.2f}%<br>"
            for sensor in sensor_names]
        colors = daily_data.iloc[0,:].copy()
        colors = colors.replace({np.nan:'#FFFFFF'})
        colorbar = dict(title=title, x=1.05, xanchor = 'left')
    else:
        colors = np.log10(daily_data.iloc[0,:].replace(0, 1e-6))
        colors = colors.replace({np.nan:'#FFFFFF'})
        figure.data[0].marker.colorscale = 'solar'
        figure.data[0].marker.cmin = 0
        figure.data[0].marker.cmax = np.log10(max_lt)
        hover_text = [
            f"<b>Sensor:</b> {sensor}<br>"
            f"<b>Light:</b> {daily_data.loc[0,sensor]:.2f} lux<br>"
            for sensor in sensor_names]
        title = 'Light (lux)'
        
        colorbar = dict(title=title, x=1.05, xanchor = 'left',
                        tickvals=np.log10([1,10,100,1000,10000,20000,50000]), #positions in log-space
                        ticktext=[1,10,100,1000,10000,20000,50000]) #positions in linear space

    figure.data[0].marker.color = colors
    figure.data[0].marker.colorbar = colorbar
    figure.data[0].text = hover_text
    figure.data[0].hovertemplate = "%{text}<extra></extra>"
    return figure

## Updating Figure for Tab 3
@app.callback(
    [Output(component_id='DGG_timeseries_temp', component_property='figure'),
    Output(component_id='DGG_timeseries_rh', component_property='figure'),
    Output(component_id='DGG_timeseries_light', component_property='figure')],
     [Input(component_id='date_range_tab3', component_property='start_date'),
     Input(component_id='date_range_tab3', component_property='end_date'),
     Input(component_id='sensor_select_tab3', component_property='value')]
)
def update_DGG_timeseries(start_date,end_date,sensors):
    figures = {}
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
        if 'T' in d:
            y_shade_bottom = np.full(n, 16)
            y_shade_top = np.full(n, 25)
        elif 'RH' in d:
            y_shade_bottom = np.full(n, 40)
            y_shade_top = np.full(n, 60)
        else:
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
            
    return figures['Temperature , °C'], figures['RH , %'], figures['Light , lux']

## Updating Figure for Tab 4
@app.callback(
    Output(component_id='DGG_psycrhometric', component_property='figure'),
    [Input(component_id='sensor_select_tab4', component_property='value'),
     Input(component_id='date_range_tab4', component_property='start_date'),
     Input(component_id='date_range_tab4', component_property='end_date')]
)
def update_DGG_psychrometric(sensors, start_date, end_date):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    rh_data = dtypes['RH , %'].copy()
    temp_data = dtypes['Temperature , °C'].copy()
    rh_data = rh_data[(rh_data['Date-Time (PST/PDT)'] < end_date) & (rh_data['Date-Time (PST/PDT)'] > start_date)]
    temp_data = temp_data[(temp_data['Date-Time (PST/PDT)'] < end_date) & (temp_data['Date-Time (PST/PDT)'] > start_date)]

    figure = go.Figure()

    for rh in rh_array:
        hr_array = [psychrolib.GetHumRatioFromRelHum(t, rh, pressure) * 1000 for t in t_array]
        figure.add_trace(go.Scatter(
            x=t_array,
            y=hr_array,
            mode='lines',
            line=dict(width=0.5, color='grey'),
            hoverinfo='skip',
            showlegend=False
        ))
    for rh, (x, y, text) in labels.items():
        figure.add_annotation(
            x=x,
            y=y,
            text=text,
            showarrow=False,
            font=dict(size=10),
            xanchor='left'
        )
    figure.add_trace(go.Scatter(
        x=np.concatenate([t_shade, t_shade[::-1]]),
        y=np.concatenate([hr_40, hr_60[::-1]]),
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
        xaxis_title='Dry-bulb Temperature (°C)',
        yaxis_title="Humidity Ratio [g₍H₂O₎/kg₍dry air₎]",
        xaxis=dict(range=[0, 45]),
        yaxis=dict(range=[0, 30]),
        plot_bgcolor='white'
    )

    for sensor in sensors:
        temp_array = temp_data[sensor]
        relh_array = rh_data[sensor]/100
        humidr_array = []
        for t,rh in zip(temp_array, relh_array):
            humidr_array.append(psychrolib.GetHumRatioFromRelHum(t, rh, pressure)*1000)
        figure.add_trace(go.Scatter(
            x=temp_array,
            y=humidr_array,
            mode='markers',
            name = sensor
        )) 
    return figure

if __name__ == '__main__':
    app.run(debug=True,use_reloader=False, port=7080)
