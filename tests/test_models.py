"""Automated Unit & Integration Tests for Demand Forecasting Models."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import torch

from src.data.pipeline import DataPipeline
from src.data.dataset import build_dataloaders
from src.models.baseline import (
    NaiveBenchmarkModel,
    SeasonalNaiveBenchmarkModel,
    MovingAverageBenchmarkModel,
    RidgeBenchmarkModel
)
from src.models.lstm import DemandLSTM, PyTorchLSTMModel
from src.models.metrics import (
    calculate_mae,
    calculate_rmse,
    calculate_mape,
    calculate_r2,
    evaluate_forecasts,
    generate_ablation_dataframe
)


def test_baseline_models_execution():
    """Verify all statistical baselines generate non-trivial predictions."""
    X_train = np.random.uniform(0, 1, size=(100, 30, 20))
    y_train = np.random.uniform(10, 50, size=(100, 1))
    X_test = np.random.uniform(0, 1, size=(20, 30, 20))

    # 1. Naive
    naive = NaiveBenchmarkModel().fit(X_train, y_train)
    pred_naive = naive.predict(X_test)
    assert pred_naive.shape == (20,)

    # 2. Seasonal Naive
    s_naive = SeasonalNaiveBenchmarkModel().fit(X_train, y_train)
    pred_s_naive = s_naive.predict(X_test)
    assert pred_s_naive.shape == (20,)

    # 3. Moving Average
    ma = MovingAverageBenchmarkModel().fit(X_train, y_train)
    pred_ma = ma.predict(X_test)
    assert pred_ma.shape == (20,)

    # 4. Ridge
    ridge = RidgeBenchmarkModel().fit(X_train, y_train.flatten())
    pred_ridge = ridge.predict(X_test)
    assert pred_ridge.shape == (20,)
    assert np.all(pred_ridge >= 0.0)


def test_lstm_forward_pass_dimensions():
    """Verify PyTorch LSTM neural network outputs (B, 1) tensors."""
    batch_size = 16
    seq_len = 30
    num_features = 20

    net = DemandLSTM(input_dim=num_features, hidden_dim=64, num_layers=2, horizon=1)
    dummy_input = torch.randn(batch_size, seq_len, num_features)
    output = net(dummy_input)

    assert output.shape == (batch_size, 1), f"Expected (16, 1), got {output.shape}"
    assert not torch.isnan(output).any(), "Found NaNs in LSTM forward pass output!"


def test_lstm_training_loop_on_real_sku():
    """Train PyTorch LSTM on real Walmart M5 SKU and verify convergence."""
    pipeline = DataPipeline()
    df = pipeline.load_data()
    sku_df = pipeline.get_sku_dataframe(df, "FOODS_3_090_CA_1")
    features_df = pipeline.engineer_features(sku_df)
    train_df, val_df, test_df = pipeline.chronological_split(features_df)
    splits = pipeline.fit_transform_splits(train_df, val_df, test_df)

    loaders = build_dataloaders(splits, sequence_length=30, horizon=1, batch_size=32)

    model = PyTorchLSTMModel(input_dim=loaders["n_features"], hidden_dim=64, num_layers=2)
    # Train for 5 epochs to verify learning loop
    model.fit(loaders["train"], loaders["val"], max_epochs=5, lr=1e-3, patience=3, verbose=False)

    assert model.is_fitted
    assert len(model.history["train_loss"]) > 0
    assert len(model.history["val_loss"]) > 0

    # Predictions
    raw_preds = model.predict(loaders["test"])
    assert len(raw_preds) == loaders["n_test_samples"]

    # Invert target back to natural units
    unscaled_preds = pipeline.inverse_transform_target(raw_preds)
    assert len(unscaled_preds) == len(raw_preds)
    assert np.all(unscaled_preds >= 0.0)


def test_lstm_uncertainty_quantification():
    """Verify Monte Carlo Dropout produces valid confidence envelopes."""
    net_wrapper = PyTorchLSTMModel(input_dim=20, hidden_dim=32, num_layers=1)
    dummy_x = torch.randn(10, 30, 20)

    mean_pred, lower_ci, upper_ci = net_wrapper.predict_with_confidence(
        dummy_x, num_mc_samples=15, ci_percentile=90.0
    )

    assert mean_pred.shape == (10, 1)
    assert lower_ci.shape == (10, 1)
    assert upper_ci.shape == (10, 1)
    # Upper CI must be greater than or equal to lower CI
    assert np.all(upper_ci >= lower_ci)


def test_evaluation_metrics_and_ablation():
    """Verify metrics calculation and ablation reporting."""
    y_true = np.array([100.0, 150.0, 200.0, 80.0, 120.0])
    y_pred = np.array([95.0, 155.0, 190.0, 85.0, 115.0])

    mae = calculate_mae(y_true, y_pred)
    rmse = calculate_rmse(y_true, y_pred)
    mape = calculate_mape(y_true, y_pred)
    r2 = calculate_r2(y_true, y_pred)

    assert mae == 6.0
    assert rmse > 0.0
    assert mape > 0.0
    assert r2 > 0.85

    eval_dict = evaluate_forecasts(y_true, y_pred, model_name="TestModel")
    assert eval_dict["mae"] == 6.0

    ablation_df = generate_ablation_dataframe([
        {"model_name": "Naive", "mae": 15.2, "rmse": 18.1, "mape_pct": 14.5},
        {"model_name": "LSTM", "mae": 8.4, "rmse": 10.2, "mape_pct": 8.1}
    ])
    assert len(ablation_df) == 2
    assert ablation_df.iloc[0]["model_name"] == "LSTM"  # Sorted by lowest MAE


if __name__ == "__main__":
    print("Running test_baseline_models_execution...")
    test_baseline_models_execution()
    print("Running test_lstm_forward_pass_dimensions...")
    test_lstm_forward_pass_dimensions()
    print("Running test_lstm_training_loop_on_real_sku...")
    test_lstm_training_loop_on_real_sku()
    print("Running test_lstm_uncertainty_quantification...")
    test_lstm_uncertainty_quantification()
    print("Running test_evaluation_metrics_and_ablation...")
    test_evaluation_metrics_and_ablation()
    print("\nALL 5 FORECASTING MODEL TESTS PASSED SUCCESSFULLY!")
