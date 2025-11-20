"""
PCA + DBSCAN Transformer
Dimensionality reduction followed by clustering for classification
"""

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer


class PcaDBSCANTransformer(BaseEstimator, TransformerMixin):
    """
    Custom transformer to perform PCA followed by HDBSCAN clustering.
    
    Pipeline:
    1. Impute missing values (median strategy)
    2. Scale features (StandardScaler)
    3. Apply PCA for dimensionality reduction
    4. Apply HDBSCAN for clustering
    5. Map clusters to binary labels (IN=1, OUT=0)
    
    Parameters
    ----------
    dbscan : object
        HDBSCAN or DBSCAN clustering object
    n_components : int
        Number of PCA components (default: 4)
    """
    
    def __init__(self, dbscan, n_components: int = 4):
        """
        Initialize transformer
        
        Args:
            dbscan: Clustering algorithm (HDBSCAN or DBSCAN)
            n_components: Number of PCA components
        """
        self.n_components = n_components
        self.pca = PCA(n_components=n_components)
        self.dbscan = dbscan
        self.scaler = StandardScaler()
        self.imputer = SimpleImputer(strategy='median')
        self.feature_names_ = None  # Store feature names during fit

    def fit(self, X, y=None):
        """
        Fit the PCA and DBSCAN on the data
        
        Args:
            X: Input DataFrame
            y: Target variable (unused)
            
        Returns:
            self
        """
        # Select only numerical columns
        X_numerical = X.select_dtypes(include=np.number)
        
        # Store the column names we're training on
        self.feature_names_ = X_numerical.columns.tolist()
        
        # Handle NaNs before scaling and PCA
        X_imputed = self.imputer.fit_transform(X_numerical)
        
        # Fit scaler, PCA, and DBSCAN
        X_scaled = self.scaler.fit_transform(X_imputed)
        X_pca = self.pca.fit_transform(X_scaled)
        self.dbscan.fit(X_pca)
        
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Transform data and predict cluster labels
        
        Args:
            X: DataFrame with numerical features
            
        Returns:
            DataFrame with added 'pca_dbscan_cluster' column
        """
        out = X.copy()
        
        # Select only numerical columns
        out_numerical = out.select_dtypes(include=np.number)
        
        # Ensure we have the same columns as during fit (if feature_names_ was stored)
        # Backward compatibility: older models don't have feature_names_
        if hasattr(self, 'feature_names_') and self.feature_names_ is not None:
            # Add missing columns with NaN
            for col in self.feature_names_:
                if col not in out_numerical.columns:
                    out_numerical[col] = np.nan
            
            # Select only the columns used during fit, in the same order
            out_numerical = out_numerical[self.feature_names_]
        elif hasattr(self.imputer, 'feature_names_in_'):
            # Use imputer's stored feature names (from old models)
            feature_names = self.imputer.feature_names_in_.tolist()
            # Add missing columns with NaN
            for col in feature_names:
                if col not in out_numerical.columns:
                    out_numerical[col] = np.nan
            # Select only the columns used during fit, in the same order
            out_numerical = out_numerical[feature_names]
        
        # Handle NaNs
        X_imputed = self.imputer.transform(out_numerical)
        
        # Scale and apply PCA
        X_scaled = self.scaler.transform(X_imputed)
        X_pca = self.pca.transform(X_scaled)
        
        # Predict cluster labels
        # Handle single/small-point predictions (HDBSCAN needs sufficient points)
        # For predictions with <10 points, classify all as noise/OUT (label = 0)
        if len(X_pca) < 10:
            # Too few points for meaningful clustering: classify as noise/OUT (label = 0)
            clusters = np.full(len(X_pca), -1)
        else:
            clusters = self.dbscan.fit_predict(X_pca)
        
        # Map clusters to binary labels
        # Noise (-1) → OUT (0)
        # All other clusters → IN (1)
        binary_labels = np.where(clusters != -1, 1, 0)
        
        out['pca_dbscan_cluster'] = binary_labels
        
        return out

    def get_explained_variance_ratio(self):
        """
        Get the explained variance ratio of PCA components
        
        Returns:
            Array of explained variance ratios
        """
        if hasattr(self.pca, 'explained_variance_ratio_'):
            return self.pca.explained_variance_ratio_
        return None

    def get_feature_names_out(self, input_features=None):
        """
        Get output feature names for transformation
        
        Returns:
            Array of feature names
        """
        if input_features is None:
            return np.array(['pca_dbscan_cluster'])
        return np.append(input_features, 'pca_dbscan_cluster')


# Example usage
if __name__ == "__main__":
    from hdbscan import HDBSCAN
    
    # Sample data
    sample_data = pd.DataFrame({
        'user_id': [1, 1, 2, 2, 3, 3],
        'speed': [5.0, 5.2, 0.5, 0.3, 4.8, 5.1],
        'acceleration': [0.1, 0.05, 0.01, -0.01, 0.08, 0.06],
        'distance_to_bus': [2.0, 1.8, 50.0, 52.0, 2.5, 2.2],
        'distance_to_stop': [100.0, 105.0, 5.0, 4.0, 98.0, 102.0]
    })
    
    # Initialize HDBSCAN
    hdbscan_model = HDBSCAN(min_cluster_size=2)
    
    # Apply transformer
    transformer = PcaDBSCANTransformer(dbscan=hdbscan_model, n_components=3)
    result = transformer.fit_transform(sample_data)
    
    print("Cluster assignments:")
    print(result[['user_id', 'pca_dbscan_cluster']])
    print("\nExplained variance ratio:", transformer.get_explained_variance_ratio())
