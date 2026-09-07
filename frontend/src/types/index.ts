export interface SKUInfo {
  item_id: string;
  item_name: string;
  category: string;
  department: string;
  store_id: string;
  base_price: number;
  historical_elasticity: number;
  description: string;
}

export interface ForecastData {
  sku_id: string;
  horizon: number;
  model_name: string;
  forecast_dates: string[];
  y_pred: number[];
  lower_ci: number[];
  upper_ci: number[];
  mae?: number;
  rmse?: number;
  mape?: number;
}

export interface OptimizationData {
  sku_id: string;
  optimal_price: number;
  optimal_profit: number;
  optimal_revenue: number;
  optimal_demand: number;
  profit_uplift_pct: number;
  price_change_pct: number;
  gross_margin_pct: number;
  breakeven_units: number;
  fixed_costs: number;
  curve_prices: number[];
  curve_profits: number[];
  curve_revenues: number[];
}

export interface FinancialKPIs {
  demand: number;
  revenue: number;
  cogs: number;
  gross_profit: number;
  gross_margin_pct: number;
  breakeven_units: number;
}

export interface SimulationResult {
  scenario_type: string;
  sku_id: string;
  candidate_price: number;
  baseline_kpis: FinancialKPIs;
  shocked_kpis: FinancialKPIs;
  demand_change_pct: number;
  revenue_change_pct: number;
  profit_change_pct: number;
  risk_label: "Positive" | "Stable" | "Moderate Risk" | "High Risk" | "Critical Risk";
  executive_brief: string;
}

export interface SimulationSliders {
  priceDeltaPct: number;      // -30% to +40%
  demandShockPct: number;     // -50% to +30%
  costSurgePct: number;       // 0% to +50%
  competitorDropPct: number;  // 0% to 30%
}

export interface HistoricalPoint {
  date: string;
  actual: number;
}
