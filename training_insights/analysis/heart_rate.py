"""Heart-rate classification and zone summaries."""
import numpy as np
import pandas as pd
import plotly.express as px
from training_insights.data import load_data_csv
from training_insights.config import CSV_DATA_DIR
from training_insights.heart_zones import HeartZoneClassifier


def load_classified_routes():
    df = load_data_csv(CSV_DATA_DIR)
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    df['date'] = df['timestamp'].dt.date
    return HeartZoneClassifier(df).assign_zones()


def plot_heart_zone_treemap(classified_df):
    df_grouped = classified_df.groupby("zone").agg(
        total_distance_km=("distance@km", 'sum'),
        average_distance_km=("distance@km", 'mean'),
        average_speed=("speed@km/h", 'mean'),
        average_cadence=("cadence@rpm", 'mean'),
        average_heart_rate = ("heart_rate@bpm", 'mean'),
        average_step_length = ("step_length@mm", 'mean'),
        num_of_trainings = ("date", "count")).reset_index()
    fig = px.treemap(
        df_grouped,
        path=["num_of_trainings","zone"],
        color='total_distance_km',
        hover_data={
            "average_heart_rate": ':.2f',
            "total_distance_km": ':.2f',
            "average_distance_km": ':.2f',
            "average_speed": ':.2f',
            "average_cadence": ':.2f',
            "average_step_length": ':.2f'
        },
        color_continuous_scale='Magenta',
        color_continuous_midpoint=np.average(
            df_grouped["average_speed"],
            weights=df_grouped["average_cadence"]
        )
    )

    fig.update_layout(title_text="zones and number of trainings in each of them", margin=dict(t=50, l=25, r=25, b=25))
    return fig
