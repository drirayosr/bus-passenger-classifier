"""
Training script with MLflow experiment tracking
Logs parameters, metrics, and models automatically
"""

import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)

import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix, f1_score, accuracy_score, precision_score, recall_score
import joblib
import os
from datetime import datetime
import mlflow
import mlflow.sklearn

try:
    from .data_loader import load_and_preprocess_data
    from .pipeline import build_pipeline
    from .config import load_config
except ImportError:
    from data_loader import load_and_preprocess_data
    from pipeline import build_pipeline
    from config import load_config


def train_and_evaluate_with_mlflow(experiment_name="bus_passenger_classification", run_name=None):
    """Train the pipeline and evaluate performance with MLflow tracking"""
    
    print("=" * 60)
    print("Training Bus Passenger Classification Model with MLflow")
    print("=" * 60)
    
    # Set up MLflow
    mlflow.set_experiment(experiment_name)
    
    # Start MLflow run
    with mlflow.start_run(run_name=run_name):
        
        # Load configuration
        config = load_config()
        
        # Log configuration parameters
        print("\nLogging configuration to MLflow...")
        mlflow.log_params({
            'aoi_buffer_m': config['preprocessing']['aoi_buffer_m'],
            'speed_limit_kmh': config['preprocessing']['speed_limit_kmh'],
            'max_speed_mps': config['preprocessing']['max_speed_mps'],
            'pca_n_components': config['feature_engineering']['pca_n_components'],
            'hdbscan_min_cluster_size': config['feature_engineering']['hdbscan_min_cluster_size'],
            'hdbscan_min_samples': str(config['feature_engineering']['hdbscan_min_samples']),
            'hdbscan_cluster_selection_epsilon': config['feature_engineering']['hdbscan_cluster_selection_epsilon'],
            'hdbscan_cluster_selection_method': config['feature_engineering']['hdbscan_cluster_selection_method'],
        })
        
        # Load and preprocess data
        print("\n1. Loading data...")
        phones, bus, bus_stops = load_and_preprocess_data()
        
        print(f"\nData loaded:")
        print(f"  Passengers: {len(phones):,} rows")
        print(f"  Bus: {len(bus):,} rows")
        print(f"  Bus stops: {len(bus_stops)} stops")
        
        # Log data metrics
        mlflow.log_metrics({
            'n_passengers_raw': len(phones),
            'n_bus_records': len(bus),
            'n_bus_stops': len(bus_stops)
        })
        
        # Check if we have labels
        if 'labelEnc2' not in phones.columns:
            print("\n[ERROR] No 'labelEnc2' column found in dataset!")
            mlflow.set_tag("status", "failed")
            mlflow.set_tag("error", "missing_labels")
            return
        
        # Store ground truth labels (keep them in the dataframe for now)
        print(f"\nGround truth distribution (before pipeline):")
        n_out_true = (phones['labelEnc2'] == 0).sum()
        n_in_true = (phones['labelEnc2'] == 1).sum()
        print(f"  Class 0 (OUT): {n_out_true:,} ({n_out_true / len(phones) * 100:.1f}%)")
        print(f"  Class 1 (IN): {n_in_true:,} ({n_in_true / len(phones) * 100:.1f}%)")
        
        mlflow.log_metrics({
            'n_class_0_true': int(n_out_true),
            'n_class_1_true': int(n_in_true),
            'class_balance_ratio': float(n_in_true / n_out_true)
        })
        
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
                dropped = len(phones) - len(X_transformed)
                print(f"[WARNING] Pipeline dropped {dropped} rows ({dropped / len(phones) * 100:.1f}%)")
                mlflow.log_metric('rows_dropped', dropped)
            
            # Get ground truth labels for the rows that remain
            if 'labelEnc2' not in X_transformed.columns:
                print("\n[ERROR] 'labelEnc2' column not found in output.")
                mlflow.set_tag("status", "failed")
                mlflow.set_tag("error", "labels_dropped")
                return
            
            # Get predicted labels
            if 'pca_dbscan_cluster' not in X_transformed.columns:
                print("\n[WARNING] No 'pca_dbscan_cluster' column found.")
                mlflow.set_tag("status", "failed")
                mlflow.set_tag("error", "no_predictions")
                return
            
            y_true = X_transformed['labelEnc2'].values
            y_pred = X_transformed['pca_dbscan_cluster'].values
            
            print(f"\nFinal dataset for evaluation:")
            print(f"  Samples: {len(y_true):,}")
            print(f"  Ground truth distribution:")
            print(f"    Class 0 (OUT): {(y_true == 0).sum():,} ({(y_true == 0).sum() / len(y_true) * 100:.1f}%)")
            print(f"    Class 1 (IN): {(y_true == 1).sum():,} ({(y_true == 1).sum() / len(y_true) * 100:.1f}%)")
            
            # Evaluate performance
            print("\n4. Evaluating model performance...")
            print("=" * 60)
            
            # Calculate metrics
            f1 = f1_score(y_true, y_pred, zero_division=0)
            accuracy = accuracy_score(y_true, y_pred)
            precision = precision_score(y_true, y_pred, average='weighted', zero_division=0)
            recall = recall_score(y_true, y_pred, average='weighted', zero_division=0)
            
            # Confusion Matrix
            cm = confusion_matrix(y_true, y_pred)
            
            print(f"\n[OK] F1 Score: {f1:.4f}")
            print(f"Accuracy: {accuracy:.4f}")
            print(f"Precision (weighted): {precision:.4f}")
            print(f"Recall (weighted): {recall:.4f}")
            
            # Classification Report
            print("\nClassification Report:")
            print(classification_report(y_true, y_pred, 
                                        target_names=['OUT (0)', 'IN (1)'],
                                        digits=4))
            
            # Confusion Matrix
            print("\nConfusion Matrix:")
            print(f"                 Predicted")
            print(f"                 OUT    IN")
            print(f"Actual OUT    {cm[0,0]:6d} {cm[0,1]:6d}")
            print(f"Actual IN     {cm[1,0]:6d} {cm[1,1]:6d}")
            
            # Per-class metrics
            precision_out = cm[0,0] / (cm[0,0] + cm[1,0]) if (cm[0,0] + cm[1,0]) > 0 else 0
            recall_out = cm[0,0] / (cm[0,0] + cm[0,1]) if (cm[0,0] + cm[0,1]) > 0 else 0
            f1_out = 2 * (precision_out * recall_out) / (precision_out + recall_out) if (precision_out + recall_out) > 0 else 0
            
            precision_in = cm[1,1] / (cm[1,1] + cm[0,1]) if (cm[1,1] + cm[0,1]) > 0 else 0
            recall_in = cm[1,1] / (cm[1,1] + cm[1,0]) if (cm[1,1] + cm[1,0]) > 0 else 0
            f1_in = 2 * (precision_in * recall_in) / (precision_in + recall_in) if (precision_in + recall_in) > 0 else 0
            
            print(f"\nPer-Class Metrics:")
            print(f"  OUT - Precision: {precision_out:.4f}, Recall: {recall_out:.4f}, F1: {f1_out:.4f}")
            print(f"  IN  - Precision: {precision_in:.4f}, Recall: {recall_in:.4f}, F1: {f1_in:.4f}")
            
            # Log all metrics to MLflow
            mlflow.log_metrics({
                'f1_score': float(f1),
                'accuracy': float(accuracy),
                'precision_weighted': float(precision),
                'recall_weighted': float(recall),
                'precision_out': float(precision_out),
                'recall_out': float(recall_out),
                'f1_out': float(f1_out),
                'precision_in': float(precision_in),
                'recall_in': float(recall_in),
                'f1_in': float(f1_in),
                'true_negatives': int(cm[0,0]),
                'false_positives': int(cm[0,1]),
                'false_negatives': int(cm[1,0]),
                'true_positives': int(cm[1,1]),
                'n_samples_evaluated': len(y_true)
            })
            
            # Log confusion matrix as artifact
            import matplotlib.pyplot as plt
            import seaborn as sns
            
            plt.figure(figsize=(8, 6))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                       xticklabels=['OUT', 'IN'], 
                       yticklabels=['OUT', 'IN'])
            plt.title(f'Confusion Matrix (F1={f1:.4f})')
            plt.ylabel('Actual')
            plt.xlabel('Predicted')
            
            cm_path = 'confusion_matrix.png'
            plt.savefig(cm_path)
            mlflow.log_artifact(cm_path)
            os.remove(cm_path)
            plt.close()
            
            # Save the trained pipeline
            print("\n5. Saving model...")
            os.makedirs('models', exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            model_path = f'models/pipeline_mlflow_{timestamp}.joblib'
            joblib.dump(pipeline, model_path)
            print(f"[OK] Model saved to: {model_path}")
            
            # Log model to MLflow
            mlflow.sklearn.log_model(pipeline, "model")
            
            # Log model locally as artifact
            mlflow.log_artifact(model_path)
            
            # Save evaluation results
            results = {
                'timestamp': timestamp,
                'f1_score': float(f1),
                'accuracy': float(accuracy),
                'confusion_matrix': cm.tolist(),
                'n_samples': len(y_true),
                'n_features': X_transformed.shape[1],
                'config': config
            }
            
            results_path = f'models/results_mlflow_{timestamp}.joblib'
            joblib.dump(results, results_path)
            print(f"[OK] Results saved to: {results_path}")
            mlflow.log_artifact(results_path)
            
            # Set tags
            mlflow.set_tag("status", "success")
            mlflow.set_tag("model_type", "hdbscan_clustering")
            mlflow.set_tag("feature_engineering", "speed_accel_bearing_distance")
            
            print("\n" + "=" * 60)
            print("[OK] Training complete! Results logged to MLflow")
            print("=" * 60)
            print(f"\nMLflow Run ID: {mlflow.active_run().info.run_id}")
            print(f"View results: mlflow ui")
            
            return pipeline, results
            
        except Exception as e:
            print(f"\n[ERROR] Error during training: {e}")
            mlflow.set_tag("status", "failed")
            mlflow.set_tag("error", str(e))
            import traceback
            traceback.print_exc()
            return None, None


if __name__ == "__main__":
    train_and_evaluate_with_mlflow()
