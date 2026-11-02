import requests
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0"
}

print("=== 1. TEST API OMS (WHO GHO) ===")
url_who = "https://ghoapi.azureedge.net/api/SDGSUICIDE"
try:
    res = requests.get(url_who, headers=HEADERS, timeout=10)
    print(f"Status Code: {res.status_code}")
    if res.status_code == 200:
        data = res.json()
        print(f"Chei principale în JSON: {list(data.keys())}")
        print("Exemplu primul element din 'value':")
        print(json.dumps(data["value"][0], indent=2))
except Exception as e:
    print(f"Eroare OMS: {e}")


print("\n=== 2. TEST API BANCA MONDIALĂ ===")
url_wb = "https://api.worldbank.org/v2/country/all/indicator/SL.UEM.TOTL.ZS?format=json&date=2020:2021&per_page=2"
try:
    res = requests.get(url_wb, headers=HEADERS, timeout=10)
    print(f"Status Code: {res.status_code}")
    if res.status_code == 200:
        data = res.json()
        print("Structură răspuns: Array cu 2 elemente [Metadata, Date]")
        print("Exemplu prima înregistrare de date (data[1][0]):")
        print(json.dumps(data[1][0], indent=2))
except Exception as e:
    print(f"Eroare Banca Mondială: {e}")