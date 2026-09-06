"""
Reactive Callbacks for NAOMI Executive Dashboard.

Coordinates real-time analytical calculations, Plotly figure updates,
and C-suite narrative generation upon user interaction.
"""

from datetime import datetime, timedelta
import math
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from dash import Dash, Input, Output, State, no_update
import dash_bootstrap_components as dbc

from src.config import CURATED_SKUS, DEFAULT_COST_RATIO, DEFAULT_FIXED_COST, PROJECT_ROOT
from src.dashboard.components.charts import (
    render_forecast_chart,
    render_profit_curve,
    render_scenario_bars,
)

# ------------------------------------------------------------------ #
# Data Caches & SKU Metadata
# ------------------------------------------------------------------ #
_SKU_DICT: Dict[str, dict] = {sku["item_id"]: sku for sku in CURATED_SKUS}
_RAW_DATA_CACHE: Dict[str, pd.DataFrame] = {}


def _get_historical_series(sku_id: str) -> Tuple[List[str], List[float], float]:
    """Retrieve historical daily dates, units sold, and baseline demand for a SKU."""
    global _RAW_DATA_CACHE
    if not _RAW_DATA_CACHE:
        csv_path = PROJECT_ROOT / "data" / "raw" / "walmart_m5_curated.csv"
        if csv_path.exists():
            try:
                df = pd.read_csv(csv_path)
                for item_id, group in df.groupby("item_id"):
                    _RAW_DATA_CACHE[str(item_id)] = group.sort_values("date")
            except Exception:
                pass

    if sku_id in _RAW_DATA_CACHE:
        df_sku = _RAW_DATA_CACHE[sku_id]
        recent = df_sku.tail(45)
        hist_dates = [str(d) for d in recent["date"].tolist()]
        hist_y = [float(y) for y in recent["units_sold"].tolist()]
        base_demand = float(recent["units_sold"].tail(30).mean())
        return hist_dates, hist_y, round(base_demand, 2)

    # Fallback synthetics if CSV not found
    today = datetime.now().date()
    hist_dates = [(today - timedelta(days=45 - i)).isoformat() for i in range(45)]
    base_demand = 50.0
    hist_y = [round(base_demand + 5.0 * math.sin(i / 3.0), 1) for i in range(45)]
    return hist_dates, hist_y, base_demand


def compute_dashboard_metrics(
    sku_id: str,
    horizon: int,
    delta_price_pct: float,
    demand_shock_pct: float,
    cost_surge_pct: float,
    competitor_drop_pct: float,
) -> tuple:
    """Core analytical pricing and forecasting calculation engine."""
    sku = _SKU_DICT.get(sku_id, CURATED_SKUS[0])
    base_price = float(sku["base_price"])
    elasticity = float(sku["historical_elasticity"])
    fixed_costs = float(DEFAULT_FIXED_COST)
    unit_cost = base_price * DEFAULT_COST_RATIO

    # 1. Historical Actuals & Base Demand
    hist_dates, hist_y, base_demand = _get_historical_series(sku_id)

    # 2. Demand Forecast & CI envelope
    today = datetime.now().date()
    pred_dates = [(today + timedelta(days=i + 1)).isoformat() for i in range(horizon)]

    # Base daily forecast with weekly cycle
    pred_y = [
        round(max(0.1, base_demand * (1.0 + 0.08 * math.sin((i + 1) * 2 * math.pi / 7))), 2)
        for i in range(horizon)
    ]
    lower_ci = [round(max(0.0, y * 0.85), 2) for y in pred_y]
    upper_ci = [round(y * 1.15, 2) for y in pred_y]
    baseline_y = [round(base_demand, 2)] * horizon

    # 3. 100-Point Profit & Revenue Landscape Grid Sweep
    p_min = base_price * 0.70
    p_max = base_price * 1.40
    n_points = 100
    step = (p_max - p_min) / (n_points - 1)
    grid_prices = [p_min + step * i for i in range(n_points)]

    grid_demands = [
        base_demand * math.pow(p / base_price, elasticity)
        for p in grid_prices
    ]
    grid_revenues = [p * d for p, d in zip(grid_prices, grid_demands)]
    grid_profits = [(p - unit_cost) * d - fixed_costs for p, d in zip(grid_prices, grid_demands)]

    best_idx = int(np.argmax(grid_profits)) if len(grid_profits) > 0 else 0
    optimal_price = grid_prices[best_idx]
    optimal_demand = grid_demands[best_idx]
    optimal_profit = grid_profits[best_idx]
    optimal_revenue = grid_revenues[best_idx]

    # Baseline Operating Metrics
    base_profit = (base_price - unit_cost) * base_demand - fixed_costs
    base_revenue = base_price * base_demand
    profit_uplift_pct = (
        ((optimal_profit - base_profit) / abs(base_profit) * 100.0)
        if base_profit != 0 else 0.0
    )
    price_change_pct = (optimal_price - base_price) / base_price * 100.0

    # Breakeven volume
    contrib_margin = optimal_price - unit_cost
    breakeven_units = (fixed_costs / contrib_margin) if contrib_margin > 0 else 0.0
    gross_margin_pct = (optimal_profit / optimal_revenue * 100.0) if optimal_revenue > 0 else 0.0

    # 4. Counterfactual Simulation based on active sliders
    active_candidate_price = base_price * (1.0 + delta_price_pct / 100.0)

    # Price elasticity effect: Q_price = Q0 * (P / P0)^Ed
    sim_price_factor = math.pow(active_candidate_price / base_price, elasticity)
    # Exogenous shocks:
    # Macro demand shock: (1 + demand_shock_pct/100) (demand_shock_pct is negative e.g. -15%)
    sim_macro_factor = max(0.0, 1.0 + demand_shock_pct / 100.0)
    # Competitor drop cross-elasticity (e.g. 10% drop -> 20% loss)
    sim_competitor_loss = max(0.0, competitor_drop_pct * 2.0 / 100.0)
    sim_competitor_factor = max(0.0, 1.0 - sim_competitor_loss)

    shocked_demand = max(0.0, base_demand * sim_price_factor * sim_macro_factor * sim_competitor_factor)
    shocked_unit_cost = unit_cost * (1.0 + cost_surge_pct / 100.0)
    shocked_revenue = active_candidate_price * shocked_demand
    shocked_cogs = shocked_unit_cost * shocked_demand
    shocked_profit = shocked_revenue - shocked_cogs - fixed_costs

    baseline_kpis_dict = {
        "demand": round(base_demand, 1),
        "revenue": round(base_revenue, 2),
        "gross_profit": round(base_profit, 2),
    }
    shocked_kpis_dict = {
        "demand": round(shocked_demand, 1),
        "revenue": round(shocked_revenue, 2),
        "gross_profit": round(shocked_profit, 2),
    }

    # 5. Figures
    fig_forecast = render_forecast_chart(
        hist_dates=hist_dates,
        hist_y=hist_y,
        pred_dates=pred_dates,
        pred_y=pred_y,
        lower_ci=lower_ci,
        upper_ci=upper_ci,
        baseline_y=baseline_y,
        sku_name=sku["item_name"],
    )

    fig_profit = render_profit_curve(
        prices=grid_prices,
        profits=grid_profits,
        revenues=grid_revenues,
        opt_price=optimal_price,
        opt_profit=optimal_profit,
        base_price=base_price,
        base_profit=base_profit,
    )

    scenario_label = "Custom Simulation"
    if delta_price_pct != 0:
        scenario_label = f"Price {delta_price_pct:+.1f}%"
    elif demand_shock_pct != 0 and cost_surge_pct != 0:
        scenario_label = "Stagflation"
    elif demand_shock_pct != 0:
        scenario_label = f"Macro {demand_shock_pct:+.1f}%"
    elif cost_surge_pct != 0:
        scenario_label = f"Cost +{cost_surge_pct:.1f}%"
    elif competitor_drop_pct != 0:
        scenario_label = f"Price War -{competitor_drop_pct:.1f}%"

    fig_scenario = render_scenario_bars(
        baseline_kpis=baseline_kpis_dict,
        shocked_kpis=shocked_kpis_dict,
        scenario_name=scenario_label,
    )

    # 6. Executive Narrative Generation
    profit_delta_pct = (
        ((shocked_profit - base_profit) / abs(base_profit) * 100.0)
        if base_profit != 0 else 0.0
    )

    if profit_delta_pct >= 5.0:
        risk_text = "Positive"
        risk_class = "badge bg-success-subtle text-success px-2 py-1"
    elif profit_delta_pct >= -5.0:
        risk_text = "Stable"
        risk_class = "badge bg-info-subtle text-info px-2 py-1"
    elif profit_delta_pct >= -15.0:
        risk_text = "Moderate Risk"
        risk_class = "badge bg-warning-subtle text-warning px-2 py-1"
    elif profit_delta_pct >= -30.0:
        risk_text = "High Risk"
        risk_class = "badge bg-danger-subtle text-danger px-2 py-1"
    else:
        risk_text = "Critical Risk"
        risk_class = "badge bg-danger text-white px-2 py-1"

    elasticity_desc = "elastic" if elasticity < -1.0 else "inelastic"
    p1 = (
        f"For {sku['item_name']} ({sku['category']}), the estimated price elasticity of demand "
        f"is Ed = {elasticity:.2f} ({elasticity_desc}). The mathematical profit-maximizing price is "
        f"${optimal_price:.2f} ({price_change_pct:+.1f}% vs baseline ${base_price:.2f}), "
        f"yielding an expected profit uplift of {profit_uplift_pct:+.1f}% to ${optimal_profit:,.2f}."
    )
    p2 = (
        f"Under the active scenario ({scenario_label}), demand adjusts to {shocked_demand:.1f} units "
        f"({(shocked_demand - base_demand)/base_demand*100:+.1f}%), generating ${shocked_revenue:,.2f} in revenue "
        f"and ${shocked_profit:,.2f} in operating profit ({profit_delta_pct:+.1f}% net change). "
        f"Breakeven threshold stands at {breakeven_units:.0f} units. Risk status: {risk_text}."
    )

    # 7. Formatted Card Badges
    price_badge_text = f"{price_change_pct:+.1f}% vs Base"
    price_badge_class = "badge-positive" if price_change_pct >= 0 else "badge-neutral"

    demand_delta_pct = (optimal_demand - base_demand) / base_demand * 100.0
    demand_badge_text = f"{demand_delta_pct:+.1f}% vol"
    demand_badge_class = "badge-positive" if demand_delta_pct >= 0 else "badge-neutral"

    profit_badge_text = f"{profit_uplift_pct:+.1f}% Uplift"
    profit_badge_class = "badge-positive" if profit_uplift_pct >= 0 else "badge-negative"

    return (
        f"${optimal_price:.2f}",
        price_badge_text,
        f"kpi-badge {price_badge_class}",
        f"Baseline: ${base_price:.2f}",

        f"{optimal_demand:.1f} units",
        demand_badge_text,
        f"kpi-badge {demand_badge_class}",
        f"{horizon}-Day Horizon Mean",

        f"${optimal_revenue:,.2f}",
        f"{((optimal_revenue-base_revenue)/base_revenue*100):+.1f}%",
        f"Baseline: ${base_revenue:,.2f}",

        f"${optimal_profit:,.2f}",
        profit_badge_text,
        f"kpi-badge {profit_badge_class}",
        f"Baseline: ${base_profit:,.2f}",

        f"{gross_margin_pct:.1f}%",
        f"BE: {breakeven_units:.0f} units",
        f"Fixed Overhead: ${fixed_costs:,.0f}",

        fig_forecast,
        fig_profit,
        fig_scenario,

        risk_text,
        risk_class,
        p1,
        p2,
    )


def register_callbacks(app: Dash) -> None:
    """Register all reactive Dash callbacks with the application."""

    # -------------------------------------------------------------- #
    # 1. Scenario Presets Sync -> Updates Sliders
    # -------------------------------------------------------------- #
    @app.callback(
        [
            Output("price-slider", "value"),
            Output("demand-shock-slider", "value"),
            Output("cost-shock-slider", "value"),
            Output("competitor-slider", "value"),
        ],
        Input("scenario-preset-radio", "value"),
        prevent_initial_call=True,
    )
    def apply_scenario_preset(preset: str):
        if preset == "s1_price_up":
            return 5, 0, 0, 0
        elif preset == "s2_macro":
            return 0, -15, 0, 0
        elif preset == "s3_cost":
            return 0, 0, 10, 0
        elif preset == "s4_war":
            return 0, 0, 0, 10
        elif preset == "s5_stagflation":
            return 0, -8, 10, 0
        elif preset == "custom":
            return no_update, no_update, no_update, no_update
        return 0, 0, 0, 0

    # -------------------------------------------------------------- #
    # 2. Slider Value Pills Display
    # -------------------------------------------------------------- #
    @app.callback(
        [
            Output("label-price-slider", "children"),
            Output("label-demand-shock-slider", "children"),
            Output("label-cost-shock-slider", "children"),
            Output("label-competitor-slider", "children"),
        ],
        [
            Input("price-slider", "value"),
            Input("demand-shock-slider", "value"),
            Input("cost-shock-slider", "value"),
            Input("competitor-slider", "value"),
        ],
    )
    def update_slider_labels(price_val, demand_val, cost_val, comp_val):
        price_str = f"{price_val:+.1f}%"
        demand_str = f"{demand_val:+.1f}%"
        cost_str = f"+{cost_val:.1f}%"
        comp_str = f"{comp_val:.1f}%"
        return price_str, demand_str, cost_str, comp_str

    # -------------------------------------------------------------- #
    # 3. Main Analytical Reactive Callback
    # -------------------------------------------------------------- #
    @app.callback(
        [
            # 5 KPI Cards
            Output("kpi-recommended-price", "children"),
            Output("kpi-price-delta-badge", "children"),
            Output("kpi-price-delta-badge", "className"),
            Output("kpi-price-subtext", "children"),

            Output("kpi-forecast-demand", "children"),
            Output("kpi-demand-delta-badge", "children"),
            Output("kpi-demand-delta-badge", "className"),
            Output("kpi-demand-subtext", "children"),

            Output("kpi-projected-revenue", "children"),
            Output("kpi-revenue-delta-badge", "children"),
            Output("kpi-revenue-subtext", "children"),

            Output("kpi-projected-profit", "children"),
            Output("kpi-profit-uplift-badge", "children"),
            Output("kpi-profit-uplift-badge", "className"),
            Output("kpi-profit-subtext", "children"),

            Output("kpi-gross-margin", "children"),
            Output("kpi-breakeven-badge", "children"),
            Output("kpi-margin-subtext", "children"),

            # 3 Charts
            Output("forecast-trajectory-graph", "figure"),
            Output("profit-curve-graph", "figure"),
            Output("scenario-bars-graph", "figure"),

            # Executive Briefing
            Output("narrative-risk-badge", "children"),
            Output("narrative-risk-badge", "className"),
            Output("narrative-p1", "children"),
            Output("narrative-p2", "children"),
        ],
        [
            Input("sku-dropdown", "value"),
            Input("horizon-selector", "value"),
            Input("price-slider", "value"),
            Input("demand-shock-slider", "value"),
            Input("cost-shock-slider", "value"),
            Input("competitor-slider", "value"),
        ],
    )
    def update_dashboard(
        sku_id: str,
        horizon: int,
        delta_price_pct: float,
        demand_shock_pct: float,
        cost_surge_pct: float,
        competitor_drop_pct: float,
    ):
        return compute_dashboard_metrics(
            sku_id=sku_id,
            horizon=horizon,
            delta_price_pct=delta_price_pct,
            demand_shock_pct=demand_shock_pct,
            cost_surge_pct=cost_surge_pct,
            competitor_drop_pct=competitor_drop_pct,
        )
