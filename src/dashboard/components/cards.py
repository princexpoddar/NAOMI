"""
KPI Hero Cards Component for NAOMI Executive Dashboard.

Renders 5 C-suite financial metric cards:
1. Recommended Optimal Price (P*)
2. Forecasted Demand (Q*)
3. Projected Revenue (R*)
4. Projected Profit (Pi*) with profit uplift badge
5. Gross Margin % and Breakeven Units
"""

from typing import Optional
from dash import html
import dash_bootstrap_components as dbc


def create_kpi_card(
    card_id: str,
    title: str,
    default_value: str,
    badge_id: Optional[str] = None,
    default_badge: Optional[str] = None,
    badge_class: str = "badge-positive",
    subtext_id: Optional[str] = None,
    default_subtext: Optional[str] = None,
    icon: str = "bi-graph-up",
) -> dbc.Card:
    """Build a styled glassmorphic KPI Hero Card."""
    card_children = [
        html.Div(
            [
                html.Span(title, className="kpi-title"),
                html.I(className=f"bi {icon} text-muted", style={"fontSize": "1rem"}),
            ],
            className="d-flex justify-content-between align-items-center mb-1",
        ),
        html.Div(
            default_value,
            id=card_id,
            className="kpi-value",
        ),
    ]

    # Optional dynamic badge
    if badge_id:
        card_children.append(
            html.Div(
                html.Span(
                    default_badge or "+0.0%",
                    id=badge_id,
                    className=f"kpi-badge {badge_class}",
                ),
                className="my-1",
            )
        )

    # Optional subtext line
    if subtext_id:
        card_children.append(
            html.Div(
                default_subtext or "",
                id=subtext_id,
                className="kpi-subtext",
            )
        )

    return dbc.Card(
        dbc.CardBody(card_children, className="p-3"),
        className="naomi-card h-100",
    )


def render_kpi_hero_row() -> dbc.Row:
    """Render the top 5 KPI hero cards in a responsive grid row."""
    return dbc.Row(
        [
            dbc.Col(
                create_kpi_card(
                    card_id="kpi-recommended-price",
                    title="Recommended Price (P*)",
                    default_value="$9.99",
                    badge_id="kpi-price-delta-badge",
                    default_badge="+0.0% vs Base",
                    badge_class="badge-positive",
                    subtext_id="kpi-price-subtext",
                    default_subtext="Baseline: $9.99",
                    icon="bi-tag",
                ),
                xs=12, sm=6, lg=True,
                className="mb-3 mb-lg-0",
            ),
            dbc.Col(
                create_kpi_card(
                    card_id="kpi-forecast-demand",
                    title="Forecasted Demand (Q*)",
                    default_value="66.0 units",
                    badge_id="kpi-demand-delta-badge",
                    default_badge="+0.0% vol",
                    badge_class="badge-neutral",
                    subtext_id="kpi-demand-subtext",
                    default_subtext="7-Day Horizon Demand",
                    icon="bi-box-seam",
                ),
                xs=12, sm=6, lg=True,
                className="mb-3 mb-lg-0",
            ),
            dbc.Col(
                create_kpi_card(
                    card_id="kpi-projected-revenue",
                    title="Projected Revenue",
                    default_value="$659.34",
                    badge_id="kpi-revenue-delta-badge",
                    default_badge="+0.0%",
                    badge_class="badge-neutral",
                    subtext_id="kpi-revenue-subtext",
                    default_subtext="Gross Receipts: P * Q",
                    icon="bi-cash-coin",
                ),
                xs=12, sm=6, lg=True,
                className="mb-3 mb-lg-0",
            ),
            dbc.Col(
                create_kpi_card(
                    card_id="kpi-projected-profit",
                    title="Projected Profit (Π*)",
                    default_value="$263.74",
                    badge_id="kpi-profit-uplift-badge",
                    default_badge="+0.0% Uplift",
                    badge_class="badge-positive",
                    subtext_id="kpi-profit-subtext",
                    default_subtext="Net Operating Margin",
                    icon="bi-trophy",
                ),
                xs=12, sm=6, lg=True,
                className="mb-3 mb-lg-0",
            ),
            dbc.Col(
                create_kpi_card(
                    card_id="kpi-gross-margin",
                    title="Gross Margin %",
                    default_value="40.0%",
                    badge_id="kpi-breakeven-badge",
                    default_badge="BE: 125 units",
                    badge_class="badge-neutral",
                    subtext_id="kpi-margin-subtext",
                    default_subtext="Breakeven: $1,248.75",
                    icon="bi-pie-chart",
                ),
                xs=12, sm=6, lg=True,
                className="mb-3 mb-lg-0",
            ),
        ],
        className="g-3 mb-4",
    )


def render_narrative_card() -> dbc.Card:
    """Render the C-suite Executive Decision Companion Narrative Card."""
    return dbc.Card(
        dbc.CardBody(
            [
                html.Div(
                    [
                        html.Span("Strategic Decision Companion", className="kpi-title"),
                        html.Span(
                            "Stable",
                            id="narrative-risk-badge",
                            className="badge bg-success-subtle text-success px-2 py-1",
                            style={"fontSize": "0.72rem", "fontWeight": "700"},
                        ),
                    ],
                    className="d-flex justify-content-between align-items-center mb-2",
                ),
                html.Div(
                    [
                        html.P(
                            "Analyzing current SKU price elasticity and demand dynamics…",
                            id="narrative-p1",
                            className="mb-2",
                        ),
                        html.P(
                            "Simulation indicates healthy operating profit margins with controlled downside risk.",
                            id="narrative-p2",
                            className="mb-0 text-secondary",
                        ),
                    ],
                    id="narrative-box",
                    className="narrative-box mb-2",
                ),
                html.Div(
                    "Notice: AI-assisted strategic guidance; non-binding C-suite recommendation.",
                    className="disclaimer-badge",
                ),
            ],
            className="p-3",
        ),
        className="naomi-card h-100",
    )
