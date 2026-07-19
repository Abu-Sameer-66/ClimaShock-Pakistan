import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path

DATA_FILE  = Path(__file__).parent.parent / "data" / "processed" / "climate_validated.csv"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "processed" / "plots"

CITY_COLORS = {
    "Sukkur":     "#D62728",
    "Multan":     "#E8501A",
    "Hyderabad":  "#F07020",
    "Faisalabad": "#E89020",
    "Karachi":    "#C0A020",
    "Lahore":     "#6AAF30",
    "Sialkot":    "#2AA050",
    "Peshawar":   "#1080C0",
    "Islamabad":  "#1050A0",
    "Quetta":     "#303090",
}

# 1984-2000 = baseline period — pre-acceleration era
BASELINE_START = 1984
BASELINE_END   = 2000


def load_data():
    df = pd.read_csv(DATA_FILE, index_col="date", parse_dates=True)
    df["year"]  = df.index.year
    df["month"] = df.index.month
    return df


def compute_anomalies(df):
    """
    temperature anomaly = actual - baseline average
    baseline: 1984-2000 per city per month
    monthly baseline isliye ke January ka 15°C normal hai
    June ka 35°C normal hai — compare karna sahi nahi
    """
    baseline = df[
        (df["year"] >= BASELINE_START) &
        (df["year"] <= BASELINE_END)
    ].groupby(["city", "month"])["temp_c"].mean()

    # har row ke liye us city+month ka baseline subtract karo
    df = df.copy()
    df["temp_anomaly"] = df.apply(
        lambda row: row["temp_c"] - baseline.get((row["city"], row["month"]), np.nan),
        axis=1
    )

    return df


def compute_annual_stats(df):
    """annual aggregations — temperature + rainfall + heat stress"""

    # heat stress days = days above 40°C
    # 40°C WBGT threshold — outdoor workers ke liye dangerous
    df["heat_stress_day"] = (df["temp_c"] >= 40.0).astype(int)

    annual = df.groupby(["city", "year"]).agg(
        avg_temp        = ("temp_c",         "mean"),
        max_temp        = ("temp_c",         "max"),
        avg_anomaly     = ("temp_anomaly",   "mean"),
        total_rain      = ("rainfall_mm",    "sum"),
        rainy_days      = ("rainfall_mm",    lambda x: (x > 1.0).sum()),
        heat_stress_days= ("heat_stress_day","sum"),
        avg_humidity    = ("humidity_pct",   "mean"),
    ).reset_index()

    return annual


def linear_trend(years, values):
    """numpy se linear regression — sklearn nahi"""
    x  = np.array(years, dtype=float)
    y  = np.array(values, dtype=float)
    mask = ~np.isnan(y)
    x, y = x[mask], y[mask]

    A       = np.column_stack([x, np.ones_like(x)])
    result  = np.linalg.lstsq(A, y, rcond=None)
    m, b    = result[0]

    y_pred  = m * x + b
    ss_res  = np.sum((y - y_pred) ** 2)
    ss_tot  = np.sum((y - y.mean()) ** 2)
    r2      = 1 - ss_res / ss_tot if ss_tot > 0 else 0

    return m, b, r2


def plot_anomaly_trends(annual, output_dir):
    """
    anomaly plot — yeh actual climate signal dikhata hai
    noise remove, real warming visible
    """
    fig = plt.figure(figsize=(15, 11))
    gs  = gridspec.GridSpec(2, 2, hspace=0.45, wspace=0.35, figure=fig)
    ax1 = fig.add_subplot(gs[0, :])   # top — full width anomaly
    ax2 = fig.add_subplot(gs[1, 0])   # bottom left — rainfall
    ax3 = fig.add_subplot(gs[1, 1])   # bottom right — heat stress

    trend_results = []

    # --- PLOT 1: Temperature Anomaly ---
    for city, color in CITY_COLORS.items():
        city_data = annual[annual["city"] == city].sort_values("year")
        if city_data.empty:
            continue

        years  = city_data["year"].values
        anom   = city_data["avg_anomaly"].values

        # 5-year rolling mean — smoother signal
        series  = pd.Series(anom, index=years)
        rolling = series.rolling(5, center=True, min_periods=3).mean()

        ax1.plot(years, rolling.values, color=color,
                 linewidth=1.8, label=city, alpha=0.85)

        m, b, r2 = linear_trend(years, anom)
        trend_results.append({
            "city":          city,
            "anomaly_trend": round(m * 40, 3),   # 40yr total
            "per_year":      round(m, 5),
            "r2":            round(r2, 3),
        })

        # 2010-2023 average anomaly — is it positive?
        recent = city_data[city_data["year"] >= 2010]["avg_anomaly"].mean()

    ax1.axhline(0, color="gray", linewidth=1.0, linestyle="--", alpha=0.6)
    ax1.fill_between(
        [2010, 2023], ax1.get_ylim()[0] if ax1.get_ylim()[0] < -1 else -1.5,
        2, alpha=0.06, color="red", label="2010–2023 (recent period)"
    )
    ax1.set_title(
        "Pakistan Temperature Anomaly — Deviation from 1984–2000 Baseline\n"
        "NASA POWER Data | ClimaRisk Project | 5-Year Rolling Mean",
        fontsize=12, fontweight="bold"
    )
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Temperature Anomaly (°C)")
    ax1.legend(loc="upper left", fontsize=8, ncol=2, framealpha=0.7)
    ax1.grid(True, alpha=0.2, linestyle="--")
    ax1.set_xlim(1984, 2023)

    # --- PLOT 2: Annual Rainfall Trend ---
    for city, color in CITY_COLORS.items():
        city_data = annual[annual["city"] == city].sort_values("year")
        if city_data.empty:
            continue
        series  = pd.Series(
            city_data["total_rain"].values,
            index=city_data["year"].values
        )
        rolling = series.rolling(5, center=True, min_periods=3).mean()
        ax2.plot(city_data["year"].values, rolling.values,
                 color=color, linewidth=1.5, alpha=0.8, label=city)

    ax2.set_title("Annual Rainfall — 5yr Rolling Mean", fontsize=11, fontweight="bold")
    ax2.set_xlabel("Year")
    ax2.set_ylabel("Total Annual Rainfall (mm)")
    ax2.legend(fontsize=7, ncol=2, framealpha=0.6)
    ax2.grid(True, alpha=0.2, linestyle="--")
    ax2.set_xlim(1984, 2023)

    # --- PLOT 3: Heat Stress Days ---
    # bar chart — 1984-2000 vs 2010-2023 comparison
    cities_list = list(CITY_COLORS.keys())
    early_heat, recent_heat = [], []

    for city in cities_list:
        city_data = annual[annual["city"] == city]
        early  = city_data[city_data["year"] <= 2000]["heat_stress_days"].mean()
        recent = city_data[city_data["year"] >= 2010]["heat_stress_days"].mean()
        early_heat.append(early)
        recent_heat.append(recent)

    x_pos  = np.arange(len(cities_list))
    width  = 0.38
    bars1  = ax3.bar(x_pos - width/2, early_heat,  width,
                     label="1984–2000", color="steelblue",  alpha=0.75)
    bars2  = ax3.bar(x_pos + width/2, recent_heat, width,
                     label="2010–2023", color="crimson",    alpha=0.75)

    ax3.set_title("Days ≥40°C per Year\n1984–2000 vs 2010–2023",
                  fontsize=11, fontweight="bold")
    ax3.set_ylabel("Days per year")
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(cities_list, rotation=45, ha="right", fontsize=8)
    ax3.legend(fontsize=9)
    ax3.grid(True, alpha=0.2, axis="y", linestyle="--")

    plt.suptitle(
        "ClimaRisk — Pakistan Climate Intelligence Dashboard\n"
        "40 Years of NASA POWER Data (1984–2023)",
        fontsize=13, fontweight="bold", y=1.01
    )

    output_file = output_dir / "climate_dashboard.png"
    plt.savefig(output_file, dpi=150, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    print(f"saved → {output_file}")
    plt.close()

    return pd.DataFrame(trend_results)


def print_advanced_report(annual, trend_df):
    """key findings print karta hai — research-grade"""

    print("\n" + "="*60)
    print("CLIMARISK — ADVANCED CLIMATE ANALYSIS REPORT")
    print("Baseline: 1984–2000 | Recent: 2010–2023")
    print("="*60)

    # anomaly trends
    trend_df = trend_df.sort_values("anomaly_trend", ascending=False)
    print(f"\n{'City':<14} {'40yr Anomaly':>14} {'Per Year':>12} {'R²':>8}")
    print("-"*52)
    for _, row in trend_df.iterrows():
        sign = "+" if row["anomaly_trend"] >= 0 else ""
        print(f"{row['city']:<14} "
              f"{sign}{row['anomaly_trend']:>11.3f}°C "
              f"{sign}{row['per_year']:>10.5f}°C "
              f"{row['r2']:>9.3f}")

    # heat stress findings
    print(f"\n--- Heat Stress Days (>=40°C) ---")
    print(f"{'City':<14} {'1984-2000 avg':>14} {'2010-2023 avg':>14} {'Change':>10}")
    print("-"*56)

    for city in CITY_COLORS.keys():
        city_data = annual[annual["city"] == city]
        early  = city_data[city_data["year"] <= 2000]["heat_stress_days"].mean()
        recent = city_data[city_data["year"] >= 2010]["heat_stress_days"].mean()
        change = recent - early
        sign   = "+" if change >= 0 else ""
        print(f"{city:<14} {early:>13.1f}d {recent:>13.1f}d {sign}{change:>8.1f}d")

    # rainfall
    print(f"\n--- Rainfall Trend (total mm per year) ---")
    for city in ["Lahore", "Karachi", "Quetta", "Islamabad"]:
        city_data = annual[annual["city"] == city].sort_values("year")
        early_r  = city_data[city_data["year"] <= 2000]["total_rain"].mean()
        recent_r = city_data[city_data["year"] >= 2010]["total_rain"].mean()
        change_r = recent_r - early_r
        sign     = "+" if change_r >= 0 else ""
        print(f"  {city:<12}: {early_r:.0f}mm → {recent_r:.0f}mm  ({sign}{change_r:.0f}mm)")


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df     = load_data()
    df     = compute_anomalies(df)
    annual = compute_annual_stats(df)

    trend_df = plot_anomaly_trends(annual, OUTPUT_DIR)
    print_advanced_report(annual, trend_df)

    # save annual stats — feature engineering mein kaam aayega
    annual_file = OUTPUT_DIR.parent / "annual_stats.csv"
    annual.to_csv(annual_file, index=False)
    print(f"\nannual stats saved → {annual_file}")