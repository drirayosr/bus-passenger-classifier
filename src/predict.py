"""
Inference Script
Load a registered model and make predictions
"""

import warnings

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import pandas as pd
import numpy as np
import argparse
from datetime import datetime
import os
from src.model_registry import ModelRegistry
from src.data_loader import load_and_preprocess_data
from src.config import load_config


def predict_batch(model, passengers_df, output_path=None):
    """
    Make batch predictions

    Args:
        model: Trained sklearn pipeline
        passengers_df: DataFrame with passenger GPS data
        output_path: Path to save predictions (optional)

    Returns:
        DataFrame with predictions
    """
    print(f"\n[*] Making predictions on {len(passengers_df)} records...")

    try:
        # Transform data through pipeline
        result = model.transform(passengers_df)

        print(f"[OK] Predictions complete")
        print(f"    Output records: {len(result)}")
        print(f"    Features: {result.shape[1]}")

        # Extract predictions
        if "pca_dbscan_cluster" in result.columns:
            predictions = result[["pca_dbscan_cluster"]].copy()
            predictions.columns = ["predicted_label"]

            # Add confidence if available
            if "pca_component_1" in result.columns:
                # Use PCA distance as confidence proxy
                pca_cols = [c for c in result.columns if c.startswith("pca_component_")]
                predictions["confidence"] = np.linalg.norm(
                    result[pca_cols].values, axis=1
                )

            # Add original IDs if available
            if "user_id" in passengers_df.columns or "id" in passengers_df.columns:
                id_col = "user_id" if "user_id" in passengers_df.columns else "id"
                # Match by index
                predictions["user_id"] = passengers_df[id_col].iloc[result.index].values

            print(f"\nPrediction Distribution:")
            print(predictions["predicted_label"].value_counts().to_string())

            if output_path:
                predictions.to_csv(output_path, index=False)
                print(f"\n[OK] Predictions saved to: {output_path}")

            return predictions
        else:
            print("[ERROR] No cluster column found in output")
            return result

    except Exception as e:
        print(f"[ERROR] Prediction failed: {e}")
        import traceback

        traceback.print_exc()
        return None


def predict_from_production():
    """Load production model and make predictions"""

    print("=" * 60)
    print("Bus Passenger Classification - Inference")
    print("=" * 60)

    # Load config
    config = load_config()

    # Load model from registry
    registry = ModelRegistry()
    model = registry.load_production_model()

    if model is None:
        print("\n[ERROR] No production model found!")
        print("\nPlease register and promote a model:")
        print("  1. python registry_manager.py register")
        print("  2. python registry_manager.py promote --version 1 --stage Production")
        return

    print("\n[*] Loading data...")
    try:
        passengers_df, bus_df, bus_stops_df = load_and_preprocess_data(config=config)

        print(f"[OK] Loaded {len(passengers_df)} passenger records")

    except Exception as e:
        print(f"[ERROR] Failed to load data: {e}")
        return

    # Make predictions
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"predictions/predictions_{timestamp}.csv"
    os.makedirs("predictions", exist_ok=True)

    predictions = predict_batch(model, passengers_df, output_path)

    if predictions is not None and "predicted_label" in predictions.columns:
        print("\n" + "=" * 60)
        print("Prediction Summary")
        print("=" * 60)
        print(f"Total predictions: {len(predictions)}")
        print(f"\nClass distribution:")
        for label, count in predictions["predicted_label"].value_counts().items():
            pct = count / len(predictions) * 100
            print(f"  Class {label}: {count:,} ({pct:.1f}%)")

        if "confidence" in predictions.columns:
            print(f"\nConfidence statistics:")
            print(f"  Mean: {predictions['confidence'].mean():.4f}")
            print(f"  Std:  {predictions['confidence'].std():.4f}")
            print(f"  Min:  {predictions['confidence'].min():.4f}")
            print(f"  Max:  {predictions['confidence'].max():.4f}")


def main():
    parser = argparse.ArgumentParser(
        description="Make predictions with registered model"
    )

    parser.add_argument("--input", type=str, help="Input CSV file path")
    parser.add_argument("--output", type=str, help="Output CSV file path")
    parser.add_argument(
        "--model-name",
        type=str,
        default="bus-passenger-classifier",
        help="Model name in registry",
    )
    parser.add_argument(
        "--stage",
        type=str,
        default="Production",
        choices=["Staging", "Production", "None"],
        help="Model stage to use",
    )

    args = parser.parse_args()

    if args.input:
        # Custom input
        print(f"[*] Loading data from: {args.input}")
        passengers_df = pd.read_csv(args.input)

        # Load model
        registry = ModelRegistry()
        if args.stage == "Production":
            model = registry.load_production_model(args.model_name)
        else:
            model_version = registry.get_model_info(args.model_name, stage=args.stage)
            if model_version:
                import mlflow.sklearn

                model_uri = f"models:/{args.model_name}/{args.stage}"
                model = mlflow.sklearn.load_model(model_uri)
            else:
                print(f"[ERROR] No model found in {args.stage} stage")
                return

        if model:
            predictions = predict_batch(model, passengers_df, args.output)
    else:
        # Use default data
        predict_from_production()


if __name__ == "__main__":
    main()
