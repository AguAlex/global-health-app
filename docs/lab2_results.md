# Lab 2 results

Indicators used in this project (Lab 1 adaptation): `SDGSUICIDE`, `SL.UEM.TOTL.ZS`, `NY.GDP.PCAP.CD`, plus `OWID_LIFE_EXPECTANCY`.

**Note:** extract uses the WHO **xMart** OData API (`xmart-api-public.who.int/DATA_/RELAY_WHS`), not the legacy GHO host (`ghoapi.azureedge.net`, which returned 503). Raw file: `data/raw/who/SDGSUICIDE_from2000.csv`.

## Task 2.2 – IQR outlier flags

`clean_observations()` adds `is_outlier` (Tukey: outside `[Q1 − 1.5·IQR, Q3 + 1.5·IQR]` per indicator). Rows are flagged, not dropped. Column added via Alembic migration `20261104_0001`.

| indicator_code | flagged | total | % |
|----------------|--------:|------:|--:|
| NY.GDP.PCAP.CD | 423 | 5242 | 8.07 |
| OWID_LIFE_EXPECTANCY | 73 | 5664 | 1.29 |
| SDGSUICIDE | 750 | 12058 | 6.22 |
| SL.UEM.TOTL.ZS | 172 | 4666 | 3.69 |

GDP and suicide rates are right-skewed, so the classic IQR rule flags relatively many high values; that is expected and is why Task 2.2 only flags instead of dropping.

## Task 2.3 – Idempotent imports

Imports were run twice (`import_worldbank`, `import_who`, `import_owid`). Row counts per indicator stayed the same; query 2 returned **0 duplicate** natural keys. Each run appended rows to `import_log` with the same `rows_loaded`.

Latest import_log (after second full pass):

| source_name | indicator_code | rows_loaded |
|-------------|----------------|------------:|
| World Bank | SL.UEM.TOTL.ZS | 4666 |
| World Bank | NY.GDP.PCAP.CD | 5242 |
| WHO xMart | SDGSUICIDE | 12058 |
| Our World in Data | OWID_LIFE_EXPECTANCY | 5664 |

Overview after imports:

| code | rows | first_year | last_year |
|------|-----:|-----------:|----------:|
| NY.GDP.PCAP.CD | 5242 | 2000 | 2024 |
| OWID_LIFE_EXPECTANCY | 5664 | 2000 | 2023 |
| SDGSUICIDE | 12058 | 2000 | 2021 |
| SL.UEM.TOTL.ZS | 4666 | 2000 | 2024 |

## Task 2.4 – Data quality checks

### 1. Countries

`COUNT(*) = 251`, `COUNT(DISTINCT region) = 7`.  
World Bank upsert contributes 217 economies (aggregates dropped). Extra rows come from the Lab 1 `pycountry` seed (region NULL for 34 rows). No `Aggregates` region remains.

### 2. Duplicates on the natural key

**0 rows** — unique constraint `uq_observation` + upsert hold.

### 3. Value ranges

| code | unit | min | max | avg |
|------|------|----:|----:|----:|
| NY.GDP.PCAP.CD | current US$ | 109.59 | 288001.57 | 16314.53 |
| OWID_LIFE_EXPECTANCY | years | 14.67 | 86.37 | 71.33 |
| SDGSUICIDE | per 100,000 | 0.00 | 95.20 | 9.61 |
| SL.UEM.TOTL.ZS | % labour force | 0.10 | 37.32 | 8.00 |

All within the plausible bounds configured in `etl/clean.py`.

### 4. Sex codes

Only `BTSX`, `MLE`, `FMLE` (WHO suicide is sex-disaggregated; WB/OWID stored as `BTSX`).

### 5. Missing values / year window

`null_values = 0`, `out_of_window = 0`.  
(Legacy PostgreSQL `NaN` numerics from an earlier import were removed; cleaning now rejects non-finite values.)

### 6. Last import vs rows stored

After removing legacy NaN leftovers, stored counts match the last import for each indicator. Earlier Lab 1 imports had loaded fewer World Bank rows; the upsert updates but never deletes, which is why a temporary mismatch can appear until orphans are cleaned — as noted in the lab text.

### 7. Coverage gaps (no `SDGSUICIDE`)

68 countries in `country` have no suicide observation (mostly microstates / Lab 1 seed extras without WHO coverage).

## Comparison with source websites (Romania, 2019)

| Source | Indicator | Stored | Source check |
|--------|-----------|-------:|-------------:|
| WHO xMart | SDGSUICIDE, BTSX | 9.1709 | 9.17093158 |
| World Bank API | SL.UEM.TOTL.ZS | 3.9120 | 3.912 |
| Our World in Data CSV | OWID_LIFE_EXPECTANCY | 75.3288 | 75.3288 |

Values match the sources (rounding to 4 decimal places in `NUMERIC(18,4)`).
