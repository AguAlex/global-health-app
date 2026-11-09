import json

import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Accept": "text/csv,application/json,*/*",
}

print("=== 1. TEST WHO xMart API ===")
url_who = (
    "https://xmart-api-public.who.int/DATA_/RELAY_WHS"
    "?$filter=IND_CODE eq 'SDGSUICIDE'"
    "&$format=csv"
    "&$select=IND_CODE,DIM_TIME,DIM_GEO_CODE_M49,DIM_GEO_CODE_TYPE,"
    "GEO_NAME_SHORT,DIM_SEX,DIM_AGE,RATE_PER_100000_N"
)
try:
    res = requests.get(url_who, headers=HEADERS, timeout=60)
    print(f"Status code: {res.status_code}")
    if res.status_code == 200:
        lines = res.text.splitlines()
        print(f"CSV header: {lines[0]}")
        print(f"First data row: {lines[1] if len(lines) > 1 else '(empty)'}")
        print(f"Rows (incl. header): {len(lines)}")
except Exception as e:
    print(f"WHO error: {e}")


print("\n=== 2. TEST WORLD BANK API ===")
url_wb = "https://api.worldbank.org/v2/country/all/indicator/SL.UEM.TOTL.ZS?format=json&date=2020:2021&per_page=2"
try:
    res = requests.get(url_wb, headers=HEADERS, timeout=10)
    print(f"Status code: {res.status_code}")
    if res.status_code == 200:
        data = res.json()
        print("Response shape: array with 2 elements [metadata, records]")
        print("Sample first data record (data[1][0]):")
        print(json.dumps(data[1][0], indent=2))
except Exception as e:
    print(f"World Bank error: {e}")
