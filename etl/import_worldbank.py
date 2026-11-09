import logging
from pathlib import Path

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_engine
from etl.clean import clean_observations
from etl.load import (
    get_or_create_indicator,
    get_or_create_source,
    log_import,
    upsert_countries,
    upsert_observations,
)
from etl.raw_files import read_source_url
from etl.transform_worldbank import (
    transform_worldbank_country_file,
    transform_worldbank_indicator_file,
)

logger = logging.getLogger(__name__)

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw" / "worldbank"
SOURCE_NAME = "World Bank"
SOURCE_URL = "https://data.worldbank.org"

# Indicators kept from Lab 1 of this project.
INDICATORS = [
    (
        "SL.UEM.TOTL.ZS",
        "Unemployment Rate",
        "% of labor force",
        "SL.UEM.TOTL.ZS_2000-2024.json",
    ),
    (
        "NY.GDP.PCAP.CD",
        "GDP per Capita",
        "current US$",
        "NY.GDP.PCAP.CD_2000-2024.json",
    ),
]


def import_all() -> list[dict]:
    results: list[dict] = []
    countries_path = RAW_DIR / "countries.json"
    if not countries_path.exists():
        results.append({
            "source": SOURCE_NAME,
            "item": "countries",
            "status": "failed",
            "message": f"missing {countries_path.name}; run Extract first",
        })
        return results

    with Session(get_engine()) as session:
        countries = transform_worldbank_country_file(countries_path)
        upsert_countries(session, countries)
        session.commit()
        results.append({
            "source": SOURCE_NAME,
            "item": "countries",
            "status": "ok",
            "message": f"{len(countries)} upserted",
        })

        valid_iso3 = set(countries["iso3"])
        source_id = get_or_create_source(session, SOURCE_NAME, SOURCE_URL)
        session.commit()

        for code, name, unit, filename in INDICATORS:
            path = RAW_DIR / filename
            if not path.exists():
                results.append({
                    "source": SOURCE_NAME,
                    "item": code,
                    "status": "skip",
                    "message": f"missing {path.name}",
                })
                continue

            try:
                raw = transform_worldbank_indicator_file(path, code)
                cleaned = clean_observations(raw, valid_iso3)
                indicator_id = get_or_create_indicator(
                    session, code, name, unit, source_id
                )
                loaded = upsert_observations(session, cleaned, indicator_id)
                log_import(
                    session, SOURCE_NAME, code, read_source_url(path), loaded
                )
                session.commit()
                results.append({
                    "source": SOURCE_NAME,
                    "item": code,
                    "status": "ok",
                    "message": (
                        f"raw={len(raw)} clean={len(cleaned)} loaded={loaded}"
                    ),
                })
            except (ValueError, OSError, SQLAlchemyError) as exc:
                session.rollback()
                logger.exception("%s: import failed", code)
                results.append({
                    "source": SOURCE_NAME,
                    "item": code,
                    "status": "failed",
                    "message": f"{type(exc).__name__}: {exc}",
                })

    return results


def main() -> None:
    results = import_all()
    for result in results:
        print(
            f"{result['source']:<18} {result['item']:<22} "
            f"{result['status']:<8} {result['message']}"
        )

    failed = [result["item"] for result in results if result["status"] == "failed"]
    if failed:
        raise SystemExit(f"{len(failed)} import(s) failed: {', '.join(failed)}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(levelname)s %(name)s: %(message)s"
    )
    main()
