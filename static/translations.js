/**
 * AgriShift — Multi-Language Translation System (English & Kannada)
 * High-accuracy localization layer decoupled from ML models.
 */

const TRANSLATIONS = {
    en: {
        // Header & Branding
        brand_name: "AgriShift",
        brand_badge: "AI Advisor",
        brand_tagline: "Market-Aware & Soil-Specific Crop Optimization System",
        header_status: "WeatherAPI & Karnataka Soil Model Active",

        // Hero Section
        hero_title_prefix: "Recommend the",
        hero_title_highlight: "Top 3 Best Crops",
        hero_title_suffix: "For Your Soil & Land",
        hero_desc: "Select your Karnataka district and season to auto-fetch soil health and live weather, or customize the parameters manually to receive your personalized crop recommendations.",

        // Presets Bar
        preset_label: "Quick Presets:",
        preset_dharwad: "📍 Dharwad (Kharif)",
        preset_belagavi: "📍 Belagavi (Rabi)",
        preset_mandya: "📍 Mandya (Sugarcane/Paddy Zone)",
        preset_udupi: "📍 Udupi (Coastal Wet)",
        preset_vijayapura: "📍 Vijayapura (Dry Jowar Zone)",

        // Form - Step 1: Location & Season
        step1_badge: "Step 1",
        step1_title: "Location & Season",
        label_district: "District in Karnataka",
        label_season: "Farming Season",
        season_kharif: "🌧️ Kharif (Monsoon)",
        season_rabi: "❄️ Rabi (Winter)",
        season_summer: "☀️ Summer",
        season_whole_year: "📅 Whole Year",
        label_farm_area: "Farm Land Size",
        unit_hectares: "Hectares",
        area_hint: "💡 1 Hectare ≈ 2.47 Acres",
        btn_autofetch: "⚡ Auto-Fetch Live Weather & Soil",
        btn_autofetch_loading: "⏳ Fetching Live Data...",
        weather_condition_prefix: "Condition:",
        weather_live_prefix: "Live Weather:",

        // Form - Step 2: Soil Nutrients
        step2_badge: "Step 2",
        step2_title: "Soil Nutrients & pH",
        label_nitrogen: "Nitrogen (N)",
        label_phosphorus: "Phosphorus (P)",
        label_potassium: "Potassium (K)",
        label_ph: "Soil pH Level",
        unit_kgha: "kg/ha",

        // Form - Step 3: Climate & Weather
        step3_badge: "Step 3",
        step3_title: "Climate & Weather",
        label_temperature: "Average Temperature",
        label_humidity: "Relative Humidity",
        label_rainfall: "Seasonal Rainfall",
        unit_celsius: "°C",
        unit_percent: "%",
        unit_mm: "mm",

        // CTA Button
        btn_predict: "🌾 Run Crop & Yield AI Analysis",
        btn_predict_loading: "Analyzing Soil & Agro-Climatic Model...",

        // Results Section
        badge_model1: "🤖 Model 1: Crop Suitability",
        badge_model2: "🌾 Model 2: Yield Forecast (XGBoost R²=0.94)",
        badge_model3: "📈 APMC Mandi Market Economics",
        results_heading: "Top 3 Recommended Crops & Yield Forecasts",
        results_summary_template: "Analyzed {district} for {season} season across {area} Hectares based on {soil}",

        // Cards Podium
        rank_1: "🥇 #1 Top Recommendation",
        rank_2: "🥈 #2 Viable Alternative",
        rank_3: "🥉 #3 Viable Alternative",
        card_suitability_label: "Agronomic Compatibility",
        card_predicted_yield_title: "🌾 Model 2: AI Yield Forecast",
        card_unit_tonnes_ha: "Tonnes / Hectare",
        card_unit_total_harvest: "Total Harvest ({area} Ha)",
        card_market_title: "📈 APMC Market Economics",
        card_mandi_price_label: "Mandi Price:",
        card_gross_rev_label: "Gross Revenue:",
        card_net_profit_label: "Est. Net Profit:",
        card_water_req: "Water Requirement:",
        card_duration: "Growing Duration:",
        card_soil: "Ideal Soil:",
        per_qtl: "/ qtl",

        // Decision Matrix Table
        matrix_badge: "Decision Matrix",
        matrix_title: "💰 Side-by-Side Harvest & Revenue Comparison",
        th_rank_crop: "Rank & Crop",
        th_match: "Model 1 Match",
        th_yield: "Model 2 Yield (t/ha)",
        th_total_harvest: "Total Harvest",
        th_mandi_rate: "Mandi Rate (₹/qtl)",
        th_gross_rev: "Gross Revenue (₹)",
        th_net_profit: "Est. Net Profit (₹)",
        tonnes_label: "Tonnes",
        qtl_label: "qtl",

        // Soil & Irrigation Guidance
        guidance_soil_title: "🧪 Soil Health & Fertilizer Advice",
        guidance_water_title: "💧 Water & Irrigation Blueprint",
        guidance_water_text: "Based on your climate profile, ensure proper drainage during heavy showers and drip irrigation during drier cycles.",

        // Footer
        footer_text: "AgriShift AI Crop Recommendation System • Trained on Karnataka Agricultural Records & Soil Data"
    },

    kn: {
        // Header & Branding
        brand_name: "ಅಗ್ರಿಶಿಫ್ಟ್ (AgriShift)",
        brand_badge: "ಎಐ ಕೃಷಿ ಸಲಹೆಗಾರ",
        brand_tagline: "ಕರ್ನಾಟಕದ ಮಣ್ಣು ಮತ್ತು ಮಾರುಕಟ್ಟೆ ಆಧಾರಿತ ಬೆಳೆ ನಿರ್ಧಾರ ವ್ಯವಸ್ಥೆ",
        header_status: "ವೆದರ್‌ಎಪಿಐ ಮತ್ತು ಮಣ್ಣಿನ ಮಾದರಿ ಸಕ್ರಿಯವಾಗಿದೆ",

        // Hero Section
        hero_title_prefix: "ನಿಮ್ಮ ಭೂಮಿ ಮತ್ತು ಮಣ್ಣಿಗೆ",
        hero_title_highlight: "ಅತ್ಯುತ್ತಮ 3 ಬೆಳೆಗಳ",
        hero_title_suffix: "ಕೃತಕ ಬುದ್ಧಿಮತ್ತೆ ಶಿಫಾರಸು",
        hero_desc: "ನಿಮ್ಮ ಕರ್ನಾಟಕ ಜಿಲ್ಲೆ ಮತ್ತು ಋತುವನ್ನು ಆಯ್ಕೆ ಮಾಡಿ ಮಣ್ಣಿನ ಗುಣ ಹಾಗೂ ಹವಾಮಾನವನ್ನು ಪಡೆಯಿರಿ, ಅಥವಾ ವೈಯಕ್ತಿಕ ಬೆಳೆ ಶಿಫಾರಸುಗಳನ್ನು ಪಡೆಯಲು ವಿವರಗಳನ್ನು ನಮೂದಿಸಿ.",

        // Presets Bar
        preset_label: "ತ್ವರಿತ ಜಿಲ್ಲಾ ಆಯ್ಕೆಗಳು:",
        preset_dharwad: "📍 ಧಾರವಾಡ (ಮುಂಗಾರು)",
        preset_belagavi: "📍 ಬೆಳಗಾವಿ (ಹಿಂಗಾರು)",
        preset_mandya: "📍 ಮಂಡ್ಯ (ಕಬ್ಬು/ಭತ್ತ ವಲಯ)",
        preset_udupi: "📍 ಉಡುಪಿ (ಕರಾವಳಿ ಮಳೆ ವಲಯ)",
        preset_vijayapura: "📍 ವಿಜಯಪುರ (ಒಣ ಜೋಳ ವಲಯ)",

        // Form - Step 1: Location & Season
        step1_badge: "ಹಂತ ೧",
        step1_title: "ಸ್ಥಳ ಮತ್ತು ಕೃಷಿ ಋತು",
        label_district: "ಕರ್ನಾಟಕದ ಜಿಲ್ಲೆ",
        label_season: "ಕೃಷಿ ಋತು (ಸೀಸನ್)",
        season_kharif: "🌧️ ಖಾರೀಫ್ (ಮುಂಗಾರು)",
        season_rabi: "❄️ ರಬಿ (ಹಿಂಗಾರು)",
        season_summer: "☀️ ಬೇಸಿಗೆ (Summer)",
        season_whole_year: "📅 ವರ್ಷಪೂರ್ತಿ (Whole Year)",
        label_farm_area: "ಜಮೀನಿನ ವಿಸ್ತೀರ್ಣ",
        unit_hectares: "ಹೆಕ್ಟೇರ್",
        area_hint: "💡 ೧ ಹೆಕ್ಟೇರ್ ≈ ೨.೪೭ ಎಕರೆ",
        btn_autofetch: "⚡ ನೇರ ಹವಾಮಾನ & ಮಣ್ಣಿನ ಮಾಹಿತಿ ಪಡೆಯಿರಿ",
        btn_autofetch_loading: "⏳ ನೇರ ಮಾಹಿತಿ ಪಡೆಯಲಾಗುತ್ತಿದೆ...",
        weather_condition_prefix: "ಹವಾಮಾನ ಸ್ಥಿತಿ:",
        weather_live_prefix: "ಲೈವ್ ಹವಾಮಾನ:",

        // Form - Step 2: Soil Nutrients
        step2_badge: "ಹಂತ ೨",
        step2_title: "ಮಣ್ಣಿನ ಪೋಷಕಾಂಶಗಳು ಮತ್ತು ಪಿ.ಹೆಚ್",
        label_nitrogen: "ಸಾರಜನಕ / ನೈಟ್ರೋಜನ್ (N)",
        label_phosphorus: "ರಂಜಕ / ಫಾಸ್ಫರಸ್ (P)",
        label_potassium: "ಪೊಟ್ಯಾಶ್ (K)",
        label_ph: "ಮಣ್ಣಿನ ಪಿ.ಹೆಚ್ (pH) ಮಟ್ಟ",
        unit_kgha: "ಕಿ.ಗ್ರಾಂ/ಹೆಕ್ಟೇರ್",

        // Form - Step 3: Climate & Weather
        step3_badge: "ಹಂತ ೩",
        step3_title: "ಹವಾಮಾನ ಮತ್ತು ಮಳೆ",
        label_temperature: "ಸರಾಸರಿ ಉಷ್ಣಾಂಶ",
        label_humidity: "ಗಾಳಿಯ ತೇವಾಂಶ (ಆರ್ದ್ರತೆ)",
        label_rainfall: "ಋತುವಿನ ಸರಾಸರಿ ಮಳೆ",
        unit_celsius: "°C",
        unit_percent: "%",
        unit_mm: "ಮಿ.ಮೀ",

        // CTA Button
        btn_predict: "🌾 ಬೆಳೆ ಮತ್ತು ಇಳುವರಿ ಎಐ ವಿಶ್ಲೇಷಣೆ ನಡೆಸಿ",
        btn_predict_loading: "ಮಣ್ಣು ಮತ್ತು ಕೃಷಿ-ಹವಾಮಾನ ಮಾದರಿಯ ವಿಶ್ಲೇಷಣೆ ನಡೆಯುತ್ತಿದೆ...",

        // Results Section
        badge_model1: "🤖 ಮಾದರಿ ೧: ಬೆಳೆ ಸೂಕ್ತತೆ (Crop Suitability)",
        badge_model2: "🌾 ಮಾದರಿ ೨: ಇಳುವರಿ ಮುನ್ಸೂಚನೆ (XGBoost R²=0.94)",
        badge_model3: "📈 ಎಪಿಎಂಸಿ ಮಾರುಕಟ್ಟೆ ಆರ್ಥಿಕತೆ",
        results_heading: "ಟಾಪ್ 3 ಶಿಫಾರಸು ಮಾಡಿದ ಬೆಳೆಗಳು & ಇಳುವರಿ ಮುನ್ಸೂಚನೆ",
        results_summary_template: "{district} ಜಿಲ್ಲೆಯ {season} ಋತುವಿನಲ್ಲಿ {area} ಹೆಕ್ಟೇರ್ ಜಮೀನಿಗೆ ({soil}) ವಿಶ್ಲೇಷಣೆ ನಡೆಸಲಾಗಿದೆ",

        // Cards Podium
        rank_1: "🥇 #೧ ಪ್ರಮುಖ ಶಿಫಾರಸು",
        rank_2: "🥈 #೨ ಪರ್ಯಾಯ ಬೆಳೆ",
        rank_3: "🥉 #೩ ಪರ್ಯಾಯ ಬೆಳೆ",
        card_suitability_label: "ಕೃಷಿ ಹೊಂದಾಣಿಕೆ (Agronomic Compatibility)",
        card_predicted_yield_title: "🌾 ಮಾದರಿ ೨: ಎಐ ಇಳುವರಿ ಮುನ್ಸೂಚನೆ",
        card_unit_tonnes_ha: "ಟನ್ / ಹೆಕ್ಟೇರ್",
        card_unit_total_harvest: "ಒಟ್ಟು ಇಳುವರಿ ({area} ಹೆಕ್ಟೇರ್)",
        card_market_title: "📈 ಎಪಿಎಂಸಿ ಮಾರುಕಟ್ಟೆ ಆರ್ಥಿಕತೆ",
        card_mandi_price_label: "ಮಾರುಕಟ್ಟೆ ದರ:",
        card_gross_rev_label: "ಒಟ್ಟು ಆದಾಯ:",
        card_net_profit_label: "ಅಂದಾಜು ನಿವ್ವಳ ಲಾಭ:",
        card_water_req: "ನೀರಿನ ಅವಶ್ಯಕತೆ:",
        card_duration: "ಬೆಳೆಯ ಅವಧಿ:",
        card_soil: "ಸೂಕ್ತ ಮಣ್ಣು:",
        per_qtl: "/ ಕ್ವಿಂಟಾಲ್",

        // Decision Matrix Table
        matrix_badge: "ಆರ್ಥಿಕ ನಿರ್ಧಾರ ಕೋಷ್ಟಕ",
        matrix_title: "💰 ಬೆಳೆಗಳ ಇಳುವರಿ ಮತ್ತು ಆದಾಯದ ಸಮಗ್ರ ಹೋಲಿಕೆ",
        th_rank_crop: "ಶ್ರೇಣಿ ಮತ್ತು ಬೆಳೆ",
        th_match: "ಹೊಂದಾಣಿಕೆ",
        th_yield: "ಇಳುವರಿ (ಟನ್/ಹೆ.)",
        th_total_harvest: "ಒಟ್ಟು ಇಳುವರಿ",
        th_mandi_rate: "ದರ (₹/ಕ್ವಿಂಟಾಲ್)",
        th_gross_rev: "ಒಟ್ಟು ಆದಾಯ (₹)",
        th_net_profit: "ನಿವ್ವಳ ಲಾಭ (₹)",
        tonnes_label: "ಟನ್",
        qtl_label: "ಕ್ವಿಂ.",

        // Soil & Irrigation Guidance
        guidance_soil_title: "🧪 ಮಣ್ಣಿನ ಫಲವತ್ತತೆ ಮತ್ತು ಗೊಬ್ಬರದ ಸಲಹೆಗಳು",
        guidance_water_title: "💧 ನೀರು ನಿರ್ವಹಣೆ ಮತ್ತು ನೀರಾವರಿ ನೀಲನಕ್ಷೆ",
        guidance_water_text: "ನಿಮ್ಮ ಪ್ರದೇಶದ ಹವಾಮಾನ ವಿವರಕ್ಕೆ ಅನುಗುಣವಾಗಿ, ಹೆಚ್ಚು ಮಳೆಯಾದಾಗ ನೀರು ಸರಾಗವಾಗಿ ಹರಿದುಹೋಗಲು ಚರಂಡಿ ವ್ಯವಸ್ಥೆ ಮಾಡಿ ಮತ್ತು ಒಣ ಹವೆಯಲ್ಲಿ ಹನಿ ನೀರಾವರಿ (Drip Irrigation) ಅಳವಡಿಸಿ.",

        // Footer
        footer_text: "ಅಗ್ರಿಶಿಫ್ಟ್ ಎಐ ಬೆಳೆ ಶಿಫಾರಸು ವ್ಯವಸ್ಥೆ • ಕರ್ನಾಟಕದ ಕೃಷಿ ದಾಖಲೆಗಳು ಮತ್ತು ಮಣ್ಣಿನ ದತ್ತಾಂಶದ ಮೇಲೆ ತರಬೇತಿ ಪಡೆದಿದೆ"
    }
};

// District name mappings (Canonical English to Kannada)
const DISTRICT_TRANSLATIONS = {
    'BAGALKOTE': 'ಬಾಗಲಕೋಟೆ (Bagalkote)',
    'BALLARI': 'ಬಳ್ಳಾರಿ (Ballari)',
    'BELAGAVI': 'ಬೆಳಗಾವಿ (Belagavi)',
    'BANGALORE RURAL': 'ಬೆಂಗಳೂರು ಗ್ರಾಮಾಂತರ (Bengaluru Rural)',
    'BENGALURU URBAN': 'ಬೆಂಗಳೂರು ನಗರ (Bengaluru Urban)',
    'BIDAR': 'ಬೀದರ್ (Bidar)',
    'CHAMARAJANAGAR': 'ಚಾಮರಾಜನಗರ (Chamarajanagar)',
    'CHIKKABALLAPURA': 'ಚಿಕ್ಕಬಳ್ಳಾಪುರ (Chikkaballapura)',
    'CHIKKAMAGALURU': 'ಚಿಕ್ಕಮಗಳೂರು (Chikkamagaluru)',
    'CHITRADURGA': 'ಚಿತ್ರದುರ್ಗ (Chitradurga)',
    'DAKSHINA KANNADA': 'ದಕ್ಷಿಣ ಕನ್ನಡ (Dakshina Kannada)',
    'DAVANGERE': 'ದಾವಣಗೆರೆ (Davanagere)',
    'DHARWAD': 'ಧಾರವಾಡ (Dharwad)',
    'GADAG': 'ಗದಗ (Gadag)',
    'KALABURAGI': 'ಕಲಬುರಗಿ (Kalaburagi)',
    'HASSAN': 'ಹಾಸನ (Hassan)',
    'HAVERI': 'ಹಾವೇರಿ (Haveri)',
    'KODAGU': 'ಕೊಡಗು (Kodagu)',
    'KOLAR': 'ಕೋಲಾರ (Kolar)',
    'KOPPAL': 'ಕೊಪ್ಪಳ (Koppal)',
    'MANDYA': 'ಮಂಡ್ಯ (Mandya)',
    'MYSURU': 'ಮೈಸೂರು (Mysuru)',
    'RAICHUR': 'ರಾಯಚೂರು (Raichur)',
    'RAMANAGARA': 'ರಾಮನಗರ (Ramanagara)',
    'SHIVAMOGGA': 'ಶಿವಮೊಗ್ಗ (Shivamogga)',
    'TUMAKURU': 'ತುಮಕೂರು (Tumakuru)',
    'UDUPI': 'ಉಡುಪಿ (Udupi)',
    'UTTARA KANNADA': 'ಉತ್ತರ ಕನ್ನಡ (Uttara Kannada)',
    'VIJAYAPURA': 'ವಿಜಯಪುರ (Vijayapura)',
    'YADGIR': 'ಯಾದಗಿರಿ (Yadgir)'
};

// Season name mappings
const SEASON_TRANSLATIONS = {
    'Kharif': { en: 'Kharif', kn: 'ಖಾರೀಫ್ (ಮುಂಗಾರು)' },
    'Rabi': { en: 'Rabi', kn: 'ರಬಿ (ಹಿಂಗಾರು)' },
    'Summer': { en: 'Summer', kn: 'ಬೇಸಿಗೆ' },
    'Whole Year': { en: 'Whole Year', kn: 'ವರ್ಷಪೂರ್ತಿ' }
};

// Crop Names (Canonical English to Kannada + English display)
const CROP_TRANSLATIONS = {
    'Maize': { en: 'Maize', kn: 'ಮೆಕ್ಕೆಜೋಳ (Maize)' },
    'Rice': { en: 'Rice', kn: 'ಭತ್ತ (Rice)' },
    'Sunflower': { en: 'Sunflower', kn: 'ಸೂರ್ಯಕಾಂತಿ (Sunflower)' },
    'Jowar': { en: 'Jowar', kn: 'ಜೋಳ (Jowar)' },
    'Dry chillies': { en: 'Dry chillies', kn: 'ಒಣ ಮೆಣಸಿನಕಾಯಿ (Dry chillies)' },
    'Onion': { en: 'Onion', kn: 'ಈರುಳ್ಳಿ (Onion)' },
    'Groundnut': { en: 'Groundnut', kn: 'ಕಡಲೆಕಾಯಿ (Groundnut)' },
    'Horse-gram': { en: 'Horse-gram', kn: 'ಹುರುಳಿ (Horse-gram)' },
    'Ragi': { en: 'Ragi', kn: 'ರಾಗಿ (Ragi)' },
    'Moong(Green Gram)': { en: 'Moong (Green Gram)', kn: 'ಹೆಸರುಕಾಳು (Moong)' },
    'Urad': { en: 'Urad', kn: 'ಉದ್ದಿನಕಾಳು (Urad)' },
    'Potato': { en: 'Potato', kn: 'ಆಲೂಗಡ್ಡೆ (Potato)' },
    'Cowpea(Lobia)': { en: 'Cowpea (Lobia)', kn: 'ಅಲಸಂದಿ (Cowpea)' },
    'Cotton(lint)': { en: 'Cotton (lint)', kn: 'ಹತ್ತಿ (Cotton)' },
    'Coconut': { en: 'Coconut', kn: 'ತೆಂಗಿನಕಾಯಿ (Coconut)' },
    'Sugarcane': { en: 'Sugarcane', kn: 'ಕಬ್ಬು (Sugarcane)' },
    'Gram': { en: 'Gram (Bengal Gram)', kn: 'ಕಡಲೆ (Gram)' },
    'Wheat': { en: 'Wheat', kn: 'ಗೋಧಿ (Wheat)' },
    'Arecanut': { en: 'Arecanut', kn: 'ಅಡಿಕೆ (Arecanut)' },
    'Banana': { en: 'Banana', kn: 'ಬಾಳೆಹಣ್ಣು (Banana)' },
    'Arhar/Tur': { en: 'Arhar / Tur', kn: 'ತೊಗರಿ (Tur)' },
    'Bajra': { en: 'Bajra', kn: 'ಸಜ್ಜೆ (Bajra)' },
    'Soyabean': { en: 'Soyabean', kn: 'ಸೋಯಾಬೀನ್ (Soyabean)' },
    'Garlic': { en: 'Garlic', kn: 'ಬೆಳ್ಳುಳ್ಳಿ (Garlic)' },
    'Ginger': { en: 'Ginger', kn: 'ಶುಂಠಿ (Ginger)' },
    'Turmeric': { en: 'Turmeric', kn: 'ಅರಿಶಿನ (Turmeric)' },
    'Cardamom': { en: 'Cardamom', kn: 'ಏಲಕ್ಕಿ (Cardamom)' },
    'Black pepper': { en: 'Black pepper', kn: 'ಕಾಳುಮೆಣಸು (Black pepper)' },
    'Cashewnut': { en: 'Cashewnut', kn: 'ಗೋಡಂಬಿ (Cashewnut)' }
};

// Crop Categories
const CATEGORY_TRANSLATIONS = {
    'Cereal': { en: 'Cereal', kn: 'ಧಾನ್ಯ (Cereal)' },
    'Millet': { en: 'Millet', kn: 'ಕಿರುಧಾನ್ಯ (Millet)' },
    'Millets': { en: 'Millet', kn: 'ಕಿರುಧಾನ್ಯ (Millet)' },
    'Oilseed': { en: 'Oilseed', kn: 'ಎಣ್ಣೆಕಾಳು (Oilseed)' },
    'Oilseed / Legume': { en: 'Oilseed / Legume', kn: 'ಎಣ್ಣೆಕಾಳು / ದ್ವಿದಳ ಧಾನ್ಯ' },
    'Pulse': { en: 'Pulse', kn: 'ದ್ವಿದಳ ಧಾನ್ಯ (Pulse)' },
    'Vegetable': { en: 'Vegetable', kn: 'ತರಕಾರಿ (Vegetable)' },
    'Spices': { en: 'Spice', kn: 'ಮಸಾಲೆ ಬೆಳೆ (Spice)' },
    'Spice': { en: 'Spice', kn: 'ಮಸಾಲೆ ಬೆಳೆ (Spice)' },
    'Tuber': { en: 'Tuber', kn: 'ಗೆಡ್ಡೆಗೆಣಸು (Tuber)' },
    'Commercial': { en: 'Commercial', kn: 'ವಾಣಿಜ್ಯ ಬೆಳೆ (Commercial)' },
    'Commercial / Fibre': { en: 'Commercial / Fibre', kn: 'ವಾಣಿಜ್ಯ / ನಾರು ಬೆಳೆ' },
    'Plantation': { en: 'Plantation', kn: 'ತೋಟಗಾರಿಕೆ / ಪ್ಲಾಂಟೇಶನ್' },
    'Horticulture': { en: 'Horticulture', kn: 'ತೋಟಗಾರಿಕೆ ಬೆಳೆ' },
    'Fruit': { en: 'Fruit', kn: 'ಹಣ್ಣು ಬೆಳೆ (Fruit)' }
};

// Water requirement translations
const WATER_TRANSLATIONS = {
    'Low': { en: 'Low', kn: 'ಕಡಿಮೆ (Low)' },
    'Very Low': { en: 'Very Low', kn: 'ಅತಿ ಕಡಿಮೆ (Very Low)' },
    'Medium': { en: 'Medium', kn: 'ಮಧ್ಯಮ (Medium)' },
    'Medium to High': { en: 'Medium to High', kn: 'ಮಧ್ಯಮದಿಂದ ಹೆಚ್ಚು' },
    'High': { en: 'High', kn: 'ಹೆಚ್ಚು (High)' },
    'Very High': { en: 'Very High', kn: 'ಅತಿ ಹೆಚ್ಚು (Very High)' },
    'Low to Medium': { en: 'Low to Medium', kn: 'ಕಡಿಮೆಯಿಂದ ಮಧ್ಯಮ' },
    'Low (Drought-hardy)': { en: 'Low (Drought-hardy)', kn: 'ಕಡಿಮೆ (ಬರ ನಿರೋಧಕ)' }
};

// Soil advice translation lookup
function translateSoilAdvice(tip, lang) {
    if (lang === 'en') return tip;

    if (tip.includes("acidic")) {
        return "ಮಣ್ಣು ಸ್ವಲ್ಪ ಆಮ್ಲೀಯವಾಗಿದೆ; ಕೃಷಿ ಸುಣ್ಣವನ್ನು (Agricultural Lime) ಮಣ್ಣಿಗೆ ಸೇರಿಸಿ.";
    }
    if (tip.includes("alkaline")) {
        return "ಮಣ್ಣು ಕ್ಷಾರೀಯವಾಗಿದೆ; ಜಿಪ್ಸಮ್ ಅಥವಾ ಸಾವಯವ ಕಾಂಪೋಸ್ಟ್ ಗೊಬ್ಬರವನ್ನು ಬಳಸಿ.";
    }
    if (tip.includes("Nitrogen")) {
        return "ಸಾರಜನಕದ ಕೊರತೆಯಿದೆ; ಯೂರಿಯಾ ಅಥವಾ ಬೇವು ಲೇಪಿತ ಯೂರಿಯಾ ಗೊಬ್ಬರವನ್ನು ಮೇಲುಗೊಬ್ಬರವಾಗಿ ನೀಡಿ.";
    }
    if (tip.includes("Phosphorus")) {
        return "ರಂಜಕದ ಪ್ರಮಾಣ ಕಡಿಮೆ ಇದೆ; ಸಿಂಗಲ್ ಸೂಪರ್ ಫಾಸ್ಫೇಟ್ (SSP) ಅಥವಾ ಡಿಎಪಿ (DAP) ಗೊಬ್ಬರ ನೀಡಿ.";
    }
    if (tip.includes("well-balanced")) {
        return "ಈ ಬೆಳೆಗೆ ಮಣ್ಣಿನ ಪೋಷಕಾಂಶಗಳು ಮತ್ತು ಪಿ.ಹೆಚ್ ಮಟ್ಟ ಸಮತೋಲನವಾಗಿದೆ.";
    }
    return tip;
}
