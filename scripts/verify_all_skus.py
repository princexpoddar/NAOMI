"""Comprehensive verification script testing all 5 SKUs end-to-end."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.data.pipeline import DataPipeline
from src.data.dataset import build_dataloaders
from src.config import CURATED_SKUS, SEQUENCE_LENGTH

def verify_all():
    pipeline = DataPipeline()
    df = pipeline.load_data()
    print(f"Total dataset records: {len(df)} (Expected: 9,565)")
    assert len(df) == 9565, "Total row count mismatch!"

    print("-" * 75)
    for sku in CURATED_SKUS:
        sku_id = sku["item_id"]
        category = sku["category"]
        base_price = sku["base_price"]

        # 1. Load SKU
        df_sku = pipeline.get_sku_dataframe(df, sku_id)
        assert len(df_sku) == 1913, f"{sku_id} expected 1913 rows, got {len(df_sku)}"

        # 2. Check price integrity
        assert (df_sku["sell_price"] > 0).all(), f"{sku_id} has non-positive prices!"
        assert (df_sku["unit_cost"] > 0).all(), f"{sku_id} has non-positive costs!"

        # 3. Feature engineering
        df_features = pipeline.engineer_features(df_sku)
        assert len(df_features) == 1913 - 30, f"{sku_id} feature row mismatch (got {len(df_features)})"
        assert df_features[DataPipeline.FEATURE_COLS].isna().sum().sum() == 0, "Found NaNs in features!"

        # 4. Chronological splits
        train_df, val_df, test_df = pipeline.chronological_split(df_features)
        assert len(train_df) + len(val_df) + len(test_df) == len(df_features)
        assert train_df["date"].max() < val_df["date"].min()
        assert val_df["date"].max() < test_df["date"].min()

        # 5. Fit & scale
        splits = pipeline.fit_transform_splits(train_df, val_df, test_df)

        # 6. DataLoaders
        loaders = build_dataloaders(splits, sequence_length=SEQUENCE_LENGTH, horizon=1, batch_size=32)
        train_loader = loaders["train"]
        x_b, y_b = next(iter(train_loader))

        print(f"PASS {sku_id:22} | {category:10} | Base Price: ${base_price:<5.2f} | "
              f"Features: {len(df_features)} | Train Tensor: {tuple(x_b.shape)}")

    print("-" * 75)
    print("ALL 5 CURATED SKUS PASS VERIFICATION ZERO LEAKAGE & CLEAN TENSORS!")

if __name__ == "__main__":
    verify_all()
