"""Activity preparation and calendar/temperature charts."""
import pandas as pd
import datetime
import calendar

import plotly.express as px
import plotly.graph_objects as go

from training_insights.data import load_data_json
from training_insights.config import JSON_DATA_DIR

def load_activity_summary():
    df_json = load_data_json(JSON_DATA_DIR)
    df_json['timestamp'] = pd.to_datetime(df_json['timestamp'], utc=True)
    df_json['start_time'] = pd.to_datetime(df_json['start_time'], utc=True)
    df_json = df_json.sort_values('start_time').reset_index(drop=True)
    df_json = df_json.set_index('timestamp').tz_convert('Australia/Melbourne').\
        tz_localize(None).reset_index(names='timestamp')
    df_json = df_json.set_index('start_time').tz_convert('Australia/Melbourne').\
        tz_localize(None).reset_index(names='start_time')
    df_json.insert(1, 'day', df_json['timestamp'].dt.strftime('%A'))
    df_json.insert(2, 'start', df_json['start_time'].dt.time)
    df_json['timestamp'] = df_json['timestamp'].dt.time
    df_json['start_time'] = df_json['start_time'].dt.date
    df_json = df_json.rename(columns={'start_time':'date', 'start':'start_time', 'timestamp':'end_time'})
    df_json['date'] = pd.to_datetime(df_json['date'])
    q = df_json[df_json['sport']=='walking']['avg_heart_rate@bpm'].quantile([0.,0.25,0.5,0.75,1.])
    iqr = q.iloc[3] - q.iloc[1]
    high_end = q.iloc[3] + 1.5*iqr
    i = df_json[(df_json['sport']=='walking') & (df_json['avg_heart_rate@bpm'] > high_end)].index
    df_json = df_json.drop(i).reset_index(drop=True)
    return df_json

def plot_activity_by_weekday(df_json):
    day_counts = df_json.groupby(['sport', 'day']).size().reset_index(name='counts')

    day_sorted = pd.DataFrame({'day': [datetime.date(2025,9,i).strftime('%A') for i in range(1,8)]})
    day_plot = day_sorted.merge(day_counts, how='left', on='day')
    day_plot['sport'] = day_plot['sport'].str.capitalize()

    fig = px.bar(day_plot, x='day', y='counts', color='sport', color_discrete_map={
        'Cycling':  'rgb(177, 77, 142)',
        'Hiking': 'rgb(202, 105, 157)',
        'Running': 'rgb(221, 136, 172)',
        'Walking': 'rgb(234, 169, 189)'
    }, width=600, range_y=[0,300],
    labels={'day':'Day of the week', 'counts':'Quantity of activity', 'sport':'Activity type'})
    fig.update_layout(title_text='The amount of activity depending on the day of the week')
    return fig
def plot_activity_by_month(df_json):
    year_month = df_json.groupby([df_json['date'].dt.year.rename('year'), df_json['date'].dt.month.rename('month')]).size().\
        reset_index(name='counts')
    year_month.sort_values(['year','month'])

    unique_years = pd.DataFrame({'year': df_json['date'].dt.year.unique()})
    unique_months = pd.DataFrame({'month': [i for i in range(1,13)], 'month_name': [datetime.date(2025, i, 1).strftime('%B') for i in range(1, 13)]})

    full = unique_years.merge(unique_months, how='cross')

    full_year_month = full.merge(year_month, how='left', on=['year','month']).fillna(0)
    full_year_month['counts'] = full_year_month['counts'].astype(int)


    heat = full_year_month.pivot(index='year', columns='month', values='counts')

    fig = px.imshow(heat, color_continuous_scale='magenta', zmin=0, zmax=60,
                    labels=dict(x='Month', y='Year', color='Quantity'), x=list(calendar.month_name)[1:])
    fig.update_layout(title_text='The amount of activity depending on the year and month')
    return fig

## WYKRES 3
## The amount of activity depending on temperature.
def plot_activity_by_temperature(df_json):
    cycling = df_json[df_json['sport']=='cycling'].groupby(['avg_temperature@C']).size().reset_index(name='counts')
    running = df_json[df_json['sport']=='running'].groupby(['avg_temperature@C']).size().reset_index(name='counts')
    walking = df_json[df_json['sport']=='walking'].groupby(['avg_temperature@C']).size().reset_index(name='counts')
    hiking = df_json[df_json['sport']=='hiking'].groupby(['avg_temperature@C']).size().reset_index(name='counts')

    counts = df_json.groupby(['avg_temperature@C']).size().reset_index(name='counts')

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=counts['avg_temperature@C'],
                             y=counts['counts'],
                             mode='lines',
                             visible=True,
                             line=dict(width=0.5, color='rgb(108, 33, 103)'),
                             name='Total activity'))
    fig.add_trace(go.Scatter(x=cycling['avg_temperature@C'],
                             y=cycling['counts'],
                             mode='lines+markers',
                             fill='tozeroy',
                             visible=False,
                             line=dict(width=0.5, color='rgb(234, 169, 189)'),
                             name='Cycling'))
    fig.add_trace(go.Scatter(x=running['avg_temperature@C'],
                             y=running['counts'],
                             mode='lines+markers',
                             fill='tozeroy',
                             visible=False,
                             line=dict(width=0.5, color='rgb(221, 136, 172)'),

                             name='Running'))
    fig.add_trace(go.Scatter(x=walking['avg_temperature@C'],
                             y=walking['counts'],
                             mode='lines+markers',
                             fill='tozeroy',
                             visible=False,
                             line=dict(width=0.5, color='rgb(202, 105, 157)'),
                             name='Walking'))
    fig.add_trace(go.Scatter(x=hiking['avg_temperature@C'],
                             y=hiking['counts'],
                             mode='lines+markers',
                             fill='tozeroy',
                             visible=False,
                             line=dict(width=0.5, color='rgb(145, 53, 125)'),
                             name='Hiking'))

    fig.update_layout(updatemenus=list([
            dict(
                buttons=list([
                    dict(
                        args=[{'visible': [True, False, False, False, False]}],
                        label='Total activity',
                        method='update',
                    ),
                    dict(
                        args=[{'visible': [True, True, False, False, False]}],
                        label='Cycling',
                        method='update',
                    ),
                    dict(
                        args=[{'visible': [True, False, True, False, False]}],
                        label='Running',
                        method='update',
                    ),
                    dict(
                        args=[{'visible': [True, False, False, True, False]}],
                        label='Walking',
                        method='update',
                    ),
                    dict(
                        args=[{'visible': [True, False, False, False, True]}],
                        label='Hiking',
                        method='update',
                    ),
                    dict(
                        args=[{'visible': [True, True, True, True, True]}],
                        label='All',
                        method='update',
                    )
                ]),
                direction='left',
                pad={'t':10},
                showactive=True,
                type='buttons',
                x=0,
                xanchor='left',
                y=1.1,
                yanchor='middle'
            )
    ]))

    fig.update_layout(
        title='The amount of activity depending on temperature',
        xaxis=dict(title='Temperature °C'),
        yaxis=dict(title='Quantity of activity')
    )
    return fig


## WYKRES 4
## Wzór Karnovena
def plot_intensity_by_temperature(df_json):
    age_mean = (35 + 36 + 37 + 38 + 39 + 40)/6
    HR_max = 210 - 0.5*(age_mean) - 0.222*75 + 4
    HR_min = 50

    intensity = df_json.groupby(['sport', 'avg_temperature@C'])['avg_heart_rate@bpm'].agg(
        lambda x: (((x - HR_min) / (HR_max - HR_min))*100).mean().round()
        ).reset_index(name='intensity')

    cycling = intensity[intensity['sport']=='cycling']
    running = intensity[intensity['sport']=='running']
    walking = intensity[intensity['sport']=='walking']
    hiking = intensity[intensity['sport']=='hiking']


    fig = go.Figure()

    fig.add_trace(go.Scatter(x=cycling['avg_temperature@C'],
                             y=cycling['intensity'],
                             mode='lines+markers',
                             visible=True,
                             line=dict(width=0.5, color='rgb(234, 169, 189)'),
                             name='Cycling'))
    fig.add_trace(go.Scatter(x=running['avg_temperature@C'],
                             y=running['intensity'],
                             mode='lines+markers',
                             visible=False,
                             line=dict(width=0.5, color='rgb(221, 136, 172)'),

                             name='Running'))
    fig.add_trace(go.Scatter(x=walking['avg_temperature@C'],
                             y=walking['intensity'],
                             mode='lines+markers',
                             visible=False,
                             line=dict(width=0.5, color='rgb(202, 105, 157)'),
                             name='Walking'))
    fig.add_trace(go.Scatter(x=hiking['avg_temperature@C'],
                             y=hiking['intensity'],
                             mode='lines+markers',
                             visible=False,
                             line=dict(width=0.5, color='rgb(145, 53, 125)'),
                             name='Hiking'))

    fig.update_layout(yaxis_range=[0,100])

    fig.update_layout(updatemenus=list([
            dict(
                buttons=list([
                    dict(
                        args=[{'visible': [True, False, False, False]}],
                        label='Cycling',
                        method='update',
                    ),
                    dict(
                        args=[{'visible': [False, True, False, False]}],
                        label='Running',
                        method='update',
                    ),
                    dict(
                        args=[{'visible': [False, False, True, False]}],
                        label='Walking',
                        method='update',
                    ),
                    dict(
                        args=[{'visible': [False, False, False, True]}],
                        label='Hiking',
                        method='update',
                    ),
                    dict(
                        args=[{'visible': [True, True, True, True]}],
                        label='All',
                        method='update',
                    ),
                ]),
                direction='left',
                pad={'t':10},
                showactive=True,
                type='buttons',
                x=0,
                xanchor='left',
                y=1.1,
                yanchor='middle'
            )
    ]))

    fig.update_layout(
        title='Intensity depending on temperature',
        xaxis=dict(title='Temperature °C'),
        yaxis=dict(title='Intensity %')
    )
    return fig
