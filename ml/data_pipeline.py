"""
AgriShift Data Pipeline
Merges soil, climate, yield, cost, and price datasets into standardized processed formats.
"""

import os
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = os.path.join(BASE_DIR, "DataSet")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

def build_master_dataset():
    """Merge yield, soil, climate, and cultivation cost datasets."""
    print("Building master dataset...")
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    yield_path = os.path.join(DATASET_DIR, "crop_yield_sample_dataset.csv")
    soil_path = os.path.join(DATASET_DIR, "soil_health_sample_dataset.csv")
    clim_path = os.path.join(DATASET_DIR, "climate_seasonal_sample_dataset.csv")
    cost_path = os.path.join(DATASET_DIR, "cost_of_cultivation_sample_dataset.csv")

    yield_df = pd.read_csv(yield_path)
    soil_df = pd.read_csv(soil_path).rename(columns={"Sample_Year": "Crop_Year"})
    clim_df = pd.read_csv(clim_path)
    cost_df = pd.read_csv(cost_path)

    # 1. Merge yield with soil
    df = pd.merge(yield_df, soil_df, on=["State", "District", "Crop_Year"], how="inner")

    # 2. Merge with seasonal climate
    df = pd.merge(df, clim_df, on=["State", "District", "Crop_Year", "Season"], how="inner")

    # 3. Merge with cost of cultivation
    df = pd.merge(df, cost_df, on=["State", "Crop", "Crop_Year"], how="inner")

    # Feature additions
    df["Yield_Tonnes_per_ha"] = df["Yield_kg_per_ha"] / 1000.0

    master_path = os.path.join(PROCESSED_DIR, "master_dataset.csv")
    df.to_csv(master_path, index=False)
    print(f"Master dataset saved: {master_path} (shape: {df.shape})")
    return df

def build_price_dataset():
    """Aggregate market Mandi price data into monthly & summary statistics per crop."""
    print("Processing market price data...")
    price_path = os.path.join(DATASET_DIR, "market_price_supply_sample_dataset.csv")
    price_df = pd.read_csv(price_path)
    price_df["Date"] = pd.to_datetime(price_df["Date"])
    price_df["Year"] = price_df["Date"].dt.year
    price_df["Month"] = price_df["Date"].dt.month

    # Monthly aggregation
    monthly = price_df.groupby(["Commodity", "State", "Year", "Month"]).agg({
        "Modal_Price_Rs_per_Quintal": ["mean", "min", "max", "std"],
        "Arrivals_Tonnes": "sum"
    }).reset_index()

    monthly.columns = [
        "Crop", "State", "Year", "Month",
        "Price_Modal_Mean", "Price_Min", "Price_Max", "Price_Std", "Arrivals_Total"
    ]
    monthly_path = os.path.join(PROCESSED_DIR, "crop_price_monthly.csv")
    monthly.to_csv(monthly_path, index=False)

    # Crop level overall summary (for baseline price and volatility)
    summary = price_df.groupby("Commodity").agg({
        "Modal_Price_Rs_per_Quintal": ["mean", "std", "min", "max", "median"],
        "Arrivals_Tonnes": ["mean", "sum"]
    }).reset_index()

    summary.columns = [
        "Crop", "Price_Mean_Rs_Quintal", "Price_Std_Rs_Quintal",
        "Price_Min_Rs_Quintal", "Price_Max_Rs_Quintal", "Price_Median_Rs_Quintal",
        "Arrivals_Mean_Tonnes", "Arrivals_Total_Tonnes"
    ]
    # Price per tonne = price per quintal * 10
    summary["Price_Mean_Rs_Tonne"] = summary["Price_Mean_Rs_Quintal"] * 10.0
    summary["Volatility_Coeff"] = summary["Price_Std_Rs_Quintal"] / summary["Price_Mean_Rs_Quintal"]

    summary_path = os.path.join(PROCESSED_DIR, "crop_price_summary.csv")
    summary.to_csv(summary_path, index=False)
    print(f"Price datasets saved: {monthly_path} and {summary_path}")
    return monthly, summary

def copy_transition_matrix():
    """Copy and verify crop transition matrix."""
    src = os.path.join(DATASET_DIR, "crop_transition_cost_matrix.csv")
    dst = os.path.join(PROCESSED_DIR, "crop_transition_matrix.csv")
    df = pd.read_csv(src)
    df.to_csv(dst, index=False)
    print(f"Transition matrix saved: {dst} ({len(df)} pairs)")
    return df

def build_district_crop_directory(master_df):
    """
    Builds a comprehensive directory of all districts and crops grown in each district,
    including historical yields, area, and seasonal suitability.
    """
    print("Building district & crop directory...")
    # Group by State, District, Crop
    grouped = master_df.groupby(["State", "District", "Crop"]).agg({
        "Yield_kg_per_ha": ["mean", "min", "max"],
        "Yield_Tonnes_per_ha": "mean",
        "Area_Hectares": "mean",
        "Production_Tonnes": "sum",
        "Season": lambda s: ", ".join(sorted(list(set(s))))
    }).reset_index()

    grouped.columns = [
        "State", "District", "Crop",
        "Avg_Yield_kg_ha", "Min_Yield_kg_ha", "Max_Yield_kg_ha",
        "Avg_Yield_t_ha", "Avg_Area_ha", "Total_Production_Tonnes", "Seasons"
    ]
    grouped["Avg_Yield_kg_ha"] = grouped["Avg_Yield_kg_ha"].round(1)
    grouped["Avg_Yield_t_ha"] = grouped["Avg_Yield_t_ha"].round(2)
    grouped["Avg_Area_ha"] = grouped["Avg_Area_ha"].round(1)
    grouped["Total_Production_Tonnes"] = grouped["Total_Production_Tonnes"].round(1)

    dir_csv_path = os.path.join(PROCESSED_DIR, "district_crop_directory.csv")
    grouped.to_csv(dir_csv_path, index=False)

    # Build nested JSON lookup: { State: { District: [ { crop, avg_yield_t_ha, seasons, ... } ] } }
    import json
    lookup = {}
    for _, row in grouped.iterrows():
        st = row["State"]
        dist = row["District"]
        c = row["Crop"]
        if st not in lookup:
            lookup[st] = {}
        if dist not in lookup[st]:
            lookup[st][dist] = []
        lookup[st][dist].append({
            "crop": c,
            "avg_yield_t_ha": float(row["Avg_Yield_t_ha"]),
            "avg_yield_kg_ha": float(row["Avg_Yield_kg_ha"]),
            "seasons": row["Seasons"],
            "avg_area_ha": float(row["Avg_Area_ha"]),
            "total_production_t": float(row["Total_Production_Tonnes"])
        })

    lookup_path = os.path.join(PROCESSED_DIR, "district_crops_lookup.json")
    with open(lookup_path, "w") as f:
        json.dump(lookup, f, indent=2)

    print(f"District crop directory saved: {dir_csv_path} and {lookup_path}")
    return grouped, lookup

def run_pipeline():
    master_df = build_master_dataset()
    monthly_price, price_summary = build_price_dataset()
    trans_matrix = copy_transition_matrix()
    dist_crop_df, dist_crop_lookup = build_district_crop_directory(master_df)
    print("Data pipeline executed successfully!")
    return {
        "master_rows": len(master_df),
        "crops": list(master_df["Crop"].unique()),
        "states": list(master_df["State"].unique()),
        "districts": list(master_df["District"].unique()),
        "districts_count": len(dist_crop_lookup)
    }

if __name__ == "__main__":
    run_pipeline()
