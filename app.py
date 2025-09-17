# -- Loading Packages ---------------------------------------------------------------------------------
import pandas as pd
import plotly.express as px 
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, dcc, html, Input, Output, callback, State
import pickle
from datetime import date, timedelta, datetime
import psychrolib
import numpy as np
from PIL import Image
import base64
import io
import json
import dash_daq as daq
import logging
from logging.handlers import RotatingFileHandler
import os
import sys
import dash_auth


#%% Dashboard Authentication


# Keep this out of source code repository - save in a file or a database
# VALID_USERNAME_PASSWORD_PAIRS = {
#     'User': 'ConservationRocks'
# }

app = Dash(__name__)
# auth = dash_auth.BasicAuth(
#     app,
#     list(VALID_USERNAME_PASSWORD_PAIRS.items())
# )

print('Welcome to the David Geffen Gallery HOBO Environmental Monitoring Dashboard!')

#%% Import and clean data (importing csv into pandas)
data_display = input('Enter 0 for before HVAC data, 1 for after HVAC data: ')
#data_display = '1'

print ('Loading Data...')

# Organizing Data into dataframes
dtypes = {'Temperature , °C':pd.DataFrame({'Date-Time (PST/PDT)':[]}), 
          'RH , %':pd.DataFrame({'Date-Time (PST/PDT)':[]}), 
          'Dew Point , °C':pd.DataFrame({'Date-Time (PST/PDT)':[]}),
          'Light , lux':pd.DataFrame({'Date-Time (PST/PDT)':[]})}

with open('Data/postHVACdata_09152025.pkl', 'rb') as file:
    postHVAC = pickle.load(file)
with open("Data/moving_24hour_average_09152025.pkl",'rb') as file:
    moving_24hour_average = pickle.load(file)  
with open("Data/moving_24hour_range_09152025.pkl",'rb') as file:
    moving_24hour_range = pickle.load(file) 
with open("Data/moving_7day_average_09152025.pkl",'rb') as file:
    moving_7day_average = pickle.load(file) 
with open("Data/moving_7day_range_09152025.pkl",'rb') as file:
    moving_7day_range = pickle.load(file) 
with open('Data/preHVACdata.pkl','rb') as file:
    preHVAC = pickle.load(file)
with open('Data/wunderground_09152025.pkl', 'rb') as file:
    weather_data = pickle.load(file)
with open('Data/outside_PJA.pkl', 'rb') as file:
    outside_PJA = pickle.load(file)
    
# Set date ranges here!
if data_display == '1':
    dtypes = postHVAC
    fmin_date_allowed=date(2025, 7, 30)
    fmax_date_allowed=date(2025, 9, 15)
    finitial_visible_month=date(2025, 8, 20)
    fdate=date(2025, 8, 20)
    fstart_date=date(2025, 8, 18)
    fend_date=date(2025, 8, 24)
elif data_display == '0':
    dtypes = preHVAC
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
max_dp = dtypes['Dew Point , °C'].iloc[:,1:].max().max()
min_dp = dtypes['Dew Point , °C'].iloc[:,1:].min().min() 
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

# sensors change with curtains

curtain_7 = ['06 E','03 E-1', '03 E-2','11 N','11 E','15 E-2','15 E-1','13 E','25 E','26 E','27 N','27 E',
             '33 E','36 E','36 N','43 E','43 W','41 N','40 W','65 S','65 W', '64 N', '63 W', '58 N', '57 W',
             '56 N','51 S','52 S','50 S','09 W-2', '01 W-2', '63 E', '60 N', '60 W', '57 N', '35 S', '17 W', 
             '07 N', '06 W'] 
    #most light that was previously recieved from window is now all covered by curtains
curtain_50 = ['29 E', '29 N', '32 W', '32 N','37 N', '55 N', '54 W', '19 E', '19 S', '18 S-2', 
              '09 W-1', '01 W-1', '01 W-3', '49 S']
             
             
             # these sensors will get 7% of light

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
        margin=dict(l=0, r=0, t=0, b=0),
    )
    return fig

#%% App layout
app.layout = html.Div([
    html.Div(
        className="app-header",
        children=[
            html.Img(src='assets/lacma-logo.png', className="app-header--logo"),
            html.Div('David Geffen Gallery HOBO Environmental Monitoring Dashboard', className='app-header--title')],
        style={'display':'flex','alignItems':'center'}
    ),
    dcc.Tabs(id="graph_type", value='tab-1', 
        parent_className = 'custom-tabs',
        className='custom-tabs-container',
        children=[
            dcc.Tab(label='Map View', value='tab-1',className = 'custom_tab',
            selected_className='custom-tab--selected'),
            dcc.Tab(label = "Daily Map View", value = 'tab-2',className = 'custom_tab',
            selected_className='custom-tab--selected'),
            dcc.Tab(label='Time Series', value='tab-3',className = 'custom_tab',
            selected_className='custom-tab--selected'),
            dcc.Tab(label='Time Series Single', value='tab-7',className = 'custom_tab',
            selected_className='custom-tab--selected'),            
            dcc.Tab(label='Psychrometric View', value='tab-4',className = 'custom_tab',
            selected_className='custom-tab--selected'),
            dcc.Tab(label='Curtain Predictions', value='tab-5',className = 'custom_tab',
            selected_className='custom-tab--selected'),
            dcc.Tab(label='HVAC Comparison', value='tab-6',className = 'custom_tab',
            selected_className='custom-tab--selected'),
            dcc.Tab(label='Weather', value = 'tab-8', className='custom_tab',
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
                            style = {'width':'65%', 
                                     'height':'45px',     
                                     'color':'darkblue',
                                     'fontFamily':'Verdana',
                                     'fontSize': '18px', 
                                     'margin': '0 auto',
                                     'fontWeight':'bold'})
                ],
                style={
                    'display':'flex', 
                    'flexDirection':'row', 
                    'justifyContent': 'space-between',
                    'alignItems':'left',
                    'gap':'20px', 
                    'margin':'20px auto 0 auto', 
                    'width':'75%'}
            ),
            dcc.Graph(id='DGG_map',
                config={'displayModeBar': True,  'responsive': True, 'autosizable': True},
                style = { 'margin':'10px auto 0 auto', 
                         'width':'75%',
                         'aspect-ratio':'22/13'})
            ], style={'display': 'block', 'marginTop':'20px'}),  # tab 1 is visible initially

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
                            style = {'width':'65%', 
                                     'height':'45px',     
                                     'color':'darkblue',
                                     'fontFamily':'Verdana',
                                     'fontSize': '18px', 
                                     'fontWeight':'bold'})],              
                style={'display':'flex', 
                       'flexDirection':'row',
                       'justifyContent':'space-between',
                       'alignItems':'left',
                       'gap':'20px', 
                       'margin':'20px auto 0 auto', 
                       'width':'75%'}),
            html.Div(
                dcc.Slider(
                    id='time_slider_tab2',
                    min=0,
                    max=1439,  # total minutes in a day
                    step=15,
                    value=0, 
                    marks={i*60: f"{i:02d}:00" for i in range(0, 24)}),  # hourly labels),
            style = {'width':'75%','margin':'20px auto 0 auto'}),
            html.Div(children=[
            dcc.Graph(id='DGG_map_tab2',
                config={'displayModeBar': True,  'responsive': True, 'autosizable': True},
                style = { 'margin':'10px auto 0 auto', 
                         'width':'75%', 
                         'aspect-ratio':'22/13'})]),
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
                    style={'width': "70%",
                           'height':'45px',     
                            'color':'darkblue',
                            'fontSize': '18px', 
                            'fontFamily':'Verdana',
                            'fontWeight':'bold'})],
                style={'display':'flex', 
                       'flexDirection':'row',
                       'justifyContent':'space-between',
                       'alignItems':'left',
                       'gap':'20px', 
                       'margin':'20px auto 0 auto', 
                       'width':'75%'} ),   
            html.Div(
                children=[
                    dcc.Graph(id='DGG_timeseries_temp', figure={}, style={'width':'100%', 'aspect-ratio':'10/3'}),
                    dcc.Graph(id='DGG_timeseries_rh', figure={}, style={'width':'100%', 'aspect-ratio':'10/3'}),
                    dcc.Graph(id='DGG_timeseries_dp', figure={}, style={'width':'100%', 'aspect-ratio':'10/3'}),
                    dcc.Graph(id='DGG_timeseries_light', figure={}, style={'width':'100%', 'aspect-ratio':'10/3'})
                ],
                style={
                    'display':'flex',
                    'flexDirection':'column',
                    'alignItems':'center',
                    'gap':'5px',  # sets vertical spacing between graphs
                    'margin':'10px auto 0 auto',
                    'width':'75%'
                })],
        style={'display': 'none'}),  # hidden initially
        
        html.Div(id='tab-7-content', children=[
            html.Div(children=[
                dcc.DatePickerRange(
                    id='date_range_tab7',
                    min_date_allowed=fmin_date_allowed,
                    max_date_allowed=fmax_date_allowed,
                    initial_visible_month=finitial_visible_month,
                    start_date=fstart_date,
                    end_date=fend_date),
                dcc.Dropdown(
                    list(circle_coords.keys()),
                    value='30 S',
                    id='sensor_select_tab7',
                    multi=False,
                    style={'width': "40%",
                           'height':'45px',     
                            'color':'darkblue',
                            'fontSize': '18px',
                            'fontFamily':'Verdana',
                            'fontWeight':'bold'})],
                style={'display':'flex', 
                       'flexDirection':'row',
                       'justifyContent':'space-between',
                       'alignItems':'left',
                       'gap':'20px', 
                       'margin':'20px auto 0 auto', 
                       'width':'75%'}  
                ),
            html.Div(children=[            
                dcc.Graph(id='DGG_timeseries_single', figure={}, style={'width':'100%', 'aspect-ratio':'10/3'}),
                dcc.Graph(id='DGG_rh_range',figure={}, style={'width':'100%', 'aspect-ratio':'10/3'})],
                style={
                    'display':'flex',
                    'flexDirection':'column',
                    'alignItems':'center',
                    'gap':'5px',  # sets vertical spacing between graphs
                    'margin':'10px auto 0 auto',
                    'width':'75%'
                })
            ], 
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
                    style={'width': "70%",
                           'height':'45px',     
                            'color':'darkblue',
                            'fontSize': '18px', 
                            'fontFamily':'Verdana',
                            'fontWeight':'bold'})],
                style={'display':'flex', 
                       'flexDirection':'row',
                       'justifyContent':'space-between',
                       'alignItems':'left',
                       'gap':'20px', 
                       'margin':'20px auto 0 auto', 
                       'width':'75%'}    
                ),
            dcc.Graph(id='DGG_psycrhometric', figure={}, 
                      style = { 'margin':'0 auto', 
                               'width':'50%', 
                               'pad':'20px',
                               'aspect-ratio':'5/4'}),
        ], style={'display': 'none'}),
        
        html.Div(id='tab-5-content', children=[
            dcc.Store(id = 'base_fig_store_curtain', data=create_base_fig(img_str).to_json()),
            html.Div(children=[
                html.Div(children=[
                    daq.BooleanSwitch(id ='curtain_boolean', on=True),
                    dcc.DatePickerSingle(
                        id='date_curtain',
                        min_date_allowed=fmin_date_allowed,
                        max_date_allowed=fmax_date_allowed,
                        initial_visible_month=finitial_visible_month,
                        date=fdate)],              
                    style={'display':'flex', 
                           'flexDirection':'row',
                           'justifyContent':'space-between',
                           'alignItems':'left',
                           'gap':'20px', 
                           'margin':'20px auto 0 auto', 
                           'width':'75%'}),
                html.Div(
                    dcc.Slider(
                        id='time_slider_curtain',
                        min=0,
                        max=1439,  # total minutes in a day
                        step=15,
                        value=0, 
                        marks={i*60: f"{i:02d}:00" for i in range(0, 24)}),  # hourly labels),
                style = {'width':'75%','margin':'20px auto 0 auto'}),
                html.Div(children=[
                    dcc.Graph(id='DGG_map_curtain',
                        #config={'displayModeBar': True,  'responsive': True, 'autosizable': True},
                        style = { 'margin':'10px auto 0 auto', 
                                 'width':'75%',
                                 'aspect-ratio':'22/13'})]),
                ]),
                html.Div(children=[
                    html.Div(children=[dcc.Dropdown(
                        list(circle_coords.keys()),
                        ['30 S'],
                        id='sensor_select_curtain',
                        multi=True,
                        style={'width': "100%",
                               'height':'48px',     
                                'color':'darkblue',
                                'fontSize': '18px', 
                                'fontFamily':'Verdana',
                                'fontWeight':'bold'})], 
                        style = {'margin':'0 auto', 
                                 'width':'75%', 
                                 'padding-top':'20px'}),   
                    dcc.Graph(id='DGG_timeseries_curtain', config = {'displayModeBar':True, 'responsive':True, 'autosizable':True})],
                    style = { 'margin':'0 auto', 'width':'75%', 'pad':'40px'}),
                dcc.Markdown('''
                ### Selecting Curtains based off Sensors
                
                All sensors that have light signficantly cut due to the placement 
                of the curtains had their light levels cut by 7%, as the installed 
                curtains only let through this amount of light.
                
                All senosrs that had curtains only partially blocking access to light 
                had their light levels cut by 50% (arbitrary number).
                
                The sensors that were designated as 7% are: 
                06 E, 03 E-1, 03 E-2, 11 N, 11 E, 15 E-2, 15 E-1, 13 E, 25 E, 26 E, 27 N, 27 E,
                33 E, 36 E, 36 N, 43 E, 43 W, 41 N, 40 W, 65 S, 65 W, 64 N, 63 W, 58 N, 57 W,
                56 N, 51 S, 52 S, 50 S, 09 W-2, 01 W-2, 63 E, 60 N, 60 W, 57 N, 35 S, 17 W,
                07 N, and 06 W
                
                The sensors that were designated as 50% are:
                29 E, 29 N, 32 W, 32 N, 37 N, 55 N, 54 W, 19 E, 19 S, 18 S-2,
                09 W-1, 01 W-1, 01 W-3, and 49 S
                             ''',style = {'width':'75%', 'margin':'10px auto 0 auto'})
            ],             
            style={'display': 'none'}),
        html.Div(id='tab-6-content', children=[
            html.Div(children=[
            dcc.Dropdown(
                list(circle_coords.keys()),
                value = '32 N',
                id='sensor_select_tab6',
                multi=False,
                style={'width': "40%",
                       'height':'48px',     
                        'color':'darkblue',
                        'fontSize': '18px',
                        'fontFamily':'Verdana',
                        'fontWeight':'bold'})],
            style={'display':'flex', 
                   'flexDirection':'row',
                   'justifyContent':'space-between',
                   'alignItems':'left',
                   'gap':'20px', 
                   'margin':'20px auto 0 auto', 
                   'width':'75%'}   
            ),
            dcc.Graph(id='HVAC_comp', figure={}, 
                      style = { 'margin':'0 auto', 
                               'width':'50%', 
                               'pad':'20px',
                               'aspect-ratio':'5/4'}),
        ], style={'display': 'none'}),
        html.Div(id='tab-8-content', children=[
            html.Div(children=[
            dcc.DatePickerRange(
                id='date_range_tab8',
                min_date_allowed=fmin_date_allowed,
                max_date_allowed=fmax_date_allowed,
                initial_visible_month=finitial_visible_month,
                start_date=fstart_date,
                end_date=fend_date)], 
            style={'display':'flex', 
                   'flexDirection':'row',
                   'justifyContent':'space-between',
                   'alignItems':'left',
                   'gap':'20px', 
                   'margin':'20px auto 0 auto', 
                   'width':'75%'} ),
            html.Div(children=[
                dcc.Graph(id='T_DP_RH', figure={}, style={'width':'100%', 'aspect-ratio':'10/3'}),
                dcc.Graph(id='solar_radiation', figure={}, style={'width':'100%', 'aspect-ratio':'10/3'}),
                dcc.Graph(id='wind_speed', figure={}, style={'width':'100%', 'aspect-ratio':'10/3'}),
                dcc.Graph(id='precipitation', figure={}, style={'width':'100%', 'aspect-ratio':'10/3'}),
                dcc.Graph(id='pressure', figure={}, style={'width':'100%', 'aspect-ratio':'10/3'})],
                style={
                    'display':'flex',
                    'flexDirection':'column',
                    'alignItems':'center',
                    'gap':'5px',  # sets vertical spacing between graphs
                    'margin':'10px auto 0 auto',
                    'width':'75%'
                }),
            dcc.Markdown('''
            ### Weather Data
            Data in these figures scraped from Weather Underground - [KCALOSAN1069 Weather Station](https://www.wunderground.com/dashboard/pws/KCALOSAN1069)
            and from a Hobo sensor placed on the roof of the Pavillion for Japanese Art.
            ''',style = {'width':'75%', 'margin':'10px auto 0 auto'})

    ],style={'display': 'none'})
    ]),
])
                         
#%% Updating Tab content when clicked
@callback(
    [Output('tab-1-content', 'style'),
     Output('tab-2-content', 'style'),
     Output('tab-3-content', 'style'),
     Output('tab-7-content', 'style'),
     Output('tab-4-content', 'style'),
     Output('tab-5-content', 'style'),
     Output('tab-6-content', 'style'),
     Output('tab-8-content', 'style')],
    Input('graph_type', 'value')
)
def display_tab_content(tab):
    return [
        {'display': 'block'} if tab == 'tab-1' else {'display': 'none'},
        {'display': 'block'} if tab == 'tab-2' else {'display': 'none'},
        {'display': 'block'} if tab == 'tab-3' else {'display': 'none'},
        {'display': 'block'} if tab == 'tab-7' else {'display': 'none'},
        {'display': 'block'} if tab == 'tab-4' else {'display': 'none'},
        {'display': 'block'} if tab == 'tab-5' else {'display': 'none'},
        {'display': 'block'} if tab == 'tab-6' else {'display': 'none'},
        {'display': 'block'} if tab == 'tab-8' else {'display': 'none'}
    ]

#%% Updating Figure for Tab 1 - Daily DGG Map View
@app.callback(
    Output(component_id='DGG_map', component_property='figure'),
    Input(component_id='slct_dtype_tab1', component_property='value'),
    Input(component_id='date_range_tab1', component_property='start_date'),
    Input(component_id='date_range_tab1', component_property='end_date'),
    State(component_id='base_fig_store', component_property='data')
)
def update_DGG_map(value, start_date,end_date,base_fig_json):
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


#%% Updating Figure for Tab 2 - DGG Map View
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

#%% Updating Figure for Tab 3 - Timeseries
@app.callback(
    [Output(component_id='DGG_timeseries_temp', component_property='figure'),
    Output(component_id='DGG_timeseries_rh', component_property='figure'),
    Output(component_id='DGG_timeseries_dp', component_property='figure'),
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
            
    return figures['Temperature , °C'], figures['RH , %'], figures['Dew Point , °C'], figures['Light , lux']

#%% Updating Figure for Tab 7 (Time Series Single)
@app.callback(
     [Output(component_id='DGG_timeseries_single', component_property='figure'),
      Output(component_id='DGG_rh_range', component_property='figure')],
     [Input(component_id='date_range_tab7', component_property='start_date'),
     Input(component_id='date_range_tab7', component_property='end_date'),
     Input(component_id='sensor_select_tab7', component_property='value')]
)
def update_DGG_timeseries_single(start_date,end_date,sensor):
    dates = pd.DataFrame(dtypes['RH , %']['Date-Time (PST/PDT)'])
    dates = dates[(dates['Date-Time (PST/PDT)']<np.datetime64(end_date))&(dates['Date-Time (PST/PDT)']>np.datetime64(start_date))]

    single_df = dates.copy()
    for d in ['Temperature , °C', 'RH , %', 'Dew Point , °C']:
        dff = dtypes[d][['Date-Time (PST/PDT)',sensor]].rename(columns={sensor:d})
        single_df=single_df.merge(dff, how='inner',on='Date-Time (PST/PDT)')
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Left axis = Temperature
    fig.add_trace(
        go.Scatter(
            x=single_df["Date-Time (PST/PDT)"],
            y=single_df['Temperature , °C'],
            name="Air Temperature (°C)",
            line=dict(color = 'firebrick')
        ),
        secondary_y=False
    )
    fig.add_trace(
        go.Scatter(
            x=single_df["Date-Time (PST/PDT)"],
            y=single_df['Dew Point , °C'],
            name="Dew Point (°C)",
            line = dict(color = 'steelblue')
        ),
        secondary_y=False
    )

    # Right axis = RH
    fig.add_trace(
        go.Scatter(
            x=single_df["Date-Time (PST/PDT)"],
            y=single_df['RH , %'],
            name="Relative Humidity (%)",
            line = dict(color = 'limegreen')
        ),
        secondary_y=True
    )

    # X-axis
    fig.update_xaxes(title_text="Date")

    # Left y-axis (Temp)
    fig.update_yaxes(
        title_text="Temperature and Dew Point (°C)",
        color = 'black',
        range = [0,80],
        secondary_y=False,
        automargin=True
    )

    # Right y-axis (RH)
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
    
    rh_24_hour_average = dates.merge(moving_24hour_average['RH , %'], how='inner',on='Date-Time (PST/PDT)')
    rh_24_hour_range = dates.merge(moving_24hour_range['RH , %'], how='inner',on='Date-Time (PST/PDT)')
    
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
    print(dates)
    
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
    return fig, fig2

#%% Updating Figure for Tab 4 - Psychrometric View
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
        xaxis=dict(range=[0, 45],showline=True, mirror=True, linecolor='black'),
        yaxis=dict(range=[0, 30],showline=True, mirror=True, linecolor='black'),
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

#%% Updating Figure for Tab 5 - Curtain Tab
@app.callback(
    [Output(component_id='DGG_map_curtain', component_property='figure'),
     Output(component_id = 'DGG_timeseries_curtain', component_property= 'figure')],
    [Input(component_id ='curtain_boolean', component_property = 'on'),
     Input(component_id='date_curtain', component_property='date'),
     Input(component_id='time_slider_curtain', component_property='value'),
     Input(component_id = 'sensor_select_curtain', component_property='value')],
    State(component_id='base_fig_store_curtain', component_property='data')
)
def update_DGG_curtains(on, date, time, sensors, base_fig_json):
    datetime_base = datetime.combine(pd.to_datetime(date),datetime.min.time()) #convert datetime at midnight
    target_time = pd.to_datetime(datetime_base+timedelta(minutes = time))
    
    dff = dtypes['Light , lux'].copy()
        
    daily_data = dff[dff['Date-Time (PST/PDT)']==target_time].drop(['Date-Time (PST/PDT)'],axis=1).reset_index(drop=True)
    if on == True:
        daily_data.loc[:,curtain_7] = (daily_data.loc[:,curtain_7])*0.07
        daily_data.loc[:,curtain_50] = (daily_data.loc[:,curtain_50])*0.5
    sensor_names = daily_data.columns
    fig_dict = json.loads(base_fig_json)
    figure_map = go.Figure(fig_dict)

    colors = np.log10(daily_data.iloc[0,:].replace(0, 1e-6))
    colors = colors.replace({np.nan:'#FFFFFF'})
    trace = figure_map.data[0]
    
    trace.marker.update(
        color = colors,
        colorscale = 'solar',
        cmin = 0,
        cmax = np.log10(max_lt),
        colorbar = dict(title= 'Light , lux', x=1.05, xanchor = 'left',
                        tickvals=np.log10([1,10,100,1000,10000,20000,50000]), #positions in log-space
                        ticktext=[1,10,100,1000,10000,20000,50000]) #positions in linear space
        )

    hover_text = [
        f"<b>Sensor:</b> {sensor}<br>"
        f"<b>Light:</b> {daily_data.loc[0,sensor]:.2f} lux<br>"
        for sensor in sensor_names]

    trace.text = hover_text
    trace.hovertemplate = "%{text}<extra></extra>"
    
    date_obj = pd.to_datetime(date).date()
    
    ts_data = dff[dff['Date-Time (PST/PDT)'].dt.date == date_obj]
    ts_data_copy = ts_data.copy()
    if on == True:
        ts_data_copy[curtain_7] = ts_data[curtain_7]*0.07
        ts_data_copy[curtain_50] = ts_data[curtain_50]*0.5
    figure_ts=px.line(        
            data_frame = ts_data_copy,
            x='Date-Time (PST/PDT)',
            y=sensors,
           labels = {
               'Date-Time (PST/PDT)': 'Time',
               'value': 'Light, lux',       
               'variable': 'Sensor'
            })
    x_shade = ts_data_copy['Date-Time (PST/PDT)']
    n = len(x_shade)
    y_shade_bottom = np.full(n, 0)
    y_shade_top = np.full(n, 250)
    figure_ts.add_trace(go.Scatter(
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
    return figure_map, figure_ts

#%% Updating Figure for Tab 5 - HVAC Psychrometric Comp
@app.callback(
    Output(component_id='HVAC_comp', component_property='figure'),
    Input(component_id='sensor_select_tab6', component_property='value')
)
def update_HVAC_comp(sensor):

    rh_data_pre = preHVAC['RH , %'][sensor]/100
    temp_data_pre = preHVAC['Temperature , °C'][sensor]
    time_pre = preHVAC['RH , %']['Date-Time (PST/PDT)'].copy()
    time_pre[np.isnan(rh_data_pre)]=pd.NaT
    
    rh_data_post = postHVAC['RH , %'][sensor]/100
    temp_data_post = postHVAC['Temperature , °C'][sensor]
    time_post = postHVAC['RH , %']['Date-Time (PST/PDT)'].copy()
    time_post[np.isnan(rh_data_post)]=pd.NaT
    
    truncated_weather = weather_data.iloc[::15]
    rh_data_wunderground = truncated_weather['Humidity']/100
    temp_data_wunderground = truncated_weather['Temperature']
    time_wunderground = truncated_weather['Date-Time']

    figure = go.Figure()

    # Creates psychrolib template
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
    
    # Adds the relative humidity labels to psychrolib template
    for rh, (x, y, text) in labels.items():
        figure.add_annotation(
            x=x,
            y=y,
            text=text,
            showarrow=False,
            font=dict(size=10),
            xanchor='left'
        )
    # Plots Bizot Standard
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
        xaxis=dict(range=[0, 45],showline=True, linecolor='black',mirror=True),
        yaxis=dict(range=[0, 30],showline=True, linecolor='black',mirror=True),
        plot_bgcolor='white'
    )
    
    # Outside Hobo
    wunderground_humidr_array = []
    custom_post = []
    for t, rh, dt in zip(temp_data_wunderground, rh_data_wunderground, time_wunderground):
        hum_ratio = psychrolib.GetHumRatioFromRelHum(t, rh, pressure) * 1000
        wunderground_humidr_array.append(hum_ratio)
        custom_post.append([rh * 100, str(dt)])

    figure.add_trace(go.Scatter(
        x=temp_data_wunderground,
        y=wunderground_humidr_array,
        mode='markers',
        name='KCALOSAN1069 Weather Station',
        customdata=custom_post,
        hovertemplate=(
            "Temp: %{x:.2f} °C<br>"
            "HumRatio: %{y:.2f} g/kg<br>"
            "RH: %{customdata[0]:.1f}%<br>"
            "Time: %{customdata[1]}<extra></extra>"
        )
    ))
    
    # Pre-HVAC
    pre_humidr_array = []
    custom_pre = []
    for t, rh, dt in zip(temp_data_pre, rh_data_pre, time_pre):
        hum_ratio = psychrolib.GetHumRatioFromRelHum(t, rh, pressure) * 1000
        pre_humidr_array.append(hum_ratio)
        custom_pre.append([rh * 100, str(dt)])  

    figure.add_trace(go.Scatter(
        x=temp_data_pre,
        y=pre_humidr_array,
        mode='markers',
        name='pre-HVAC',
        customdata=custom_pre,  # plain Python list of lists
        hovertemplate=(
            "Temp: %{x:.2f} °C<br>"
            "HumRatio: %{y:.2f} g/kg<br>"
            "RH: %{customdata[0]:.1f}%<br>"
            "Time: %{customdata[1]}<extra></extra>"
        )
    ))

    # Post-HVAC
    post_humidr_array = []
    custom_post = []
    for t, rh, dt in zip(temp_data_post, rh_data_post, time_post):
        hum_ratio = psychrolib.GetHumRatioFromRelHum(t, rh, pressure) * 1000
        post_humidr_array.append(hum_ratio)
        custom_post.append([rh * 100, str(dt)])

    figure.add_trace(go.Scatter(
        x=temp_data_post,
        y=post_humidr_array,
        mode='markers',
        name='post-HVAC',
        customdata=custom_post,
        hovertemplate=(
            "Temp: %{x:.2f} °C<br>"
            "HumRatio: %{y:.2f} g/kg<br>"
            "RH: %{customdata[0]:.1f}%<br>"
            "Time: %{customdata[1]}<extra></extra>"
        )
    ))
    

    
    return figure

#%% Updating Figure for Tab 8 - Outside Weather
@app.callback(
    [Output(component_id='T_DP_RH', component_property='figure'),
     Output(component_id='solar_radiation', component_property='figure'),
     Output(component_id='wind_speed', component_property='figure'),
     Output(component_id='precipitation', component_property='figure'),
     Output(component_id='pressure', component_property='figure')],
     [Input(component_id='date_range_tab8', component_property='start_date'),
     Input(component_id='date_range_tab8', component_property='end_date')]
)
def update_weather_tab(start_date, end_date):
    weather_data_df = weather_data[(weather_data['Date-Time']<end_date)&(weather_data['Date-Time']>start_date)]
    figure_T = make_subplots(specs=[[{"secondary_y": True}]])

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

    figure_T.update_yaxes(title_text="Temperature and Dew Point (°C)",
                          range=[0,100])
    
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
#%% Configuring error logging
# Create a rotating file handler
file_handler = RotatingFileHandler(
    "logs/errors.log", maxBytes=5*1024*1024, backupCount=5
)
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
))

# Get root logger and attach handler
logger = logging.getLogger()
logger.setLevel(logging.ERROR)
logger.addHandler(file_handler)
#%%
if __name__ == '__main__':
    app.run(debug=True,use_reloader=False, port=7070)
