#%% md
# IMPORTS
#%%
from training_insights.data import load_data_json
from training_insights.visualization import heatmap_plotly, plotly_treemap_sports
from training_insights.weather import load_weather_data

hourly_dataframe = load_weather_data()

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

import plotly.graph_objects as go
from training_insights.config import JSON_DATA_DIR as filename_json, CSV_DATA_DIR as filename_csv, MAPBOX_TOKEN as map_token
#%% md
# EXPLANATORY DATA ANALYSIS
#%%
df = load_data_json(filename_json)
df.describe()
#%%
df
#%%
df.columns
#%%
ax = plt.axes()
sns.heatmap(df.isna().transpose(), cbar=False, cmap="BuPu", ax = ax)
plt.xlabel("Missing Values")
plt.ylabel("Columns")
plt.show()
#%%
heatmap_plotly(df)
#%% md
# DATA CLEANING
#%%
df_weather = hourly_dataframe
df['timestamp'] = pd.to_datetime(df['timestamp'])
df_weather['date'] = pd.to_datetime(df_weather['date'])
df['timestamp_rounded'] = df['timestamp'].dt.floor('h')
df_merged = pd.merge(
    df,
    df_weather,
    left_on='timestamp_rounded',
    right_on='date',
    how='left'
)
df_merged = df_merged.drop(columns=['date'])
df_merged.columns
#%% md
#     DATA VISUALISATION
#%%

#%%
#plotly_points_map(-37.821, 144.9425, map_token, "Most common start")
#%%
plotly_treemap_sports(df)
#%%
df_merged['rain_flag'] = df_merged['rain'] > 0

grouped = df_merged.groupby('rain_flag')['total_distance@km'].mean().reset_index()

fig = go.Figure()
fig.add_trace(go.Bar(
    x=['no rain ;)', 'rain ;('],
    y=grouped['total_distance@km'],
    name='avg distance',
    marker_color=['#002654', '#0097db']
))
fig.update_layout(
    title='distance vs rain',
    yaxis_title='avg distance'
)
fig.show()

#%%
