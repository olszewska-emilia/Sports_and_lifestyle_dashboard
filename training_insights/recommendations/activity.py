from training_insights.config import JSON_DATA_DIR
#IMPORTS
from training_insights.data import load_data_json
from training_insights.heart_zones import HeartZoneClassifier
from training_insights.weather import load_weather_data

import numpy as np
import pandas as pd
class ActivityRecommendationSystem:
    def __init__(self, data_dir=JSON_DATA_DIR):
        self.df = load_data_json(data_dir)
        self.df["start_time"] = pd.to_datetime(self.df["start_time"], utc=True)
        self.df["end_time"] = pd.to_datetime(self.df["start_time"], utc=True) + pd.to_timedelta(self.df["total_elapsed_time@s"], unit='s')
        self.features = [
            'total_distance@km',
            'total_elapsed_time@s',
            'total_calories@kcal',
            'zone'
        ]
        self.x_scaled = None
        self.query_vector = None
        self.recommended_routes = None

    def data_preprocessing(self):
        hourly_dataframe = load_weather_data()
        df_running = self.df[self.df["sport"] == "running"]
        threshold = 0.7
        df_running_cleaned = df_running.loc[:, df_running.isna().mean() < threshold].copy()

        df_running_cleaned.rename(columns={"avg_heart_rate@bpm": 'heart_rate@bpm'}, inplace=True)
        classifier = HeartZoneClassifier(df_running_cleaned)
        filtered_df = classifier.filter_outliers()
        classified_df = classifier.assign_zones()

        classified_df['timestamp'] = pd.to_datetime(classified_df['timestamp'], utc=True)

        hourly_dataframe['date'] = pd.to_datetime(hourly_dataframe['date'])
        classified_df['timestamp_rounded'] = classified_df['timestamp'].dt.floor('h')
        df_merged = pd.merge(
            classified_df,
            hourly_dataframe,
            left_on='timestamp_rounded',
            right_on='date',
            how='left'
        )

        df_merged = df_merged.drop(columns=['date'])
        df_merged['rain_flag'] = df_merged['rain'] > 0
        self.df = df_merged

    def recommend_routes(self, user_query):
        x = self.df[self.features].dropna()
        self.x_scaled = ( x - x.mean(axis=0) ) / x.std(axis=0).replace(0, 1)

        query_df = pd.DataFrame([user_query])
        self.query_vector = query_df.iloc[0]
        self.query_vector = (self.query_vector - x.mean(axis=0)) / x.std(axis=0).replace(0, 1) #standarization

        correlations = self.x_scaled.apply(lambda row: self.pearson(row), axis=1)
        self.recommended_routes = self.df.loc[correlations.sort_values(ascending=False).head(5).index]
        return  self.recommended_routes

    def cosine_similarity(self):
        dot_product = self.x_scaled @ self.query_vector
        query_norm = np.sqrt((self.query_vector ** 2).sum())
        row_norms = np.sqrt((self.x_scaled ** 2).sum(axis=1))
        similarities = dot_product / (row_norms * query_norm) #didn't work very well
        return similarities

    def pearson(self, x):
        x_mean = np.mean(x)
        y_mean = np.mean(self.query_vector)

        numerator = np.sum((x - x_mean) * (self.query_vector - y_mean))
        denominator = np.sqrt(np.sum((x - x_mean) ** 2)) * np.sqrt(np.sum((self.query_vector - y_mean) ** 2))

        if denominator == 0:
            return 0  # lub np.nan
        return numerator / denominator
