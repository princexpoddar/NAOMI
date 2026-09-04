"""Pydantic and Dataclass Schemas for NAOMI."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


@dataclass
class SKUProfile:
    """Product metadata and baseline financial attributes."""
    sku_id: str
    sku_name: str
    category: str
    department: str
    store_id: str
    base_price: float
    unit_cost: float
    fixed_costs: float = 500.0
    historical_elasticity: float = -1.0
    description: str = ""


class SalesRecord(BaseModel):
    """Schema for individual sales time-series observation."""
    date: str
    item_id: str
    item_name: str
    category: str
    store_id: str
    units_sold: float = Field(ge=0.0)
    sell_price: float = Field(gt=0.0)
    unit_cost: float = Field(gt=0.0)
    fixed_costs: float = Field(default=500.0, ge=0.0)
    event_name: Optional[str] = None
    event_type: Optional[str] = None
    snap_flag: int = Field(default=0, ge=0, le=1)
    competitor_price: float = Field(gt=0.0)


@dataclass
class ForecastOutput:
    """Output contract produced by Demand Forecasting models."""
    sku_id: str
    horizon: int
    model_name: str
    forecast_dates: List[str]
    y_pred: List[float]
    lower_ci: List[float]
    upper_ci: List[float]
    mae: float
    rmse: float
    mape: float


@dataclass
class FinancialKPIs:
    """Core financial metrics for a candidate or baseline operating state."""
    price: float
    demand: float
    revenue: float
    cogs: float
    gross_profit: float
    gross_margin_pct: float
    breakeven_units: float
    breakeven_revenue: float


@dataclass
class OptimizationResult:
    """Optimal pricing policy and profit landscape coordinates."""
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
    candidate_prices: List[float] = field(default_factory=list)
    candidate_profits: List[float] = field(default_factory=list)
    candidate_revenues: List[float] = field(default_factory=list)


@dataclass
class ScenarioResult:
    """Counterfactual scenario simulation comparison."""
    scenario_id: str
    scenario_name: str
    parameters: Dict[str, Any]
    baseline_kpis: FinancialKPIs
    shocked_kpis: FinancialKPIs
    demand_delta_pct: float
    revenue_delta_pct: float
    profit_delta_pct: float
    risk_assessment: str
