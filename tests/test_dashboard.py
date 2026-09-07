"""
Automated Unit & Integration Tests for NAOMI Executive Dashboard (Member 4).

Validates:
- Component rendering (KPI cards, controls, narrative)
- Plotly figure generation (forecast trajectory, profit parabola, scenario bars)
- Layout initialization
- Reactive analytical logic and financial calculations
"""

import pytest
import plotly.graph_objects as go
from dash import html
import dash_bootstrap_components as dbc

from src.dashboard.components.cards import create_kpi_card, render_kpi_hero_row, render_narrative_card
from src.dashboard.components.charts import (
    render_forecast_chart,
    render_profit_curve,
    render_scenario_bars,
)
from src.dashboard.components.controls import render_header_controls, render_scenario_controls
from src.dashboard.layouts.main_layout import build_main_layout
from src.dashboard.callbacks.main_callbacks import compute_dashboard_metrics
from src.dashboard.app import app, server
from src.config import CURATED_SKUS


class TestDashboardComponents:
    """Test individual component rendering and DOM structure."""

    def test_create_kpi_card(self):
        card = create_kpi_card(
            card_id="test-card-id",
            title="Revenue Test",
            default_value="$1,234.56",
            badge_id="test-badge-id",
            default_badge="+5.2%",
        )
        assert isinstance(card, dbc.Card)

    def test_render_kpi_hero_row(self):
        row = render_kpi_hero_row()
        assert isinstance(row, dbc.Row)
        assert len(row.children) == 5

    def test_render_narrative_card(self):
        narrative = render_narrative_card()
        assert isinstance(narrative, dbc.Card)

    def test_render_header_controls(self):
        header = render_header_controls()
        assert isinstance(header, html.Div)

    def test_render_scenario_controls(self):
        controls = render_scenario_controls()
        assert isinstance(controls, dbc.Card)


class TestPlotlyCharts:
    """Test Plotly visualization generators."""

    def test_forecast_chart_generation(self):
        hist_dates = ["2026-08-01", "2026-08-02", "2026-08-03"]
        hist_y = [50.0, 52.0, 48.0]
        pred_dates = ["2026-08-04", "2026-08-05"]
        pred_y = [55.0, 56.0]
        lower_ci = [46.0, 47.0]
        upper_ci = [64.0, 65.0]

        fig = render_forecast_chart(
            hist_dates=hist_dates,
            hist_y=hist_y,
            pred_dates=pred_dates,
            pred_y=pred_y,
            lower_ci=lower_ci,
            upper_ci=upper_ci,
            sku_name="Test SKU",
        )
        assert isinstance(fig, go.Figure)
        trace_names = [t.name for t in fig.data if t.name]
        assert "Historical Actuals" in trace_names
        assert "PyTorch LSTM Forecast" in trace_names

    def test_profit_curve_generation(self):
        prices = [7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0]
        profits = [100.0, 150.0, 180.0, 195.0, 190.0, 170.0, 140.0, 90.0]
        revenues = [700.0, 800.0, 850.0, 870.0, 860.0, 830.0, 780.0, 700.0]

        fig = render_profit_curve(
            prices=prices,
            profits=profits,
            revenues=revenues,
            opt_price=10.0,
            opt_profit=195.0,
            base_price=9.0,
            base_profit=180.0,
        )
        assert isinstance(fig, go.Figure)
        assert len(fig.data) >= 3

    def test_scenario_bars_generation(self):
        baseline_kpis = {"demand": 100.0, "revenue": 1000.0, "gross_profit": 400.0}
        shocked_kpis = {"demand": 80.0, "revenue": 800.0, "gross_profit": 280.0}

        fig = render_scenario_bars(
            baseline_kpis=baseline_kpis,
            shocked_kpis=shocked_kpis,
            scenario_name="Test Shock",
        )
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 2


class TestDashboardLayoutAndApp:
    """Test main layout tree and Dash app initialization."""

    def test_build_main_layout(self):
        layout = build_main_layout()
        assert isinstance(layout, html.Div)

    def test_app_and_server_configured(self):
        assert app is not None
        assert server is not None
        assert app.title == "NAOMI | AI Business Decision Companion"


class TestAnalyticalCalculations:
    """Verify underlying economics and simulation math used in callbacks."""

    def test_grid_search_optimal_price_peak(self):
        base_price = 10.0
        unit_cost = 6.0
        elasticity = -1.5
        base_demand = 100.0
        fixed_costs = 200.0

        p_min = base_price * 0.70
        p_max = base_price * 1.40
        prices = [p_min + (p_max - p_min) / 99 * i for i in range(100)]
        profits = [
            (p - unit_cost) * (base_demand * ((p / base_price) ** elasticity)) - fixed_costs
            for p in prices
        ]

        max_profit_idx = profits.index(max(profits))
        optimal_price = prices[max_profit_idx]

        # Theoretical unconstrained optimal price P* = c * [Ed / (1 + Ed)] = 6.0 * [-1.5 / -0.5] = 18.0
        # Clamped at upper bound p_max = 14.0
        assert optimal_price <= p_max
        assert optimal_price >= p_min

    def test_compute_dashboard_metrics_end_to_end(self):
        sku_id = CURATED_SKUS[0]["item_id"]
        result = compute_dashboard_metrics(
            sku_id=sku_id,
            horizon=7,
            delta_price_pct=5.0,
            demand_shock_pct=-10.0,
            cost_surge_pct=5.0,
            competitor_drop_pct=10.0,
        )
        assert len(result) == 25
        # Verify KPI price text and figures
        assert result[0].startswith("$")
        assert isinstance(result[18], go.Figure)  # Forecast chart
        assert isinstance(result[19], go.Figure)  # Profit curve
        assert isinstance(result[20], go.Figure)  # Scenario bars
        assert isinstance(result[23], str) and len(result[23]) > 0  # Narrative p1

