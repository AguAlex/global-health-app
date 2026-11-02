import pycountry
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from app.models import Source, Country, Indicator, Observation, ImportLog

def seed_dimensions(db: Session):
    """Populează tabelele de dimensiuni (source, indicator, country) dacă nu există deja."""
    # 1. Populează Sursele
    sources = [
        {"name": "WHO GHO", "url": "https://ghoapi.azureedge.net/api/"},
        {"name": "World Bank", "url": "https://api.worldbank.org/v2/"}
    ]
    for s in sources:
        db.merge(Source(name=s["name"], url=s["url"]))
    db.commit()

    who_src = db.query(Source).filter_by(name="WHO GHO").first()
    wb_src = db.query(Source).filter_by(name="World Bank").first()

    # 2. Populează Indicatorii
    indicators = [
        {"code": "SDGSUICIDE", "name": "Suicide Mortality Rate", "unit": "per 100,000", "source_id": who_src.source_id},
        {"code": "SL.UEM.TOTL.ZS", "name": "Unemployment Rate", "unit": "% of labor force", "source_id": wb_src.source_id},
        {"code": "NY.GDP.PCAP.CD", "name": "GDP per Capita", "unit": "Current USD ($)", "source_id": wb_src.source_id}
    ]
    for ind in indicators:
        existing = db.query(Indicator).filter_by(code=ind["code"]).first()
        if not existing:
            db.add(Indicator(**ind))

    # 3. Populează Țările din pycountry
    for c in pycountry.countries:
        existing_c = db.query(Country).filter_by(iso3=c.alpha_3).first()
        if not existing_c:
            db.add(Country(iso3=c.alpha_3, iso2=getattr(c, "alpha_2", None), name=c.name))

    db.commit()


def load_observations(db: Session, df_clean: pd.DataFrame, source_name: str, indicator_code: str, url: str):
    """Inserează observațiile în baza de date folosind Upsert (ON CONFLICT DO UPDATE)."""
    if df_clean.empty:
        print(f"[ETL Load] Nu există date de inserat pentru {indicator_code}.")
        return

    indicator = db.query(Indicator).filter_by(code=indicator_code).first()
    if not indicator:
        print(f"[ETL Load] Indicatorul {indicator_code} nu a fost găsit în baza de date.")
        return

    loaded_count = 0
    for _, row in df_clean.iterrows():
        stmt = insert(Observation).values(
            country_iso3=row["country_iso3"],
            indicator_id=indicator.indicator_id,
            year=int(row["year"]),
            sex=row["sex"],
            value=row["value"]
        )
        # Upsert: Dacă există deja o înregistrare pentru (country, indicator, year, sex), o actualizează
        stmt = stmt.on_conflict_do_update(
            constraint="uq_observation",
            set_={"value": stmt.excluded.value}
        )
        db.execute(stmt)
        loaded_count += 1

    # Jurnalizare în import_log
    log_entry = ImportLog(
        source_name=source_name,
        indicator_code=indicator_code,
        url=url,
        rows_loaded=loaded_count
    )
    db.add(log_entry)
    db.commit()
    print(f"[ETL Load] Am încărcat cu succes {loaded_count} rânduri pentru {indicator_code}.")