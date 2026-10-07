"""
train_yield_model.py
Trains and evaluates Model 2: Yield Prediction Regressor.
Compares Random Forest Regressor vs XGBoost Regressor.
Evaluates using R2 Score, RMSE, and MAE.
Saves best model pipeline to models/yield_prediction_model.joblib.
"""

import os
import joblib
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

def run_yield_training():
    print("=" * 60)
    print("STEP 1: LOAD YIELD MASTER DATASET")
    print("=" * 60)
    
    data_path = 'DataSet/processed/yield_master_dataset.csv'
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Missing dataset at {data_path}. Run prepare_yield_dataset.py first.")
        
    df = pd.read_csv(data_path)
    print(f"Loaded dataset: {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"Unique Crops: {df['Crop'].nunique()} | Districts: {df['District'].nunique()} | Seasons: {df['Season'].nunique()}")
    
    print("\nYield Statistics across all crops (Tonnes/Hectare):")
    print(df['Yield'].describe().to_string())
    
    print("\n" + "=" * 60)
    print("STEP 2: PREPARE FEATURE MATRIX (X) AND TARGET (y)")
    print("=" * 60)
    
    X = df.drop('Yield', axis=1)
    y = df['Yield']
    
    categorical_cols = ['District', 'Season', 'Crop']
    numerical_cols = ['N', 'P', 'K', 'pH', 'Temperature', 'Humidity', 'Rainfall']
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_cols),
            ('num', 'passthrough', numerical_cols)
        ]
    )
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f"Train samples: {len(X_train)} | Test samples: {len(X_test)}")
    
    print("\n" + "=" * 60)
    print("STEP 3: TRAIN REGRESSION MODELS (RF VS XGBOOST)")
    print("=" * 60)
    
    # Model A: Random Forest Regressor
    print("\n[1/2] Training Random Forest Regressor (n_estimators=150, max_depth=22)...")
    rf_pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(
            n_estimators=150,
            max_depth=22,
            min_samples_split=4,
            random_state=42,
            n_jobs=-1
        ))
    ])
    rf_pipeline.fit(X_train, y_train)
    rf_preds = rf_pipeline.predict(X_test)
    
    rf_r2 = r2_score(y_test, rf_preds)
    rf_rmse = np.sqrt(mean_squared_error(y_test, rf_preds))
    rf_mae = mean_absolute_error(y_test, rf_preds)
    
    print(f"Random Forest Results:")
    print(f"  - R² Score: {rf_r2:.4f}")
    print(f"  - RMSE:     {rf_rmse:.4f} Tonnes/Ha")
    print(f"  - MAE:      {rf_mae:.4f} Tonnes/Ha")
    
    # Model B: XGBoost Regressor
    print("\n[2/2] Training XGBoost Regressor (n_estimators=200, max_depth=7, lr=0.08)...")
    xgb_pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('regressor', XGBRegressor(
            n_estimators=200,
            max_depth=7,
            learning_rate=0.08,
            subsample=0.85,
            colsample_bytree=0.85,
            random_state=42,
            n_jobs=-1
        ))
    ])
    xgb_pipeline.fit(X_train, y_train)
    xgb_preds = xgb_pipeline.predict(X_test)
    
    xgb_r2 = r2_score(y_test, xgb_preds)
    xgb_rmse = np.sqrt(mean_squared_error(y_test, xgb_preds))
    xgb_mae = mean_absolute_error(y_test, xgb_preds)
    
    print(f"XGBoost Regressor Results:")
    print(f"  - R² Score: {xgb_r2:.4f}")
    print(f"  - RMSE:     {xgb_rmse:.4f} Tonnes/Ha")
    print(f"  - MAE:      {xgb_mae:.4f} Tonnes/Ha")
    
    print("\n" + "=" * 60)
    print("STEP 4: MODEL COMPARISON & SELECTION")
    print("=" * 60)
    
    comparison = pd.DataFrame({
        'Model': ['Random Forest Regressor', 'XGBoost Regressor'],
        'R2 Score': [rf_r2, xgb_r2],
        'RMSE (Tonnes/Ha)': [rf_rmse, xgb_rmse],
        'MAE (Tonnes/Ha)': [rf_mae, xgb_mae]
    })
    print(comparison.to_string(index=False))
    
    best_name = "Random Forest Regressor" if rf_r2 >= xgb_r2 else "XGBoost Regressor"
    best_pipeline = rf_pipeline if rf_r2 >= xgb_r2 else xgb_pipeline
    best_metrics = {
        'model_name': best_name,
        'r2_score': round(float(max(rf_r2, xgb_r2)), 4),
        'rmse': round(float(rf_rmse if best_name == "Random Forest Regressor" else xgb_rmse), 4),
        'mae': round(float(rf_mae if best_name == "Random Forest Regressor" else xgb_mae), 4),
        'features': list(X.columns),
        'categorical_cols': categorical_cols,
        'numerical_cols': numerical_cols
    }
    
    print(f"\nChampion Model: {best_name} (R² = {best_metrics['r2_score']})")
    
    print("\n" + "=" * 60)
    print("STEP 5: PERSIST MODEL ARTIFACT")
    print("=" * 60)
    
    os.makedirs('models', exist_ok=True)
    model_save_path = 'models/yield_prediction_model.joblib'
    
    joblib.dump({
        'pipeline': best_pipeline,
        'metadata': best_metrics
    }, model_save_path, compress=3)
    print(f"Model saved successfully to: {model_save_path}")
    
    print("\n" + "=" * 60)
    print("STEP 6: VALIDATION TEST - TOP 3 CROP YIELD FORECAST")
    print("=" * 60)
    
    # Simulate farmer input: Dharwad, Kharif season
    test_farmer = {
        'District': 'DHARWAD',
        'Season': 'Kharif',
        'N': 80.0,
        'P': 48.0,
        'K': 25.0,
        'pH': 6.5,
        'Temperature': 26.0,
        'Humidity': 68.0,
        'Rainfall': 650.0
    }
    
    sample_top3 = ['Maize', 'Sunflower', 'Dry chillies']
    farm_size_ha = 2.5
    
    print(f"Farmer Scenario: Dharwad | Kharif | Farm Size: {farm_size_ha} Hectares")
    print(f"Top 3 Crops from Model 1: {sample_top3}\n")
    
    for crop in sample_top3:
        input_data = pd.DataFrame([{**test_farmer, 'Crop': crop}])
        pred_yield = float(best_pipeline.predict(input_data)[0])
        pred_yield = max(pred_yield, 0.1)
        total_production = pred_yield * farm_size_ha
        print(f"[*] Crop: {crop:<15} -> Predicted Yield: {pred_yield:.2f} t/ha | Total Production: {total_production:.2f} Tonnes")

if __name__ == '__main__':
    run_yield_training()
