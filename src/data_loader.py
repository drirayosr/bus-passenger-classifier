"""
Data Loader Module
Handles loading and preprocessing of bus and passenger data
"""

import warnings

warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Optional
from sklearn.cluster import DBSCAN

try:
    from .utils import to_utc, detect_column, compute_aoi_bounds, apply_aoi
    from .config import load_config
except ImportError:
    from utils import to_utc, detect_column, compute_aoi_bounds, apply_aoi
    from config import load_config


def load_dataset(path: str, role_hint: str) -> pd.DataFrame:
    """
    Load and standardize dataset (bus or passengers)

    Args:
        path: Path to CSV file
        role_hint: Either "phone" or "bus"

    Returns:
        Standardized DataFrame with timestamp_utc, lat, lon, and ID columns
    """
    df = pd.read_csv(path)

    # Standardize timestamp column
    tcol = detect_column(df, ["timestamp_utc", "utc_time"])
    if tcol is None:
        raise ValueError(f"No timestamp column found in {path}")
    df = df.rename(columns={tcol: "timestamp_utc"})
    df["timestamp_utc"] = to_utc(df["timestamp_utc"])

    # Standardize lat/lon columns
    latc = detect_column(df, ["lat", "latitude", "Lat", "Latitude"])
    lonc = detect_column(df, ["lon", "lng", "longitude", "Lon", "Longitude", "Lng"])
    if latc is not None:
        df = df.rename(columns={latc: "lat"})
    if lonc is not None:
        df = df.rename(columns={lonc: "lon"})

    # Add ID and role columns
    if role_hint == "phone":
        uc = detect_column(
            df, ["user_id", "userid", "uid", "device_id", "phone_id", "user", "id"]
        )
        df["user_id"] = df[uc] if uc is not None else "user_0"
        df["role"] = "phone"
    else:
        bc = detect_column(df, ["bus_id", "vehicle_id"])
        df["bus_id"] = df[bc] if bc is not None else "bus_0"
        df["role"] = "bus"

    # Sort by timestamp
    df = df.sort_values("timestamp_utc").reset_index(drop=True)

    return df


def detect_bus_stops(
    bus_df: pd.DataFrame, eps: float = 0.0001, min_samples: int = 5, top_n: int = 3
) -> pd.DataFrame:
    """
    Detect bus stop locations using DBSCAN on door-open events

    Args:
        bus_df: Bus DataFrame with door_state column
        eps: DBSCAN epsilon parameter
        min_samples: DBSCAN min_samples parameter
        top_n: Number of top clusters to return

    Returns:
        DataFrame with columns: lat, lon, label (e.g., 'Stop A', 'Stop B', 'Stop C')
    """
    # Check if door_state column exists
    if "door_state" not in bus_df.columns:
        print("Warning: No door_state column found. Using default stop locations.")
        # Return default stops from config
        config = load_config()
        stops_config = config["feature_engineering"]["bus_stops"]
        stops_data = []
        for key, value in stops_config.items():
            stops_data.append(
                {"lat": value["lat"], "lon": value["lon"], "label": value["label"]}
            )
        return pd.DataFrame(stops_data)

    # Get unique door states (usually: closed, open, etc.)
    door_states = bus_df["door_state"].unique()
    print(f"Found door states: {door_states}")

    # Filter for door-open events (assuming second or third state is "open")
    # Typically: closed=0, open=1 or similar
    door_open_states = [s for s in door_states if s not in ["closed", "Closed", 0]]

    if not door_open_states:
        print("Warning: No open door states detected. Using all non-closed states.")
        door_open_states = door_states[1:] if len(door_states) > 1 else door_states

    door_open_bus = bus_df[bus_df["door_state"].isin(door_open_states)][
        ["lon", "lat"]
    ].copy()

    if len(door_open_bus) == 0:
        print("Warning: No door-open events found. Returning empty stops.")
        return pd.DataFrame(columns=["lat", "lon", "label"])

    # Apply DBSCAN clustering
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    door_open_bus["cluster"] = dbscan.fit_predict(door_open_bus)

    # Count points per cluster and rank
    cluster_counts = door_open_bus["cluster"].value_counts()

    # Get top N clusters (excluding noise cluster -1)
    top_clusters = cluster_counts[cluster_counts.index != -1].head(top_n).index.tolist()

    if len(top_clusters) == 0:
        print("Warning: No valid clusters found. Using default stops.")
        config = load_config()
        stops_config = config["feature_engineering"]["bus_stops"]
        stops_data = []
        for key, value in stops_config.items():
            stops_data.append(
                {"lat": value["lat"], "lon": value["lon"], "label": value["label"]}
            )
        return pd.DataFrame(stops_data)

    # Calculate median coordinates for top clusters
    median_coords = (
        door_open_bus[door_open_bus["cluster"].isin(top_clusters)]
        .groupby("cluster")[["lon", "lat"]]
        .median()
    )

    # Assign labels (Stop A, Stop B, Stop C, etc.)
    labels = ["Stop A", "Stop B", "Stop C", "Stop D", "Stop E"]
    median_coords["label"] = [labels[i] for i in range(len(median_coords))]

    print(f"Detected {len(median_coords)} bus stops:")
    for idx, row in median_coords.iterrows():
        print(f"  {row['label']}: lat={row['lat']:.6f}, lon={row['lon']:.6f}")

    return median_coords.reset_index(drop=True)


def load_and_preprocess_data(
    config: Optional[dict] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Load and preprocess all data

    Args:
        config: Configuration dictionary (if None, loads from config.yaml)

    Returns:
        Tuple of (passengers_df, bus_df, bus_stops_df)
    """
    if config is None:
        config = load_config()

    # Get paths
    passengers_path = config["data"]["passengers_path"]
    bus_path = config["data"]["bus_path"]

    print("Loading datasets...")
    print(f"  Passengers: {passengers_path}")
    print(f"  Bus: {bus_path}")

    # Load data
    phones = load_dataset(passengers_path, "phone")
    bus = load_dataset(bus_path, "bus")

    print(f"\nLoaded:")
    print(f"  Passengers: {phones.shape[0]:,} rows")
    print(f"  Bus: {bus.shape[0]:,} rows")

    # Compute Area of Interest (AOI)
    print("\nComputing Area of Interest...")
    aoi_buffer = config["preprocessing"]["aoi_buffer_m"]
    aoi_bounds = compute_aoi_bounds(bus, phones, buffer_m=aoi_buffer)

    if aoi_bounds:
        print(f"  AOI bounds (lat, lon): {aoi_bounds}")
        phones = apply_aoi(phones, aoi_bounds)
        bus = apply_aoi(bus, aoi_bounds)

        phones_in_aoi = phones["gps_in_aoi"].sum()
        bus_in_aoi = bus["gps_in_aoi"].sum()

        print(
            f"  Passengers in AOI: {phones_in_aoi:,} / {len(phones):,} ({phones_in_aoi/len(phones)*100:.1f}%)"
        )
        print(
            f"  Bus in AOI: {bus_in_aoi:,} / {len(bus):,} ({bus_in_aoi/len(bus)*100:.1f}%)"
        )

        # Filter to AOI
        phones = phones[phones["gps_in_aoi"]].reset_index(drop=True)
        bus = bus[bus["gps_in_aoi"]].reset_index(drop=True)

    # Detect bus stops
    print("\nDetecting bus stops...")
    dbscan_params = config["feature_engineering"]
    bus_stops = detect_bus_stops(
        bus,
        eps=dbscan_params["dbscan_eps"],
        min_samples=dbscan_params["dbscan_min_samples"],
        top_n=3,
    )

    # Remove rows with missing labels (if ground truth available)
    if "labelEnc2" in phones.columns:
        phones_before = len(phones)
        phones = phones[phones["labelEnc2"].notna()].reset_index(drop=True)
        phones_after = len(phones)
        if phones_before != phones_after:
            print(
                f"\nRemoved {phones_before - phones_after:,} rows with missing labels"
            )

    print(f"\nFinal dataset sizes:")
    print(f"  Passengers: {len(phones):,} rows")
    print(f"  Bus: {len(bus):,} rows")
    print(f"  Bus stops: {len(bus_stops)} stops")

    return phones, bus, bus_stops


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("Testing Data Loader")
    print("=" * 60)

    try:
        phones, bus, stops = load_and_preprocess_data()

        print("\n" + "=" * 60)
        print("[OK] Data loaded successfully!")
        print("=" * 60)

        print("\nPassenger data columns:")
        print(phones.columns.tolist())

        print("\nBus data columns:")
        print(bus.columns.tolist())

        print("\nBus stops:")
        print(stops)

    except Exception as e:
        print(f"\n[ERROR] Error loading data: {e}")
        import traceback

        traceback.print_exc()
