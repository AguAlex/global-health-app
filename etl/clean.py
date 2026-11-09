import logging
from typing import NamedTuple

import numpy as np
import pandas as pd

from app.models import Sex

logger = logging.getLogger(__name__)

_OUTPUT_COLUMNS = [
    "country_iso3",
    "indicator_code",
    "year",
    "sex",
    "value",
    "is_outlier",
]
_KEY_COLUMNS = ["country_iso3", "indicator_code", "year", "sex"]

# WHO xMart is mapped to "SEX_BTSX" etc.; derived from the model so the two cannot drift.
_SEX_MAP = {f"SEX_{sex.value}": sex.value for sex in Sex}
_VALID_SEX = {sex.value for sex in Sex}


class _Bounds(NamedTuple):
    """Plausible value range; ``high`` is inclusive, ``low`` if ``low_inclusive``."""

    low: float
    high: float
    low_inclusive: bool = True


# Bounds adapted to this project's Lab 1 indicators (+ OWID life expectancy).
_INDICATOR_BOUNDS = {
    "SDGSUICIDE": _Bounds(0, 150),
    "SL.UEM.TOTL.ZS": _Bounds(0, 100),
    "NY.GDP.PCAP.CD": _Bounds(0, 500_000, low_inclusive=False),
    "OWID_LIFE_EXPECTANCY": _Bounds(0, 120, low_inclusive=False),
}


def _drop(cleaned: pd.DataFrame, mask: pd.Series, reason: str) -> pd.DataFrame:
    """Drop the rows where ``mask`` is true, logging how many and why."""
    dropped = int(mask.sum())
    if dropped:
        logger.info("dropped %d observation rows: %s", dropped, reason)
    return cleaned[~mask]


def _out_of_bounds(cleaned: pd.DataFrame) -> pd.Series:
    mask = pd.Series(False, index=cleaned.index)
    for code, bounds in _INDICATOR_BOUNDS.items():
        value = cleaned["value"]
        too_low = value < bounds.low if bounds.low_inclusive else value <= bounds.low
        mask |= (cleaned["indicator_code"] == code) & (too_low | (value > bounds.high))
    return mask


def _flag_iqr_outliers(cleaned: pd.DataFrame) -> pd.Series:
    """Flag Tukey IQR outliers per indicator without dropping rows."""
    flags = pd.Series(False, index=cleaned.index)
    for code, group in cleaned.groupby("indicator_code"):
        q1 = group["value"].quantile(0.25)
        q3 = group["value"].quantile(0.75)
        iqr = q3 - q1
        low = q1 - 1.5 * iqr
        high = q3 + 1.5 * iqr
        outlier_mask = (group["value"] < low) | (group["value"] > high)
        flags.loc[group.index] = outlier_mask
        flagged = int(outlier_mask.sum())
        if flagged:
            logger.info(
                "flagged %d IQR outliers for %s (bounds %.4f .. %.4f)",
                flagged,
                code,
                low,
                high,
            )
    return flags.astype(bool)


def clean_observations(
    normalized: pd.DataFrame,
    valid_iso3: set[str],
    *,
    year_window: tuple[int, int] = (2000, 2024),
) -> pd.DataFrame:
    if normalized.empty:
        return pd.DataFrame(columns=_OUTPUT_COLUMNS)

    cleaned = normalized.copy()

    cleaned["country_iso3"] = (
        cleaned["country_iso3"].astype("string").str.strip().str.upper()
    )
    cleaned = _drop(
        cleaned,
        ~cleaned["country_iso3"].isin(valid_iso3).fillna(False).astype(bool),
        "not a known country (aggregate, region or missing code)",
    )

    cleaned["year"] = pd.to_numeric(cleaned["year"], errors="coerce")
    cleaned["value"] = pd.to_numeric(cleaned["value"], errors="coerce")
    cleaned = _drop(
        cleaned,
        cleaned["year"].isna() | ~np.isfinite(cleaned["value"]),
        "missing or non-numeric year/value",
    )
    # astype(int) would truncate 2010.5 to 2010 and overwrite the real 2010 row.
    cleaned = _drop(cleaned, cleaned["year"] % 1 != 0, "year is not a whole number")
    cleaned["year"] = cleaned["year"].astype(int)

    year_low, year_high = year_window
    cleaned = _drop(
        cleaned,
        (cleaned["year"] < year_low) | (cleaned["year"] > year_high),
        f"year outside {year_low}-{year_high}",
    )

    cleaned["sex"] = cleaned["sex"].fillna(Sex.BOTH.value).replace(_SEX_MAP)
    cleaned = _drop(cleaned, ~cleaned["sex"].isin(_VALID_SEX), "unknown sex code")

    cleaned = _drop(cleaned, _out_of_bounds(cleaned), "value outside plausible bounds")

    cleaned = _drop(
        cleaned,
        cleaned.duplicated(subset=_KEY_COLUMNS, keep="last"),
        "duplicate (country, indicator, year, sex); kept the last",
    )

    cleaned["is_outlier"] = _flag_iqr_outliers(cleaned)

    return cleaned[_OUTPUT_COLUMNS].reset_index(drop=True)
