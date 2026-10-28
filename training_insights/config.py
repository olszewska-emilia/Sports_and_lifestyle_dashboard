"""Portable paths and environment-based configuration (no embedded credentials)."""
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def configured_path(variable, default):
    value = Path(os.environ.get(variable) or default).expanduser()
    return value if value.is_absolute() else PROJECT_ROOT / value


JSON_DATA_DIR = configured_path("PDU_JSON_DATA_DIR", "data/raw/json")
CSV_DATA_DIR = configured_path("PDU_CSV_DATA_DIR", "data/raw/csv")
WEATHER_DATA_PATH = configured_path("PDU_WEATHER_DATA_PATH", "data/weather/hourly_data.csv")
MAPBOX_TOKEN = os.environ.get("MAPBOX_TOKEN", "")
TEA_ANIMATION_PATH = PROJECT_ROOT / "assets/animations/tea.json"
