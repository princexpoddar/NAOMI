"""Forecasting Evaluation Metrics and Model Ablation Reporting."""

from typing import Dict, List, Any
import numpy as np
import pandas as pd


def calculate_mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Mean Absolute Error."""
    return float(np.mean(np.abs(y_true - y_pred)))


def calculate_rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Root Mean Squared Error."""
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def calculate_mape(y_true: np.ndarray, y_pred: np.ndarray, epsilon: float = 1.0) -> float:
    """Mean Absolute Percentage Error with epsilon smoothing to prevent zero-division."""
    denom = np.abs(y_true) + epsilon
    return float(np.mean(np.abs(y_true - y_pred) / denom) * 100.0)


def calculate_r2(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Coefficient of Determination (R^2)."""
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2) + 1e-8
    return float(1.0 - (ss_res / ss_tot))


def evaluate_forecasts(y_true: np.ndarray, y_pred: np.ndarray, model_name: str = "Model") -> Dict[str, Any]:
    """Compute standard suite of quantitative forecasting evaluation metrics."""
    y_true_flat = np.array(y_true).flatten()
    y_pred_flat = np.array(y_pred).flatten()

    mae = calculate_mae(y_true_flat, y_pred_flat)
    rmse = calculate_rmse(y_true_flat, y_pred_flat)
    mape = calculate_mape(y_true_flat, y_pred_flat)
    r2 = calculate_r2(y_true_flat, y_pred_flat)

    return {
        "model_name": model_name,
        "mae": round(mae, 2),
        "rmse": round(rmse, 2),
        "mape_pct": round(mape, 2),
        "r2_score": round(r2, 4)
    }


def generate_ablation_dataframe(eval_results: List[Dict[str, Any]]) -> pd.DataFrame:
    """Generate a clean pandas DataFrame summarizing model ablation benchmarks."""
    df = pd.DataFrame(eval_results)
    if not df.empty and "mae" in df.columns:
        # Sort by best (lowest) MAE
        df = df.sort_values(by="mae").reset_index(drop=True)
    return df
