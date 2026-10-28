"""Regression tests using temporary, synthetic activity data."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

from training_insights.data import load_data_csv, load_data_json
from training_insights.heart_zones import HeartZoneClassifier
from training_insights.recommendations.activity import ActivityRecommendationSystem
from training_insights.recommendations.weather import WeatherRecommendationSystem
from training_insights.analysis.weather import merge_weather
from training_insights.weather import load_weather_data


class DataTests(unittest.TestCase):
    def test_missing_exports_have_actionable_errors(self):
        with tempfile.TemporaryDirectory() as folder:
            for loader in (load_data_json, load_data_csv):
                with self.assertRaisesRegex(FileNotFoundError, 'README'):
                    loader(folder)

    def test_json_reader_removes_empty_fields(self):
        with tempfile.TemporaryDirectory() as folder:
            Path(folder, 'activity.json').write_text(json.dumps({
                'sport': 'running', 'empty': None, 'empty_list': [None, None]
            }))
            frame = load_data_json(folder)
            self.assertEqual(list(frame.columns), ['sport'])
            self.assertEqual(frame.iloc[0]['sport'], 'running')

    def test_csv_reader_combines_exports(self):
        with tempfile.TemporaryDirectory() as folder:
            for index in range(2):
                Path(folder, f'{index}.csv').write_text(f'distance@km,empty\n{index},\n')
            frame = load_data_csv(folder)
            self.assertEqual(frame['distance@km'].tolist(), [0, 1])
            self.assertNotIn('empty', frame.columns)

    def test_weather_snapshot_is_utc_without_export_index(self):
        weather = load_weather_data()
        self.assertFalse(weather.empty)
        self.assertEqual(str(weather['date'].dt.tz), 'UTC')
        self.assertFalse(any(c.startswith('Unnamed:') for c in weather))

    def test_weather_matches_equivalent_timezone_offsets(self):
        weather = pd.DataFrame({'date': pd.to_datetime(['2020-01-01T00:00:00Z']), 'rain': [1.5]})
        activities = pd.DataFrame({'timestamp': ['2020-01-01T11:30:00+11:00']})
        with patch('training_insights.analysis.weather.load_weather_data', return_value=weather):
            result = merge_weather(activities)
        self.assertEqual(result.iloc[0]['rain'], 1.5)
        self.assertNotIn('timestamp_rounded', activities)


class RecommendationTests(unittest.TestCase):
    def test_ranking_preserves_labels_after_missing_rows_are_removed(self):
        for cls in (ActivityRecommendationSystem, WeatherRecommendationSystem):
            engine = cls.__new__(cls)
            engine.features = ['distance', 'duration', 'calories']
            engine.df = pd.DataFrame({
                'distance': [1., np.nan, 3., 4.],
                'duration': [40., 30., 20., 10.],
                'calories': [10., 20., 40., 30.],
            }, index=[10, 20, 30, 40])
            result = engine.recommend_routes({'distance': 4., 'duration': 10., 'calories': 30.})
            self.assertEqual(result.index[0], 40)
            self.assertNotIn(20, result.index)
            self.assertEqual(len(result), 3)

    def test_constant_feature_does_not_create_nan_scores(self):
        engine = ActivityRecommendationSystem.__new__(ActivityRecommendationSystem)
        engine.features = ['distance', 'duration', 'zone']
        engine.df = pd.DataFrame({'distance': [1., 2., 3.], 'duration': [30., 20., 10.], 'zone': [3., 3., 3.]})
        result = engine.recommend_routes({'distance': 3., 'duration': 10., 'zone': 3.})
        self.assertEqual(result.index[0], 2)
        self.assertTrue(np.isfinite(engine.x_scaled.to_numpy()).all())

    def test_heart_zones_filter_outliers(self):
        frame = pd.DataFrame({'heart_rate@bpm': [100.] * 20 + [1000.]})
        classified = HeartZoneClassifier(frame).assign_zones()
        self.assertEqual(len(classified), 20)
        self.assertEqual(classified['zone'].unique().tolist(), [5])
        self.assertNotIn('zone', frame)


if __name__ == '__main__':
    unittest.main()
