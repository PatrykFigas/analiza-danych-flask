import json
from pathlib import Path

import pandas as pd
import requests


API_URL = "https://bdl.stat.gov.pl/api/v1/data/by-variable/{variable_id}"

VARIABLE_ID = 196229
UNIT_LEVEL = 2
YEARS = list(range(2015, 2024))

OUTPUT_DIR = Path("data")
RAW_OUTPUT_PATH = OUTPUT_DIR / "raw_average_monthly_wages.json"
CSV_OUTPUT_PATH = OUTPUT_DIR / "average_monthly_wages.csv"


def get_value(dictionary: dict, possible_keys: list[str]):
    for key in possible_keys:
        if key in dictionary:
            return dictionary[key]
    return None


def fetch_bdl_data() -> dict:
    params = [
        ("format", "json"),
        ("unit-level", str(UNIT_LEVEL)),
        ("page", "0"),
        ("page-size", "100"),
    ]

    for year in YEARS:
        params.append(("year", str(year)))

    response = requests.get(
        API_URL.format(variable_id=VARIABLE_ID),
        params=params,
        timeout=30,
    )
    response.raise_for_status()

    return response.json()


def normalize_bdl_data(data: dict) -> pd.DataFrame:
    rows = []

    for unit in data.get("results", []):
        unit_id = get_value(unit, ["id", "unitId"])
        region = get_value(unit, ["name", "unitName"])

        values = get_value(unit, ["values", "data"]) or []

        for item in values:
            year = get_value(item, ["year"])
            value = get_value(item, ["val", "value"])
            attribute_id = get_value(item, ["attrId", "attributeId"])

            rows.append(
                {
                    "unit_id": unit_id,
                    "region": region,
                    "year": year,
                    "average_monthly_wage_pln": value,
                    "attribute_id": attribute_id,
                }
            )

    dataframe = pd.DataFrame(rows)
    dataframe = dataframe.dropna(subset=["year", "average_monthly_wage_pln"])
    dataframe["year"] = dataframe["year"].astype(int)
    dataframe["average_monthly_wage_pln"] = dataframe[
        "average_monthly_wage_pln"
    ].astype(float)

    return dataframe.sort_values(["region", "year"])


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    data = fetch_bdl_data()

    total_records = data.get("totalRecords", 0)
    print(f"Total records: {total_records}")

    if total_records == 0:
        raise ValueError("No data found for selected variable.")

    with RAW_OUTPUT_PATH.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

    dataframe = normalize_bdl_data(data)

    if dataframe.empty:
        raise ValueError("Downloaded data could not be converted to a table.")

    dataframe.to_csv(CSV_OUTPUT_PATH, index=False, encoding="utf-8")

    print("Data downloaded successfully.")
    print(f"Variable ID: {VARIABLE_ID}")
    print(f"Unit level: {UNIT_LEVEL}")
    print(f"Years: {YEARS[0]}-{YEARS[-1]}")
    print(f"Rows saved: {len(dataframe)}")
    print(f"CSV file: {CSV_OUTPUT_PATH}")


if __name__ == "__main__":
    main()