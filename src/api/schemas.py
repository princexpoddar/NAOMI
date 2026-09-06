"""
Pydantic request/response schemas for the NAOMI REST API.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ------------------------------------------------------------------ #
# Shared
# ------------------------------------------------------------------ #

class HealthResponse(BaseModel):
    status: str = "ok"
    version: str
    message: str


class SKUInfo(BaseModel):
    item_id: str
    item_name: str
    category: str
    department: str
    store_id: str
    base_price: float
    historical_elasticity: float
    description: str


class SKUListResponse(BaseModel):
    skus: List[SKUInfo]
    count: int


# ------------------------------------------------------------------ #
# /forecast
# ------------------------------------------------------------------ #

class ForecastRequest(BaseModel):
    sku_id: str = Field(..., description="SKU identifier (must be in CURATED_SKUS)")
    horizon: int = Field(
        default=7,
        ge=1,
        le=30,
        description="Number of days ahead to forecast (1, 7, or 30)",
    )
    model: str = Field(
        default="lstm",
        description="Model to use: lstm | naive | seasonal_naive | moving_average | ridge",
    )


class ForecastResponse(BaseModel):
    sku_id: str
    horizon: int
    model_name: str
    forecast_dates: List[str]
    y_pred: List[float]
    lower_ci: List[float]
    upper_ci: List[float]
    mae: Optional[float] = None
    rmse: Optional[float] = None
    mape: Optional[float] = None


# ------------------------------------------------------------------ #
# /pricing/optimize
# ------------------------------------------------------------------ #

class OptimizePricingRequest(BaseModel):
    sku_id: str = Field(..., description="SKU identifier")
    base_demand: float = Field(
        ...,
        gt=0,
        description="Expected demand units at current base price",
    )
    override_elasticity: Optional[float] = Field(
        default=None,
        description="Override the SKU's historical elasticity (must be ≤ 0)",
    )
    override_unit_cost: Optional[float] = Field(
        default=None,
        gt=0,
        description="Override the SKU's unit cost",
    )
    fixed_costs: float = Field(
        default=500.0,
        ge=0,
        description="Periodic fixed overhead ($)",
    )
    price_grid_points: int = Field(
        default=100,
        ge=10,
        le=500,
        description="Resolution of the profit curve grid search",
    )


class OptimizePricingResponse(BaseModel):
    sku_id: str
    base_price: float
    optimal_price: float
    price_change_pct: float
    base_demand: float
    optimal_demand: float
    demand_change_pct: float
    base_profit: float
    optimal_profit: float
    profit_uplift_pct: float
    optimal_revenue: float
    elasticity: float
    candidate_prices: List[float]
    candidate_profits: List[float]
    candidate_revenues: List[float]


# ------------------------------------------------------------------ #
# /simulate
# ------------------------------------------------------------------ #

class SimulateRequest(BaseModel):
    sku_id: str = Field(
        ...,
        description="SKU identifier — used to pull baseline price, cost, and elasticity",
    )
    scenario_type: str = Field(
        ...,
        description=(
            "Scenario to run: price_policy | macro_demand_shock | "
            "supply_chain_inflation | competitor_price_war | stagflation"
        ),
    )
    base_demand: float = Field(
        ...,
        gt=0,
        description="Baseline demand units (e.g. last 7-day average)",
    )
    params: Dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Scenario-specific parameters:\n"
            "  price_policy            → delta_price_pct (float)\n"
            "  macro_demand_shock      → shock_pct (float, default 15)\n"
            "  supply_chain_inflation  → cost_pct (float, default 10)\n"
            "  competitor_price_war    → competitor_price_drop_pct (float, default 10)\n"
            "  stagflation             → cost_surge_pct (float), demand_contraction_pct (float)"
        ),
    )
    override_unit_cost: Optional[float] = Field(
        default=None,
        gt=0,
        description="Override the SKU's unit cost for this simulation",
    )
    override_elasticity: Optional[float] = Field(
        default=None,
        description="Override the SKU's historical elasticity (must be ≤ 0)",
    )
    fixed_costs: float = Field(
        default=500.0,
        ge=0,
        description="Periodic fixed overhead ($)",
    )


class FinancialKPIsSchema(BaseModel):
    price: float
    demand: float
    revenue: float
    cogs: float
    gross_profit: float
    gross_margin_pct: float
    breakeven_units: float
    breakeven_revenue: float


class SimulateResponse(BaseModel):
    scenario_id: str
    scenario_name: str
    parameters: Dict[str, Any]
    baseline_kpis: FinancialKPIsSchema
    shocked_kpis: FinancialKPIsSchema
    demand_delta_pct: float
    revenue_delta_pct: float
    profit_delta_pct: float
    risk_assessment: str
