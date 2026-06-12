import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


DATA_PATH = Path("data/average_monthly_wages.csv")
SUMMARY_OUTPUT_PATH = Path("data/analysis_summary.json")
CHARTS_DIR = Path("static/charts")


def load_data() -> pd.DataFrame:
    dataframe = pd.read_csv(DATA_PATH)
    dataframe["year"] = dataframe["year"].astype(int)
    dataframe["average_monthly_wage_pln"] = dataframe["average_monthly_wage_pln"].astype(float)
    return dataframe


def create_mean_wage_trend_chart(dataframe: pd.DataFrame) -> None:
    mean_by_year = (
        dataframe.groupby("year")["average_monthly_wage_pln"]
        .mean()
        .reset_index()
    )

    plt.figure(figsize=(10, 6))
    plt.plot(
        mean_by_year["year"],
        mean_by_year["average_monthly_wage_pln"],
        marker="o",
    )
    plt.title("Average monthly gross wage by year")
    plt.xlabel("Year")
    plt.ylabel("Average monthly wage [PLN]")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "mean_wage_trend.png")
    plt.close()


def create_latest_year_ranking_chart(dataframe: pd.DataFrame, latest_year: int) -> None:
    latest_data = dataframe[dataframe["year"] == latest_year].sort_values(
        "average_monthly_wage_pln",
        ascending=True,
    )

    plt.figure(figsize=(10, 8))
    plt.barh(
        latest_data["region"],
        latest_data["average_monthly_wage_pln"],
    )
    plt.title(f"Average monthly gross wage by voivodeship in {latest_year}")
    plt.xlabel("Average monthly wage [PLN]")
    plt.ylabel("Voivodeship")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "latest_year_ranking.png")
    plt.close()


def create_growth_chart(dataframe: pd.DataFrame, first_year: int, latest_year: int) -> pd.DataFrame:
    first_year_data = dataframe[dataframe["year"] == first_year][
        ["region", "average_monthly_wage_pln"]
    ].rename(columns={"average_monthly_wage_pln": "first_year_wage"})

    latest_year_data = dataframe[dataframe["year"] == latest_year][
        ["region", "average_monthly_wage_pln"]
    ].rename(columns={"average_monthly_wage_pln": "latest_year_wage"})

    growth_data = first_year_data.merge(latest_year_data, on="region")
    growth_data["wage_growth_pln"] = (
        growth_data["latest_year_wage"] - growth_data["first_year_wage"]
    )
    growth_data["wage_growth_percent"] = (
        growth_data["wage_growth_pln"] / growth_data["first_year_wage"] * 100
    )

    growth_data = growth_data.sort_values("wage_growth_percent", ascending=True)

    plt.figure(figsize=(10, 8))
    plt.barh(
        growth_data["region"],
        growth_data["wage_growth_percent"],
    )
    plt.title(f"Wage growth by voivodeship: {first_year}-{latest_year}")
    plt.xlabel("Growth [%]")
    plt.ylabel("Voivodeship")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "wage_growth.png")
    plt.close()

    return growth_data


def create_summary(dataframe: pd.DataFrame, growth_data: pd.DataFrame) -> dict:
    first_year = int(dataframe["year"].min())
    latest_year = int(dataframe["year"].max())

    latest_data = dataframe[dataframe["year"] == latest_year].copy()

    highest_wage_row = latest_data.loc[
        latest_data["average_monthly_wage_pln"].idxmax()
    ]

    lowest_wage_row = latest_data.loc[
        latest_data["average_monthly_wage_pln"].idxmin()
    ]

    highest_growth_row = growth_data.loc[
        growth_data["wage_growth_percent"].idxmax()
    ]

    lowest_growth_row = growth_data.loc[
        growth_data["wage_growth_percent"].idxmin()
    ]

    summary = {
        "first_year": first_year,
        "latest_year": latest_year,
        "regions_count": int(dataframe["region"].nunique()),
        "rows_count": int(len(dataframe)),
        "mean_wage_latest_year": round(
            float(latest_data["average_monthly_wage_pln"].mean()),
            2,
        ),
        "highest_wage_region": str(highest_wage_row["region"]),
        "highest_wage_value": round(
            float(highest_wage_row["average_monthly_wage_pln"]),
            2,
        ),
        "lowest_wage_region": str(lowest_wage_row["region"]),
        "lowest_wage_value": round(
            float(lowest_wage_row["average_monthly_wage_pln"]),
            2,
        ),
        "highest_growth_region": str(highest_growth_row["region"]),
        "highest_growth_percent": round(
            float(highest_growth_row["wage_growth_percent"]),
            2,
        ),
        "lowest_growth_region": str(lowest_growth_row["region"]),
        "lowest_growth_percent": round(
            float(lowest_growth_row["wage_growth_percent"]),
            2,
        ),
        "latest_year_ranking": latest_data.sort_values(
            "average_monthly_wage_pln",
            ascending=False,
        )[["region", "average_monthly_wage_pln"]].to_dict(orient="records"),
    }

    return summary


def main() -> None:
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)

    dataframe = load_data()

    first_year = int(dataframe["year"].min())
    latest_year = int(dataframe["year"].max())

    create_mean_wage_trend_chart(dataframe)
    create_latest_year_ranking_chart(dataframe, latest_year)
    growth_data = create_growth_chart(dataframe, first_year, latest_year)

    summary = create_summary(dataframe, growth_data)

    with SUMMARY_OUTPUT_PATH.open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2, ensure_ascii=False)

    print("Analysis completed successfully.")
    print(f"Charts saved in: {CHARTS_DIR}")
    print(f"Summary saved in: {SUMMARY_OUTPUT_PATH}")


if __name__ == "__main__":
    main()