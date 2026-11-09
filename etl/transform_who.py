"""Normalize WHO xMart CSV rows to the shared observation columns."""

from pathlib import Path

import pandas as pd
import pycountry

from app.models import Sex

_NORMALIZED_COLUMNS = ["country_iso3", "indicator_code", "year", "sex", "value"]
_REQUIRED_COLUMNS = (
    "IND_CODE",
    "DIM_TIME",
    "DIM_GEO_CODE_M49",
    "DIM_GEO_CODE_TYPE",
    "DIM_SEX",
    "DIM_AGE",
    "RATE_PER_100000_N",
)

# xMart sex labels → GHO-style codes that clean_observations already maps.
_SEX_MAP = {
    "TOTAL": f"SEX_{Sex.BOTH.value}",
    "MALE": f"SEX_{Sex.MALE.value}",
    "FEMALE": f"SEX_{Sex.FEMALE.value}",
}


def _m49_to_iso3(m49: object) -> str | None:
    if m49 is None or (isinstance(m49, float) and pd.isna(m49)):
        return None
    try:
        numeric = str(int(m49)).zfill(3)
    except (TypeError, ValueError):
        return None
    country = pycountry.countries.get(numeric=numeric)
    return country.alpha_3 if country is not None else None


def transform_who_frame(raw: pd.DataFrame, code: str) -> pd.DataFrame:
    if raw.empty:
        return pd.DataFrame(columns=_NORMALIZED_COLUMNS)

    missing = [col for col in _REQUIRED_COLUMNS if col not in raw.columns]
    if missing:
        raise ValueError(f"WHO xMart {code}: missing columns {missing}")

    frame = raw.copy()
    frame = frame[frame["DIM_GEO_CODE_TYPE"].astype("string") == "COUNTRY"]
    frame = frame[frame["DIM_AGE"].astype("string") == "TOTAL"]
    frame = frame[frame["IND_CODE"].astype("string") == code]

    return pd.DataFrame(
        {
            "country_iso3": frame["DIM_GEO_CODE_M49"].map(_m49_to_iso3),
            "indicator_code": code,
            "year": frame["DIM_TIME"],
            "sex": frame["DIM_SEX"].astype("string").str.upper().map(_SEX_MAP),
            "value": frame["RATE_PER_100000_N"],
        }
    )


def transform_who_file(path: Path, code: str) -> pd.DataFrame:
    raw = pd.read_csv(path)
    return transform_who_frame(raw, code)
