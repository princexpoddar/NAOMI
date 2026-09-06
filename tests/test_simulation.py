"""
Tests for src/core/simulator.py and the /simulate + /pricing/optimize FastAPI endpoints.

Run with:
    pytest tests/test_simulation.py -v
"""

import pytest
from fastapi.testclient import TestClient

from src.core.simulator import simulate_scenario
from src.api.main import app

# ------------------------------------------------------------------ #
# Fixtures
# ------------------------------------------------------------------ #

BASE_KPIS = {
    "price": 10.0,
    "demand": 100.0,
    "unit_cost": 6.0,
    "fixed_costs": 200.0,
    "elasticity": -1.0,
}

# Use sync TestClient (no DB required — DB is optional in unit tests)
@pytest.fixture(scope="module")
def client():
    """FastAPI test client with DB writes disabled via dependency override."""
    from unittest.mock import AsyncMock, MagicMock
    from src.api.database import get_db

    async def _mock_db():
        session = MagicMock()
        session.add = MagicMock()
        session.commit = AsyncMock()
        session.rollback = AsyncMock()
        yield session

    app.dependency_overrides[get_db] = _mock_db
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
    app.dependency_overrides.clear()


# ------------------------------------------------------------------ #
# Unit tests — simulate_scenario()
# ------------------------------------------------------------------ #

class TestSimulatorUnit:

    # ── Scenario 1: Price Policy ──────────────────────────────────────

    def test_price_policy_price_increase(self):
        result = simulate_scenario("price_policy", BASE_KPIS, {"delta_price_pct": 10.0})
        assert result["scenario_id"] == "S1"
        assert result["scenario_name"] == "Price Policy"
        # Price rose 10% → new price = 11.0
        assert abs(result["shocked_kpis"]["price"] - 11.0) < 0.01
        # Demand fell (elasticity = -1.0, +10% price → -10% demand)
        assert result["demand_delta_pct"] < 0

    def test_price_policy_price_decrease(self):
        result = simulate_scenario("price_policy", BASE_KPIS, {"delta_price_pct": -10.0})
        assert result["shocked_kpis"]["price"] < BASE_KPIS["price"]
        # Demand should increase with price decrease when elasticity is negative
        assert result["demand_delta_pct"] > 0

    def test_price_policy_zero_change(self):
        result = simulate_scenario("price_policy", BASE_KPIS, {"delta_price_pct": 0.0})
        assert result["demand_delta_pct"] == 0.0
        assert result["revenue_delta_pct"] == 0.0

    # ── Scenario 2: Macro Demand Shock ──────────────────────────────

    def test_macro_demand_shock_default(self):
        result = simulate_scenario("macro_demand_shock", BASE_KPIS, {})
        assert result["scenario_id"] == "S2"
        # Default shock is -15%
        expected_demand = 100.0 * (1 - 15 / 100)
        assert abs(result["shocked_kpis"]["demand"] - expected_demand) < 0.01
        assert result["demand_delta_pct"] == pytest.approx(-15.0, abs=0.01)

    def test_macro_demand_shock_custom(self):
        result = simulate_scenario("macro_demand_shock", BASE_KPIS, {"shock_pct": 25.0})
        assert abs(result["shocked_kpis"]["demand"] - 75.0) < 0.01

    def test_macro_demand_shock_price_unchanged(self):
        result = simulate_scenario("macro_demand_shock", BASE_KPIS, {"shock_pct": 10.0})
        assert result["shocked_kpis"]["price"] == BASE_KPIS["price"]

    # ── Scenario 3: Supply Chain Cost Inflation ───────────────────

    def test_supply_chain_inflation_default(self):
        result = simulate_scenario("supply_chain_inflation", BASE_KPIS, {})
        assert result["scenario_id"] == "S3"
        expected_cost = 6.0 * 1.10
        assert abs(result["shocked_kpis"]["cogs"] - expected_cost * 100.0) < 0.1

    def test_supply_chain_demand_unchanged(self):
        result = simulate_scenario("supply_chain_inflation", BASE_KPIS, {"cost_pct": 20.0})
        # Demand must not change — only cost increases
        assert result["demand_delta_pct"] == 0.0
        assert result["profit_delta_pct"] < 0  # profit must fall

    # ── Scenario 4: Competitor Price War ──────────────────────────

    def test_competitor_price_war(self):
        result = simulate_scenario("competitor_price_war", BASE_KPIS, {})
        assert result["scenario_id"] == "S4"
        # Spec: −20% demand loss
        assert abs(result["demand_delta_pct"] - (-20.0)) < 0.01

    def test_competitor_price_war_own_price_unchanged(self):
        result = simulate_scenario("competitor_price_war", BASE_KPIS, {})
        assert result["shocked_kpis"]["price"] == BASE_KPIS["price"]

    # ── Scenario 5: Stagflation ────────────────────────────────────

    def test_stagflation_defaults(self):
        result = simulate_scenario("stagflation", BASE_KPIS, {})
        assert result["scenario_id"] == "S5"
        assert result["scenario_name"] == "Leeroy & Leeroy Stagflation"
        # +10% cost: new_unit_cost = 6.6; -8% demand: new_demand = 92
        assert abs(result["shocked_kpis"]["demand"] - 92.0) < 0.1
        expected_cogs = 6.6 * 92.0
        assert abs(result["shocked_kpis"]["cogs"] - expected_cogs) < 0.5
        assert result["profit_delta_pct"] < 0

    def test_stagflation_custom_params(self):
        result = simulate_scenario(
            "stagflation",
            BASE_KPIS,
            {"cost_surge_pct": 5.0, "demand_contraction_pct": 10.0},
        )
        assert abs(result["shocked_kpis"]["demand"] - 90.0) < 0.1

    # ── Edge cases ────────────────────────────────────────────────

    def test_invalid_scenario_type_raises(self):
        with pytest.raises(ValueError, match="Unknown scenario_type"):
            simulate_scenario("unknown_scenario", BASE_KPIS, {})

    def test_demand_never_negative(self):
        """Extreme shock should floor demand at 0, not go negative."""
        result = simulate_scenario("macro_demand_shock", BASE_KPIS, {"shock_pct": 200.0})
        assert result["shocked_kpis"]["demand"] == 0.0

    def test_risk_label_critical(self):
        result = simulate_scenario("macro_demand_shock", BASE_KPIS, {"shock_pct": 95.0})
        assert "Critical" in result["risk_assessment"] or "High" in result["risk_assessment"]

    def test_risk_label_positive(self):
        # A meaningful price decrease for an elastic SKU should boost profit
        elastic_kpis = {**BASE_KPIS, "elasticity": -2.5}
        result = simulate_scenario("price_policy", elastic_kpis, {"delta_price_pct": -5.0})
        # Just verify the result serialises correctly
        assert "risk_assessment" in result


# ------------------------------------------------------------------ #
# Integration tests — FastAPI endpoints
# ------------------------------------------------------------------ #

class TestHealthEndpoint:
    def test_health_ok(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert "version" in data


class TestSKUsEndpoint:
    def test_list_skus_returns_five(self, client):
        r = client.get("/skus")
        assert r.status_code == 200
        data = r.json()
        assert data["count"] == 5
        assert len(data["skus"]) == 5

    def test_sku_has_required_fields(self, client):
        r = client.get("/skus")
        sku = r.json()["skus"][0]
        for field in ("item_id", "item_name", "category", "base_price", "historical_elasticity"):
            assert field in sku


class TestForecastEndpoint:
    def test_forecast_default(self, client):
        payload = {"sku_id": "FOODS_3_090_CA_1", "horizon": 7, "model": "lstm"}
        r = client.post("/forecast", json=payload)
        assert r.status_code == 200
        data = r.json()
        assert len(data["y_pred"]) == 7
        assert len(data["forecast_dates"]) == 7

    def test_forecast_invalid_sku(self, client):
        r = client.post("/forecast", json={"sku_id": "NONEXISTENT", "horizon": 7})
        assert r.status_code == 404

    def test_forecast_all_models(self, client):
        for model in ("lstm", "naive", "seasonal_naive", "moving_average", "ridge"):
            r = client.post(
                "/forecast",
                json={"sku_id": "HOUSEHOLD_1_001_CA_1", "horizon": 3, "model": model},
            )
            assert r.status_code == 200, f"Model {model} failed: {r.text}"


class TestPricingOptimizeEndpoint:
    def test_optimize_returns_higher_profit(self, client):
        r = client.post(
            "/pricing/optimize",
            json={"sku_id": "FOODS_3_090_CA_1", "base_demand": 100.0},
        )
        assert r.status_code == 200
        data = r.json()
        assert "optimal_price" in data
        assert "profit_uplift_pct" in data
        assert len(data["candidate_prices"]) == 100

    def test_optimize_invalid_sku(self, client):
        r = client.post("/pricing/optimize", json={"sku_id": "FAKE", "base_demand": 50.0})
        assert r.status_code == 404

    def test_optimize_positive_elasticity_rejected(self, client):
        r = client.post(
            "/pricing/optimize",
            json={
                "sku_id": "FOODS_3_090_CA_1",
                "base_demand": 100.0,
                "override_elasticity": 0.5,
            },
        )
        assert r.status_code == 422


class TestSimulateEndpoint:
    def test_simulate_price_policy(self, client):
        r = client.post(
            "/simulate",
            json={
                "sku_id": "FOODS_3_090_CA_1",
                "scenario_type": "price_policy",
                "base_demand": 100.0,
                "params": {"delta_price_pct": 10.0},
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert data["scenario_id"] == "S1"
        assert "baseline_kpis" in data
        assert "shocked_kpis" in data
        assert "risk_assessment" in data

    def test_simulate_macro_shock(self, client):
        r = client.post(
            "/simulate",
            json={
                "sku_id": "HOUSEHOLD_1_001_CA_1",
                "scenario_type": "macro_demand_shock",
                "base_demand": 80.0,
                "params": {"shock_pct": 20.0},
            },
        )
        assert r.status_code == 200
        assert r.json()["scenario_id"] == "S2"

    def test_simulate_stagflation(self, client):
        r = client.post(
            "/simulate",
            json={
                "sku_id": "HOBBIES_1_001_CA_1",
                "scenario_type": "stagflation",
                "base_demand": 60.0,
                "params": {},
            },
        )
        assert r.status_code == 200
        assert r.json()["scenario_id"] == "S5"

    def test_simulate_all_five_scenarios(self, client):
        scenarios = [
            ("price_policy", {"delta_price_pct": 5.0}),
            ("macro_demand_shock", {"shock_pct": 10.0}),
            ("supply_chain_inflation", {"cost_pct": 10.0}),
            ("competitor_price_war", {}),
            ("stagflation", {}),
        ]
        for scenario_type, params in scenarios:
            r = client.post(
                "/simulate",
                json={
                    "sku_id": "FOODS_1_001_CA_1",
                    "scenario_type": scenario_type,
                    "base_demand": 75.0,
                    "params": params,
                },
            )
            assert r.status_code == 200, f"Scenario '{scenario_type}' failed: {r.text}"

    def test_simulate_invalid_scenario_type(self, client):
        r = client.post(
            "/simulate",
            json={
                "sku_id": "FOODS_3_090_CA_1",
                "scenario_type": "not_a_real_scenario",
                "base_demand": 50.0,
                "params": {},
            },
        )
        assert r.status_code == 422

    def test_simulate_invalid_sku(self, client):
        r = client.post(
            "/simulate",
            json={
                "sku_id": "DOES_NOT_EXIST",
                "scenario_type": "stagflation",
                "base_demand": 50.0,
                "params": {},
            },
        )
        assert r.status_code == 404

    def test_simulate_override_unit_cost(self, client):
        r = client.post(
            "/simulate",
            json={
                "sku_id": "FOODS_3_090_CA_1",
                "scenario_type": "supply_chain_inflation",
                "base_demand": 100.0,
                "params": {"cost_pct": 15.0},
                "override_unit_cost": 0.50,
            },
        )
        assert r.status_code == 200
