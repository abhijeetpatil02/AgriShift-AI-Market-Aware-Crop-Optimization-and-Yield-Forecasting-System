# AgriShift: AI Market-Aware Crop Optimization & Yield Forecasting System   
 
An intelligent, agro-climatic crop recommendation system tailored for Karnataka farmers and agricultural stakeholders. The system evaluates soil health ($N, P, K, \text{pH}$), historical seasonal patterns, and real-time weather data to recommend the **Top 3 Best Compatible Crops** with probability match meters, expected yield benchmarks, and actionable agronomic advice. 

---

## 🌾 System Architecture & 10-Step Workflow 

```mermaid
flowchart TD
    S1["1. Soil Data (Soil data.csv)<br>District-level N, P, K, pH profiles"] --> S4["4. Master Integration<br>[District, Season, N, P, K, pH, Temp, Rain, Hum, Crop]"]
    S2["2. Weather Data (Historical & Live)<br>Agro-climatic seasonal norms + WeatherAPI"] --> S4
    S3["3. Historical Crop Data (karnataka_only.csv)<br>27,493 historical records across Karnataka"] --> S4
    S4 --> S5["5. Data Cleaning & Validation<br>Outlier clipping, bounds checking, unit checks"]
    S5 --> S6["6. Exploratory Data Analysis (EDA)<br>Crop frequencies, pH ranges, rainfall profiles"]
    S6 --> S7["7. Train/Test Stratified Split (80/20)"]
    S7 --> S8["8. Multi-Model Training<br>Random Forest Classifier & XGBoost"]
    S8 --> S9["9. Evaluation & Benchmarking<br>Top-1, Top-3 Probability Accuracy, F1-Score"]
    S9 --> S10["10. Interactive Web Application<br>Flask Backend + Dynamic Podium UI"]
```

---

## 📊 Dataset Overview

| Dataset Source | Records / Coverage | Key Attributes |
| :--- | :--- | :--- |
| **`Soil data.csv`** | 875 samples, 101 districts | Nitrogen ($N$), Phosphorus ($P$), Potassium ($K$), Soil $\text{pH}$ |
| **`karnataka_only.csv`** | 27,493 records (1997–2020) | District, Season, Crop, Production, Area, Yield (Tonnes/Ha) |
| **WeatherAPI.com** | Live real-time & seasonal norms | Live Temperature (°C), Humidity (%), Precipitation (mm) |

---

## 🚀 How to Run the Application

### 1. Requirements
Ensure Python is installed along with the dependencies:
```bash
pip install flask flask-cors scikit-learn pandas numpy xgboost joblib
```

### 2. (Optional) Re-run Data Preprocessing & Model Training
To regenerate the master dataset and re-train the models:
```bash
python prepare_master_dataset.py
python train_crop_model.py
```

### 3. Launch the Web Application
```bash
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🎯 Key Features

1. **Farmer Authentication & Separation of Concerns**:
   - Clean, professional login and signup system (`/login`, `/signup`) tailored specifically for farmers and agricultural professionals.
   - Strict separation between account security (credentials, user role, preferred language) and farm soil/crop data (configured independently in the dashboard).
   - MySQL database integration (via `PyMySQL`) with automatic schema initialization and resilient SQLite fallback.
2. **Top 3 Ranked Recommendations**:
   - 🥇 **#1 Primary Crop**: Highest compatibility score with expected yield in Tonnes/Hectare.
   - 🥈 **#2 Alternative Crop**: Viable backup option with comparative advantages.
   - 🥉 **#3 Alternative Crop**: Diversification option for crop rotation or risk mitigation.
3. **Saved Prediction History**:
   - Farmers can save their seasonal ML recommendations and APMC Mandi revenue forecasts directly to their account history (`/api/history`).
4. **Auto-Fill from District Soil & Weather**:
   - Selecting a Karnataka district automatically fetches live weather (via WeatherAPI) and pre-populates typical local soil nutrient levels.
5. **Multi-Language Advisory**:
   - Bilingually localized in English and ಕನ್ನಡ (Kannada) with seamless language selection.
6. **Fertilizer & Soil Conditioning Tips**:
   - Provides targeted guidance on nutrient deficiencies (e.g., lime for acidic soils, urea top-dressing for low nitrogen).

---

## 🔐 MySQL Configuration

AgriShift connects to MySQL automatically. To specify your local MySQL credentials, create a `.env` file or export environment variables:
```bash
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=agrishift_db
SECRET_KEY=your_secret_key
```
*(If MySQL credentials are not yet supplied, AgriShift automatically uses an integrated SQLite database fallback so development and testing never stall.)*
