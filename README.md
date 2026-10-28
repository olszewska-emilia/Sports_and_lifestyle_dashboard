# Training Insights

An interactive Python dashboard for exploring physical activity, understanding weather patterns, and finding similar running routes. Built as a university data analysis project (PDU) by **Aleksandra Mulewicz, Emilia Olszewska, and Nina Onyszczuk**.

![Training Insights demo](docs/media/demo.gif)

[Original intro animation](docs/media/intro.gif) · [Project presentation](docs/presentation.pdf)

## Features

- Activity summaries by weekday, month, sport, and temperature.
- Heart-rate outlier filtering and six relative intensity zones.
- Geographic visualizations of training start points, route centroids, and recorded tracks.
- Running route recommendations based on distance, duration, calories, and intensity, or on distance and weather conditions.
- Exploratory comparisons of wind, rainfall, performance, and energy expenditure.

The interface retains the original project's tea animations and playful dataset facts. Some chart labels and exploratory comments are in Polish.

## Quick start

Use Python 3.11 or newer. Run the commands from the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local URL printed by Streamlit. Without training exports, the app displays setup instructions. **Personal training data is not included**, so the complete dashboard requires the data described below. The GIF and presentation provide a preview without installing anything.

## Data and configuration

Place your extracted exports in:

```text
data/raw/json/   # One activity summary object per .json file
data/raw/csv/    # Route samples in .csv files, concatenated by the loader
```

These directories are ignored by Git except for their placeholder files. This project expects the original course export schema; it is not a general-purpose Garmin/FIT/GPX importer. Keep the field names, including units, intact.

| Input | Fields used by the dashboard |
| --- | --- |
| Activity JSON | `timestamp`, `start_time`, `sport`, `avg_heart_rate@bpm`, `avg_temperature@C`, `total_distance@km`, `total_elapsed_time@s`, `total_timer_time@s`, `total_calories@kcal`, `enhanced_max_speed@km/h` |
| Activity coordinates | `start_position_lat@deg`, `start_position_long@deg`, `nec_lat@deg`, `nec_long@deg`, `swc_lat@deg`, `swc_long@deg` |
| Route CSV | `timestamp`, `position_lat@deg`, `position_long@deg`, `heart_rate@bpm`, `distance@km`, `speed@km/h`, `cadence@rpm`, `step_length@mm` |

Timestamps are normalized to UTC for weather and route matching. Activity calendar charts use Melbourne local time. The exploratory scripts use additional columns from the original export, such as cadence, strides, and ascent.

The bundled `data/weather/hourly_data.csv` contains hourly Melbourne weather for **29 August 2019–21 March 2024**. Activities outside this range will not have matching weather observations. The download script records the original archive request and variables.

Configuration uses environment variables:

| Variable | Default | Purpose |
| --- | --- | --- |
| `MAPBOX_TOKEN` | Empty | Optional token for Mapbox styling; otherwise OpenStreetMap tiles |
| `PDU_JSON_DATA_DIR` | `data/raw/json` | Activity export directory |
| `PDU_CSV_DATA_DIR` | `data/raw/csv` | Route export directory |
| `PDU_WEATHER_DATA_PATH` | `data/weather/hourly_data.csv` | Hourly weather snapshot |

Relative paths resolve from the repository root. You can use absolute paths for exports stored elsewhere.

For macOS/Linux, copy `.env.example` to `.env`, fill in your values, and load it before starting the app:

```bash
cp .env.example .env
# Edit .env, then:
set -a
source .env
set +a
python -m streamlit run app.py
```

The application does not automatically read `.env`. In PowerShell, set variables directly, for example `$env:MAPBOX_TOKEN = "your-token"`.

## Repository layout

```text
app.py                          Streamlit entry point
training_insights/
  config.py                     Environment variables and portable paths
  data.py                       JSON and CSV readers
  weather.py                    Local weather snapshot reader
  heart_zones.py                Heart-rate filtering and classification
  visualization.py              Shared Plotly maps and charts
  analysis/                     Activity, heart-rate, and weather analyses
  recommendations/              Activity-based and weather-based route ranking
scripts/                        Original explorations and explicit weather download
assets/animations/              Tea animation used in the dashboard
data/raw/                       Local-only activity and route exports
data/weather/                   Bundled hourly weather snapshot
docs/                           Presentation and original demo animations
tests/                          Automated regression checks
.github/workflows/              GitHub Actions checks
```

Reusable modules do not fetch weather, open plot windows, or load private training exports on import. Exploratory scripts intentionally execute analyses and display plots when run:

```bash
python -m scripts.explore_routes
python -m scripts.explore_weather
python -m scripts.explore_energy
```

To refresh the weather snapshot (requires internet access and replaces the configured weather CSV):

```bash
python -m scripts.download_weather
```

## How recommendations work

The app filters running activities, standardizes the selected features, and ranks historical activities by Pearson correlation with the requested feature vector. It returns up to five matches and selects recorded route points within each activity's time window.

Heart-rate zones are relative to the maximum observed heart rate after three-standard-deviation outlier filtering. They are dataset-derived categories, not personalized physiological thresholds. Weather matching uses the activity timestamp rounded down to the hour. This is an exploratory historical recommender, not a live weather forecast or route planner.

The original dashboard assumes a sufficiently populated dataset containing running, cycling, and walking activities. Some plots and the five-route selector require enough complete records. Sparse or differently structured exports may need additional adaptation.

## Development

```bash
python -m unittest discover -s tests -v
python -m compileall -q app.py training_insights scripts
```

GitHub Actions runs these checks on pushes and pull requests. The tests use synthetic records; they do not need private exports, API credentials, or network access.

## Publication notes and credits

- Keep personal training exports and `.env` files out of commits. GPS routes, timestamps, and health measurements may identify a person.
- The original source contained a Mapbox token. It has been removed from the working tree, but existing Git history can still contain it. Replace/revoke the old token before publishing that history; the cleanup does not rewrite commits.
- Demo animations and the presentation are preserved unchanged. Review their visible content and confirm permission to share the included materials and weather snapshot before public release.
- Weather data was obtained using Open-Meteo; the original request is preserved in `scripts/download_weather.py`. The tea animation source is recorded in the app's animation loader. Python, pandas, NumPy, Plotly, Matplotlib, Seaborn, Streamlit, and the listed integrations power the project.
- No open-source license has been selected. Public visibility alone does not grant permission to reuse the project; the authors should agree on a license before adding one.
