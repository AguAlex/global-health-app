# Global Health Data Platform

PostgreSQL + FastAPI project for Lab 1–2 (CSP in Global Health): extract, clean and store indicators from WHO, the World Bank and Our World in Data.

## Indicators (adapted from Lab 1)

| Source | Code | Name |
|--------|------|------|
| WHO xMart | `SDGSUICIDE` | Suicide mortality rate (per 100,000) |
| World Bank | `SL.UEM.TOTL.ZS` | Unemployment rate (% of labor force) |
| World Bank | `NY.GDP.PCAP.CD` | GDP per capita (current US$) |
| Our World in Data | `OWID_LIFE_EXPECTANCY` | Life expectancy |

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # or create .env with DATABASE_URL
```

`.env` example:

```
DATABASE_URL=postgresql+psycopg://gh_user:gh_pass@localhost:5432/global_health
```

Create the schema (once) and apply migrations:

```bash
# tables from Lab 1
psql "$DATABASE_URL" -f db/schema.sql
# or: python -m app.create_tables

# Lab 2: observation.is_outlier
alembic upgrade head
```

## Extraction (raw files under `data/raw/`)

From the project root, with the venv active:

```python
from etl.extract_owid import download_owid_chart
from etl.extract_who import download_who_indicator
from etl.extract_worldbank import (
    download_worldbank_countries,
    download_worldbank_indicator,
)

download_worldbank_countries()
for code in ("SL.UEM.TOTL.ZS", "NY.GDP.PCAP.CD"):
    download_worldbank_indicator(code, years="2000:2024")

download_who_indicator("SDGSUICIDE")  # WHO xMart → data/raw/who/SDGSUICIDE_from2000.csv

download_owid_chart("life-expectancy")
```

Or open `notebooks/lab2_explore_raw.ipynb` (Task 2.1).

## Import (idempotent upsert)

World Bank first (loads `country`), then WHO and OWID:

```bash
python -m etl.import_worldbank
python -m etl.import_who
python -m etl.import_owid
# or: python -m etl.run_import
```

Re-running the imports updates existing rows and appends to `import_log`; it does not create duplicates on `(country_iso3, indicator_id, year, sex)`.

## Useful paths

- `etl/extract_*.py` – download only  
- `etl/transform_*.py` – raw → normalized columns  
- `etl/clean.py` – cleaning + IQR `is_outlier` flag  
- `etl/load.py` / `etl/import_*.py` – upsert + import log  
- `docs/lab2_results.md` – Task 2.2–2.4 results  
- `docs/prompts/lab2.md` – AI prompts used for Lab 2  

Never commit `.env` or `data/raw/` (see `.gitignore`).
