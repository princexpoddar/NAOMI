"""Abstract Base Class for Demand Forecasting Models."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import numpy as np


class BaseForecastModel(ABC):
    """Unified interface for all statistical, ML, and deep learning demand forecasters."""

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.is_fitted = False

    @abstractmethod
    def fit(self, X_train: Any, y_train: Any, **kwargs) -> "BaseForecastModel":
        """Train the forecasting model on training data."""
        pass

    @abstractmethod
    def predict(self, X: Any) -> np.ndarray:
        """Generate point forecasts for input features."""
        pass

    def get_metadata(self) -> Dict[str, Any]:
        """Return model metadata and configuration."""
        return {
            "model_name": self.model_name,
            "is_fitted": self.is_fitted
        }
