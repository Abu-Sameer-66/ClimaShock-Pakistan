import pandas as pd
import numpy as np
from pathlib import Path

# validated daily data
DAILY_FILE  = Path(__file__).parent.parent / "data" / "processed" / "climate_validated.csv"
ANNUAL_FILE = Path(__file__).parent.parent / "data" / "processed" / "annual_stats.csv"
OUTPUT_DIR  = Path(__file__).parent.parent / "data" / "processed"


def load_data():
    daily  = pd.read_csv(DAILY_FILE,  index_col="date", parse_dates=True)
    annual = pd.read_csv(ANNUAL_FILE)
    daily["year"]  = daily.index.year
    daily["month"] = daily.index.month
    daily["doy"]   = daily.index.dayofyear  # day of year
    print(f"daily:  {len(daily):,} rows")
    print(f"annual: {len(annual):,} rows")
    return daily, annual


def compute_heat_risk_features(daily):
    """
    heat risk features — dry temperature + wet bulb both
    wet bulb = actual human heat stress metric
    Steadman 1979 formula — used by meteorologists globally
    """
    df = daily.copy()

    # --- WET BULB TEMPERATURE (Steadman approximation) ---
    # yeh formula simple approximation hai
    # T = temp_c, RH = humidity percentage
    T  = df["temp_c"]
    RH = df["humidity_pct"]

    df["wet_bulb_c"] = (
        T * np.arctan(0.151977 * (RH + 8.313659) ** 0.5)
        + np.arctan(T + RH)
        - np.arctan(RH - 1.676331)
        + 0.00391838 * RH ** 1.5 * np.arctan(0.023101 * RH)
        - 4.686035
    )

    # --- HEAT INDEX CATEGORIES ---
    # 35°C wet bulb = absolute human survival limit
    # 28°C wet bulb = dangerous for outdoor work
    df["extreme_heat_day"] = (df["wet_bulb_c"] >= 32.0).astype(int)  # dangerous
    df["critical_heat_day"]= (df["wet_bulb_c"] >= 35.0).astype(int)  # survival limit

    # dry temperature thresholds
    df["hot_day_38"]  = (df["temp_c"] >= 38.0).astype(int)
    df["hot_day_42"]  = (df["temp_c"] >= 42.0).astype(int)

    print("heat features: wet_bulb_c, extreme_heat_day, critical_heat_day")
    return df


def compute_flood_risk_features(daily):
    """
    flood risk features — rainfall patterns + extremes
    """
    df = daily.copy()

    # extreme rainfall days
    df["heavy_rain_day"]   = (df["rainfall_mm"] >= 50.0).astype(int)   # heavy
    df["extreme_rain_day"] = (df["rainfall_mm"] >= 100.0).astype(int)  # extreme
    df["flood_proxy_day"]  = (df["rainfall_mm"] >= 150.0).astype(int)  # direct flood risk

    # 7-day rolling total — sustained rainfall = flood
    df = df.sort_values(["city", "date"] if "city" in df.columns else "date")
    df["rain_7day"] = (
        df.groupby("city")["rainfall_mm"]
        .transform(lambda x: x.rolling(7, min_periods=1).sum())
    )
    df["rain_7day_flood"] = (df["rain_7day"] >= 200.0).astype(int)

    print("flood features: heavy/extreme/flood_proxy rain, 7-day rolling")
    return df


def compute_water_stress_features(daily):
    """
    water scarcity features
    PDSI proxy — simplified drought index
    """
    df = daily.copy()

    # monthly water balance — rain minus evaporation demand
    # simplified PET (potential evapotranspiration) using temperature
    # Thornthwaite method approximation
    df["pet_proxy"] = np.where(
        df["temp_c"] > 0,
        0.533 * (df["temp_c"] ** 1.514),  # simplified Thornthwaite
        0.0
    )
    df["water_balance"] = df["rainfall_mm"] - df["pet_proxy"]

    # drought day = more evaporation demand than rainfall
    df["drought_day"] = (df["water_balance"] < -5.0).astype(int)

    print("water stress features: pet_proxy, water_balance, drought_day")
    return df


def build_annual_risk_features(daily):
    """
    daily features → yearly risk scores per city
    yeh directly ML model ka input banega
    """

    annual = daily.groupby(["city", "year"]).agg(
        # temperature
        avg_temp           = ("temp_c",          "mean"),
        max_temp           = ("temp_c",           "max"),
        avg_wet_bulb       = ("wet_bulb_c",       "mean"),
        max_wet_bulb       = ("wet_bulb_c",        "max"),
        extreme_heat_days  = ("extreme_heat_day", "sum"),
        critical_heat_days = ("critical_heat_day","sum"),
        hot_days_38        = ("hot_day_38",       "sum"),

        # flood
        heavy_rain_days    = ("heavy_rain_day",   "sum"),
        extreme_rain_days  = ("extreme_rain_day", "sum"),
        flood_proxy_days   = ("flood_proxy_day",  "sum"),
        flood_week_events  = ("rain_7day_flood",  "sum"),
        total_rainfall     = ("rainfall_mm",      "sum"),
        max_daily_rain     = ("rainfall_mm",       "max"),

        # water stress
        drought_days       = ("drought_day",      "sum"),
        avg_water_balance  = ("water_balance",    "mean"),

        # humidity
        avg_humidity       = ("humidity_pct",     "mean"),
        avg_wind           = ("wind_ms",          "mean"),
    ).reset_index()

    return annual


def compute_composite_risk_scores(annual):
    """
    raw features → 0-100 risk scores
    min-max normalization per feature
    phir weighted average → composite score
    """

    def normalize(series):
        """0 to 100 scale — higher = more risk"""
        mn, mx = series.min(), series.max()
        if mx == mn:
            return pd.Series(50.0, index=series.index)
        return (series - mn) / (mx - mn) * 100

    df = annual.copy()

    # HEAT RISK SCORE — wet bulb based (more accurate than dry temp)
    df["heat_risk"] = (
        normalize(df["avg_wet_bulb"])      * 0.40 +
        normalize(df["extreme_heat_days"]) * 0.35 +
        normalize(df["max_wet_bulb"])      * 0.25
    )

    # FLOOD RISK SCORE
    df["flood_risk"] = (
        normalize(df["total_rainfall"])    * 0.25 +
        normalize(df["extreme_rain_days"]) * 0.30 +
        normalize(df["flood_proxy_days"])  * 0.25 +
        normalize(df["flood_week_events"]) * 0.20
    )

    # WATER STRESS RISK SCORE
    # invert water balance — lower balance = higher risk
    df["water_risk"] = (
        normalize(-df["avg_water_balance"]) * 0.50 +
        normalize(df["drought_days"])       * 0.50
    )

    # COMPOSITE RISK — weighted
    # flood weight high because data shows this is primary Pakistan risk
    df["composite_risk"] = (
        df["heat_risk"]  * 0.30 +
        df["flood_risk"] * 0.45 +
        df["water_risk"] * 0.25
    )

    return df


def print_risk_summary(risk_df):
    """2023 ke liye har city ka risk score"""
    latest = risk_df[risk_df["year"] == 2023].sort_values(
        "composite_risk", ascending=False
    )

    print("\n" + "="*65)
    print("CLIMARISK — 2023 RISK SCORES (0-100 scale)")
    print("="*65)
    print(f"{'City':<14} {'Heat':>8} {'Flood':>8} {'Water':>8} {'Composite':>11}")
    print("-"*55)

    for _, row in latest.iterrows():
        print(f"{row['city']:<14} "
              f"{row['heat_risk']:>8.1f} "
              f"{row['flood_risk']:>8.1f} "
              f"{row['water_risk']:>8.1f} "
              f"{row['composite_risk']:>11.1f}")

    top = latest.iloc[0]
    print(f"\nHIGHEST RISK: {top['city']} — composite score {top['composite_risk']:.1f}/100")


if __name__ == "__main__":
    daily, _ = load_data()

    print("\nComputing features...")
    daily = compute_heat_risk_features(daily)
    daily = compute_flood_risk_features(daily)
    daily = compute_water_stress_features(daily)

    print("\nBuilding annual risk features...")
    annual_risk = build_annual_risk_features(daily)

    print("\nComputing composite risk scores...")
    risk_df = compute_composite_risk_scores(annual_risk)

    # save
    out_file = OUTPUT_DIR / "risk_features.csv"
    risk_df.to_csv(out_file, index=False)
    print(f"\nrisk features saved → {out_file}")
    print(f"shape: {risk_df.shape}")

    print_risk_summary(risk_df)