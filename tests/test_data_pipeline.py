"""Unit tests for NAOMI Data Pipeline and Sequential Windowing."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    import pytest
    fixture = pytest.fixture
except ImportError:
    pytest = None
    def fixture(func):
        return func

import numpy as np
import pandas as pd
import torch

from src.config import PRIMARY_DATASET_PATH, CURATED_SKUS, SEQUENCE_LENGTH
from src.data.pipeline import DataPipeline
from src.data.dataset import TimeSeriesWindowDataset, build_dataloaders


@fixture
def pipeline():
    return DataPipeline()


@fixture
def raw_df(pipeline):
    return pipeline.load_data()



def test_primary_dataset_exists_and_valid(raw_df):
    """Verify that the primary curated Walmart dataset exists with all 5 SKUs."""
    assert len(raw_df) == 9565, f"Expected 9,565 rows, got {len(raw_df)}"
    skus_in_data = raw_df["item_id"].unique().tolist()
    assert len(skus_in_data) == 5, f"Expected 5 SKUs, got {len(skus_in_data)}"
    for sku in CURATED_SKUS:
        assert sku["item_id"] in skus_in_data


def test_feature_engineering_dimensions_and_cleanliness(pipeline, raw_df):
    """Verify lag and rolling feature computation without remaining NaNs."""
    first_sku = CURATED_SKUS[0]["item_id"]
    df_sku = pipeline.get_sku_dataframe(raw_df, first_sku)
    df_features = pipeline.engineer_features(df_sku)

    # All feature columns must be present
    for col in DataPipeline.FEATURE_COLS:
        assert col in df_features.columns, f"Missing feature column: {col}"

    # Verify zero NaNs in engineered features
    assert df_features[DataPipeline.FEATURE_COLS].isna().sum().sum() == 0

    # Ensure temporal ordering is preserved
    assert df_features["date"].is_monotonic_increasing


def test_chronological_splits_integrity(pipeline, raw_df):
    """Verify temporal separation across Train (70%), Val (15%), Test (15%)."""
    first_sku = CURATED_SKUS[0]["item_id"]
    df_sku = pipeline.get_sku_dataframe(raw_df, first_sku)
    df_features = pipeline.engineer_features(df_sku)

    train_df, val_df, test_df = pipeline.chronological_split(df_features)

    assert len(train_df) + len(val_df) + len(test_df) == len(df_features)
    assert train_df["date"].max() < val_df["date"].min(), "Train/Val split has temporal overlap!"
    assert val_df["date"].max() < test_df["date"].min(), "Val/Test split has temporal overlap!"


def test_scaling_and_inverse_transformation(pipeline, raw_df):
    """Verify that scaling is fitted on train only and inverse transforms cleanly."""
    first_sku = CURATED_SKUS[0]["item_id"]
    df_sku = pipeline.get_sku_dataframe(raw_df, first_sku)
    df_features = pipeline.engineer_features(df_sku)

    train_df, val_df, test_df = pipeline.chronological_split(df_features)
    splits = pipeline.fit_transform_splits(train_df, val_df, test_df)

    # Scaled values in train must be within [0, 1]
    assert np.all(splits["X_train"] >= -1e-5) and np.all(splits["X_train"] <= 1.0 + 1e-5)
    assert np.all(splits["y_train"] >= -1e-5) and np.all(splits["y_train"] <= 1.0 + 1e-5)

    # Invert target and compare with raw test
    inverted_y = pipeline.inverse_transform_target(splits["y_test"])
    raw_y = splits["raw_y_test"]
    assert np.allclose(inverted_y, raw_y, atol=0.2), "Inverse transform deviates from original target!"


def test_pytorch_sliding_windows_and_dataloaders(pipeline, raw_df):
    """Verify (B, W=30, F) tensor shapes in PyTorch DataLoaders."""
    first_sku = CURATED_SKUS[0]["item_id"]
    df_sku = pipeline.get_sku_dataframe(raw_df, first_sku)
    df_features = pipeline.engineer_features(df_sku)

    train_df, val_df, test_df = pipeline.chronological_split(df_features)
    splits = pipeline.fit_transform_splits(train_df, val_df, test_df)

    loaders = build_dataloaders(splits, sequence_length=SEQUENCE_LENGTH, horizon=1, batch_size=32)

    train_loader = loaders["train"]
    x_batch, y_batch = next(iter(train_loader))

    assert x_batch.shape == (32, SEQUENCE_LENGTH, len(DataPipeline.FEATURE_COLS))
    assert y_batch.shape == (32, 1)
    assert isinstance(x_batch, torch.Tensor)
    assert isinstance(y_batch, torch.Tensor)


if __name__ == "__main__":
    p = DataPipeline()
    df = p.load_data()
    print("Running test_primary_dataset_exists_and_valid...")
    test_primary_dataset_exists_and_valid(df)
    print("Running test_feature_engineering_dimensions_and_cleanliness...")
    test_feature_engineering_dimensions_and_cleanliness(p, df)
    print("Running test_chronological_splits_integrity...")
    test_chronological_splits_integrity(p, df)
    print("Running test_scaling_and_inverse_transformation...")
    test_scaling_and_inverse_transformation(p, df)
    print("Running test_pytorch_sliding_windows_and_dataloaders...")
    test_pytorch_sliding_windows_and_dataloaders(p, df)
    print("\n All 5 Data Pipeline tests passed successfully!")

