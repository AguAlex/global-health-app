import requests
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0"
}

print("=== 1. TEST API OMS (cu filtru OData) ===")
# Adăugăm $filter=SpatialDimType eq 'COUNTRY' pentru a reduce sarcina pe serverul Azure
url_who = "https://ghoapi.azureedge.net/api/SDGSUICIDE?$filter=SpatialDimType eq 'COUNTRY'"

try:
    res = requests.get(url_who, headers=HEADERS, timeout=20)
    print(f"Status Code OMS: {res.status_code}")
    if res.status_code == 200:
        data = res.json()
        records = data.get("value", [])
        print(f"Număr înregistrări primite: {len(records)}")
        if records:
            print("Exemplu prima înregistrare de la OMS:")
            print(json.dumps(records[0], indent=2))
    else:
        print(f"Serverul OMS a răspuns cu eroarea {res.status_code}")
except Exception as e:
    print(f"Eroare conexiune OMS: {e}")