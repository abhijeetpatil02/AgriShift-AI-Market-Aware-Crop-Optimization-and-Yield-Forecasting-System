"""
train_crop_model.py
Executes Step 6 to Step 10:
- Step 6: Exploratory Data Analysis (EDA)
- Step 7: Prepare X and y, Train/Test Split
- Step 8: Train Random Forest & XGBoost Classifiers
- Step 9: Detailed Evaluation (Accuracy, Top-3 Accuracy, Precision, Recall, F1, Per-crop report)
- Step 10: Save best model artifact and demonstrate Top-3 prediction on sample farmer input
"""

import pandas as pd
import numpy as np
import os
import joblib
import json

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report, top_k_accuracy_score

def run_training_pipeline():
    print("==========================================================")
    print("STEP 6: EXPLORATORY DATA ANALYSIS (EDA)")
    print("==========================================================")
    
    data_path = 'DataSet/processed/crop_master_dataset.csv'
    df = pd.read_csv(data_path)
    print(f"Loaded master dataset: {df.shape[0]} rows, {df.shape[1]} columns")
    
    # Check top crops
    top_crops = df['Crop'].value_counts()
    print(f"Total Unique Crops: {len(top_crops)}")
    print("Top 10 Most Frequent Crops:")
    for crop, count in top_crops.head(10).items():
        print(f"  - {crop:<20}: {count} records")
        
    print("\nRainfall Profiles by Crop (Top 5 high rainfall crops):")
    rain_crop = df.groupby('Crop')['Rainfall'].mean().sort_values(ascending=False).head(5)
    for crop, rain in rain_crop.items():
        print(f"  - {crop:<20}: {rain:.1f} mm average rainfall")
        
    print("\nSoil pH Profiles by Crop (Top 3 acidic vs alkaline):")
    ph_crop = df.groupby('Crop')['pH'].mean().sort_values()
    print("  Most Acidic Soils:")
    for crop, ph in ph_crop.head(3).items():
        print(f"    * {crop:<18}: pH {ph:.2f}")
    print("  Most Alkaline Soils:")
    for crop, ph in ph_crop.tail(3).items():
        print(f"    * {crop:<18}: pH {ph:.2f}")

    print("\n==========================================================")
    print("STEP 7: PREPARE X AND y (FEATURE MATRIX & TARGET)")
    print("==========================================================")
    
    X = df.drop('Crop', axis=1)
    y_raw = df['Crop']
    
    # Target encoding for XGBoost compatibility
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y_raw)
    class_names = list(label_encoder.classes_)
    
    categorical_cols = ['District', 'Season']
    numerical_cols = ['N', 'P', 'K', 'pH', 'Temperature', 'Humidity', 'Rainfall']
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_cols),
            ('num', 'passthrough', numerical_cols)
        ]
    )
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"Train set: {X_train.shape[0]} samples | Test set: {X_test.shape[0]} samples")

    print("\n==========================================================")
    print("STEP 8: TRAIN MODELS (RANDOM FOREST VS XGBOOST)")
    print("==========================================================")
    
    # Model 1: Random Forest
    print("Training Model 1: Random Forest Classifier...")
    rf_pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=140, max_depth=25, min_samples_split=2, random_state=42, n_jobs=-1))
    ])
    rf_pipeline.fit(X_train, y_train)
    
    # Model 2: XGBoost
    print("Training Model 2: XGBoost Classifier...")
    xgb_pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42, eval_metric='mlogloss', n_jobs=-1))
    ])
    xgb_pipeline.fit(X_train, y_train)

    print("\n==========================================================")
    print("STEP 9: EVALUATE MODELS (ACCURACY, TOP-3 ACCURACY, F1)")
    print("==========================================================")
    
    models = {
        "Random Forest Classifier": rf_pipeline,
        "XGBoost Classifier": xgb_pipeline
    }
    
    eval_results = {}
    
    for name, model in models.items():
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)
        
        acc = accuracy_score(y_test, y_pred)
        top3_acc = top_k_accuracy_score(y_test, y_proba, k=3)
        
        eval_results[name] = {
            'accuracy': acc,
            'top3_accuracy': top3_acc,
            'model': model
        }
        
        print(f"\n--- {name} ---")
        print(f"Top-1 Accuracy: {acc * 100:.2f}%")
        print(f"Top-3 Recommendation Accuracy: {top3_acc * 100:.2f}% (The actual crop was in Top 3)")

    # Select best model based on Top-3 Accuracy & Top-1
    best_name = max(eval_results.keys(), key=lambda k: (eval_results[k]['top3_accuracy'], eval_results[k]['accuracy']))
    best_model = eval_results[best_name]['model']
    print(f"\n>>> Best Performing Model: {best_name} <<<")
    
    # Detailed classification report for best model
    y_pred_best = best_model.predict(X_test)
    report = classification_report(y_test, y_pred_best, target_names=class_names, output_dict=True)
    
    print("\nPer-Crop Performance Sample (Precision / Recall / F1):")
    sample_crops = ['Maize', 'Rice', 'Sunflower', 'Jowar', 'Groundnut', 'Ragi', 'Cotton(lint)', 'Coconut', 'Sugarcane']
    for c in sample_crops:
        if c in report:
            r = report[c]
            print(f"  - {c:<15}: Precision={r['precision']:.2f}, Recall={r['recall']:.2f}, F1={r['f1-score']:.2f} (Support: {int(r['support'])})")

    # Overall Metrics
    print(f"\nMacro Avg F1-Score: {report['macro avg']['f1-score']:.3f}")
    print(f"Weighted Avg F1-Score: {report['weighted avg']['f1-score']:.3f}")

    print("\n==========================================================")
    print("STEP 10: SAVE ARTIFACT & DEMONSTRATE TOP-3 INFERENCE")
    print("==========================================================")
    
    os.makedirs('models', exist_ok=True)
    model_save_path = 'models/crop_recommendation_model.joblib'
    
    bundle = {
        'model': best_model,
        'label_encoder': label_encoder,
        'classes': class_names,
        'model_name': best_name,
        'top1_accuracy': eval_results[best_name]['accuracy'],
        'top3_accuracy': eval_results[best_name]['top3_accuracy'],
        'features': {
            'categorical': categorical_cols,
            'numerical': numerical_cols
        }
    }
    
    joblib.dump(bundle, model_save_path)
    print(f"Saved complete model bundle to: {model_save_path}")

    # Test with farmer input example
    sample_farmer_input = pd.DataFrame([{
        'District': 'DHARWAD',
        'Season': 'Kharif',
        'N': 25.5,
        'P': 58.2,
        'K': 62.4,
        'pH': 7.1,
        'Temperature': 26.5,
        'Humidity': 72.0,
        'Rainfall': 550.0
    }])
    
    print("\nTesting Sample Farmer Input:")
    for k, v in sample_farmer_input.iloc[0].items():
        print(f"  {k:<12}: {v}")
        
    probs = best_model.predict_proba(sample_farmer_input)[0]
    top3_idx = np.argsort(probs)[::-1][:3]
    
    print("\n>>> Top 3 Recommended Crops for Farmer <<<")
    for rank, idx in enumerate(top3_idx, 1):
        crop = class_names[idx]
        conf = probs[idx] * 100
        print(f"  {rank}. {crop:<18} (Match Confidence: {conf:.1f}%)")

if __name__ == '__main__':
    run_training_pipeline()
