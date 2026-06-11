import requests


API_URL = "https://bdl.stat.gov.pl/api/v1/data/by-variable/{variable_id}"

VARIABLES_TO_CHECK = {
    58787: "average monthly gross wages - total",
    58879: "average monthly gross wages",
    196229: "average monthly gross wages - total alternative",
    459121: "unemployment",
}

YEARS_TO_CHECK = [2015, 2020, 2021, 2022, 2023]
UNIT_LEVELS = range(0, 8)


def check_variable(variable_id: int, variable_name: str) -> None:
    print("=" * 100)
    print(f"Variable ID: {variable_id} | {variable_name}")
    print("=" * 100)

    for unit_level in UNIT_LEVELS:
        params = [
            ("format", "json"),
            ("unit-level", str(unit_level)),
            ("page", "0"),
            ("page-size", "5"),
        ]

        for year in YEARS_TO_CHECK:
            params.append(("year", str(year)))

        try:
            response = requests.get(
                API_URL.format(variable_id=variable_id),
                params=params,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            total_records = data.get("totalRecords", 0)

            if total_records > 0:
                print(
                    f"FOUND DATA | unit-level={unit_level} | "
                    f"totalRecords={total_records}"
                )

        except requests.RequestException as error:
            print(f"ERROR | unit-level={unit_level} | {error}")


def main() -> None:
    for variable_id, variable_name in VARIABLES_TO_CHECK.items():
        check_variable(variable_id, variable_name)


if __name__ == "__main__":
    main()