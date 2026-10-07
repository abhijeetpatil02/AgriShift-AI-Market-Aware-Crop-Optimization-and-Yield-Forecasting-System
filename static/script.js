/* AgriShift — Frontend Logic & Model Integration */

let districtSoilCache = {};

// On DOM Loaded
document.addEventListener('DOMContentLoaded', () => {
    bindSyncInputs();
    loadDistrictSoilCache();
    
    // Auto-fetch initial weather for default selected district
    setTimeout(() => {
        fetchLiveWeatherAndSoil();
    }, 300);

    // Form submit listener
    const form = document.getElementById('recommendForm');
    form.addEventListener('submit', handlePrediction);
});

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
    const district = districtSelect.value;
    const btnAutoFetch = document.getElementById('btnAutoFetch');
    const statusBox = document.getElementById('liveWeatherStatus');

    btnAutoFetch.disabled = true;
    btnAutoFetch.innerHTML = '<span>⏳</span> Fetching Live Data...';

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
            
            // If precipitation > 0, set rainfall or keep seasonal norm
            if (w.precipitation && w.precipitation > 0) {
                // Adjust precipitation to seasonal context if needed
                const estRain = Math.max(w.precipitation * 30, 150);
                updateValue('rainfallRange', 'rainfallNum', estRain);
            }

            // Update UI status box
            statusBox.classList.remove('hidden');
            document.getElementById('weatherLocation').textContent = w.location || `${district}, Karnataka`;
            document.getElementById('weatherConditionText').textContent = `Live Weather: ${w.condition} • ${w.temperature}°C • ${w.humidity}% Humidity`;
        }
    } catch (err) {
        console.error('Weather API error:', err);
    } finally {
        btnAutoFetch.disabled = false;
        btnAutoFetch.innerHTML = '<span class="btn-icon">⚡</span> Auto-Fetch Live Weather & Soil';
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
    districtSelect.value = district;

    const seasonRadios = document.getElementsByName('season');
    for (let r of seasonRadios) {
        if (r.value === season) {
            r.checked = true;
            break;
        }
    }

    fetchLiveWeatherAndSoil();
}

// Handle Crop Recommendation Prediction
async function handlePrediction(e) {
    e.preventDefault();

    const btnPredict = document.getElementById('btnPredict');
    const spinner = document.getElementById('loadingSpinner');
    const btnText = btnPredict.querySelector('.btn-text');
    const resultsSection = document.getElementById('resultsSection');

    // Show loading
    btnPredict.disabled = true;
    spinner.classList.remove('hidden');
    btnText.textContent = 'Analyzing Soil & Agro-Climatic Model...';

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
            renderRecommendations(data);
            resultsSection.classList.remove('hidden');
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } else {
            alert('Error generating recommendation: ' + (data.error || 'Unknown error'));
        }
    } catch (err) {
        console.error('Prediction request error:', err);
        alert('Server connection error. Please verify the Flask server is running.');
    } finally {
        btnPredict.disabled = false;
        spinner.classList.add('hidden');
        btnText.textContent = '🌾 Run Crop & Yield AI Analysis';
    }
}

// Render Top 3 Cards in the Podium & Decision Matrix Table
function renderRecommendations(data) {
    const container = document.getElementById('podiumCards');
    const summary = document.getElementById('resultSummary');
    const adviceList = document.getElementById('soilAdviceList');
    const tableBody = document.getElementById('economicTableBody');

    summary.textContent = `Analyzed ${data.district} for ${data.season} season across ${data.farm_area_ha} Hectares based on ${payloadNpkSummary()}`;
    container.innerHTML = '';

    const rankIcons = ['🥇 #1 Top Recommendation', '🥈 #2 Viable Alternative', '🥉 #3 Viable Alternative'];

    data.recommendations.forEach((item, index) => {
        const card = document.createElement('div');
        card.className = `podium-card rank-${item.rank}`;

        card.innerHTML = `
            <div class="rank-banner">${rankIcons[index]}</div>
            <div class="crop-header-row">
                <div class="crop-icon-large">${item.icon}</div>
                <div>
                    <h3 class="crop-name">${item.crop}</h3>
                    <span class="crop-category-badge">${item.category}</span>
                </div>
            </div>

            <!-- MODEL 1: Suitability Score -->
            <div class="model-badge-row">
                <span class="model-tag-chip m1">🤖 Model 1: Crop Suitability</span>
            </div>
            <div class="match-meter-wrap">
                <div class="match-label-row">
                    <span>Agronomic Compatibility</span>
                    <span class="score-text">${item.model1_match_score}%</span>
                </div>
                <div class="match-bar-bg">
                    <div class="match-bar-fill" style="width: ${item.model1_match_score}%;"></div>
                </div>
            </div>

            <!-- MODEL 2: Machine Learning Yield Prediction -->
            <div class="model-badge-row">
                <span class="model-tag-chip m2">🌾 Model 2: AI Yield Forecast</span>
            </div>
            <div class="yield-highlight-box">
                <div class="yield-stat">
                    <span class="yield-val">${item.model2_predicted_yield_ha}</span>
                    <span class="yield-lbl">Tonnes / Hectare</span>
                </div>
                <div class="yield-divider"></div>
                <div class="yield-stat">
                    <span class="yield-val">${item.total_production_tonnes} t</span>
                    <span class="yield-lbl">Total Harvest (${data.farm_area_ha} Ha)</span>
                </div>
            </div>

            <!-- MARKET-AWARE ECONOMICS -->
            <div class="model-badge-row">
                <span class="model-tag-chip m3">📈 APMC Market Economics</span>
            </div>
            <div class="economics-card-box">
                <div class="econ-row">
                    <span>Mandi Price:</span>
                    <strong>₹${item.mandi_price_qtl.toLocaleString('en-IN')} / qtl</strong>
                </div>
                <div class="econ-row">
                    <span>Gross Revenue:</span>
                    <strong class="revenue-val">₹${item.gross_revenue_inr.toLocaleString('en-IN')}</strong>
                </div>
                <div class="econ-row highlight-profit">
                    <span>Est. Net Profit:</span>
                    <strong class="profit-val">₹${item.net_profit_inr.toLocaleString('en-IN')}</strong>
                </div>
                <div class="mandi-source">📍 ${item.mandi_location}</div>
            </div>

            <ul class="crop-metrics-list">
                <li><span>Water Requirement:</span> <strong>${item.water_requirement}</strong></li>
                <li><span>Growing Duration:</span> <strong>${item.duration}</strong></li>
                <li><span>Ideal Soil:</span> <strong>${item.ideal_soil}</strong></li>
            </ul>
        `;
        container.appendChild(card);
    });

    // Populate Decision Matrix Table
    if (tableBody) {
        tableBody.innerHTML = '';
        data.recommendations.forEach(item => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>#${item.rank} ${item.icon} ${item.crop}</strong> <div class="subtext">${item.category}</div></td>
                <td><span class="score-badge">${item.model1_match_score}%</span></td>
                <td><strong>${item.model2_predicted_yield_ha} t/ha</strong></td>
                <td><strong>${item.total_production_tonnes} Tonnes</strong> <div class="subtext">(${item.total_production_quintals} qtl)</div></td>
                <td>₹${item.mandi_price_qtl.toLocaleString('en-IN')} / qtl</td>
                <td class="revenue-cell">₹${item.gross_revenue_inr.toLocaleString('en-IN')}</td>
                <td class="profit-cell"><strong>₹${item.net_profit_inr.toLocaleString('en-IN')}</strong></td>
            `;
            tableBody.appendChild(tr);
        });
    }

    // Populate Soil Advice
    if (adviceList) {
        adviceList.innerHTML = '';
        const firstCrop = data.recommendations[0];
        if (firstCrop && firstCrop.soil_advice) {
            firstCrop.soil_advice.forEach(tip => {
                const li = document.createElement('li');
                li.textContent = tip;
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
    return `Soil N:${n}, P:${p}, K:${k}, pH:${ph}`;
}
