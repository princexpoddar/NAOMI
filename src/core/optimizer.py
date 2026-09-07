
import numpy as np
from scipy.optimize import minimize_scalar

from src.core.elasticity import iso_elastic_demand


def profit(
    price,
    base_price,
    base_demand,
    elasticity,
    unit_cost,
    fixed_cost,
):
    demand = iso_elastic_demand(
        price,
        base_price,
        base_demand,
        elasticity,
    )

    return (price - unit_cost) * demand - fixed_cost


def optimize_price(
    base_price,
    base_demand,
    elasticity,
    unit_cost,
    fixed_cost=0,
):
    lower = max(unit_cost * 1.05, 0.70 * base_price)
    upper = 1.40 * base_price

    prices = np.linspace(lower, upper, 100)

    profits = [
        profit(
            p,
            base_price,
            base_demand,
            elasticity,
            unit_cost,
            fixed_cost,
        )
        for p in prices
    ]

    best_grid_price = prices[np.argmax(profits)]

    result = minimize_scalar(
        lambda p: -profit(
            p,
            base_price,
            base_demand,
            elasticity,
            unit_cost,
            fixed_cost,
        ),
        bounds=(lower, upper),
        method="bounded",
    )

    optimal_price = result.x

    optimal_profit = profit(
        optimal_price,
        base_price,
        base_demand,
        elasticity,
        unit_cost,
        fixed_cost,
    )

    optimal_demand = iso_elastic_demand(
        optimal_price,
        base_price,
        base_demand,
        elasticity,
    )

    return {
        "optimal_price": float(optimal_price),
        "optimal_profit": float(optimal_profit),
        "forecasted_demand": float(optimal_demand),
        "grid_price": float(best_grid_price),
    }