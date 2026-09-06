"""
Counterfactual Scenario Simulator for NAOMI.

Implements 5 business scenarios that compute shocked KPIs relative to a baseline,
using price elasticity and cross-price elasticity to model demand response.
"""

from typing import Any
from src.data.schemas import FinancialKPIs, ScenarioResult

# Cross-elasticity constant: a 10% competitor price drop drives ~20% own demand loss
CROSS_ELASTICITY_DEMAND_LOSS_PCT = 20.0


def _compute_financial_kpis(
    price: float,
    demand: float,
    unit_cost: float,
    fixed_costs: float,
) -> FinancialKPIs:
    """Derive a full FinancialKPIs record from primitive operating values."""
    revenue = price * demand
    cogs = unit_cost * demand
    gross_profit = revenue - cogs - fixed_costs
    gross_margin_pct = (gross_profit / revenue * 100.0) if revenue > 0 else 0.0
    contribution_margin = price - unit_cost
    breakeven_units = (fixed_costs / contribution_margin) if contribution_margin > 0 else float("inf")
    breakeven_revenue = breakeven_units * price

    return FinancialKPIs(
        price=round(price, 4),
        demand=round(demand, 4),
        revenue=round(revenue, 4),
        cogs=round(cogs, 4),
        gross_profit=round(gross_profit, 4),
        gross_margin_pct=round(gross_margin_pct, 4),
        breakeven_units=round(breakeven_units, 4),
        breakeven_revenue=round(breakeven_revenue, 4),
    )


def _risk_label(profit_delta_pct: float) -> str:
    """Classify profit impact into a human-readable risk tier."""
    if profit_delta_pct >= 5.0:
        return "Positive — profit improves under this scenario."
    elif profit_delta_pct >= -5.0:
        return "Neutral — marginal profit impact; monitor closely."
    elif profit_delta_pct >= -15.0:
        return "Moderate Risk — meaningful profit erosion; review pricing and costs."
    elif profit_delta_pct >= -30.0:
        return "High Risk — significant profit erosion; corrective action needed."
    else:
        return "Critical Risk — severe profit loss; immediate intervention required."


def _pct_change(new_val: float, old_val: float) -> float:
    """Safe percentage change calculation."""
    if old_val == 0:
        return 0.0
    return round((new_val - old_val) / abs(old_val) * 100.0, 4)


def simulate_scenario(
    scenario_type: str,
    base_kpis: dict,
    params: dict,
) -> dict:
    """
    Simulate a counterfactual business scenario and return a serialised ScenarioResult.

    Parameters
    ----------
    scenario_type : str
        One of: "price_policy", "macro_demand_shock", "supply_chain_inflation",
                "competitor_price_war", "stagflation"
    base_kpis : dict
        Baseline operating state with keys:
            price (float), demand (float), unit_cost (float), fixed_costs (float),
            elasticity (float, negative)
    params : dict
        Scenario-specific parameters (see each scenario for keys).

    Returns
    -------
    dict
        Serialised ScenarioResult (all dataclass fields as a dict).
    """
    # ------------------------------------------------------------------ #
    # Extract baseline values
    # ------------------------------------------------------------------ #
    price = float(base_kpis["price"])
    demand = float(base_kpis["demand"])
    unit_cost = float(base_kpis["unit_cost"])
    fixed_costs = float(base_kpis.get("fixed_costs", 500.0))
    elasticity = float(base_kpis.get("elasticity", -1.0))  # must be negative

    baseline_kpis = _compute_financial_kpis(price, demand, unit_cost, fixed_costs)

    # ------------------------------------------------------------------ #
    # Branch per scenario
    # ------------------------------------------------------------------ #
    scenario_type = scenario_type.strip().lower()

    # ── Scenario 1: Price Policy ────────────────────────────────────────
    if scenario_type == "price_policy":
        """
        User supplies a price change (delta_price_pct, e.g. +10 or -5).
        New demand is derived via own-price elasticity:
            Q_new = Q * (1 + elasticity * delta_price_pct/100)
        """
        delta_price_pct = float(params.get("delta_price_pct", 0.0))
        new_price = price * (1 + delta_price_pct / 100.0)
        new_demand = demand * (1 + elasticity * (delta_price_pct / 100.0))
        new_demand = max(0.0, new_demand)

        shocked_kpis = _compute_financial_kpis(new_price, new_demand, unit_cost, fixed_costs)
        scenario_id = "S1"
        scenario_name = "Price Policy"
        scenario_params: dict[str, Any] = {
            "delta_price_pct": delta_price_pct,
            "new_price": round(new_price, 4),
        }

    # ── Scenario 2: Macro Demand Shock ──────────────────────────────────
    elif scenario_type == "macro_demand_shock":
        """
        Exogenous contraction in demand, e.g. recession.
            Q_shock = Q * (1 - shock_pct / 100)
        Price and costs are unchanged.
        """
        shock_pct = float(params.get("shock_pct", 15.0))  # default −15%
        new_demand = demand * (1.0 - shock_pct / 100.0)
        new_demand = max(0.0, new_demand)

        shocked_kpis = _compute_financial_kpis(price, new_demand, unit_cost, fixed_costs)
        scenario_id = "S2"
        scenario_name = "Macro Demand Shock"
        scenario_params = {
            "shock_pct": shock_pct,
            "description": f"Demand contracted by {shock_pct}% due to macroeconomic headwinds.",
        }

    # ── Scenario 3: Supply Chain Cost Inflation ─────────────────────────
    elif scenario_type == "supply_chain_inflation":
        """
        Unit cost surge.
            c_new = c * (1 + cost_pct / 100)
        Demand and price are unchanged (cost is absorbed internally).
        """
        cost_pct = float(params.get("cost_pct", 10.0))  # default +10%
        new_unit_cost = unit_cost * (1.0 + cost_pct / 100.0)

        shocked_kpis = _compute_financial_kpis(price, demand, new_unit_cost, fixed_costs)
        scenario_id = "S3"
        scenario_name = "Supply Chain Cost Inflation"
        scenario_params = {
            "cost_pct": cost_pct,
            "new_unit_cost": round(new_unit_cost, 4),
            "description": f"Unit cost increased by {cost_pct}% due to supply chain disruption.",
        }

    # ── Scenario 4: Competitor Price War ────────────────────────────────
    elif scenario_type == "competitor_price_war":
        """
        Competitor drops price ⟹ own-brand demand loss via cross-price elasticity.
        Baseline: 10% competitor price drop yields 20% own demand loss (cross-elasticity = 2.0).
        """
        competitor_price_drop_pct = float(params.get("competitor_price_drop_pct", 10.0))
        cross_elasticity = float(params.get("cross_elasticity", 2.0))
        demand_loss_pct = float(params.get("demand_loss_pct", competitor_price_drop_pct * cross_elasticity))
        demand_loss_pct = min(100.0, max(0.0, demand_loss_pct))

        new_demand = demand * (1.0 - demand_loss_pct / 100.0)
        new_demand = max(0.0, new_demand)

        shocked_kpis = _compute_financial_kpis(price, new_demand, unit_cost, fixed_costs)
        scenario_id = "S4"
        scenario_name = "Competitor Price War"
        scenario_params = {
            "competitor_price_drop_pct": competitor_price_drop_pct,
            "implied_demand_loss_pct": round(demand_loss_pct, 4),
            "description": (
                f"Competitor reduced price by {competitor_price_drop_pct}%, "
                f"triggering a {round(demand_loss_pct, 2)}% cross-elasticity demand loss."
            ),
        }

    # ── Scenario 5: Leeroy & Leeroy Stagflation ─────────────────────────
    elif scenario_type == "stagflation":
        """
        Compound shock: +10% unit cost surge AND −8% demand contraction.
        Both hit simultaneously (stagflation profile).
        """
        cost_surge_pct = float(params.get("cost_surge_pct", 10.0))
        demand_contraction_pct = float(params.get("demand_contraction_pct", 8.0))

        new_unit_cost = unit_cost * (1.0 + cost_surge_pct / 100.0)
        new_demand = demand * (1.0 - demand_contraction_pct / 100.0)
        new_demand = max(0.0, new_demand)

        shocked_kpis = _compute_financial_kpis(price, new_demand, new_unit_cost, fixed_costs)
        scenario_id = "S5"
        scenario_name = "Leeroy & Leeroy Stagflation"
        scenario_params = {
            "cost_surge_pct": cost_surge_pct,
            "demand_contraction_pct": demand_contraction_pct,
            "new_unit_cost": round(new_unit_cost, 4),
            "description": (
                f"Stagflation: +{cost_surge_pct}% unit cost surge "
                f"and -{demand_contraction_pct}% demand contraction."
            ),
        }

    else:
        raise ValueError(
            f"Unknown scenario_type '{scenario_type}'. "
            "Valid options: price_policy, macro_demand_shock, supply_chain_inflation, "
            "competitor_price_war, stagflation"
        )

    # ------------------------------------------------------------------ #
    # Compute delta KPIs and risk label
    # ------------------------------------------------------------------ #
    demand_delta_pct = _pct_change(shocked_kpis.demand, baseline_kpis.demand)
    revenue_delta_pct = _pct_change(shocked_kpis.revenue, baseline_kpis.revenue)
    profit_delta_pct = _pct_change(shocked_kpis.gross_profit, baseline_kpis.gross_profit)
    risk = _risk_label(profit_delta_pct)

    result = ScenarioResult(
        scenario_id=scenario_id,
        scenario_name=scenario_name,
        parameters=scenario_params,
        baseline_kpis=baseline_kpis,
        shocked_kpis=shocked_kpis,
        demand_delta_pct=demand_delta_pct,
        revenue_delta_pct=revenue_delta_pct,
        profit_delta_pct=profit_delta_pct,
        risk_assessment=risk,
    )

    # Serialise dataclasses to plain dict for JSON transport
    return _scenario_result_to_dict(result)


def _financial_kpis_to_dict(kpis: FinancialKPIs) -> dict:
    return {
        "price": kpis.price,
        "demand": kpis.demand,
        "revenue": kpis.revenue,
        "cogs": kpis.cogs,
        "gross_profit": kpis.gross_profit,
        "gross_margin_pct": kpis.gross_margin_pct,
        "breakeven_units": kpis.breakeven_units,
        "breakeven_revenue": kpis.breakeven_revenue,
    }


def _scenario_result_to_dict(result: ScenarioResult) -> dict:
    return {
        "scenario_id": result.scenario_id,
        "scenario_name": result.scenario_name,
        "parameters": result.parameters,
        "baseline_kpis": _financial_kpis_to_dict(result.baseline_kpis),
        "shocked_kpis": _financial_kpis_to_dict(result.shocked_kpis),
        "demand_delta_pct": result.demand_delta_pct,
        "revenue_delta_pct": result.revenue_delta_pct,
        "profit_delta_pct": result.profit_delta_pct,
        "risk_assessment": result.risk_assessment,
    }
