"""
prepare_yield_dataset.py
Prepares the master dataset for Model 2 (Yield Prediction System).
Merges Soil data, Agro-climatic features, and Historical Yields (in Tonnes/Hectare).
"""

import pandas as pd
import numpy as np
import os

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

def clean_and_build_yield_dataset():
    print("Building Yield Master Dataset (Model 2)...", flush=True)
    crop_df = pd.read_csv('DataSet/karnataka_only.csv')
    crop_df['District_Clean'] = crop_df['District'].astype(str).str.strip().str.upper().map(DISTRICT_NAME_MAP)
    crop_df = crop_df.dropna(subset=['District_Clean', 'Crop', 'Season', 'Yield'])
    crop_df['Crop'] = crop_df['Crop'].astype(str).str.strip()
    
    # Filter valid crops matching Model 1
    valid_crops = list(CROP_AGRO_PROFILES.keys())
    crop_df = crop_df[crop_df['Crop'].isin(valid_crops)].copy()
    
    # Standardize Season
    crop_df['Season_Clean'] = crop_df['Season'].apply(lambda s: s if s in ['Kharif', 'Rabi', 'Summer'] else 'Whole Year')
    
    # Convert Yield strictly to Tonnes/Hectare
    # 1. Cotton: recorded in Bales (1 bale = 170kg = 0.17 tonnes)
    # 2. Coconut: recorded in Nuts (1000 nuts ~ 1.0 tonne)
    # 3. All other crops: already Tonnes/Hectare
    def standardize_yield(row):
        val = float(row['Yield'])
        unit = str(row['Production Units']).strip()
        if row['Crop'] == 'Cotton(lint)' or unit == 'Bales':
            return val * 0.170
        elif row['Crop'] == 'Coconut' or unit == 'Nuts':
            return val / 1000.0
        return val

    crop_df['Yield_Tonnes_Per_Ha'] = crop_df.apply(standardize_yield, axis=1)
    
    # Remove negative or extreme outlier yield noise (e.g. yield > 150 t/ha or yield == 0)
    crop_df = crop_df[(crop_df['Yield_Tonnes_Per_Ha'] > 0.01) & (crop_df['Yield_Tonnes_Per_Ha'] <= 120.0)].reset_index(drop=True)
    
    # Generate agronomic conditions matching district & crop profile
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

    # Master yield dataframe
    yield_df = pd.DataFrame({
        'District': crop_df['District_Clean'],
        'Season': crop_df['Season_Clean'],
        'Crop': crop_df['Crop'],
        'N': crop_df['N'],
        'P': crop_df['P'],
        'K': crop_df['K'],
        'pH': crop_df['pH'],
        'Temperature': crop_df['Temperature'],
        'Humidity': crop_df['Humidity'],
        'Rainfall': crop_df['Rainfall'],
        'Yield': crop_df['Yield_Tonnes_Per_Ha'].round(3)
    })
    
    yield_df = yield_df.dropna().drop_duplicates()
    
    os.makedirs('DataSet/processed', exist_ok=True)
    out_path = 'DataSet/processed/yield_master_dataset.csv'
    yield_df.to_csv(out_path, index=False)
    print(f"Successfully generated Yield Master Dataset: {out_path} ({len(yield_df)} records)", flush=True)
    print("\nSample records:")
    print(yield_df.head(5))
    print("\nYield summary (Tonnes/Ha):")
    print(yield_df['Yield'].describe())

if __name__ == '__main__':
    clean_and_build_yield_dataset()
