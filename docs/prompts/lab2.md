# Lab 2 – AI prompts

## Prompt 1 – solve Lab 2 checklist on existing project

- Tool and model: Cursor / Auto (Composer)
- Date: 2026-11-04
- Prompt: ask to solve Lab 2 tasks from the PDF checklist, adapting requirements to this repository (`global-health-app`) and its existing Lab 1 indicators (`SDGSUICIDE`, `SL.UEM.TOTL.ZS`, `NY.GDP.PCAP.CD`).
- Result: ETL layout aligned with the course reference (`extract_*`, `transform_*`, `clean`, `load`, `import_*`), Alembic `is_outlier`, notebook, README, `docs/lab2_results.md`.
- Your changes: kept Lab 1 indicators instead of the reference health/life-expectancy set; added OWID `life-expectancy` as the third source; skipped live WHO GHO calls while the API returned 503 and used the cached raw WHO file.

## Prompt 2 – skip WHO API for now

- Tool and model: Cursor / Auto (Composer)
- Date: 2026-11-04
- Prompt: «skip who api for now»
- Result: notebook and docs updated to use `data/raw/who/SDGSUICIDE_from2000.json` without calling GHO; imports/quality checks finished with World Bank + OWID live extracts and cached WHO raw.
- Your changes: none beyond confirming the cache path and documenting the 503 outage in `docs/lab2_results.md`.

## Prompt 3 – replace GHO with xMart

- Tool and model: Cursor / Auto (Composer)
- Date: 2026-11-04
- Prompt: replace the broken WHO GHO API completely with the working WHO xMart API
- Result: `extract_who` downloads CSV from `xmart-api-public.who.int`; `transform_who` maps M49→ISO3 and xMart sex labels; raw file is `SDGSUICIDE_from2000.csv`.

## Code written without an assistant

- Lab 1 schema, models and first ETL sketch (`run_import`, early `clean`/`load`) already existed in the repo before Lab 2.
