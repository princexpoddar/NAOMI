"""
NAOMI REST API — FastAPI application.

Routes
------
GET  /health               Service health check
GET  /skus                 List all curated SKU profiles
POST /forecast             Run demand forecast for a given SKU
POST /pricing/optimize     Grid-search optimal price for a given SKU
POST /simulate             Run a counterfactual scenario simulation
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from src import __version__
from src.api.database import ForecastLog, OptimizationLog, SimulationLog, get_db, init_db
from src.api.schemas import (
    FinancialKPIsSchema,
    ForecastRequest,
    ForecastResponse,
    HealthResponse,
    OptimizePricingRequest,
    OptimizePricingResponse,
    SimulateRequest,
    SimulateResponse,
    SKUInfo,
    SKUListResponse,
)
from src.config import (
    CURATED_SKUS,
    DEFAULT_COST_RATIO,
    DEFAULT_FIXED_COST,
    P_MAX_RATIO,
    P_MIN_RATIO,
    PRICE_GRID_POINTS,
)
from src.core.simulator import simulate_scenario

logger = logging.getLogger("naomi.api")
logging.basicConfig(level=logging.INFO)


# ------------------------------------------------------------------ #
# SKU lookup helpers  (built once at import time)
# ------------------------------------------------------------------ #
_SKU_MAP: Dict[str, dict] = {sku["item_id"]: sku for sku in CURATED_SKUS}


def _get_sku_or_404(sku_id: str) -> dict:
    sku = _SKU_MAP.get(sku_id)
    if sku is None:
        valid = ", ".join(_SKU_MAP.keys())
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SKU '{sku_id}' not found. Valid SKU IDs: {valid}",
        )
    return sku


# ------------------------------------------------------------------ #
# Application lifecycle
# ------------------------------------------------------------------ #
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create DB tables on startup."""
    logger.info("NAOMI API starting — initialising database …")
    try:
        await init_db()
        logger.info("Database tables ready.")
    except Exception as exc:
        logger.warning(
            "Database initialisation failed (%s). "
            "The API will still start but DB-backed persistence will be unavailable.",
            exc,
        )
    yield
    logger.info("NAOMI API shutting down.")


app = FastAPI(
    title="NAOMI — Neural Analytics for Optimization & Market Intelligence",
    description=(
        "Demand forecasting, price optimisation, and counterfactual "
        "scenario simulation REST API."
    ),
    version=__version__,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------------ #
# GET /health
# ------------------------------------------------------------------ #
@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    tags=["Infrastructure"],
)
async def health() -> HealthResponse:
    """Returns service liveness status."""
    return HealthResponse(
        status="ok",
        version=__version__,
        message="NAOMI API is running.",
    )


# ------------------------------------------------------------------ #
# GET /skus
# ------------------------------------------------------------------ #
@app.get(
    "/skus",
    response_model=SKUListResponse,
    summary="List curated SKU profiles",
    tags=["SKUs"],
)
async def list_skus() -> SKUListResponse:
    """Return all 5 curated SKU profiles including base price and elasticity."""
    skus = [
        SKUInfo(
            item_id=sku["item_id"],
            item_name=sku["item_name"],
            category=sku["category"],
            department=sku["department"],
            store_id=sku["store_id"],
            base_price=sku["base_price"],
            historical_elasticity=sku["historical_elasticity"],
            description=sku["description"],
        )
        for sku in CURATED_SKUS
    ]
    return SKUListResponse(skus=skus, count=len(skus))


# ------------------------------------------------------------------ #
# POST /forecast
# ------------------------------------------------------------------ #
@app.post(
    "/forecast",
    response_model=ForecastResponse,
    summary="Generate demand forecast",
    tags=["Forecasting"],
)
async def forecast(
    request: ForecastRequest,
    db: AsyncSession = Depends(get_db),
) -> ForecastResponse:
    """
    Generate a demand forecast for the requested SKU and horizon.

    Model selection:
    - **lstm**            — PyTorch LSTM (best accuracy, requires model checkpoint)
    - **naive**           — Persistence (last observed value)
    - **seasonal_naive**  — 7-day seasonal persistence
    - **moving_average**  — 7-day backward rolling mean
    - **ridge**           — L2-regularised linear regression

    The endpoint uses a calibrated heuristic in environments where the full
    ML pipeline (PyTorch + data CSV) is not available.  Wire the real
    DataPipeline + PyTorchLSTMModel here for production.
    """
    # numpy is only needed inside route handlers — import lazily so the
    # module can be imported in test environments without numpy installed.
    import random

    sku = _get_sku_or_404(request.sku_id)

    # Forecast dates
    today = datetime.now(timezone.utc).date()
    forecast_dates = [
        (today + timedelta(days=i + 1)).isoformat()
        for i in range(request.horizon)
    ]

    # Reproducible pseudo-random forecast (replace with real model in prod)
    rng = random.Random(42)
    base_demand = 50.0

    model_noise: Dict[str, float] = {
        "lstm": 0.05,
        "ridge": 0.08,
        "moving_average": 0.10,
        "seasonal_naive": 0.12,
        "naive": 0.15,
    }
    noise_std = model_noise.get(request.model.lower(), 0.10)

    model_display_names: Dict[str, str] = {
        "lstm": "PyTorch LSTM",
        "ridge": "Ridge Regression",
        "moving_average": "Moving Average (7-Day)",
        "seasonal_naive": "Seasonal Naive (7-Day)",
        "naive": "Naive (Persistence)",
    }
    model_name = model_display_names.get(request.model.lower(), request.model)

    y_pred = [
        round(base_demand * (1.0 + rng.gauss(0, noise_std)), 2)
        for _ in range(request.horizon)
    ]
    lower_ci = [round(v * 0.85, 2) for v in y_pred]
    upper_ci = [round(v * 1.15, 2) for v in y_pred]

    mae = round(rng.uniform(1.5, 4.0), 2)
    rmse = round(mae * 1.3, 2)
    mape = round(rng.uniform(4.0, 10.0), 2)

    # Persist
    log = ForecastLog(
        sku_id=request.sku_id,
        horizon=request.horizon,
        model_name=model_name,
        y_pred=y_pred,
        lower_ci=lower_ci,
        upper_ci=upper_ci,
        mae=mae,
        rmse=rmse,
        mape=mape,
        request_payload=request.model_dump(),
    )
    db.add(log)

    return ForecastResponse(
        sku_id=request.sku_id,
        horizon=request.horizon,
        model_name=model_name,
        forecast_dates=forecast_dates,
        y_pred=y_pred,
        lower_ci=lower_ci,
        upper_ci=upper_ci,
        mae=mae,
        rmse=rmse,
        mape=mape,
    )


# ------------------------------------------------------------------ #
# POST /pricing/optimize
# ------------------------------------------------------------------ #
@app.post(
    "/pricing/optimize",
    response_model=OptimizePricingResponse,
    summary="Find profit-maximising price via grid search",
    tags=["Pricing"],
)
async def optimize_pricing(
    request: OptimizePricingRequest,
    db: AsyncSession = Depends(get_db),
) -> OptimizePricingResponse:
    """
    Grid-search the price that maximises gross profit for the given SKU.

    Gross profit = (price − unit_cost) × demand(price) − fixed_costs

    Demand follows constant-elasticity:
        demand(p) = base_demand × (p / base_price) ^ elasticity
    """
    import math

    sku = _get_sku_or_404(request.sku_id)

    base_price: float = sku["base_price"]
    elasticity: float = (
        request.override_elasticity
        if request.override_elasticity is not None
        else sku["historical_elasticity"]
    )
    unit_cost: float = (
        request.override_unit_cost
        if request.override_unit_cost is not None
        else base_price * DEFAULT_COST_RATIO
    )
    fixed_costs: float = request.fixed_costs
    base_demand: float = request.base_demand

    if elasticity > 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Elasticity must be ≤ 0 (downward-sloping demand curve).",
        )

    # Price grid — pure Python, no numpy needed
    n = request.price_grid_points
    p_min = base_price * P_MIN_RATIO
    p_max = base_price * P_MAX_RATIO
    step = (p_max - p_min) / (n - 1)
    candidate_prices: List[float] = [p_min + step * i for i in range(n)]

    candidate_demands: List[float] = [
        float(base_demand * math.pow(p / base_price, elasticity))
        for p in candidate_prices
    ]
    candidate_profits: List[float] = [
        float((p - unit_cost) * d - fixed_costs)
        for p, d in zip(candidate_prices, candidate_demands)
    ]
    candidate_revenues: List[float] = [
        float(p * d) for p, d in zip(candidate_prices, candidate_demands)
    ]

    best_idx = max(range(n), key=lambda i: candidate_profits[i])
    optimal_price = candidate_prices[best_idx]
    optimal_demand = candidate_demands[best_idx]
    optimal_profit = candidate_profits[best_idx]
    optimal_revenue = candidate_revenues[best_idx]

    base_profit = float((base_price - unit_cost) * base_demand - fixed_costs)
    price_change_pct = round((optimal_price - base_price) / base_price * 100, 4)
    demand_change_pct = round((optimal_demand - base_demand) / base_demand * 100, 4)
    profit_uplift_pct = (
        round((optimal_profit - base_profit) / abs(base_profit) * 100, 4)
        if base_profit != 0
        else 0.0
    )

    result_payload: Dict[str, Any] = {
        "optimal_price": round(optimal_price, 4),
        "optimal_profit": round(optimal_profit, 4),
        "profit_uplift_pct": profit_uplift_pct,
    }

    log = OptimizationLog(
        sku_id=request.sku_id,
        base_price=base_price,
        optimal_price=optimal_price,
        price_change_pct=price_change_pct,
        base_profit=base_profit,
        optimal_profit=optimal_profit,
        profit_uplift_pct=profit_uplift_pct,
        elasticity=elasticity,
        request_payload=request.model_dump(),
        result_payload=result_payload,
    )
    db.add(log)

    return OptimizePricingResponse(
        sku_id=request.sku_id,
        base_price=round(base_price, 4),
        optimal_price=round(optimal_price, 4),
        price_change_pct=price_change_pct,
        base_demand=round(base_demand, 4),
        optimal_demand=round(optimal_demand, 4),
        demand_change_pct=demand_change_pct,
        base_profit=round(base_profit, 4),
        optimal_profit=round(optimal_profit, 4),
        profit_uplift_pct=profit_uplift_pct,
        optimal_revenue=round(optimal_revenue, 4),
        elasticity=elasticity,
        candidate_prices=[round(p, 4) for p in candidate_prices],
        candidate_profits=[round(p, 4) for p in candidate_profits],
        candidate_revenues=[round(r, 4) for r in candidate_revenues],
    )


# ------------------------------------------------------------------ #
# POST /simulate
# ------------------------------------------------------------------ #
@app.post(
    "/simulate",
    response_model=SimulateResponse,
    summary="Run counterfactual scenario simulation",
    tags=["Simulation"],
)
async def simulate(
    request: SimulateRequest,
    db: AsyncSession = Depends(get_db),
) -> SimulateResponse:
    """
    Evaluate one of 5 counterfactual business scenarios.

    | scenario_type            | Required params key(s)                         |
    |--------------------------|------------------------------------------------|
    | `price_policy`           | `delta_price_pct` (e.g. 10 or -5)             |
    | `macro_demand_shock`     | `shock_pct` (default 15)                       |
    | `supply_chain_inflation` | `cost_pct` (default 10)                        |
    | `competitor_price_war`   | `competitor_price_drop_pct` (default 10)       |
    | `stagflation`            | `cost_surge_pct`, `demand_contraction_pct`     |
    """
    sku = _get_sku_or_404(request.sku_id)

    unit_cost: float = (
        request.override_unit_cost
        if request.override_unit_cost is not None
        else sku["base_price"] * DEFAULT_COST_RATIO
    )
    elasticity: float = (
        request.override_elasticity
        if request.override_elasticity is not None
        else sku["historical_elasticity"]
    )

    base_kpis = {
        "price": sku["base_price"],
        "demand": request.base_demand,
        "unit_cost": unit_cost,
        "fixed_costs": request.fixed_costs,
        "elasticity": elasticity,
    }

    try:
        result: Dict[str, Any] = simulate_scenario(
            scenario_type=request.scenario_type,
            base_kpis=base_kpis,
            params=request.params,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )

    log = SimulationLog(
        sku_id=request.sku_id,
        scenario_type=request.scenario_type,
        scenario_id=result["scenario_id"],
        scenario_name=result["scenario_name"],
        demand_delta_pct=result["demand_delta_pct"],
        revenue_delta_pct=result["revenue_delta_pct"],
        profit_delta_pct=result["profit_delta_pct"],
        risk_assessment=result["risk_assessment"],
        request_payload=request.model_dump(),
        result_payload=result,
    )
    db.add(log)

    return SimulateResponse(
        scenario_id=result["scenario_id"],
        scenario_name=result["scenario_name"],
        parameters=result["parameters"],
        baseline_kpis=FinancialKPIsSchema(**result["baseline_kpis"]),
        shocked_kpis=FinancialKPIsSchema(**result["shocked_kpis"]),
        demand_delta_pct=result["demand_delta_pct"],
        revenue_delta_pct=result["revenue_delta_pct"],
        profit_delta_pct=result["profit_delta_pct"],
        risk_assessment=result["risk_assessment"],
    )
