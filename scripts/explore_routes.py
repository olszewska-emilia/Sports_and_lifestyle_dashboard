#%% md
# IMPORTS (ladniej napisane)
#%%
from training_insights.data import load_data_json
from training_insights.visualization import heatmap_plotly, plotly_hex_map, plotly_scatter_map, plotly_points_map
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from training_insights.config import JSON_DATA_DIR as filename_json, CSV_DATA_DIR as filename_csv, MAPBOX_TOKEN as map_token

#%% md
# EXPLANATORY DATA ANALYSIS
#%%
df = load_data_json(filename_json)
df.describe()
#%%
df_running = df[df["sport"] == "running"]
df_running['total_calories@kcal'].max()
#%%
df.columns
#%%
ax = plt.axes()
sns.heatmap(df.isna().transpose(), cbar=False, cmap="YlGnBu", ax = ax)
plt.xlabel("Missing Values")
plt.ylabel("Columns")
plt.show()
#%%
heatmap_plotly(df)
#%%
## Zmiana typu pierwszych kolumn na datetime
df_json = df
df_json['timestamp'] = pd.to_datetime(df_json['timestamp'])
df_json['start_time'] = pd.to_datetime(df_json['start_time'])

## Sortowanie po czasie rozpoczęcia treningu
df_json = df_json.sort_values('start_time').reset_index(drop=True)
#%%
## Zmiana strefy czasowej na australijską
df_json = df_json.set_index('timestamp').tz_convert('Australia/Melbourne').\
    tz_localize(None).reset_index(names='timestamp')

df_json = df_json.set_index('start_time').tz_convert('Australia/Melbourne').\
    tz_localize(None).reset_index(names='start_time')
#%%
df["date"] = df["start_time"].dt.date
counts = df["date"].value_counts()
counts
#%% md
#     DATA VISUALISATION
#%%
plotly_hex_map(df,
        lat="start_position_lat@deg",
        long="start_position_long@deg",
        map_token = map_token)
#%%
plotly_hex_map(df,
        lat="nec_lat@deg",
        long="nec_long@deg",
        map_token = map_token)
#%%
df['centroid_lat'] = df.apply(lambda row: (row['nec_lat@deg'] + row['swc_lat@deg']) / 2, axis=1)
df['centroid_lon'] = df.apply(lambda row: (row['nec_long@deg'] + row['swc_long@deg']) / 2, axis=1)
#%%
df['centroid_lat']
#%%
plotly_hex_map(df,
        lat="centroid_lat",
        long="centroid_lon",
        map_token = map_token)
#%%
plotly_scatter_map(df,
        map_token = map_token,
        lat="centroid_lat",
        lon="centroid_lon",
        color="enhanced_max_speed@km/h",
        size="total_distance@km" )

#%%
df['start_lat_rounded'] = df['start_position_lat@deg'].round(3)
df['start_lon_rounded'] = df['start_position_long@deg'].round(3)
start_counts = df.groupby(['start_lat_rounded', 'start_lon_rounded']).size().reset_index(name='count')

most_common_start = start_counts.loc[start_counts['count'].idxmax()]
most_common_start
#%%
plotly_points_map([-37.821], [144.9425], map_token, "Most common start")
#%%
import plotly.graph_objects as go

fig = go.Figure()
help(fig.update_layout)
