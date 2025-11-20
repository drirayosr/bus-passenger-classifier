"""
Distance to Buses Transformer
Computes time-aligned distance from phones to buses
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


class DistanceToBusesTransformer(BaseEstimator, TransformerMixin):
    """
    Custom transformer to compute distance from each phone point to specific buses.
    
    Uses pd.merge_asof to find nearest bus location in time.
    
    Parameters
    ----------
    bus_df : pd.DataFrame
        DataFrame with bus GPS data (timestamp_utc, lat, lon, bus_id)
    bus_ids : list
        List of bus IDs to compute distances for
    tolerance : str
        Time tolerance for merge_asof (e.g., '60s', '5min')
    """
    
    def __init__(self, bus_df: pd.DataFrame, bus_ids: list, tolerance: str = '60s'):
        """
        Initialize transformer with bus data
        
        Args:
            bus_df: DataFrame with bus GPS traces
            bus_ids: List of bus IDs to track
            tolerance: Time window for matching phone-bus timestamps
        """
        self.bus_df = bus_df
        self.bus_ids = bus_ids
        self.tolerance = tolerance

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
        Transform method to compute distances to buses
        
        Args:
            X: DataFrame with columns: timestamp_utc, lat, lon
            
        Returns:
            DataFrame with added 'distance_to_bus_{bus_id}' columns
        """
        out = X.copy()

        # Check required columns in phone data
        if not {"timestamp_utc", "lat", "lon"}.issubset(out.columns):
            print("Warning: Required columns not present in phone DataFrame.")
            return out
        
        # Check required columns in bus data
        if not {"timestamp_utc", "lat", "lon", "bus_id"}.issubset(self.bus_df.columns):
            print("Warning: Required columns not present in bus DataFrame.")
            return out

        # Drop rows with null timestamps
        out = out.dropna(subset=['timestamp_utc']).copy()
        out = out.sort_values(by='timestamp_utc').reset_index(drop=True)

        # Process each bus
        for bus_id in self.bus_ids:
            distance_col_name = f'distance_to_bus_{bus_id}'
            out[distance_col_name] = np.nan

            # Filter bus data for this specific bus
            bus_filtered = self.bus_df[self.bus_df['bus_id'] == bus_id].copy()

            if bus_filtered.empty:
                print(f"Warning: No data found for bus ID: {bus_id}")
                continue

            bus_filtered = bus_filtered.dropna(subset=['timestamp_utc']).copy()
            bus_filtered = bus_filtered.sort_values(by='timestamp_utc').reset_index(drop=True)

            # Merge phone data with nearest bus data by timestamp
            merged_df = pd.merge_asof(
                out,
                bus_filtered[['timestamp_utc', 'lat', 'lon']],
                on='timestamp_utc',
                direction='nearest',
                tolerance=pd.Timedelta(self.tolerance),
                suffixes=('', '_bus')
            )

            # Calculate Haversine distance for merged rows
            valid_mask = merged_df['lat_bus'].notna() & merged_df['lon_bus'].notna()
            merged_df.loc[valid_mask, distance_col_name] = haversine_array(
                merged_df.loc[valid_mask, 'lat'],
                merged_df.loc[valid_mask, 'lon'],
                merged_df.loc[valid_mask, 'lat_bus'],
                merged_df.loc[valid_mask, 'lon_bus']
            )

            # Update output with distance column
            out[distance_col_name] = merged_df[distance_col_name]

        return out

    def get_feature_names_out(self, input_features=None):
        """
        Get output feature names for transformation
        
        Returns:
            Array of feature names
        """
        feature_names = [f'distance_to_bus_{bus_id}' for bus_id in self.bus_ids]
        
        if input_features is None:
            return np.array(feature_names)
        return np.append(input_features, feature_names)


# Example usage
if __name__ == "__main__":
    # Sample bus data
    bus_data = pd.DataFrame({
        'bus_id': ['bus1', 'bus1', 'bus2', 'bus2'],
        'lat': [55.7922, 55.7923, 55.7925, 55.7926],
        'lon': [12.5230, 12.5231, 12.5233, 12.5234],
        'timestamp_utc': pd.to_datetime([
            '2020-01-22 10:00:00',
            '2020-01-22 10:00:10',
            '2020-01-22 10:00:05',
            '2020-01-22 10:00:15'
        ], utc=True)
    })
    
    # Sample phone data
    phone_data = pd.DataFrame({
        'user_id': [1, 1],
        'lat': [55.7922, 55.7924],
        'lon': [12.5230, 12.5232],
        'timestamp_utc': pd.to_datetime([
            '2020-01-22 10:00:02',
            '2020-01-22 10:00:12'
        ], utc=True)
    })
    
    transformer = DistanceToBusesTransformer(
        bus_df=bus_data, 
        bus_ids=['bus1', 'bus2'],
        tolerance='60s'
    )
    result = transformer.fit_transform(phone_data)
    
    print("Computed distances to buses:")
    distance_cols = [col for col in result.columns if col.startswith('distance_to_bus')]
    print(result[['user_id', 'timestamp_utc'] + distance_cols])
