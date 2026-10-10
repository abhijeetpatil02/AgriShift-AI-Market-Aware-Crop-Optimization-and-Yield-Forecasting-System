/* AgriShift — Frontend Logic, Multi-Language & Model Integration */

let districtSoilCache = {};
let currentLanguage = localStorage.getItem('agrishift_lang') || 'en';
let lastPredictionData = null;

// On DOM Loaded
document.addEventListener('DOMContentLoaded', () => {
    bindSyncInputs();
    loadDistrictSoilCache();
    
    // Initialize UI language
    switchLanguage(currentLanguage, false);

    // Auto-fetch initial weather for default selected district
    setTimeout(() => {
        fetchLiveWeatherAndSoil();
    }, 300);

    // Form submit listener
    const form = document.getElementById('recommendForm');
    if (form) {
        form.addEventListener('submit', handlePrediction);
    }
});

/**
 * Switch Active Application Language (English <-> Kannada)
 * @param {string} lang - 'en' or 'kn'
 * @param {boolean} reRenderResults - whether to re-render output if available
 */
function switchLanguage(lang, reRenderResults = true) {
    currentLanguage = (lang === 'kn') ? 'kn' : 'en';
    localStorage.setItem('agrishift_lang', currentLanguage);

    // Update active button state
    const btnEn = document.getElementById('langBtnEn');
    const btnKn = document.getElementById('langBtnKn');
    if (btnEn && btnKn) {
        btnEn.classList.toggle('active', currentLanguage === 'en');
        btnKn.classList.toggle('active', currentLanguage === 'kn');
    }

    const dict = TRANSLATIONS[currentLanguage] || TRANSLATIONS.en;

    // 1. Update all static elements marked with data-i18n
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (dict[key]) {
            el.textContent = dict[key];
        }
    });

    // 2. Localize District Dropdown text while preserving canonical English values
    const districtSelect = document.getElementById('districtSelect');
    if (districtSelect) {
        Array.from(districtSelect.options).forEach(opt => {
            const rawDist = opt.value;
            if (currentLanguage === 'kn' && DISTRICT_TRANSLATIONS[rawDist]) {
                opt.textContent = DISTRICT_TRANSLATIONS[rawDist];
            } else {
                opt.textContent = rawDist;
            }
        });
    }

    // 3. Update weather auto-fetch button label
    const autoFetchText = document.getElementById('btnAutoFetchText');
    if (autoFetchText) {
        autoFetchText.textContent = dict.btn_autofetch;
    }

    // 4. Update predict CTA button text (if not currently loading)
    const btnPredict = document.getElementById('btnPredict');
    if (btnPredict && !btnPredict.disabled) {
        const btnText = btnPredict.querySelector('.btn-text');
        if (btnText) btnText.textContent = dict.btn_predict;
    }

    // 5. If recommendations are currently displayed, re-render them dynamically in the new language
    if (reRenderResults && lastPredictionData) {
        renderRecommendations(lastPredictionData);
    }
}

// Synchronize Sliders with Numeric Inputs
function bindSyncInputs() {
    const pairs = [
        ['nitrogenRange', 'nitrogenNum'],
        ['phosphorusRange', 'phosphorusNum'],
        ['potassiumRange', 'potassiumNum'],
        ['phRange', 'phNum'],
        ['tempRange', 'tempNum'],
        ['humidityRange', 'humidityNum'],
        ['rainfallRange', 'rainfallNum']
    ];

    pairs.forEach(([sliderId, numId]) => {
        const slider = document.getElementById(sliderId);
        const num = document.getElementById(numId);

        if (slider && num) {
            slider.addEventListener('input', () => {
                num.value = slider.value;
            });
            num.addEventListener('input', () => {
                slider.value = num.value;
            });
        }
    });
}

// Load baseline soil database for all Karnataka districts
async function loadDistrictSoilCache() {
    try {
        const res = await fetch('/api/districts');
        const data = await res.json();
        if (data.soil_profiles) {
            districtSoilCache = data.soil_profiles;
        }
    } catch (e) {
        console.warn('Could not pre-cache district soil:', e);
    }
}

// Fetch live weather and baseline soil for chosen district
async function fetchLiveWeatherAndSoil() {
    const districtSelect = document.getElementById('districtSelect');
    if (!districtSelect) return;
    const district = districtSelect.value;
    const btnAutoFetch = document.getElementById('btnAutoFetch');
    const autoFetchText = document.getElementById('btnAutoFetchText');
    const statusBox = document.getElementById('liveWeatherStatus');
    const dict = TRANSLATIONS[currentLanguage] || TRANSLATIONS.en;

    if (btnAutoFetch) btnAutoFetch.disabled = true;
    if (autoFetchText) autoFetchText.textContent = dict.btn_autofetch_loading;

    // 1. Auto-fill Soil Values from Local Soil Dataset
    if (districtSoilCache[district]) {
        const soil = districtSoilCache[district];
        updateValue('nitrogenRange', 'nitrogenNum', soil.N);
        updateValue('phosphorusRange', 'phosphorusNum', soil.P);
        updateValue('potassiumRange', 'potassiumNum', soil.K);
        updateValue('phRange', 'phNum', soil.pH);
    }

    // 2. Fetch Live Weather via WeatherAPI
    try {
        const res = await fetch(`/api/weather?district=${encodeURIComponent(district)}`);
        const w = await res.json();

        if (w.success || w.temperature) {
            updateValue('tempRange', 'tempNum', w.temperature);
            updateValue('humidityRange', 'humidityNum', w.humidity);
            
            if (w.precipitation && w.precipitation > 0) {
                const estRain = Math.max(w.precipitation * 30, 150);
                updateValue('rainfallRange', 'rainfallNum', estRain);
            }

            if (statusBox) {
                statusBox.classList.remove('hidden');
                const locEl = document.getElementById('weatherLocation');
                const condEl = document.getElementById('weatherConditionText');
                
                const dispDistrict = (currentLanguage === 'kn' && DISTRICT_TRANSLATIONS[district]) 
                    ? DISTRICT_TRANSLATIONS[district] 
                    : (w.location || `${district}, Karnataka`);
                
                if (locEl) locEl.textContent = dispDistrict;
                if (condEl) {
                    const condPrefix = dict.weather_live_prefix || "Live Weather:";
                    condEl.textContent = `${condPrefix} ${w.condition || 'Clear'} • ${w.temperature}°C • ${w.humidity}%`;
                }
            }
        }
    } catch (err) {
        console.error('Weather API error:', err);
    } finally {
        if (btnAutoFetch) btnAutoFetch.disabled = false;
        if (autoFetchText) autoFetchText.textContent = dict.btn_autofetch;
    }
}

// Helper to update both slider and input box
function updateValue(sliderId, numId, val) {
    const slider = document.getElementById(sliderId);
    const num = document.getElementById(numId);
    if (slider) slider.value = val;
    if (num) num.value = val;
}

// Quick Preset handler
function applyPreset(district, season) {
    const districtSelect = document.getElementById('districtSelect');
    if (districtSelect) districtSelect.value = district;

    const seasonRadios = document.getElementsByName('season');
    for (let r of seasonRadios) {
        if (r.value === season) {
            r.checked = true;
            break;
        }
    }

    fetchLiveWeatherAndSoil();
}

// Handle Crop Recommendation Prediction (ML Model Pipeline)
async function handlePrediction(e) {
    e.preventDefault();

    const dict = TRANSLATIONS[currentLanguage] || TRANSLATIONS.en;
    const btnPredict = document.getElementById('btnPredict');
    const spinner = document.getElementById('loadingSpinner');
    const btnText = btnPredict.querySelector('.btn-text');
    const resultsSection = document.getElementById('resultsSection');

    // Show loading state
    btnPredict.disabled = true;
    if (spinner) spinner.classList.remove('hidden');
    if (btnText) btnText.textContent = dict.btn_predict_loading;

    // Normalization Layer: Canonical English categorical values and numeric floats
    const payload = {
        district: document.getElementById('districtSelect').value,
        season: document.querySelector('input[name="season"]:checked').value,
        farm_area: parseFloat(document.getElementById('farmAreaInput').value || 2.0),
        N: parseFloat(document.getElementById('nitrogenNum').value),
        P: parseFloat(document.getElementById('phosphorusNum').value),
        K: parseFloat(document.getElementById('potassiumNum').value),
        pH: parseFloat(document.getElementById('phNum').value),
        temperature: parseFloat(document.getElementById('tempNum').value),
        humidity: parseFloat(document.getElementById('humidityNum').value),
        rainfall: parseFloat(document.getElementById('rainfallNum').value)
    };

    try {
        const res = await fetch('/api/recommend', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await res.json();

        if (data.success && data.recommendations) {
            lastPredictionData = data; // Cache for seamless language switching
            renderRecommendations(data);
            if (resultsSection) {
                resultsSection.classList.remove('hidden');
                resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        } else {
            alert('Error generating recommendation: ' + (data.error || 'Unknown error'));
        }
    } catch (err) {
        console.error('Prediction request error:', err);
        alert('Server connection error. Please verify the Flask server is running.');
    } finally {
        btnPredict.disabled = false;
        if (spinner) spinner.classList.add('hidden');
        if (btnText) btnText.textContent = dict.btn_predict;
    }
}

// Render Top 3 Cards in the Podium & Decision Matrix Table
function renderRecommendations(data) {
    const dict = TRANSLATIONS[currentLanguage] || TRANSLATIONS.en;
    const container = document.getElementById('podiumCards');
    const summary = document.getElementById('resultSummary');
    const adviceList = document.getElementById('soilAdviceList');
    const tableBody = document.getElementById('economicTableBody');
    const heading = document.getElementById('resultHeading');

    if (heading) {
        heading.textContent = dict.results_heading;
    }

    // Format District & Season localized name for summary
    const dispDistrict = (currentLanguage === 'kn' && DISTRICT_TRANSLATIONS[data.district]) 
        ? DISTRICT_TRANSLATIONS[data.district] 
        : data.district;
        
    const dispSeason = SEASON_TRANSLATIONS[data.season] 
        ? SEASON_TRANSLATIONS[data.season][currentLanguage] 
        : data.season;

    if (summary) {
        summary.textContent = dict.results_summary_template
            .replace('{district}', dispDistrict)
            .replace('{season}', dispSeason)
            .replace('{area}', data.farm_area_ha)
            .replace('{soil}', payloadNpkSummary());
    }

    if (!container) return;
    container.innerHTML = '';

    const rankLabels = [dict.rank_1, dict.rank_2, dict.rank_3];

    data.recommendations.forEach((item, index) => {
        // Localize crop name and category
        const cropDisplay = (CROP_TRANSLATIONS[item.crop] && CROP_TRANSLATIONS[item.crop][currentLanguage])
            ? CROP_TRANSLATIONS[item.crop][currentLanguage]
            : item.crop;

        const categoryDisplay = (CATEGORY_TRANSLATIONS[item.category] && CATEGORY_TRANSLATIONS[item.category][currentLanguage])
            ? CATEGORY_TRANSLATIONS[item.category][currentLanguage]
            : item.category;

        const waterDisplay = (WATER_TRANSLATIONS[item.water_requirement] && WATER_TRANSLATIONS[item.water_requirement][currentLanguage])
            ? WATER_TRANSLATIONS[item.water_requirement][currentLanguage]
            : item.water_requirement;

        const card = document.createElement('div');
        card.className = `podium-card rank-${item.rank}`;

        card.innerHTML = `
            <div class="rank-banner">${rankLabels[index] || `#${item.rank}`}</div>
            <div class="crop-header-row">
                <div class="crop-icon-large">${item.icon}</div>
                <div>
                    <h3 class="crop-name">${cropDisplay}</h3>
                    <span class="crop-category-badge">${categoryDisplay}</span>
                </div>
            </div>

            <!-- MODEL 1: Suitability Score -->
            <div class="model-badge-row">
                <span class="model-tag-chip m1">${dict.badge_model1}</span>
            </div>
            <div class="match-meter-wrap">
                <div class="match-label-row">
                    <span>${dict.card_suitability_label}</span>
                    <span class="score-text">${item.model1_match_score}%</span>
                </div>
                <div class="match-bar-bg">
                    <div class="match-bar-fill" style="width: ${item.model1_match_score}%;"></div>
                </div>
            </div>

            <!-- MODEL 2: Machine Learning Yield Prediction -->
            <div class="model-badge-row">
                <span class="model-tag-chip m2">${dict.card_predicted_yield_title}</span>
            </div>
            <div class="yield-highlight-box">
                <div class="yield-stat">
                    <span class="yield-val">${item.model2_predicted_yield_ha}</span>
                    <span class="yield-lbl">${dict.card_unit_tonnes_ha}</span>
                </div>
                <div class="yield-divider"></div>
                <div class="yield-stat">
                    <span class="yield-val">${item.total_production_tonnes} t</span>
                    <span class="yield-lbl">${dict.card_unit_total_harvest.replace('{area}', data.farm_area_ha)}</span>
                </div>
            </div>

            <!-- MARKET-AWARE ECONOMICS -->
            <div class="model-badge-row">
                <span class="model-tag-chip m3">${dict.card_market_title}</span>
            </div>
            <div class="economics-card-box">
                <div class="econ-row">
                    <span>${dict.card_mandi_price_label}</span>
                    <strong>₹${item.mandi_price_qtl.toLocaleString('en-IN')} ${dict.per_qtl}</strong>
                </div>
                <div class="econ-row">
                    <span>${dict.card_gross_rev_label}</span>
                    <strong class="revenue-val">₹${item.gross_revenue_inr.toLocaleString('en-IN')}</strong>
                </div>
                <div class="econ-row highlight-profit">
                    <span>${dict.card_net_profit_label}</span>
                    <strong class="profit-val">₹${item.net_profit_inr.toLocaleString('en-IN')}</strong>
                </div>
                <div class="mandi-source">📍 ${item.mandi_location}</div>
            </div>

            <ul class="crop-metrics-list">
                <li><span>${dict.card_water_req}</span> <strong>${waterDisplay}</strong></li>
                <li><span>${dict.card_duration}</span> <strong>${item.duration}</strong></li>
                <li><span>${dict.card_soil}</span> <strong>${item.ideal_soil}</strong></li>
            </ul>
        `;
        container.appendChild(card);
    });

    // Populate Decision Matrix Table
    if (tableBody) {
        tableBody.innerHTML = '';
        data.recommendations.forEach(item => {
            const cropDisplay = (CROP_TRANSLATIONS[item.crop] && CROP_TRANSLATIONS[item.crop][currentLanguage])
                ? CROP_TRANSLATIONS[item.crop][currentLanguage]
                : item.crop;
            const categoryDisplay = (CATEGORY_TRANSLATIONS[item.category] && CATEGORY_TRANSLATIONS[item.category][currentLanguage])
                ? CATEGORY_TRANSLATIONS[item.category][currentLanguage]
                : item.category;

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>#${item.rank} ${item.icon} ${cropDisplay}</strong> <div class="subtext">${categoryDisplay}</div></td>
                <td><span class="score-badge">${item.model1_match_score}%</span></td>
                <td><strong>${item.model2_predicted_yield_ha} t/ha</strong></td>
                <td><strong>${item.total_production_tonnes} ${dict.tonnes_label}</strong> <div class="subtext">(${item.total_production_quintals} ${dict.qtl_label})</div></td>
                <td>₹${item.mandi_price_qtl.toLocaleString('en-IN')} ${dict.per_qtl}</td>
                <td class="revenue-cell">₹${item.gross_revenue_inr.toLocaleString('en-IN')}</td>
                <td class="profit-cell"><strong>₹${item.net_profit_inr.toLocaleString('en-IN')}</strong></td>
            `;
            tableBody.appendChild(tr);
        });
    }

    // Populate Soil Advice in the user's selected language
    if (adviceList) {
        adviceList.innerHTML = '';
        const firstCrop = data.recommendations[0];
        if (firstCrop && firstCrop.soil_advice) {
            firstCrop.soil_advice.forEach(tip => {
                const li = document.createElement('li');
                li.textContent = translateSoilAdvice(tip, currentLanguage);
                adviceList.appendChild(li);
            });
        }
    }
}

function payloadNpkSummary() {
    const n = document.getElementById('nitrogenNum').value;
    const p = document.getElementById('phosphorusNum').value;
    const k = document.getElementById('potassiumNum').value;
    const ph = document.getElementById('phNum').value;
    if (currentLanguage === 'kn') {
        return `ಸಾರಜನಕ(N): ${n}, ರಂಜಕ(P): ${p}, ಪೊಟ್ಯಾಶ್(K): ${k}, ಪಿ.ಹೆಚ್(pH): ${ph}`;
    }
    return `Soil N:${n}, P:${p}, K:${k}, pH:${ph}`;
}
