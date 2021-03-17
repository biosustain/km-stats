"""Provides a function prepare_data."""

import os
import numpy as np
import pandas as pd

from .util import make_columns_lower_case

RENAMING_DICT = {"Class": "ec4", "Km value": "km"}
COLS_THAT_MUST_BE_NON_NULL = [
    "class",
    "ec4",
    "km",
    "superkingdom",
    "family",
    "genus",
    "species",
]
T_REGEX = r"(\d+) ?°[Cc]"  # extract temperature from comment

# Where to find raw data and where to save prepared data: probably don't edit!
HERE = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_DIR = os.path.join(HERE, "..", "data", "raw")
PREPARED_DATA_DIR = os.path.join(HERE, "..", "data", "prepared")

# Filenames of the input and output: edit these unless they are already what
# you want
RAW_DATA_CSV = os.path.join(RAW_DATA_DIR, "new_taxa.csv")
PREPARED_DATA_CSV = os.path.join(RAW_DATA_DIR, "data_prepared.csv")


def prepare_data(raw_data: pd.DataFrame) -> pd.DataFrame:
    """Takes in raw data, returns prepared data.

    :param raw_data: pd.DataFrame of raw data
    ::
    """
    out = (
        raw_data.copy()
        .rename(columns=RENAMING_DICT)
        .pipe(make_columns_lower_case)
        .dropna(subset=COLS_THAT_MUST_BE_NON_NULL)
        .drop_duplicates()
        .reset_index(drop=True)
    )
    out["dummy_col"] = 1
    out["temperature"] = out["comments"].str.extract(T_REGEX)[0].astype(float)
    out["temperature_m25"] = out["temperature"] - 25.01
    out["ec3"] = [".".join(ecs.split(".")[:3]) for ecs in out["ec4"]]
    out["ec2"] = [".".join(ecs.split(".")[:2]) for ecs in out["ec4"]]
    out["log_km"] = np.log(out["km"])
    out = out.dropna(subset=["temperature"]).reset_index(drop=True)
    return out
