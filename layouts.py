from dash import html, dcc
from create_base_fig import create_base_fig

def get_layout(date_config, img_str, cropped_img, circle_coords, x_vals, y_vals):
    return html.Div([
        html.Div(
            className="app-header",
            children=[
                html.Img(src='assets/lacma-logo.png', className="app-header--logo"),
                html.Div('David Geffen Gallery HOBO Environmental Monitoring Dashboard', className='app-header--title')],
            style={'display':'flex','alignItems':'center'}
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
                dcc.Store(id = 'base_fig_store', data=create_base_fig(x_vals, y_vals, img_str, cropped_img).to_json()),
                html.Div(children=[
                    dcc.DatePickerRange(
                        id='date_range_tab-map-view-content',
                        min_date_allowed=date_config['fmin_date_allowed'],
                        max_date_allowed=date_config['fmax_date_allowed'],
                        initial_visible_month=date_config['finitial_visible_month'],
                        start_date=date_config['fstart_date'],
                        end_date=date_config['fend_date']),
                    dcc.Dropdown(id="slct_dtype_tab-map-view-content",
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
            
            
            #Daily Map View Tab
            html.Div(id='tab-map-daily-view-content', children=[
                dcc.Store(id = 'base_fig_store2', data=create_base_fig(x_vals, y_vals, img_str, cropped_img).to_json()),
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
                dcc.Graph(id='DGG_map_tab-map-daily-view',
                    config={'displayModeBar': True,  'responsive': True, 'autosizable': True},
                    style = { 'margin':'10px auto 0 auto', 
                             'width':'75%', 
                             'aspect-ratio':'22/13'})]),
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
                        list(circle_coords.keys()),
                        ['30 S'],
                        id='sensor_select_tab-timeseries',
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
                    dcc.Graph(id='DGG_rh_range',figure={}, style={'width':'100%', 'aspect-ratio':'10/3'}),
                    dcc.Graph(id='DGG_light_plt',figure={}, style={'width':'100%', 'aspect-ratio':'10/3'})],
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
            
            # Curtain Predictions Tab
            # html.Div(id='tab-curtains-content', children=[
            #     dcc.Store(id = 'base_fig_store_curtain', data=create_base_fig(x_vals, y_vals, img_str, cropped_img).to_json()),
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
                                   'aspect-ratio':'5/4'}),
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
                Data in these figures scraped from Weather Underground - [KCALOSAN1069 Weather Station](https://www.wunderground.com/dashboard/pws/KCALOSAN1069)
                and from a Hobo sensor placed on the roof of the Pavillion for Japanese Art.
                ''',style = {'width':'75%', 'margin':'10px auto 0 auto'})
    
        ],style={'display': 'none'})
        ]),
    ])