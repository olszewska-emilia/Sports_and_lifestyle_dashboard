"""Weather enrichment and wind visualization."""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from training_insights.weather import load_weather_data

def merge_weather(df):
    df = df.copy()
    df["timestamp_rounded"] = pd.to_datetime(df["timestamp"], utc=True).dt.floor("h")
    return df.merge(load_weather_data(), left_on="timestamp_rounded", right_on="date", how="left").drop(columns="date")

def plot_wind_effect(df_merged):
    activities = df_merged[df_merged["total_distance@km"]>10]
    mask_wind = activities["wind_speed_10m"] > 15
    strong_wind = activities[mask_wind]
    light_wind = activities[~mask_wind]
    clean = activities[["avg_speed@km/h","wind_speed_10m"]].copy()
    clean = clean.replace([np.inf, -np.inf], np.nan).dropna()

    x = clean["avg_speed@km/h"].values
    y = clean["wind_speed_10m"].values
    m, b = np.polyfit(x, y, 1)
    x_line = np.linspace(x.min(), x.max(), 100)
    y_line = m * x_line + b
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=strong_wind["avg_speed@km/h"],
        y=strong_wind["wind_speed_10m"],
        mode='markers',
        name='silny wiatr >15 km/h',
        marker=dict(color='mediumvioletred', opacity=0.6)
    ))

    fig.add_trace(go.Scatter(
        x=light_wind["avg_speed@km/h"],
        y=light_wind["wind_speed_10m"],
        mode='markers',
        name='słaby wiatr ≤15 km/h',
        marker=dict(color='lightpink', opacity=0.6)
    ))

    fig.add_trace(go.Scatter(
        x=x_line,
        y=y_line,
        mode='lines',
        name=f'linia trendu',
        line=dict(dash='dash', color='deeppink')
    ))

    fig.update_layout(
        title='wpływ wiatru na średnią prędkość',
        xaxis_title='średnia prędkość (km/h)',
        yaxis_title='prędkość wiatru (km/h)',
        legend=dict(bordercolor="gray", borderwidth=0.5),
        template='simple_white'
    )
    return fig
