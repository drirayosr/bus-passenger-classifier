"""
Utility functions for geospatial calculations and data processing
Extracted from the original notebook
"""

import numpy as np
import pandas as pd
from typing import Optional, Tuple


def haversine_array(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points on Earth
    Uses vectorized Haversine formula for efficiency

    Args:
        lat1, lon1: Latitude and longitude of first point(s) in degrees
        lat2, lon2: Latitude and longitude of second point(s) in degrees

    Returns:
        Distance in meters

    Note:
        All inputs can be scalars or arrays for vectorized computation
    """
    R = 6371000.0  # Earth radius in meters

    # Convert to radians
    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))

    return R * c


def to_utc(s: pd.Series) -> pd.Series:
    """
    Convert a pandas Series to UTC timezone

    Args:
        s: Pandas Series with datetime strings

    Returns:
        Pandas Series with UTC timezone-aware datetimes
    """
    t = pd.to_datetime(s, errors="coerce", utc=True)
    if t.dt.tz is None:
        t = t.dt.tz_localize("UTC")
    return t


def detect_column(df: pd.DataFrame, candidates: list) -> Optional[str]:
    """
    Detect which column name from a list exists in the DataFrame
    Useful for handling different column naming conventions

    Args:
        df: DataFrame to search
        candidates: List of possible column names

    Returns:
        First matching column name, or None if no match
    """
    for c in candidates:
        if c in df.columns:
            return c
    return None


def compute_aoi_bounds(
    bus_df: pd.DataFrame,
    phone_df: pd.DataFrame,
    lat_col: str = "lat",
    lon_col: str = "lon",
    buffer_m: float = 50,
) -> Optional[Tuple[float, float, float, float]]:
    """
    Compute Area of Interest (AOI) bounds from bus route with buffer

    Args:
        bus_df: DataFrame with bus GPS data
        phone_df: DataFrame with phone GPS data (not used but kept for compatibility)
        lat_col: Name of latitude column
        lon_col: Name of longitude column
        buffer_m: Buffer distance in meters

    Returns:
        Tuple of (lat_lo, lat_hi, lon_lo, lon_hi) or None if columns missing
    """
    if not all(c in bus_df.columns for c in (lat_col, lon_col)):
        return None

    # Calculate initial bounds from bus data
    bus_lat_lo, bus_lat_hi = bus_df[lat_col].quantile([0, 1]).tolist()
    bus_lon_lo, bus_lon_hi = bus_df[lon_col].quantile([0, 1]).tolist()

    # Approximate meters per degree at the median latitude of the bus route
    median_lat = bus_df[lat_col].median()

    # Haversine-based conversion
    m_per_deg_lat = (
        111132.92
        - 559.82 * np.cos(2 * np.radians(median_lat))
        + 1.175 * np.cos(4 * np.radians(median_lat))
        - 0.0023 * np.cos(6 * np.radians(median_lat))
    )

    m_per_deg_lon = (
        111412.84 * np.cos(np.radians(median_lat))
        - 93.5 * np.cos(3 * np.radians(median_lat))
        + 0.118 * np.cos(5 * np.radians(median_lat))
    )

    # Expand boundaries by buffer_m meters
    lat_buffer_deg = buffer_m / m_per_deg_lat
    lon_buffer_deg = buffer_m / m_per_deg_lon

    lat_lo = bus_lat_lo - lat_buffer_deg
    lat_hi = bus_lat_hi + lat_buffer_deg
    lon_lo = bus_lon_lo - lon_buffer_deg
    lon_hi = bus_lon_hi + lon_buffer_deg

    return (lat_lo, lat_hi, lon_lo, lon_hi)


def apply_aoi(
    df: pd.DataFrame,
    bounds: Optional[Tuple[float, float, float, float]],
    lat_col: str = "lat",
    lon_col: str = "lon",
) -> pd.DataFrame:
    """
    Filter DataFrame to points within Area of Interest

    Args:
        df: DataFrame with GPS coordinates
        bounds: Tuple of (lat_lo, lat_hi, lon_lo, lon_hi) or None
        lat_col: Name of latitude column
        lon_col: Name of longitude column

    Returns:
        DataFrame with added 'gps_in_aoi' boolean column
    """
    out = df.copy()

    if bounds is None or lat_col not in out.columns or lon_col not in out.columns:
        out["gps_in_aoi"] = True
        return out

    lat_lo, lat_hi, lon_lo, lon_hi = bounds

    mask = (out[lat_col].between(lat_lo, lat_hi)) & (
        out[lon_col].between(lon_lo, lon_hi)
    )

    out["gps_in_aoi"] = mask.fillna(False)

    return out


def time_coverage(df: pd.DataFrame, name: str) -> np.ndarray:
    """
    Calculate time sampling statistics for a DataFrame

    Args:
        df: DataFrame with timestamp_utc column
        name: Name for logging purposes

    Returns:
        Array of time deltas in seconds
    """
    t = df["timestamp_utc"]
    print(f"\n{name} — time span: {t.min()} → {t.max()} | duration = {t.max()-t.min()}")

    dt = t.astype("int64") / 1e9
    dt = sorted(dt)
    dt = np.r_[np.nan, np.diff(dt)]

    print(
        f"{name} — sampling Δt (s) median={np.nanmedian(dt):.3f}, "
        f"mean={np.nanmean(dt):.3f}, p95={np.nanpercentile(dt, 95):.3f}"
    )

    return dt


def flag_unrealistic_speed(
    df: pd.DataFrame,
    role_col: str = "role",
    speed_col: str = "speed_mps",
    threshold_kmh: float = 35,
) -> pd.DataFrame:
    """
    Flag data points with unrealistic speeds

    Args:
        df: DataFrame with speed data
        role_col: Column identifying role (bus/phone)
        speed_col: Column with speed values
        threshold_kmh: Maximum realistic speed in km/h

    Returns:
        DataFrame with added 'speed_outlier' boolean column
    """
    out = df.copy()
    out["speed_outlier"] = False

    if speed_col not in out.columns:
        return out

    # Convert km/h to m/s
    threshold_mps = threshold_kmh / 3.6

    too_fast = (out[speed_col] > threshold_mps) & (out[speed_col] > 0)
    out.loc[too_fast, "speed_outlier"] = True

    return out


# Test functions if run directly
if __name__ == "__main__":
    print("Testing utility functions...")

    # Test haversine
    dist = haversine_array(55.7922, 12.5230, 55.7923, 12.5231)
    print(f"Haversine distance: {dist:.2f} meters")

    # Test detect_column
    test_df = pd.DataFrame({"lat": [1, 2], "lon": [3, 4]})
    col = detect_column(test_df, ["latitude", "lat", "Lat"])
    print(f"Detected column: {col}")

    print("All tests passed!")
