# Colorado-Crimes-Dashboard

Colorado Crimes Dashboard is a data visualization project that gives some insights into crime trends that were reported in Colorado from 2016 to 2023. It features a choropleth map showing the crime distribution across counties, in which users can click on a county to see a more detailed breakdown of top crimes in the area via a bar chart; both years and crime categories can be filtered for this view. The tabbed section allows for a statewide view of crime trends which are influenced by the selected year. Lastly, the profile summary gives a quick snapshot of the crimes in the state; this was meant to fill in the gap below the map without overwhelming the user with too much information.

## Data Source
The data was sourced from [Colorado Information Marketplace](https://data.colorado.gov/Public-Safety/Crimes-in-Colorado/j6g4-gayk/about_data). This was the most relevant data I could find as of June 2026, however, it gave a good, ecompassing view of how crimes have evolved in Colorado over the years. 

## County Mapping
The county borders file was taken from [Colorado Counties GeoJSON](https://github.com/earthlab/earthpy/blob/main/earthpy/example-data/colorado-counties.geojson?short_path=251016f) and was used to create the choropleth map in the dashboard.

## Libraries Used
- Dash: For building the interactive web app
- Plotly: For creating the viz
- Pandas: For reading and manipulating the data


## Directions for Use
> **Note**: Github does not support files over 100MB, so I have used lfs to store the colorado crimes csv file. If you clone the repository, make sure to install git lfs and pull the file thereafter.


1. Clone the repository local machine and install required libraries
2. Make sure to download the data files using git lfs
3. Run `main.py` to start the Dash app
4. Open the localhost URL (most likely localhost:8050) in a web browser to interact with the dashboard

