# climarisk/api/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
import xgboost as xgb
import pandas as pd
import numpy as np
import joblib
import json
from pathlib import Path

# ── paths ──────────────────────────────────────────────────────────────────
BASE        = Path(__file__).parent.parent
MODEL_FILE  = BASE / "models" / "business_risk_model.json"
COLS_FILE   = BASE / "models" / "feature_columns.json"
SHAP_FILE   = BASE / "models" / "shap_explainer.pkl"

# ── load on startup ─────────────────────────────────────────────────────────
print("Loading ClimaRisk models...")

model = xgb.XGBRegressor()
model.load_model(MODEL_FILE)

with open(COLS_FILE) as f:
    FEATURE_COLS = json.load(f)

try:
    explainer = joblib.load(SHAP_FILE)
    SHAP_AVAILABLE = True
except Exception:
    SHAP_AVAILABLE = False
    print("SHAP not available — predictions will work without explanations")

print(f"Model loaded — {len(FEATURE_COLS)} features")
print(f"SHAP available: {SHAP_AVAILABLE}")

# ── city risk scores (from NASA POWER analysis) ──────────────────────────
CITY_RISK = {
    "Sukkur":     {"heat": 72.1, "flood":  2.2, "water": 93.0},
    "Karachi":    {"heat": 78.2, "flood":  1.0, "water": 84.6},
    "Hyderabad":  {"heat": 73.0, "flood":  1.5, "water": 88.2},
    "Multan":     {"heat": 69.5, "flood":  2.3, "water": 89.1},
    "Faisalabad": {"heat": 69.4, "flood":  4.6, "water": 81.0},
    "Lahore":     {"heat": 69.8, "flood":  7.8, "water": 74.5},
    "Sialkot":    {"heat": 70.3, "flood":  9.0, "water": 70.7},
    "Islamabad":  {"heat": 63.7, "flood":  9.0, "water": 62.5},
    "Peshawar":   {"heat": 63.0, "flood":  6.9, "water": 63.5},
    "Quetta":     {"heat": 29.8, "flood":  2.1, "water": 31.1},
}

INDUSTRY_PROFILES = {
    "agriculture":       {"heat": 1.85, "flood": 1.90, "water": 1.95},
    "textile":           {"heat": 1.40, "flood": 1.20, "water": 1.75},
    "real_estate":       {"heat": 0.80, "flood": 1.85, "water": 0.60},
    "logistics":         {"heat": 1.20, "flood": 1.60, "water": 0.50},
    "manufacturing":     {"heat": 1.30, "flood": 1.40, "water": 1.20},
    "retail":            {"heat": 0.70, "flood": 1.30, "water": 0.40},
    "healthcare":        {"heat": 1.50, "flood": 1.10, "water": 1.30},
    "education":         {"heat": 1.10, "flood": 1.00, "water": 0.70},
    "electric_sanitary": {"heat": 0.90, "flood": 1.20, "water": 0.80},
    "food_processing":   {"heat": 1.60, "flood": 1.50, "water": 1.70},
}

# ── FastAPI app ─────────────────────────────────────────────────────────────
app = FastAPI(
    title       = "ClimaRisk API",
    description = "Pakistan Climate Risk Intelligence — Business Level Assessment",
    version     = "2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins  = ["*"],
    allow_methods  = ["*"],
    allow_headers  = ["*"],
)

# ── request / response schemas ───────────────────────────────────────────────
class RiskRequest(BaseModel):
    city:          str   = Field(..., example="Lahore")
    industry:      str   = Field(..., example="textile")
    asset_value_cr: float = Field(..., gt=0, example=20.0,
                                  description="Asset value in Crore PKR")
    employees:     int   = Field(..., gt=0, example=200)

    @validator("city")
    def city_must_exist(cls, v):
        if v not in CITY_RISK:
            raise ValueError(
                f"City '{v}' not supported. "
                f"Available: {list(CITY_RISK.keys())}"
            )
        return v

    @validator("industry")
    def industry_must_exist(cls, v):
        if v not in INDUSTRY_PROFILES:
            raise ValueError(
                f"Industry '{v}' not supported. "
                f"Available: {list(INDUSTRY_PROFILES.keys())}"
            )
        return v


class RiskResponse(BaseModel):
    city:                  str
    industry:              str
    asset_value_cr:        float
    employees:             int
    heat_risk:             float
    flood_risk:            float
    water_risk:            float
    composite_risk:        float
    revenue_at_risk_pct:   float
    financial_impact_cr:   float
    primary_risk:          str
    risk_level:            str
    shap_explanation:      dict
    data_source:           str
    model_version:         str


# ── core prediction logic ───────────────────────────────────────────────────
def compute_risk(city, industry, asset_cr, employees):
    base   = CITY_RISK[city]
    prof   = INDUSTRY_PROFILES[industry]

    biz_h  = min(base["heat"]  * prof["heat"],  100.0)
    biz_f  = min(base["flood"] * prof["flood"], 100.0)
    biz_w  = min(base["water"] * prof["water"], 100.0)
    comp   = biz_h * 0.30 + biz_f * 0.45 + biz_w * 0.25

    # build feature vector
    row = {col: 0.0 for col in FEATURE_COLS}
    row.update({
        "asset_cr":   asset_cr,
        "employees":  employees,
        "base_heat":  base["heat"],
        "base_flood": base["flood"],
        "base_water": base["water"],
        "biz_heat":   biz_h,
        "biz_flood":  biz_f,
        "biz_water":  biz_w,
        "composite":  comp,
    })

    ind_col  = f"ind_{industry}"
    city_col = f"city_{city}"
    if ind_col  in row: row[ind_col]  = 1.0
    if city_col in row: row[city_col] = 1.0

    X = pd.DataFrame([row])[FEATURE_COLS]

    rev_risk   = float(model.predict(X)[0])
    fin_impact = (rev_risk / 100.0) * asset_cr

    # risk level label
    if comp >= 60:   level = "CRITICAL"
    elif comp >= 45: level = "HIGH"
    elif comp >= 30: level = "MODERATE"
    else:            level = "LOW"

    # primary risk
    primary = max(
        [("heat", biz_h), ("flood", biz_f), ("water", biz_w)],
        key=lambda x: x[1]
    )[0]

    # SHAP explanation
    shap_dict = {}
    if SHAP_AVAILABLE:
        try:
            sv = explainer.shap_values(X)
            top_features = sorted(
                zip(FEATURE_COLS, sv[0]),
                key=lambda x: abs(x[1]),
                reverse=True
            )[:5]
            shap_dict = {
                feat: round(float(val), 4)
                for feat, val in top_features
            }
        except Exception:
            shap_dict = {"note": "SHAP temporarily unavailable"}

    return {
        "city":                city,
        "industry":            industry,
        "asset_value_cr":      asset_cr,
        "employees":           employees,
        "heat_risk":           round(biz_h,  1),
        "flood_risk":          round(biz_f,  1),
        "water_risk":          round(biz_w,  1),
        "composite_risk":      round(comp,   1),
        "revenue_at_risk_pct": round(rev_risk,   1),
        "financial_impact_cr": round(fin_impact, 3),
        "primary_risk":        primary,
        "risk_level":          level,
        "shap_explanation":    shap_dict,
        "data_source":         "NASA POWER 1984-2023 | IPCC AR6 | EM-DAT",
        "model_version":       "2.0.0",
    }


# ── endpoints ───────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "system":      "ClimaRisk × ClimaShock",
        "version":     "2.0.0",
        "description": "Pakistan Climate Risk Intelligence Platform",
        "endpoints": {
            "risk_assessment": "POST /api/v1/risk-score",
            "cities":          "GET  /api/v1/cities",
            "industries":      "GET  /api/v1/industries",
            "health":          "GET  /api/v1/health",
            "docs":            "GET  /docs",
        }
    }


@app.get("/api/v1/health")
def health():
    return {
        "status":         "ok",
        "model_loaded":   True,
        "shap_available": SHAP_AVAILABLE,
        "cities":         len(CITY_RISK),
        "industries":     len(INDUSTRY_PROFILES),
    }


@app.get("/api/v1/cities")
def get_cities():
    return {
        "cities": [
            {
                "name":       city,
                "heat_risk":  scores["heat"],
                "flood_risk": scores["flood"],
                "water_risk": scores["water"],
            }
            for city, scores in CITY_RISK.items()
        ],
        "source": "NASA POWER 1984-2023"
    }


@app.get("/api/v1/industries")
def get_industries():
    return {
        "industries": list(INDUSTRY_PROFILES.keys()),
        "source":     "IPCC AR6 WG2 + World Bank"
    }


@app.post("/api/v1/risk-score", response_model=RiskResponse)
def get_risk_score(request: RiskRequest):
    try:
        result = compute_risk(
            request.city,
            request.industry,
            request.asset_value_cr,
            request.employees,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))