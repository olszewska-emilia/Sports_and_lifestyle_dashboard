"""Readers for locally supplied training exports."""
from pathlib import Path
import json
import pandas as pd

def load_data_json(filename):
    """
    :param filename: ".../pdu-2025L-dane-json/", extracted
    :return: DataFrame without empty columns

    """
    filepath = Path(filename)
    files = sorted(filepath.glob("*.json"))
    if not files:
        raise FileNotFoundError(f"No activity JSON files found in {filepath}. See README.md for data setup.")
    data = []
    for file in files:
        with file.open(encoding="utf-8") as handle:
            data.append(json.load(handle))
    df = pd.DataFrame.from_records(data)
    df = df.dropna(axis=1, how='all')
    df = df[[col for col in df.columns if not all(isinstance(x, list) and all(v is None for v in x) for x in df[col])]]
    return df

def load_data_csv(filename):
    """
    :param filename: ".../pdu-2025L-dane-csv/", extracted
    :return: DataFrame without empty columns

    """
    filepath = Path(filename)
    files = sorted(filepath.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No route CSV files found in {filepath}. See README.md for data setup.")
    data = [pd.read_csv(file) for file in files]
    data = pd.concat(data)
    df = pd.DataFrame(data)
    df = df.dropna(axis=1, how='all')
    return df
