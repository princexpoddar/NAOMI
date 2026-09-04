"""Data Pipeline & Feature Engineering Engine for NAOMI."""

from typing import List, Tuple, Dict, Optional, Any
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from src.config import (
    PRIMARY_DATASET_PATH,
    TRAIN_RATIO,
    VAL_RATIO,
    TEST_RATIO,
)


class DataPipeline:
    """End-to-end data ingestion, lag feature creation, and leakage-free scaling."""

    FEATURE_COLS = [
        # Lagged target demand
        "lag_1", "lag_2", "lag_3", "lag_7", "lag_14", "lag_28",
        # Rolling statistics (strictly backward-looking)
        "roll_mean_7", "roll_std_7", "roll_mean_30",
        # Pricing features
        "sell_price", "competitor_price", "price_ratio", "price_momentum_7",
        # Calendar & Event features
        "sin_dow", "cos_dow", "sin_month", "cos_month", "is_weekend",
        "has_event", "snap_flag"
    ]
    TARGET_COL = "units_sold"

    def __init__(self, dataset_path: Optional[str] = None):
        self.dataset_path = dataset_path or PRIMARY_DATASET_PATH
        self.feature_scaler = MinMaxScaler(feature_range=(0, 1))
        self.target_scaler = MinMaxScaler(feature_range=(0, 1))
        self.is_fitted = False

    def load_data(self) -> pd.DataFrame:
        """Load the raw dataset from disk."""
        df = pd.read_csv(self.dataset_path)
        df["date"] = pd.to_datetime(df["date"])
        return df.sort_values(by=["item_id", "date"]).reset_index(drop=True)

    def get_sku_dataframe(self, df: pd.DataFrame, sku_id: str) -> pd.DataFrame:
        """Filter data for a single SKU and sort chronologically."""
        df_sku = df[df["item_id"] == sku_id].copy()
        if df_sku.empty:
            raise ValueError(f"SKU ID '{sku_id}' not found in dataset.")
        return df_sku.sort_values(by="date").reset_index(drop=True)

    def engineer_features(self, df_sku: pd.DataFrame) -> pd.DataFrame:
        """Compute backward-looking lag, rolling, cyclical, and pricing features.
        
        Zero lookahead bias is guaranteed by shifting target values before computing
        rolling windows.
        """
        df = df_sku.copy().sort_values(by="date").reset_index(drop=True)

        # Lags (strictly prior days)
        df["lag_1"] = df[self.TARGET_COL].shift(1)
        df["lag_2"] = df[self.TARGET_COL].shift(2)
        df["lag_3"] = df[self.TARGET_COL].shift(3)
        df["lag_7"] = df[self.TARGET_COL].shift(7)
        df["lag_14"] = df[self.TARGET_COL].shift(14)
        df["lag_28"] = df[self.TARGET_COL].shift(28)

        # Rolling Statistics (shift(1) prevents lookahead leakage)
        df["roll_mean_7"] = df[self.TARGET_COL].shift(1).rolling(window=7).mean()
        df["roll_std_7"] = df[self.TARGET_COL].shift(1).rolling(window=7).std().fillna(0.0)
        df["roll_mean_30"] = df[self.TARGET_COL].shift(1).rolling(window=30).mean()

        # Pricing features
        df["price_ratio"] = df["sell_price"] / (df["competitor_price"] + 1e-6)
        df["price_momentum_7"] = (df["sell_price"] - df["sell_price"].shift(7)) / (df["sell_price"].shift(7) + 1e-6)

        # Calendar Cyclical Encodings
        dow = df["date"].dt.dayofweek
        month = df["date"].dt.month
        df["sin_dow"] = np.sin(2 * np.pi * dow / 7.0)
        df["cos_dow"] = np.cos(2 * np.pi * dow / 7.0)
        df["sin_month"] = np.sin(2 * np.pi * month / 12.0)
        df["cos_month"] = np.cos(2 * np.pi * month / 12.0)
        df["is_weekend"] = dow.isin([5, 6]).astype(int)

        # Event features
        df["has_event"] = (df["event_name"].astype(str).str.lower() != "none").astype(int)
        df["snap_flag"] = df["snap_flag"].fillna(0).astype(int)

        # Drop initial rows with NaNs resulting from 30-day lookback (only check feature cols)
        df_clean = df.dropna(subset=self.FEATURE_COLS).reset_index(drop=True)
        return df_clean

    def chronological_split(
        self, df_features: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Split into Train (70%), Val (15%), Test (15%) preserving temporal order."""
        n = len(df_features)
        n_train = int(n * TRAIN_RATIO)
        n_val = int(n * VAL_RATIO)

        train_df = df_features.iloc[:n_train].copy().reset_index(drop=True)
        val_df = df_features.iloc[n_train : n_train + n_val].copy().reset_index(drop=True)
        test_df = df_features.iloc[n_train + n_val :].copy().reset_index(drop=True)

        return train_df, val_df, test_df

    def fit_transform_splits(
        self, train_df: pd.DataFrame, val_df: pd.DataFrame, test_df: pd.DataFrame
    ) -> Dict[str, np.ndarray]:
        """Fit scalers exclusively on the training split and transform all splits."""
        # Fit on train strictly
        self.feature_scaler.fit(train_df[self.FEATURE_COLS].values)
        self.target_scaler.fit(train_df[[self.TARGET_COL]].values)
        self.is_fitted = True

        X_train = self.feature_scaler.transform(train_df[self.FEATURE_COLS].values)
        y_train = self.target_scaler.transform(train_df[[self.TARGET_COL]].values).flatten()

        X_val = self.feature_scaler.transform(val_df[self.FEATURE_COLS].values)
        y_val = self.target_scaler.transform(val_df[[self.TARGET_COL]].values).flatten()

        X_test = self.feature_scaler.transform(test_df[self.FEATURE_COLS].values)
        y_test = self.target_scaler.transform(test_df[[self.TARGET_COL]].values).flatten()

        return {
            "X_train": X_train, "y_train": y_train,
            "X_val": X_val, "y_val": y_val,
            "X_test": X_test, "y_test": y_test,
            "dates_train": train_df["date"].values,
            "dates_val": val_df["date"].values,
            "dates_test": test_df["date"].values,
            "raw_y_test": test_df[self.TARGET_COL].values,
            "raw_prices_test": test_df["sell_price"].values,
        }

    def inverse_transform_target(self, scaled_y: np.ndarray) -> np.ndarray:
        """Invert normalized target back to original units sold."""
        if not self.is_fitted:
            raise RuntimeError("Pipeline must be fitted before inverse transform.")
        scaled_2d = scaled_y.reshape(-1, 1)
        inverted = self.target_scaler.inverse_transform(scaled_2d).flatten()
        return np.maximum(0.0, np.round(inverted, 1))
