import logging
import os
from pathlib import Path
from typing import AsyncGenerator

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.config import PROJECT_ROOT

logger = logging.getLogger("naomi.database")

# ------------------------------------------------------------------ #
# Connection URL & Engine Configuration
# ------------------------------------------------------------------ #
DEFAULT_DB_DIR = PROJECT_ROOT / "data"
DEFAULT_DB_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_SQLITE_PATH = (DEFAULT_DB_DIR / "naomi.db").resolve()
DEFAULT_SQLITE_URL = f"sqlite+aiosqlite:///{DEFAULT_SQLITE_PATH.as_posix()}"

DATABASE_URL: str = os.getenv("DATABASE_URL", DEFAULT_SQLITE_URL)

is_sqlite = DATABASE_URL.startswith("sqlite")

if is_sqlite:
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
    )
else:
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
    )

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ------------------------------------------------------------------ #
# Base ORM declarative
# ------------------------------------------------------------------ #
class Base(DeclarativeBase):
    pass


# ------------------------------------------------------------------ #
# ORM Models
# ------------------------------------------------------------------ #

class ForecastLog(Base):
    """Persists each /forecast request + response for auditability."""

    __tablename__ = "forecast_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    sku_id = Column(String(64), nullable=False, index=True)
    horizon = Column(Integer, nullable=False)
    model_name = Column(String(64), nullable=False)
    # Serialised list of predicted values
    y_pred = Column(JSON, nullable=False)
    lower_ci = Column(JSON, nullable=True)
    upper_ci = Column(JSON, nullable=True)
    mae = Column(Float, nullable=True)
    rmse = Column(Float, nullable=True)
    mape = Column(Float, nullable=True)
    # Raw request payload stored for reproducibility
    request_payload = Column(JSON, nullable=True)


class OptimizationLog(Base):
    """Persists each /pricing/optimize request + result."""

    __tablename__ = "optimization_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    sku_id = Column(String(64), nullable=False, index=True)
    base_price = Column(Float, nullable=False)
    optimal_price = Column(Float, nullable=False)
    price_change_pct = Column(Float, nullable=False)
    base_profit = Column(Float, nullable=False)
    optimal_profit = Column(Float, nullable=False)
    profit_uplift_pct = Column(Float, nullable=False)
    elasticity = Column(Float, nullable=False)
    request_payload = Column(JSON, nullable=True)
    result_payload = Column(JSON, nullable=True)


class SimulationLog(Base):
    """Persists each /simulate request + ScenarioResult."""

    __tablename__ = "simulation_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    sku_id = Column(String(64), nullable=False, index=True)
    scenario_type = Column(String(64), nullable=False)
    scenario_id = Column(String(8), nullable=False)
    scenario_name = Column(String(128), nullable=False)
    demand_delta_pct = Column(Float, nullable=False)
    revenue_delta_pct = Column(Float, nullable=False)
    profit_delta_pct = Column(Float, nullable=False)
    risk_assessment = Column(Text, nullable=False)
    # Full request + result stored as JSON blobs
    request_payload = Column(JSON, nullable=True)
    result_payload = Column(JSON, nullable=True)


# ------------------------------------------------------------------ #
# Async dependency for FastAPI
# ------------------------------------------------------------------ #
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ------------------------------------------------------------------ #
# Schema creation utility (called at startup)
# ------------------------------------------------------------------ #
async def init_db() -> None:
    """Create all tables if they do not already exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
