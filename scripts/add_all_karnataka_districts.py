"""
Add All 31 Districts of Karnataka to AgriShift Datasets & Database
Generates agronomically realistic soil, climate, and crop yield data for
the remaining 27 districts of Karnataka across 2015-2023, rebuilds the
master dataset and district directory, updates the SQLite database,
and retrains the yield prediction ML models.
"""

import os
import sys
import json
import sqlite3
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

DATASET_DIR = os.path.join(BASE_DIR, "DataSet")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
MODELS_DIR = os.path.join(BASE_DIR, "models")
DB_PATH = os.path.join(BASE_DIR, "backend", "agrishift.db")

# All 31 Karnataka Districts categorized by Agro-Climatic Zone
KARNATAKA_DISTRICT_PROFILES = {
    # 1. North Dry & Semi-Arid (Black Soil, High Temp, Moderate/Low Rain)
    "Bagalkote": {"zone": "north_dry", "soil_ph": (7.4, 7.8), "n": (210, 240), "p": (11, 15), "k": (160, 210), "oc": (0.46, 0.54), "ec": (0.4, 0.8), "rain_k": (620, 780), "rain_r": (80, 130), "temp_k": (29.0, 31.0), "temp_r": (21.0, 23.0)},
    "Ballari": {"zone": "north_dry", "soil_ph": (7.3, 7.7), "n": (205, 235), "p": (10, 14), "k": (165, 215), "oc": (0.45, 0.53), "ec": (0.4, 0.8), "rain_k": (600, 750), "rain_r": (75, 125), "temp_k": (29.5, 31.5), "temp_r": (21.5, 23.5)},
    "Bidar": {"zone": "north_dry", "soil_ph": (7.1, 7.5), "n": (215, 245), "p": (11, 15), "k": (170, 220), "oc": (0.48, 0.56), "ec": (0.3, 0.7), "rain_k": (750, 920), "rain_r": (90, 140), "temp_k": (28.5, 30.5), "temp_r": (20.0, 22.5)},
    "Gadag": {"zone": "north_dry", "soil_ph": (7.3, 7.7), "n": (210, 240), "p": (11, 15), "k": (160, 210), "oc": (0.46, 0.54), "ec": (0.35, 0.75), "rain_k": (640, 800), "rain_r": (85, 135), "temp_k": (28.5, 30.5), "temp_r": (21.0, 23.0)},
    "Kalaburagi": {"zone": "north_dry", "soil_ph": (7.5, 7.9), "n": (200, 230), "p": (10, 14), "k": (165, 215), "oc": (0.44, 0.52), "ec": (0.4, 0.85), "rain_k": (680, 840), "rain_r": (80, 130), "temp_k": (29.5, 31.5), "temp_r": (21.5, 23.5)},
    "Koppal": {"zone": "north_dry", "soil_ph": (7.3, 7.7), "n": (205, 235), "p": (11, 15), "k": (160, 210), "oc": (0.46, 0.54), "ec": (0.35, 0.75), "rain_k": (610, 760), "rain_r": (80, 130), "temp_k": (29.0, 31.0), "temp_r": (21.0, 23.0)},
    "Vijayanagara": {"zone": "north_dry", "soil_ph": (7.2, 7.6), "n": (210, 240), "p": (11, 15), "k": (165, 215), "oc": (0.47, 0.55), "ec": (0.35, 0.75), "rain_k": (620, 770), "rain_r": (80, 130), "temp_k": (29.0, 31.0), "temp_r": (21.0, 23.0)},
    "Vijayapura": {"zone": "north_dry", "soil_ph": (7.5, 8.0), "n": (200, 230), "p": (10, 14), "k": (155, 205), "oc": (0.43, 0.51), "ec": (0.4, 0.9), "rain_k": (580, 730), "rain_r": (70, 120), "temp_k": (29.5, 31.5), "temp_r": (21.5, 23.5)},
    "Yadgir": {"zone": "north_dry", "soil_ph": (7.4, 7.8), "n": (205, 235), "p": (10, 14), "k": (160, 210), "oc": (0.45, 0.53), "ec": (0.4, 0.8), "rain_k": (650, 810), "rain_r": (75, 125), "temp_k": (29.5, 31.5), "temp_r": (21.5, 23.5)},

    # 2. Northern & Central Transition (Red Loam / Medium Black, Good Rain)
    "Dharwad": {"zone": "transition", "soil_ph": (6.6, 7.1), "n": (225, 255), "p": (12, 16), "k": (190, 235), "oc": (0.52, 0.62), "ec": (0.2, 0.5), "rain_k": (820, 1020), "rain_r": (110, 155), "temp_k": (27.5, 29.5), "temp_r": (20.5, 22.5)},
    "Haveri": {"zone": "transition", "soil_ph": (6.7, 7.2), "n": (220, 250), "p": (12, 16), "k": (185, 230), "oc": (0.50, 0.60), "ec": (0.25, 0.55), "rain_k": (800, 990), "rain_r": (105, 150), "temp_k": (27.8, 29.8), "temp_r": (20.8, 22.8)},

    # 3. Southern & Eastern Dry (Red Sandy Loam, Plains)
    "Bengaluru Rural": {"zone": "south_dry", "soil_ph": (6.3, 6.8), "n": (220, 250), "p": (12, 16), "k": (180, 225), "oc": (0.50, 0.60), "ec": (0.2, 0.5), "rain_k": (780, 960), "rain_r": (115, 165), "temp_k": (26.5, 28.5), "temp_r": (19.5, 21.5)},
    "Bengaluru Urban": {"zone": "south_dry", "soil_ph": (6.4, 6.9), "n": (215, 245), "p": (12, 16), "k": (175, 220), "oc": (0.49, 0.58), "ec": (0.25, 0.55), "rain_k": (760, 940), "rain_r": (110, 160), "temp_k": (26.8, 28.8), "temp_r": (19.8, 21.8)},
    "Chamarajanagar": {"zone": "south_dry", "soil_ph": (6.5, 7.0), "n": (210, 240), "p": (11, 15), "k": (170, 215), "oc": (0.48, 0.57), "ec": (0.25, 0.6), "rain_k": (720, 900), "rain_r": (110, 155), "temp_k": (27.0, 29.0), "temp_r": (20.0, 22.0)},
    "Chikkaballapura": {"zone": "south_dry", "soil_ph": (6.5, 7.0), "n": (210, 240), "p": (11, 15), "k": (170, 215), "oc": (0.47, 0.56), "ec": (0.3, 0.65), "rain_k": (710, 890), "rain_r": (100, 150), "temp_k": (27.2, 29.2), "temp_r": (20.0, 22.0)},
    "Chitradurga": {"zone": "south_dry", "soil_ph": (6.8, 7.3), "n": (215, 245), "p": (11, 15), "k": (180, 225), "oc": (0.47, 0.56), "ec": (0.35, 0.7), "rain_k": (650, 820), "rain_r": (90, 140), "temp_k": (28.0, 30.0), "temp_r": (21.0, 23.0)},
    "Kolar": {"zone": "south_dry", "soil_ph": (6.4, 6.9), "n": (215, 245), "p": (12, 16), "k": (175, 220), "oc": (0.48, 0.57), "ec": (0.3, 0.65), "rain_k": (730, 910), "rain_r": (105, 155), "temp_k": (27.0, 29.0), "temp_r": (20.0, 22.0)},
    "Mandya": {"zone": "south_dry", "soil_ph": (6.5, 7.0), "n": (225, 255), "p": (13, 17), "k": (185, 230), "oc": (0.52, 0.62), "ec": (0.2, 0.5), "rain_k": (760, 950), "rain_r": (120, 170), "temp_k": (27.0, 29.0), "temp_r": (20.0, 22.0)},
    "Ramanagara": {"zone": "south_dry", "soil_ph": (6.4, 6.9), "n": (220, 250), "p": (12, 16), "k": (180, 225), "oc": (0.50, 0.59), "ec": (0.2, 0.55), "rain_k": (770, 960), "rain_r": (115, 165), "temp_k": (26.8, 28.8), "temp_r": (19.8, 21.8)},
    "Tumakuru": {"zone": "south_dry", "soil_ph": (6.6, 7.1), "n": (215, 245), "p": (11, 15), "k": (175, 220), "oc": (0.48, 0.58), "ec": (0.25, 0.6), "rain_k": (700, 880), "rain_r": (95, 145), "temp_k": (27.5, 29.5), "temp_r": (20.5, 22.5)},

    # 4. Hilly, Malnad & Coastal (Heavy Rainfall, Lateritic / Alluvial Soil)
    "Chikkamagaluru": {"zone": "malnad", "soil_ph": (5.9, 6.5), "n": (235, 265), "p": (13, 17), "k": (190, 240), "oc": (0.60, 0.72), "ec": (0.15, 0.4), "rain_k": (1450, 1950), "rain_r": (130, 185), "temp_k": (25.0, 27.5), "temp_r": (18.5, 21.0)},
    "Dakshina Kannada": {"zone": "coastal", "soil_ph": (5.6, 6.3), "n": (240, 270), "p": (13, 17), "k": (180, 235), "oc": (0.62, 0.75), "ec": (0.15, 0.45), "rain_k": (2200, 2900), "rain_r": (140, 200), "temp_k": (26.5, 28.5), "temp_r": (21.5, 23.5)},
    "Hassan": {"zone": "malnad", "soil_ph": (6.1, 6.6), "n": (230, 260), "p": (13, 17), "k": (190, 235), "oc": (0.56, 0.68), "ec": (0.15, 0.45), "rain_k": (1050, 1450), "rain_r": (120, 175), "temp_k": (26.0, 28.0), "temp_r": (19.0, 21.5)},
    "Kodagu": {"zone": "malnad", "soil_ph": (5.7, 6.4), "n": (240, 270), "p": (13, 17), "k": (195, 245), "oc": (0.65, 0.78), "ec": (0.12, 0.38), "rain_k": (1800, 2500), "rain_r": (135, 190), "temp_k": (24.0, 26.5), "temp_r": (17.5, 20.0)},
    "Shivamogga": {"zone": "malnad", "soil_ph": (6.0, 6.6), "n": (230, 265), "p": (13, 17), "k": (190, 240), "oc": (0.58, 0.70), "ec": (0.15, 0.45), "rain_k": (1350, 1850), "rain_r": (125, 180), "temp_k": (26.0, 28.0), "temp_r": (19.5, 21.8)},
    "Udupi": {"zone": "coastal", "soil_ph": (5.5, 6.2), "n": (240, 270), "p": (13, 17), "k": (180, 230), "oc": (0.62, 0.75), "ec": (0.15, 0.45), "rain_k": (2300, 3050), "rain_r": (140, 205), "temp_k": (26.5, 28.5), "temp_r": (21.5, 23.5)},
    "Uttara Kannada": {"zone": "coastal", "soil_ph": (5.7, 6.4), "n": (235, 265), "p": (13, 17), "k": (185, 235), "oc": (0.60, 0.72), "ec": (0.15, 0.45), "rain_k": (2100, 2800), "rain_r": (135, 195), "temp_k": (26.0, 28.0), "temp_r": (21.0, 23.0)}
}

# 10 Standard Crops with their Karnataka Seasons and typical Yield Range (kg/ha)
CROP_SPECS = {
    "Bajra": [("Kharif", 850, 1750, 15000, 32000)],
    "Cotton": [("Kharif", 400, 680, 18000, 30000)],
    "Gram": [("Rabi", 750, 1320, 16000, 28000)],
    "Groundnut": [("Kharif", 950, 1700, 18000, 35000), ("Rabi", 1200, 2050, 12000, 25000)],
    "Jowar": [("Kharif", 780, 1450, 18000, 32000), ("Rabi", 850, 1650, 15000, 28000)],
    "Maize": [("Kharif", 1950, 3500, 18000, 32000), ("Rabi", 2200, 3800, 12000, 24000)],
    "Rice": [("Kharif", 1900, 3100, 18000, 30000)],
    "Soyabean": [("Kharif", 880, 1500, 12000, 26000)],
    "Sugarcane": [("Whole Year", 52000, 82000, 15000, 32000)],
    "Wheat": [("Rabi", 2600, 4200, 12000, 22000)]
}

YEARS = list(range(2015, 2024))

def generate_karnataka_data():
    np.random.seed(42)

    soil_path = os.path.join(DATASET_DIR, "soil_health_sample_dataset.csv")
    clim_path = os.path.join(DATASET_DIR, "climate_seasonal_sample_dataset.csv")
    yield_path = os.path.join(DATASET_DIR, "crop_yield_sample_dataset.csv")

    soil_df = pd.read_csv(soil_path)
    clim_df = pd.read_csv(clim_path)
    yield_df = pd.read_csv(yield_path)

    existing_districts = set(yield_df[yield_df["State"] == "Karnataka"]["District"].unique())
    print(f"Existing Karnataka districts in dataset: {sorted(list(existing_districts))}")

    new_districts = [d for d in KARNATAKA_DISTRICT_PROFILES.keys() if d not in existing_districts]
    print(f"Adding {len(new_districts)} new Karnataka districts...")

    new_soil_rows = []
    new_clim_rows = []
    new_yield_rows = []

    for dist in new_districts:
        prof = KARNATAKA_DISTRICT_PROFILES[dist]

        for year in YEARS:
            # 1. Soil Health Row
            n = round(np.random.uniform(prof["n"][0], prof["n"][1]), 1)
            p = round(np.random.uniform(prof["p"][0], prof["p"][1]), 1)
            k = round(np.random.uniform(prof["k"][0], prof["k"][1]), 1)
            ph = round(np.random.uniform(prof["soil_ph"][0], prof["soil_ph"][1]), 2)
            oc = round(np.random.uniform(prof["oc"][0], prof["oc"][1]), 2)
            ec = round(np.random.uniform(prof["ec"][0], prof["ec"][1]), 2)

            new_soil_rows.append({
                "State": "Karnataka",
                "District": dist,
                "Sample_Year": year,
                "Nitrogen_kg_ha": n,
                "Phosphorus_kg_ha": p,
                "Potassium_kg_ha": k,
                "pH": ph,
                "Organic_Carbon_pct": oc,
                "EC_dS_per_m": ec
            })

            # 2. Climate Seasonal Rows (Kharif, Rabi, Whole Year)
            rain_k = round(np.random.uniform(prof["rain_k"][0], prof["rain_k"][1]), 1)
            temp_k = round(np.random.uniform(prof["temp_k"][0], prof["temp_k"][1]), 1)
            hum_k = round(np.random.uniform(73.0, 84.0) if prof["zone"] in ["malnad", "coastal"] else np.random.uniform(70.0, 78.0), 1)
            sm_k = round(np.random.uniform(32.0, 42.0) if prof["zone"] in ["malnad", "coastal"] else np.random.uniform(26.0, 34.0), 1)

            rain_r = round(np.random.uniform(prof["rain_r"][0], prof["rain_r"][1]), 1)
            temp_r = round(np.random.uniform(prof["temp_r"][0], prof["temp_r"][1]), 1)
            hum_r = round(np.random.uniform(58.0, 66.0), 1)
            sm_r = round(np.random.uniform(11.0, 16.0), 1)

            rain_wy = round(rain_k + rain_r + np.random.uniform(120.0, 250.0), 1)
            temp_wy = round((temp_k + temp_r) / 2.0 + np.random.uniform(2.0, 3.5), 1)
            hum_wy = round((hum_k + hum_r) / 2.0, 1)
            sm_wy = round((sm_k + sm_r) / 2.0, 1)

            new_clim_rows.append({
                "State": "Karnataka", "District": dist, "Crop_Year": year, "Season": "Kharif",
                "Avg_Temperature_C": temp_k, "Total_Rainfall_mm": rain_k, "Avg_Humidity_pct": hum_k, "Avg_Soil_Moisture_pct": sm_k
            })
            new_clim_rows.append({
                "State": "Karnataka", "District": dist, "Crop_Year": year, "Season": "Rabi",
                "Avg_Temperature_C": temp_r, "Total_Rainfall_mm": rain_r, "Avg_Humidity_pct": hum_r, "Avg_Soil_Moisture_pct": sm_r
            })
            new_clim_rows.append({
                "State": "Karnataka", "District": dist, "Crop_Year": year, "Season": "Whole Year",
                "Avg_Temperature_C": temp_wy, "Total_Rainfall_mm": rain_wy, "Avg_Humidity_pct": hum_wy, "Avg_Soil_Moisture_pct": sm_wy
            })

            # 3. Crop Yield Rows
            for crop, season_configs in CROP_SPECS.items():
                for season, min_y, max_y, min_a, max_a in season_configs:
                    area = round(np.random.uniform(min_a, max_a), 1)
                    yield_kg = round(np.random.uniform(min_y, max_y), 1)
                    prod = round((area * yield_kg) / 1000.0, 1)

                    new_yield_rows.append({
                        "State": "Karnataka",
                        "District": dist,
                        "Crop": crop,
                        "Season": season,
                        "Crop_Year": year,
                        "Area_Hectares": area,
                        "Production_Tonnes": prod,
                        "Yield_kg_per_ha": yield_kg
                    })

    # Append to raw dataframes and save
    if new_soil_rows:
        updated_soil = pd.concat([soil_df, pd.DataFrame(new_soil_rows)], ignore_index=True)
        updated_soil.to_csv(soil_path, index=False)
        print(f"Updated {soil_path} (+{len(new_soil_rows)} rows)")

    if new_clim_rows:
        updated_clim = pd.concat([clim_df, pd.DataFrame(new_clim_rows)], ignore_index=True)
        updated_clim.to_csv(clim_path, index=False)
        print(f"Updated {clim_path} (+{len(new_clim_rows)} rows)")

    if new_yield_rows:
        updated_yield = pd.concat([yield_df, pd.DataFrame(new_yield_rows)], ignore_index=True)
        updated_yield.to_csv(yield_path, index=False)
        print(f"Updated {yield_path} (+{len(new_yield_rows)} rows)")

def rebuild_pipeline_and_db():
    print("Rebuilding data pipeline...")
    from ml.data_pipeline import run_pipeline
    summary = run_pipeline()
    print("Data pipeline finished:", summary)

    print("Updating SQLite database...")
    from backend.database import init_db
    init_db()
    print("Database district baselines updated.")

def retrain_yield_model():
    print("Retraining yield models with all 31 Karnataka districts...")
    from ml.yield_prediction import train_and_evaluate_models
    train_and_evaluate_models()
    print("Yield models retrained and saved.")

if __name__ == "__main__":
    generate_karnataka_data()
    rebuild_pipeline_and_db()
    retrain_yield_model()
    print("\n[SUCCESS] All 31 Karnataka districts have been successfully added to the dataset, database, and ML models!")
