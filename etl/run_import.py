from app.database import SessionLocal
from etl.extract_who import extract_who_data
from etl.extract_worldbank import extract_worldbank_data
from etl.clean import clean_who_data, clean_worldbank_data
from etl.load import seed_dimensions, load_observations

def run_pipeline():
    print("=== START ETL PIPELINE ===")
    db = SessionLocal()

    try:
        # 1. Populează tabelele de dimensiuni
        print("\n--- PASUL 1: Seeding Dimensions (source, indicator, country) ---")
        seed_dimensions(db)

        # 2. Extragere + Curățare + Încărcare OMS (Suicide Rate)
        print("\n--- PASUL 2: Procesare Indicator OMS (SDGSUICIDE) ---")
        who_url = "https://ghoapi.azureedge.net/api/SDGSUICIDE"
        raw_who = extract_who_data("SDGSUICIDE")
        clean_who = clean_who_data(raw_who, "SDGSUICIDE")
        load_observations(db, clean_who, "WHO GHO", "SDGSUICIDE", who_url)

        # 3. Extragere + Curățare + Încărcare Banca Mondială (Unemployment)
        print("\n--- PASUL 3: Procesare Indicator Banca Mondială (SL.UEM.TOTL.ZS) ---")
        wb_unemp_url = "https://api.worldbank.org/v2/country/all/indicator/SL.UEM.TOTL.ZS"
        raw_unemp = extract_worldbank_data("SL.UEM.TOTL.ZS", 2010, 2023)
        clean_unemp = clean_worldbank_data(raw_unemp, "SL.UEM.TOTL.ZS")
        load_observations(db, clean_unemp, "World Bank", "SL.UEM.TOTL.ZS", wb_unemp_url)

        # 4. Extragere + Curățare + Încărcare Banca Mondială (GDP per Capita)
        print("\n--- PASUL 4: Procesare Indicator Banca Mondială (NY.GDP.PCAP.CD) ---")
        wb_gdp_url = "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.PCAP.CD"
        raw_gdp = extract_worldbank_data("NY.GDP.PCAP.CD", 2010, 2023)
        clean_gdp = clean_worldbank_data(raw_gdp, "NY.GDP.PCAP.CD")
        load_observations(db, clean_gdp, "World Bank", "NY.GDP.PCAP.CD", wb_gdp_url)

        print("\n=== ETL PIPELINE FINALIZAT CU SUCCES! ===")

    except Exception as e:
        print(f"\n[CRITICAL ERROR] Pipeline-ul ETL a eșuat: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    run_pipeline()