"""PyTorch LSTM Neural Network Architecture and Training Engine for Demand Forecasting."""

from typing import Tuple, List, Dict, Optional, Any
from pathlib import Path
import copy
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from src.models.base import BaseForecastModel
from src.config import (
    LSTM_HIDDEN_DIM,
    LSTM_NUM_LAYERS,
    LSTM_DROPOUT,
    LEARNING_RATE,
    MAX_EPOCHS,
    PATIENCE,
    DEVICE,
    MODELS_DIR
)


class DemandLSTM(nn.Module):
    """Stacked 2-Layer LSTM with fully connected projection head."""

    def __init__(
        self,
        input_dim: int,
        hidden_dim: int = LSTM_HIDDEN_DIM,
        num_layers: int = LSTM_NUM_LAYERS,
        dropout: float = LSTM_DROPOUT,
        horizon: int = 1
    ):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.horizon = horizon

        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0
        )

        self.fc_projection = nn.Sequential(
            nn.Linear(hidden_dim, 32),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(32, horizon)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass through recurrent network.
        
        Args:
            x: Tensor of shape (Batch, Seq_Len, Features)
        Returns:
            Tensor of shape (Batch, Horizon)
        """
        lstm_out, (hn, cn) = self.lstm(x)
        # Use last hidden state: hn[-1] of shape (Batch, hidden_dim)
        last_hidden = hn[-1]
        out = self.fc_projection(last_hidden)
        return out


class PyTorchLSTMModel(BaseForecastModel):
    """Wrapper implementing BaseForecastModel contract with early stopping and uncertainty."""

    def __init__(
        self,
        input_dim: int,
        hidden_dim: int = LSTM_HIDDEN_DIM,
        num_layers: int = LSTM_NUM_LAYERS,
        dropout: float = LSTM_DROPOUT,
        horizon: int = 1,
        device: torch.device = DEVICE
    ):
        super().__init__(model_name="PyTorch LSTM")
        self.device = device
        self.horizon = horizon
        self.network = DemandLSTM(
            input_dim=input_dim,
            hidden_dim=hidden_dim,
            num_layers=num_layers,
            dropout=dropout,
            horizon=horizon
        ).to(self.device)
        self.best_weights = None
        self.history: Dict[str, List[float]] = {"train_loss": [], "val_loss": []}

    def fit(
        self,
        train_loader: DataLoader,
        val_loader: DataLoader,
        max_epochs: int = MAX_EPOCHS,
        lr: float = LEARNING_RATE,
        patience: int = PATIENCE,
        verbose: bool = False
    ) -> "PyTorchLSTMModel":
        """Train model with Huber (Smooth L1) loss, Adam, and Early Stopping."""
        criterion = nn.SmoothL1Loss(beta=1.0)
        optimizer = torch.optim.Adam(self.network.parameters(), lr=lr, weight_decay=1e-5)
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode="min", factor=0.5, patience=4
        )

        best_val_loss = float("inf")
        epochs_without_improvement = 0

        for epoch in range(1, max_epochs + 1):
            # Training epoch
            self.network.train()
            train_losses = []
            for X_b, y_b in train_loader:
                X_b = X_b.to(self.device)
                y_b = y_b.to(self.device)

                optimizer.zero_grad()
                pred = self.network(X_b)
                loss = criterion(pred, y_b)
                loss.backward()
                # Gradient clipping to prevent exploding gradients
                torch.nn.utils.clip_grad_norm_(self.network.parameters(), max_norm=1.0)
                optimizer.step()
                train_losses.append(loss.item())

            avg_train_loss = float(np.mean(train_losses))

            # Validation epoch
            self.network.eval()
            val_losses = []
            with torch.no_grad():
                for X_b, y_b in val_loader:
                    X_b = X_b.to(self.device)
                    y_b = y_b.to(self.device)
                    pred = self.network(X_b)
                    loss = criterion(pred, y_b)
                    val_losses.append(loss.item())

            avg_val_loss = float(np.mean(val_losses))
            scheduler.step(avg_val_loss)

            self.history["train_loss"].append(avg_train_loss)
            self.history["val_loss"].append(avg_val_loss)

            if verbose and (epoch % 10 == 0 or epoch == 1):
                print(f"Epoch {epoch:2d}/{max_epochs} | Train Loss: {avg_train_loss:.5f} | Val Loss: {avg_val_loss:.5f}")

            # Early stopping check
            if avg_val_loss < best_val_loss:
                best_val_loss = avg_val_loss
                epochs_without_improvement = 0
                self.best_weights = copy.deepcopy(self.network.state_dict())
            else:
                epochs_without_improvement += 1
                if epochs_without_improvement >= patience:
                    if verbose:
                        print(f"Early stopping triggered at epoch {epoch}. Best Val Loss: {best_val_loss:.5f}")
                    break

        # Restore best weights
        if self.best_weights is not None:
            self.network.load_state_dict(self.best_weights)

        self.is_fitted = True
        return self

    def predict(self, X: Any) -> np.ndarray:
        """Generate point predictions for input tensor or DataLoader."""
        self.network.eval()
        preds = []

        if isinstance(X, DataLoader):
            with torch.no_grad():
                for X_b, _ in X:
                    X_b = X_b.to(self.device)
                    out = self.network(X_b)
                    preds.append(out.cpu().numpy())
            return np.concatenate(preds, axis=0)
        else:
            if not isinstance(X, torch.Tensor):
                X = torch.tensor(X, dtype=torch.float32)
            X = X.to(self.device)
            with torch.no_grad():
                out = self.network(X)
            return out.cpu().numpy()

    def predict_with_confidence(
        self,
        X: Any,
        num_mc_samples: int = 25,
        ci_percentile: float = 90.0
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Monte Carlo Dropout inference estimating point forecast and confidence bands."""
        self.network.train()  # Enable dropout layers for stochastic sampling
        mc_preds = []

        # Convert to tensor if needed
        if isinstance(X, DataLoader):
            X_all = torch.cat([x for x, _ in X], dim=0)
        elif not isinstance(X, torch.Tensor):
            X_all = torch.tensor(X, dtype=torch.float32)
        else:
            X_all = X

        X_all = X_all.to(self.device)

        with torch.no_grad():
            for _ in range(num_mc_samples):
                out = self.network(X_all)
                mc_preds.append(out.cpu().numpy())

        # Shape: (num_samples, N, Horizon)
        mc_array = np.array(mc_preds)
        mean_pred = np.mean(mc_array, axis=0)
        
        alpha = (100.0 - ci_percentile) / 2.0
        lower_ci = np.percentile(mc_array, alpha, axis=0)
        upper_ci = np.percentile(mc_array, 100.0 - alpha, axis=0)

        return mean_pred, lower_ci, upper_ci

    def save_checkpoint(self, filepath: Optional[Path] = None) -> Path:
        """Save model state to disk."""
        path = filepath or (MODELS_DIR / f"{self.model_name.replace(' ', '_').lower()}.pt")
        path.parent.mkdir(parents=True, exist_ok=True)
        torch.save({
            "state_dict": self.network.state_dict(),
            "history": self.history,
            "input_dim": self.network.input_dim,
            "horizon": self.horizon
        }, path)
        return path
