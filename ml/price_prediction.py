"""
Price Forecasting Engine
Generates time-series price forecasts (Next-month, 3-month, 6-month, 12-month)
and computes historical price volatility / variance for the optimization risk term.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

class PriceForecaster:
    """Forecaster for crop mandi prices and volatility parameters."""
    def __init__(self):
        self.summary_df = pd.read_csv(os.path.join(PROCESSED_DIR, "crop_price_summary.csv"))
        self.monthly_df = pd.read_csv(os.path.join(PROCESSED_DIR, "crop_price_monthly.csv"))
        self._build_or_load_models()

    def _build_or_load_models(self):
        """Fit trend & seasonality models per crop."""
        self.crop_stats = {}
        crops = self.summary_df["Crop"].unique()

        for crop in crops:
            sub = self.monthly_df[self.monthly_df["Crop"] == crop].sort_values(["Year", "Month"])
            prices = sub["Price_Modal_Mean"].values
            
            if len(prices) == 0:
                mean_p = 2500.0
                std_p = 300.0
            else:
                mean_p = float(np.mean(prices))
                std_p = float(np.std(prices))
            
            # Linear trend over recent 24 periods
            if len(prices) >= 12:
                recent = prices[-24:]
                t = np.arange(len(recent))
                slope, intercept = np.polyfit(t, recent, 1)
                last_price = float(recent[-1])
            else:
                slope = 0.0
                intercept = mean_p
                last_price = mean_p

            # Monthly seasonal indices (1..12)
            monthly_season = sub.groupby("Month")["Price_Modal_Mean"].mean().to_dict()
            overall_avg = sub["Price_Modal_Mean"].mean() if len(sub) > 0 else 1.0
            seasonal_factors = {
                m: round(float(monthly_season.get(m, overall_avg) / (overall_avg if overall_avg > 0 else 1.0)), 3)
                for m in range(1, 13)
            }

            self.crop_stats[crop] = {
                "crop": crop,
                "current_price_rs_quintal": round(last_price, 1),
                "current_price_rs_tonne": round(last_price * 10.0, 1),
                "mean_price_rs_quintal": round(mean_p, 1),
                "mean_price_rs_tonne": round(mean_p * 10.0, 1),
                "std_price_rs_quintal": round(std_p, 1),
                "std_price_rs_tonne": round(std_p * 10.0, 1),
                "volatility_ratio": round(std_p / max(1.0, mean_p), 3),
                "trend_slope": round(float(slope), 2),
                "seasonal_factors": seasonal_factors,
                "history_points": len(prices)
            }

        # Save metadata
        os.makedirs(MODELS_DIR, exist_ok=True)
        meta_path = os.path.join(MODELS_DIR, "price_metadata.json")
        with open(meta_path, "w") as f:
            json.dump(self.crop_stats, f, indent=2)

        # Save model pickle
        joblib.dump(self.crop_stats, os.path.join(MODELS_DIR, "price_model.pkl"))
        print(f"Price forecast profiles saved for {len(crops)} crops.")

    def forecast_horizons(self, crop, start_month=10):
        """Forecast price for 1-month, 3-month, 6-month, and 12-month horizons."""
        stats = self.crop_stats.get(crop)
        if not stats:
            # Fallback
            return {
                "next_month": 25000.0,
                "month_3": 25500.0,
                "month_6": 26000.0,
                "month_12": 26500.0,
                "volatility": 0.12
            }

        current_q = stats["current_price_rs_quintal"]
        slope = stats["trend_slope"]
        season_factors = stats["seasonal_factors"]

        forecasts = {}
        for h, label in [(1, "1_month"), (3, "3_month"), (6, "6_month"), (12, "12_month")]:
            target_month = ((start_month + h - 1) % 12) + 1
            sf = season_factors.get(target_month, 1.0)
            pred_q = (current_q + slope * h) * sf
            pred_t = pred_q * 10.0 # Rs per tonne
            forecasts[label] = {
                "price_rs_quintal": round(pred_q, 1),
                "price_rs_tonne": round(pred_t, 1),
                "target_month": target_month
            }

        forecasts["crop"] = crop
        forecasts["current_price_rs_tonne"] = stats["current_price_rs_tonne"]
        forecasts["volatility_ratio"] = stats["volatility_ratio"]
        forecasts["std_price_rs_tonne"] = stats["std_price_rs_tonne"]
        return forecasts

    def get_all_crop_prices(self):
        """Returns baseline price and volatility for all crops."""
        results = {}
        for crop, stats in self.crop_stats.items():
            results[crop] = {
                "price_rs_quintal": stats["current_price_rs_quintal"],
                "price_rs_tonne": stats["current_price_rs_tonne"],
                "volatility": stats["volatility_ratio"],
                "std_tonne": stats["std_price_rs_tonne"]
            }
        return results

if __name__ == "__main__":
    pf = PriceForecaster()
    for crop in ["Rice", "Wheat", "Maize", "Cotton", "Sugarcane"]:
        f = pf.forecast_horizons(crop)
        print(f"{crop:10} | Current: Rs {f['current_price_rs_tonne']}/t | 3M: Rs {f['3_month']['price_rs_tonne']}/t | Volatility: {f['volatility_ratio']}")
