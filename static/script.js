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

    // Update Save button status
    const saveBtn = document.getElementById('btnSaveHistory');
    if (saveBtn) {
        if (data.saved_to_history) {
            saveBtn.classList.add('saved');
            saveBtn.innerHTML = '<span>✅</span> <span>Saved to MySQL History</span>';
        } else {
            saveBtn.classList.remove('saved');
            saveBtn.innerHTML = '<span>💾</span> <span>Save to My History</span>';
        }
    }

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

// ----------------- Prediction History & Session Controls -----------------

// Toggle Prediction History Drawer
function toggleHistoryDrawer() {
    const overlay = document.getElementById('historyOverlay');
    const drawer = document.getElementById('historyDrawer');
    if (!drawer) return;
    const isActive = drawer.classList.contains('active');
    if (isActive) {
        drawer.classList.remove('active');
        if (overlay) overlay.classList.remove('active');
    } else {
        drawer.classList.add('active');
        if (overlay) overlay.classList.add('active');
        fetchPredictionHistory();
    }
}

// Fetch user prediction history from backend
async function fetchPredictionHistory() {
    const loading = document.getElementById('historyLoading');
    const list = document.getElementById('historyItemsList');
    const empty = document.getElementById('historyEmpty');
    if (!list) return;

    list.innerHTML = '';
    if (loading) loading.style.display = 'block';
    if (empty) empty.style.display = 'none';

    try {
        const res = await fetch('/api/history');
        if (res.status === 401) {
            if (loading) loading.style.display = 'none';
            list.innerHTML = '<div style="padding:1rem;color:#fca5a5;text-align:center;">Please <a href="/login" style="color:#34d399;font-weight:bold;">sign in</a> to view your prediction history.</div>';
            return;
        }
        const data = await res.json();
        if (loading) loading.style.display = 'none';

        if (data.success && data.records && data.records.length > 0) {
            list.innerHTML = data.records.map(rec => {
                const cropsList = [
                    { rank: '🥇 #1', name: rec.top_crop_1, yield: rec.crop1_yield || rec.predicted_yield, rev: rec.crop1_revenue || rec.estimated_revenue },
                    { rank: '🥈 #2', name: rec.top_crop_2, yield: rec.crop2_yield, rev: rec.crop2_revenue },
                    { rank: '🥉 #3', name: rec.top_crop_3, yield: rec.crop3_yield, rev: rec.crop3_revenue }
                ].filter(c => c.name);

                const cropsHtml = cropsList.map(c => `
                    <div class="history-crop-box">
                        <div class="crop-rank-name">${c.rank} <strong>${c.name}</strong></div>
                        <div class="crop-metrics-pair">
                            <span>Yield: <strong>${c.yield ? c.yield + ' t/ha' : 'N/A'}</strong></span>
                            <span class="crop-rev">Rev: <strong>₹${c.rev ? Number(c.rev).toLocaleString('en-IN') : 'N/A'}</strong></span>
                        </div>
                    </div>
                `).join('');

                const dateStr = rec.created_at ? new Date(rec.created_at).toLocaleDateString(undefined, {
                    month: 'short', day: 'numeric', year: 'numeric'
                }) : 'Recent';

                return `
                    <div class="history-card-item" id="history-item-${rec.id}">
                        <button class="btn-del-history" onclick="deleteHistoryRecord(${rec.id})" title="Delete record">&times;</button>
                        <div class="history-card-top">
                            <span class="history-dist-badge">📍 ${rec.district} (${rec.season})</span>
                            <span class="history-date">${dateStr} • Land: ${rec.farm_area_ha} Ha</span>
                        </div>
                        <div class="history-3crops-grid">${cropsHtml}</div>
                    </div>
                `;
            }).join('');
        } else {
            if (empty) empty.style.display = 'block';
        }
    } catch (e) {
        if (loading) loading.style.display = 'none';
        list.innerHTML = `<div style="padding:1rem;color:#fca5a5;text-align:center;">Failed to load history: ${e.message}</div>`;
    }
}

// Delete history record
async function deleteHistoryRecord(id) {
    if (!confirm('Are you sure you want to delete this prediction record?')) return;
    try {
        const res = await fetch(`/api/history/${id}`, { method: 'DELETE' });
        const data = await res.json();
        if (data.success) {
            const el = document.getElementById(`history-item-${id}`);
            if (el) el.remove();
            const list = document.getElementById('historyItemsList');
            if (list && list.children.length === 0) {
                const empty = document.getElementById('historyEmpty');
                if (empty) empty.style.display = 'block';
            }
        }
    } catch (e) {
        alert('Failed to delete history record: ' + e.message);
    }
}

// Save current prediction to history
async function saveCurrentPrediction() {
    if (!lastPredictionData) {
        alert('Please run a crop prediction first.');
        return;
    }
    const btn = document.getElementById('btnSaveHistory');
    if (!btn) return;

    btn.disabled = true;
    btn.innerHTML = '<span>⏳</span> <span>Saving...</span>';

    const payload = {
        district: lastPredictionData.district || document.getElementById('districtSelect').value,
        season: lastPredictionData.season || document.querySelector('input[name="season"]:checked').value,
        farm_area_ha: parseFloat(lastPredictionData.farm_area_ha || document.getElementById('farmAreaInput').value || 1.0),
        nitrogen: parseFloat(document.getElementById('nitrogenNum').value),
        phosphorus: parseFloat(document.getElementById('phosphorusNum').value),
        potassium: parseFloat(document.getElementById('potassiumNum').value),
        ph: parseFloat(document.getElementById('phNum').value),
        temperature: parseFloat(document.getElementById('tempNum').value),
        humidity: parseFloat(document.getElementById('humidityNum').value),
        rainfall: parseFloat(document.getElementById('rainfallNum').value),
        top_crops: lastPredictionData.recommendations || []
    };

    try {
        const res = await fetch('/api/history/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (res.status === 401) {
            alert('Please sign in or create an account to save predictions.');
            window.location.href = '/login';
            return;
        }
        const data = await res.json();
        if (data.success) {
            btn.classList.add('saved');
            btn.innerHTML = '<span>✅</span> <span>Saved to History</span>';
        } else {
            btn.disabled = false;
            btn.innerHTML = '<span>💾</span> <span>Save to My History</span>';
            alert('Could not save prediction: ' + (data.error || 'Server error'));
        }
    } catch (e) {
        btn.disabled = false;
        btn.innerHTML = '<span>💾</span> <span>Save to My History</span>';
        alert('Failed to save prediction: ' + e.message);
    }
}

// Toggle Farm Profile Modal
function toggleFarmProfileModal() {
    const modal = document.getElementById('farmProfileModal');
    if (!modal) return;
    modal.classList.toggle('active');
    const alertBox = document.getElementById('farmProfileAlert');
    if (alertBox) alertBox.style.display = 'none';
}

// Save Farm Profile to MySQL
async function handleSaveFarmProfile(e) {
    e.preventDefault();
    const btn = document.getElementById('btnSaveFarmProfile');
    const alertBox = document.getElementById('farmProfileAlert');
    const landArea = parseFloat(document.getElementById('profileLandArea').value);
    const landUnit = document.getElementById('profileLandUnit').value;
    const soilType = document.getElementById('profileSoilType').value;
    const irrigation = document.getElementById('profileIrrigation').value;

    if (isNaN(landArea) || landArea <= 0) {
        alert('Please enter a valid land area size.');
        return false;
    }

    if (btn) {
        btn.disabled = true;
        btn.textContent = 'Saving to MySQL...';
    }

    try {
        const res = await fetch('/api/farm-profile', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                land_area: landArea,
                land_unit: landUnit,
                primary_soil_type: soilType,
                irrigation_source: irrigation
            })
        });

        const data = await res.json();
        if (data.success) {
            if (alertBox) {
                alertBox.className = 'modal-msg success';
                alertBox.style.display = 'block';
                alertBox.textContent = '✅ Farm profile saved successfully to MySQL database!';
            }
            // Auto sync to main dashboard input
            const mainArea = document.getElementById('farmAreaInput');
            if (mainArea) {
                const inHa = landUnit === 'Acres' ? (landArea / 2.471).toFixed(2) : landArea.toFixed(1);
                mainArea.value = inHa;
            }
            setTimeout(() => {
                toggleFarmProfileModal();
                if (btn) {
                    btn.disabled = false;
                    btn.textContent = '💾 Save to MySQL';
                }
            }, 1200);
        } else {
            alert('Failed to save farm profile: ' + (data.error || 'Server error'));
            if (btn) {
                btn.disabled = false;
                btn.textContent = '💾 Save to MySQL';
            }
        }
    } catch (err) {
        alert('Server error saving farm profile: ' + err.message);
        if (btn) {
            btn.disabled = false;
            btn.textContent = '💾 Save to MySQL';
        }
    }
    return false;
}

// Auto-initialize profile preferences from session metadata
window.addEventListener('DOMContentLoaded', () => {
    const meta = document.getElementById('userSessionMeta');
    if (meta) {
        const userDistrict = meta.getAttribute('data-user-district');
        const userLang = meta.getAttribute('data-user-lang');
        const farmArea = meta.getAttribute('data-farm-area');
        const farmUnit = meta.getAttribute('data-farm-unit');

        if (userLang && ['en', 'kn'].includes(userLang) && typeof switchLanguage === 'function') {
            switchLanguage(userLang);
        }
        if (userDistrict) {
            const districtSelect = document.getElementById('districtSelect');
            if (districtSelect) {
                districtSelect.value = userDistrict.toUpperCase();
                if (typeof fetchLiveWeatherAndSoil === 'function') {
                    fetchLiveWeatherAndSoil();
                }
            }
        }
        if (farmArea && parseFloat(farmArea) > 0) {
            const mainArea = document.getElementById('farmAreaInput');
            if (mainArea) {
                const inHa = farmUnit === 'Acres' ? (parseFloat(farmArea) / 2.471).toFixed(2) : parseFloat(farmArea).toFixed(1);
                mainArea.value = inHa;
            }
        }
    }

    // Close modal on Escapee key 
    window.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            const farmModal = document.getElementById('farmProfileModal');
            if (farmModal && farmModal.classList.contains('active')) {
                farmModal.classList.remove('active');
            }
            const historyDrawer = document.getElementById('historyDrawer');
            if (historyDrawer && historyDrawer.classList.contains('active')) {
                toggleHistoryDrawer();
            }
        }
    });
});

