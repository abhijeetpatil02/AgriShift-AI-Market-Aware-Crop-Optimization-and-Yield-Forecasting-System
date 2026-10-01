# 🌱 AgriShift: AI Market-Aware Crop Optimization & Yield Forecasting System

> An end-to-end Transition-Aware Crop Portfolio Optimization System that predicts crop yields and market prices, models switching friction and volatility risk, simulates Cobweb market feedback, and generates optimal multi-crop allocations through mixed-integer linear programming (MILP).

---

## 📌 Architecture Overview

```
                      FARMER
                         │
                         ▼
                ┌─────────────────┐
                │   WEB PORTAL    │
                │ Location        │
                │ Farm Area (ha)  │
                │ Soil N-P-K & pH │
                │ Previous Crop   │
                │ Risk Tolerance  │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ FASTAPI BACKEND │
                └────────┬────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
   ┌───────────┐   ┌───────────┐   ┌───────────┐
   │ YIELD ML  │   │   PRICE   │   │  DATA &   │
   │  ENGINE   │   │ FORECASTER│   │ SQLITE DB │
   │ (RF/XGB)  │   │ (Horizons)│   │(Baselines)│
   └─────┬─────┘   └─────┬─────┘   └───────────┘
         │               │
         └───────┬───────┘
                 ▼
        ┌─────────────────┐
        │  PROFIT ENGINE  │
        └────────┬────────┘
                 ▼
        ┌─────────────────┐
        │ SWITCHING COST  │
        │ Transition Mat. │
        └────────┬────────┘
                 ▼
        ┌─────────────────┐
        │  COBWEB FEEDBACK│
        │ Price Elasticity│
        └────────┬────────┘
                 ▼
        ┌─────────────────┐
        │ MILP OPTIMIZER  │
        │ (SciPy HiGHS)   │
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │ RECOMMENDATION  │
        │ Crop Portfolio  │
        │ Expected Profit │
        │ Naive Plan Comp │
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │ SIMPLE DASHBOARD│
        └─────────────────┘
```

---

## 🚀 Key Modules Implemented

### 1. Data Pipeline (`ml/data_pipeline.py`)
- Standardizes and joins historical datasets across **10 States**, **40 Districts**, **10 Major Indian Crops**, and **9 Years (2015–2023)**.
- Merges soil chemistry ($N, P, K, pH, OC, EC$), seasonal climate ($Temperature, Rainfall, Humidity, Soil Moisture$), production costs (Cost $A2+FL$, Cost $C2$, Fertilizer, Labor), and weekly mandi prices with 100% inner join match rate.

### 2. Yield Prediction Engine (`ml/yield_prediction.py`)
- Models: **Ridge Regression**, **Random Forest Regressor**, and **XGBoost Regressor**.
- Evaluated using **Walk-Forward Out-of-Time Splits** (Train: 2015–2021 | Test: 2022–2023) to eliminate data leakage.
- **Performance**:
  - **Random Forest**: $R^2 = 0.9712$ | $\text{RMSE} = 3.09 \text{ t/ha}$ | $\text{MAE} = 0.99 \text{ t/ha}$ (Best Model)
  - **Ridge Baseline**: $R^2 = 0.9685$ | $\text{RMSE} = 3.23 \text{ t/ha}$
  - **XGBoost**: $R^2 = 0.9683$ | $\text{RMSE} = 3.24 \text{ t/ha}$
- Generates top feature importances (Sugarcane seasonality, Nitrogen, Phosphorus, EC, Potassium, pH).

### 3. Market Price Forecasting (`ml/price_prediction.py`)
- Produces multi-horizon price forecasts:
  - **Next-Month**, **3-Month**, **6-Month**, and **12-Month** mandi forecasts.
  - Calculates crop-specific historical volatility coefficients ($\sigma / \mu$) used in the optimization risk penalty term.

### 4. Switching Cost Matrix (`optimizer/switching_cost.py`)
- Accounts for the financial and operational friction of crop transition (land preparation, seed changeover, specialized equipment adjustment).
- Full $10 \times 10$ transition matrix loaded from `data/processed/crop_transition_matrix.csv`.
- Transition to the same crop has **₹0/ha** switching cost; transitioning from cereals to perennials (e.g., Rice to Sugarcane) incorporates land preparation and setts costs (~₹24,000/ha).

### 5. Cobweb Market Feedback Simulation (`optimizer/cobweb.py`)
- Simulates price degradation under farmer adoption scenarios ($0\%, 10\%, 30\%, 60\%, 100\%$).
- Applies agricultural price elasticity of demand ($\epsilon_d = -0.55$):
  $$\frac{\Delta P}{P} = \frac{1}{\epsilon_d} \times \frac{\Delta S}{S_{\text{baseline}}}$$
- Evaluates supply gluts and re-optimizes portfolios to protect farmers from price collapse.

### 6. Portfolio Optimization Engine (`optimizer/crop_optimizer.py`)
- Mixed-Integer Linear Programming (MILP via SciPy HiGHS):
  $$\max \sum_{i=1}^N \left[ x_i \cdot (\text{Yield}_i \times P_i - \text{CultivationCost}_i - \text{SwitchCost}_i) - \lambda \cdot x_i \cdot \text{RiskPenalty}_i \right]$$
  $$\text{Subject to: } \sum x_i \le \text{FarmArea}, \quad x_i \ge A_{\min} y_i, \quad x_i \le \text{FarmArea} \cdot y_i, \quad \sum y_i \le K$$
- Includes a **Strategy Comparison** comparing AgriShift's transition-aware portfolio against a traditional naive single-crop allocation.

### 7. Clean, Simple Web UI (`frontend/static/`)
- Clean, responsive, and intuitive interface with 5 tabs:
  1. 🌾 **Crop Recommendation**: Clean farm details form + auto-filled district defaults + instant visual portfolio results.
  2. 📈 **Yield & Price Forecast**: Single crop predictor with 1M, 3M, 6M, 12M horizons and trend graphs.
  3. 🕸️ **Market Feedback (Cobweb)**: Interactive adoption slider, supply shift vs. price impact chart.
  4. 🔬 **Model Evaluation**: Walk-forward metrics table and yield driver bar chart.
  5. 📜 **Saved Plans**: Audit log of previous recommendations stored in SQLite.

---

## 🛠️ How to Run Locally

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.14 on Windows)
- Required packages:
  ```bash
  pip install fastapi uvicorn scipy scikit-learn xgboost pandas numpy
  ```

### 2. Run Data Pipeline & Train ML Models (Optional, already pre-trained)
```bash
python ml/data_pipeline.py
python ml/yield_prediction.py
python ml/price_prediction.py
python backend/database.py
```

### 3. Start the Web Application
```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```
Open your browser at: **`http://127.0.0.1:8000`**

---

## 🧪 Running Automated Tests

Run the full system integration test suite:
```bash
python tests/test_system.py
```
*Result: 7/7 tests passed.*

---

## 📂 Project Structure

```
crop-optimization-system/
│
├── DataSet/                               # Raw source CSV datasets
│   ├── crop_yield_sample_dataset.csv
│   ├── soil_health_sample_dataset.csv
│   ├── climate_seasonal_sample_dataset.csv
│   ├── cost_of_cultivation_sample_dataset.csv
│   ├── crop_transition_cost_matrix.csv
│   └── market_price_supply_sample_dataset.csv
│
├── data/processed/                        # Preprocessed & merged datasets
│   ├── master_dataset.csv
│   ├── crop_price_monthly.csv
│   ├── crop_price_summary.csv
│   └── crop_transition_matrix.csv
│
├── ml/                                    # Machine Learning modules
│   ├── data_pipeline.py                   # Data merge & preprocessing
│   ├── yield_prediction.py                # Ridge, RF, XGBoost training & inference
│   └── price_prediction.py                # Time series forecasting & volatility
│
├── optimizer/                             # Decision and simulation layer
│   ├── switching_cost.py                  # Transition matrix manager
│   ├── cobweb.py                          # Cobweb market feedback simulation
│   └── crop_optimizer.py                  # SciPy HiGHS MILP optimizer
│
├── models/                                # Trained model artifacts
│   ├── yield_model.pkl                    # Best model pipeline (Random Forest)
│   ├── yield_metadata.json                # Walk-forward validation metrics & features
│   ├── price_model.pkl                    # Crop price profiles
│   └── price_metadata.json                # Price trend & seasonal indices
│
├── backend/                               # API Layer
│   ├── main.py                            # FastAPI application server
│   ├── database.py                        # SQLite layer for district defaults & logs
│   └── agrishift.db                       # SQLite database
│
├── frontend/static/                       # Clean, simple web interface
│   ├── index.html                         # Single-page application
│   ├── style.css                          # Modern, clean CSS
│   └── app.js                             # Interactive controller with Chart.js
│
├── tests/                                 # Unit & Integration tests
│   └── test_system.py                     # Full test suite
│
└── README.md
```

---

## 📜 License
Academic Research / Open Access.
