"""PyTorch Dataset and DataLoader generation for sequential window modeling."""

from typing import Tuple, Dict
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader

from src.config import SEQUENCE_LENGTH, BATCH_SIZE


class TimeSeriesWindowDataset(Dataset):
    """Sliding window dataset converting tabular series into (B, W, F) input tensors."""

    def __init__(
        self,
        X: np.ndarray,
        y: np.ndarray,
        sequence_length: int = SEQUENCE_LENGTH,
        horizon: int = 1
    ):
        """
        Args:
            X: 2D array of scaled features (N, F).
            y: 1D or 2D array of scaled target (N,).
            sequence_length: Lookback window W (default 30 days).
            horizon: Steps ahead to forecast H (default 1 day).
        """
        self.sequence_length = sequence_length
        self.horizon = horizon
        self.X_windows, self.y_targets = self._create_windows(X, y)

    def _create_windows(self, X: np.ndarray, y: np.ndarray) -> Tuple[torch.Tensor, torch.Tensor]:
        X_list, y_list = [], []
        n_samples = len(X)

        for i in range(n_samples - self.sequence_length - self.horizon + 1):
            x_win = X[i : i + self.sequence_length]
            y_tar = y[i + self.sequence_length : i + self.sequence_length + self.horizon]
            X_list.append(x_win)
            y_list.append(y_tar)

        if not X_list:
            raise ValueError(
                f"Insufficient data ({n_samples} points) for sequence_length={self.sequence_length} "
                f"and horizon={self.horizon}."
            )

        X_tensor = torch.tensor(np.array(X_list), dtype=torch.float32)
        y_tensor = torch.tensor(np.array(y_list), dtype=torch.float32)
        return X_tensor, y_tensor

    def __len__(self) -> int:
        return len(self.X_windows)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        return self.X_windows[idx], self.y_targets[idx]


def build_dataloaders(
    data_splits: Dict[str, np.ndarray],
    sequence_length: int = SEQUENCE_LENGTH,
    horizon: int = 1,
    batch_size: int = BATCH_SIZE
) -> Dict[str, DataLoader]:
    """Construct Train, Validation, and Test DataLoaders from scaled arrays."""
    train_dataset = TimeSeriesWindowDataset(
        data_splits["X_train"], data_splits["y_train"],
        sequence_length=sequence_length, horizon=horizon
    )
    val_dataset = TimeSeriesWindowDataset(
        data_splits["X_val"], data_splits["y_val"],
        sequence_length=sequence_length, horizon=horizon
    )
    test_dataset = TimeSeriesWindowDataset(
        data_splits["X_test"], data_splits["y_test"],
        sequence_length=sequence_length, horizon=horizon
    )

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    return {
        "train": train_loader,
        "val": val_loader,
        "test": test_loader,
        "n_features": data_splits["X_train"].shape[1],
        "n_train_samples": len(train_dataset),
        "n_test_samples": len(test_dataset)
    }
