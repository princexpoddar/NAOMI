"""
Interactive Controls Component for NAOMI Executive Dashboard.

Provides:
1. Header SKU selector dropdown & forecast horizon selector.
2. 4 interactive scenario simulation sliders:
   - Candidate Price Adjustment %
   - Macro Demand Shock %
   - Supply Chain Cost Surge %
   - Competitor Price Cut %
3. Scenario Preset buttons for instantaneous C-suite scenario injection.
"""

from typing import Any, Dict, List
from dash import dcc, html
import dash_bootstrap_components as dbc
from src.config import CURATED_SKUS


def render_header_controls() -> html.Div:
    """Render the global navigation header with SKU dropdown and horizon selector."""
    sku_options = [
        {
            "label": f"{sku['item_name']} ({sku['item_id']} • ${sku['base_price']:.2f})",
            "value": sku["item_id"],
        }
        for sku in CURATED_SKUS
    ]

    return html.Div(
        [
            dbc.Row(
                [
                    # Left: Branding & Status Indicator
                    dbc.Col(
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Span("NAOMI", className="brand-title"),
                                        html.Span("DECISION COMPANION", className="brand-badge ms-2"),
                                    ],
                                    className="d-flex align-items-center mb-1",
                                ),
                                html.Div(
                                    [
                                        html.Span("🟢 Engine Active", className="text-success me-2", style={"fontSize": "0.78rem"}),
                                        html.Span("• 5.4 Yrs Walmart M5 Data", className="text-muted me-2", style={"fontSize": "0.78rem"}),
                                        html.Span("• Leeroy & Leeroy (2025) Method", className="text-muted", style={"fontSize": "0.78rem"}),
                                    ],
                                    className="d-flex align-items-center",
                                ),
                            ]
                        ),
                        xs=12, md=5,
                        className="mb-2 mb-md-0",
                    ),
                    # Right: SKU Dropdown & Horizon Selector
                    dbc.Col(
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.Label("Target SKU Profile", className="control-label"),
                                        dcc.Dropdown(
                                            id="sku-dropdown",
                                            options=sku_options,
                                            value="FOODS_3_090_CA_1",
                                            clearable=False,
                                            searchable=False,
                                            style={"fontSize": "0.85rem"},
                                        ),
                                    ],
                                    xs=12, sm=7,
                                    className="mb-2 mb-sm-0",
                                ),
                                dbc.Col(
                                    [
                                        html.Label("Horizon", className="control-label"),
                                        dbc.RadioItems(
                                            id="horizon-selector",
                                            options=[
                                                {"label": "1D", "value": 1},
                                                {"label": "7D", "value": 7},
                                                {"label": "30D", "value": 30},
                                            ],
                                            value=7,
                                            inline=True,
                                            className="btn-group",
                                            inputClassName="btn-check",
                                            labelClassName="btn btn-outline-secondary btn-sm px-2 py-1",
                                            labelCheckedClassName="active btn-primary",
                                            style={"display": "flex", "marginTop": "2px"},
                                        ),
                                    ],
                                    xs=12, sm=5,
                                ),
                            ],
                            className="g-2 align-items-end",
                        ),
                        xs=12, md=7,
                    ),
                ],
                className="align-items-center",
            )
        ],
        className="executive-header",
    )


def render_scenario_controls() -> dbc.Card:
    """Render the 4 interactive scenario simulation sliders and preset buttons."""
    return dbc.Card(
        dbc.CardBody(
            [
                html.Div(
                    [
                        html.Span("Counterfactual Shock Simulator", className="kpi-title"),
                        html.Span("Interactive Sliders", className="badge bg-indigo-subtle text-indigo px-2 py-1", style={"fontSize": "0.7rem"}),
                    ],
                    className="d-flex justify-content-between align-items-center mb-3",
                ),

                # Scenario Preset Quick-Toggles
                html.Div(
                    [
                        html.Label("Scenario Presets", className="control-label mb-1"),
                        dbc.RadioItems(
                            id="scenario-preset-radio",
                            options=[
                                {"label": "Custom", "value": "custom"},
                                {"label": "S1 Price +5%", "value": "s1_price_up"},
                                {"label": "S2 Demand -15%", "value": "s2_macro"},
                                {"label": "S3 Cost +10%", "value": "s3_cost"},
                                {"label": "S4 War -10%", "value": "s4_war"},
                                {"label": "S5 Stagflation", "value": "s5_stagflation"},
                            ],
                            value="custom",
                            inline=True,
                            className="btn-group w-100 flex-wrap mb-3",
                            inputClassName="btn-check",
                            labelClassName="btn btn-outline-secondary btn-sm py-1 px-2 mb-1",
                            labelCheckedClassName="active btn-primary",
                        ),
                    ]
                ),

                # Slider 1: Candidate Price Shift
                html.Div(
                    [
                        html.Div(
                            [
                                html.Span("1. Candidate Price Override", className="control-label mb-0"),
                                html.Span("+0.0%", id="label-price-slider", className="control-val-pill"),
                            ],
                            className="d-flex justify-content-between align-items-center mb-1",
                        ),
                        dcc.Slider(
                            id="price-slider",
                            min=-30,
                            max=40,
                            step=1,
                            value=0,
                            marks={-30: "-30%", -15: "-15%", 0: "0%", 15: "+15%", 40: "+40%"},
                            tooltip={"placement": "bottom", "always_visible": False},
                        ),
                    ],
                    className="mb-3",
                ),

                # Slider 2: Macro Demand Shock
                html.Div(
                    [
                        html.Div(
                            [
                                html.Span("2. Macro Demand Shock (Recession)", className="control-label mb-0"),
                                html.Span("0.0%", id="label-demand-shock-slider", className="control-val-pill"),
                            ],
                            className="d-flex justify-content-between align-items-center mb-1",
                        ),
                        dcc.Slider(
                            id="demand-shock-slider",
                            min=-40,
                            max=10,
                            step=1,
                            value=0,
                            marks={-40: "-40%", -25: "-25%", -15: "-15%", 0: "0%", 10: "+10%"},
                            tooltip={"placement": "bottom", "always_visible": False},
                        ),
                    ],
                    className="mb-3",
                ),

                # Slider 3: Cost Inflation Surge
                html.Div(
                    [
                        html.Div(
                            [
                                html.Span("3. Supply Chain Cost Surge", className="control-label mb-0"),
                                html.Span("0.0%", id="label-cost-shock-slider", className="control-val-pill"),
                            ],
                            className="d-flex justify-content-between align-items-center mb-1",
                        ),
                        dcc.Slider(
                            id="cost-shock-slider",
                            min=0,
                            max=40,
                            step=1,
                            value=0,
                            marks={0: "0%", 10: "+10%", 20: "+20%", 30: "+30%", 40: "+40%"},
                            tooltip={"placement": "bottom", "always_visible": False},
                        ),
                    ],
                    className="mb-3",
                ),

                # Slider 4: Competitor Price Drop
                html.Div(
                    [
                        html.Div(
                            [
                                html.Span("4. Competitor Price Cut (Price War)", className="control-label mb-0"),
                                html.Span("0.0%", id="label-competitor-slider", className="control-val-pill"),
                            ],
                            className="d-flex justify-content-between align-items-center mb-1",
                        ),
                        dcc.Slider(
                            id="competitor-slider",
                            min=0,
                            max=25,
                            step=1,
                            value=0,
                            marks={0: "0%", 5: "5%", 10: "10%", 15: "15%", 25: "25%"},
                            tooltip={"placement": "bottom", "always_visible": False},
                        ),
                    ],
                    className="mb-1",
                ),
            ],
            className="p-3",
        ),
        className="naomi-card h-100",
    )
