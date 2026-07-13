import pandas as pd
import numpy as np
from pathlib import Path

# NASA -999 = missing value ka code — yeh actual temperature nahi hai
NASA_MISSING = -999.0

# physically possible ranges — Pakistan ke context mein
VALID_RANGES = {
    "temp_c":       (-20.0, 55.0),   # Pakistan mein kabhi bhi is se bahar nahi
    "rainfall_mm":  (0.0,   500.0),  # daily max ever recorded ~400mm
    "humidity_pct": (0.0,   100.0),  # percentage — 0 to 100 only
    "wind_ms":      (0.0,   60.0),   # extreme cyclone bhi 60 se kam
}

DATA_DIR = Path(__file__).parent.parent / "data" / "raw" / "climate"


def load_all_data():
    combined_file = DATA_DIR / "all_cities_climate.csv"
    df = pd.read_csv(combined_file, index_col="date", parse_dates=True)
    print(f"loaded: {len(df):,} rows, {df['city'].nunique()} cities")
    return df


def check_nasa_missing(df):
    """NASA -999 values dhoondta hai — yeh actual data nahi hain"""
    print("\n--- NASA missing value check (-999) ---")
    issues = {}

    for col in ["temp_c", "rainfall_mm", "humidity_pct", "wind_ms"]:
        count = (df[col] == NASA_MISSING).sum()
        if count > 0:
            issues[col] = count
            print(f"  WARNING {col}: {count} values are -999 (missing)")
        else:
            print(f"  OK {col}: no -999 values")

    return issues


def check_physical_ranges(df):
    """physically impossible values check karta hai"""
    print("\n--- Physical range validation ---")
    issues = {}

    for col, (min_val, max_val) in VALID_RANGES.items():
        out_of_range = df[
            (df[col] < min_val) | (df[col] > max_val)
        ]

        if len(out_of_range) > 0:
            issues[col] = out_of_range
            print(f"  WARNING {col}: {len(out_of_range)} out-of-range values")
            # worst offenders dikhao
            print(f"    min found: {df[col].min():.2f}, max found: {df[col].max():.2f}")
            print(f"    expected:  {min_val} to {max_val}")
        else:
            print(f"  OK {col}: all values in [{min_val}, {max_val}]")

    return issues


def check_date_gaps(df):
    """missing dates check karta hai — koi gap toh nahi timeline mein"""
    print("\n--- Date continuity check ---")

    for city in df["city"].unique():
        city_df = df[df["city"] == city].sort_index()

        expected_days = pd.date_range(
            start=city_df.index.min(),
            end=city_df.index.max(),
            freq="D"
        )
        actual_days = city_df.index

        missing_dates = expected_days.difference(actual_days)

        if len(missing_dates) > 0:
            print(f"  WARNING {city}: {len(missing_dates)} missing dates")
        else:
            print(f"  OK {city}: complete timeline ({len(city_df)} days)")


def city_summary(df):
    """har city ka statistical summary — anomalies pakadne ke liye"""
    print("\n--- City-level statistics ---")

    summary = df.groupby("city").agg(
        avg_temp    = ("temp_c",       "mean"),
        max_temp    = ("temp_c",       "max"),
        min_temp    = ("temp_c",       "min"),
        total_rain  = ("rainfall_mm",  "sum"),
        avg_humidity= ("humidity_pct", "mean"),
        missing_any = ("temp_c",       lambda x: (x == NASA_MISSING).sum()),
    ).round(2)

    # sort by avg temp — makes sense geographically
    summary = summary.sort_values("avg_temp", ascending=False)
    print(summary.to_string())
    return summary


def fix_missing_values(df):
    """
    -999 values fix karta hai — forward fill method
    forward fill isliye: climate data mein kal ka value
    aaj ke missing value ka best estimate hai
    """
    print("\n--- Fixing missing values ---")

    # pehle -999 ko NaN banao — pandas ki standard missing marker
    for col in ["temp_c", "rainfall_mm", "humidity_pct", "wind_ms"]:
        nasa_missing_count = (df[col] == NASA_MISSING).sum()
        if nasa_missing_count > 0:
            df[col] = df[col].replace(NASA_MISSING, np.nan)
            print(f"  {col}: replaced {nasa_missing_count} NASA -999 with NaN")

    # city ke andar forward fill — doosre city ka data mix nahi hona chahiye
    df_fixed = df.groupby("city", group_keys=False).apply(
        lambda g: g.fillna(method="ffill").fillna(method="bfill")
    )

    remaining = df_fixed.isnull().sum().sum()
    print(f"  remaining NaN after fix: {remaining}")

    return df_fixed


def run_validation():
    df = load_all_data()

    # checks chalao
    missing_issues = check_nasa_missing(df)
    range_issues   = check_physical_ranges(df)
    check_date_gaps(df)
    summary        = city_summary(df)

    # fix karo agar zaroorat ho
    if missing_issues:
        df = fix_missing_values(df)

    # validated data save karo — raw se alag folder mein
    processed_dir = DATA_DIR.parent.parent / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    output_file = processed_dir / "climate_validated.csv"
    df.to_csv(output_file)
    print(f"\nvalidated data saved → {output_file}")
    print(f"shape: {df.shape}")

    return df


if __name__ == "__main__":
    df = run_validation()