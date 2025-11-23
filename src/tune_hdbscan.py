"""
Hyperparameter tuning script for HDBSCAN
Tests different configurations to find the best F1 score
"""

import warnings

warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
from sklearn.metrics import f1_score, classification_report
from hdbscan import HDBSCAN
import joblib
from datetime import datetime

try:
    from .data_loader import load_and_preprocess_data
    from .pipeline import build_pipeline
    from .config import load_config
except ImportError:
    from data_loader import load_and_preprocess_data
    from pipeline import build_pipeline
    from config import load_config


def test_hdbscan_config(
    phones,
    bus,
    bus_stops,
    config,
    min_cluster_size,
    min_samples=None,
    cluster_selection_epsilon=0.0,
    cluster_selection_method="eom",
):
    """
    Test a specific HDBSCAN configuration

    Args:
        phones: Passenger dataframe
        bus: Bus dataframe
        bus_stops: Bus stops dataframe
        config: Configuration dict
        min_cluster_size: HDBSCAN min_cluster_size parameter
        min_samples: HDBSCAN min_samples parameter (None = auto)
        cluster_selection_epsilon: HDBSCAN cluster_selection_epsilon parameter
        cluster_selection_method: HDBSCAN cluster_selection_method ('eom' or 'leaf')

    Returns:
        dict with results
    """
    print(f"\n{'='*60}")
    print(
        f"Testing: min_cluster_size={min_cluster_size}, min_samples={min_samples}, "
        f"epsilon={cluster_selection_epsilon}, method={cluster_selection_method}"
    )
    print(f"{'='*60}")

    try:
        # Update config with new HDBSCAN parameters
        config_copy = config.copy()
        config_copy["feature_engineering"][
            "hdbscan_min_cluster_size"
        ] = min_cluster_size
        if min_samples is not None:
            config_copy["feature_engineering"]["hdbscan_min_samples"] = min_samples
        config_copy["feature_engineering"][
            "hdbscan_cluster_selection_epsilon"
        ] = cluster_selection_epsilon
        config_copy["feature_engineering"][
            "hdbscan_cluster_selection_method"
        ] = cluster_selection_method

        # Build and train pipeline
        pipeline = build_pipeline(bus, bus_stops, config_copy)
        X_transformed = pipeline.fit_transform(phones.copy())

        # Get labels
        if "labelEnc2" not in X_transformed.columns:
            print("[ERROR] labelEnc2 not in output")
            return None

        if "pca_dbscan_cluster" not in X_transformed.columns:
            print("[ERROR] pca_dbscan_cluster not in output")
            return None

        y_true = X_transformed["labelEnc2"].values
        y_pred = X_transformed["pca_dbscan_cluster"].values

        # Check cluster distribution
        unique_clusters, counts = np.unique(y_pred, return_counts=True)
        print(f"\nCluster distribution:")
        for cluster, count in zip(unique_clusters, counts):
            print(
                f"  Cluster {cluster}: {count} samples ({count/len(y_pred)*100:.1f}%)"
            )

        # Calculate metrics
        f1 = f1_score(y_true, y_pred, zero_division=0)

        # Class distribution
        n_class_0 = (y_pred == 0).sum()
        n_class_1 = (y_pred == 1).sum()

        print(f"\nPredictions:")
        print(f"  Class 0 (OUT): {n_class_0} ({n_class_0/len(y_pred)*100:.1f}%)")
        print(f"  Class 1 (IN): {n_class_1} ({n_class_1/len(y_pred)*100:.1f}%)")
        print(f"\nF1 Score: {f1:.4f}")

        result = {
            "min_cluster_size": min_cluster_size,
            "min_samples": min_samples,
            "cluster_selection_epsilon": cluster_selection_epsilon,
            "cluster_selection_method": cluster_selection_method,
            "f1_score": float(f1),
            "n_samples": len(y_true),
            "n_clusters": len(unique_clusters),
            "cluster_distribution": dict(
                zip(unique_clusters.tolist(), counts.tolist())
            ),
            "pred_class_0": int(n_class_0),
            "pred_class_1": int(n_class_1),
        }

        return result

    except Exception as e:
        print(f"[ERROR] Failed: {e}")
        import traceback

        traceback.print_exc()
        return None


def tune_hdbscan():
    """Run hyperparameter tuning for HDBSCAN"""

    print("=" * 60)
    print("HDBSCAN Hyperparameter Tuning")
    print("=" * 60)

    # Load data
    print("\n1. Loading data...")
    config = load_config()
    phones, bus, bus_stops = load_and_preprocess_data()

    print(f"\nData loaded: {len(phones):,} passengers")

    # Define parameter grid
    param_grid = [
        # Original settings
        {
            "min_cluster_size": 1000,
            "min_samples": None,
            "epsilon": 0.0,
            "method": "eom",
        },
        # Try smaller min_cluster_size
        {"min_cluster_size": 500, "min_samples": None, "epsilon": 0.0, "method": "eom"},
        {"min_cluster_size": 300, "min_samples": None, "epsilon": 0.0, "method": "eom"},
        {"min_cluster_size": 200, "min_samples": None, "epsilon": 0.0, "method": "eom"},
        # Try with min_samples
        {"min_cluster_size": 500, "min_samples": 10, "epsilon": 0.0, "method": "eom"},
        {"min_cluster_size": 300, "min_samples": 10, "epsilon": 0.0, "method": "eom"},
        # Try with epsilon (allows smaller clusters near large clusters)
        {"min_cluster_size": 500, "min_samples": None, "epsilon": 0.5, "method": "eom"},
        {"min_cluster_size": 300, "min_samples": None, "epsilon": 0.5, "method": "eom"},
        # Try leaf method
        {
            "min_cluster_size": 500,
            "min_samples": None,
            "epsilon": 0.0,
            "method": "leaf",
        },
        {
            "min_cluster_size": 300,
            "min_samples": None,
            "epsilon": 0.0,
            "method": "leaf",
        },
    ]

    # Test each configuration
    results = []
    for i, params in enumerate(param_grid, 1):
        print(f"\n\n{'#'*60}")
        print(f"Configuration {i}/{len(param_grid)}")
        print(f"{'#'*60}")

        result = test_hdbscan_config(
            phones,
            bus,
            bus_stops,
            config,
            min_cluster_size=params["min_cluster_size"],
            min_samples=params["min_samples"],
            cluster_selection_epsilon=params["epsilon"],
            cluster_selection_method=params["method"],
        )

        if result:
            results.append(result)

    # Sort by F1 score
    results.sort(key=lambda x: x["f1_score"], reverse=True)

    # Print summary
    print("\n\n" + "=" * 60)
    print("TUNING RESULTS SUMMARY")
    print("=" * 60)
    print(
        f"\n{'Rank':<6}{'F1 Score':<12}{'min_size':<12}{'min_samp':<12}{'epsilon':<12}{'method':<10}"
    )
    print("-" * 60)

    for i, result in enumerate(results, 1):
        print(
            f"{i:<6}{result['f1_score']:<12.4f}{result['min_cluster_size']:<12}"
            f"{str(result['min_samples']):<12}{result['cluster_selection_epsilon']:<12.1f}"
            f"{result['cluster_selection_method']:<10}"
        )

    # Save results
    print("\n\nSaving results...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_path = f"models/hdbscan_tuning_{timestamp}.joblib"
    joblib.dump(results, results_path)
    print(f"[OK] Results saved to: {results_path}")

    # Show best configuration
    if results:
        best = results[0]
        print("\n" + "=" * 60)
        print("BEST CONFIGURATION")
        print("=" * 60)
        print(f"F1 Score: {best['f1_score']:.4f}")
        print(f"min_cluster_size: {best['min_cluster_size']}")
        print(f"min_samples: {best['min_samples']}")
        print(f"cluster_selection_epsilon: {best['cluster_selection_epsilon']}")
        print(f"cluster_selection_method: {best['cluster_selection_method']}")
        print(f"Number of clusters: {best['n_clusters']}")
        print(
            f"Predictions - Class 0: {best['pred_class_0']}, Class 1: {best['pred_class_1']}"
        )
        print("\nUpdate your config.yaml with these values!")

    return results


if __name__ == "__main__":
    tune_hdbscan()
