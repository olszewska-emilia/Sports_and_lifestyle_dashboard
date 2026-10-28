# Training Insights

![Python](https://img.shields.io/badge/Python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)

An interactive data visualization dashboard designed to explore physical activity, understand how weather relates to training habits, and discover similar running routes. The application brings together activity records, GPS tracks, and historical Melbourne weather through a Streamlit interface, complete with tea animations and playful insights into the dataset.

## About this repository

Built as a university data analysis project (PDU) by **Aleksandra Mulewicz, Emilia Olszewska, and Nina Onyszczuk**, Training Insights explores patterns in running, cycling, and walking activities. It combines data preparation, interactive charts, geographic analysis, and two historical route recommendation methods in one application.

The frontend is built with **Streamlit**, while reusable Python modules handle activity processing, heart-rate classification, weather matching, and route ranking. Some chart labels and exploratory comments are in Polish.

## Application Overview

The application is divided into five sections accessible through the sidebar:

- **Overview:** An introduction to the project, its authors, technologies, and observations about activity preferences in the original dataset.
- **Data Visualisation:** Interactive charts showing activity patterns by weekday, month, and temperature, alongside intensity comparisons and a heart-rate zone treemap.
- **Nobody Expects The Spanish Inquisition:** A playful look at training data, turning performance and energy expenditure into unexpected comparisons.
- **Plotly Map Visualisation:** Geographic views of training start points and route centroids, with distance and maximum speed adding context to the maps.
- **Recommendation System:** Two ways to explore recorded running routes: by distance, duration, calories, and intensity, or by distance and weather conditions such as temperature, rain, wind, and cloud cover.

### Technical Highlights

- **Data Pipeline:** Loads activity summaries from JSON and route samples from CSV, prepares timestamps, and combines training records with an hourly weather snapshot.
- **Heart-Rate Analysis:** Filters outliers using a three-standard-deviation threshold and groups measurements into six relative intensity zones based on the maximum observed heart rate.
- **Geographic Visualization:** Uses Plotly for interactive maps of activity locations and recorded tracks. OpenStreetMap tiles are available by default, with optional Mapbox styling.
- **Route Recommendations:** Standardizes selected features and ranks historical running activities by Pearson correlation with the requested feature vector, returning up to five matches.
- **Weather Exploration:** Matches activity timestamps to hourly observations and supports exploratory analysis of weather, performance, and energy expenditure. Weather downloads are handled by a separate script using Open-Meteo.

## Tech Stack

| Layer | Technology |
| --- | --- |
| **Frontend** | Streamlit, streamlit-option-menu, streamlit-lottie |
| **Data Processing** | Pandas, NumPy |
| **Visualizations** | Plotly, Matplotlib, Seaborn |
| **Weather Data** | Open-Meteo, openmeteo-requests, requests-cache, retry-requests |
| **Maps** | Plotly, OpenStreetMap, optional Mapbox |
| **Testing** | Python unittest |

---

## Setup & Installation

Use **Python 3.11 or newer**. Run the following commands from the repository root.

### 1. Create a virtual environment and install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows PowerShell, activate the environment with `.venv\Scripts\Activate.ps1`.

### 2. Add your training data

Personal training exports are not included. Create and populate these directories:

```text
data/raw/json/    # One activity summary object per JSON file
data/raw/csv/     # CSV files containing recorded route samples
```

The dashboard expects the original course export schema, including field names and units. It does not directly import FIT or GPX files.

| Input | Expected fields |
| --- | --- |
| **Activity summaries** | `timestamp`, `start_time`, `sport`, `avg_heart_rate@bpm`, `avg_temperature@C`, `avg_speed@km/h`, `total_distance@km`, `total_elapsed_time@s`, `total_timer_time@s`, `total_calories@kcal`, `enhanced_max_speed@km/h` |
| **Activity coordinates** | `start_position_lat@deg`, `start_position_long@deg`, `nec_lat@deg`, `nec_long@deg`, `swc_lat@deg`, `swc_long@deg` |
| **Route samples** | `timestamp`, `position_lat@deg`, `position_long@deg`, `heart_rate@bpm`, `distance@km`, `speed@km/h`, `cadence@rpm`, `step_length@mm` |

Exploratory scripts may require additional fields from the original exports. Keep personal training exports and credentials out of version control.

### 3. Configure optional settings

Configuration uses environment variables; no API credentials are required for the default map tiles or bundled weather data.

| Variable | Default | Purpose |
| --- | --- | --- |
| `MAPBOX_TOKEN` | Empty | Enables the original Mapbox styling |
| `PDU_JSON_DATA_DIR` | `data/raw/json` | Activity summary directory |
| `PDU_CSV_DATA_DIR` | `data/raw/csv` | Route sample directory |
| `PDU_WEATHER_DATA_PATH` | `data/weather/hourly_data.csv` | Weather snapshot location |

Relative paths resolve from the repository root. Absolute paths can point to exports stored elsewhere. Set variables in your terminal before launching the app; `.env` files are not loaded automatically.

### 4. Run the application

```bash
python -m streamlit run app.py
```

Open the local URL printed by Streamlit. If training exports are missing, the app displays setup instructions.

## Data & Recommendation Notes

The bundled weather snapshot covers **Melbourne from 29 August 2019 to 21 March 2024**. Activities outside this period will not have matching observations. Activity and route matching uses UTC timestamps, while activity calendar charts use Melbourne local time.

Recommendations retrieve similar historical activities and their recorded routes. They do not generate new routes or use live weather forecasts. Heart-rate zones describe the supplied dataset and are not personalized physiological thresholds.

The dashboard was designed for a sufficiently populated dataset containing running, cycling, and walking. Some charts and the five-route selector require enough complete records; sparse or differently structured exports may need adaptation.

## Project Structure

```text
app.py                      Streamlit entry point
training_insights/
  config.py                 Environment variables and paths
  data.py                   Activity and route loaders
  weather.py                Weather snapshot reader
  heart_zones.py            Heart-rate filtering and classification
  visualization.py          Shared maps and charts
  analysis/                 Activity, heart-rate, and weather analyses
  recommendations/          Activity-based and weather-based route ranking
scripts/                    Exploratory analyses and weather download
assets/animations/          Tea animation
data/weather/               Bundled hourly Melbourne weather
tests/                      Automated regression checks
```

## Development

Run the regression checks with:

```bash
python -m unittest discover -s tests -v
```

Run the original exploratory analyses with:

```bash
python -m scripts.explore_routes
python -m scripts.explore_weather
python -m scripts.explore_energy
```

To download weather data again, run the command below. It requires internet access and replaces the configured weather CSV.

```bash
python -m scripts.download_weather
```

## Authors

**Aleksandra Mulewicz · Emilia Olszewska · Nina Onyszczuk**  
University data analysis project (PDU).
