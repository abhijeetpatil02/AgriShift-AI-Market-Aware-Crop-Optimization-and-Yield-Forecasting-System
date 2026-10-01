"""
Yield Prediction Engine
Trains Baseline Ridge, Random Forest, and XGBoost models on historical crop yields.
Evaluates using Walk-Forward / Time-Based splits (2015-2021 train, 2022-2023 test).
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_PATH = os.path.join(BASE_DIR, "data", "processed", "master_dataset.csv")
MODELS_DIR = os.path.join(BASE_DIR, "models")

CAT_COLS = ["State", "District", "Crop", "Season"]
NUM_COLS = [
    "Nitrogen_kg_ha", "Phosphorus_kg_ha", "Potassium_kg_ha", "pH",
    "Organic_Carbon_pct", "EC_dS_per_m", "Avg_Temperature_C",
    "Total_Rainfall_mm", "Avg_Humidity_pct", "Avg_Soil_Moisture_pct"
]
TARGET_COL = "Yield_kg_per_ha"

def load_data():
    df = pd.read_csv(PROCESSED_PATH)
    train_df = df[df["Crop_Year"] <= 2021].copy()
    test_df = df[df["Crop_Year"] >= 2022].copy()
    return df, train_df, test_df

def build_preprocessor():
    categorical_transformer = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    numerical_transformer = StandardScaler()

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", categorical_transformer, CAT_COLS),
            ("num", numerical_transformer, NUM_COLS)
        ]
    )
    return preprocessor

def train_and_evaluate_models():
    os.makedirs(MODELS_DIR, exist_ok=True)
    df, train_df, test_df = load_data()

    X_train = train_df[CAT_COLS + NUM_COLS]
    y_train = train_df[TARGET_COL]

    X_test = test_df[CAT_COLS + NUM_COLS]
    y_test = test_df[TARGET_COL]

    preprocessor = build_preprocessor()

    models = {
        "Ridge_Regression": Ridge(alpha=1.0),
        "Random_Forest": RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1),
        "XGBoost": XGBRegressor(n_estimators=120, max_depth=6, learning_rate=0.08, random_state=42, n_jobs=-1)
    }

    results = {}
    best_r2 = -1e9
    best_model_name = None
    best_pipeline = None

    print(f"Training models with {len(X_train)} train rows and {len(X_test)} test rows (time-split: train <=2021, test >=2022)...")

    for name, model in models.items():
        pipeline = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("regressor", model)
        ])
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)

        # In kg/ha
        rmse_kg = np.sqrt(mean_squared_error(y_test, y_pred))
        mae_kg = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        # In tonnes/ha
        rmse_tonnes = rmse_kg / 1000.0
        mae_tonnes = mae_kg / 1000.0

        results[name] = {
            "RMSE_kg_ha": round(float(rmse_kg), 2),
            "MAE_kg_ha": round(float(mae_kg), 2),
            "RMSE_tonnes_ha": round(float(rmse_tonnes), 3),
            "MAE_tonnes_ha": round(float(mae_tonnes), 3),
            "R2_Score": round(float(r2), 4)
        }
        print(f"-> {name:18} | R2: {r2:.4f} | RMSE: {rmse_kg:.1f} kg/ha ({rmse_tonnes:.2f} t/ha) | MAE: {mae_kg:.1f} kg/ha")

        if r2 > best_r2:
            best_r2 = r2
            best_model_name = name
            best_pipeline = pipeline

    # Extract feature importances if tree model
    feature_importance_dict = {}
    fitted_preprocessor = best_pipeline.named_steps["preprocessor"]
    fitted_regressor = best_pipeline.named_steps["regressor"]

    try:
        cat_features = fitted_preprocessor.named_transformers_["cat"].get_feature_names_out(CAT_COLS)
        all_features = list(cat_features) + NUM_COLS
        if hasattr(fitted_regressor, "feature_importances_"):
            importances = fitted_regressor.feature_importances_
            top_indices = np.argsort(importances)[::-1][:20]
            feature_importance_dict = {
                all_features[idx]: round(float(importances[idx]), 4)
                for idx in top_indices
            }
    except Exception as e:
        print(f"Feature importance extraction note: {e}")

    # Save best pipeline
    model_save_path = os.path.join(MODELS_DIR, "yield_model.pkl")
    joblib.dump(best_pipeline, model_save_path)
    print(f"Best yield model ({best_model_name}) saved to: {model_save_path}")

    # Save metadata
    metadata = {
        "best_model": best_model_name,
        "evaluation_metrics": results,
        "top_feature_importances": feature_importance_dict,
        "train_years": "2015-2021",
        "test_years": "2022-2023",
        "features": {
            "categorical": CAT_COLS,
            "numerical": NUM_COLS
        },
        "crops": list(df["Crop"].unique()),
        "states": list(df["State"].unique()),
        "districts": list(df["District"].unique())
    }
    meta_path = os.path.join(MODELS_DIR, "yield_metadata.json")
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"Yield metadata saved to: {meta_path}")

    return best_pipeline, metadata

class YieldPredictor:
    """Wrapper to load trained model and predict crop yield."""
    def __init__(self):
        self.reload()

    def reload(self):
        model_path = os.path.join(MODELS_DIR, "yield_model.pkl")
        meta_path = os.path.join(MODELS_DIR, "yield_metadata.json")
        if not os.path.exists(model_path):
            train_and_evaluate_models()
        self.pipeline = joblib.load(model_path)
        with open(meta_path, "r") as f:
            self.metadata = json.load(f)

    def predict_single(self, state, district, crop, season, n, p, k, ph, oc, ec, temp, rainfall, humidity, moisture):
        row = pd.DataFrame([{
            "State": state,
            "District": district,
            "Crop": crop,
            "Season": season,
            "Nitrogen_kg_ha": n,
            "Phosphorus_kg_ha": p,
            "Potassium_kg_ha": k,
            "pH": ph,
            "Organic_Carbon_pct": oc,
            "EC_dS_per_m": ec,
            "Avg_Temperature_C": temp,
            "Total_Rainfall_mm": rainfall,
            "Avg_Humidity_pct": humidity,
            "Avg_Soil_Moisture_pct": moisture
        }])
        pred_kg = self.pipeline.predict(row)[0]
        # Yield cannot be negative
        pred_kg = max(100.0, float(pred_kg))
        pred_tonnes = pred_kg / 1000.0
        return {
            "crop": crop,
            "predicted_yield_kg_ha": round(pred_kg, 1),
            "predicted_yield_tonnes_ha": round(pred_tonnes, 2)
        }

    def predict_all_crops(self, state, district, season, n, p, k, ph, oc, ec, temp, rainfall, humidity, moisture, crops=None):
        if crops is None:
            crops = self.metadata["crops"]
        rows = []
        for crop in crops:
            rows.append({
                "State": state,
                "District": district,
                "Crop": crop,
                "Season": season,
                "Nitrogen_kg_ha": n,
                "Phosphorus_kg_ha": p,
                "Potassium_kg_ha": k,
                "pH": ph,
                "Organic_Carbon_pct": oc,
                "EC_dS_per_m": ec,
                "Avg_Temperature_C": temp,
                "Total_Rainfall_mm": rainfall,
                "Avg_Humidity_pct": humidity,
                "Avg_Soil_Moisture_pct": moisture
            })
        batch_df = pd.DataFrame(rows)
        preds_kg = self.pipeline.predict(batch_df)
        results = {}
        for crop, pkg in zip(crops, preds_kg):
            val_kg = max(100.0, float(pkg))
            results[crop] = {
                "predicted_yield_kg_ha": round(val_kg, 1),
                "predicted_yield_tonnes_ha": round(val_kg / 1000.0, 2)
            }
        return results

if __name__ == "__main__":
    train_and_evaluate_models()
