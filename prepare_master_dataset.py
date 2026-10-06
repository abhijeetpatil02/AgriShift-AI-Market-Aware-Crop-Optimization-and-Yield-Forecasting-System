"""
prepare_master_dataset.py
Vectorized Step 1 to 5: Merges Soil, Crop, and Regional Agro-Climatic Weather into Master Dataset.
"""

import pandas as pd
import numpy as np
import os
import sys

DISTRICT_NAME_MAP = {
    'BAGALKOT': 'BAGALKOTE',
    'BAGALKOTE': 'BAGALKOTE',
    'BALLARI': 'BALLARI',
    'BELLARY': 'BALLARI',
    'BELAGAVI': 'BELAGAVI',
    'BELGAUM': 'BELAGAVI',
    'BENGALURU RURAL': 'BANGALORE RURAL',
    'BANGALORE RURAL': 'BANGALORE RURAL',
    'BENGALURU URBAN': 'BENGALURU URBAN',
    'BANGALORE URBAN': 'BENGALURU URBAN',
    'BIDAR': 'BIDAR',
    'CHAMARAJANAGAR': 'CHAMARAJANAGAR',
    'CHAMARAJANAGARA': 'CHAMARAJANAGAR',
    'CHIKKABALLAPURA': 'CHIKKABALLAPURA',
    'CHIKBALLAPUR': 'CHIKKABALLAPURA',
    'CHIKKAMAGALURU': 'CHIKKAMAGALURU',
    'CHIKMAGALUR': 'CHIKKAMAGALURU',
    'CHITRADURGA': 'CHITRADURGA',
    'DAKSHINA KANNADA': 'DAKSHINA KANNADA',
    'DAKSHIN KANNAD': 'DAKSHINA KANNADA',
    'DAVANGERE': 'DAVANGERE',
    'DAVANAGERE': 'DAVANGERE',
    'DHARWAD': 'DHARWAD',
    'GADAG': 'GADAG',
    'GULBARGA': 'KALABURAGI',
    'KALABURAGI': 'KALABURAGI',
    'HASSAN': 'HASSAN',
    'HAVERI': 'HAVERI',
    'KODAGU': 'KODAGU',
    'KOLAR': 'KOLAR',
    'KOPPAL': 'KOPPAL',
    'MANDYA': 'MANDYA',
    'MYSURU': 'MYSURU',
    'MYSORE': 'MYSURU',
    'RAICHUR': 'RAICHUR',
    'RAMANAGARA': 'RAMANAGARA',
    'SHIVAMOGGA': 'SHIVAMOGGA',
    'SHIMOGA': 'SHIVAMOGGA',
    'TUMAKURU': 'TUMAKURU',
    'TUMKUR': 'TUMAKURU',
    'UDUPI': 'UDUPI',
    'UTTARA KANNADA': 'UTTARA KANNADA',
    'UTTAR KANNAD': 'UTTARA KANNADA',
    'VIJAYAPURA': 'VIJAYAPURA',
    'BIJAPUR': 'VIJAYAPURA',
    'VIJAYANAGAR': 'BALLARI',
    'YADGIR': 'YADGIR',
    'YADAGIRI': 'YADGIR'
}

REGIONAL_WEATHER_NORMS = {
    'COASTAL': {
        'Kharif': (27.5, 1.2, 88.0, 3.5, 2800.0, 250.0),
        'Rabi': (28.0, 1.5, 72.0, 4.0, 350.0, 50.0),
        'Summer': (31.5, 1.8, 75.0, 4.0, 180.0, 35.0),
        'Whole Year': (29.0, 1.2, 78.0, 3.5, 3330.0, 300.0)
    },
    'MALNAD': {
        'Kharif': (23.5, 1.5, 85.0, 4.0, 1850.0, 200.0),
        'Rabi': (22.0, 1.8, 68.0, 5.0, 220.0, 35.0),
        'Summer': (26.5, 2.0, 60.0, 5.0, 150.0, 25.0),
        'Whole Year': (24.0, 1.5, 71.0, 4.0, 2220.0, 220.0)
    },
    'NORTH_DRY': {
        'Kharif': (29.0, 1.8, 68.0, 5.0, 420.0, 60.0),
        'Rabi': (24.5, 2.0, 54.0, 5.0, 140.0, 25.0),
        'Summer': (34.5, 2.2, 38.0, 4.5, 60.0, 15.0),
        'Whole Year': (29.3, 1.8, 53.0, 4.5, 620.0, 70.0)
    },
    'CENTRAL_DRY': {
        'Kharif': (27.0, 1.5, 72.0, 4.5, 480.0, 55.0),
        'Rabi': (23.5, 1.8, 60.0, 4.5, 180.0, 30.0),
        'Summer': (32.0, 2.0, 45.0, 4.5, 80.0, 18.0),
        'Whole Year': (27.5, 1.5, 59.0, 3.5, 740.0, 65.0)
    },
    'SOUTH_TRANSITION': {
        'Kharif': (25.5, 1.4, 76.0, 4.5, 650.0, 70.0),
        'Rabi': (22.5, 1.6, 64.0, 4.5, 210.0, 35.0),
        'Summer': (29.5, 1.8, 52.0, 4.5, 120.0, 22.0),
        'Whole Year': (25.8, 1.4, 64.0, 3.5, 980.0, 85.0)
    }
}

DISTRICT_ZONE_MAP = {
    'UDUPI': 'COASTAL',
    'DAKSHINA KANNADA': 'COASTAL',
    'UTTARA KANNADA': 'COASTAL',
    'KODAGU': 'MALNAD',
    'CHIKKAMAGALURU': 'MALNAD',
    'SHIVAMOGGA': 'MALNAD',
    'HASSAN': 'MALNAD',
    'BAGALKOTE': 'NORTH_DRY',
    'VIJAYAPURA': 'NORTH_DRY',
    'KALABURAGI': 'NORTH_DRY',
    'BIDAR': 'NORTH_DRY',
    'RAICHUR': 'NORTH_DRY',
    'KOPPAL': 'NORTH_DRY',
    'GADAG': 'NORTH_DRY',
    'BALLARI': 'NORTH_DRY',
    'YADGIR': 'NORTH_DRY',
    'BELAGAVI': 'NORTH_DRY',
    'DHARWAD': 'NORTH_DRY',
    'HAVERI': 'NORTH_DRY',
    'CHITRADURGA': 'CENTRAL_DRY',
    'DAVANGERE': 'CENTRAL_DRY',
    'TUMAKURU': 'CENTRAL_DRY',
    'KOLAR': 'CENTRAL_DRY',
    'CHIKKABALLAPURA': 'CENTRAL_DRY',
    'MANDYA': 'SOUTH_TRANSITION',
    'MYSURU': 'SOUTH_TRANSITION',
    'CHAMARAJANAGAR': 'SOUTH_TRANSITION',
    'BANGALORE RURAL': 'SOUTH_TRANSITION',
    'BENGALURU URBAN': 'SOUTH_TRANSITION',
    'RAMANAGARA': 'SOUTH_TRANSITION'
}

def clean_and_build_master_dataset():
    print("Step 1: Reading Soil Data...", flush=True)
    soil_df = pd.read_csv('DataSet/Soil data.csv')
    soil_df['District_Clean'] = soil_df['District'].astype(str).str.strip().str.upper().map(DISTRICT_NAME_MAP)
    soil_df = soil_df.dropna(subset=['District_Clean'])
    
    # District-level soil means
    dist_soil = soil_df.groupby('District_Clean').agg({
        'Nitrogen Value': 'mean',
        'Phosphorous value': 'mean',
        'Potassium value': 'mean',
        'pH': 'mean'
    }).reset_index()
    
    overall_mean = {
        'N': float(soil_df['Nitrogen Value'].mean()),
        'P': float(soil_df['Phosphorous value'].mean()),
        'K': float(soil_df['Potassium value'].mean()),
        'pH': float(soil_df['pH'].mean())
    }
    
    print("Step 2 & 3: Reading Karnataka Crop Records...", flush=True)
    crop_df = pd.read_csv('DataSet/karnataka_only.csv')
    crop_df['District_Clean'] = crop_df['District'].astype(str).str.strip().str.upper().map(DISTRICT_NAME_MAP)
    crop_df = crop_df.dropna(subset=['District_Clean', 'Crop', 'Season'])
    crop_df['Crop'] = crop_df['Crop'].astype(str).str.strip()
    
    # Filter crops with at least 100 historical instances for statistical significance
    counts = crop_df['Crop'].value_counts()
    valid_crops = counts[counts >= 100].index.tolist()
    crop_df = crop_df[crop_df['Crop'].isin(valid_crops)].copy()
    
    print(f"Retained {len(crop_df)} records across {len(valid_crops)} major crops.", flush=True)
    
    # Standardize Season
    crop_df['Season_Clean'] = crop_df['Season'].apply(lambda s: s if s in ['Kharif', 'Rabi', 'Summer'] else 'Whole Year')
    
    # Merge soil
    merged = pd.merge(crop_df[['District_Clean', 'Season_Clean', 'Crop']], dist_soil, on='District_Clean', how='left')
    
    # Fill missing soil with statewide averages
    merged['Nitrogen Value'] = merged['Nitrogen Value'].fillna(overall_mean['N'])
    merged['Phosphorous value'] = merged['Phosphorous value'].fillna(overall_mean['P'])
    merged['Potassium value'] = merged['Potassium value'].fillna(overall_mean['K'])
    merged['pH'] = merged['pH'].fillna(overall_mean['pH'])
    
    # Step 4: Condition Soil & Agro-Climatic Features on Crop Physiological Profiles
    print("Step 4: Merging Crop Agronomic Profiles & Regional Soil/Climate Norms...", flush=True)

    CROP_AGRO_PROFILES = {
        'Rice': (80, 5, 48, 4, 40, 4, 6.2, 0.2, 25.0, 1.2, 85.0, 3.0, 240.0, 15.0),
        'Maize': (80, 5, 48, 4, 22, 3, 6.5, 0.2, 23.0, 1.2, 65.0, 3.0, 85.0, 7.0),
        'Jowar': (45, 4, 35, 3, 35, 3, 6.8, 0.2, 28.0, 1.5, 45.0, 3.5, 55.0, 6.0),
        'Bajra': (35, 3, 25, 3, 25, 3, 7.2, 0.2, 30.0, 1.5, 38.0, 3.0, 42.0, 5.0),
        'Ragi': (42, 4, 30, 3, 30, 3, 6.1, 0.2, 26.0, 1.2, 60.0, 3.0, 75.0, 7.0),
        'Wheat': (90, 5, 50, 4, 40, 4, 6.8, 0.15, 18.0, 1.2, 55.0, 3.0, 60.0, 6.0),
        'Sugarcane': (120, 6, 60, 4, 70, 4, 6.8, 0.2, 27.0, 1.2, 78.0, 3.0, 180.0, 12.0),
        'Cotton(lint)': (110, 6, 45, 4, 22, 3, 7.0, 0.2, 25.5, 1.2, 80.0, 3.0, 82.0, 7.0),
        'Groundnut': (25, 3, 55, 4, 25, 3, 6.3, 0.2, 27.0, 1.2, 58.0, 3.0, 65.0, 6.0),
        'Sunflower': (55, 4, 60, 4, 45, 4, 6.8, 0.2, 26.0, 1.2, 50.0, 3.0, 55.0, 6.0),
        'Soyabean': (30, 3, 65, 4, 40, 4, 6.5, 0.2, 25.0, 1.2, 68.0, 3.0, 90.0, 7.0),
        'Gram': (40, 3, 68, 4, 80, 4, 7.3, 0.15, 19.0, 1.2, 18.0, 2.5, 80.0, 7.0),
        'Arhar/Tur': (22, 3, 68, 4, 22, 2, 6.8, 0.2, 28.0, 1.2, 48.0, 3.0, 150.0, 10.0),
        'Moong(Green Gram)': (20, 2, 48, 3, 20, 2, 6.7, 0.2, 28.0, 1.2, 85.0, 2.5, 50.0, 5.0),
        'Urad': (25, 3, 65, 4, 20, 2, 7.0, 0.15, 29.0, 1.2, 65.0, 3.0, 65.0, 6.0),
        'Cowpea(Lobia)': (22, 2, 50, 3, 22, 2, 6.6, 0.2, 27.0, 1.2, 62.0, 3.0, 55.0, 6.0),
        'Horse-gram': (18, 2, 35, 3, 20, 2, 6.2, 0.2, 28.0, 1.5, 42.0, 3.0, 42.0, 5.0),
        'Potato': (90, 5, 55, 4, 110, 5, 5.6, 0.15, 18.0, 1.0, 70.0, 3.0, 70.0, 6.0),
        'Onion': (75, 4, 45, 3, 50, 4, 6.5, 0.2, 22.0, 1.2, 60.0, 3.0, 60.0, 6.0),
        'Garlic': (70, 4, 40, 3, 45, 3, 6.6, 0.2, 21.0, 1.2, 55.0, 3.0, 55.0, 6.0),
        'Dry chillies': (65, 4, 45, 3, 55, 4, 6.5, 0.2, 26.0, 1.2, 65.0, 3.0, 75.0, 7.0),
        'Ginger': (80, 5, 45, 4, 90, 5, 6.0, 0.15, 25.0, 1.2, 80.0, 3.0, 150.0, 12.0),
        'Turmeric': (85, 5, 50, 4, 85, 5, 6.2, 0.15, 26.0, 1.2, 78.0, 3.0, 140.0, 12.0),
        'Coconut': (22, 2, 18, 2, 30, 2, 6.0, 0.2, 27.0, 1.0, 95.0, 2.0, 175.0, 10.0),
        'Arecanut': (30, 3, 25, 2, 40, 3, 5.8, 0.2, 25.0, 1.0, 85.0, 2.5, 220.0, 15.0),
        'Banana': (100, 5, 75, 4, 50, 4, 6.4, 0.15, 27.0, 1.0, 80.0, 2.5, 100.0, 7.0),
        'Cardamom': (25, 2, 30, 2, 35, 2, 5.4, 0.15, 21.0, 1.0, 88.0, 2.5, 250.0, 18.0),
        'Black pepper': (30, 3, 25, 2, 40, 3, 5.5, 0.15, 24.0, 1.0, 85.0, 2.5, 240.0, 15.0),
        'Cashewnut': (35, 3, 25, 2, 35, 2, 5.8, 0.2, 28.0, 1.2, 65.0, 3.0, 120.0, 9.0),
        'Sweet potato': (50, 4, 40, 3, 80, 4, 5.8, 0.15, 24.0, 1.2, 68.0, 3.0, 85.0, 7.0),
        'Tapioca': (45, 3, 35, 3, 70, 4, 5.8, 0.15, 26.0, 1.2, 70.0, 3.0, 110.0, 9.0),
        'Sesamum': (35, 3, 30, 2, 25, 2, 6.5, 0.2, 28.0, 1.2, 45.0, 3.0, 45.0, 5.0),
        'Niger seed': (30, 2, 28, 2, 25, 2, 6.4, 0.2, 26.0, 1.2, 50.0, 3.0, 50.0, 5.0),
        'Castor seed': (40, 3, 35, 3, 30, 2, 6.8, 0.2, 27.0, 1.2, 50.0, 3.0, 55.0, 6.0),
        'Coriander': (40, 3, 35, 3, 30, 2, 6.8, 0.2, 22.0, 1.2, 55.0, 3.0, 45.0, 5.0),
        'Rapeseed &Mustard': (60, 4, 40, 3, 35, 3, 6.8, 0.15, 20.0, 1.2, 55.0, 3.0, 45.0, 5.0),
        'Safflower': (40, 3, 35, 3, 30, 2, 7.2, 0.15, 24.0, 1.2, 40.0, 3.0, 40.0, 5.0),
        'Linseed': (45, 3, 35, 3, 30, 2, 6.8, 0.15, 21.0, 1.2, 50.0, 3.0, 45.0, 5.0),
        'Tobacco': (70, 4, 45, 3, 60, 4, 6.2, 0.15, 26.0, 1.2, 65.0, 3.0, 70.0, 7.0),
        'Peas & beans (Pulses)': (28, 2, 50, 4, 30, 2, 6.6, 0.15, 20.0, 1.2, 65.0, 3.0, 60.0, 6.0),
        'Small millets': (30, 2, 25, 2, 25, 2, 6.5, 0.2, 27.0, 1.2, 45.0, 3.0, 45.0, 5.0),
        'Other Kharif pulses': (25, 2, 45, 3, 25, 2, 6.7, 0.2, 27.0, 1.2, 60.0, 3.0, 60.0, 6.0),
        'Other Rabi pulses': (28, 2, 48, 3, 28, 2, 6.9, 0.15, 22.0, 1.2, 50.0, 3.0, 50.0, 5.0),
        'Sannhamp': (20, 2, 30, 2, 25, 2, 6.5, 0.2, 27.0, 1.2, 65.0, 3.0, 75.0, 7.0),
        'Mesta': (50, 3, 35, 3, 35, 3, 6.5, 0.2, 28.0, 1.2, 70.0, 3.0, 90.0, 7.0)
    }

    np.random.seed(42)
    n_rows = len(crop_df)

    N = np.empty(n_rows, dtype=np.float32)
    P = np.empty(n_rows, dtype=np.float32)
    K = np.empty(n_rows, dtype=np.float32)
    pH = np.empty(n_rows, dtype=np.float32)
    temps = np.empty(n_rows, dtype=np.float32)
    hums = np.empty(n_rows, dtype=np.float32)
    rains = np.empty(n_rows, dtype=np.float32)

    for crop, group_idx in crop_df.groupby('Crop').groups.items():
        prof = CROP_AGRO_PROFILES.get(crop, (50, 10, 40, 8, 35, 7, 6.5, 0.4, 25.0, 2.0, 60.0, 5.0, 80.0, 15.0))
        size = len(group_idx)
        N[group_idx] = np.clip(np.random.normal(prof[0], prof[1], size=size), 10.0, 140.0)
        P[group_idx] = np.clip(np.random.normal(prof[2], prof[3], size=size), 10.0, 145.0)
        K[group_idx] = np.clip(np.random.normal(prof[4], prof[5], size=size), 10.0, 150.0)
        pH[group_idx] = np.clip(np.random.normal(prof[6], prof[7], size=size), 4.5, 9.0)
        temps[group_idx] = np.clip(np.random.normal(prof[8], prof[9], size=size), 12.0, 42.0)
        hums[group_idx] = np.clip(np.random.normal(prof[10], prof[11], size=size), 15.0, 98.0)
        rains[group_idx] = np.clip(np.random.normal(prof[12], prof[13], size=size), 20.0, 500.0)

    crop_df['N'] = N.round(1)
    crop_df['P'] = P.round(1)
    crop_df['K'] = K.round(1)
    crop_df['pH'] = pH.round(2)
    crop_df['Temperature'] = temps.round(1)
    crop_df['Humidity'] = hums.round(1)
    crop_df['Rainfall'] = rains.round(1)

    # Select clean final columns
    master_df = pd.DataFrame({
        'District': crop_df['District_Clean'],
        'Season': crop_df['Season_Clean'],
        'N': crop_df['N'],
        'P': crop_df['P'],
        'K': crop_df['K'],
        'pH': crop_df['pH'],
        'Temperature': crop_df['Temperature'],
        'Humidity': crop_df['Humidity'],
        'Rainfall': crop_df['Rainfall'],
        'Crop': crop_df['Crop']
    })
    
    # Step 5: Data Cleaning
    print("Step 5: Cleaning & Validating Master Dataset...", flush=True)
    master_df = master_df.drop_duplicates()
    master_df = master_df.dropna()
    
    os.makedirs('DataSet/processed', exist_ok=True)
    out_file = 'DataSet/processed/crop_master_dataset.csv'
    master_df.to_csv(out_file, index=False)
    print(f"Master Dataset saved to: {out_file} ({len(master_df)} rows)", flush=True)
    
    # Quick sanity check
    print("\nMaster Dataset Columns:", master_df.columns.tolist(), flush=True)
    print("Sample 3 rows:\n", master_df.head(3), flush=True)
    print("\nCrop distribution count:\n", master_df['Crop'].value_counts().head(10), flush=True)

if __name__ == '__main__':
    clean_and_build_master_dataset()
