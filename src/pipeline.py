"""
Pipeline Builder
Creates the complete ML pipeline with all transformers
"""

from sklearn.pipeline import Pipeline
from hdbscan import HDBSCAN

try:
    from .transformers import (
        SpeedTransformer,
        AccelerationTransformer,
        BearingRateVariationTransformer,
        DistanceToStopsTransformer,
        DistanceToBusesTransformer,
        PcaDBSCANTransformer,
    )
    from .config import load_config
except ImportError:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent))
    from transformers import (
        SpeedTransformer,
        AccelerationTransformer,
        BearingRateVariationTransformer,
        DistanceToStopsTransformer,
        DistanceToBusesTransformer,
        PcaDBSCANTransformer,
    )
    from config import load_config


def build_pipeline(bus_df, bus_stops_df, config=None):
    """
    Build the complete ML pipeline

    Args:
        bus_df: Bus DataFrame (needed for distance calculations)
        bus_stops_df: Bus stops DataFrame (needed for distance calculations)
        config: Configuration dict (if None, loads from config.yaml)

    Returns:
        sklearn Pipeline object
    """
    if config is None:
        config = load_config()

    # Extract parameters
    preprocessing = config["preprocessing"]
    feature_eng = config["feature_engineering"]

    # Get unique bus IDs
    unique_bus_ids = bus_df["bus_id"].unique().tolist()

    print("Building pipeline with components:")
    print(f"  1. SpeedTransformer (limit: {preprocessing['speed_limit_kmh']} km/h)")
    print(f"  2. AccelerationTransformer")
    print(f"  3. BearingRateVariationTransformer")
    print(f"  4. DistanceToStopsTransformer ({len(bus_stops_df)} stops)")
    print(f"  5. DistanceToBusesTransformer ({len(unique_bus_ids)} buses)")
    print(
        f"  6. PcaDBSCANTransformer (PCA={feature_eng['pca_n_components']}, "
        f"HDBSCAN min_cluster_size={feature_eng['hdbscan_min_cluster_size']})"
    )

    # Initialize HDBSCAN with configurable parameters
    hdbscan_params = {
        "min_cluster_size": feature_eng["hdbscan_min_cluster_size"],
        "prediction_data": True,  # Enable prediction on new data
    }

    # Add optional parameters if present in config
    if (
        "hdbscan_min_samples" in feature_eng
        and feature_eng["hdbscan_min_samples"] is not None
    ):
        hdbscan_params["min_samples"] = feature_eng["hdbscan_min_samples"]

    if "hdbscan_cluster_selection_epsilon" in feature_eng:
        hdbscan_params["cluster_selection_epsilon"] = feature_eng[
            "hdbscan_cluster_selection_epsilon"
        ]

    if "hdbscan_cluster_selection_method" in feature_eng:
        hdbscan_params["cluster_selection_method"] = feature_eng[
            "hdbscan_cluster_selection_method"
        ]

    hdbscan_model = HDBSCAN(**hdbscan_params)

    # Create pipeline
    pipeline = Pipeline(
        [
            ("speed", SpeedTransformer(speed_limit_mps=preprocessing["max_speed_mps"])),
            ("acceleration", AccelerationTransformer()),
            ("bearing_rate_variation", BearingRateVariationTransformer()),
            (
                "distance_to_stops",
                DistanceToStopsTransformer(median_coords=bus_stops_df),
            ),
            (
                "distance_to_buses",
                DistanceToBusesTransformer(
                    bus_df=bus_df,
                    bus_ids=unique_bus_ids,
                    tolerance=preprocessing["bus_time_tolerance"],
                ),
            ),
            (
                "pca_dbscan",
                PcaDBSCANTransformer(
                    dbscan=hdbscan_model, n_components=feature_eng["pca_n_components"]
                ),
            ),
        ]
    )

    print("\n[OK] Pipeline created successfully!")
    return pipeline


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("Testing Pipeline Builder")
    print("=" * 60)

    try:
        # Load data first
        print("\nLoading data...")
        try:
            from .data_loader import load_and_preprocess_data
        except ImportError:
            from data_loader import load_and_preprocess_data
        phones, bus, stops = load_and_preprocess_data()

        # Build pipeline
        print("\n" + "=" * 60)
        pipeline = build_pipeline(bus, stops)

        print("\n" + "=" * 60)
        print("Pipeline Steps:")
        print("=" * 60)
        for name, transformer in pipeline.named_steps.items():
            print(f"  {name}: {type(transformer).__name__}")

        print("\n[OK] Pipeline built successfully!")
        print("\nNext: Run pipeline with phones.fit_transform(phones)")

    except Exception as e:
        print(f"\n[ERROR] Error building pipeline: {e}")
        import traceback

        traceback.print_exc()
