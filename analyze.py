# analyze.py
# Breakdown-risk analysis for Vossberg Mobility fleet (120 cars, historical data).
#
# KEY FINDINGS:
#   - km_since_service and load_factor are the strongest predictors of breakdown.
#     Cars that broke down had, on average, 61% more km since their last service (11,678 vs 7,261)
#     and 19% higher load factor (0.60 vs 0.51).
#   - The obvious suspects — total odometer mileage and age — predict almost nothing.
#     The two groups are virtually identical on both: mean odometer differs by only 146 km
#     (53,448 vs 53,302) and mean age by 0.01 years. High-mileage, older cars do not break
#     down more than low-mileage, young ones in this fleet.
#
# RISK SCORE:
#   A simple 0–100 score built from the two separating factors:
#     50% weight → km_since_service normalised to [0, 1] across the fleet
#     50% weight → load_factor normalised to [0, 1] across the fleet
#   This keeps the model transparent and auditable without any machine learning.

import pandas as pd

df = pd.read_csv("fleet_history.csv")

# --- 1. Compare group means to find which columns separate the two groups ---
print("=== Group means: broke_down=1 vs broke_down=0 ===")
print(df.groupby("broke_down")[
    ["odometer_km", "km_since_service", "avg_daily_km", "load_factor", "age_years"]
].mean().round(2).to_string())
print()

# --- 2. Normalise the two predictors to [0, 1] ---
def normalise(series: pd.Series) -> pd.Series:
    """Min-max normalise a series to [0, 1]."""
    lo, hi = series.min(), series.max()
    return (series - lo) / (hi - lo)

df["score_km_since"] = normalise(df["km_since_service"])
df["score_load"]     = normalise(df["load_factor"])

# --- 3. Build the composite risk score (0–100) ---
df["risk_score"] = ((df["score_km_since"] * 0.5 + df["score_load"] * 0.5) * 100).round(1)

# --- 4. Print cars ranked by risk, highest first ---
ranked = df[["car_id", "km_since_service", "load_factor", "risk_score", "broke_down"]].sort_values(
    "risk_score", ascending=False
)

print("=== Fleet ranked by breakdown risk (highest first) ===")
print(f"{'car_id':<12} {'km_since_svc':>13} {'load_factor':>12} {'risk_score':>11} {'broke_down':>11}")
print("-" * 62)
for _, row in ranked.iterrows():
    flag = " ← broke" if row["broke_down"] == 1 else ""
    print(
        f"{row['car_id']:<12} {int(row['km_since_service']):>13,} "
        f"{row['load_factor']:>12.2f} {row['risk_score']:>11.1f}{flag}"
    )

# --- 5. Quick validation: do high-risk cars actually break down more? ---
top_quartile    = ranked.head(30)
bottom_quartile = ranked.tail(30)
top_rate    = top_quartile["broke_down"].mean()
bottom_rate = bottom_quartile["broke_down"].mean()
print()
print("=== Score validation ===")
print(f"Breakdown rate in top-30 risk cars:    {top_rate:.0%}")
print(f"Breakdown rate in bottom-30 risk cars: {bottom_rate:.0%}")
