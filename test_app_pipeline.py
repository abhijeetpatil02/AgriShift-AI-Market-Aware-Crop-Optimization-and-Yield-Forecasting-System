import app
import json

client = app.app.test_client()
payload = {
    'district': 'DHARWAD',
    'season': 'Kharif',
    'farm_area': 2.5,
    'N': 80,
    'P': 48,
    'K': 25,
    'pH': 6.5,
    'temperature': 26,
    'humidity': 68,
    'rainfall': 650
}

response = client.post('/api/recommend', json=payload)
data = response.get_json()

print("=" * 70)
print("TESTING FULL AGRISHIFT PIPELINE (MODEL 1 + MODEL 2 + MARKET ECONOMICS)")
print("=" * 70)
print(f"Status: {response.status_code} | Success: {data.get('success')}")
print(f"District: {data.get('district')} | Season: {data.get('season')} | Farm Size: {data.get('farm_area_ha')} Ha")
print(f"Model 2 Info: {data.get('model2_info')}\n")

for c in data.get('recommendations', []):
    print(f"Rank {c['rank']}: {c['crop']} ({c['category']})")
    print(f"  [Model 1 - Recommendation]:  Match Score: {c['model1_match_score']}%")
    print(f"  [Model 2 - Yield Prediction]: {c['model2_predicted_yield_ha']} t/ha -> Total Harvest: {c['total_production_tonnes']} Tonnes ({c['total_production_quintals']} Quintals)")
    print(f"  [Market-Aware Economics]:    Mandi Price: Rs.{c['mandi_price_qtl']}/qtl ({c['mandi_location']})")
    print(f"                               Gross Revenue: Rs.{c['gross_revenue_inr']:,} | Cultivation Cost: Rs.{c['cultivation_cost_inr']:,} | Net Profit: Rs.{c['net_profit_inr']:,}")
    print("-" * 70)
