/**
 * AgriShift Frontend Controller
 * Handles interactive tabs, API communication, and Chart.js visualizations.
 */

let appMeta = {};
let portfolioChartInstance = null;
let horizonChartInstance = null;
let cobwebChartInstance = null;
let featuresChartInstance = null;

document.addEventListener("DOMContentLoaded", () => {
  setupTabs();
  loadMetadata();
  setupEventListeners();
  loadHistory();
});

// ==================== TABS CONTROLLER ====================
function setupTabs() {
  const navBtns = document.querySelectorAll(".nav-btn");
  navBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      navBtns.forEach((b) => b.classList.remove("active"));
      document.querySelectorAll(".tab-content").forEach((c) => c.classList.remove("active"));
      btn.classList.add("active");
      const targetId = btn.getAttribute("data-tab");
      document.getElementById(targetId).classList.add("active");

      if (targetId === "tab-history") {
        loadHistory();
      }
    });
  });
}

// ==================== LOAD METADATA & DROPDOWNS ====================
async function loadMetadata() {
  try {
    const res = await fetch("/api/meta");
    appMeta = await res.json();

    // 1. Populate States
    const stateSelect = document.getElementById("state-select");
    const singleState = document.getElementById("single-state");
    const states = Object.keys(appMeta.states_and_districts || {});

    stateSelect.innerHTML = "";
    singleState.innerHTML = "";
    states.forEach((st) => {
      const opt1 = new Option(st, st);
      const opt2 = new Option(st, st);
      stateSelect.add(opt1);
      singleState.add(opt2);
    });

    // Default select Karnataka if present
    if (states.includes("Karnataka")) {
      stateSelect.value = "Karnataka";
      singleState.value = "Karnataka";
    }

    updateDistricts("state-select", "district-select");
    updateDistricts("single-state", "single-district");

    // 2. Populate Crops
    const crops = appMeta.crops || [];
    const prevSelect = document.getElementById("previous-crop");
    const singleCrop = document.getElementById("single-crop");
    const cwCrop = document.getElementById("cw-crop-select");

    prevSelect.innerHTML = "";
    singleCrop.innerHTML = "";
    cwCrop.innerHTML = "";

    crops.forEach((c) => {
      prevSelect.add(new Option(c, c));
      singleCrop.add(new Option(c, c));
      cwCrop.add(new Option(c, c));
    });

    if (crops.includes("Rice")) prevSelect.value = "Rice";
    if (crops.includes("Maize")) {
      singleCrop.value = "Maize";
      cwCrop.value = "Maize";
    }

    // 3. Render Research Metrics & Feature Importances
    renderEvaluationMetrics(appMeta.evaluation_metrics, appMeta.best_yield_model);
    renderFeatureImportances(appMeta.top_features);

    // 4. Initialize District Crops & Directory
    updateDistrictCrops();
    initDirectoryTab();

    // Initial district defaults load
    loadDistrictDefaults();

  } catch (err) {
    console.error("Failed to load metadata:", err);
  }
}

function updateDistricts(stateElemId, distElemId) {
  const st = document.getElementById(stateElemId).value;
  const distSelect = document.getElementById(distElemId);
  const districts = (appMeta.states_and_districts && appMeta.states_and_districts[st]) || [];
  distSelect.innerHTML = "";
  districts.forEach((d) => distSelect.add(new Option(d, d)));

  if (stateElemId === "state-select") {
    updateDistrictCrops();
  }
}

function updateDistrictCrops() {
  const st = document.getElementById("state-select").value;
  const dist = document.getElementById("district-select").value;
  if (!st || !dist) return;

  const distNameLabel = document.getElementById("indicator-dist-name");
  if (distNameLabel) distNameLabel.textContent = dist;

  const cropsInfo = (appMeta.district_crops && appMeta.district_crops[st] && appMeta.district_crops[st][dist]) || [];
  const container = document.getElementById("indicator-crops-list");
  const prevSelect = document.getElementById("previous-crop");

  if (container) {
    container.innerHTML = "";
    if (cropsInfo.length === 0) {
      container.innerHTML = `<span style="font-size:0.75rem; color:#64748b;">All standard regional crops suitable.</span>`;
    } else {
      cropsInfo.forEach((item) => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "crop-pill";
        btn.innerHTML = `${item.crop} <span class="crop-yield">${item.avg_yield_t_ha} t/ha</span>`;
        btn.title = `Click to select ${item.crop} as previous crop (Avg Yield: ${item.avg_yield_t_ha} t/ha | Seasons: ${item.seasons})`;
        btn.addEventListener("click", () => {
          if (prevSelect) prevSelect.value = item.crop;
        });
        container.appendChild(btn);
      });
    }
  }

  // Also update previous crop dropdown options with yield info
  if (prevSelect && cropsInfo.length > 0) {
    const currentVal = prevSelect.value;
    prevSelect.innerHTML = "";
    cropsInfo.forEach((item) => {
      const opt = new Option(`${item.crop} (Avg: ${item.avg_yield_t_ha} t/ha)`, item.crop);
      prevSelect.add(opt);
    });
    if (currentVal && cropsInfo.some((c) => c.crop === currentVal)) {
      prevSelect.value = currentVal;
    }
  }
}

async function loadDistrictDefaults() {
  const st = document.getElementById("state-select").value;
  const dist = document.getElementById("district-select").value;
  if (!st || !dist) return;

  try {
    const res = await fetch(`/api/district-defaults?state=${encodeURIComponent(st)}&district=${encodeURIComponent(dist)}`);
    const data = await res.json();
    document.getElementById("soil-n").value = data.nitrogen || 240;
    document.getElementById("soil-p").value = data.phosphorus || 14;
    document.getElementById("soil-k").value = data.potassium || 210;
    document.getElementById("soil-ph").value = data.ph || 6.8;
    document.getElementById("temp").value = data.avg_temp || 26.0;
    document.getElementById("rainfall").value = data.rainfall || 650.0;
  } catch (e) {
    console.error("District defaults error:", e);
  }
}

// ==================== ALL DISTRICTS & CROPS DIRECTORY ====================
let allDistrictsFlat = [];

function initDirectoryTab() {
  if (!appMeta.district_crops) return;

  // Flatten directory
  allDistrictsFlat = [];
  const stateFilter = document.getElementById("dir-state-filter");
  const cropFilter = document.getElementById("dir-crop-filter");
  const searchInput = document.getElementById("dir-search-input");

  if (!stateFilter || !cropFilter) return;

  // Populate state filter
  const states = Object.keys(appMeta.district_crops).sort();
  stateFilter.innerHTML = `<option value="ALL">All States (${states.length} States)</option>`;
  states.forEach((s) => stateFilter.add(new Option(s, s)));

  // Populate crop filter
  const crops = appMeta.crops || [];
  cropFilter.innerHTML = `<option value="ALL">All Crops (${crops.length} Crops)</option>`;
  crops.forEach((c) => cropFilter.add(new Option(c, c)));

  // Compile flat district list
  states.forEach((st) => {
    Object.keys(appMeta.district_crops[st]).forEach((dist) => {
      const cropsList = appMeta.district_crops[st][dist];
      // Find top yielding crop
      let topCrop = cropsList[0] || {};
      cropsList.forEach((c) => {
        if (c.avg_yield_t_ha > (topCrop.avg_yield_t_ha || 0)) {
          topCrop = c;
        }
      });

      // Primary seasons
      const allSeasons = Array.from(new Set(cropsList.map((c) => c.seasons))).join(", ");

      allDistrictsFlat.push({
        state: st,
        district: dist,
        cropsList: cropsList,
        cropNames: cropsList.map((c) => c.crop),
        topCrop: topCrop,
        seasons: allSeasons
      });
    });
  });

  renderDirectoryTable();

  // Filter events
  stateFilter.addEventListener("change", renderDirectoryTable);
  cropFilter.addEventListener("change", renderDirectoryTable);
  searchInput.addEventListener("input", renderDirectoryTable);
}

function renderDirectoryTable() {
  const stateFilter = document.getElementById("dir-state-filter").value;
  const cropFilter = document.getElementById("dir-crop-filter").value;
  const searchVal = document.getElementById("dir-search-input").value.toLowerCase().trim();

  const tbody = document.querySelector("#directory-table tbody");
  if (!tbody) return;
  tbody.innerHTML = "";

  const filtered = allDistrictsFlat.filter((d) => {
    if (stateFilter !== "ALL" && d.state !== stateFilter) return false;
    if (cropFilter !== "ALL" && !d.cropNames.includes(cropFilter)) return false;
    if (searchVal && !d.district.toLowerCase().includes(searchVal) && !d.state.toLowerCase().includes(searchVal)) return false;
    return true;
  });

  document.getElementById("dir-count-badge").textContent = `${filtered.length} Districts Found`;

  if (filtered.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: #64748b;">No districts match the selected filters.</td></tr>`;
    return;
  }

  filtered.forEach((item) => {
    const tr = document.createElement("tr");
    const cropBadges = item.cropsList.slice(0, 5).map((c) => `<span class="badge" style="margin-right:2px; font-size:0.7rem;">${c.crop}</span>`).join(" ");
    const extraCount = item.cropsList.length > 5 ? `<span style="font-size:0.7rem; color:#64748b;">+${item.cropsList.length - 5} more</span>` : "";

    tr.innerHTML = `
      <td><strong>${item.state}</strong></td>
      <td><strong>${item.district}</strong></td>
      <td>${cropBadges} ${extraCount}</td>
      <td class="text-success"><strong>${item.topCrop.crop}</strong> (${item.topCrop.avg_yield_t_ha} t/ha)</td>
      <td><span class="badge badge-success">${item.seasons || "Kharif, Rabi"}</span></td>
    `;
    tbody.appendChild(tr);
  });
}

// ==================== EVENT LISTENERS ====================
function setupEventListeners() {
  // District cascading
  document.getElementById("state-select").addEventListener("change", () => {
    updateDistricts("state-select", "district-select");
    loadDistrictDefaults();
  });
  document.getElementById("district-select").addEventListener("change", () => {
    updateDistrictCrops();
    loadDistrictDefaults();
  });

  document.getElementById("single-state").addEventListener("change", () => {
    updateDistricts("single-state", "single-district");
  });

  // Optimize form submit
  document.getElementById("optimize-form").addEventListener("submit", handleOptimize);

  // Single Predict form submit
  document.getElementById("single-predict-form").addEventListener("submit", handleSinglePredict);

  // Cobweb slider
  const cwSlider = document.getElementById("cw-adoption-slider");
  cwSlider.addEventListener("input", (e) => {
    document.getElementById("cw-rate-val").textContent = `${e.target.value}%`;
  });
  document.getElementById("btn-run-cobweb").addEventListener("click", handleCobwebSimulate);

  // Refresh history button
  document.getElementById("btn-refresh-history").addEventListener("click", loadHistory);
}

// ==================== TAB 1: OPTIMIZE PORTFOLIO ====================
async function handleOptimize(e) {
  e.preventDefault();
  const btn = document.getElementById("btn-optimize");
  btn.disabled = true;
  btn.textContent = "⏳ Solving Optimal Allocation...";

  const payload = {
    farmer_name: document.getElementById("farmer-name").value || "Farmer",
    state: document.getElementById("state-select").value,
    district: document.getElementById("district-select").value,
    farm_area_ha: parseFloat(document.getElementById("farm-area").value),
    previous_crop: document.getElementById("previous-crop").value,
    season: document.getElementById("season-select").value,
    risk_preference: document.getElementById("risk-pref").value,
    max_crops: parseInt(document.getElementById("max-crops").value),
    adoption_rate_pct: 0.0,
    nitrogen: parseFloat(document.getElementById("soil-n").value) || undefined,
    phosphorus: parseFloat(document.getElementById("soil-p").value) || undefined,
    potassium: parseFloat(document.getElementById("soil-k").value) || undefined,
    ph: parseFloat(document.getElementById("soil-ph").value) || undefined,
    avg_temp: parseFloat(document.getElementById("temp").value) || undefined,
    rainfall: parseFloat(document.getElementById("rainfall").value) || undefined
  };

  try {
    const res = await fetch("/api/optimize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    renderOptimizationResults(data);
  } catch (err) {
    alert("Optimization failed: " + err.message);
  } finally {
    btn.disabled = false;
    btn.textContent = "⚡ Optimize Crop Portfolio";
  }
}

function renderOptimizationResults(data) {
  document.getElementById("opt-empty-state").classList.add("hidden");
  document.getElementById("opt-results-content").classList.remove("hidden");

  // Summary KPIs
  document.getElementById("kpi-profit").textContent = `₹${Math.round(data.totals.net_profit_rs).toLocaleString("en-IN")}`;
  document.getElementById("kpi-revenue").textContent = `₹${Math.round(data.totals.expected_revenue_rs).toLocaleString("en-IN")}`;
  document.getElementById("kpi-switch").textContent = `₹${Math.round(data.totals.switching_cost_rs).toLocaleString("en-IN")}`;
  document.getElementById("kpi-cultivation").textContent = `₹${Math.round(data.totals.cultivation_cost_rs).toLocaleString("en-IN")}`;
  document.getElementById("roi-badge").textContent = `ROI: +${data.totals.roi_pct}%`;

  // Comparison Banner
  const comp = data.comparison;
  const naiveCrop = comp.naive_mono_plan.crop;
  const switchSave = comp.switching_cost_savings_rs;
  const riskRed = comp.risk_reduction_pct;

  let compMsg = `Traditional approach would plant 100% <strong>${naiveCrop}</strong>. `;
  if (switchSave > 0) {
    compMsg += `AgriShift saved <strong>₹${Math.round(switchSave).toLocaleString("en-IN")}</strong> in transition & machinery costs. `;
  }
  compMsg += `Portfolio diversification reduced price volatility risk by <strong>${riskRed}%</strong>.`;
  document.getElementById("comp-text").innerHTML = compMsg;

  // Table
  const tbody = document.querySelector("#allocation-table tbody");
  tbody.innerHTML = "";
  data.portfolio.forEach((p) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><strong>${p.crop}</strong></td>
      <td>${p.allocated_ha} ha (${p.percentage_area}%)</td>
      <td>${p.predicted_yield_t_ha} t/ha</td>
      <td>₹${Math.round(p.price_rs_tonne).toLocaleString("en-IN")}</td>
      <td class="text-success"><strong>₹${Math.round(p.net_profit_rs).toLocaleString("en-IN")}</strong></td>
    `;
    tbody.appendChild(tr);
  });

  // Chart
  renderPortfolioChart(data.portfolio);
}

function renderPortfolioChart(portfolio) {
  const ctx = document.getElementById("portfolioChart").getContext("2d");
  if (portfolioChartInstance) portfolioChartInstance.destroy();

  const labels = portfolio.map((p) => `${p.crop} (${p.allocated_ha}ha)`);
  const values = portfolio.map((p) => p.allocated_ha);
  const colors = ["#16a34a", "#0284c7", "#f59e0b", "#8b5cf6", "#ec4899"];

  portfolioChartInstance = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: labels,
      datasets: [{
        data: values,
        backgroundColor: colors.slice(0, values.length),
        borderWidth: 2,
        borderColor: "#ffffff"
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: "bottom" },
        tooltip: {
          callbacks: {
            label: (item) => ` ${item.label}: ${item.raw} ha`
          }
        }
      }
    }
  });
}

// ==================== TAB 2: SINGLE PREDICT ====================
async function handleSinglePredict(e) {
  e.preventDefault();
  const crop = document.getElementById("single-crop").value;
  const state = document.getElementById("single-state").value;
  const district = document.getElementById("single-district").value;
  const season = document.getElementById("single-season").value;

  try {
    // 1. Fetch defaults for district
    const defRes = await fetch(`/api/district-defaults?state=${encodeURIComponent(state)}&district=${encodeURIComponent(district)}`);
    const defaults = await defRes.json();

    // 2. Predict Yield
    const yieldRes = await fetch("/api/predict-yield", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        crop, state, district, season,
        ...defaults
      })
    });
    const yieldData = await yieldRes.json();

    // 3. Forecast Price
    const priceRes = await fetch("/api/forecast-price", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ crop, start_month: 10 })
    });
    const priceData = await priceRes.json();

    renderSingleResults(crop, state, district, yieldData, priceData);
  } catch (err) {
    alert("Prediction failed: " + err.message);
  }
}

function renderSingleResults(crop, state, district, yieldData, priceData) {
  document.getElementById("single-empty-state").classList.add("hidden");
  document.getElementById("single-results-content").classList.remove("hidden");

  document.getElementById("single-title").textContent = `${crop} in ${district}, ${state}`;
  document.getElementById("single-yield").textContent = `${yieldData.predicted_yield_tonnes_ha} t/ha (${yieldData.predicted_yield_kg_ha} kg/ha)`;
  document.getElementById("single-price").textContent = `₹${Math.round(priceData.current_price_rs_tonne).toLocaleString("en-IN")} / t`;
  document.getElementById("single-volatility").textContent = `${(priceData.volatility_ratio * 100).toFixed(1)}%`;

  // Horizons
  const hGrid = document.getElementById("horizon-grid");
  hGrid.innerHTML = `
    <div class="horizon-box">
      <h5>Next Month</h5>
      <span class="price">₹${Math.round(priceData["1_month"].price_rs_tonne).toLocaleString("en-IN")}</span>
    </div>
    <div class="horizon-box">
      <h5>3 Months</h5>
      <span class="price">₹${Math.round(priceData["3_month"].price_rs_tonne).toLocaleString("en-IN")}</span>
    </div>
    <div class="horizon-box">
      <h5>6 Months</h5>
      <span class="price">₹${Math.round(priceData["6_month"].price_rs_tonne).toLocaleString("en-IN")}</span>
    </div>
    <div class="horizon-box">
      <h5>12 Months</h5>
      <span class="price">₹${Math.round(priceData["12_month"].price_rs_tonne).toLocaleString("en-IN")}</span>
    </div>
  `;

  // Horizon Line Chart
  const ctx = document.getElementById("priceHorizonChart").getContext("2d");
  if (horizonChartInstance) horizonChartInstance.destroy();

  const labels = ["Current", "1 Month", "3 Months", "6 Months", "12 Months"];
  const values = [
    priceData.current_price_rs_tonne,
    priceData["1_month"].price_rs_tonne,
    priceData["3_month"].price_rs_tonne,
    priceData["6_month"].price_rs_tonne,
    priceData["12_month"].price_rs_tonne
  ];

  horizonChartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [{
        label: `${crop} Forecast (₹/tonne)`,
        data: values,
        borderColor: "#0284c7",
        backgroundColor: "rgba(2, 132, 199, 0.1)",
        fill: true,
        tension: 0.3,
        pointRadius: 5
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          title: { display: true, text: "Price (₹/tonne)" }
        }
      }
    }
  });
}

// ==================== TAB 3: COBWEB SIMULATION ====================
async function handleCobwebSimulate() {
  const crop = document.getElementById("cw-crop-select").value;
  try {
    const res = await fetch("/api/cobweb-simulate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ crop })
    });
    const data = await res.json();
    renderCobwebResults(data);
  } catch (err) {
    alert("Cobweb simulation error: " + err.message);
  }
}

function renderCobwebResults(data) {
  const tbody = document.querySelector("#cobweb-table tbody");
  tbody.innerHTML = "";

  const labels = [];
  const prices = [];
  const supplies = [];

  data.scenarios.forEach((s) => {
    labels.push(`${s.adoption_rate_pct}%`);
    prices.push(s.adjusted_price_rs_tonne);
    supplies.push(s.additional_supply_tonnes);

    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><strong>${s.adoption_rate_pct}%</strong></td>
      <td>+${Math.round(s.additional_supply_tonnes)} t</td>
      <td>+${s.market_supply_pct_increase}%</td>
      <td class="text-primary"><strong>₹${Math.round(s.adjusted_price_rs_tonne).toLocaleString("en-IN")}/t</strong></td>
      <td class="text-warning">-${s.price_drop_pct}%</td>
    `;
    tbody.appendChild(tr);
  });

  // Chart
  const ctx = document.getElementById("cobwebChart").getContext("2d");
  if (cobwebChartInstance) cobwebChartInstance.destroy();

  cobwebChartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Adjusted Price (₹/tonne)",
          data: prices,
          borderColor: "#dc2626",
          backgroundColor: "rgba(220, 38, 38, 0.1)",
          yAxisID: "yPrice",
          tension: 0.2
        },
        {
          label: "Extra Supply (Tonnes)",
          data: supplies,
          borderColor: "#16a34a",
          backgroundColor: "rgba(22, 163, 74, 0.1)",
          yAxisID: "ySupply",
          tension: 0.2
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        yPrice: {
          type: "linear",
          position: "left",
          title: { display: true, text: "Adjusted Price (₹/t)" }
        },
        ySupply: {
          type: "linear",
          position: "right",
          title: { display: true, text: "Extra Supply (Tonnes)" },
          grid: { drawOnChartArea: false }
        }
      }
    }
  });
}

// ==================== TAB 4: RESEARCH METRICS ====================
function renderEvaluationMetrics(metrics, bestModel) {
  if (!metrics) return;
  const tbody = document.querySelector("#metrics-table tbody");
  tbody.innerHTML = "";

  Object.entries(metrics).forEach(([model, val]) => {
    const isBest = model === bestModel;
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><strong>${model.replace("_", " ")}</strong></td>
      <td><span class="badge ${isBest ? "badge-success" : ""}">${val.R2_Score}</span></td>
      <td>${val.RMSE_tonnes_ha}</td>
      <td>${val.MAE_tonnes_ha}</td>
      <td>${isBest ? "⭐ Recommended" : "Baseline"}</td>
    `;
    tbody.appendChild(tr);
  });
}

function renderFeatureImportances(features) {
  if (!features) return;
  const ctx = document.getElementById("featuresChart").getContext("2d");
  if (featuresChartInstance) featuresChartInstance.destroy();

  const labels = Object.keys(features).slice(0, 10).map((f) => f.replace("Crop_", "Crop: ").replace("_kg_ha", "").replace("_pct", " %"));
  const values = Object.values(features).slice(0, 10);

  featuresChartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "Feature Importance Score",
        data: values,
        backgroundColor: "#16a34a",
        borderRadius: 4
      }]
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      }
    }
  });
}

// ==================== TAB 5: HISTORY ====================
async function loadHistory() {
  try {
    const res = await fetch("/api/recommendation-history?limit=15");
    const data = await res.json();
    const tbody = document.querySelector("#history-table tbody");
    tbody.innerHTML = "";

    if (!data || data.length === 0) {
      tbody.innerHTML = `<tr><td colspan="9" style="text-align: center;">No saved recommendations yet. Run an optimization to see it here!</td></tr>`;
      return;
    }

    data.forEach((row) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>#${row.id}</td>
        <td>${row.timestamp}</td>
        <td><strong>${row.farmer_name}</strong></td>
        <td>${row.district}, ${row.state}</td>
        <td>${row.farm_area_ha} ha</td>
        <td>${row.previous_crop}</td>
        <td>${row.allocated_crops}</td>
        <td class="text-success"><strong>₹${Math.round(row.total_net_profit_rs).toLocaleString("en-IN")}</strong></td>
        <td class="text-warning">₹${Math.round(row.total_switching_cost_rs).toLocaleString("en-IN")}</td>
      `;
      tbody.appendChild(tr);
    });
  } catch (e) {
    console.error("History fetch error:", e);
  }
}
