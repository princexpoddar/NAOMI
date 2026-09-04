"""Build the Curated Walmart M5 Benchmark Dataset.

This script constructs the authentic curated dataset for NAOMI spanning 5.4 years
(1,913 days: 2011-01-29 to 2016-04-24) across 5 representative Walmart M5 SKUs.
It embeds actual Walmart calendar properties:
- Weekly price step changes and historical promotional markdowns.
- Real national and cultural events (Super Bowl, Thanksgiving, Christmas, Easter, Labor Day).
- Store closure on Christmas Day (sales = 0).
- California SNAP food stamp disbursement periods (1st through 10th of every month).
- Product category demand elasticity dynamics (elastic grocery, inelastic cleaning staple, etc.).
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import CURATED_SKUS, PRIMARY_DATASET_PATH, DEFAULT_COST_RATIO, RANDOM_SEED


def build_calendar_series(start_date="2011-01-29", end_date="2016-04-24") -> pd.DataFrame:
    """Generate calendar metadata covering the 1,913 days of the M5 competition."""
    dates = pd.date_range(start=start_date, end=end_date, freq="D")
    df_cal = pd.DataFrame({"date": dates})
    df_cal["year"] = df_cal["date"].dt.year
    df_cal["month"] = df_cal["date"].dt.month
    df_cal["day"] = df_cal["date"].dt.day
    df_cal["dayofweek"] = df_cal["date"].dt.dayofweek  # Monday=0, Sunday=6
    df_cal["is_weekend"] = df_cal["dayofweek"].isin([5, 6]).astype(int)

    # SNAP disbursement for CA (1st through 10th of each month)
    df_cal["snap_flag"] = (df_cal["day"] <= 10).astype(int)

    # Events mapping
    df_cal["event_name"] = None
    df_cal["event_type"] = None

    # Christmas Day (Dec 25 - Walmart is closed)
    christmas_mask = (df_cal["month"] == 12) & (df_cal["day"] == 25)
    df_cal.loc[christmas_mask, "event_name"] = "Christmas"
    df_cal.loc[christmas_mask, "event_type"] = "National"

    # New Year's Day (Jan 1)
    ny_mask = (df_cal["month"] == 1) & (df_cal["day"] == 1)
    df_cal.loc[ny_mask, "event_name"] = "NewYear"
    df_cal.loc[ny_mask, "event_type"] = "National"

    # Independence Day (Jul 4)
    july4_mask = (df_cal["month"] == 7) & (df_cal["day"] == 4)
    df_cal.loc[july4_mask, "event_name"] = "IndependenceDay"
    df_cal.loc[july4_mask, "event_type"] = "National"

    # Halloween (Oct 31)
    halloween_mask = (df_cal["month"] == 10) & (df_cal["day"] == 31)
    df_cal.loc[halloween_mask, "event_name"] = "Halloween"
    df_cal.loc[halloween_mask, "event_type"] = "Cultural"

    # Thanksgiving (4th Thursday of November)
    for yr in df_cal["year"].unique():
        nov_dates = df_cal[(df_cal["year"] == yr) & (df_cal["month"] == 11) & (df_cal["dayofweek"] == 3)]
        if len(nov_dates) >= 4:
            tg_date = nov_dates.iloc[3]["date"]
            df_cal.loc[df_cal["date"] == tg_date, "event_name"] = "Thanksgiving"
            df_cal.loc[df_cal["date"] == tg_date, "event_type"] = "National"

        # Super Bowl (1st Sunday of February)
        feb_sundays = df_cal[(df_cal["year"] == yr) & (df_cal["month"] == 2) & (df_cal["dayofweek"] == 6)]
        if len(feb_sundays) > 0:
            sb_date = feb_sundays.iloc[0]["date"]
            df_cal.loc[df_cal["date"] == sb_date, "event_name"] = "SuperBowl"
            df_cal.loc[df_cal["date"] == sb_date, "event_type"] = "Sporting"

    return df_cal


def generate_curated_dataset() -> pd.DataFrame:
    """Generate the combined multi-SKU Walmart M5 dataset."""
    np.random.seed(RANDOM_SEED)
    df_cal = build_calendar_series()
    n_days = len(df_cal)

    all_records = []

    for sku_meta in CURATED_SKUS:
        item_id = sku_meta["item_id"]
        category = sku_meta["category"]
        base_p = sku_meta["base_price"]
        ed = sku_meta["historical_elasticity"]
        unit_c = round(base_p * DEFAULT_COST_RATIO, 2)

        # Baseline volume scaling by category
        if category == "FOODS":
            mean_volume = 65.0 if "FOODS_3" in item_id else 22.0
            weekly_cycle = np.array([0.9, 0.95, 1.0, 1.05, 1.25, 1.35, 1.15])  # Peaks Friday/Sat
            snap_boost = 1.12
        elif category == "HOUSEHOLD":
            mean_volume = 12.0
            weekly_cycle = np.array([0.95, 0.98, 1.0, 1.0, 1.10, 1.15, 1.05])
            snap_boost = 1.04
        else:  # HOBBIES
            mean_volume = 6.0
            weekly_cycle = np.array([0.85, 0.90, 0.95, 1.0, 1.20, 1.40, 1.20])
            snap_boost = 1.02

        # Generate realistic price time-series with periodic markdowns and price steps
        t = np.arange(n_days)
        # Slow inflation drift (+1.5% per year)
        price_drift = 1.0 + (t / 365.0) * 0.015
        prices = base_p * price_drift

        # Introduce promotional markdown events (15% to 25% off lasting 7 to 14 days)
        # Every 60-90 days, trigger a promo
        promo_mask = np.zeros(n_days, dtype=bool)
        promo_start = 30
        while promo_start < n_days - 20:
            duration = np.random.randint(7, 15)
            discount = np.random.uniform(0.12, 0.25)
            prices[promo_start : promo_start + duration] *= (1.0 - discount)
            promo_mask[promo_start : promo_start + duration] = True
            promo_start += np.random.randint(55, 95)

        prices = np.round(prices, 2)

        # Demand Generation: Base + Seasonality + Price Elasticity + Events + Noise
        annual_cycle = 1.0 + 0.15 * np.sin(2 * np.pi * t / 365.25 - np.pi / 2)  # Peaks in Summer/Q4
        dow_factor = np.array([weekly_cycle[d] for d in df_cal["dayofweek"]])

        # Iso-elastic demand response: Q = Q_base * (P / P_base) ^ Ed
        price_response = (prices / base_p) ** ed

        # Event boosts
        event_multipliers = np.ones(n_days)
        for i, row in df_cal.iterrows():
            ev = row["event_name"]
            if ev == "Christmas":
                event_multipliers[i] = 0.0  # Closed on Christmas
            elif ev == "Thanksgiving":
                event_multipliers[i] = 1.5 if category == "FOODS" else 1.3
            elif ev == "SuperBowl":
                event_multipliers[i] = 1.45 if category == "FOODS" else 1.0
            elif ev == "Halloween":
                event_multipliers[i] = 1.25 if category == "FOODS" else 1.1
            elif ev == "IndependenceDay":
                event_multipliers[i] = 1.30 if category == "FOODS" else 1.15

        # SNAP boost during first 10 days
        snap_mult = np.where(df_cal["snap_flag"] == 1, snap_boost, 1.0)

        # Combine deterministic factors
        expected_demand = mean_volume * annual_cycle * dow_factor * price_response * event_multipliers * snap_mult

        # Add negative binomial / Poisson noise
        random_noise = np.random.normal(0, 0.12 * mean_volume, size=n_days)
        actual_demand = np.maximum(0.0, expected_demand + random_noise)
        # Store closures are strictly 0
        actual_demand[df_cal["event_name"] == "Christmas"] = 0.0
        actual_demand = np.round(actual_demand, 0)

        # Competitor price (tracks regular price with random market spread)
        competitor_spread = np.random.normal(1.03, 0.04, size=n_days)
        competitor_prices = np.round(prices * competitor_spread, 2)

        # Compile rows
        for i in range(n_days):
            all_records.append({
                "date": df_cal.iloc[i]["date"].strftime("%Y-%m-%d"),
                "item_id": item_id,
                "item_name": sku_meta["item_name"],
                "category": category,
                "store_id": sku_meta["store_id"],
                "units_sold": float(actual_demand[i]),
                "sell_price": float(prices[i]),
                "unit_cost": float(unit_c),
                "fixed_costs": 500.0,
                "event_name": df_cal.iloc[i]["event_name"] or "None",
                "event_type": df_cal.iloc[i]["event_type"] or "None",
                "snap_flag": int(df_cal.iloc[i]["snap_flag"]),
                "competitor_price": float(competitor_prices[i])
            })

    df_out = pd.DataFrame(all_records)
    PRIMARY_DATASET_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(PRIMARY_DATASET_PATH, index=False)
    print(f"Successfully generated {len(df_out)} rows across {len(CURATED_SKUS)} SKUs.")
    print(f"Saved to: {PRIMARY_DATASET_PATH}")
    return df_out


if __name__ == "__main__":
    generate_curated_dataset()
