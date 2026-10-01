"""
AgriShift FastAPI Backend Server
Serves ML yield predictions, price forecasting, switching cost matrices,
Cobweb market feedback simulation, and MILP crop portfolio optimization.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import json
import pandas as pd

from ml.yield_prediction import YieldPredictor
from ml.price_prediction import PriceForecaster
from optimizer.switching_cost import SwitchingCostManager
from optimizer.cobweb import CobwebSimulator
from optimizer.crop_optimizer import CropPortfolioOptimizer, DEFAULT_CULTIVATION_COSTS
from backend.database import init_db, get_district_defaults, log_recommendation, get_recommendation_history

app = FastAPI(
    title="AgriShift API",
    description="AI Market-Aware Crop Optimization & Yield Forecasting System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize singletons
init_db()
yield_predictor = YieldPredictor()
price_forecaster = PriceForecaster()
switching_manager = SwitchingCostManager()
cobweb_sim = CobwebSimulator()
portfolio_optimizer = CropPortfolioOptimizer()

# Load state-to-district mappings and district-crop directory
PROCESSED_PATH = os.path.join(BASE_DIR, "data", "processed", "master_dataset.csv")
STATE_DISTRICT_MAP = {}
if os.path.exists(PROCESSED_PATH):
    df_meta = pd.read_csv(PROCESSED_PATH)
    for state in sorted(df_meta["State"].unique()):
        districts = sorted(df_meta[df_meta["State"] == state]["District"].unique())
        STATE_DISTRICT_MAP[state] = districts

DISTRICT_CROPS_LOOKUP = {}
lookup_path = os.path.join(BASE_DIR, "data", "processed", "district_crops_lookup.json")
if os.path.exists(lookup_path):
    with open(lookup_path, "r") as f:
        DISTRICT_CROPS_LOOKUP = json.load(f)

# ----------------- Pydantic Models -----------------

class YieldPredictRequest(BaseModel):
    state: str = "Karnataka"
    district: str = "Belagavi"
    crop: str = "Rice"
    season: str = "Kharif"
    nitrogen: float = 240.0
    phosphorus: float = 14.0
    potassium: float = 215.0
    ph: float = 6.6
    organic_carbon: float = 0.58
    ec: float = 0.5
    avg_temp: float = 26.0
    rainfall: float = 670.0
    humidity: float = 68.0
    soil_moisture: float = 23.0

class PriceForecastRequest(BaseModel):
    crop: str = "Rice"
    start_month: int = 10

class OptimizeRequest(BaseModel):
    farmer_name: Optional[str] = "Farmer"
    state: str = "Karnataka"
    district: str = "Belagavi"
    farm_area_ha: float = Field(2.5, gt=0, le=100)
    previous_crop: str = "Rice"
    season: str = "Kharif"
    risk_preference: str = "Medium"
    adoption_rate_pct: float = Field(0.0, ge=0.0, le=100.0)
    max_crops: int = Field(3, ge=1, le=5)
    # Soil & Climate overrides (optional, will use district defaults if None)
    nitrogen: Optional[float] = None
    phosphorus: Optional[float] = None
    potassium: Optional[float] = None
    ph: Optional[float] = None
    organic_carbon: Optional[float] = None
    ec: Optional[float] = None
    avg_temp: Optional[float] = None
    rainfall: Optional[float] = None
    humidity: Optional[float] = None
    soil_moisture: Optional[float] = None

class CobwebRequest(BaseModel):
    crop: str = "Maize"
    yield_tonnes_ha: float = 4.0
    base_price_rs_tonne: float = 33675.0
    portfolio_share: float = 0.5

# ----------------- API Endpoints -----------------

@app.get("/api/meta")
def get_metadata():
    """Returns application options, state-district hierarchy, crops, district crops directory, and evaluation metrics."""
    return {
        "states_and_districts": STATE_DISTRICT_MAP,
        "crops": yield_predictor.metadata.get("crops", []),
        "district_crops": DISTRICT_CROPS_LOOKUP,
        "seasons": ["Kharif", "Rabi", "Whole Year"],
        "risk_levels": ["Low", "Medium", "High"],
        "default_cultivation_costs": DEFAULT_CULTIVATION_COSTS,
        "evaluation_metrics": yield_predictor.metadata.get("evaluation_metrics", {}),
        "best_yield_model": yield_predictor.metadata.get("best_model", "Random_Forest"),
        "top_features": yield_predictor.metadata.get("top_feature_importances", {})
    }

@app.get("/api/district-defaults")
def get_defaults(state: str = Query(...), district: str = Query(...)):
    """Returns average soil and climate values for a selected district."""
    defaults = get_district_defaults(state, district)
    return defaults

@app.get("/api/district-crops")
def get_district_crops(state: str = Query(...), district: str = Query(...)):
    """Returns all crops grown in the specified district with historical yields, area, and seasons."""
    crops_info = DISTRICT_CROPS_LOOKUP.get(state, {}).get(district, [])
    return {
        "state": state,
        "district": district,
        "crops": crops_info
    }

@app.get("/api/all-districts-crops")
def get_all_districts_crops():
    """Returns complete directory of all 40 districts and all crops grown across all 10 states."""
    return DISTRICT_CROPS_LOOKUP

@app.post("/api/predict-yield")
def predict_yield(req: YieldPredictRequest):
    """Predicts expected yield in tonnes/ha and kg/ha for a specific crop."""
    try:
        pred = yield_predictor.predict_single(
            req.state, req.district, req.crop, req.season,
            req.nitrogen, req.phosphorus, req.potassium, req.ph,
            req.organic_carbon, req.ec, req.avg_temp,
            req.rainfall, req.humidity, req.soil_moisture
        )
        return pred
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/forecast-price")
def forecast_price(req: PriceForecastRequest):
    """Returns price horizons and volatility for a commodity."""
    try:
        forecast = price_forecaster.forecast_horizons(req.crop, req.start_month)
        return forecast
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/optimize")
def optimize_portfolio_endpoint(req: OptimizeRequest):
    """
    Executes the full pipeline:
      1. Prepopulates / validates soil & weather
      2. Predicts yields across candidate crops
      3. Gathers market prices, volatility, switching costs
      4. Solves MILP portfolio optimization
      5. Simulates Cobweb market feedback if adoption > 0
      6. Compares with naive mono-crop baseline
      7. Logs to SQLite database
    """
    # 1. Fill missing parameters from district defaults
    defaults = get_district_defaults(req.state, req.district)
    n = req.nitrogen if req.nitrogen is not None else defaults["nitrogen"]
    p = req.phosphorus if req.phosphorus is not None else defaults["phosphorus"]
    k = req.potassium if req.potassium is not None else defaults["potassium"]
    ph = req.ph if req.ph is not None else defaults["ph"]
    oc = req.organic_carbon if req.organic_carbon is not None else defaults["organic_carbon"]
    ec = req.ec if req.ec is not None else defaults["ec"]
    temp = req.avg_temp if req.avg_temp is not None else defaults["avg_temp"]
    rain = req.rainfall if req.rainfall is not None else defaults["rainfall"]
    hum = req.humidity if req.humidity is not None else defaults["humidity"]
    moist = req.soil_moisture if req.soil_moisture is not None else defaults["soil_moisture"]

    # 2. Predict yields for all candidate crops
    candidate_crops = yield_predictor.metadata.get("crops", [])
    yield_results = yield_predictor.predict_all_crops(
        req.state, req.district, req.season,
        n, p, k, ph, oc, ec, temp, rain, hum, moist,
        crops=candidate_crops
    )

    # 3. Assemble candidates data for optimizer
    all_prices = price_forecaster.get_all_crop_prices()
    candidates_data = {}
    for crop, yres in yield_results.items():
        price_info = all_prices.get(crop, {"price_rs_tonne": 28000.0, "volatility": 0.18})
        candidates_data[crop] = {
            "yield_tonnes_ha": yres["predicted_yield_tonnes_ha"],
            "yield_kg_ha": yres["predicted_yield_kg_ha"],
            "price_rs_tonne": price_info["price_rs_tonne"],
            "volatility": price_info["volatility"],
            "cultivation_cost_per_ha": DEFAULT_CULTIVATION_COSTS.get(crop, 35000.0)
        }

    # 4. Run portfolio optimization
    adoption_ratio = req.adoption_rate_pct / 100.0
    solution = portfolio_optimizer.optimize_portfolio(
        farm_area_ha=req.farm_area_ha,
        previous_crop=req.previous_crop,
        risk_preference=req.risk_preference,
        candidates_data=candidates_data,
        max_crops=req.max_crops,
        adoption_rate=adoption_ratio
    )

    # 5. Log recommendation to database
    try:
        log_id = log_recommendation(
            farmer_name=req.farmer_name,
            state=req.state,
            district=req.district,
            farm_area=req.farm_area_ha,
            previous_crop=req.previous_crop,
            risk_pref=req.risk_preference,
            adoption_rate=req.adoption_rate_pct,
            portfolio=solution["portfolio"],
            net_profit=solution["totals"]["net_profit_rs"],
            switch_cost=solution["totals"]["switching_cost_rs"],
            full_data=solution
        )
        solution["log_id"] = log_id
    except Exception as e:
        print("Log error:", e)

    solution["environmental_inputs"] = {
        "nitrogen": n, "phosphorus": p, "potassium": k, "ph": ph,
        "organic_carbon": oc, "ec": ec, "avg_temp": temp,
        "rainfall": rain, "humidity": hum, "soil_moisture": moist
    }

    return solution

@app.post("/api/cobweb-simulate")
def cobweb_simulate(req: CobwebRequest):
    """Simulates market feedback across 0%, 10%, 30%, 60%, 100% adoption scenarios."""
    scenarios = cobweb_sim.simulate_all_scenarios(
        req.crop, req.base_price_rs_tonne, req.yield_tonnes_ha, req.portfolio_share
    )
    return {
        "crop": req.crop,
        "scenarios": scenarios
    }

@app.get("/api/recommendation-history")
def recommendation_history(limit: int = 15):
    """Fetches recent recommendation logs."""
    return get_recommendation_history(limit)

@app.get("/api/transition-matrix")
def transition_matrix(from_crop: Optional[str] = None):
    """Returns switching cost lookup or pivot table."""
    if from_crop:
        return switching_manager.get_all_transitions_for(from_crop)
    return switching_manager.get_matrix_pivot()

# Mount frontend static directory
STATIC_DIR = os.path.join(BASE_DIR, "frontend", "static")
if os.path.exists(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=False)
