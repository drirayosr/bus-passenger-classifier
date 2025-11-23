"""
Distance to Bus Stops Transformer
Computes distance from each GPS point to predefined bus stops
"""

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

# Handle both direct execution and module import
try:
    from ..utils import haversine_array
except ImportError:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent.parent))
    from utils import haversine_array


class DistanceToStopsTransformer(BaseEstimator, TransformerMixin):
    """
    Custom transformer to compute distance from each point to defined bus stops.

    Creates one feature per bus stop with distance in meters.

    Parameters
    ----------
    median_coords : pd.DataFrame
        DataFrame with columns: ['lat', 'lon', 'label']
        Each row represents a bus stop
    """

    def __init__(self, median_coords: pd.DataFrame):
        """
        Initialize transformer with bus stop locations

        Args:
            median_coords: DataFrame with bus stop coordinates and labels
        """
        self.median_coords = median_coords

    def fit(self, X, y=None):
        """
        Fit method (does nothing, required by sklearn interface)

        Args:
            X: Input DataFrame
            y: Target variable (unused)

        Returns:
            self
        """
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Transform method to compute distances to bus stops

        Args:
            X: DataFrame with columns: lat, lon

        Returns:
            DataFrame with added 'distance_to_{stop_name}' columns
        """
        out = X.copy()

        # Check required columns
        if not {"lat", "lon"}.issubset(out.columns):
            print("Warning: Required 'lat' and 'lon' columns not present in DataFrame.")
            return out

        if self.median_coords is None or self.median_coords.empty:
            print("Warning: median_coords is not provided or is empty.")
            return out

        # Compute distance to each bus stop
        for index, row in self.median_coords.iterrows():
            stop_name = row["label"]
            stop_lat = row["lat"]
            stop_lon = row["lon"]

            # Clean stop name for column name
            distance_col_name = f'distance_to_{stop_name.replace(" ", "_")}'

            # Calculate Haversine distance
            out[distance_col_name] = haversine_array(
                out["lat"], out["lon"], stop_lat, stop_lon
            )

        return out

    def get_feature_names_out(self, input_features=None):
        """
        Get output feature names for transformation

        Returns:
            Array of feature names
        """
        if self.median_coords is None or self.median_coords.empty:
            return np.array([])

        feature_names = [
            f'distance_to_{row["label"].replace(" ", "_")}'
            for _, row in self.median_coords.iterrows()
        ]

        if input_features is None:
            return np.array(feature_names)
        return np.append(input_features, feature_names)


# Example usage
if __name__ == "__main__":
    # Sample bus stops
    bus_stops = pd.DataFrame(
        {
            "lat": [55.7923, 55.7924, 55.7925],
            "lon": [12.5231, 12.5232, 12.5233],
            "label": ["Stop A", "Stop B", "Stop C"],
        }
    )

    # Sample passenger data
    sample_data = pd.DataFrame(
        {
            "user_id": [1, 1, 2],
            "lat": [55.7922, 55.7923, 55.7926],
            "lon": [12.5230, 12.5231, 12.5234],
        }
    )

    transformer = DistanceToStopsTransformer(median_coords=bus_stops)
    result = transformer.fit_transform(sample_data)

    print("Computed distances to stops:")
    distance_cols = [col for col in result.columns if col.startswith("distance_to_")]
    print(result[["user_id"] + distance_cols])
