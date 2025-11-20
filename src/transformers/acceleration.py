"""
Acceleration Transformer
Computes acceleration from speed changes
"""

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class AccelerationTransformer(BaseEstimator, TransformerMixin):
    """
    Custom transformer to compute acceleration for each point, grouped by user.
    
    Calculates acceleration using:
    - Change in speed between consecutive points
    - Time delta between timestamps
    
    Requires 'speed_mps_computed' column from SpeedTransformer
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
        Transform method to compute acceleration
        
        Args:
            X: DataFrame with columns: timestamp_utc, speed_mps_computed, user_id
            
        Returns:
            DataFrame with added 'acceleration_mps2_computed' column
        """
        out = X.copy()
        out["acceleration_mps2_computed"] = np.nan

        # Check required columns
        required_cols = {"timestamp_utc", "speed_mps_computed", "user_id"}
        if not required_cols.issubset(out.columns):
            print(f"Warning: Required columns {required_cols} not present in DataFrame.")
            return out

        def compute_acceleration_for_group(group):
            """Compute acceleration for a single user's trajectory"""
            group = group.sort_values(by=['timestamp_utc'], ascending=True).reset_index(drop=True).copy()
            
            if len(group) < 2:
                group["acceleration_mps2_computed"] = np.nan
                return group

            # Time delta in seconds
            dt = group["timestamp_utc"].diff().dt.total_seconds()
            
            # Speed change
            ds = group["speed_mps_computed"].diff()

            # Acceleration = change in speed / time
            acceleration = np.where(dt > 0, ds / dt, np.nan)
            group["acceleration_mps2_computed"] = acceleration
            
            return group

        # Process each user separately
        processed_groups = [
            compute_acceleration_for_group(group) 
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
            return np.array(['acceleration_mps2_computed'])
        return np.append(input_features, 'acceleration_mps2_computed')


# Example usage
if __name__ == "__main__":
    # Sample data with pre-computed speed
    sample_data = pd.DataFrame({
        'user_id': [1, 1, 1],
        'timestamp_utc': pd.to_datetime([
            '2020-01-22 10:00:00',
            '2020-01-22 10:00:10',
            '2020-01-22 10:00:20'
        ], utc=True),
        'speed_mps_computed': [5.0, 7.0, 6.5]
    })
    
    transformer = AccelerationTransformer()
    result = transformer.fit_transform(sample_data)
    
    print("Computed accelerations:")
    print(result[['user_id', 'speed_mps_computed', 'acceleration_mps2_computed']])
