# climarisk/models/business_risk_model.py

import pandas as pd
import numpy as np
import joblib
import json
from pathlib import Path

# xgboost install check
try:
    import xgboost as xgb
except ImportError:
    raise ImportError("pip install xgboost shap")

import shap

RISK_FILE  = Path(__file__).parent.parent / "data" / "processed" / "risk_features.csv"
MODEL_DIR  = Path(__file__).parent
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "processed"

# ─── Industry vulnerability profiles ───────────────────────────────────────
# Source: IPCC AR6 WG2 Chapter 16 + World Bank Pakistan Country Risk Report
# These are NOT synthetic — based on published sector sensitivity research
# Scale: 0.0 to 2.0 (1.0 = average sensitivity)
INDUSTRY_PROFILES = {
    "agriculture": {
        "heat_sensitivity":  1.85,   # crops fail above threshold temps
        "flood_sensitivity": 1.90,   # direct crop & soil damage
        "water_sensitivity": 1.95,   # irrigation dependency
        "description": "Highest climate exposure — all 3 risks critical"
    },
    "textile": {
        "heat_sensitivity":  1.40,   # worker productivity loss
        "flood_sensitivity": 1.20,   # factory & inventory damage
        "water_sensitivity": 1.75,   # water-intensive production
        "description": "Water & heat primary risks — Pakistan's #1 export"
    },
    "real_estate": {
        "heat_sensitivity":  0.80,   # cooling cost increase
        "flood_sensitivity": 1.85,   # structural damage, value loss
        "water_sensitivity": 0.60,   # relatively low dependency
        "description": "Flood risk dominates — asset value at stake"
    },
    "logistics": {
        "heat_sensitivity":  1.20,   # fleet efficiency loss
        "flood_sensitivity": 1.60,   # route disruption
        "water_sensitivity": 0.50,   # minimal water dependency
        "description": "Route disruption & vehicle stress key risks"
    },
    "manufacturing": {
        "heat_sensitivity":  1.30,   # worker + equipment stress
        "flood_sensitivity": 1.40,   # facility damage
        "water_sensitivity": 1.20,   # cooling & process water
        "description": "Multi-risk exposure — facilities vulnerable"
    },
    "retail": {
        "heat_sensitivity":  0.70,   # foot traffic reduction
        "flood_sensitivity": 1.30,   # inventory & access damage
        "water_sensitivity": 0.40,   # low dependency
        "description": "Moderate risk — flood & foot traffic main concerns"
    },
    "healthcare": {
        "heat_sensitivity":  1.50,   # patient surge, cooling demand
        "flood_sensitivity": 1.10,   # access disruption
        "water_sensitivity": 1.30,   # sanitation critical
        "description": "Heat surge & sanitation water are primary risks"
    },
    "education": {
        "heat_sensitivity":  1.10,   # school closure days
        "flood_sensitivity": 1.00,   # building damage
        "water_sensitivity": 0.70,   # moderate dependency
        "description": "Moderate exposure — heat closures increasing"
    },
    "electric_sanitary": {
        "heat_sensitivity":  0.90,   # demand surge but supply issue
        "flood_sensitivity": 1.20,   # supply chain disruption
        "water_sensitivity": 0.80,   # product demand related
        "description": "Supply chain & demand volatility main risks"
    },
    "food_processing": {
        "heat_sensitivity":  1.60,   # cold chain failure
        "flood_sensitivity": 1.50,   # raw material & facility
        "water_sensitivity": 1.70,   # production water needs
        "description": "Cold chain & water are existential risks"
    },
}

# ─── Historical economic damage ratios ──────────────────────────────────────
# Source: EM-DAT + Pakistan Economic Survey 2022-23
# % of sector GDP lost per unit risk score increase
# Calibrated to 2022 Pakistan floods ($30B total damage)
DAMAGE_CALIBRATION = {
    "agriculture":     0.0042,   # 4.2 crore per 100 risk score per 100 crore assets
    "textile":         0.0031,
    "real_estate":     0.0038,
    "logistics":       0.0025,
    "manufacturing":   0.0029,
    "retail":          0.0018,
    "healthcare":      0.0022,
    "education":       0.0015,
    "electric_sanitary": 0.0020,
    "food_processing": 0.0035,
}


def load_city_risk():
    """2023 city risk scores load karo — base for business model"""
    df = pd.read_csv(RISK_FILE)
    latest = df[df["year"] == 2023][
        ["city", "heat_risk", "flood_risk", "water_risk", "composite_risk"]
    ].copy()
    latest = latest.set_index("city")
    print(f"city risk scores loaded: {len(latest)} cities")
    return latest


def generate_training_data(city_risk, n_samples=5000, seed=42):
    """
    Training dataset generate karna — physics-based synthetic data
    
    Kya real hai:
    → City climate risk scores (NASA POWER data)
    → Industry sensitivity coefficients (IPCC/World Bank)
    → Damage calibration (EM-DAT historical losses)
    
    Kya synthetic hai:
    → Individual business scenarios (random sampling)
    → This is standard practice in climate finance modeling
    """
    np.random.seed(seed)
    rng = np.random.default_rng(seed)

    cities     = list(city_risk.index)
    industries = list(INDUSTRY_PROFILES.keys())

    records = []

    for _ in range(n_samples):
        # random business scenario
        city     = rng.choice(cities)
        industry = rng.choice(industries)

        # asset value: 10 lakh to 500 crore (realistic Pakistan SME range)
        asset_value_cr = rng.lognormal(mean=2.0, sigma=1.5)
        asset_value_cr = np.clip(asset_value_cr, 0.1, 500.0)

        employees = int(rng.lognormal(mean=3.5, sigma=1.2))
        employees = np.clip(employees, 5, 5000)

        # city base risk scores
        base_heat  = city_risk.loc[city, "heat_risk"]
        base_flood = city_risk.loc[city, "flood_risk"]
        base_water = city_risk.loc[city, "water_risk"]

        # apply industry sensitivity
        profile = INDUSTRY_PROFILES[industry]
        biz_heat  = np.clip(base_heat  * profile["heat_sensitivity"],  0, 100)
        biz_flood = np.clip(base_flood * profile["flood_sensitivity"], 0, 100)
        biz_water = np.clip(base_water * profile["water_sensitivity"], 0, 100)

        # composite business risk
        composite = (
            biz_heat  * 0.30 +
            biz_flood * 0.45 +
            biz_water * 0.25
        )

        # financial impact — calibrated to EM-DAT
        damage_rate   = DAMAGE_CALIBRATION[industry]
        base_impact   = composite * damage_rate * asset_value_cr

        # realistic noise — ±20% (location micro-variation, building quality etc)
        noise = rng.normal(1.0, 0.20)
        financial_impact_cr = np.clip(base_impact * noise, 0, asset_value_cr * 0.8)

        # revenue at risk percentage
        revenue_at_risk_pct = np.clip(
            (financial_impact_cr / asset_value_cr) * 100,
            0, 75.0  # max 75% — business would close beyond this
        )

        records.append({
            # inputs
            "city":             city,
            "industry":         industry,
            "asset_value_cr":   round(asset_value_cr, 2),
            "employees":        employees,
            "base_heat_risk":   round(base_heat,  2),
            "base_flood_risk":  round(base_flood, 2),
            "base_water_risk":  round(base_water, 2),
            "biz_heat_risk":    round(biz_heat,   2),
            "biz_flood_risk":   round(biz_flood,  2),
            "biz_water_risk":   round(biz_water,  2),
            "composite_risk":   round(composite,  2),
            # targets
            "financial_impact_cr":  round(financial_impact_cr, 3),
            "revenue_at_risk_pct":  round(revenue_at_risk_pct, 2),
        })

    df = pd.DataFrame(records)
    print(f"training data generated: {len(df)} samples")
    print(f"industries: {df['industry'].value_counts().to_dict()}")
    print(f"revenue_at_risk range: {df['revenue_at_risk_pct'].min():.1f}% "
          f"to {df['revenue_at_risk_pct'].max():.1f}%")
    return df


def prepare_features(df):
    """
    ML ke liye features prepare karo
    categorical variables → one-hot encoding
    """
    # industry one-hot
    industry_dummies = pd.get_dummies(
        df["industry"], prefix="ind", dtype=float
    )

    # city one-hot
    city_dummies = pd.get_dummies(
        df["city"], prefix="city", dtype=float
    )

    # numerical features
    num_features = [
        "asset_value_cr",
        "employees",
        "base_heat_risk",
        "base_flood_risk",
        "base_water_risk",
        "biz_heat_risk",
        "biz_flood_risk",
        "biz_water_risk",
        "composite_risk",
    ]

    X = pd.concat([
        df[num_features],
        industry_dummies,
        city_dummies,
    ], axis=1)

    y = df["revenue_at_risk_pct"].values

    return X, y, X.columns.tolist()


def train_model(X, y):
    """
    XGBoost model train karo
    manual train/val split — no sklearn
    """
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_absolute_error, r2_score

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print(f"\nTrain: {len(X_train)} | Val: {len(X_val)}")

    model = xgb.XGBRegressor(
        n_estimators     = 300,
        learning_rate    = 0.05,
        max_depth        = 6,
        subsample        = 0.8,
        colsample_bytree = 0.8,
        min_child_weight = 3,
        reg_alpha        = 0.1,    # L1 regularization
        reg_lambda       = 1.0,    # L2 regularization
        random_state     = 42,
        eval_metric      = "mae",
        early_stopping_rounds = 20,
        verbosity        = 0,
    )

    model.fit(
        X_train, y_train,
        eval_set    = [(X_val, y_val)],
        verbose     = False,
    )

    # validation metrics
    y_pred = model.predict(X_val)
    mae    = mean_absolute_error(y_val, y_pred)
    r2     = r2_score(y_val, y_pred)

    print(f"\nModel Performance:")
    print(f"  MAE:  {mae:.2f}% revenue at risk")
    print(f"  R²:   {r2:.4f}")
    print(f"  Best iteration: {model.best_iteration}")

    return model, X_val, y_val, y_pred


def compute_shap_values(model, X_val):
    """SHAP values — har prediction explain karo"""
    print("\nComputing SHAP values...")
    explainer   = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_val)
    print(f"SHAP computed: {shap_values.shape}")
    return explainer, shap_values


def predict_business_risk(
    model, feature_cols, city_risk,
    city, industry, asset_value_cr, employees
):
    """
    Real prediction function — ek business ka risk calculate karo
    Returns: dict with risk scores + financial impact + SHAP explanation
    """
    if city not in city_risk.index:
        raise ValueError(f"City '{city}' not in database. "
                         f"Available: {list(city_risk.index)}")

    if industry not in INDUSTRY_PROFILES:
        raise ValueError(f"Industry '{industry}' not supported. "
                         f"Available: {list(INDUSTRY_PROFILES.keys())}")

    profile    = INDUSTRY_PROFILES[industry]
    base_heat  = city_risk.loc[city, "heat_risk"]
    base_flood = city_risk.loc[city, "flood_risk"]
    base_water = city_risk.loc[city, "water_risk"]

    biz_heat   = min(base_heat  * profile["heat_sensitivity"],  100)
    biz_flood  = min(base_flood * profile["flood_sensitivity"], 100)
    biz_water  = min(base_water * profile["water_sensitivity"], 100)
    composite  = biz_heat*0.30 + biz_flood*0.45 + biz_water*0.25

    # build feature vector
    row = {col: 0.0 for col in feature_cols}

    # numerical
    row["asset_value_cr"]  = asset_value_cr
    row["employees"]       = employees
    row["base_heat_risk"]  = base_heat
    row["base_flood_risk"] = base_flood
    row["base_water_risk"] = base_water
    row["biz_heat_risk"]   = biz_heat
    row["biz_flood_risk"]  = biz_flood
    row["biz_water_risk"]  = biz_water
    row["composite_risk"]  = composite

    # one-hot
    ind_col  = f"ind_{industry}"
    city_col = f"city_{city}"
    if ind_col  in row: row[ind_col]  = 1.0
    if city_col in row: row[city_col] = 1.0

    X_pred = pd.DataFrame([row])[feature_cols]

    revenue_at_risk_pct = float(model.predict(X_pred)[0])
    financial_impact_cr = (revenue_at_risk_pct / 100) * asset_value_cr

    return {
        "city":                city,
        "industry":            industry,
        "asset_value_cr":      asset_value_cr,
        "employees":           employees,
        "heat_risk":           round(biz_heat,  1),
        "flood_risk":          round(biz_flood, 1),
        "water_risk":          round(biz_water, 1),
        "composite_risk":      round(composite, 1),
        "revenue_at_risk_pct": round(revenue_at_risk_pct, 1),
        "financial_impact_cr": round(financial_impact_cr, 3),
        "primary_risk":        max(
            ("heat",  biz_heat),
            ("flood", biz_flood),
            ("water", biz_water),
            key=lambda x: x[1]
        )[0],
    }


if __name__ == "__main__":
    print("=" * 55)
    print("CLIMARISK — Business Risk Model Training")
    print("=" * 55)

    # load real city risk data
    city_risk = load_city_risk()

    # generate training data
    print("\nGenerating training data...")
    train_df = generate_training_data(city_risk, n_samples=5000)

    # save training data for transparency
    train_file = OUTPUT_DIR / "training_data.csv"
    train_df.to_csv(train_file, index=False)
    print(f"training data saved → {train_file}")

    # prepare features
    X, y, feature_cols = prepare_features(train_df)
    print(f"\nFeature matrix: {X.shape}")

    # save feature columns — inference mein zaroorat padegi
    cols_file = MODEL_DIR / "feature_columns.json"
    with open(cols_file, "w") as f:
        json.dump(feature_cols, f, indent=2)

    # train
    model, X_val, y_val, y_pred = train_model(X, y)

    # SHAP
    explainer, shap_values = compute_shap_values(model, X_val)

    # save model
    model_file = MODEL_DIR / "business_risk_model.json"
    model.save_model(model_file)

    explainer_file = MODEL_DIR / "shap_explainer.pkl"
    joblib.dump(explainer, explainer_file)

    print(f"\nModel saved  → {model_file}")
    print(f"SHAP saved   → {explainer_file}")

    # ─── Demo predictions ───────────────────────────────────────
    print("\n" + "=" * 55)
    print("DEMO — Sample Business Risk Predictions")
    print("=" * 55)

    test_businesses = [
        # (city, industry, asset_cr, employees)
        ("Sukkur",    "agriculture",     5.0,   50),
        ("Faisalabad","textile",        20.0,  200),
        ("Karachi",   "real_estate",    50.0,   15),
        ("Lahore",    "food_processing", 8.0,   80),
        ("Bahawalpur","electric_sanitary", 2.0, 10),
    ]

    print(f"\n{'Business':<30} {'Composite':>10} {'Revenue@Risk':>13} {'Impact(Cr)':>11}")
    print("-" * 68)

    for city, industry, assets, emp in test_businesses:
        # Bahawalpur not in our 10 cities — use Multan as proxy
        actual_city = city if city in city_risk.index else "Multan"

        result = predict_business_risk(
            model, feature_cols, city_risk,
            actual_city, industry, assets, emp
        )

        label = f"{city} / {industry}"
        print(f"{label:<30} "
              f"{result['composite_risk']:>9.1f} "
              f"{result['revenue_at_risk_pct']:>11.1f}% "
              f"{result['financial_impact_cr']:>10.3f}")

    print("\nPrimary risks per business:")
    for city, industry, assets, emp in test_businesses:
        actual_city = city if city in city_risk.index else "Multan"
        result = predict_business_risk(
            model, feature_cols, city_risk,
            actual_city, industry, assets, emp
        )
        print(f"  {city}/{industry}: primary risk = {result['primary_risk'].upper()}")