from dash import html, dcc
import dash_bootstrap_components as dbc
from create_base_fig import create_base_fig
import dash_daq as daq

def new_get_layout(date_config, img_str, cropped_img, circle_coords, all_coords, x_vals, y_vals):
    return html.Div([
        dbc.Row([
            dbc.Col([html.Img(src='assets/lacma-logo.png', className="app-header--logo")],
                    xs=4, sm = 4, md = 2, lg = 2, xl=1),
            dbc.Col([html.Div('David Geffen Gallery Dashboard',
                             style = {'font-size': 'clamp(20px, 2vw, 28px)', 
                                      'font-weight':'bold'})],
                    xs = 8, sm = 8, md = 6, lg = 6, xl = 7),
            dbc.Col([html.Div([daq.BooleanSwitch(id='unit-system-switch',on=True),
                               html.Div(id='unit-system-switch-label',
                                        style = {'margin-left': '10px',
                                                 'font-family':'Verdana',
                                                 'font-size':'1rem',
                                                 'align-self':'center'})],
                              style = {'display':'flex', 
                                       'flexDirection':'row',
                                       'alignItems':'center',
                                       'justifyContent':'flex-start'})],
                    xs = 6, sm = 6, md = 2, lg = 2, xl = 2,
                    align='center'),
            dbc.Col([html.A(
                html.Button("Submit Feedback", className='feedback-button'),
                href="https://forms.gle/2ZVi9vHus1XhnyJN8",
                style={'text-decoration': 'none'})],
                xs = 6, sm = 6, md = 2, lg = 2, xl = 2,
                align='center',
                style={'margin-top':'6px'})
        ],
        style = {'padding-top':'10px',
                 'padding-bottom': '10px'},
        justify='end'),
        dbc.Row([
            dbc.Col([dcc.Tabs(id="graph_type", value='tab-map-view', 
                              parent_className = 'custom-tabs',
                              className='custom-tabs-container',
                                children=[
                                    dcc.Tab(label='Map View', value='tab-map-view',className = 'custom_tab',
                                    selected_className='custom-tab--selected'),
                                    dcc.Tab(label = "Daily Map View", value = 'tab-map-daily-view',className = 'custom_tab',
                                    selected_className='custom-tab--selected'),
                                    dcc.Tab(label='Time Series', value='tab-time-series',className = 'custom_tab',
                                    selected_className='custom-tab--selected'),
                                    dcc.Tab(label='Time Series Single', value='tab-ts-single',className = 'custom_tab',
                                    selected_className='custom-tab--selected'),            
                                    dcc.Tab(label='Psychrometric View', value='tab-psychrometric',className = 'custom_tab',
                                    selected_className='custom-tab--selected'),
                                    dcc.Tab(label='HVAC Comparison', value='tab-hvac',className = 'custom_tab',
                                    selected_className='custom-tab--selected'),
                                    dcc.Tab(label='Weather', value = 'tab-weather', className='custom_tab',
                                    selected_className='custom-tab--selected')
                                ],
                                style = {'font-size': 'clamp(13px, 1vw, 15px)'})
                     ], width = 12)
            ]),
        html.Div(id='tab-map-view-content', children = [
            map_view_tab(date_config, img_str, cropped_img, all_coords, x_vals, y_vals)],
            style = {'display': 'block'}),
        
        html.Div(id='tab-map-daily-view-content', children = [
            daily_map_view_tab(date_config, img_str, cropped_img, all_coords, x_vals, y_vals)],
            style = {'display': 'none'}),
        
        html.Div(id='tab-time-series-content', children = [
            time_series_tab(date_config, all_coords)],
            style = {'display': 'none'}),
        
        html.Div(id='tab-ts-single-content', children = [
            time_series_single_tab(date_config, circle_coords)],
            style = {'display': 'none'}),
        
        html.Div(id='tab-psychrometric-content', children = [
            psychrometric_tab(date_config, all_coords)],
            style = {'display': 'none'}),
        
        html.Div(id='tab-hvac-content', children = [
            hvac_comparison(all_coords)],
            style = {'display': 'none'}),
        
        html.Div(id='tab-weather-content', children = [
            weather_tab(date_config)],
            style = {'display': 'none'})])
        
def map_view_tab(date_config, img_str, cropped_img, all_coords, x_vals, y_vals):
    return dbc.Container([
        dcc.Store(id = 'base_fig_store', 
                  data=create_base_fig(x_vals, y_vals, all_coords, img_str, cropped_img).to_json()),
        dbc.Row([
            dbc.Col([
                dcc.DatePickerRange(
                    id='date_range_tab-map-view-content',
                    min_date_allowed=date_config['fmin_date_allowed'],
                    max_date_allowed=date_config['fmax_date_allowed'],
                    initial_visible_month=date_config['finitial_visible_month'],
                    start_date=date_config['fstart_date'],
                    end_date=date_config['fend_date'])],
                xs = 12, sm = 12, md = 12, lg = 4, xl = 4),
            dbc.Col([
                dcc.Dropdown(id="slct_dtype_tab-map-view-content",
                            options=["Averaged Daily Temperature Range", "Average Temperature", 
                                    "Averaged Daily Relative Humidity Range", "Average Relative Humidity",
                                    "Average Daily Maximum Light", "Average Light"],
                            value="Averaged Daily Temperature Range",
                            style = {'color':'darkblue',
                                     'fontFamily':'Verdana',
                                     'fontWeight':'bold'})],
                xs = 12, sm = 12, md = 12, lg = 7, xl = 7)
            ],
            justify='center',
            style = {'padding-top':'10px',
                     'padding-bottom': '10px'}),
        dbc.Row([
            dbc.Col([
                dcc.Graph(
                    id='DGG_map',
                    selectedData={},
                    config={
                        'displayModeBar': True,
                        'responsive': True,
                        'autosizable': True,
                        'displaylogo': False,
                        'toImageButtonOptions': {
                            'format': 'png',
                            'filename': 'DGG_map_view',
                            'scale': 3}},
                    style={'aspectRatio': '22/13'}
                )],
                xs = 12, sm = 12, md = 12, lg = 11, xl = 11
                ),
            ],justify='center'),
        dbc.Row([
            dbc.Col([
                dcc.Markdown('''
                    ### How to Use
                    
                    **1. Select Dates of Interest**
                    * Data is averaged between 12:00am of the first date, and 12:00am of the second date.  
                    
                    **2. Select Aggregate Statistic**:  
                    * **Averaged Daily Temperature Range** subtracts the daily maximum temperature by the daily minimum temperature and averages those values over the selected dates. Gives a rough idea of the temperature fluctuations of each sensor.  
                    * **Average Temperature** takes the average of temperature readings for each sensor over the selected dates.  
                    * **Averaged Daily Relative Humidity Range** subtracts the daily maximum RH by the daily minimum RH and averages those values over the selected dates. Gives a rough idea of the relative humidity fluctuations of each sensor.  
                    * **Average Relative Humidity** takes the average of relative humidity readings for each sensor over the selected dates.  
                    * **Average Daily Maximum Light** averages the maximum illuminance reading of each day in the selected dates.  
                    * **Average Light** takes the average of illuminance readings for each sensor over the selected dates.  
                    
                    **3. Plot is generated!**
                    * The color bar on the right will change color and scale automatically depending on the data being displayed.  
                    * Use your mouse to hover over specific points to see more information about each sensor.  
                    * To download the plot, click on the "Download plot as a PNG" button (camera icon).  
                    * Click and drag on the figure to zoom into an area.  
                    
                    #### Pro-Tip
                    Use the **Lasso Select Tool**, **Box Select Tool**, or **Shift + Click** to select sensors of interest. This will automatically populate the other tabs. To deselect, double-click outside the selection.
                    ''', 
                    style={
                        'padding': '10px'})],
                xs = 12, sm = 12, md = 12, lg = 10, xl = 10, align='center'
                    )
            ],justify='center')
        ])    
        
def daily_map_view_tab(date_config, img_str, cropped_img, all_coords, x_vals, y_vals):
    return dbc.Container([
        dcc.Store(id = 'base_fig_store2', 
                  data=create_base_fig(x_vals, y_vals, all_coords, img_str, cropped_img).to_json()),
        dbc.Row([
            dbc.Col([
                dcc.DatePickerSingle(
                    id='date_tab-map-daily-view',
                    min_date_allowed=date_config['fmin_date_allowed'],
                    max_date_allowed=date_config['fmax_date_allowed'],
                    initial_visible_month=date_config['finitial_visible_month'],
                    date=date_config['fdate'])],
                xs = 12, sm = 12, md = 4, lg = 4, xl = 4
                ),
            dbc.Col([dcc.Dropdown(id="slct_dtype_tab-map-daily-view",
                        options=["Temperature , °C", "RH , %", "Light , lux"],
                        value="Temperature , °C",
                        style = {'height':'45px',     
                                 'color':'darkblue',
                                 'fontFamily':'Verdana',
                                 'fontSize': '18px', 
                                 'fontWeight':'bold'})],
                    xs = 12, sm = 12, md = 8, lg = 7, xl = 7)
                ], justify='center', 
                    style = {'padding-top':'10px','padding-bottom': '10px'}),
        dbc.Row([
            dbc.Col([
                dcc.Slider(
                    id='time_slider_tab-map-daily-view',
                    min=0,
                    max=1439,  # total minutes in a day
                    step=15,
                    value=0,
                    marks={
                        i * 60: {
                            'label': f"{i:02d}:00",
                            'style':{'font-size':'clamp(7px, 1.3vw, 11px)'}
                        }
                        for i in range(0, 24)
                    })
                ], xs = 12, sm = 12, md = 12, lg = 11, xl = 11)
            ],justify='center', style = {'padding-top':'5px','padding-bottom': '5px'}),
        dbc.Row([
            dbc.Col([
                dcc.Graph(
                    id='DGG_map_tab-map-daily-view',
                    selectedData={},
                    config={
                        'displayModeBar': True,
                        'responsive': True,
                        'autosizable': True,
                        'displaylogo': False,
                        'toImageButtonOptions': {
                            'format': 'png',
                            'filename': 'DGG_map_view',
                            'scale': 3}},
                    style={'aspectRatio': '22/13'}
                )], xs = 12, sm = 12, md = 12, lg = 11, xl = 11 )
            ],justify='center'),
        dbc.Row([
            dbc.Col([
                dcc.Markdown('''
                    ### How to Use
                    
                    **1. Select Date of Interest**  
                    
                    **2. Select Environmental Parameter**  
                    
                    **3. Select Time**  
                    * Click or drag slider with mouse. The plot will not update until the left button of the mouse is released!
                    * Use keyboard arrows to increment time forwards or backwards.
                    
                    **4. Plot is generated!**  
                    * The color bar on the right is static and only changes depending on the selected environmental parameter.  
                    * Use your mouse to hover over specific points to see more information about each sensor.  
                    * To download the plot, click on the "Download plot as a PNG" button (camera icon).  
                    * Click and drag on the figure to zoom into an area.  
                    
                    #### Pro-Tip
                    Use the **Lasso Select Tool**, **Box Select Tool**, or **Shift + Click** to select sensors of interest. This will automatically populate the other tabs. To deselect, double-click outside the selection.
                    ''')
                ],xs = 12, sm = 12, md = 12, lg = 10, xl = 10)
            ],justify='center')
        ])

def time_series_tab(date_config, all_coords):
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dcc.DatePickerRange(
                    id='date_range_tab-timeseries',
                    min_date_allowed=date_config['fmin_date_allowed'],
                    max_date_allowed=date_config['fmax_date_allowed'],
                    initial_visible_month=date_config['finitial_visible_month'],
                    start_date=date_config['fstart_date'],
                    end_date=date_config['fend_date'])
                ],
                xs = 12, sm = 12, md = 5, lg = 4, xl = 4),
            dbc.Col([
                dcc.Dropdown(
                    options = [{'label':k, 'value': k} for k in all_coords.keys()],
                    value=['30 S'],
                    id='sensor_select_tab-timeseries',
                    multi=True,
                    style={'flex':'1',
                           'minHeight':'45px',
                            'color':'darkblue',
                            'fontSize': '18px', 
                            'fontFamily':'Verdana',
                            'fontWeight':'bold'},
                    clearable=True)
                ],
                xs = 12, sm = 12, md = 5, lg = 4, xl = 4),
            dbc.Col([
                daq.BooleanSwitch(id='sensor_movement-timeseries',
                              on=True,
                              label = 'Hide Sensor Movement Data',
                              labelPosition='top',
                              style={'marginLeft': '20px'})
                ],
                xs = 12, sm = 12, md = 5, lg = 4, xl = 4)
            ],style = {'padding-top':'10px','padding-bottom': '10px'}),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='DGG_timeseries_temp', 
                          figure={}, 
                          style={'width':'100%', 'aspect-ratio':'10/3'},
                          config={'displayModeBar': True,  
                                  'responsive': True, 
                                  'autosizable': True,
                                  'displaylogo':False,
                                  'toImageButtonOptions':{
                                      'format': 'png',
                                      'filename':'DGG_timeseries_temp',
                                      'height':None,
                                      'width':None,
                                      'scale': 3}
                                      })
                ])
            ]),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='DGG_timeseries_rh', 
                          figure={}, 
                          style={'width':'100%', 'aspect-ratio':'10/3'},
                          config={'displayModeBar': True,  
                                  'responsive': True, 
                                  'autosizable': True,
                                  'displaylogo':False,
                                  'toImageButtonOptions':{
                                      'format': 'png',
                                      'filename':'DGG_timeseries_rh',
                                      'height':None,
                                      'width':None,
                                      'scale': 3}
                                      })
                ])
            ]),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='DGG_timeseries_dp', 
                          figure={}, 
                          style={'width':'100%', 'aspect-ratio':'10/3'},
                          config={'displayModeBar': True,  
                                  'responsive': True, 
                                  'autosizable': True,
                                  'displaylogo':False,
                                  'toImageButtonOptions':{
                                      'format': 'png',
                                      'filename':'DGG_timeseries_dp',
                                      'height':None,
                                      'width':None,
                                      'scale': 3}
                                      })
                ])
            ]),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='DGG_timeseries_light', 
                          figure={}, 
                          style={'width':'100%', 'aspect-ratio':'10/3'},
                          config={'displayModeBar': True,  
                                  'responsive': True, 
                                  'autosizable': True,
                                  'displaylogo':False,
                                  'toImageButtonOptions':{
                                      'format': 'png',
                                      'filename':'DGG_timeseries_light',
                                      'height':None,
                                      'width':None,
                                      'scale': 3}
                                      })
                ])
            ]),
        dbc.Row([
            dbc.Col([
                dcc.Markdown('''
                    ### How to Use
                    **1. Select Dates of Interest**  
                    
                    **2. Select Sensors of Interest**  
                    * Type in names of sensors, or
                    * Select sensors from dropdown menu, or
                    * Select sensors from DGG maps (see Pro-Tip!)  
                    
                    **3. Hide Sensor Movement Data**  
                    * When data was being collected, sensors were occasionally moved for long periods of time for installation, construction, or other activities. Hide this irrepresentative data by turning on the switch. Show all data by turning off the switch
                    
                    **4. Plot is generated!**  
                    * Temperature, relative humidity, dew point, and light plots are generated 
                    * Click on the legend to deselect any sensor or the Bizot Standard
                    * Use your mouse to hover over specific points to see more detailed information  
                    * To download the plot, click on the "Download plot as a PNG" button (camera icon).  
                    * Click and drag on the figure to zoom into an area.  
                    ''')
                ],xs = 12, sm = 12, md = 12, lg = 10, xl = 10)
            ],  justify='center')
        ])

def time_series_single_tab(date_config, circle_coords):
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dcc.DatePickerRange(
                    id='date_range_tab-ts-single',
                    min_date_allowed=date_config['fmin_date_allowed'],
                    max_date_allowed=date_config['fmax_date_allowed'],
                    initial_visible_month=date_config['finitial_visible_month'],
                    start_date=date_config['fstart_date'],
                    end_date=date_config['fend_date'])
                ], xs = 12, sm = 12, md = 5, lg = 5, xl = 3),
            dbc.Col([
                dcc.Dropdown(
                    list(circle_coords.keys()),
                    value='30 S',
                    id='sensor_select_tab-ts-single',
                    multi=False,
                    style={'height':'45px',     
                            'color':'darkblue',
                            'fontSize': '18px',
                            'fontFamily':'Verdana',
                            'fontWeight':'bold'})
                ], xs = 12, sm = 12, md = 5, lg = 4, xl = 5),
            dbc.Col([
                daq.BooleanSwitch(id='sensor_movement-ts-single',
                              on=True,
                              label = 'Hide Sensor Movement Data',
                              labelPosition='top')
                ], xs = 12, sm = 12, md = 5, lg = 3, xl = 4)
            ], style = {'padding-top':'10px',
                     'padding-bottom': '10px'}),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='DGG_timeseries_single', 
                          figure={}, 
                          style={'width':'100%', 'aspect-ratio':'10/3'},
                          config={'displayModeBar': True,  
                                  'responsive': True, 
                                  'autosizable': True,
                                  'displaylogo':False,
                                  'toImageButtonOptions':{
                                      'format': 'png',
                                      'filename':'DGG_timeseries_T_RH_DP',
                                      'height':None,
                                      'width':None,
                                      'scale': 3}
                                      })
                ])
            ]),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='DGG_rh_range',
                          figure={}, 
                          style={'width':'100%', 'aspect-ratio':'10/3'},
                          config={'displayModeBar': True,  
                                  'responsive': True, 
                                  'autosizable': True,
                                  'displaylogo':False,
                                  'toImageButtonOptions':{
                                      'format': 'png',
                                      'filename':'DGG_RH_range',
                                      'height':None,
                                      'width':None,
                                      'scale': 3}
                                      })
                ])
            ]),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='DGG_light_plt',
                          figure={}, 
                          style={'width':'100%', 'aspect-ratio':'10/5'},
                          config={'displayModeBar': True,  
                                  'responsive': True, 
                                  'autosizable': True,
                                  'displaylogo':False,
                                  'toImageButtonOptions':{
                                      'format': 'png',
                                      'filename':'DGG_light',
                                      'height':None,
                                      'width':None,
                                      'scale': 3}
                                      })
                ])
            ]),
        dbc.Row([
            dbc.Col([
                dcc.Markdown('''
                    ### How to Use
                    **1. Select Dates of Interest**  
                    
                    **2. Select Sensor of Interest**  
                    * Type in name of sensor, or
                    * Select sensor from dropdown menu, or
                    * Select sensor from DGG maps - if multiple sensors selected, will select first from alphabetical order
                    
                    **3. Hide Sensor Movement Data**  
                    * When data was being collected, sensors were occasionally moved for long periods of time for installation, construction, or other activities. Hide this irrepresentative data by turning on the switch. Show all data by turning off the switch
                    
                    **4. Plot is generated!**  
                    * The first plot shows temperature and dew point on the left y-axis and relative humidity on the right y-axis. By default the left and right y-axes are aligned, but you can expand the relative humidity axis by clicking on **Autoscale**. This plot shows whether relative humidity fluctuations are coming from temperature changes or dew point changes.
                    * The second plot shows the relative humidity, the average 24 hour relative humidity, and the 24 hour range, calculated with a rolling window.
                    * The third plot showcases the illuminance of the sensor, and calculates the cumulative light exposure of that sensor over the specified time window using numerical integration.
                    * Use your mouse to hover over specific points to see more information about each sensor.  
                    * To download the plot, click on the "Download plot as a PNG" button (camera icon).  
                    * Click and drag on the figure to zoom into an area.  
                    ''', 
                    style={
                        'width': '100%', 
                        'margin': '10px auto 0 auto',
                        'padding': '10px'
                    })
                ], xs = 12, sm = 12, md = 12, lg = 10, xl = 10)
            ], )
        ])

def psychrometric_tab(date_config, all_coords):
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dcc.DatePickerRange(
                    id='date_range_tab-psychrometric',
                    min_date_allowed=date_config['fmin_date_allowed'],
                    max_date_allowed=date_config['fmax_date_allowed'],
                    initial_visible_month=date_config['finitial_visible_month'],
                    start_date=date_config['fstart_date'],
                    end_date=date_config['fend_date'])
                ],  xs = 12, sm = 12, md = 4, lg = 4, xl = 4),
            dbc.Col([
                dcc.Dropdown(
                    list(all_coords.keys()),
                    ['30 S'],
                    id='sensor_select_tab-psychrometric',
                    multi=True,
                    style={'flex':'1',
                           'minHeight':'45px',
                            'color':'darkblue',
                            'fontSize': '18px', 
                            'fontFamily':'Verdana',
                            'fontWeight':'bold'})
                ],  xs = 12, sm = 12, md = 8, lg = 8, xl = 8)
            ], justify = 'center', style = {'padding-top':'5px',
                     'padding-bottom': '5px'}),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='DGG_psycrhometric', figure={'layout':{'clickmode':'event+select'}}, 
                          style = {'aspect-ratio':'5/4'},
                          config={'displayModeBar': True,  
                                  'responsive': True, 
                                  'autosizable': True,
                                  'displaylogo':False,
                                  'toImageButtonOptions':{
                                      'format': 'png',
                                      'filename':'DGG_psychrometric',
                                      'height':None,
                                      'width':None,
                                      'scale': 3}
                                      })
                ], xs = 12, sm = 12, md = 12, lg = 7, xl = 7)
            ], justify='center'),
        dbc.Row([
            dbc.Col([
                dcc.Markdown('''
                    ### How to Use
                    **1. Select Dates of Interest**  
                    
                    **2. Select Sensors of Interest**  
                    * Type in name of sensors, or
                    * Select sensors from dropdown menu, or
                    * Select sensors from DGG maps 
 
                    **3. Plot is generated!**  
                    * A psychrometric chart is a "map" for analyzing moist air, graphically showing the interrelationships between air properties like temperature, humidity, and moisture content.
                    * Use your mouse to hover over specific points to see more information about each sensor.  
                    * To download the plot, click on the "Download plot as a PNG" button (camera icon).  
                    * Click and drag on the figure to zoom into an area.  
                    ''')
                ], xs = 12, sm = 12, md = 12, lg = 10, xl = 10)
            ], justify='center')
        ])

def hvac_comparison(all_coords):
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                    list(all_coords.keys()),
                    value = '32 N',
                    id='sensor_select_tab-hvac',
                    multi=False,
                    style={'height':'48px',     
                            'color':'darkblue',
                            'fontSize': '18px',
                            'fontFamily':'Verdana',
                            'fontWeight':'bold'})
                ])
            ],style = {'padding-top':'10px',
                     'padding-bottom': '10px'}),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='HVAC_comp', figure={}, 
                          style = {'margin':'0 auto',
                                   'pad':'20px',
                                   'aspect-ratio':'1/1'},
                          config={'displayModeBar': True,  
                                  'responsive': True, 
                                  'autosizable': True,
                                  'displaylogo':False,
                                  'toImageButtonOptions':{
                                      'format': 'png',
                                      'filename':'HVAC_Comparison',
                                      'height':None,
                                      'width':None,
                                      'scale': 3}
                                      })
                ], xs = 12, sm = 12, md = 12, lg = 7, xl = 7)
            ], justify='center'),
        dbc.Row([
            dbc.Col([
                dcc.Markdown('''
                    ### How to Use
                    **1. Select Sensor of Interest**  
                    * Type in name of sensors, or
                    * Select sensors from dropdown menu, or
                    * Select sensors from DGG maps - if multiple sensors selected, will select first from alphabetical order
 
                    **2. Plot is generated!**  
                    * A psychrometric chart is a "map" for analyzing moist air, graphically showing the interrelationships between air properties like temperature, humidity, and moisture content.
                    * This psychrometric chart demonstrates the narrowing of temperature and humidity ranges from the building envelope and the HVAC system. 
                    * Deselect items by clicking them on the legend
                    * Use your mouse to hover over specific points to see more information about each sensor.  
                    * To download the plot, click on the "Download plot as a PNG" button (camera icon).  
                    * Click and drag on the figure to zoom into an area.  
                    
                    Note: "Outside data is collected from the KCALOSAN1069 Weather Station"
                    '''
                    )
                ], xs = 12, sm = 12, md = 12, lg = 10, xl = 10)
            ],  justify='center')
        ])

def weather_tab(date_config):
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dcc.DatePickerRange(
                    id='date_range_tab-weather',
                    min_date_allowed=date_config['fmin_date_allowed'],
                    max_date_allowed=date_config['fmax_date_allowed'],
                    initial_visible_month=date_config['finitial_visible_month'],
                    start_date=date_config['fstart_date'],
                    end_date=date_config['fend_date'])
                ])
            ], style = {'padding-top':'10px',
                     'padding-bottom': '10px'}),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='T_DP_RH', figure={}, 
                          style={'width':'100%', 'aspect-ratio':'10/3'},
                          config={'displayModeBar': True,  
                                  'responsive': True, 
                                  'autosizable': True,
                                  'displaylogo':False,
                                  'toImageButtonOptions':{
                                      'format': 'png',
                                      'filename':'weather_T_DP_RH',
                                      'height':None,
                                      'width':None,
                                      'scale': 3}
                                      })
                ]),
                dbc.Col([
                    dcc.Graph(id='solar_radiation', figure={}, 
                              style={'width':'100%', 'aspect-ratio':'10/3'},
                              config={'displayModeBar': True,  
                                      'responsive': True, 
                                      'autosizable': True,
                                      'displaylogo':False,
                                      'toImageButtonOptions':{
                                          'format': 'png',
                                          'filename':'weather_solar_radiation',
                                          'height':None,
                                          'width':None,
                                          'scale': 3}
                                          })
                    ]),
                dbc.Col([
                    dcc.Graph(id='wind_speed', figure={}, 
                              style={'width':'100%', 'aspect-ratio':'10/3'},
                              config={'displayModeBar': True,  
                                      'responsive': True, 
                                      'autosizable': True,
                                      'displaylogo':False,
                                      'toImageButtonOptions':{
                                          'format': 'png',
                                          'filename':'weather_wind_speed',
                                          'height':None,
                                          'width':None,
                                          'scale': 3}
                                          })
                    ]),
                dbc.Col([
                    dcc.Graph(id='precipitation', figure={}, 
                              style={'width':'100%', 'aspect-ratio':'10/3'},
                              config={'displayModeBar': True,  
                                      'responsive': True, 
                                      'autosizable': True,
                                      'displaylogo':False,
                                      'toImageButtonOptions':{
                                          'format': 'png',
                                          'filename':'weather_precipitation',
                                          'height':None,
                                          'width':None,
                                          'scale': 3}
                                          })
                    ]),
                dbc.Col([
                    dcc.Graph(id='pressure', figure={}, 
                              style={'width':'100%', 'aspect-ratio':'10/3'},
                              config={'displayModeBar': True,  
                                      'responsive': True, 
                                      'autosizable': True,
                                      'displaylogo':False,
                                      'toImageButtonOptions':{
                                          'format': 'png',
                                          'filename':'weather_pressure',
                                          'height':None,
                                          'width':None,
                                          'scale': 3}
                                          })
                    ])
                ]),
            dbc.Row([
                dbc.Col([
                    dcc.Markdown('''
                    ### Weather Data
                    Data in these figures scraped from Weather Underground - [KCALOSAN1069 Weather Station](https://www.wunderground.com/dashboard/pws/KCALOSAN1069). Weather station is located at the Grove.
                    ''')
                    ])
                ])
        ])
