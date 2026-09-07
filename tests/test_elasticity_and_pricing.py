
import pandas as pd

from src.core.elasticity import estimate_elasticity, iso_elastic_demand
from src.core.optimizer import optimize_price


def test_estimate_elasticity_returns_negative():
    """
    If price increases while demand decreases,
    elasticity should be negative.
    """

    df = pd.DataFrame({
        "sell_price": [1, 2, 3, 4, 5],
        "units_sold": [100, 70, 50, 40, 30]
    })

    elasticity = estimate_elasticity(df)

    assert elasticity < 0


def test_iso_elastic_demand_decreases_when_price_increases():
    """
    Higher price should reduce demand
    when elasticity is negative.
    """

    demand = iso_elastic_demand(
        p_candidate=6,
        p_base=5,
        q_base=100,
        elasticity=-1.2,
    )

    assert demand < 100


def test_iso_elastic_demand_increases_when_price_drops():
    """
    Lower price should increase demand.
    """

    demand = iso_elastic_demand(
        p_candidate=4,
        p_base=5,
        q_base=100,
        elasticity=-1.2,
    )

    assert demand > 100


def test_optimize_price_returns_valid_result():
    """
    Optimizer should return a valid dictionary
    with positive values.
    """

    result = optimize_price(
        base_price=5,
        base_demand=100,
        elasticity=-1.2,
        unit_cost=3,
        fixed_cost=15,
    )

    assert isinstance(result, dict)

    assert "optimal_price" in result
    assert "optimal_profit" in result
    assert "forecasted_demand" in result

    assert result["optimal_price"] > 0
    assert result["forecasted_demand"] > 0


def test_optimizer_respects_price_bounds():
    """
    README requires search between
    70% and 140% of base price.
    """

    base_price = 5

    result = optimize_price(
        base_price=base_price,
        base_demand=100,
        elasticity=-1.2,
        unit_cost=3,
        fixed_cost=15,
    )

    assert 0.70 * base_price <= result["optimal_price"] <= 1.40 * base_price