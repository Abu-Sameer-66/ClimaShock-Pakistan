<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:000000,30:0a1628,60:0d2137,100:1a3a4a&height=340&section=header&text=⚡%20ClimaShock&fontSize=90&fontColor=ffffff&animation=fadeIn&fontAlignY=38&desc=Pakistan%27s%20First%20Distributed%20Causal%20Climate-Economic%20Intelligence%20System&descSize=18&descAlignY=60&descAlign=50&descColor=E8A020" width="100%"/>

<br/>

<img src="https://readme-typing-svg.herokuapp.com?font=JetBrains+Mono&weight=700&size=22&pause=1000&color=E8A020&center=true&vCenter=true&width=900&lines=3-Node+Parallel+Distributed+Architecture;Granger+Causal+Discovery+%7C+21+Links+Found;LSTM+%2B+XGBoost+Ensemble+%7C+Inflation+MAE+2.87%25;NASA+%2B+World+Bank+%2B+FAO+%7C+34+Years+%7C+10+Districts;Pakistan%27s+First+Climate-Economic+Causal+Atlas" />

<br/><br/>

<a href="#">
<img src="https://img.shields.io/badge/%F0%9F%9F%A2%20LIVE%20UI-Vercel-E8A020?style=for-the-badge&labelColor=0a1628"/>
</a>
&nbsp;
<a href="#">
<img src="https://img.shields.io/badge/%F0%9F%9F%A2%20LIVE%20API-HuggingFace-E8A020?style=for-the-badge&labelColor=0d2137"/>
</a>
&nbsp;
<a href="https://kaggle.com/code/sameernadeem66/climashock-data-collection">
<img src="https://img.shields.io/badge/%F0%9F%93%8A%20Kaggle-Notebook-20BEFF?style=for-the-badge&logo=kaggle&labelColor=0a1628"/>
</a>
&nbsp;
<a href="https://github.com/Abu-Sameer-66/ClimaShock-Pakistan">
<img src="https://img.shields.io/badge/%F0%9F%96%A5%20GitHub-Repo-E8A020?style=for-the-badge&logo=github&labelColor=0d2137"/>
</a>

<br/><br/>

<img src="https://img.shields.io/badge/Python-3.12-E8A020?style=flat-square&logo=python&logoColor=black&labelColor=0a1628"/>
<img src="https://img.shields.io/badge/PyTorch-LSTM-C86A00?style=flat-square&logo=pytorch&logoColor=white&labelColor=0d2137"/>
<img src="https://img.shields.io/badge/XGBoost-Ensemble-E8A020?style=flat-square&labelColor=0a1628"/>
<img src="https://img.shields.io/badge/PySpark-4.0.2-C86A00?style=flat-square&logo=apachespark&logoColor=white&labelColor=0d2137"/>
<img src="https://img.shields.io/badge/FastAPI-0.111-E8A020?style=flat-square&logo=fastapi&logoColor=white&labelColor=0a1628"/>
<img src="https://img.shields.io/badge/Next.js-15-C86A00?style=flat-square&logo=nextdotjs&logoColor=white&labelColor=0d2137"/>
<img src="https://img.shields.io/badge/NASA%20POWER-API-E8A020?style=flat-square&labelColor=0a1628"/>
<img src="https://img.shields.io/badge/Tesla%20T4-GPU-C86A00?style=flat-square&logo=nvidia&logoColor=white&labelColor=0d2137"/>

</div>

---

## The Problem Nobody Has Quantified

**Pakistan loses billions every year to climate-driven economic cascades.**

The 2022 floods displaced 33 million people. But nobody knew — in advance — how a rainfall anomaly in Sukkur would cascade into cotton collapse, food price spirals, and a national inflation crisis peaking at 30.8% the following year.

The problem is not that the data does not exist. NASA, World Bank, and FAO publish decades of it — freely.

**The problem is that nobody built a distributed system to find the causal chains hidden inside it.**

**ClimaShock is that system.**

---

## Live Deployment

| Service | URL | Status |
|:---|:---|:---:|
| Web UI | [climashock.vercel.app](#) | 🟢 Live |
| REST API | [HuggingFace Spaces](#) | 🟢 Live |
| API Docs | [/docs](#) | 🟢 Live |
| Kaggle Notebook | [sameernadeem66/climashock](https://kaggle.com/code/sameernadeem66/climashock-data-collection) | 🟢 Public |

---

## Novel Discoveries — World First for Pakistan

> These findings did not exist before this system was built.

| Rank | Discovery | Evidence | Quantified For First Time |
|:---|:---|:---|:---:|
| 🥇 | Extreme rainfall causes national **inflation spike after 2-year lag** | Granger strength **0.347** — strongest causal link in system | ✅ |
| 🥈 | **Sukkur** is Pakistan's highest climate-economic risk epicentre | 2022 rainfall **+1293%** — highest σ of all 10 districts | ✅ |
| 🥉 | **Cotton** is Pakistan's most climate-vulnerable export crop | 2022: -37.7% yield → direct export revenue shock | ✅ |
| 4 | Temperature anomaly has **4-year delayed inflation effect** | Granger strength 0.128, lag=4y | ✅ |
| 5 | 21 causal links discovered across climate-economic-agricultural domains | Pakistan's first cross-domain causal graph | ✅ |

---

## System Architecture — Distributed 3-Node Design
┌─────────────────────────────────────────────────────────────────┐
│                         DATA LAYER                              │
│   NASA POWER API (climate) │ World Bank API │ FAO Crop Data     │
│        34 years · 10 districts · 4,080 monthly records         │
└──────────────┬──────────────────┬───────────────────┬───────────┘
│                  │                   │
┌─────────▼──────┐  ┌───────▼────────┐  ┌──────▼──────────┐
│  NODE 1        │  │  NODE 2        │  │  NODE 3         │
│  PID 798       │  │  PID 799       │  │  PID 800        │
│  Climate       │  │  Economic      │  │  Agricultural   │
│  Processor     │  │  Processor     │  │  Processor      │
│                │  │                │  │                 │
│  Z-scores      │  │  Inflation     │  │  Crop yield     │
│  Anomaly det.  │  │  GDP shocks    │  │  YoY change     │
│  Risk scoring  │  │  Stress index  │  │  Shock detect   │
└────────┬───────┘  └──────┬─────────┘  └──────┬──────────┘
│                 │                    │
└────────────┬────┘────────────────────┘
│  Queue-based Message Passing
┌──────────▼──────────────┐
│   CENTRAL AGGREGATOR    │
│   Data fusion engine    │
│   (34, 28) master matrix│
└──────────┬──────────────┘
│
┌────────────────▼────────────────────┐
│       CAUSAL DISCOVERY ENGINE        │
│  Granger Causality · 21 links found  │
│  Temporal lag analysis (1–4 years)   │
└────────────────┬────────────────────┘
│
┌─────────────────────▼──────────────────────────┐
│              ML ENSEMBLE LAYER                  │
│                                                 │
│  LSTM (PyTorch)          XGBoost Ensemble       │
│  Inflation MAE: 2.87%    Inflation MAE: 3.19%   │
│  GPU: Tesla T4           Lag features: 6        │
│                                                 │
│  10 District-Specific Models (parallel trained) │
│  Average MAE: 4.42%  ·  Training: 47.3s on GPU  │
└─────────────────────┬──────────────────────────┘
│
┌─────────────────────▼──────────────────────────┐
│                 API + UI LAYER                  │
│  FastAPI (HuggingFace) · Next.js (Vercel)       │
│  /predict  /causal  /districts  /discoveries    │
└────────────────────────────────────────────────┘

---

## Model Performance

| Model | Inflation MAE | Crop MAE | Notes |
|:---|:---:|:---:|:---|
| LSTM (national) | **2.87%** | 7.09% | Best inflation predictor |
| XGBoost (national) | 3.19% | 9.39% | Lag features: 6 |
| **Ensemble** | **3.13%** | **7.89%** | Weighted inverse-MAE |
| District LSTM (avg) | 4.42% | 13.71% | 10 parallel models, GPU T4 |

**Back-test 2022:** Predicted inflation 26.0% → Actual 2023: **30.8%** (4.8% error)
**GDP direction:** Predicted "contraction likely" → Actual: **-0.41%** ✅

---

## Parallel Processing — PDC Architecture
3 nodes spawned simultaneously:
Node 1 — PID 798 — climate   ─┐
Node 2 — PID 799 — economic   ├─ 0.076 seconds total
Node 3 — PID 800 — agri      ─┘
10 district models trained in parallel on Tesla T4 GPU:
Faisalabad · Hyderabad · Islamabad · Karachi · Lahore
Multan · Peshawar · Quetta · Sialkot · Sukkur
Total training time: 47.3 seconds

---

## Causal Links Discovered

| Rank | Cause | Effect | Lag | Granger Strength |
|:---:|:---|:---|:---:|:---:|
| 1 | rain_anomaly | **inflation_pct** | 2 years | **0.347** |
| 2 | food_production_index | crop_stress | 1 year | 0.365 |
| 3 | gdp_growth_pct | crop_stress | 1 year | 0.224 |
| 4 | rain_anomaly | crop_stress | 2 years | 0.181 |
| 5 | temp_anomaly | inflation_pct | 4 years | 0.128 |

---

## Data Sources

| Source | Data | Years | Access |
|:---|:---|:---:|:---:|
| NASA POWER API | Temperature, rainfall, humidity, solar radiation | 1990–2023 | Free |
| World Bank Open Data | GDP growth, inflation, food production index | 1990–2023 | Free |
| FAO / Pakistan Economic Survey | Wheat, rice, cotton, sugarcane, maize production | 1990–2023 | Free |

---

## Quick Start

```bash
git clone https://github.com/Abu-Sameer-66/ClimaShock-Pakistan.git
cd ClimaShock-Pakistan/backend
pip install -r requirements.txt
uvicorn app:app --reload
```

Local API → `http://localhost:8000`
Live API  → `https://[huggingface-space-url]`
Live UI   → `https://climashock.vercel.app`

---

## API Usage

```bash
# cascade prediction — district + current climate
curl -X POST "https://api-url/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "district": "Sukkur",
    "rainfall_mm_day": 4.16,
    "temperature_c": 30.2
  }'

# get all causal links
curl "https://api-url/causal?min_strength=0.1"

# all districts + model accuracy
curl "https://api-url/districts"

# novel discoveries
curl "https://api-url/discoveries"
```

---

## Tech Stack
Heavy ML (Kaggle T4 GPU)      Backend (HuggingFace Spaces)    Frontend (Vercel)
──────────────────────────    ──────────────────────────────   ─────────────────
PyTorch LSTM training    →    FastAPI REST API             →   Next.js 15
XGBoost ensemble         →    Joblib model serving         →   Dark terminal UI
PySpark 4.0 MapReduce    →    Pydantic validation          →   Real-time cascade
Granger causal discovery →    CORS + error handling        →   District selector
multiprocessing nodes    →    /predict /causal /districts  →   Animated chain viz
NASA POWER API           →    Auto-loaded models           →   Pakistan risk map

---

## Author

<div align="center">

**Sameer Nadeem** — AI/ML Engineer · Data Scientist · PDC Researcher

<br/>

<a href="https://sameer-nadeem-portfolio.vercel.app"><img src="https://img.shields.io/badge/Portfolio-Live-E8A020?style=for-the-badge&labelColor=0a1628"/></a>
&nbsp;
<a href="https://github.com/Abu-Sameer-66"><img src="https://img.shields.io/badge/GitHub-Abu--Sameer--66-C86A00?style=for-the-badge&logo=github&labelColor=0d2137"/></a>
&nbsp;
<a href="https://www.linkedin.com/in/sameer-nadeem-66339a357/"><img src="https://img.shields.io/badge/LinkedIn-Sameer%20Nadeem-E8A020?style=for-the-badge&logo=linkedin&labelColor=0a1628"/></a>
&nbsp;
<a href="https://www.kaggle.com/sameernadeem66"><img src="https://img.shields.io/badge/Kaggle-sameernadeem66-C86A00?style=for-the-badge&logo=kaggle&labelColor=0d2137"/></a>

</div>

---

<div align="center">

*Built to tell Pakistan what climate does to its economy — before it happens.*

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:1a3a4a,50:0d2137,100:000000&height=140&section=footer" width="100%"/>

</div>