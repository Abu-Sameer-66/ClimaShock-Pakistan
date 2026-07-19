import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path

DATA_FILE  = Path(__file__).parent.parent / "data" / "processed" / "climate_validated.csv"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "processed" / "plots"

# city colors — geographically meaningful
# warmer cities = warmer colors
CITY_COLORS = {
    "Sukkur":     "#D62728",   # darkest red    — hottest
    "Multan":     "#E8501A",   # red-orange
    "Hyderabad":  "#F07020",   # orange
    "Faisalabad": "#E89020",   # amber
    "Karachi":    "#C0A020",   # gold
    "Lahore":     "#6AAF30",   # light green
    "Sialkot":    "#2AA050",   # green
    "Peshawar":   "#1080C0",   # light blue
    "Islamabad":  "#1050A0",   # blue
    "Quetta":     "#303090",   # darkest blue   — coldest
}


def load_data():
    df = pd.read_csv(DATA_FILE, index_col="date", parse_dates=True)
    print(f"loaded: {len(df):,} rows")
    return df


def compute_annual(df):
    """
    daily data → yearly averages
    yeh trend dekhne ke liye zaroori hai — daily noise remove hoti hai
    """
    df["year"] = df.index.year
    annual = df.groupby(["city", "year"]).agg(
        avg_temp     = ("temp_c",       "mean"),
        max_temp     = ("temp_c",       "max"),
        total_rain   = ("rainfall_mm",  "sum"),
        avg_humidity = ("humidity_pct", "mean"),
        avg_wind     = ("wind_ms",      "mean"),
    ).reset_index()
    return annual


def linear_trend(years, values):
    """
    simple linear regression — numpy se, koi sklearn nahi
    returns: slope (change per year), intercept, r_squared
    """
    x = np.array(years, dtype=float)
    y = np.array(values, dtype=float)

    # numpy least squares — matrix form: [x, 1] * [m, b] = y
    A = np.column_stack([x, np.ones_like(x)])
    result = np.linalg.lstsq(A, y, rcond=None)
    m, b = result[0]

    # r-squared — trend kitna strong hai
    y_pred  = m * x + b
    ss_res  = np.sum((y - y_pred) ** 2)
    ss_tot  = np.sum((y - y.mean()) ** 2)
    r2      = 1 - ss_res / ss_tot if ss_tot > 0 else 0

    return m, b, r2


def plot_temperature_trends(annual, output_dir):
    """
    main visualization — 40 saal ka temperature trend
    har city ki apni line + trend line
    """
    fig = plt.figure(figsize=(14, 10))
    gs  = gridspec.GridSpec(2, 1, hspace=0.45, figure=fig)
    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1])

    years = sorted(annual["year"].unique())
    trend_data = []

    for city, color in CITY_COLORS.items():
        city_data = annual[annual["city"] == city].sort_values("year")
        if city_data.empty:
            continue

        y_vals = city_data["avg_temp"].values
        x_vals = city_data["year"].values

        # raw annual line — thin, semi-transparent
        ax1.plot(x_vals, y_vals, color=color, alpha=0.35, linewidth=0.9)

        # 5-year rolling mean — smoother trend
        city_series = pd.Series(y_vals, index=x_vals)
        rolling     = city_series.rolling(5, center=True).mean()
        ax1.plot(x_vals, rolling.values, color=color,
                 linewidth=2.0, label=city)

        # trend calculation
        m, b, r2 = linear_trend(x_vals, y_vals)
        warming_40yr = m * 40  # total change over 40 years

        trend_data.append({
            "city":         city,
            "slope_per_yr": round(m, 4),
            "warming_40yr": round(warming_40yr, 2),
            "r2":           round(r2, 3),
            "avg_temp":     round(y_vals.mean(), 2),
        })

    ax1.set_title("Pakistan — Annual Average Temperature Trends (1984–2023)\n"
                  "NASA POWER Data | ClimaRisk × ClimaShock Project",
                  fontsize=13, fontweight="bold", pad=12)
    ax1.set_xlabel("Year", fontsize=11)
    ax1.set_ylabel("Average Temperature (°C)", fontsize=11)
    ax1.legend(loc="upper left", fontsize=8, ncol=2,
               framealpha=0.7, edgecolor="lightgray")
    ax1.grid(True, alpha=0.2, linestyle="--")
    ax1.set_xlim(1984, 2023)

    # warming summary — horizontal bar chart
    trend_df = pd.DataFrame(trend_data).sort_values("warming_40yr", ascending=True)

    bars = ax2.barh(
        trend_df["city"],
        trend_df["warming_40yr"],
        color=[CITY_COLORS[c] for c in trend_df["city"]],
        alpha=0.85,
        edgecolor="white",
        linewidth=0.5,
    )

    # value labels on bars
    for bar, val in zip(bars, trend_df["warming_40yr"]):
        sign = "+" if val >= 0 else ""
        ax2.text(
            bar.get_width() + 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"{sign}{val:.2f}°C",
            va="center", fontsize=9, fontweight="bold"
        )

    ax2.set_title("Total Temperature Change Over 40 Years per City",
                  fontsize=12, fontweight="bold", pad=10)
    ax2.set_xlabel("Temperature Change (°C) — 1984 to 2023", fontsize=11)
    ax2.axvline(0, color="black", linewidth=0.8, alpha=0.5)
    ax2.grid(True, alpha=0.2, axis="x", linestyle="--")

    plt.tight_layout()

    output_file = output_dir / "temperature_trends_40yr.png"
    plt.savefig(output_file, dpi=150, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    print(f"saved → {output_file}")
    plt.close()

    return pd.DataFrame(trend_data)


def print_trend_report(trend_df):
    """research-grade findings print karta hai"""
    trend_df = trend_df.sort_values("warming_40yr", ascending=False)

    print("\n" + "="*55)
    print("CLIMARISK — 40-YEAR TEMPERATURE TREND REPORT")
    print("Data: NASA POWER | Period: 1984–2023")
    print("="*55)

    print(f"\n{'City':<14} {'Avg°C':>6} {'Per Year':>10} {'40yr Total':>12} {'R²':>6}")
    print("-"*55)
    for _, row in trend_df.iterrows():
        sign = "+" if row["slope_per_yr"] >= 0 else ""
        print(f"{row['city']:<14} "
              f"{row['avg_temp']:>6.2f} "
              f"{sign}{row['slope_per_yr']:>9.4f}°C "
              f"{sign}{row['warming_40yr']:>9.2f}°C "
              f"{row['r2']:>8.3f}")

    fastest = trend_df.iloc[0]
    print(f"\n KEY FINDING:")
    print(f"  Fastest warming: {fastest['city']} "
          f"(+{fastest['warming_40yr']}°C over 40 years)")
    print(f"  That is +{fastest['slope_per_yr']:.4f}°C per year on average")


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df     = load_data()
    annual = compute_annual(df)

    print(f"years covered: {annual['year'].min()} – {annual['year'].max()}")
    print(f"cities: {annual['city'].nunique()}")

    trend_df = plot_temperature_trends(annual, OUTPUT_DIR)
    print_trend_report(trend_df)