"""
Training script for bus passenger classification
Executes the complete pipeline and evaluates model performance
"""

import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)

import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix, f1_score
import joblib
import os
from datetime import datetime

try:
    from .data_loader import load_and_preprocess_data
    from .pipeline import build_pipeline
    from .config import load_config
except ImportError:
    from data_loader import load_and_preprocess_data
    from pipeline import build_pipeline
    from config import load_config


def train_and_evaluate():
    """Train the pipeline and evaluate performance"""
    
    print("=" * 60)
    print("Training Bus Passenger Classification Model")
    print("=" * 60)
    
    # Load configuration
    config = load_config()
    
    # Load and preprocess data
    print("\n1. Loading data...")
    phones, bus, bus_stops = load_and_preprocess_data()
    
    print(f"\nData loaded:")
    print(f"  Passengers: {len(phones):,} rows")
    print(f"  Bus: {len(bus):,} rows")
    print(f"  Bus stops: {len(bus_stops)} stops")
    
    # Check if we have labels
    if 'labelEnc2' not in phones.columns:
        print("\n[ERROR] No 'labelEnc2' column found in dataset!")
        return
    
    # Store ground truth labels (keep them in the dataframe for now)
    print(f"\nGround truth distribution (before pipeline):")
    print(f"  Class 0 (OUT): {(phones['labelEnc2'] == 0).sum():,} ({(phones['labelEnc2'] == 0).sum() / len(phones) * 100:.1f}%)")
    print(f"  Class 1 (IN): {(phones['labelEnc2'] == 1).sum():,} ({(phones['labelEnc2'] == 1).sum() / len(phones) * 100:.1f}%)")
    
    # Build pipeline
    print("\n2. Building pipeline...")
    pipeline = build_pipeline(bus, bus_stops, config)
    
    # Train the pipeline
    print("\n3. Training pipeline (this may take a few minutes)...")
    try:
        X_transformed = pipeline.fit_transform(phones)
        print(f"[OK] Pipeline trained successfully!")
        print(f"  Input shape: {phones.shape}")
        print(f"  Output shape: {X_transformed.shape}")
        
        # Check if rows were dropped
        if len(X_transformed) != len(phones):
            print(f"[WARNING] Pipeline dropped {len(phones) - len(X_transformed)} rows ({(len(phones) - len(X_transformed)) / len(phones) * 100:.1f}%)")
        
        # Get ground truth labels for the rows that remain (using index alignment)
        if 'labelEnc2' in X_transformed.columns:
            y_true = X_transformed['labelEnc2'].values
        else:
            print("\n[ERROR] 'labelEnc2' column not found in output. Pipeline may have dropped it.")
            print(f"Available columns: {list(X_transformed.columns)}")
            return
        
        # Get predicted labels from the last step (PcaDBSCANTransformer)
        # The transformer adds a 'pca_dbscan_cluster' column with binary labels
        if 'pca_dbscan_cluster' in X_transformed.columns:
            y_pred = X_transformed['pca_dbscan_cluster'].values
        else:
            print("\n[WARNING] No 'pca_dbscan_cluster' column found. Cannot evaluate.")
            print(f"Available columns: {list(X_transformed.columns)}")
            return
        
        print(f"\nFinal dataset for evaluation:")
        print(f"  Samples: {len(y_true):,}")
        print(f"  Ground truth distribution:")
        print(f"    Class 0 (OUT): {(y_true == 0).sum():,} ({(y_true == 0).sum() / len(y_true) * 100:.1f}%)")
        print(f"    Class 1 (IN): {(y_true == 1).sum():,} ({(y_true == 1).sum() / len(y_true) * 100:.1f}%)")
        
        # Evaluate performance
        print("\n4. Evaluating model performance...")
        print("=" * 60)
        
        # F1 Score
        f1 = f1_score(y_true, y_pred)
        print(f"\n[OK] F1 Score: {f1:.4f}")
        
        # Classification Report
        print("\nClassification Report:")
        print(classification_report(y_true, y_pred, 
                                    target_names=['OUT (0)', 'IN (1)'],
                                    digits=4))
        
        # Confusion Matrix
        cm = confusion_matrix(y_true, y_pred)
        print("\nConfusion Matrix:")
        print(f"                 Predicted")
        print(f"                 OUT    IN")
        print(f"Actual OUT    {cm[0,0]:6d} {cm[0,1]:6d}")
        print(f"Actual IN     {cm[1,0]:6d} {cm[1,1]:6d}")
        
        # Additional metrics
        accuracy = (cm[0,0] + cm[1,1]) / cm.sum()
        precision_out = cm[0,0] / (cm[0,0] + cm[1,0]) if (cm[0,0] + cm[1,0]) > 0 else 0
        recall_out = cm[0,0] / (cm[0,0] + cm[0,1]) if (cm[0,0] + cm[0,1]) > 0 else 0
        precision_in = cm[1,1] / (cm[1,1] + cm[0,1]) if (cm[1,1] + cm[0,1]) > 0 else 0
        recall_in = cm[1,1] / (cm[1,1] + cm[1,0]) if (cm[1,1] + cm[1,0]) > 0 else 0
        
        print(f"\nDetailed Metrics:")
        print(f"  Accuracy: {accuracy:.4f}")
        print(f"  Precision (OUT): {precision_out:.4f}")
        print(f"  Recall (OUT): {recall_out:.4f}")
        print(f"  Precision (IN): {precision_in:.4f}")
        print(f"  Recall (IN): {recall_in:.4f}")
        
        # Save the trained pipeline
        print("\n5. Saving model...")
        os.makedirs('models', exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save with timestamp (for archival)
        model_path_timestamped = f'models/pipeline_{timestamp}.joblib'
        joblib.dump(pipeline, model_path_timestamped)
        print(f"[OK] Model saved to: {model_path_timestamped}")
        
        # Save to fixed path (for DVC)
        model_path = 'models/pipeline.joblib'
        joblib.dump(pipeline, model_path)
        print(f"[OK] Model saved to: {model_path} (DVC tracked)")
        
        # Save evaluation results
        results = {
            'timestamp': timestamp,
            'f1_score': float(f1),
            'accuracy': float(accuracy),
            'confusion_matrix': cm.tolist(),
            'n_samples': len(phones),
            'n_features': X_transformed.shape[1] if hasattr(X_transformed, 'shape') else None,
            'config': config
        }
        
        results_path = f'models/results_{timestamp}.joblib'
        joblib.dump(results, results_path)
        print(f"[OK] Results saved to: {results_path}")
        
        # Save metrics for DVC
        import json
        metrics_dvc = {
            'f1_score': float(f1),
            'accuracy': float(accuracy),
            'precision_out': float(precision_out),
            'recall_out': float(recall_out),
            'precision_in': float(precision_in),
            'recall_in': float(recall_in)
        }
        with open('models/metrics.json', 'w') as f:
            json.dump(metrics_dvc, f, indent=2)
        print(f"[OK] Metrics saved for DVC: models/metrics.json")
        
        print("\n" + "=" * 60)
        print("[OK] Training complete!")
        print("=" * 60)
        
        return pipeline, results
        
    except Exception as e:
        print(f"\n[ERROR] Error during training: {e}")
        import traceback
        traceback.print_exc()
        return None, None


if __name__ == "__main__":
    train_and_evaluate()
