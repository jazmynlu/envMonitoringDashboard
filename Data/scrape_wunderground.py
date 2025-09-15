#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Module to scrape 5-min personal weather station data from Weather Underground.

Usage is:
>>> python scrape_wunderground.py   STATION    DATE     FREQ

where station is a personal weather station (e.g., KCAJAMES3), date is in the
format YYYY-MM-DD and FREQ is either 'daily' or '5min' (for daily or 5-minute
observations, respectively).

Alternatively, each function below can be imported and used in a separate python
script. Note that a working version of chromedriver must be installed and the absolute
path to executable has to be updated below ("chromedriver_path").

Zach Perzan, 2021-07-28"""

import time
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup as BS
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

# Set the absolute path to chromedriver
chromedriver_path = r'C:\Users\jlu.LACMA\Documents\envMonitoring\Dashboard\Data\chromedriver-win64\chromedriver.exe'


def render_page(url):
    """Given a url, render it with chromedriver and return the html source

    Parameters
    ----------
        url : str
            url to render

    Returns
    -------
        r :
            rendered page source
    """

    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service)
    #driver = webdriver.Chrome(chromedriver_path)
    driver.get(url)
    time.sleep(3) # Could potentially decrease the sleep time
    r = driver.page_source
    driver.quit()

    return r

def scrape_wunderground(station, date, freq='5min'):
    """Scrape Weather Underground PWS data (5-min or daily summary).

    Parameters
    ----------
    station : str
        The personal weather station ID
    date : str
        The date for which to acquire data, formatted as 'YYYY-MM-DD'
    freq : {'5min', 'daily'}
        Whether to download 5-minute weather observations or daily summaries.

    Returns
    -------
    df : DataFrame
        Weather observations, indexed by timestamp.
    """

    # WU table naming conventions
    if freq == '5min':
        timespan = 'daily'
    elif freq == 'daily':
        timespan = 'monthly'
    else:
        raise ValueError("freq must be '5min' or 'daily'")

    # Render the page
    url = f'https://www.wunderground.com/dashboard/pws/{station}/table/{date}/{date}/{timespan}'
    r = render_page(url)
    soup = BS(r, "html.parser")

    container = soup.find('lib-history-table')
    if container is None:
        raise ValueError(f"could not find lib-history-table in html source for {url}")

    # Separate time and data sections
    all_checks = container.find_all('tbody')
    time_check = all_checks[0]
    data_check = all_checks[1]

    # Timestamps
    hours = [tr.get_text(strip=True) for tr in time_check.find_all('tr')]

    # Row-wise data parsing
    rows = []
    for tr in data_check.find_all("tr"):
        cells = []
        for td in tr.find_all("td"):
            # try to find value
            strong = td.find("strong")
            span   = td.find("span", class_=["wu-value", "wu-value-to",
                                             "wu-unit-no-value", "ng-star-inserted"])
            if strong:
                cells.append(strong.get_text(strip=True))
            elif span:
                cells.append(span.get_text(strip=True))
            else:
                cells.append("--")  # placeholder for missing
        rows.append(cells)

    # Column definitions
    if freq == '5min':
        columns = [
            'time','Temperature', 'Dew Point', 'Humidity', 'Wind Direction',  'Wind Speed',
            'Wind Gust', 'Pressure', 'Precip. Rate', 'Precip. Accum',
            'UV Index', 'Solar Radiation', 
        ]
    else:  # daily
        columns = [
            'Temperature_High', 'Temperature_Avg', 'Temperature_Low',
            'DewPoint_High', 'DewPoint_Avg', 'DewPoint_Low',
            'Humidity_High', 'Humidity_Avg', 'Humidity_Low',
            'WindSpeed_High', 'WindSpeed_Avg', 'WindSpeed_Low',
            'Pressure_High', 'Pressure_Low', 'Precip_Sum',
            'UV_Index_High', 'UV_Index_Avg', 'UV_Index_Low',
            'SolarRadiation_High', 'SolarRadiation_Avg', 'SolarRadiation_Low'
        ]

    # Flatten rows
    data_array = np.array(rows, dtype=object)

    # Convert '--' to NaN, keep wind direction as string
    clean_data = []
    for row in data_array:
        clean_row = []
        for val in row:
            if val == '--':
                clean_row.append(np.nan)
            else:
                # wind direction is categorical (letters), don’t cast
                if isinstance(val, str) and not val.replace('.', '', 1).isdigit():
                    clean_row.append(val)
                else:
                    try:
                        clean_row.append(float(val))
                    except ValueError:
                        clean_row.append(val)
        clean_data.append(clean_row)

    # Prepend date to HH:MM timestamps for 5min freq
    if freq == '5min':
        timestamps = [f"{date} {t}" for t in hours]
    else:
        timestamps = hours

    # DataFrame
    df = pd.DataFrame(index=timestamps, data=clean_data, columns=columns)
    df=df.drop('time',axis=1)

    return df


def scrape_multiattempt(station, date, attempts=4, wait_time=5.0, freq='5min'):
    """Try to scrape data from Weather Underground. If there is an error on the
    first attempt, try again.

    Parameters
    ----------
        station : str
            The personal weather station ID
        date : str
            The date for which to acquire data, formatted as 'YYYY-MM-DD'
        attempts : int, default 4
            Maximum number of times to try accessing before failuer
        wait_time : float, default 5.0
            Amount of time to wait in between attempts
        freq : {'5min', 'daily'}
            Whether to download 5-minute weather observations or daily
            summaries (average, min and max for each day)

    Returns
    -------
        df : dataframe or None
            A dataframe of weather observations, with index as pd.DateTimeIndex
            and columns as the observed data
    """

    # Try to download data limited number of attempts
    for n in range(attempts):
        try:
            df = scrape_wunderground(station, date, freq=freq)
        except:
            # if unsuccessful, pause and retry
            time.sleep(wait_time)
        else:
            # if successful, then break
            break
    # If all attempts failed, return empty df
    else:
        df = pd.DataFrame()

    return df


def scrape_multidate(station, start_date, end_date, freq):
    """Given a PWS station ID and a start and end date, scrape data from Weather
        Underground for that date range and return it as a dataframe.

        Parameters
        ----------
            station : str
                The personal weather station ID
            start_date : str
                The date for which to begin acquiring data, formatted as 'YYYY-MM-DD'
            end_date : str
                The date for which to end acquiring data, formatted as 'YYYY-MM-DD'

        Returns
        -------
            df : dataframe or None
                A dataframe of weather observations, with index as pd.DateTimeIndex
                and columns as the observed data
        """
    # Convert end_date and start_date to datetime types
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()

    # Calculate time delta
    delta = end_date - start_date

    # Create list dates and append all days within the start and end date to dates
    dates = []
    for i in range(delta.days + 1):
        day = start_date + timedelta(days=i)
        dates.append(day)
    dates = [date.strftime('%Y-%m-%d') for date in dates]

    # Repeat the station name in a list for as many dates are in the date range
    stations = [station] * len(dates)

    # Scrape wunderground for data from all dates in range and store in list of dateframes
    df_list = [scrape_multiattempt(st, dt, freq=freq) for st, dt in zip(stations, dates)]

    # Convert list of dataframes to one dataframe
    df = pd.concat(df_list)

    return df

#%%
df = scrape_multidate('KCALOSAN1069','2025-01-01', '2025-08-28', freq='5min')
#df.to_csv('output.csv', index = True)