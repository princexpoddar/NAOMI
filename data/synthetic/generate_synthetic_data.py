"""Secondary Validation Harness: Controlled Synthetic Data Generator.

This script produces controlled synthetic sales time-series with mathematically
known ground-truth parameters (elasticity Ed = -1.20, true base demand = 1,000).
It is used in automated test suites (tests/test_elasticity_and_pricing.py) to
mathematically verify that our estimation and optimization algorithms recover
exact theoretical optima.
"""

from pathlib import Path
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SYNTHETIC_CSV_PATH = PROJECT_ROOT / "data" / "synthetic" / "synthetic_sales.csv"


def generate_synthetic_benchmark(
    n_days: int = 1095,  # 3 years
    base_price: float = 50.0,
    unit_cost: float = 25.0,
    true_elasticity: float = -1.20,
    base_volume: float = 500.0,
    random_seed: int = 42
) -> pd.DataFrame:
    """Generate synthetic sales data with exact ground truth for unit test validation."""
    np.random.seed(random_seed)
    dates = pd.date_range(start="2023-01-01", periods=n_days, freq="D")
    t = np.arange(n_days)

    # Seasonal variation (annual + weekly sine waves)
    annual_seasonality = 1.0 + 0.20 * np.sin(2 * np.pi * t / 365.25)
    weekly_seasonality = 1.0 + 0.10 * np.sin(2 * np.pi * t / 7.0)

    # Controlled price fluctuations around base price (+/- 15%)
    price_noise = np.random.uniform(-0.15, 0.15, size=n_days)
    prices = np.round(base_price * (1.0 + price_noise), 2)

    # Ground-truth iso-elastic demand response: Q = Q_base * (P / P_base) ^ Ed
    price_effect = (prices / base_price) ** true_elasticity

    # Promotions (+25% volume on random promotional days)
    promo_flags = (np.random.rand(n_days) < 0.08).astype(int)
    promo_multiplier = np.where(promo_flags == 1, 1.25, 1.0)

    # Baseline demand with controlled Gaussian noise
    expected_q = base_volume * annual_seasonality * weekly_seasonality * price_effect * promo_multiplier
    demand_noise = np.random.normal(0, 15.0, size=n_days)
    actual_q = np.maximum(0.0, expected_q + demand_noise)
    actual_q = np.round(actual_q, 0)

    competitor_prices = np.round(prices * np.random.normal(1.02, 0.03, size=n_days), 2)

    df = pd.DataFrame({
        "date": dates.strftime("%Y-%m-%d"),
        "item_id": "SYNTH_BENCHMARK_01",
        "item_name": "Synthetic Controlled SKU",
        "category": "TESTING",
        "store_id": "BENCH_1",
        "units_sold": actual_q,
        "sell_price": prices,
        "unit_cost": unit_cost,
        "fixed_costs": 500.0,
        "event_name": "None",
        "event_type": "None",
        "snap_flag": 0,
        "competitor_price": competitor_prices,
        "promotion_active": promo_flags,
        "true_elasticity": true_elasticity
    })

    SYNTHETIC_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(SYNTHETIC_CSV_PATH, index=False)
    print(f"Synthetic benchmark generated: {len(df)} rows saved to {SYNTHETIC_CSV_PATH}")
    return df


if __name__ == "__main__":
    generate_synthetic_benchmark()
