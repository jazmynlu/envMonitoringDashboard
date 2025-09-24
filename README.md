# Welcome to the LACMA David Geffen Galleries Dashboard!

## About
This overarching project aims to collect environmental data on LACMA's David Geffen Galleries (DGG) and to monitor the collection closely for any damage, especially through LACMA's transition into the Bizot Green Protocol. There are 77 Hobo monitors set up in various areas around the building, collecting data every 15 minutes on the Temperature, Relative Humidity, and Light levels. The monitors are NOT connected to WiFi, so every week or two, someone has to physically go and collect data with a Bluetooth-enabled device. 

The dashboard aims to make the data collected from these monitors more accessible and easy to comprehend for the conservation and installation teams to better visualize changes in temperature, relative humidity, and light levels in the exhibition level of DGG. These three parameters have a huge impact on the longevity of the objects, especially considering they are on long-term display. We are also trying to analyze how well the building conforms to the Bizot Green Protocol, which stipulates that the gallery must remain between 16-25 °C and 40-60% relative humidity (with a maximum daily fluctuation of ±10%), and have light levels ideally below 250 lux for light-sensitive objects.

Within the Dashboard, there are seven tabs for data visualization: 
* **Map View** - Gives a bird's eye view of all sensors in DGG with the ability to choose aggregated statistics of a given environmental parameter (Average Temperature, Averaged Temperature Daily Ranges, etc.) over a specified time period.
* **Daily Map View**- Gives a bird's eye view of all sensors in DGG at a specific date, time, and environmental parameter
* **Time Series** - Shows time series plots for all environmental parameters over a specified date period. Designed to compare multiple sensors at a time. There is a toggle to show or hide data that does not reflect that sensor location (for instance, when a sensor is moved to a different location for art installation)
* **Time Series Single** - Designed to study one sensor at a time, over a specified time period, and provide more detail on the data of that sensor. Cumulative Light Exposure over the specified time period is provided at the bottom. 
* **Psychrometric View** - Plots multiple sensors together over a given time period on a psychrometric chart. The Bizot Standard is highlighted for easy comparison
* **HVAC Comparison** - Plots a psychrometric chart of one sensor before the HVAC system, after the HVAC system, and data from a nearby weather station. Highlights how the building envelope and HVAC systems changes temperature and humidity. 
* **Weather** - Plots a time series of all available weather station data located near the Grove

## About 'envMonitoringDashboard'
### Root Files
- `README.md` — project documentation  
- `app.py` — main script to run for Dashboard deployment  
- `create_base_fig.py` — function to create map view graphs  
- `data_loaders.py` — loads and organizes preprocessed data and initializes dashboard  
- `layouts.py` — defines the layout of the webpage  
- `requirements.txt` — list of Python package requirements to run  

---

### assets/  
CSS files to define styles in the Dashboard  
- `header.css`  
- `lacma-logo.png`  
- `tabs.css`  
- `typography.css`  

---

### Data/  
Folder that holds all data processed in `data_loaders.py`. All new data will be populated here, and older versions will be in the archive folder.
- `archive/` — ignore files in this folder!  
- `moving_7day_average_xxxx2025.pkl`  
- `moving_7day_range_xxxx2025.pkl`  
- `moving_24hour_average_xxxx2025.pkl`  
- `moving_24hour_range_xxxx2025.pkl`  
- `postHVACdata_xxxx2025.pkl`  
- `preHVACdata.pkl`  
- `wunderground_xxxx2025.pkl`  

---

### galleryInfo/  
Information related to DGG  
- `2025 - DGG Exhibition Level Blueprint (LACMA).jpg`  
- `DGG_coords.pkl`  
---

### logs/  
Folder for logging errors  
- `errors.log`  

---

### setup/  
Folder of txt files that need to be manually updated every data update!  
- `df_config.txt` — connects variable name in `data_loaders.py` to specific file name  
- `sensor_movement.csv` — organizes dates and sensors with incorrect information  
- `set_dates.txt` — sets minimum and maximum dates to show in the dashboard (manual update required)  
- `set_dates_preHVAC.txt`  


## To run:
    python app.py
