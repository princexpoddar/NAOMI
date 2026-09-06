"""
Main Executive Layout for NAOMI Dashboard.

Assembles the full responsive executive view:
- Global Navigation Header & SKU Selector
- 5 Hero KPI Metric Cards
- Middle Row: Forecast Trajectory Chart & Profit Landscape Parabola
- Bottom Row: Counterfactual Simulation Sliders, Scenario Impact Bars & AI Narrative Brief
"""

from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from src.dashboard.components.cards import render_kpi_hero_row, render_narrative_card
from src.dashboard.components.charts import DARK_TEMPLATE
from src.dashboard.components.controls import render_header_controls, render_scenario_controls


def _init_graph_figure(height: int = 360) -> go.Figure:
    """Produce an initial empty dark-themed figure to prevent white box flashes."""
    fig = go.Figure()
    fig.update_layout(
        template=DARK_TEMPLATE,
        height=height,
        paper_bgcolor="#161E2E",
        plot_bgcolor="rgba(15, 23, 42, 0.45)",
    )
    return fig


def build_main_layout() -> html.Div:
    """Construct the full executive layout tree."""
    return html.Div(
        [
            # 1. Global Navigation & Header
            render_header_controls(),

            # 2. Main Executive Content Container
            dbc.Container(
                [
                    # Top Row: 5 Hero KPI Cards
                    render_kpi_hero_row(),

                    # Middle Row: Two Core Analytical Charts
                    dbc.Row(
                        [
                            # Left: Forecast Trajectory (Actuals + LSTM + CI envelope)
                            dbc.Col(
                                dbc.Card(
                                    dbc.CardBody(
                                        dcc.Graph(
                                            id="forecast-trajectory-graph",
                                            figure=_init_graph_figure(360),
                                            config={"displayModeBar": False, "responsive": True},
                                            style={"height": "360px"},
                                        ),
                                        className="p-2",
                                    ),
                                    className="naomi-card h-100",
                                ),
                                xs=12, lg=6,
                                className="mb-4",
                            ),
                            # Right: Profit & Revenue vs Price Parabola
                            dbc.Col(
                                dbc.Card(
                                    dbc.CardBody(
                                        dcc.Graph(
                                            id="profit-curve-graph",
                                            figure=_init_graph_figure(360),
                                            config={"displayModeBar": False, "responsive": True},
                                            style={"height": "360px"},
                                        ),
                                        className="p-2",
                                    ),
                                    className="naomi-card h-100",
                                ),
                                xs=12, lg=6,
                                className="mb-4",
                            ),
                        ],
                        className="g-3 mb-1",
                    ),

                    # Bottom Row: 3-Column Decision Workspace
                    dbc.Row(
                        [
                            # 1. Counterfactual Sliders (Left)
                            dbc.Col(
                                render_scenario_controls(),
                                xs=12, lg=4,
                                className="mb-3 mb-lg-0",
                            ),
                            # 2. Scenario Comparison Bars (Middle)
                            dbc.Col(
                                dbc.Card(
                                    dbc.CardBody(
                                        dcc.Graph(
                                            id="scenario-bars-graph",
                                            figure=_init_graph_figure(345),
                                            config={"displayModeBar": False, "responsive": True},
                                            style={"height": "345px"},
                                        ),
                                        className="p-2",
                                    ),
                                    className="naomi-card h-100",
                                ),
                                xs=12, lg=4,
                                className="mb-3 mb-lg-0",
                            ),
                            # 3. AI Executive Narrative Brief (Right)
                            dbc.Col(
                                render_narrative_card(),
                                xs=12, lg=4,
                                className="mb-3 mb-lg-0",
                            ),
                        ],
                        className="g-3 pb-5",
                    ),
                ],
                fluid=True,
                className="px-3 px-md-4 mt-3",
            ),
        ],
        className="naomi-dashboard-root",
    )
