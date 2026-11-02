import requests
import pandas as pd

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0"
}

def extract_who_data(indicator_code="SDGSUICIDE") -> pd.DataFrame:
    """Extrage date brute de la OMS pentru un indicator dat."""
    url = f"https://ghoapi.azureedge.net/api/{indicator_code}"
    print(f"[ETL Extract] Descarc date OMS: {url}")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        response.raise_for_status()
        records = response.json().get("value", [])
        return pd.DataFrame(records)
    except Exception as e:
        print(f"[ERROR WHO] A apărut o eroare la extragere: {e}")
        return pd.DataFrame()