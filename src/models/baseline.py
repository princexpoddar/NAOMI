"""Classical Statistical and Machine Learning Baseline Forecasting Models."""

from typing import Any, Optional
import numpy as np
from sklearn.linear_model import Ridge

from src.models.base import BaseForecastModel


class NaiveBenchmarkModel(BaseForecastModel):
    """Naive persistence baseline predicting y_hat_{t+h} = y_t."""

    def __init__(self, lag_idx: int = 0):
        super().__init__(model_name="Naive (Persistence)")
        self.lag_idx = lag_idx

    def fit(self, X_train: Any, y_train: Any, **kwargs) -> "NaiveBenchmarkModel":
        self.is_fitted = True
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Uses lag_1 (column 0) as prediction."""
        if isinstance(X, np.ndarray) and X.ndim == 3:
            # Sequence tensor shape (N, W, F): pick last timestep lag_1
            return X[:, -1, self.lag_idx]
        return X[:, self.lag_idx]


class SeasonalNaiveBenchmarkModel(BaseForecastModel):
    """Seasonal persistence baseline predicting y_hat_{t+h} = y_{t+h-7}."""

    def __init__(self, lag_7_idx: int = 3):
        super().__init__(model_name="Seasonal Naive (7-Day)")
        self.lag_7_idx = lag_7_idx

    def fit(self, X_train: Any, y_train: Any, **kwargs) -> "SeasonalNaiveBenchmarkModel":
        self.is_fitted = True
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Uses lag_7 as prediction."""
        if isinstance(X, np.ndarray) and X.ndim == 3:
            return X[:, -1, self.lag_7_idx]
        return X[:, self.lag_7_idx]


class MovingAverageBenchmarkModel(BaseForecastModel):
    """7-day backward-looking moving average baseline."""

    def __init__(self, roll_mean_7_idx: int = 6):
        super().__init__(model_name="Moving Average (7-Day)")
        self.roll_mean_7_idx = roll_mean_7_idx

    def fit(self, X_train: Any, y_train: Any, **kwargs) -> "MovingAverageBenchmarkModel":
        self.is_fitted = True
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        if isinstance(X, np.ndarray) and X.ndim == 3:
            return X[:, -1, self.roll_mean_7_idx]
        return X[:, self.roll_mean_7_idx]


class RidgeBenchmarkModel(BaseForecastModel):
    """L2-Regularized Linear Regression on engineered tabular features."""

    def __init__(self, alpha: float = 1.0):
        super().__init__(model_name="Ridge Regression")
        self.alpha = alpha
        self.model = Ridge(alpha=alpha)

    def fit(self, X_train: np.ndarray, y_train: np.ndarray, **kwargs) -> "RidgeBenchmarkModel":
        if X_train.ndim == 3:
            # Flatten window features (N, W * F)
            N, W, F = X_train.shape
            X_flat = X_train.reshape(N, W * F)
        else:
            X_flat = X_train

        self.model.fit(X_flat, y_train)
        self.is_fitted = True
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before predict().")
        if X.ndim == 3:
            N, W, F = X.shape
            X_flat = X.reshape(N, W * F)
        else:
            X_flat = X
        preds = self.model.predict(X_flat)
        return np.maximum(0.0, preds)
