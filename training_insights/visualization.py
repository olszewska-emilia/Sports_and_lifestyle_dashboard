import numpy as np
import pandas as pd

import plotly.figure_factory as ff
import plotly.express as px
import plotly.graph_objects as go


def heatmap_plotly(df):
    """

    :param df: DataFrame
    :return: figure

    """
    correlation_matrix = df.corr(numeric_only=True)
    fig = px.imshow(
        correlation_matrix,
        color_continuous_scale='BuPu',
        title="Correlation Matrix",
        zmin=-1, zmax=1
    )

    fig.update_layout(
        xaxis=dict(tickfont=dict(size=1)),  # Bigger heatmap, smaller text, relying on hover
        yaxis=dict(tickfont=dict(size=1)),
        margin={"r": 15, "t": 15, "l": 15, "b": 15}
    )
    return fig

def plotly_hex_map(df, lat,long, map_token):
    """

    inspired by: https://www.kaggle.com/code/shtrausslearning/geospatial-data-visualisation-australia
    :param df: DataFrame
    :param lat: Column Name, String
    :param long: Column Name, String
    :param map_token: personal token generated using https://www.mapbox.com
    :return: figure

    """
    fig = ff.create_hexbin_mapbox(
        data_frame=df, lat=lat, lon=long,
        nx_hexagon=200, opacity=0.5, labels={"color": "Point Count"},
        range_color=[0, 20],
        color_continuous_scale="BuPu",
        show_original_data=True,
        original_data_marker=dict(size=3, opacity=0.25, color='black'),
        zoom=10, height=600,
    )

    fig.update_layout(
        hovermode='closest',
        mapbox=dict(
            accesstoken=map_token or None,
            bearing=90, #Sets the bearing angle of the map in degrees counter-clockwise from North
            center=dict(lat=-37.840935, lon= 144.946457),  # Melbourne
            pitch=60, #Sets the pitch angle of the map (in degrees) - documentation
            zoom=10
        ),
        margin={"r": 15, "t": 15, "l": 15, "b": 15}, mapbox_style="light" if map_token else "open-street-map"
    )

    return fig
def plotly_scatter_map(df, map_token, lat, lon, color, size, palette = "BuPu"):
    """

    :param df: DataFrame
    :param map_token: mapbox token
    :param lat: latitude as a list
    :param lon: longitude as a list
    :param color: the column in dataset responsible for color change
    :param size: the column in dataset responsible for size change
    :return: figure

    """
    fig = px.scatter_mapbox(
        df,
        lat=lat,
        lon=lon,
        color=color,
        size=size,
        color_continuous_scale=palette,
        size_max=15
    )

    fig.update_layout(
        mapbox_style="light" if map_token else "open-street-map",
        hovermode="closest",
        mapbox=dict(
            accesstoken=map_token or None,
            bearing=90,
            center=dict(lat=-37.8136, lon=144.9631),
            pitch=60,
            zoom=12
        ),
        margin={"r": 15, "t": 15, "l": 15, "b": 15},
        height=600
    )

    return fig


def plotly_points_map(lat, lon, map_token, label):
    """

    :param lat: lattitude as a list
    :param lon: longitude as a list
    :param map_token: a map token
    :param label: the name of the plot
    :return: figure

    """
    fig = go.Figure(go.Scattermapbox(
        lat=lat,
        lon=lon,
        mode='markers+text',
        marker=dict(size=15, color='purple'),
        text=[label],
        textposition="top center",
        name=label
    ))

    fig.update_layout(
        mapbox=dict(
            accesstoken=map_token or None,
            center=dict(lat=lat[0], lon=lon[0]),  # UWAGA: lat i lon to listy!
            pitch=60,
            zoom=15,
            style="light" if map_token else "open-street-map"
        ),
        margin={"r": 15, "t": 15, "l": 15, "b": 15},
        height=600,
        title=label.upper(),
        showlegend=False,
        font=dict(family="Arial Black")
    )

    return fig

def plotly_treemap_sports(df):
    """

    inspired by: https://plotly.com/python/treemaps/
    :param df: DataFrame
    :return: figure

    """
    df_grouped = df.groupby(["sport", "sub_sport"]).agg({
        "total_distance@km": "sum",
        "avg_speed@km/h": "mean",
        "avg_step_length@mm": "mean",
        "avg_running_cadence@strides/min": "mean",
        "avg_heart_rate@bpm": "mean"
    }).reset_index()

    fig = px.treemap(df_grouped,
                     path=["sport"],
                     color='avg_heart_rate@bpm',
                     hover_data=[
                         'sub_sport',
                         "total_distance@km",
                         "avg_speed@km/h",
                         "avg_step_length@mm",
                         "avg_running_cadence@strides/min"
                     ],
                     color_continuous_scale='BuPu',
                     color_continuous_midpoint=np.average(
                         df_grouped['avg_heart_rate@bpm'],
                         weights=df_grouped['avg_running_cadence@strides/min']
                     )
                     )
    fig.update_layout(margin={"r": 15, "t": 15, "l": 15, "b": 15})
    return fig
