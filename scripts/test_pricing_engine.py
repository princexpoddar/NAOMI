
"""
Member 2 Integration Script
---------------------------
Tests the complete pricing engine by connecting:
1. DataPipeline
2. Elasticity estimation
3. Price optimization
4. Financial KPI generation
"""

from src.data.pipeline import DataPipeline
from src.core.elasticity import estimate_elasticity
from src.core.optimizer import optimize_price
from src.core.financial import compute_financial_kpis

# Use the same fixed cost everywhere
FIXED_COST = 15


def main():
    print("=" * 60)
    print("NAOMI - MEMBER 2 PRICING ENGINE")
    print("=" * 60)

    # Load Walmart M5 data
    pipeline = DataPipeline()
    df = pipeline.load_data()

    sku_id = "FOODS_3_090_CA_1"
    sku = pipeline.get_sku_dataframe(df, sku_id)

    # Estimate elasticity
    elasticity = estimate_elasticity(sku)

    # Baseline values
    base_price = float(sku["sell_price"].iloc[-1])
    base_demand = float(sku["units_sold"].mean())
    unit_cost = float(sku["unit_cost"].iloc[-1])

    print("\nINPUT VALUES")
    print("-" * 40)
    print(f"SKU                : {sku_id}")
    print(f"Estimated Elasticity : {elasticity:.3f}")
    print(f"Base Price           : {base_price:.2f}")
    print(f"Average Demand       : {base_demand:.2f}")
    print(f"Unit Cost            : {unit_cost:.2f}")
    print(f"Fixed Cost           : {FIXED_COST:.2f}")

    # Optimize price
    result = optimize_price(
        base_price=base_price,
        base_demand=base_demand,
        elasticity=elasticity,
        unit_cost=unit_cost,
        fixed_cost=FIXED_COST,
    )

    # Financial KPIs
    kpis = compute_financial_kpis(
        price=result["optimal_price"],
        demand=result["forecasted_demand"],
        unit_cost=unit_cost,
        fixed_costs=FIXED_COST,
    )

    print("\nRECOMMENDED PRICE")
    print("-" * 40)
    print(f"Optimal Price      : {result['optimal_price']:.2f}")
    print(f"Forecast Demand    : {result['forecasted_demand']:.2f} units")
    print(f"Projected Profit   : {result['optimal_profit']:.2f}")

    print("\nFINANCIAL KPIs")
    print("-" * 40)
    for key, value in kpis.items():
        print(f"{key:<20}: {value:.2f}")

    print("\n" + "=" * 60)
    print("Pricing Engine executed successfully.")
    print("=" * 60)


if __name__ == "__main__":
    main()