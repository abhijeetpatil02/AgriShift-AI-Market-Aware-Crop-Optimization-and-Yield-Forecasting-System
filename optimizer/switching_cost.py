"""
Switching Cost Module
Models the economic friction and land-preparation costs of switching crops.
Derived from seed, fertilizer, machinery, and land transition requirements.
"""

import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MATRIX_PATH = os.path.join(BASE_DIR, "data", "processed", "crop_transition_matrix.csv")

class SwitchingCostManager:
    def __init__(self):
        self.df = pd.read_csv(MATRIX_PATH)
        self.lookup = {}
        for _, row in self.df.iterrows():
            from_c = str(row["From_Crop"]).strip()
            to_c = str(row["To_Crop"]).strip()
            cost = float(row["Transition_Cost_per_ha_INR"])
            self.lookup[(from_c, to_c)] = cost

    def get_cost(self, from_crop: str, to_crop: str) -> float:
        """Returns the switching cost in INR/ha when transitioning from from_crop to to_crop."""
        if from_crop == to_crop:
            return 0.0
        return self.lookup.get((from_crop, to_crop), 3500.0)

    def get_all_transitions_for(self, from_crop: str):
        """Returns switching costs from a given previous crop to all possible destination crops."""
        results = {}
        crops = sorted(list(self.df["To_Crop"].unique()))
        for c in crops:
            results[c] = self.get_cost(from_crop, c)
        return results

    def get_matrix_pivot(self):
        """Returns full pivot table for display."""
        pivot = self.df.pivot(index="From_Crop", columns="To_Crop", values="Transition_Cost_per_ha_INR").round(1)
        return pivot.to_dict()

if __name__ == "__main__":
    mgr = SwitchingCostManager()
    print("Switching from Rice:")
    for crop, cost in mgr.get_all_transitions_for("Rice").items():
        print(f"  Rice -> {crop:10} : ₹{cost:,.1f}/ha")
