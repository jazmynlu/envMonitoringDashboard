import pickle
from datetime import date
import psychrolib
import numpy as np
from PIL import Image
import pandas as pd
import base64
import io

def load_sensor_movement(filepath = 'setup/sensor_movement.csv'):
    """
    Loads and organizes sensor_movements.csv, a file that is updated manually 
    to keep track of when sensors are moved away from their original locations 
    due to installation

    """
    sensor_movement_df= pd.read_csv(filepath)
    sensor_movement_df['Start'] = pd.to_datetime(sensor_movement_df['Start'], format="%m/%d/%Y %H:%M")
    sensor_movement_df['End'] = pd.to_datetime(sensor_movement_df['End'], format="%m/%d/%Y %H:%M")
    return sensor_movement_df

def load_dataframes(filepath = 'setup/df_config.txt', filepath_sensor_mvmt ='setup/sensor_movement.csv'):
    """
    Reads in pickle files generated with dataPreprocessing.py that is processed
    locally. Also prunes data from start and end times from sensor_movement_df. 
    Returns a dictionary of dataframes. Each key is self-explanatory.

    """
    dataframes = {}
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            name,value = line.split('=',1)
            name=name.strip()
            value=value.strip().strip("'").strip('"')
            with open(value,'rb') as file:
                dataframes[name]=pickle.load(file)
    sensor_mvmt = load_sensor_movement(filepath = filepath_sensor_mvmt)
    dataframes['sensor_movement'] = sensor_mvmt
    
    postHVAC_pruned = {}
    for key in dataframes['postHVAC'].keys():
        df_pruned = dataframes['postHVAC'][key].copy()
        for _, row in sensor_mvmt.iterrows():
            sensor = row['Sensor']
            start = row['Start']
            end = row['End']
            mask = (df_pruned['Date-Time (PST/PDT)'] >= start) & (df_pruned['Date-Time (PST/PDT)'] <= end)
            df_pruned.loc[mask,sensor]=pd.NA
        postHVAC_pruned[key]=df_pruned
    dataframes['postHVAC_pruned'] = postHVAC_pruned
    
    return dataframes
    
def load_initial_dashboard_vars(filepath = 'setup/set_dates.txt'):
    """
    Loads in initial dates for interactive components of dashboard

    """
    safe_env = {'date': date}
    date_config = {}
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            name,value = line.split('=',1)
            date_config[name.strip()] = eval(value.strip(), safe_env)
    return date_config

def crop_map(image_path='galleryInfo/2025 - DGG Exhibition Level Blueprint (LACMA).jpg'):
    """
    Prepares image for plotting in DGG Map tabs.

    """
    # Load Image of Map
    Image.MAX_IMAGE_PIXELS = None
    img = Image.open(image_path)
    
    # Crop the image
    crop_box = (3000, 1000, 14000, 7500)
    cropped_img = img.crop(crop_box)
    # Resize image to smaller width while keeping aspect ratio
    target_width = 2000
    target_height = int(target_width * cropped_img.height / cropped_img.width)
    resized_img = cropped_img.resize((target_width, target_height), Image.Resampling.LANCZOS)

    # Convert numpy image to base64 string for Plotly
    buffered = io.BytesIO()
    resized_img.save(buffered, format="PNG")
    img_str = "data:image/png;base64," + base64.b64encode(buffered.getvalue()).decode()
    return img_str, cropped_img

def initialize_dashboard(df_filepath = 'setup/df_config.txt', 
                         setdates_filepath = 'setup/set_dates.txt',
                         image_path='galleryInfo/2025 - DGG Exhibition Level Blueprint (LACMA).jpg'):
    dfs = load_dataframes(df_filepath)
    date_config = load_initial_dashboard_vars(setdates_filepath)
    img_str, cropped_img = crop_map(image_path)
    max_temp = dfs['postHVAC']['Temperature , °C'].iloc[:,1:].max().max()
    min_temp = dfs['postHVAC']['Temperature , °C'].iloc[:,1:].min().min()
    max_RH = dfs['postHVAC']['RH , %'].iloc[:,1:].max().max()
    min_RH = dfs['postHVAC']['RH , %'].iloc[:,1:].min().min()
    max_dp = dfs['postHVAC']['Dew Point , °C'].iloc[:,1:].max().max()
    min_dp = dfs['postHVAC']['Dew Point , °C'].iloc[:,1:].min().min() 
    max_lt = dfs['postHVAC']['Light , lux'].iloc[:,1:].max().max()
    min_lt = dfs['postHVAC']['Light , lux'].iloc[:,1:].min().min()

    # Prepare data for Map plotting
    x_vals = []
    y_vals = []
    
    for i in dfs['circle_coords'].keys():
        x_vals.append(dfs['circle_coords'][i][0])
        y_vals.append(dfs['circle_coords'][i][1])

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


    return dfs, date_config, img_str, cropped_img, {
        'max_temp': max_temp,
        'min_temp': min_temp,
        'max_RH': max_RH,
        'min_RH': min_RH,
        'max_dp': max_dp,
        'min_dp': min_dp,
        'max_lt': max_lt,
        'min_lt': min_lt,
        'x_vals': x_vals,
        'y_vals': y_vals,
        't_array': t_array,
        'rh_array': rh_array,
        'pressure': pressure,
        'labels': labels,
        't_shade': t_shade,
        'hr_40': hr_40,
        'hr_60': hr_60
    }    
