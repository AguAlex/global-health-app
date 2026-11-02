import requests
import pandas as pd

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0"
}

def extract_worldbank_data(indicator_code="SL.UEM.TOTL.ZS", start_year=2010, end_year=2023) -> pd.DataFrame:
    """Extrage date brute de la Banca Mondială pentru un indicator dat."""
    url = f"https://api.worldbank.org/v2/country/all/indicator/{indicator_code}?format=json&date={start_year}:{end_year}&per_page=1000"
    print(f"[ETL Extract] Descarc date Banca Mondială: {url}")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        response.raise_for_status()
        json_data = response.json()
        
        if len(json_data) > 1 and json_data[1] is not None:
            return pd.DataFrame(json_data[1])
        return pd.DataFrame()
    except Exception as e:
        print(f"[ERROR WorldBank] A apărut o eroare la extragere: {e}")
        return pd.DataFrame()