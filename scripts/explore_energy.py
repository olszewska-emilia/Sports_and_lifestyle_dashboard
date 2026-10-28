from training_insights.config import JSON_DATA_DIR as filename_json, CSV_DATA_DIR as filename_csv, MAPBOX_TOKEN as map_token
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from training_insights.analysis.weather import merge_weather
from training_insights.weather import load_weather_data

hourly_dataframe = load_weather_data()
from training_insights.data import load_data_json
import plotly.graph_objects as go
# %%
df_emilka = load_data_json(filename_json)
df_merged = merge_weather(df_emilka)
# %%
#print(df_emilka.columns)
#print(df_emilka[["total_calories@kcal",'sport']])
kalorie_suma_na_sport = (df_emilka.groupby("sport")["total_calories@kcal"].sum().sort_values().reset_index(name="count"))
kalorie_suma_na_sport["energia"] = kalorie_suma_na_sport["count"] * 4180
kalorie_suma_na_sport.loc[len(kalorie_suma_na_sport)] = ["all",kalorie_suma_na_sport["count"].sum(),kalorie_suma_na_sport["energia"].sum()]
# plt.bar(kalorie_suma_na_sport["sport"], kalorie_suma_na_sport["count"],color="pink")
# plt.xlabel("rodzaj aktywnosci", fontsize=10)
# plt.ylabel("wyprodukowana energia", fontsize=10)
# plt.show()
cieplo_wlasciwe_wody = 4200
temperatura_poczatkowa = 15
temperatura_koncowa = 100
kalorie_suma_na_sport["ilosc litrow wody"] = round(kalorie_suma_na_sport["energia"]/(cieplo_wlasciwe_wody*(temperatura_koncowa-temperatura_poczatkowa)))
print(kalorie_suma_na_sport)
#okolo 14 palet wody minerlanej 1,5 l
plt.bar(kalorie_suma_na_sport["sport"], kalorie_suma_na_sport["ilosc litrow wody"],color="pink")
plt.xlabel("rodzaj aktywnosci", fontsize=10)
plt.ylabel("ilosc litrow wody", fontsize=10)
plt.title("Ile litrów wody można zagotować do temperatury 100 stopni Celciusa \nprzez wytworzoną energie podczas aktywności")
plt.show()

# %%
print(hourly_dataframe.head())
print(hourly_dataframe.columns)
print(df_merged.columns)
print(df_merged.sort_values("timestamp").head())
df_weather = hourly_dataframe
df_emilka['timestamp'] = pd.to_datetime(df_emilka['timestamp'])
df_weather['date'] = pd.to_datetime(df_weather['date'])
df_emilka['timestamp_rounded'] = df_emilka['timestamp'].dt.floor('h')
df_merged_2 = pd.merge(
    df_weather,
    df_emilka,
    right_on='timestamp_rounded',
    left_on='date',
    how="outer"
)
df_merged_2 = df_merged_2.drop(columns=['date'])
df_merged_2 = df_merged_2[['timestamp', 'start_time', 'start_position_lat@deg',
       'start_position_long@deg', 'total_elapsed_time@s', 'total_timer_time@s',
       'total_distance@km', 'total_strides@strides', 'nec_lat@deg',
       'nec_long@deg', 'swc_lat@deg', 'swc_long@deg',
       'enhanced_avg_speed@km/h', 'enhanced_max_speed@km/h', 'message_index',
       'total_calories@kcal', 'avg_speed@km/h', 'max_speed@km/h',
       'total_ascent@m', 'total_descent@m', 'first_lap_index', 'num_laps',
       'avg_vertical_oscillation@mm', 'avg_stance_time_percent@percent',
       'avg_stance_time@ms', 'avg_vertical_ratio@percent',
       'avg_stance_time_balance@percent', 'avg_step_length@mm', 'event',
       'event_type', 'sport', 'sub_sport', 'avg_heart_rate@bpm',
       'max_heart_rate@bpm', 'avg_running_cadence@strides/min',
       'max_running_cadence@strides/min', 'total_training_effect', 'trigger',
       'avg_temperature@C', 'max_temperature@C', 'avg_fractional_cadence@rpm',
       'max_fractional_cadence@rpm', 'total_anaerobic_training_effect',
       'total_strokes@strokes', 'avg_cadence@rpm', 'max_cadence@rpm',
       'total_fractional_ascent@m', 'total_fractional_descent@m',
       'total_cycles@cycles', 'timestamp_rounded', 'temperature_2m',
       'relative_humidity_2m', 'rain', 'snowfall', 'wind_speed_10m',
       'wind_direction_10m', 'cloud_cover', 'cloud_cover_low',
       'cloud_cover_mid', 'cloud_cover_high', 'surface_pressure',
       'pressure_msl', 'apparent_temperature']]
dni_bez_aktywnosci = (df_merged_2[df_merged_2['sport'].isna()])
 # %%
 # dni bez aktywnosci
dni_bez_aktywnosci['rain_flag'] = dni_bez_aktywnosci['rain'] > 0

grouped = dni_bez_aktywnosci.groupby('rain_flag')['total_distance@km'].mean().reset_index()

df = dni_bez_aktywnosci.copy()

df['high_pressure_flag'] = df['pressure_msl'] > 1015
df['cloudy_flag'] = df['cloud_cover'] > 70
df['wind_flag'] = df['wind_speed_10m'] > 20
df['snow_flag'] = df['snowfall'] > 0
df['humidity_flag'] = df['relative_humidity_2m'] > 80

# %%
#zmiana_wartosci = np.where(df_merged["rain"]>0.0,1,0)
fig, ax = plt.subplots(figsize=(10, 6))
sc = ax.scatter(
    df_merged['temperature_2m'],
    df_merged['relative_humidity_2m'],
    c=df_merged['avg_speed@km/h'],
    cmap='coolwarm',
    s=100,
    edgecolors='k'
)
plt.xlabel('Temperatura [°C]')
plt.ylabel('Wilgotność [%]')
plt.title('Wpływ pogody na wydajność treningu')
cbar = plt.colorbar(sc)
cbar.set_label('Średnia prędkość [km/h]')
plt.grid(True)
plt.tight_layout()
plt.show()

# %%
print(df_emilka[['event',
       'event_type', 'sport', 'sub_sport']])
print(np.unique(df_emilka[['event_type']]))
ramka_nowa = df_emilka[['total_elapsed_time@s', 'total_timer_time@s',
       'total_distance@km','enhanced_avg_speed@km/h', 'enhanced_max_speed@km/h']]
df_emilka['difference_in_time'] = df_emilka['total_elapsed_time@s'] - df_emilka['total_timer_time@s']
df_time = df_emilka.groupby('sport')['total_timer_time@s'].sum().sort_values().reset_index(name='sum_time')
df_time['sum_time'] = round(df_time['sum_time']/60,2)
print(df_time)
print(4012*23)

# %%
# ile razy powie ulubiony cytat
idx_bieg = (df_emilka["total_distance@km"]>10) & (df_emilka["sport"] =="running")
idx_rower = (df_emilka["total_distance@km"]>40) & (df_emilka["sport"] =="cycling")
df_running = df_emilka.loc[idx_bieg]
df_cycling = df_emilka.loc[idx_rower]
idx_max_bieg = (df_running['avg_speed@km/h'].idxmax())
idx_max_rower = (df_cycling['avg_speed@km/h'].idxmax())
new_df_max = (df_emilka.loc[[idx_max_bieg,idx_max_rower]])
new_df_max["text_frequency"] = new_df_max["total_timer_time@s"]/9
plt.bar(new_df_max["sport"], new_df_max["text_frequency"],color="deeppink")
plt.xlabel("rodzaj aktywnosci", fontsize=10)
plt.ylabel("mozliwa ilosc wypowiedznia cytatu", fontsize=10)
plt.title("Ile razy można wypowiedzieć cytat podczas treningu\n z najmniejsza predkoscia srednia")
plt.show()

#%%
df_merged_2_treningi = df_merged_2[df_merged_2["total_distance@km"]>10]
mask_wind = df_merged_2_treningi["wind_speed_10m"] > 15
silny_wiatr = df_merged_2_treningi[mask_wind]
slaby_wiatr = df_merged_2_treningi[~mask_wind]
avg_speed_silny = silny_wiatr["avg_speed@km/h"].mean()
avg_speed_slaby = slaby_wiatr["avg_speed@km/h"].mean()
roznica = avg_speed_slaby - avg_speed_silny
print(roznica)
clean = df_merged_2_treningi[["avg_speed@km/h","wind_speed_10m"]].copy()
clean = clean.replace([np.inf, -np.inf], np.nan).dropna()
plt.figure(figsize=(8,5))
plt.scatter(silny_wiatr["avg_speed@km/h"], silny_wiatr["wind_speed_10m"],alpha=0.5,label = f"silny wiatr >15 m/s",color = "palevioletred")
plt.scatter(slaby_wiatr["avg_speed@km/h"], slaby_wiatr["wind_speed_10m"],alpha=0.5,label = f"slaby wiatr <=15 m/s",color = "lightpink")
x = clean["avg_speed@km/h"].values
y = clean["wind_speed_10m"].values
m, b = np.polyfit(x, y, 1)
x_line = np.linspace(x.min(), x.max(), 100)
y_line = m * x_line + b

plt.plot(x_line, m * x_line + b,linestyle='--', color='hotpink',label=f'Linia trendu (y={m:.3f}·x+{b:.2f})')
plt.ylabel('Prędkość wiatru (m/s)')
plt.xlabel('Średnia prędkość (km/h)')
plt.title('Wpływ wiatru na średnią prędkość')
plt.legend()
plt.grid(axis='both', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()

def wiatr():
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=silny_wiatr["avg_speed@km/h"],
        y=silny_wiatr["wind_speed_10m"],
        mode='markers',
        name='silny wiatr >15 m/s',
        marker=dict(color='mediumvioletred', opacity=0.6)
    ))

    fig.add_trace(go.Scatter(
        x=slaby_wiatr["avg_speed@km/h"],
        y=slaby_wiatr["wind_speed_10m"],
        mode='markers',
        name='słaby wiatr ≤15 m/s',
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
        yaxis_title='prędkość wiatru (m/s)',
        legend=dict(bordercolor="gray", borderwidth=0.5),
        template='simple_white'
    )
    return fig
