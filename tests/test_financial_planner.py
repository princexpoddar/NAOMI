
from src.core.financial import compute_financial_kpis


def test_revenue_calculation():
    kpi = compute_financial_kpis(
        price=5,
        demand=100,
        unit_cost=3,
        fixed_costs=15,
    )

    assert kpi["Revenue"] == 500.0


def test_cogs_calculation():
    kpi = compute_financial_kpis(
        price=5,
        demand=100,
        unit_cost=3,
        fixed_costs=15,
    )

    assert kpi["COGS"] == 300.0


def test_gross_profit_calculation():
    kpi = compute_financial_kpis(
        price=5,
        demand=100,
        unit_cost=3,
        fixed_costs=15,
    )

    assert kpi["Gross Profit"] == 200.0


def test_operating_profit_calculation():
    kpi = compute_financial_kpis(
        price=5,
        demand=100,
        unit_cost=3,
        fixed_costs=15,
    )

    assert kpi["Operating Profit"] == 185.0


def test_gross_margin_percentage():
    kpi = compute_financial_kpis(
        price=5,
        demand=100,
        unit_cost=3,
        fixed_costs=15,
    )

    expected = 40.0

    assert abs(kpi["Gross Margin %"] - expected) < 1e-6


def test_breakeven_volume():
    kpi = compute_financial_kpis(
        price=5,
        demand=100,
        unit_cost=3,
        fixed_costs=20,
    )

    expected = 10.0

    assert abs(kpi["Breakeven Volume"] - expected) < 1e-6


def test_zero_revenue_case():
    kpi = compute_financial_kpis(
        price=0,
        demand=0,
        unit_cost=3,
        fixed_costs=20,
    )

    assert kpi["Revenue"] == 0.0
    assert kpi["Gross Margin %"] == 0.0