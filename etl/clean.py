import pandas as pd
import pycountry

def clean_who_data(df_raw: pd.DataFrame, indicator_code: str) -> pd.DataFrame:
    """Curăță și normalizează datele brute de la OMS."""
    if df_raw.empty:
        return pd.DataFrame()

    # Păstrăm doar rândurile la nivel de țară (fără regiuni sau agregări globale)
    if "SpatialDimType" in df_raw.columns:
        df_raw = df_raw[df_raw["SpatialDimType"] == "COUNTRY"]

    df_clean = pd.DataFrame({
        "country_iso3": df_raw["SpatialDim"],
        "indicator_code": indicator_code,
        "year": pd.to_numeric(df_raw["TimeDim"], errors="coerce"),
        "sex": df_raw["Dim1"].fillna("BTSX") if "Dim1" in df_raw.columns else "BTSX",
        "value": pd.to_numeric(df_raw["NumericValue"], errors="coerce")
    })

    # Filtrăm doar codurile ISO3 valide din 3 litere
    valid_iso3 = {c.alpha_3 for c in pycountry.countries}
    df_clean = df_clean[df_clean["country_iso3"].isin(valid_iso3)]

    return df_clean.dropna(subset=["country_iso3", "year", "value"])


def clean_worldbank_data(df_raw: pd.DataFrame, indicator_code: str) -> pd.DataFrame:
    """Curăță și normalizează datele brute de la Banca Mondială."""
    if df_raw.empty:
        return pd.DataFrame()

    rows = []
    valid_iso3 = {c.alpha_3 for c in pycountry.countries}

    for _, row in df_raw.iterrows():
        iso3 = row.get("countryiso3code")
        val = row.get("value")
        year = row.get("date")

        if iso3 in valid_iso3 and val is not None and year is not None:
            rows.append({
                "country_iso3": iso3,
                "indicator_code": indicator_code,
                "year": int(year),
                "sex": "BTSX",
                "value": float(val)
            })

    return pd.DataFrame(rows)