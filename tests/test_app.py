"""Check the public checkout's first-run experience without private data."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest


class AppTests(unittest.TestCase):
    def test_missing_data_shows_setup_instructions(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch('training_insights.config.JSON_DATA_DIR', Path(folder)), patch('training_insights.config.CSV_DATA_DIR', Path(folder)):
                app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py')).run(timeout=20)
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.title[0].value, 'Training Insights')
        self.assertIn('data/raw/json', app.info[0].value)

    def test_dashboard_pages_with_synthetic_exports(self):
        import json
        from time import sleep as real_sleep
        import pandas as pd

        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            records = []
            for index in range(24):
                start = pd.Timestamp('2020-01-01T00:00:00Z') + pd.Timedelta(days=index)
                activity = {
                    'timestamp': (start + pd.Timedelta(hours=1)).isoformat(),
                    'start_time': start.isoformat(),
                    'sport': ['running', 'cycling', 'walking'][index % 3],
                    'avg_heart_rate@bpm': 110 + index,
                    'avg_temperature@C': 10 + index,
                    'total_distance@km': 45 + index,
                    'total_elapsed_time@s': 3600 + index,
                    'total_timer_time@s': 3500 + index,
                    'total_calories@kcal': 400 + index,
                    'enhanced_max_speed@km/h': 15 + index,
                    'avg_speed@km/h': 10 + index,
                    'start_position_lat@deg': -37.8,
                    'start_position_long@deg': 144.9,
                    'nec_lat@deg': -37.7,
                    'nec_long@deg': 145.,
                    'swc_lat@deg': -37.9,
                    'swc_long@deg': 144.8,
                }
                (folder / f'{index}.json').write_text(json.dumps(activity))
                records.append({
                    'timestamp': start.isoformat(), 'position_lat@deg': -37.8,
                    'position_long@deg': 144.9, 'heart_rate@bpm': 110 + index,
                    'distance@km': 1 + index, 'speed@km/h': 10 + index,
                    'cadence@rpm': 70 + index, 'step_length@mm': 700 + index,
                })
            pd.DataFrame(records).to_csv(folder / 'routes.csv', index=False)
            from training_insights.analysis.activity import load_activity_summary
            from training_insights.data import load_data_csv, load_data_json
            from training_insights.heart_zones import HeartZoneClassifier

            routes = load_data_csv(folder)
            routes['timestamp'] = pd.to_datetime(routes['timestamp'], utc=True)
            routes['date'] = routes['timestamp'].dt.date
            routes = HeartZoneClassifier(routes).assign_zones()
            with patch('training_insights.analysis.activity.JSON_DATA_DIR', folder):
                summary = load_activity_summary()
            def synthetic_routes():
                return routes

            def synthetic_summary():
                return summary

            for page in ['Overview', 'Data Visualisation', 'Nobody Expects The Spanish Inquisition', 'Plotly Map Visualisation', 'Recommendation System']:
                with self.subTest(page=page), \
                     patch('training_insights.config.JSON_DATA_DIR', folder), \
                     patch('training_insights.config.CSV_DATA_DIR', folder), \
                     patch('training_insights.analysis.activity.load_activity_summary', new=synthetic_summary), \
                     patch('training_insights.analysis.heart_rate.load_classified_routes', new=synthetic_routes), \
                     patch('training_insights.recommendations.activity.load_data_json', side_effect=lambda _: load_data_json(folder)), \
                     patch('training_insights.recommendations.weather.load_data_json', side_effect=lambda _: load_data_json(folder)), \
                     patch('streamlit_option_menu.option_menu', return_value=page), \
                     patch('streamlit_lottie.st_lottie'), patch('time.sleep', side_effect=lambda _: real_sleep(0.001)):
                    app = AppTest.from_file(str(root / 'app.py')).run(timeout=30)
                    self.assertEqual(len(app.exception), 0, [e.message for e in app.exception])
