"""
Bearing Rate Variation Transformer
Computes changes in direction (bearing) over time
"""

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class BearingRateVariationTransformer(BaseEstimator, TransformerMixin):
    """
    Custom transformer to compute bearing rate variation for each point, grouped by user.
    
    Calculates:
    - Bearing (direction) between consecutive GPS points
    - Bearing rate (change in direction per second)
    - Bearing rate variation (change in bearing rate)
    
    High bearing rate variation indicates erratic movement patterns.
    """
    
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
        Transform method to compute bearing rate variation
        
        Args:
            X: DataFrame with columns: timestamp_utc, lat, lon, user_id
            
        Returns:
            DataFrame with added 'bearing_rate_variation_rad_per_s2_computed' column
        """
        out = X.copy()
        out["bearing_rate_variation_rad_per_s2_computed"] = np.nan

        # Check required columns
        required_cols = {"timestamp_utc", "lat", "lon", "user_id"}
        if not required_cols.issubset(out.columns):
            print(f"Warning: Required columns {required_cols} not present in DataFrame.")
            return out

        def compute_bearing_rate_variation_for_group(group):
            """Compute bearing rate variation for a single user's trajectory"""
            group = group.sort_values(by=['timestamp_utc'], ascending=True).reset_index(drop=True).copy()
            
            if len(group) < 2:
                group["bearing_rate_variation_rad_per_s2_computed"] = np.nan
                return group

            # Convert coordinates to radians
            lat1 = np.radians(group["lat"].shift(1))
            lon1 = np.radians(group["lon"].shift(1))
            lat2 = np.radians(group["lat"])
            lon2 = np.radians(group["lon"])

            delta_lon = lon2 - lon1

            # Calculate bearing using formula
            y = np.sin(delta_lon) * np.cos(lat2)
            x = np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(lat2) * np.cos(delta_lon)

            bearing = np.arctan2(y, x)
            # Normalize bearing to [0, 2π)
            bearing = (bearing + 2 * np.pi) % (2 * np.pi)

            # Calculate bearing change
            bearing_change = np.diff(bearing, prepend=np.nan)

            # Handle wrap-around (e.g., from 359° to 1°)
            bearing_change = np.where(bearing_change > np.pi, bearing_change - 2 * np.pi, bearing_change)
            bearing_change = np.where(bearing_change < -np.pi, bearing_change + 2 * np.pi, bearing_change)

            # Time delta in seconds
            dt = group["timestamp_utc"].diff().dt.total_seconds()

            # Bearing rate (rad/s)
            bearing_rate = np.where(dt > 0, bearing_change / dt, np.nan)

            # Bearing rate variation (rad/s²)
            bearing_rate_variation = np.diff(bearing_rate, prepend=np.nan)

            group["bearing_rate_variation_rad_per_s2_computed"] = bearing_rate_variation
            
            return group

        # Process each user separately
        processed_groups = [
            compute_bearing_rate_variation_for_group(group) 
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
            return np.array(['bearing_rate_variation_rad_per_s2_computed'])
        return np.append(input_features, 'bearing_rate_variation_rad_per_s2_computed')


# Example usage
if __name__ == "__main__":
    # Sample data
    sample_data = pd.DataFrame({
        'user_id': [1, 1, 1, 1],
        'lat': [55.7922, 55.7923, 55.7924, 55.7925],
        'lon': [12.5230, 12.5231, 12.5232, 12.5233],
        'timestamp_utc': pd.to_datetime([
            '2020-01-22 10:00:00',
            '2020-01-22 10:00:10',
            '2020-01-22 10:00:20',
            '2020-01-22 10:00:30'
        ], utc=True)
    })
    
    transformer = BearingRateVariationTransformer()
    result = transformer.fit_transform(sample_data)
    
    print("Computed bearing rate variations:")
    print(result[['user_id', 'bearing_rate_variation_rad_per_s2_computed']])
