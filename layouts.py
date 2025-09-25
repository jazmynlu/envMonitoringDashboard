from dash import html, dcc
from create_base_fig import create_base_fig
import dash_daq as daq

def get_layout(date_config, img_str, cropped_img, circle_coords, x_vals, y_vals):
    return html.Div([
        html.Div(
            className="app-header",
            children=[
                html.Div(
                    children=[
                        html.Img(src='assets/lacma-logo.png', className="app-header--logo"),
                        html.Div('David Geffen Gallery Environmental Monitoring Dashboard', className='app-header--title')],
                    style={'display':'flex','alignItems':'center','gap':'10px'}),   
                html.A(
                    html.Button(
                        "Submit Feedback",
                        className='feedback-button'
                    ),
                    href="https://forms.gle/2ZVi9vHus1XhnyJN8",
                    style={'text-decoration': 'none'}
                    )],
            style={'display':'flex',
                   'alignItems':'center',
                   'justifyContent':'space-between'}
        ),
        #Display tabs
        dcc.Tabs(id="graph_type", value='tab-map-view', 
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
                # dcc.Tab(label='Curtain Predictions', value='tab-curtains',className = 'custom_tab',
                # selected_className='custom-tab--selected'),
                dcc.Tab(label='HVAC Comparison', value='tab-hvac',className = 'custom_tab',
                selected_className='custom-tab--selected'),
                dcc.Tab(label='Weather', value = 'tab-weather', className='custom_tab',
                selected_className='custom-tab--selected')
            ]
        ),
        # Render all tab content here, but hide/show them dynamically
        
        # Map View Tab
        html.Div([
            html.Div(id='tab-map-view-content', children=[
                dcc.Store(id = 'base_fig_store', data=create_base_fig(x_vals, y_vals, circle_coords, img_str, cropped_img).to_json()),
                html.Div(children=[
                    dcc.DatePickerRange(
                        id='date_range_tab-map-view-content',
                        min_date_allowed=date_config['fmin_date_allowed'],
                        max_date_allowed=date_config['fmax_date_allowed'],
                        initial_visible_month=date_config['finitial_visible_month'],
                        start_date=date_config['fstart_date'],
                        end_date=date_config['fend_date']),
                    dcc.Dropdown(id="slct_dtype_tab-map-view-content",
                                options=["Averaged Daily Temperature Range (Δ°C)", "Average Temperature (°C)", 
                                        "Averaged Daily Relative Humidity Range (Δ%)", "Average Relative Humidity (%)",
                                        "Average Daily Maximum Light (lux)", "Average Light(lux)"],
                                value="Averaged Daily Temperature Range (Δ°C)",
                                style = {'width':'70%', 
                                         'height':'45px',     
                                         'color':'darkblue',
                                         'fontFamily':'Verdana',
                                         'fontSize': '18px', 
                                         'margin': '0 auto',
                                         'fontWeight':'bold'})
                    ],style={
                        'display':'flex', 
                        'flexDirection':'row', 
                        'justifyContent': 'space-between',
                        'alignItems':'left',
                        'gap':'20px', 
                        'margin':'20px auto 0 auto', 
                        'width':'75%'}
                ),
                dcc.Graph(
                    id='DGG_map',
                    selectedData = {},
                    config={'displayModeBar': True,  
                            'responsive': True, 
                            'autosizable': True,
                            'displaylogo':False,
                            'toImageButtonOptions':{
                                'format': 'png',
                                'filename':'DGG_map_view',
                                'height':None,
                                'width':None,
                                'scale': 3}
                                },
                    style = { 'margin':'10px auto 0 auto', 
                             'width':'75%',
                             'aspect-ratio':'22/13'}),
                dcc.Markdown('''
                    ### How to Use
                    
                    **1. Select Dates of Interest**
                    * Data is averaged between 12:00am of the first date, and 12:00am of the second date.  
                    
                    **2. Select Aggregate Statistic**:  
                    * **Averaged Daily Temperature Range (Δ°C)** subtracts the daily maximum temperature by the daily minimum temperature and averages those values over the selected dates. Gives a rough idea of the temperature fluctuations of each sensor.  
                    * **Average Temperature (°C)** takes the average of temperature readings for each sensor over the selected dates.  
                    * **Averaged Daily Relative Humidity Range (Δ%)** subtracts the daily maximum RH by the daily minimum RH and averages those values over the selected dates. Gives a rough idea of the relative humidity fluctuations of each sensor.  
                    * **Average Relative Humidity (%)** takes the average of relative humidity readings for each sensor over the selected dates.  
                    * **Average Daily Maximum Light (lux)** averages the maximum illuminance reading of each day in the selected dates.  
                    * **Average Light (lux)** takes the average of illuminance readings for each sensor over the selected dates.  
                    
                    **3. Plot is generated!**
                    * The color bar on the right will change color and scale automatically depending on the data being displayed.  
                    * Use your mouse to hover over specific points to see more information about each sensor.  
                    * To download the plot, click on the "Download plot as a PNG" button (camera icon).  
                    * Click and drag on the figure to zoom into an area.  
                    
                    #### Pro-Tip
                    Use the **Lasso Select Tool**, **Box Select Tool**, or **Shift + Click** to select sensors of interest. This will automatically populate the other tabs. To deselect, double-click outside the selection.
                    ''', 
                    style={
                        'width': '75%', 
                        'margin': '10px auto 0 auto',
                        'padding': '10px'
                    })

                ], style={'display': 'block', 'marginTop':'20px'}),  # tab 1 is visible initially
            
            #Daily Map View Tab
            html.Div(id='tab-map-daily-view-content', children=[
                dcc.Store(id = 'base_fig_store2', data=create_base_fig(x_vals, y_vals, circle_coords, img_str, cropped_img).to_json()),
                html.Div(children=[
                    dcc.DatePickerSingle(
                        id='date_tab-map-daily-view',
                        min_date_allowed=date_config['fmin_date_allowed'],
                        max_date_allowed=date_config['fmax_date_allowed'],
                        initial_visible_month=date_config['finitial_visible_month'],
                        date=date_config['fdate']),
                    dcc.Dropdown(id="slct_dtype_tab-map-daily-view",
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
                        id='time_slider_tab-map-daily-view',
                        min=0,
                        max=1439,  # total minutes in a day
                        step=15,
                        value=0, 
                        marks={i*60: f"{i:02d}:00" for i in range(0, 24)}),  # hourly labels),
                style = {'width':'75%','margin':'20px auto 0 auto'}),
                html.Div(children=[
                dcc.Graph(
                    id='DGG_map_tab-map-daily-view',
                    selectedData = {},
                    config={'displayModeBar': True,  
                           'responsive': True, 
                           'autosizable': True,
                           'displaylogo':False,
                           'toImageButtonOptions':{
                               'format': 'png',
                               'filename':'Daily_DGG_map_view',
                               'height':None,
                               'width':None,
                               'scale': 3}
                               },
                    style = { 'margin':'10px auto 0 auto', 
                             'width':'75%', 
                             'aspect-ratio':'22/13'})]),
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
                    ''', 
                    style={
                        'width': '75%', 
                        'margin': '10px auto 0 auto',
                        'padding': '10px'
                    })
                ], style={'display': 'none'}),  # hidden initially
            
            # Time Series tab
            html.Div(id='tab-time-series-content', children=[
                html.Div(children=[
                    dcc.DatePickerRange(
                        id='date_range_tab-timeseries',
                        min_date_allowed=date_config['fmin_date_allowed'],
                        max_date_allowed=date_config['fmax_date_allowed'],
                        initial_visible_month=date_config['finitial_visible_month'],
                        start_date=date_config['fstart_date'],
                        end_date=date_config['fend_date']),
                    dcc.Dropdown(
                        options = [{'label':k, 'value': k} for k in circle_coords.keys()],
                        value=['30 S'],
                        id='sensor_select_tab-timeseries',
                        multi=True,
                        style={'flex':'1',
                               'minHeight':'45px',
                                'color':'darkblue',
                                'fontSize': '18px', 
                                'fontFamily':'Verdana',
                                'fontWeight':'bold'},
                        clearable=True),
                    daq.BooleanSwitch(id='sensor_movement-timeseries',
                                  on=True,
                                  label = 'Hide Sensor Movement Data',
                                  labelPosition='top',
                                  style={'marginLeft': '20px'})],
                    style={'flex':'1',
                        'display':'flex',
                           'flexDirection':'row',
                           'justifyContent':'flex-start',
                           'alignItems':'flex-start',
                           'gap':'20px', 
                           'margin':'20px auto 0 auto', 
                           'width':'75%'}),   
                html.Div(
                    children=[
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
                                              }),
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
                                              }),
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
                                              }),
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
                    ],
                    style={
                        'display':'flex',
                        'flexDirection':'column',
                        'alignItems':'center',
                        'gap':'5px',  # sets vertical spacing between graphs
                        'margin':'10px auto 0 auto',
                        'width':'75%'
                    }),
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
                    ''', 
                    style={
                        'width': '75%', 
                        'margin': '10px auto 0 auto',
                        'padding': '10px'
                    })],
            style={'display': 'none'}),  # hidden initially
            
            # Time Series Single Tab
            html.Div(id='tab-ts-single-content', children=[
                html.Div(children=[
                    dcc.DatePickerRange(
                        id='date_range_tab-ts-single',
                        min_date_allowed=date_config['fmin_date_allowed'],
                        max_date_allowed=date_config['fmax_date_allowed'],
                        initial_visible_month=date_config['finitial_visible_month'],
                        start_date=date_config['fstart_date'],
                        end_date=date_config['fend_date']),
                    dcc.Dropdown(
                        list(circle_coords.keys()),
                        value='30 S',
                        id='sensor_select_tab-ts-single',
                        multi=False,
                        style={'width': "40%",
                               'height':'45px',     
                                'color':'darkblue',
                                'fontSize': '18px',
                                'fontFamily':'Verdana',
                                'fontWeight':'bold'}),
                    daq.BooleanSwitch(id='sensor_movement-ts-single',
                                  on=True,
                                  label = 'Hide Sensor Movement Data',
                                  labelPosition='top')],
                    style={'display':'flex', 
                           'flexDirection':'row',
                           'justifyContent':'flex-start',
                           'alignItems':'center',
                           'gap':'20px', 
                           'margin':'20px auto 0 auto', 
                           'width':'75%'} 
                    ),
                html.Div(children=[            
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
                                          }),
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
                                          }),
                    dcc.Graph(id='DGG_light_plt',
                              figure={}, 
                              style={'width':'100%', 'aspect-ratio':'10/3'},
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
                                          }),
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
                        })],
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
            
            
            #Psychrometric View Tab
            html.Div(id='tab-psychrometric-content', children=[
                html.Div(children=[
                    dcc.DatePickerRange(
                        id='date_range_tab-psychrometric',
                        min_date_allowed=date_config['fmin_date_allowed'],
                        max_date_allowed=date_config['fmax_date_allowed'],
                        initial_visible_month=date_config['finitial_visible_month'],
                        start_date=date_config['fstart_date'],
                        end_date=date_config['fend_date']),
                    dcc.Dropdown(
                        list(circle_coords.keys()),
                        ['30 S'],
                        id='sensor_select_tab-psychrometric',
                        multi=True,
                        style={'flex':'1',
                               'minHeight':'45px',
                                'color':'darkblue',
                                'fontSize': '18px', 
                                'fontFamily':'Verdana',
                                'fontWeight':'bold'})],
                    style={'flex':'1',
                        'display':'flex', 
                           'flexDirection':'row',
                           'justifyContent':'flex-start',
                           'alignItems':'flex-start',
                           'gap':'20px', 
                           'margin':'20px auto 0 auto', 
                           'width':'75%'}    
                    ),
                dcc.Graph(id='DGG_psycrhometric', figure={'layout':{'clickmode':'event+select'}}, 
                          style = { 'margin':'0 auto', 
                                   'width':'50%', 
                                   'pad':'20px',
                                   'aspect-ratio':'5/4'},
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
                                      }),
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
                    ''', 
                    style={
                        'width': '75%', 
                        'margin': '10px auto 0 auto',
                        'padding': '10px'
                    })
            ], style={'display': 'none'}),
            
            # Curtain Predictions  -- NOT FOR DEPLOYMENT
            # html.Div(id='tab-curtains-content', children=[
            #     dcc.Store(id = 'base_fig_store_curtain', data=create_base_fig(x_vals, y_vals, circle_coords, img_str, cropped_img).to_json()),
            #     html.Div(children=[
            #         html.Div(children=[
            #             daq.BooleanSwitch(id ='curtain_boolean', on=True),
            #             dcc.DatePickerSingle(
            #                 id='date_curtain',
            #                 min_date_allowed=date_config['fmin_date_allowed'],
            #                 max_date_allowed=date_config['fmax_date_allowed'],
            #                 initial_visible_month=date_config['finitial_visible_month'],
            #                 date=date_config['fdate'])],              
            #             style={'display':'flex', 
            #                    'flexDirection':'row',
            #                    'justifyContent':'space-between',
            #                    'alignItems':'left',
            #                    'gap':'20px', 
            #                    'margin':'20px auto 0 auto', 
            #                    'width':'75%'}),
            #         html.Div(
            #             dcc.Slider(
            #                 id='time_slider_curtain',
            #                 min=0,
            #                 max=1439,  # total minutes in a day
            #                 step=15,
            #                 value=0, 
            #                 marks={i*60: f"{i:02d}:00" for i in range(0, 24)}),  # hourly labels),
            #         style = {'width':'75%','margin':'20px auto 0 auto'}),
            #         html.Div(children=[
            #             dcc.Graph(id='DGG_map_curtain',
            #                 #config={'displayModeBar': True,  'responsive': True, 'autosizable': True},
            #                 style = { 'margin':'10px auto 0 auto', 
            #                          'width':'75%',
            #                          'aspect-ratio':'22/13'})]),
            #         ]),
            #         html.Div(children=[
            #             html.Div(children=[dcc.Dropdown(
            #                 list(circle_coords.keys()),
            #                 ['30 S'],
            #                 id='sensor_select_curtain',
            #                 multi=True,
            #                 style={'width': "100%",
            #                        'height':'48px',     
            #                         'color':'darkblue',
            #                         'fontSize': '18px', 
            #                         'fontFamily':'Verdana',
            #                         'fontWeight':'bold'})], 
            #                 style = {'margin':'0 auto', 
            #                          'width':'75%', 
            #                          'padding-top':'20px'}),   
            #             dcc.Graph(id='DGG_timeseries_curtain', config = {'displayModeBar':True, 'responsive':True, 'autosizable':True})],
            #             style = { 'margin':'0 auto', 'width':'75%', 'pad':'40px'}),
            #         dcc.Markdown('''
            #         ### Selecting Curtains based off Sensors
                    
            #         All sensors that have light signficantly cut due to the placement 
            #         of the curtains had their light levels cut by 7%, as the installed 
            #         curtains only let through this amount of light.
                    
            #         All senosrs that had curtains only partially blocking access to light 
            #         had their light levels cut by 50% (arbitrary number).
                    
            #         The sensors that were designated as 7% are: 
            #         06 E, 03 E-1, 03 E-2, 11 N, 11 E, 15 E-2, 15 E-1, 13 E, 25 E, 26 E, 27 N, 27 E,
            #         33 E, 36 E, 36 N, 43 E, 43 W, 41 N, 40 W, 65 S, 65 W, 64 N, 63 W, 58 N, 57 W,
            #         56 N, 51 S, 52 S, 50 S, 09 W-2, 01 W-2, 63 E, 60 N, 60 W, 57 N, 35 S, 17 W,
            #         07 N, and 06 W
                    
            #         The sensors that were designated as 50% are:
            #         29 E, 29 N, 32 W, 32 N, 37 N, 55 N, 54 W, 19 E, 19 S, 18 S-2,
            #         09 W-1, 01 W-1, 01 W-3, and 49 S
            #                      ''',style = {'width':'75%', 'margin':'10px auto 0 auto'})
            #     ],             
            #     style={'display': 'none'}),
                                 
            # HVAC Comparison Tab
            html.Div(id='tab-hvac-content', children=[
                html.Div(children=[
                dcc.Dropdown(
                    list(circle_coords.keys()),
                    value = '32 N',
                    id='sensor_select_tab-hvac',
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
                                   'aspect-ratio':'5/4'},
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
                                      }),
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
                    ''', 
                    style={
                        'width': '75%', 
                        'margin': '10px auto 0 auto',
                        'padding': '10px'
                    })
            ], style={'display': 'none'}),
            
            # Weather Tab
            html.Div(id='tab-weather-content', children=[
                html.Div(children=[
                dcc.DatePickerRange(
                    id='date_range_tab-weather',
                    min_date_allowed=date_config['fmin_date_allowed'],
                    max_date_allowed=date_config['fmax_date_allowed'],
                    initial_visible_month=date_config['finitial_visible_month'],
                    start_date=date_config['fstart_date'],
                    end_date=date_config['fend_date'])], 
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
                Data in these figures scraped from Weather Underground - [KCALOSAN1069 Weather Station](https://www.wunderground.com/dashboard/pws/KCALOSAN1069). Weather station is located at the Grove.
                ''',style = {'width':'75%', 'margin':'10px auto 0 auto'})
    
        ],style={'display': 'none'})
        ]),
    ])