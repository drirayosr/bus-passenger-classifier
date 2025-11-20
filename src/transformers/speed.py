"""
Speed Transformer
Computes speed between consecutive GPS points for each user
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


class SpeedTransformer(BaseEstimator, TransformerMixin):
    """
    Custom transformer to compute speed for each point, grouped by user.
    
    Calculates speed using:
    - Haversine distance between consecutive GPS points
    - Time delta between timestamps
    - Filters points exceeding speed limit
    
    Parameters
    ----------
    speed_limit_mps : float
        Maximum allowed speed in meters per second
        Points exceeding this speed are filtered out as outliers
        
    Attributes
    ----------
    speed_limit_mps : float
        The speed limit threshold
    """
    
    def __init__(self, speed_limit_mps: float = 9.72) -> None:
        """
        Initialize SpeedTransformer
        
        Args:
            speed_limit_mps: Maximum speed in m/s (default: 35 km/h = 9.72 m/s)
        """
        self.speed_limit_mps = speed_limit_mps

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
        Transform method to compute speed
        
        Args:
            X: DataFrame with columns: timestamp_utc, lat, lon, user_id
            
        Returns:
            DataFrame with added 'speed_mps_computed' column
            Rows with speed > speed_limit are removed
        """
        out = X.copy()
        out["speed_mps_computed"] = np.nan

        # Check required columns
        required_cols = {"timestamp_utc", "lat", "lon", "user_id"}
        if not required_cols.issubset(out.columns):
            print(f"Warning: Required columns {required_cols} not present in DataFrame.")
            return out

        def compute_speed_for_group(group):
            """Compute speed for a single user's trajectory"""
            group = group.sort_values(by=['timestamp_utc'], ascending=True).reset_index(drop=True).copy()
            
            if len(group) < 2:
                group["speed_mps_computed"] = np.nan
                return group

            # Time delta in seconds
            dt = group["timestamp_utc"].diff().dt.total_seconds()
            
            # Distance between consecutive points
            dist = haversine_array(
                group["lat"].shift(1), 
                group["lon"].shift(1), 
                group["lat"], 
                group["lon"]
            )

            # Speed = distance / time
            speed = np.where(dt > 0, dist / dt, np.nan)
            group["speed_mps_computed"] = speed
            
            # Filter outliers based on speed limit
            return group[group["speed_mps_computed"] < self.speed_limit_mps]

        # Process each user separately
        processed_groups = [
            compute_speed_for_group(group) 
            for _, group in out.groupby('user_id')
        ]
        
        result = pd.concat(processed_groups, axis=0).reset_index(drop=True)
        
        return result

    def get_feature_names_out(self, input_features=None):
        """
        Get output feature names for transformation
        
        Returns:
            Array of feature names
        """
        if input_features is None:
            return np.array(['speed_mps_computed'])
        return np.append(input_features, 'speed_mps_computed')


# Example usage and testing
if __name__ == "__main__":
    # Create sample data
    sample_data = pd.DataFrame({
        'user_id': [1, 1, 1, 2, 2],
        'lat': [55.7922, 55.7923, 55.7924, 55.7925, 55.7926],
        'lon': [12.5230, 12.5231, 12.5232, 12.5233, 12.5234],
        'timestamp_utc': pd.to_datetime([
            '2020-01-22 10:00:00',
            '2020-01-22 10:00:10',
            '2020-01-22 10:00:20',
            '2020-01-22 10:00:00',
            '2020-01-22 10:00:10'
        ], utc=True)
    })
    
    # Test transformer
    transformer = SpeedTransformer(speed_limit_mps=20.0)
    result = transformer.fit_transform(sample_data)
    
    print("Original shape:", sample_data.shape)
    print("Transformed shape:", result.shape)
    print("\nComputed speeds:")
    print(result[['user_id', 'speed_mps_computed']])
