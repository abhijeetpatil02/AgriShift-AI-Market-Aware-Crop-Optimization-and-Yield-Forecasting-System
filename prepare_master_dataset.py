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
    
    # Vectorized weather assignment
    np.random.seed(42)
    n_rows = len(merged)
    
    merged['Zone'] = merged['District_Clean'].map(lambda d: DISTRICT_ZONE_MAP.get(d, 'CENTRAL_DRY'))
    
    temps = np.empty(n_rows, dtype=np.float32)
    hums = np.empty(n_rows, dtype=np.float32)
    rains = np.empty(n_rows, dtype=np.float32)
    
    # Group by Zone & Season to vectorize random draws
    for (zone, season), group_idx in merged.groupby(['Zone', 'Season_Clean']).groups.items():
        w_norm = REGIONAL_WEATHER_NORMS[zone][season]
        size = len(group_idx)
        temps[group_idx] = np.random.normal(w_norm[0], w_norm[1], size=size)
        hums[group_idx] = np.clip(np.random.normal(w_norm[2], w_norm[3], size=size), 20.0, 98.0)
        rains[group_idx] = np.clip(np.random.normal(w_norm[4], w_norm[5], size=size), 15.0, 4500.0)
        
    # Add slight natural soil variation per field
    merged['N'] = np.clip(np.random.normal(merged['Nitrogen Value'], 3.0), 10.0, 140.0).round(2)
    merged['P'] = np.clip(np.random.normal(merged['Phosphorous value'], 4.0), 10.0, 145.0).round(2)
    merged['K'] = np.clip(np.random.normal(merged['Potassium value'], 4.0), 10.0, 150.0).round(2)
    merged['pH'] = np.clip(np.random.normal(merged['pH'], 0.15), 4.5, 9.5).round(2)
    merged['Temperature'] = temps.round(1)
    merged['Humidity'] = hums.round(1)
    merged['Rainfall'] = rains.round(1)
    
    # Rename & select final columns
    master_df = merged.rename(columns={'District_Clean': 'District', 'Season_Clean': 'Season'})[
        ['District', 'Season', 'N', 'P', 'K', 'pH', 'Temperature', 'Humidity', 'Rainfall', 'Crop']
    ]
    
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
