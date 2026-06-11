import json
import sys

import requests


API_URL = "https://bdl.stat.gov.pl/api/v1/variables/search"


def search_variables(keyword: str) -> None:
    params = {
        "format": "json",
        "name": keyword,
        "page-size": 10,
    }

    response = requests.get(API_URL, params=params, timeout=20)
    response.raise_for_status()

    data = response.json()

    total_records = data.get("totalRecords", 0)
    results = data.get("results", [])

    print(f"Search keyword: {keyword}")
    print(f"Total records: {total_records}")
    print("-" * 80)

    if not results:
        print("No variables found.")
        return

    for variable in results:
        print(json.dumps(variable, indent=2, ensure_ascii=False))
        print("-" * 80)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/search_bdl_variables.py <keyword>")
        sys.exit(1)

    search_keyword = " ".join(sys.argv[1:])
    search_variables(search_keyword)