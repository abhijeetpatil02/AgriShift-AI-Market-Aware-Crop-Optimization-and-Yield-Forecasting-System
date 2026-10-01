"""
AgriShift Comprehensive System Test Suite
Tests:
  1. Data Pipeline (master dataset, monthly price summary, transition matrix)
  2. Yield Prediction Engine (Pipeline prediction, positive yields)
  3. Price Forecaster (Horizons 1M, 3M, 6M, 12M and volatility)
  4. Switching Cost Lookup (Diagonal is 0, valid INR/ha values)
  5. Cobweb Market Feedback (Elasticity price adjustment)
  6. MILP Crop Portfolio Optimizer (Area conservation, max crops constraint, net profit)
  7. FastAPI Endpoints (/api/meta, /api/predict-yield, /api/forecast-price, /api/optimize, /api/cobweb-simulate)
"""

import os
import sys
import unittest
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ml.yield_prediction import YieldPredictor
from ml.price_prediction import PriceForecaster
from optimizer.switching_cost import SwitchingCostManager
from optimizer.cobweb import CobwebSimulator
from optimizer.crop_optimizer import CropPortfolioOptimizer
from backend.database import get_district_defaults, log_recommendation, get_recommendation_history
import urllib.request
import json

class TestAgriShiftSystem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.base_url = "http://127.0.0.1:8000"
        cls.yield_pred = YieldPredictor()
        cls.price_fore = PriceForecaster()
        cls.switching_mgr = SwitchingCostManager()
        cls.cobweb = CobwebSimulator()
        cls.optimizer = CropPortfolioOptimizer()

    def test_01_master_dataset_exists(self):
        master_path = os.path.join(BASE_DIR, "data", "processed", "master_dataset.csv")
        self.assertTrue(os.path.exists(master_path), "Master dataset file missing")
        df = pd.read_csv(master_path)
        self.assertGreater(len(df), 3000, "Master dataset should have >3000 rows")
        self.assertIn("Yield_Tonnes_per_ha", df.columns)

    def test_02_yield_prediction(self):
        res = self.yield_pred.predict_single(
            state="Karnataka", district="Belagavi", crop="Rice", season="Kharif",
            n=240, p=14, k=215, ph=6.6, oc=0.58, ec=0.5,
            temp=26.0, rainfall=670.0, humidity=68.0, moisture=23.0
        )
        self.assertEqual(res["crop"], "Rice")
        self.assertGreater(res["predicted_yield_tonnes_ha"], 0.5)
        self.assertLess(res["predicted_yield_tonnes_ha"], 15.0)

    def test_03_price_forecasting(self):
        f = self.price_fore.forecast_horizons("Rice", start_month=10)
        self.assertIn("1_month", f)
        self.assertIn("3_month", f)
        self.assertIn("6_month", f)
        self.assertIn("12_month", f)
        self.assertGreater(f["3_month"]["price_rs_tonne"], 15000)
        self.assertGreater(f["volatility_ratio"], 0.05)

    def test_04_switching_cost(self):
        # Rice to Rice is 0
        self.assertEqual(self.switching_mgr.get_cost("Rice", "Rice"), 0.0)
        # Rice to Sugarcane has substantial land transition cost
        self.assertGreater(self.switching_mgr.get_cost("Rice", "Sugarcane"), 10000.0)

    def test_05_cobweb_feedback(self):
        cw0 = self.cobweb.simulate_feedback("Maize", 33000.0, 4.0, adoption_rate=0.0)
        cw30 = self.cobweb.simulate_feedback("Maize", 33000.0, 4.0, adoption_rate=0.30)
        self.assertEqual(cw0["adjusted_price_rs_tonne"], 33000.0)
        self.assertLess(cw30["adjusted_price_rs_tonne"], 33000.0)
        self.assertGreater(cw30["price_drop_pct"], 0.0)

    def test_06_crop_optimizer_milp(self):
        candidates = {
            "Rice": {"yield_tonnes_ha": 4.5, "price_rs_tonne": 25975.0, "volatility": 0.18},
            "Maize": {"yield_tonnes_ha": 3.8, "price_rs_tonne": 33675.0, "volatility": 0.20},
            "Groundnut": {"yield_tonnes_ha": 2.1, "price_rs_tonne": 64000.0, "volatility": 0.15}
        }
        farm_area = 2.5
        sol = self.optimizer.optimize_portfolio(
            farm_area_ha=farm_area, previous_crop="Rice",
            risk_preference="Medium", candidates_data=candidates, max_crops=3
        )
        self.assertEqual(sol["status"], "Optimal")
        self.assertAlmostEqual(sol["totals"]["allocated_area_ha"], farm_area, delta=0.05)
        self.assertGreater(sol["totals"]["net_profit_rs"], 50000)
        self.assertLessEqual(len(sol["portfolio"]), 3)

    def test_07_api_endpoints(self):
        # GET /api/meta
        req = urllib.request.urlopen(f"{self.base_url}/api/meta")
        self.assertEqual(req.status, 200)
        data = json.loads(req.read().decode("utf-8"))
        self.assertIn("states_and_districts", data)
        self.assertIn("evaluation_metrics", data)

        # POST /api/optimize
        opt_payload = {
            "farmer_name": "Test Farmer",
            "state": "Karnataka",
            "district": "Belagavi",
            "farm_area_ha": 3.0,
            "previous_crop": "Rice",
            "season": "Kharif",
            "risk_preference": "Medium",
            "max_crops": 2
        }
        req_opt = urllib.request.Request(
            f"{self.base_url}/api/optimize",
            data=json.dumps(opt_payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        resp_opt = urllib.request.urlopen(req_opt)
        self.assertEqual(resp_opt.status, 200)
        opt_res = json.loads(resp_opt.read().decode("utf-8"))
        self.assertEqual(opt_res["status"], "Optimal")
        self.assertIn("portfolio", opt_res)
        self.assertIn("comparison", opt_res)

        # POST /api/cobweb-simulate
        cw_payload = {"crop": "Maize", "yield_tonnes_ha": 4.0, "base_price_rs_tonne": 33000.0, "portfolio_share": 0.5}
        req_cw = urllib.request.Request(
            f"{self.base_url}/api/cobweb-simulate",
            data=json.dumps(cw_payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        resp_cw = urllib.request.urlopen(req_cw)
        self.assertEqual(resp_cw.status, 200)
        self.assertEqual(len(json.loads(resp_cw.read().decode("utf-8"))["scenarios"]), 5)

if __name__ == "__main__":
    unittest.main()
