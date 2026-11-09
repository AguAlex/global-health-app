"""Download WHO indicator data from the public xMart OData API.

Replaces the legacy GHO OData host (``ghoapi.azureedge.net``), which has been
unreliable. Raw landing files are CSV as returned by xMart.
"""

from pathlib import Path

import requests

from etl.raw_files import save_raw

BASE_URL = "https://xmart-api-public.who.int/DATA_/RELAY_WHS"
_DEFAULT_RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw" / "who"
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) "
        "Gecko/20100101 Firefox/120.0"
    ),
    "Accept": "text/csv,*/*",
}
_SELECT = (
    "IND_CODE,DIM_TIME,DIM_GEO_CODE_M49,DIM_GEO_CODE_TYPE,"
    "GEO_NAME_SHORT,DIM_SEX,DIM_AGE,RATE_PER_100000_N"
)


class WhoApiError(RuntimeError):
    """The WHO xMart API returned a response we cannot interpret."""


def _download_csv(code: str) -> tuple[bytes, str]:
    # xMart rejects combined $filter expressions that include DIM_TIME
    # (HTTP 406), so year windows are applied after download in transform.
    params = {
        "$filter": f"IND_CODE eq '{code}'",
        "$format": "csv",
        "$select": _SELECT,
    }
    response = requests.get(
        BASE_URL, params=params, headers=_HEADERS, timeout=180
    )
    response.raise_for_status()
    content_type = response.headers.get("content-type", "")
    if "csv" not in content_type and not response.text.lstrip().startswith(
        "IND_CODE"
    ):
        raise WhoApiError(
            f"{response.url}: expected CSV, got {content_type!r}: "
            f"{response.text[:200]!r}"
        )
    return response.content, response.url


def download_who_indicator(
    code: str,
    year_from: int = 2000,
    *,
    output_dir: Path | None = None,
) -> tuple[Path, str]:
    """Download ``code`` from xMart and save as ``{code}_from{year_from}.csv``.

    ``year_from`` is kept in the filename for Lab compatibility; the year
    window itself is enforced in ``transform_who`` / ``clean_observations``.
    """
    content, url = _download_csv(code)
    path = save_raw(
        output_dir or _DEFAULT_RAW_DIR,
        f"{code}_from{year_from}.csv",
        content,
        url,
    )
    return path, url


def download_who_indicator_for_year(
    code: str,
    year: int,
    *,
    output_dir: Path | None = None,
) -> tuple[Path, str]:
    """Download ``code`` from xMart and save as ``{code}_{year}.csv``.

    Same full extract as ``download_who_indicator``; year filtering happens
    downstream. Prefer the ``fromN`` helper for the normal Lab pipeline.
    """
    content, url = _download_csv(code)
    path = save_raw(
        output_dir or _DEFAULT_RAW_DIR,
        f"{code}_{year}.csv",
        content,
        url,
    )
    return path, url
