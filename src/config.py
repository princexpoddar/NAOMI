"""Global Configuration and Constants for NAOMI."""

from pathlib import Path
import os
# Base Directories
SRC_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SRC_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SYNTHETIC_DATA_DIR = DATA_DIR / "synthetic"
MODELS_DIR = PROJECT_ROOT / "models_cache"

# Ensure directories exist
for d in [RAW_DATA_DIR, PROCESSED_DATA_DIR, SYNTHETIC_DATA_DIR, MODELS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Datasets
PRIMARY_DATASET_PATH = RAW_DATA_DIR / "walmart_m5_curated.csv"
SYNTHETIC_DATASET_PATH = SYNTHETIC_DATA_DIR / "synthetic_sales.csv"

# Curated 5 SKUs from Walmart M5
CURATED_SKUS = [
    {
        "item_id": "FOODS_3_090_CA_1",
        "item_name": "Fresh Grocery Item 090",
        "category": "FOODS",
        "department": "FOODS_3",
        "store_id": "CA_1",
        "base_price": 1.25,
        "historical_elasticity": -1.35,
        "description": "High-volume perishable grocery; highly price-elastic"
    },
    {
        "item_id": "FOODS_1_001_CA_1",
        "item_name": "Packaged Staples Item 001",
        "category": "FOODS",
        "department": "FOODS_1",
        "store_id": "CA_1",
        "base_price": 2.24,
        "historical_elasticity": -0.80,
        "description": "Supermarket food staple; steady weekly shopping cycles"
    },
    {
        "item_id": "HOUSEHOLD_1_001_CA_1",
        "item_name": "Cleaning Essentials 001",
        "category": "HOUSEHOLD",
        "department": "HOUSEHOLD_1",
        "store_id": "CA_1",
        "base_price": 5.97,
        "historical_elasticity": -0.42,
        "description": "Household cleaning essential; inelastic demand"
    },
    {
        "item_id": "HOUSEHOLD_2_005_CA_1",
        "item_name": "Home Goods Item 005",
        "category": "HOUSEHOLD",
        "department": "HOUSEHOLD_2",
        "store_id": "CA_1",
        "base_price": 8.94,
        "historical_elasticity": -0.95,
        "description": "Semi-durable home goods; cyclical sensitivity"
    },
    {
        "item_id": "HOBBIES_1_001_CA_1",
        "item_name": "Entertainment / Toy 001",
        "category": "HOBBIES",
        "department": "HOBBIES_1",
        "store_id": "CA_1",
        "base_price": 11.97,
        "historical_elasticity": -1.15,
        "description": "Discretionary hobby goods; seasonal holiday spikes"
    }
]

DEFAULT_ACTIVE_SKU = "FOODS_3_090_CA_1"

# Time Series & Forecasting Parameters
SEQUENCE_LENGTH = 30  # Lookback window (days)
DEFAULT_HORIZON = 7   # 7 days ahead
SUPPORTED_HORIZONS = [1, 7, 30]

# Train / Val / Test Split Ratios (chronological, no shuffle)
TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15

# Deep Learning Hyperparameters (PyTorch LSTM)
LSTM_HIDDEN_DIM = 64
LSTM_NUM_LAYERS = 2
LSTM_DROPOUT = 0.2
LEARNING_RATE = 1e-3
BATCH_SIZE = 32
MAX_EPOCHS = 60
PATIENCE = 10
RANDOM_SEED = 42

# Device (CPU is prioritized for zero-cost reproduction)
try:
    import torch as _torch
    DEVICE = _torch.device("cuda" if _torch.cuda.is_available() else "cpu")
except ImportError:
    # torch not installed — device config unavailable outside ML training
    DEVICE = None  # type: ignore[assignment]

# Financial & Pricing Parameters
DEFAULT_COST_RATIO = 0.60  # Default unit cost = 60% of baseline price (40% gross margin)
DEFAULT_FIXED_COST = 500.0  # Periodic fixed overhead ($)
P_MIN_RATIO = 0.70         # Minimum search price (-30%)
P_MAX_RATIO = 1.40         # Maximum search price (+40%)
PRICE_GRID_POINTS = 100    # Points for profit curve resolution

# Server & Dashboard
DASH_HOST = "127.0.0.1"
DASH_PORT = 8050
API_PORT = 8000
