"""Read the bundled weather snapshot without making network requests."""
import pandas as pd
from training_insights.config import WEATHER_DATA_PATH


def load_weather_data(path=WEATHER_DATA_PATH):
    """Load hourly weather and normalize timestamps to UTC."""
    data = pd.read_csv(path)
    data["date"] = pd.to_datetime(data["date"], utc=True)
    return data.loc[:, ~data.columns.str.startswith("Unnamed:")]
