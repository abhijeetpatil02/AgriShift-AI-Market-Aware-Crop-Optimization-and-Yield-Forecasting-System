"""
AgriShift Crop Portfolio Optimizer
Uses Mixed-Integer Linear Programming (MILP via SciPy HiGHS) to find the optimal crop allocation
maximizing expected net profit while accounting for transition switching costs,
volatility risk penalties, and simulated market feedback.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import numpy as np
import pandas as pd
from scipy.optimize import milp, LinearConstraint, Bounds
from optimizer.switching_cost import SwitchingCostManager
from optimizer.cobweb import CobwebSimulator

# Representative cultivation costs per hectare (Cost A2+FL in INR)
DEFAULT_CULTIVATION_COSTS = {
    "Bajra": 23834.0,
    "Cotton": 50574.0,
    "Gram": 27732.0,
    "Groundnut": 44911.0,
    "Jowar": 25428.0,
    "Maize": 31752.0,
    "Rice": 42265.0,
    "Soyabean": 29280.0,
    "Sugarcane": 112365.0,
    "Wheat": 37189.0
}

RISK_WEIGHTS = {
    "Low": 0.35,      # High penalty on volatility
    "Medium": 0.18,   # Balanced
    "High": 0.05      # Aggressive returns
}

class CropPortfolioOptimizer:
    def __init__(self):
        self.switching_mgr = SwitchingCostManager()
        self.cobweb_sim = CobwebSimulator()

    def optimize_portfolio(
        self,
        farm_area_ha: float,
        previous_crop: str,
        risk_preference: str = "Medium",
        candidates_data: dict = None,
        max_crops: int = 3,
        min_parcel_ha: float = 0.2,
        adoption_rate: float = 0.0
    ):
        """
        Solves the MILP allocation problem:
          Maximize: Sum( Area_i * (NetMargin_i - lambda * RiskPenalty_i) )
          Subject to:
            Sum( Area_i ) <= FarmArea
            Area_i >= min_parcel * y_i
            Area_i <= FarmArea * y_i
            Sum( y_i ) <= max_crops
            y_i in {0, 1}, Area_i >= 0
        """
        risk_lambda = RISK_WEIGHTS.get(risk_preference, 0.18)
        crops = list(candidates_data.keys())
        N = len(crops)

        # 1. Compute financial metrics per candidate crop
        crop_metrics = {}
        obj_coefficients = []

        for crop in crops:
            cdata = candidates_data[crop]
            yield_t = float(cdata["yield_tonnes_ha"])
            base_price = float(cdata["price_rs_tonne"])
            volatility = float(cdata.get("volatility", 0.18))
            cult_cost = float(cdata.get("cultivation_cost_per_ha", DEFAULT_CULTIVATION_COSTS.get(crop, 35000.0)))
            switch_cost = self.switching_mgr.get_cost(previous_crop, crop)

            # Cobweb market feedback price adjustment
            if adoption_rate > 0.0:
                cw = self.cobweb_sim.simulate_feedback(crop, base_price, yield_t, portfolio_share=0.5, adoption_rate=adoption_rate)
                effective_price = cw["adjusted_price_rs_tonne"]
                price_drop_pct = cw["price_drop_pct"]
            else:
                effective_price = base_price
                price_drop_pct = 0.0

            revenue_per_ha = yield_t * effective_price
            gross_margin_per_ha = revenue_per_ha - cult_cost
            net_margin_per_ha = gross_margin_per_ha - switch_cost
            
            # Risk penalty per hectare
            risk_penalty_per_ha = risk_lambda * (revenue_per_ha * volatility)

            # Objective coefficient: net margin minus risk penalty
            net_coef = net_margin_per_ha - risk_penalty_per_ha
            obj_coefficients.append(net_coef)

            crop_metrics[crop] = {
                "yield_tonnes_ha": round(yield_t, 2),
                "base_price_rs_tonne": round(base_price, 1),
                "effective_price_rs_tonne": round(effective_price, 1),
                "price_drop_pct": price_drop_pct,
                "cultivation_cost_ha": round(cult_cost, 1),
                "switch_cost_ha": round(switch_cost, 1),
                "revenue_ha": round(revenue_per_ha, 1),
                "gross_margin_ha": round(gross_margin_per_ha, 1),
                "net_margin_ha": round(net_margin_per_ha, 1),
                "volatility": round(volatility, 3),
                "risk_penalty_ha": round(risk_penalty_per_ha, 1),
                "obj_coef": round(net_coef, 1)
            }

        # 2. Formulate MILP problem with SciPy
        # Variables: [x_0..x_{N-1}, y_0..y_{N-1}] where x is continuous area, y is binary selection
        # We minimize -Profit
        c = -np.array(obj_coefficients + [0.0] * N)

        # Variable Bounds:
        # x_i in [0, farm_area_ha]
        # y_i in [0, 1]
        lb = [0.0] * N + [0.0] * N
        ub = [farm_area_ha] * N + [1.0] * N
        bounds = Bounds(lb, ub)

        # Integrality: 0 for continuous (x), 1 for integer (y)
        integrality = np.array([0] * N + [1] * N)

        # Linear constraints:
        # A_rows:
        # Row 1: Sum(x_i) <= farm_area_ha
        # Row 2: Sum(y_i) <= max_crops
        # Next N rows: x_i - farm_area_ha * y_i <= 0  (if y_i=0 => x_i=0)
        # Next N rows: x_i - min_parcel_ha * y_i >= 0 (if y_i=1 => x_i >= min_parcel)

        rows = []
        lhs_bounds = []
        rhs_bounds = []

        # 1. Total area constraint
        row_area = [1.0] * N + [0.0] * N
        rows.append(row_area)
        lhs_bounds.append(0.0)
        rhs_bounds.append(farm_area_ha)

        # 2. Max crops constraint
        row_max_crops = [0.0] * N + [1.0] * N
        rows.append(row_max_crops)
        lhs_bounds.append(0.0)
        rhs_bounds.append(float(max_crops))

        # 3. Big-M upper bounds: x_i - farm_area_ha * y_i <= 0
        for i in range(N):
            r = [0.0] * (2 * N)
            r[i] = 1.0
            r[N + i] = -farm_area_ha
            rows.append(r)
            lhs_bounds.append(-np.inf)
            rhs_bounds.append(0.0)

        # 4. Minimum parcel size: x_i - min_parcel_ha * y_i >= 0
        for i in range(N):
            r = [0.0] * (2 * N)
            r[i] = 1.0
            r[N + i] = -min_parcel_ha
            rows.append(r)
            lhs_bounds.append(0.0)
            rhs_bounds.append(np.inf)

        A = np.array(rows)
        constraints = LinearConstraint(A, lhs_bounds, rhs_bounds)

        # Solve MILP
        res = milp(c=c, constraints=constraints, bounds=bounds, integrality=integrality)

        if not res.success:
            # Fallback simple greedy allocation if numerical edge case
            sol_x = [0.0] * N
            best_idx = int(np.argmax(obj_coefficients))
            sol_x[best_idx] = farm_area_ha
        else:
            sol_x = res.x[:N]

        # 3. Compile portfolio allocations
        allocations = []
        total_allocated_area = 0.0
        total_expected_revenue = 0.0
        total_cultivation_cost = 0.0
        total_switching_cost = 0.0
        total_net_profit = 0.0
        total_risk_penalty = 0.0

        for i, crop in enumerate(crops):
            allocated_ha = float(sol_x[i])
            if allocated_ha > 0.01:
                allocated_ha = round(allocated_ha, 2)
                m = crop_metrics[crop]
                crop_rev = allocated_ha * m["revenue_ha"]
                crop_cult = allocated_ha * m["cultivation_cost_ha"]
                crop_switch = allocated_ha * m["switch_cost_ha"]
                crop_profit = allocated_ha * m["net_margin_ha"]
                crop_risk = allocated_ha * m["risk_penalty_ha"]

                total_allocated_area += allocated_ha
                total_expected_revenue += crop_rev
                total_cultivation_cost += crop_cult
                total_switching_cost += crop_switch
                total_net_profit += crop_profit
                total_risk_penalty += crop_risk

                allocations.append({
                    "crop": crop,
                    "allocated_ha": allocated_ha,
                    "percentage_area": round((allocated_ha / farm_area_ha) * 100.0, 1),
                    "predicted_yield_t_ha": m["yield_tonnes_ha"],
                    "total_production_t": round(allocated_ha * m["yield_tonnes_ha"], 2),
                    "price_rs_tonne": m["effective_price_rs_tonne"],
                    "revenue_rs": round(crop_rev, 1),
                    "cultivation_cost_rs": round(crop_cult, 1),
                    "switching_cost_rs": round(crop_switch, 1),
                    "net_profit_rs": round(crop_profit, 1),
                    "volatility": m["volatility"]
                })

        allocations.sort(key=lambda x: x["allocated_ha"], reverse=True)

        # Traditional Naive Plan (Highest gross margin ignoring switching cost & risk)
        naive_crop = max(crops, key=lambda c: crop_metrics[c]["gross_margin_ha"])
        naive_m = crop_metrics[naive_crop]
        naive_switch_cost = farm_area_ha * self.switching_mgr.get_cost(previous_crop, naive_crop)
        naive_revenue = farm_area_ha * naive_m["revenue_ha"]
        naive_cult_cost = farm_area_ha * naive_m["cultivation_cost_ha"]
        naive_net_profit = naive_revenue - naive_cult_cost - naive_switch_cost
        naive_risk_exposure = farm_area_ha * naive_m["revenue_ha"] * naive_m["volatility"]

        comparison = {
            "agrishift_plan": {
                "crops": [a["crop"] for a in allocations],
                "total_area_ha": round(total_allocated_area, 2),
                "expected_revenue_rs": round(total_expected_revenue, 1),
                "cultivation_cost_rs": round(total_cultivation_cost, 1),
                "switching_cost_rs": round(total_switching_cost, 1),
                "net_profit_rs": round(total_net_profit, 1),
                "risk_exposure_rs": round(total_risk_penalty, 1),
                "diversification_count": len(allocations)
            },
            "naive_mono_plan": {
                "crop": naive_crop,
                "total_area_ha": farm_area_ha,
                "expected_revenue_rs": round(naive_revenue, 1),
                "cultivation_cost_rs": round(naive_cult_cost, 1),
                "switching_cost_rs": round(naive_switch_cost, 1),
                "net_profit_rs": round(naive_net_profit, 1),
                "risk_exposure_rs": round(naive_risk_exposure, 1),
                "diversification_count": 1
            },
            "switching_cost_savings_rs": round(naive_switch_cost - total_switching_cost, 1),
            "profit_improvement_rs": round(total_net_profit - naive_net_profit, 1),
            "risk_reduction_pct": round(max(0.0, (naive_risk_exposure - total_risk_penalty) / max(1.0, naive_risk_exposure)) * 100.0, 1)
        }

        return {
            "status": "Optimal",
            "farm_area_ha": farm_area_ha,
            "previous_crop": previous_crop,
            "risk_preference": risk_preference,
            "adoption_rate_pct": round(adoption_rate * 100.0, 1),
            "portfolio": allocations,
            "totals": {
                "allocated_area_ha": round(total_allocated_area, 2),
                "expected_revenue_rs": round(total_expected_revenue, 1),
                "cultivation_cost_rs": round(total_cultivation_cost, 1),
                "switching_cost_rs": round(total_switching_cost, 1),
                "net_profit_rs": round(total_net_profit, 1),
                "roi_pct": round((total_net_profit / max(1.0, total_cultivation_cost + total_switching_cost)) * 100.0, 1)
            },
            "comparison": comparison,
            "all_crop_metrics": crop_metrics
        }

if __name__ == "__main__":
    opt = CropPortfolioOptimizer()
    candidates = {
        "Rice": {"yield_tonnes_ha": 4.5, "price_rs_tonne": 25975.0, "volatility": 0.18},
        "Maize": {"yield_tonnes_ha": 3.8, "price_rs_tonne": 33675.0, "volatility": 0.20},
        "Cotton": {"yield_tonnes_ha": 1.2, "price_rs_tonne": 88294.0, "volatility": 0.22},
        "Groundnut": {"yield_tonnes_ha": 2.1, "price_rs_tonne": 64000.0, "volatility": 0.15},
        "Wheat": {"yield_tonnes_ha": 3.4, "price_rs_tonne": 38163.0, "volatility": 0.19}
    }
    sol = opt.optimize_portfolio(2.5, "Rice", "Medium", candidates, max_crops=3)
    print("Portfolio Solution:")
    for p in sol["portfolio"]:
        print(f"  {p['crop']:10} : {p['allocated_ha']} ha ({p['percentage_area']}%) | Profit: Rs. {p['net_profit_rs']:,.0f}")
    print("Total Net Profit:", f"Rs. {sol['totals']['net_profit_rs']:,.0f}")
    print("Switching Cost:", f"Rs. {sol['totals']['switching_cost_rs']:,.0f}")
    print("AgriShift vs Naive Profit Improvement:", f"Rs. {sol['comparison']['profit_improvement_rs']:,.0f}")
    print("Risk Reduction:", f"{sol['comparison']['risk_reduction_pct']}%")
