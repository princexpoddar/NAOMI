"""Train and Benchmark Forecasting Models on All 5 Curated Walmart M5 SKUs."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import numpy as np

from src.data.pipeline import DataPipeline
from src.data.dataset import build_dataloaders
from src.config import CURATED_SKUS, SEQUENCE_LENGTH, DEFAULT_HORIZON
from src.models.baseline import (
    NaiveBenchmarkModel,
    SeasonalNaiveBenchmarkModel,
    MovingAverageBenchmarkModel,
    RidgeBenchmarkModel
)
from src.models.lstm import PyTorchLSTMModel
from src.models.metrics import evaluate_forecasts, generate_ablation_dataframe


def run_benchmark_for_sku(pipeline: DataPipeline, raw_df: pd.DataFrame, sku_id: str) -> pd.DataFrame:
    """Run full benchmark for a single SKU across all candidate models."""
    df_sku = pipeline.get_sku_dataframe(raw_df, sku_id)
    df_features = pipeline.engineer_features(df_sku)
    train_df, val_df, test_df = pipeline.chronological_split(df_features)
    splits = pipeline.fit_transform_splits(train_df, val_df, test_df)

    loaders = build_dataloaders(splits, sequence_length=SEQUENCE_LENGTH, horizon=1, batch_size=32)

    # Actual test demand in natural units
    # Note: Test set sequence window drops the first W=30 points of test split
    raw_y_test_windowed = splits["raw_y_test"][SEQUENCE_LENGTH:]

    results = []

    # 1. Naive Model
    naive = NaiveBenchmarkModel().fit(splits["X_train"], splits["y_train"])
    pred_naive_scaled = naive.predict(splits["X_test"])[SEQUENCE_LENGTH:]
    pred_naive = pipeline.inverse_transform_target(pred_naive_scaled)
    results.append(evaluate_forecasts(raw_y_test_windowed, pred_naive, model_name="Naive (Persistence)"))

    # 2. Seasonal Naive Model (7-Day)
    s_naive = SeasonalNaiveBenchmarkModel().fit(splits["X_train"], splits["y_train"])
    pred_s_naive_scaled = s_naive.predict(splits["X_test"])[SEQUENCE_LENGTH:]
    pred_s_naive = pipeline.inverse_transform_target(pred_s_naive_scaled)
    results.append(evaluate_forecasts(raw_y_test_windowed, pred_s_naive, model_name="Seasonal Naive (7-Day)"))

    # 3. Moving Average Model (7-Day)
    ma = MovingAverageBenchmarkModel().fit(splits["X_train"], splits["y_train"])
    pred_ma_scaled = ma.predict(splits["X_test"])[SEQUENCE_LENGTH:]
    pred_ma = pipeline.inverse_transform_target(pred_ma_scaled)
    results.append(evaluate_forecasts(raw_y_test_windowed, pred_ma, model_name="Moving Average (7-Day)"))

    # 4. Ridge Regression Model
    ridge = RidgeBenchmarkModel(alpha=10.0).fit(splits["X_train"], splits["y_train"])
    pred_ridge_scaled = ridge.predict(splits["X_test"])[SEQUENCE_LENGTH:]
    pred_ridge = pipeline.inverse_transform_target(pred_ridge_scaled)
    results.append(evaluate_forecasts(raw_y_test_windowed, pred_ridge, model_name="Ridge Regression"))

    # 5. PyTorch LSTM Neural Network
    lstm = PyTorchLSTMModel(input_dim=loaders["n_features"], hidden_dim=64, num_layers=2)
    # Train with early stopping on CPU
    lstm.fit(loaders["train"], loaders["val"], max_epochs=25, lr=1e-3, patience=5, verbose=False)
    pred_lstm_scaled = lstm.predict(loaders["test"]).flatten()
    pred_lstm = pipeline.inverse_transform_target(pred_lstm_scaled)
    results.append(evaluate_forecasts(raw_y_test_windowed, pred_lstm, model_name="PyTorch LSTM (2-Layer)"))

    # Save trained checkpoint
    lstm.save_checkpoint()

    df_ablation = generate_ablation_dataframe(results)
    df_ablation["sku_id"] = sku_id
    return df_ablation


def main():
    print("=" * 80)
    print("NAOMI: BENCHMARKING DEMAND FORECASTING MODELS ACROSS ALL 5 WALMART SKUS")
    print("=" * 80)

    pipeline = DataPipeline()
    raw_df = pipeline.load_data()

    all_sku_results = []

    for sku in CURATED_SKUS:
        sku_id = sku["item_id"]
        category = sku["category"]
        print(f"\nTraining models for: {sku_id} ({category})...")
        df_res = run_benchmark_for_sku(pipeline, raw_df, sku_id)
        all_sku_results.append(df_res)
        print(df_res[["model_name", "mae", "rmse", "mape_pct", "r2_score"]].to_string(index=False))

    combined = pd.concat(all_sku_results, ignore_index=True)
    summary_path = PROJECT_ROOT / "docs" / "ablation_benchmark_results.csv"
    combined.to_csv(summary_path, index=False)
    print("\n" + "=" * 80)
    print(f"Benchmark results successfully written to: {summary_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
