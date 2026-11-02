import requests
import pandas as pd

# Header pentru a preveni blocarea/eroarea 500 de la OMS
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0"
}

def fetch_who_indicator(indicator_code="SDGSUICIDE"):
    url = f"https://ghoapi.azureedge.net/api/{indicator_code}"
    print(f"--> Extragere OMS ({indicator_code}): {url}")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        json_data = response.json()
        
        records = json_data.get("value", [])
        if not records:
            print(f"   [WARN] OMS nu a returnat date pentru {indicator_code}.")
            return pd.DataFrame()
            
        print(f"   [OK] Primit {len(records)} rânduri brute de la OMS.")
        df = pd.DataFrame(records)
        
        if "SpatialDimType" in df.columns:
            df = df[df["SpatialDimType"] == "COUNTRY"]
            
        df_normalized = pd.DataFrame({
            "country_iso3": df["SpatialDim"],
            "indicator_code": indicator_code,
            "year": pd.to_numeric(df["TimeDim"], errors="coerce"),
            "sex": df["Dim1"].fillna("BTSX") if "Dim1" in df.columns else "BTSX",
            "value": pd.to_numeric(df["NumericValue"], errors="coerce")
        })
        return df_normalized.dropna(subset=["value", "year"])
        
    except requests.exceptions.HTTPError as e:
        print(f"   [EROARE HTTP OMS]: Serverul OMS a returnat status {e.response.status_code}.")
        print("   -> Se continuă execuția fără acest indicator OMS.")
        return pd.DataFrame()
    except Exception as e:
        print(f"   [EROARE CONEXIUNE OMS]: {e}")
        return pd.DataFrame()


def fetch_worldbank_indicator(indicator_code="SL.UEM.TOTL.ZS", start_year=2010, end_year=2023):
    url = f"https://api.worldbank.org/v2/country/all/indicator/{indicator_code}?format=json&date={start_year}:{end_year}&per_page=1000"
    print(f"--> Extragere Banca Mondială ({indicator_code}): {url}")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        json_data = response.json()
        
        if len(json_data) < 2 or json_data[1] is None:
            print("   [WARN] Banca Mondială nu a returnat date.")
            return pd.DataFrame()
            
        records = json_data[1]
        print(f"   [OK] Primit {len(records)} rânduri brute de la Banca Mondială.")
        
        rows = []
        for item in records:
            iso3 = item.get("countryiso3code")
            if iso3 and len(iso3) == 3 and item.get("value") is not None:
                rows.append({
                    "country_iso3": iso3,
                    "indicator_code": indicator_code,
                    "year": int(item["date"]),
                    "sex": "BTSX",
                    "value": float(item["value"])
                })
                
        return pd.DataFrame(rows)
    except Exception as e:
        print(f"   [EROARE BANCA MONDIALĂ]: {e}")
        return pd.DataFrame()


if __name__ == "__main__":
    # 1. Extragere OMS (cu tratare de eroare)
    df_suicide = fetch_who_indicator("SDGSUICIDE")
    
    # Dacă SDGSUICIDE dă 500, încercăm codul standard OMS de speranță de viață (din laborator)
    if df_suicide.empty:
        print("--> Încercare indicator OMS alternativ (WHOSIS_000001)...")
        df_suicide = fetch_who_indicator("WHOSIS_000001")
    
    # 2. Extragere Banca Mondială (foarte stabilă)
    df_unemployment = fetch_worldbank_indicator("SL.UEM.TOTL.ZS", 2010, 2023)
    df_gdp = fetch_worldbank_indicator("NY.GDP.PCAP.CD", 2010, 2023)
    
    # 3. Combinare date
    combined_df = pd.concat([df_suicide, df_unemployment, df_gdp], ignore_index=True)
    
    print("\n================ REZULTAT FINAL ================")
    if not combined_df.empty:
        print(combined_df.head(15))
        print(f"\nTotal observații extrase cu succes: {len(combined_df)}")
    else:
        print("Nu s-au putut extrage date.")