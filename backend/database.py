"""
AgriShift Database Layer (SQLite)
Manages district defaults, soil/climate baselines, and logs farmer recommendation runs.
"""

import os
import sqlite3
import json
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "backend", "agrishift.db")
PROCESSED_PATH = os.path.join(BASE_DIR, "data", "processed", "master_dataset.csv")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes tables and populates district baselines from master dataset."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. District defaults table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS district_baselines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            state TEXT NOT NULL,
            district TEXT NOT NULL,
            nitrogen REAL,
            phosphorus REAL,
            potassium REAL,
            ph REAL,
            organic_carbon REAL,
            ec REAL,
            avg_temp REAL,
            rainfall REAL,
            humidity REAL,
            soil_moisture REAL,
            UNIQUE(state, district)
        )
    """)

    # 2. Recommendations history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recommendation_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            farmer_name TEXT,
            state TEXT,
            district TEXT,
            farm_area_ha REAL,
            previous_crop TEXT,
            risk_preference TEXT,
            adoption_rate_pct REAL,
            allocated_crops TEXT,
            total_net_profit_rs REAL,
            total_switching_cost_rs REAL,
            portfolio_json TEXT
        )
    """)
    conn.commit()

    # Prepopulate district baselines if empty
    cursor.execute("SELECT COUNT(*) as cnt FROM district_baselines")
    count = cursor.fetchone()["cnt"]
    if count == 0 and os.path.exists(PROCESSED_PATH):
        print("Populating district baselines in SQLite...")
        df = pd.read_csv(PROCESSED_PATH)
        grouped = df.groupby(["State", "District"]).agg({
            "Nitrogen_kg_ha": "mean",
            "Phosphorus_kg_ha": "mean",
            "Potassium_kg_ha": "mean",
            "pH": "mean",
            "Organic_Carbon_pct": "mean",
            "EC_dS_per_m": "mean",
            "Avg_Temperature_C": "mean",
            "Total_Rainfall_mm": "mean",
            "Avg_Humidity_pct": "mean",
            "Avg_Soil_Moisture_pct": "mean"
        }).reset_index()

        for _, row in grouped.iterrows():
            cursor.execute("""
                INSERT OR IGNORE INTO district_baselines (
                    state, district, nitrogen, phosphorus, potassium, ph,
                    organic_carbon, ec, avg_temp, rainfall, humidity, soil_moisture
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row["State"], row["District"],
                round(float(row["Nitrogen_kg_ha"]), 1),
                round(float(row["Phosphorus_kg_ha"]), 1),
                round(float(row["Potassium_kg_ha"]), 1),
                round(float(row["pH"]), 2),
                round(float(row["Organic_Carbon_pct"]), 2),
                round(float(row["EC_dS_per_m"]), 2),
                round(float(row["Avg_Temperature_C"]), 1),
                round(float(row["Total_Rainfall_mm"]), 1),
                round(float(row["Avg_Humidity_pct"]), 1),
                round(float(row["Avg_Soil_Moisture_pct"]), 1)
            ))
        conn.commit()
        print(f"Prepopulated {len(grouped)} district baselines.")

    conn.close()

def get_district_defaults(state: str, district: str):
    """Retrieves baseline soil & climate averages for a district."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM district_baselines WHERE LOWER(state)=LOWER(?) AND LOWER(district)=LOWER(?)
    """, (state, district))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    # Default fallback
    return {
        "nitrogen": 240.0,
        "phosphorus": 16.0,
        "potassium": 210.0,
        "ph": 7.2,
        "organic_carbon": 0.48,
        "ec": 0.65,
        "avg_temp": 26.5,
        "rainfall": 750.0,
        "humidity": 62.0,
        "soil_moisture": 22.0
    }

def log_recommendation(farmer_name, state, district, farm_area, previous_crop, risk_pref, adoption_rate, portfolio, net_profit, switch_cost, full_data):
    """Logs a completed recommendation run into SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()
    crops_str = ", ".join([f"{p['crop']} ({p['allocated_ha']}ha)" for p in portfolio])
    cursor.execute("""
        INSERT INTO recommendation_logs (
            farmer_name, state, district, farm_area_ha, previous_crop,
            risk_preference, adoption_rate_pct, allocated_crops,
            total_net_profit_rs, total_switching_cost_rs, portfolio_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        farmer_name or "Farmer", state, district, farm_area, previous_crop,
        risk_pref, adoption_rate, crops_str, net_profit, switch_cost,
        json.dumps(full_data)
    ))
    conn.commit()
    inserted_id = cursor.lastrowid
    conn.close()
    return inserted_id

def get_recommendation_history(limit: int = 15):
    """Fetches recent recommendation history."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, timestamp, farmer_name, state, district, farm_area_ha,
               previous_crop, risk_preference, adoption_rate_pct,
               allocated_crops, total_net_profit_rs, total_switching_cost_rs
        FROM recommendation_logs
        ORDER BY id DESC LIMIT ?
    """, (limit,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

if __name__ == "__main__":
    init_db()
    sample = get_district_defaults("Karnataka", "Belagavi")
    print("Sample District Defaults for Belagavi, Karnataka:", sample)
