"""Convenience entry point: import World Bank, then WHO xMart, then OWID."""

import logging
import sys

from etl import import_owid, import_who, import_worldbank


def main() -> None:
    logging.basicConfig(
        level=logging.INFO, format="%(levelname)s %(name)s: %(message)s"
    )
    failed: list[str] = []
    for module in (import_worldbank, import_who, import_owid):
        print(f"\n=== {module.__name__} ===")
        results = module.import_all()
        for result in results:
            print(
                f"{result['source']:<18} {result['item']:<22} "
                f"{result['status']:<8} {result['message']}"
            )
            if result["status"] == "failed":
                failed.append(f"{result['source']}:{result['item']}")

    if failed:
        raise SystemExit(f"{len(failed)} import(s) failed: {', '.join(failed)}")
    print("\n=== ALL IMPORTS OK ===")


if __name__ == "__main__":
    # Allow `python -m etl.run_import` from project root.
    sys.exit(main() or 0)
