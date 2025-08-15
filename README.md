## Welcome to the LACMA David Geffen Galleries Dashboard!
In this repository you will find the python script for a Dash-based application that creates a webpage that links to data being collected on 77 different Hobo environmental monitors around the David Geffen Galleries.

The main code for deploying the Dashboard is app.py which is currently being continually updated to add new features and fix bugs. 

requirements.txt is the virtual environment with all of the Python packages needed to run the script. I used Python 3.13.

The Data folder contains pickle files that are dataframes processed from the Hobo monitor data, which are generated locally on my (Jazmyn's) laptop. The hobo monitors are *not* live, so Data is updated weekly. These pickle files exist to cut down on data processing times, as the excel files only really need to be read through and cleaned-up when collected.

The galleryInfo folder contains DGG information such as the map, coordinates of Hobo monitors (DGG_coords.pkl), gallery materials, and locations of the testo monitors (which are updated live, so I may integrate that into the dashboard in the future if it is found to be necessary).

The assets folder are some css files to stylize the Dashboard (to be updated later)
