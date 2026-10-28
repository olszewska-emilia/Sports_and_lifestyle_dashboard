"""Streamlit entry point. Run with: python -m streamlit run app.py."""
import json
import time
import streamlit as st
import plotly.express as px
from streamlit_lottie import st_lottie
from streamlit_option_menu import option_menu
from training_insights.config import JSON_DATA_DIR as filename_json, CSV_DATA_DIR, MAPBOX_TOKEN as map_token, TEA_ANIMATION_PATH
from training_insights.data import load_data_json
from training_insights.visualization import plotly_hex_map, plotly_points_map, plotly_scatter_map
from training_insights.recommendations.activity import ActivityRecommendationSystem
from training_insights.recommendations.weather import WeatherRecommendationSystem
from training_insights.analysis.activity import load_activity_summary, plot_activity_by_weekday, plot_activity_by_month, plot_activity_by_temperature, plot_intensity_by_temperature
from training_insights.analysis.heart_rate import load_classified_routes, plot_heart_zone_treemap
from training_insights.analysis.weather import merge_weather, plot_wind_effect

st.set_page_config(page_title="Training Insights", layout="wide")
if not any(filename_json.glob("*.json")) or not any(CSV_DATA_DIR.glob("*.csv")):
    st.title("Training Insights")
    st.info("Add your activity JSON exports to data/raw/json and route CSV exports to data/raw/csv. See README.md for configuration and data requirements.")
    st.stop()
if not map_token:
    st.info("Maps use OpenStreetMap tiles. Set MAPBOX_TOKEN for the original Mapbox styling.")

classified_df = st.cache_data(load_classified_routes)()
activity_summary = st.cache_data(load_activity_summary)()

df = load_data_json(filename_json)
df['centroid_lat'] = df.apply(lambda row: (row['nec_lat@deg'] + row['swc_lat@deg']) / 2, axis=1)
df['centroid_lon'] = df.apply(lambda row: (row['nec_long@deg'] + row['swc_long@deg']) / 2, axis=1)
@st.cache_data
def start_hex_map():
    hex_start = plotly_hex_map(df,
            lat="start_position_lat@deg",
            long="start_position_long@deg",
            map_token = map_token)
    st.plotly_chart(hex_start)

#hex_swc = plotly_hex_map(df,
  #      lat="swc_lat@deg",
  #      long="swc_long@deg",
  #      map_token = map_token)

#hex_nec = plotly_hex_map(df,
#        lat="nec_lat@deg",
 #       long="nec_long@deg",
 #       map_token = map_token)
@st.cache_data
def hex_centroid_map():
    hex_visualisation = plotly_hex_map(df,
            lat="centroid_lat",
            long="centroid_lon",
            map_token = map_token)
    st.plotly_chart(hex_visualisation)
def scatter_hex():
    scatter = plotly_scatter_map(df,
            map_token = map_token,
            lat="centroid_lat",
            lon="centroid_lon",
            color="enhanced_max_speed@km/h",
            size="total_distance@km")
    st.plotly_chart(scatter)

st.title('Training Insights')
st.sidebar.title("Brew your tea")
with st.sidebar:
    selected = option_menu(
        menu_title="Navigation bar",
        options=["Overview", "Data Visualisation", "Nobody Expects The Spanish Inquisition", "Plotly Map Visualisation", "Recommendation System"]
    )

intense_mapping = {
    "very low":0, "low":1, "medium":3, "high":4, "very high":5
}

recommendation_system = ActivityRecommendationSystem()
recommendation_system.data_preprocessing()

@st.cache_data
def get_recc(user):
    return recommendation_system.recommend_routes(user)

recommendation_system_weather = WeatherRecommendationSystem()
recommendation_system_weather.data_preprocessing()

@st.cache_data
def get_recc_weather(user):
    return recommendation_system_weather.recommend_routes(user)

@st.cache_data
def get_route(user, i):
    """

    :param user: data from user, by default zeros
    :param i: index of the reccomendation to be returned
    :return: reccomendation route
    """
    recc = recommendation_system.recommend_routes(user)
    recc = recc.iloc[i]
    mask = (
        classified_df["timestamp"] >= recc["start_time"]
    ) & (
        classified_df["timestamp"] <= recc["end_time"]
    )

    recommendation_routes = classified_df[mask]
    return(recommendation_routes)

@st.cache_data
def get_route_weather(user, i):
    """

    :param user: data from user, by default zeros
    :param i: index of the reccomendation to be returned
    :return: reccomendation route
    """
    recc = recommendation_system_weather.recommend_routes(user)
    recc = recc.iloc[i]
    mask = (
        classified_df["timestamp"] >= recc["start_time"]
    ) & (
        classified_df["timestamp"] <= recc["end_time"]
    )

    recommendation_routes = classified_df[mask]
    return(recommendation_routes)

def load(message):
    """

    :param message: message to be displayed after loading
    :return: animation from https://app.lottiefiles.com/share/57d1ff68-8c95-4cf2-a91f-777149b75125
    """
    with TEA_ANIMATION_PATH.open(encoding="utf-8") as f:
        lottie_tea = json.load(f)
    placeholder = st.empty()

    with st.spinner("your tea is brewing..."):
        with placeholder.container():
            left, center, right = st.columns([1, 2, 1])
            with center:
                st_lottie(lottie_tea, height=400, width=400)
        time.sleep(7)

    placeholder.empty()
    st.success(message)

if selected == "Overview":
    st.subheader("Project Overview")
    load("your black tea is ready!")
    st.write("authors: Aleksandra Mulewicz, Emilia Olszewska, Nina Onyszczuk")
    st.subheader("our project involves:")
    st.markdown("""
    * data visualisation in plotly (page: Data Visualisation)
    * fun facts about the datataset (page: Nobody Expects The Spanish Inquisition)
    * routes visualised and analysed with plotly (page: Plotly Map Visualisation)
    * route reccomendation system (page: Reccomendation System)
    """)

    st.subheader("technology used:")
    st.markdown("""
        * python
        * plotly, pyplot, mapbox
        * streamlit
        * openmeteo_requests
        """)

    st.subheader("data filtering methods:")
    st.markdown("""
            * timezone modification
            * outlier indentification (IQR)
            * empty columns
            * merging with weather data
            """)

    st.subheader("physical activity preferences:")
    st.markdown("""
                * preferred activity type -> running and cycling
                * high intensivity
                * preferred temperature -> 20-25*C
                * the raise in the temperature causes intensivity to lower
                """)

elif selected == "Data Visualisation":
    st.subheader("Data Visualisation")
    load("your chai tea is ready!")

    st.plotly_chart(plot_activity_by_weekday(activity_summary))
    st.plotly_chart(plot_activity_by_month(activity_summary))
    st.plotly_chart(plot_activity_by_temperature(activity_summary))
    st.plotly_chart(plot_intensity_by_temperature(activity_summary))
    st.plotly_chart(plot_heart_zone_treemap(classified_df))

elif selected == "Nobody Expects The Spanish Inquisition":
    st.subheader("Fun Facts about the Dataset")
    load("your coffee is ready!")

    idx_bieg = (df["total_distance@km"] > 10) & (df["sport"] == "running")
    idx_rower = (df["total_distance@km"] > 40) & (df["sport"] == "cycling")

    df_running = df.loc[idx_bieg]
    df_cycling = df.loc[idx_rower]

    idx_max_bieg = df_running["avg_speed@km/h"].idxmax()
    idx_max_rower = df_cycling["avg_speed@km/h"].idxmax()

    new_df_max = df.loc[[idx_max_bieg, idx_max_rower]].copy()
    new_df_max["text_frequency"] = new_df_max["total_timer_time@s"] / 9


    fig = px.bar(
        new_df_max,
        x="sport",
        y="text_frequency",
        color_discrete_sequence=["deeppink"],
        labels={
            "sport": "Rodzaj aktywności",
            "text_frequency": "Możliwa ilość wypowiedzenia cytatu"
        },
        title="Ile razy można wypowiedzieć cytat podczas treningu\nz najwyższą prędkością średnią"
    )
    st.plotly_chart(fig, use_container_width=True)
    st.write("cytat -> NOBODY EXPECTS THE SPANISH INQUISITION (with sound effects)")
    kalorie_suma_na_sport = (
        df
        .groupby("sport")["total_calories@kcal"]
        .sum()
        .sort_values()
        .reset_index(name="count")
    )

    kalorie_suma_na_sport["energia"] = kalorie_suma_na_sport["count"] * 4180

    kalorie_suma_na_sport.loc[len(kalorie_suma_na_sport)] = [
        "all",
        kalorie_suma_na_sport["count"].sum(),
        kalorie_suma_na_sport["energia"].sum()
    ]

    cieplo_wlasciwe_wody = 4200  # J/(kg·°C)
    temperatura_poczatkowa = 15
    temperatura_koncowa = 100
    delta_T = temperatura_koncowa - temperatura_poczatkowa

    kalorie_suma_na_sport["ilosc litrow wody"] = round(
        kalorie_suma_na_sport["energia"] / (cieplo_wlasciwe_wody * delta_T)
    )

    st.subheader("zestawienie energii i odpowiadajacej jej ilosci zagotowanej wody")
    st.dataframe(kalorie_suma_na_sport)

    fig = px.bar(
        kalorie_suma_na_sport,
        x="sport",
        y="ilosc litrow wody",
        color_discrete_sequence=["pink"],
        labels={
            "sport": "rodzaj aktywności",
            "ilosc litrow wody": "ilość litrow wody"
        },
        title="ile litrow wody mozna zagotowac do 100°C\nprzez energie wytworzona podczas aktywnosci"
    )

    st.plotly_chart(fig, use_container_width=True)

    litry = kalorie_suma_na_sport.loc[kalorie_suma_na_sport["sport"] == "all", "ilosc litrow wody"].values[0]
    palety = litry / (1.5 * 6 * 7)  # zakładamy 6 butelek po 1.5 l, 7 warstw
    st.markdown(f" *To odpowiada okolo `{palety:.1f}` paletom wody mineralnej (1.5 l x 6 szt. x 7 warstw).*")

    st.plotly_chart(plot_wind_effect(merge_weather(df)), use_container_width=True)
    st.write("najczęstrzy punkt startowy")
    st.plotly_chart(plotly_points_map([-37.821], [144.9425], map_token, label=""), use_container_width=True)

elif selected == "Plotly Map Visualisation":
    st.subheader("Map Visualisation")
    load("your earl grey is ready!")
    if st.button("click me for starting positions hex map"):
        start_hex_map()
    else:
        st.info('Starting positions visualised on the hex map...')

    if st.button('click me for centroid hex map'):
        st.write("Hex map visualising the centroid position of every training (nec + swc/2)")
        hex_centroid_map()

    else:
        st.info('position hex map...')

    if st.button('click me for scatter'):
        st.write("scatter map of the positions")
        scatter_hex()
    else:
        st.info('position scatter map...')


elif selected == "Recommendation System":
    st.subheader("Route Recommendation System")
    st.write("Choose your parameters: ")
    sub_page = st.radio("Recommendation type", ["classic", "weather"])
    if sub_page == "classic":
        load("your reccomended tea is ready!")
        option = st.radio("Choose an intensivity of your training", ["very low", "low", "medium", "high", "very high"])
        zone = intense_mapping[option]
        distance = st.slider("Set your preferred distance in km", 0.0, 42.0, step=0.5)
        duration = st.slider("Set your preferred time in min", 0.0, 210.0, step=0.5)
        duration = duration * 60
        calories = st.slider("Set your preferred calories", 0.0, 2300.0, step=0.5)
        if calories == zone == distance == duration == calories == 0:
            st.write("just stay at home...")
        else:
            user = {
                'total_distance@km': distance,
                'total_elapsed_time@s': duration,
                'total_calories@kcal': calories,
                'zone': zone
            }

            index = st.radio("you've got 5 reccomendations ready, which one would you like to get visualised",
                             ["1", "2", "3", "4", "5"])
            index = int(index) - 1
            recomendation_routes = get_route(user, index)

            route = plotly_scatter_map(recomendation_routes,
                                       map_token=map_token,
                                       lat="position_lat@deg",
                                       lon="position_long@deg",
                                       color="zone",
                                       size="distance@km")

            if st.button('click me for routes'):
                st.subheader("scatter map of the positions")
                st.write(f"the heart zones at each step of the training are illustrated by the colors")
                st.plotly_chart(route)
                # recc = get_recc(user)
                # st.write(f"the distance for this route is: {recc['total_distance@km']}")
                # st.write(f"the total time for this route is: {recc['total_elapsed_time@s']}")
                # st.write(f"the number of calories burned for this route is: {recc['total_calories@kcal']}")

            else:
                st.info('position scatter map...')

    elif sub_page == "weather":
        load("your reccomended tea is ready!")
        rainfall = st.slider("Choose an intensivity of rain", 0.0, 5.0, step=0.5)
        cloudcover = st.slider("Choose how cloudy it is: ", 0.0, 100.0, step=0.5)
        distance = st.slider("Set your preferred distance in km", 0.0, 42.0, step=0.5)
        windspeed = st.slider("Choose the wind speed", 0.0, 38.0, step=0.5)
        temperature = st.slider("What is the temperature", 5.0, 31.0, step=0.5)
        user = {
                'rain': rainfall,
                'cloud_cover': cloudcover,
                'total_distance@km': distance,
                'temperature_2m': temperature,
                'wind_speed_10m': windspeed
            }

        index = st.radio("you've got 5 reccomendations ready, which one would you like to get visualised",
                             ["1", "2", "3", "4", "5"])
        index = int(index) - 1
        recomendation_routes = get_route_weather(user, index)

        route = plotly_scatter_map(recomendation_routes,
                                       map_token=map_token,
                                       lat="position_lat@deg",
                                       lon="position_long@deg",
                                       color='heart_rate@bpm',
                                       size="distance@km",
                                       palette="Magenta")

        if st.button('click me for routes'):
                st.subheader("scatter map of the positions")
                st.write(f"the heart rate at each step of the training is illustrated by the colors")
                st.plotly_chart(route)
                # recc = get_recc(user)
                # st.write(f"the distance for this route is: {recc['total_distance@km']}")
                # st.write(f"the total time for this route is: {recc['total_elapsed_time@s']}")
                # st.write(f"the number of calories burned for this route is: {recc['total_calories@kcal']}")

        else:
                st.info('position scatter map...')
