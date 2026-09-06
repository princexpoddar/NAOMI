"""
Plotly Chart Generators for NAOMI Executive Dashboard.

Implements 3 C-suite visualizations:
1. Forecast Trajectory Chart (Actuals + LSTM 90% CI + Baselines)
2. Profit & Revenue vs Price Curve (Parabolic optimization with P* peak marker)
3. Counterfactual Scenario Comparison (Grouped bars: Baseline vs Shocked)
"""

from typing import Dict, List, Optional
import numpy as np
import plotly.graph_objects as go


# Consistent Dark Theme Layout Defaults
DARK_TEMPLATE = dict(
    layout=go.Layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15, 23, 42, 0.45)",
        font=dict(family="Inter, Segoe UI, sans-serif", color="#94A3B8", size=12),
        margin=dict(l=45, r=25, t=35, b=35),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11, color="#CBD5E1"),
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.05)",
            zeroline=False,
            showline=True,
            linecolor="rgba(255, 255, 255, 0.1)",
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.05)",
            zeroline=False,
            showline=True,
            linecolor="rgba(255, 255, 255, 0.1)",
        ),
    )
)


def render_forecast_chart(
    hist_dates: List[str],
    hist_y: List[float],
    pred_dates: List[str],
    pred_y: List[float],
    lower_ci: Optional[List[float]] = None,
    upper_ci: Optional[List[float]] = None,
    baseline_y: Optional[List[float]] = None,
    sku_name: str = "Curated SKU",
) -> go.Figure:
    """Render demand time-series actuals and forecast with 90% confidence bands."""
    fig = go.Figure()

    # 1. Historical Actuals
    fig.add_trace(
        go.Scatter(
            x=hist_dates,
            y=hist_y,
            mode="lines",
            name="Historical Actuals",
            line=dict(color="#64748B", width=1.75),
            hovertemplate="<b>%{x}</b><br>Actual Demand: %{y:.1f} units<extra></extra>",
        )
    )

    # 2. 90% Confidence Interval Envelope
    if lower_ci and upper_ci and len(lower_ci) == len(pred_dates):
        # Upper bound
        fig.add_trace(
            go.Scatter(
                x=pred_dates,
                y=upper_ci,
                mode="lines",
                line=dict(width=0),
                hoverinfo="skip",
                showlegend=False,
            )
        )
        # Lower bound with fill
        fig.add_trace(
            go.Scatter(
                x=pred_dates,
                y=lower_ci,
                mode="lines",
                line=dict(width=0),
                fill="tonexty",
                fillcolor="rgba(16, 185, 129, 0.14)",
                name="90% Confidence Band",
                hoverinfo="skip",
            )
        )

    # 3. PyTorch LSTM Forecast
    fig.add_trace(
        go.Scatter(
            x=pred_dates,
            y=pred_y,
            mode="lines+markers",
            name="PyTorch LSTM Forecast",
            line=dict(color="#10B981", width=2.5),
            marker=dict(size=6, color="#10B981", symbol="circle"),
            hovertemplate="<b>%{x}</b><br>LSTM Forecast: %{y:.1f} units<extra></extra>",
        )
    )

    # 4. Optional Statistical Baseline Overlay
    if baseline_y and len(baseline_y) == len(pred_dates):
        fig.add_trace(
            go.Scatter(
                x=pred_dates,
                y=baseline_y,
                mode="lines",
                name="Naive Baseline",
                line=dict(color="#F59E0B", width=1.5, dash="dot"),
                hovertemplate="<b>%{x}</b><br>Baseline: %{y:.1f} units<extra></extra>",
            )
        )

    fig.update_layout(
        template=DARK_TEMPLATE,
        title=dict(
            text=f"<b>Demand Trajectory & Forecast Horizon</b> <span style='font-size:11px;color:#64748B;'>({sku_name})</span>",
            x=0.02,
            font=dict(size=14, color="#F8FAFC"),
        ),
        yaxis_title="Units Sold / Day",
        height=360,
        hovermode="x unified",
    )
    return fig


def render_profit_curve(
    prices: List[float],
    profits: List[float],
    revenues: List[float],
    opt_price: float,
    opt_profit: float,
    base_price: float,
    base_profit: float,
) -> go.Figure:
    """Render the concave profit and revenue curves vs candidate price with P* callout."""
    fig = go.Figure()

    # Revenue Curve (Secondary / Dotted)
    fig.add_trace(
        go.Scatter(
            x=prices,
            y=revenues,
            mode="lines",
            name="Gross Revenue",
            line=dict(color="#6366F1", width=2, dash="dash"),
            hovertemplate="Price: $%{x:.2f}<br>Revenue: $%{y:,.2f}<extra></extra>",
        )
    )

    # Profit Curve (Primary Emerald)
    fig.add_trace(
        go.Scatter(
            x=prices,
            y=profits,
            mode="lines",
            name="Projected Profit Π(P)",
            line=dict(color="#10B981", width=3),
            fill="tozeroy",
            fillcolor="rgba(16, 185, 129, 0.08)",
            hovertemplate="Price: $%{x:.2f}<br><b>Profit: $%{y:,.2f}</b><extra></extra>",
        )
    )

    # Optimal Price Marker (P*)
    fig.add_trace(
        go.Scatter(
            x=[opt_price],
            y=[opt_profit],
            mode="markers+text",
            name=f"Optimal P* (${opt_price:.2f})",
            marker=dict(color="#F59E0B", size=12, symbol="star"),
            text=[f"P* = ${opt_price:.2f}"],
            textposition="top center",
            textfont=dict(color="#FCD34D", size=11, family="Inter, sans-serif"),
            hovertemplate="<b>Optimal Price P*</b>: $%{x:.2f}<br>Max Profit: $%{y:,.2f}<extra></extra>",
        )
    )

    # Baseline Price Indicator
    fig.add_trace(
        go.Scatter(
            x=[base_price],
            y=[base_profit],
            mode="markers+text",
            name=f"Baseline P₀ (${base_price:.2f})",
            marker=dict(color="#94A3B8", size=9, symbol="diamond"),
            text=[f"P₀ = ${base_price:.2f}"],
            textposition="bottom center",
            textfont=dict(color="#CBD5E1", size=10),
            hovertemplate="Baseline Price: $%{x:.2f}<br>Profit: $%{y:,.2f}<extra></extra>",
        )
    )

    # Vertical dashed line at optimal price
    fig.add_vline(
        x=opt_price,
        line_width=1.5,
        line_dash="dot",
        line_color="rgba(245, 158, 11, 0.6)",
    )

    fig.update_layout(
        template=DARK_TEMPLATE,
        title=dict(
            text="<b>Profit & Revenue vs. Price Landscape</b> <span style='font-size:11px;color:#64748B;'>(Grid Sweep [0.70P₀, 1.40P₀])</span>",
            x=0.02,
            font=dict(size=14, color="#F8FAFC"),
        ),
        xaxis_title="Candidate Price ($)",
        yaxis_title="Amount ($)",
        height=360,
        hovermode="closest",
    )
    return fig


def render_scenario_bars(
    baseline_kpis: Dict[str, float],
    shocked_kpis: Dict[str, float],
    scenario_name: str = "Simulated Shock",
) -> go.Figure:
    """Render grouped bar chart comparing Baseline vs Shocked metrics."""
    metrics = ["Demand (Units)", "Revenue ($)", "Gross Profit ($)"]
    
    base_values = [
        baseline_kpis.get("demand", 0.0),
        baseline_kpis.get("revenue", 0.0),
        baseline_kpis.get("gross_profit", 0.0),
    ]
    shock_values = [
        shocked_kpis.get("demand", 0.0),
        shocked_kpis.get("revenue", 0.0),
        shocked_kpis.get("gross_profit", 0.0),
    ]

    fig = go.Figure(
        data=[
            go.Bar(
                name="Baseline Operating State",
                x=metrics,
                y=base_values,
                marker_color="#475569",
                hovertemplate="%{x}: <b>%{y:,.2f}</b><extra></extra>",
            ),
            go.Bar(
                name=f"Shock: {scenario_name}",
                x=metrics,
                y=shock_values,
                marker_color="#6366F1",
                hovertemplate="%{x}: <b>%{y:,.2f}</b><extra></extra>",
            ),
        ]
    )

    fig.update_layout(
        template=DARK_TEMPLATE,
        barmode="group",
        title=dict(
            text="<b>Counterfactual Shock Impact Comparison</b>",
            x=0.02,
            font=dict(size=14, color="#F8FAFC"),
        ),
        height=330,
        margin=dict(l=45, r=25, t=35, b=30),
    )
    return fig
