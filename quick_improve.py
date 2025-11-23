"""
Quick Model Improvement Script (5-10 minutes)
Tests the most promising hyperparameter combinations
"""

import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
from sklearn.metrics import f1_score, accuracy_score, classification_report, confusion_matrix
from datetime import datetime

from src.data_loader import load_and_preprocess_data
from src.pipeline import build_pipeline
from src.config import load_config


def quick_tune():
    """Quick tuning with most promising parameters"""
    
    print("=" * 80)
    print("QUICK MODEL ACCURACY IMPROVEMENT")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%H:%M:%S')}")
    
    # Load data
    print("\nLoading data...")
    phones, bus, bus_stops = load_and_preprocess_data()
    config = load_config()
    
    # Test promising combinations (based on typical HDBSCAN performance)
    test_configs = [
        # Current baseline
        {'name': 'BASELINE (current)', 
         'min_cluster_size': 300, 'min_samples': None, 
         'cluster_selection_epsilon': 0.5, 'cluster_selection_method': 'eom'},
        
        # Smaller clusters for better granularity
        {'name': 'Smaller clusters', 
         'min_cluster_size': 100, 'min_samples': 5, 
         'cluster_selection_epsilon': 0.3, 'cluster_selection_method': 'eom'},
        
        # Medium clusters with leaf selection
        {'name': 'Medium + leaf', 
         'min_cluster_size': 200, 'min_samples': 10, 
         'cluster_selection_epsilon': 0.5, 'cluster_selection_method': 'leaf'},
        
        # Larger clusters for stability
        {'name': 'Larger stable', 
         'min_cluster_size': 500, 'min_samples': 15, 
         'cluster_selection_epsilon': 0.7, 'cluster_selection_method': 'eom'},
        
        # Very tight clusters
        {'name': 'Very tight', 
         'min_cluster_size': 150, 'min_samples': 20, 
         'cluster_selection_epsilon': 0.3, 'cluster_selection_method': 'eom'},
        
        # Balanced approach
        {'name': 'Balanced', 
         'min_cluster_size': 250, 'min_samples': 10, 
         'cluster_selection_epsilon': 0.4, 'cluster_selection_method': 'eom'},
    ]
    
    print(f"\nTesting {len(test_configs)} configurations...\n")
    
    results = []
    best_f1 = 0
    best_config = None
    best_y_pred = None
    best_y_true = None
    
    for i, test_cfg in enumerate(test_configs, 1):
        print(f"[{i}/{len(test_configs)}] {test_cfg['name']}")
        print(f"  min_cluster_size={test_cfg['min_cluster_size']}, "
              f"min_samples={test_cfg['min_samples']}, "
              f"epsilon={test_cfg['cluster_selection_epsilon']}, "
              f"method={test_cfg['cluster_selection_method']}")
        
        # Update config
        cfg = config.copy()
        cfg['feature_engineering']['hdbscan_min_cluster_size'] = test_cfg['min_cluster_size']
        cfg['feature_engineering']['hdbscan_min_samples'] = test_cfg['min_samples']
        cfg['feature_engineering']['hdbscan_cluster_selection_epsilon'] = test_cfg['cluster_selection_epsilon']
        cfg['feature_engineering']['hdbscan_cluster_selection_method'] = test_cfg['cluster_selection_method']
        
        try:
            # Build and train
            pipeline = build_pipeline(bus, bus_stops, cfg)
            X_transformed = pipeline.fit_transform(phones)
            
            if 'labelEnc2' not in X_transformed.columns or 'pca_dbscan_cluster' not in X_transformed.columns:
                print("  ⚠️  Missing columns, skipping...")
                continue
            
            y_true = X_transformed['labelEnc2'].values
            y_pred = X_transformed['pca_dbscan_cluster'].values
            
            # Calculate metrics
            accuracy = accuracy_score(y_true, y_pred)
            f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)
            
            # Count unique clusters
            n_clusters = len(np.unique(y_pred[y_pred != -1]))
            n_noise = (y_pred == -1).sum()
            
            print(f"  ✓ Accuracy: {accuracy:.4f} | F1: {f1:.4f} | Clusters: {n_clusters} | Noise: {n_noise}")
            
            results.append({
                'config': test_cfg['name'],
                'accuracy': accuracy,
                'f1_score': f1,
                'n_clusters': n_clusters,
                'n_noise': n_noise,
                **test_cfg
            })
            
            # Track best
            if f1 > best_f1:
                best_f1 = f1
                best_config = test_cfg
                best_y_pred = y_pred
                best_y_true = y_true
                print(f"  ★ NEW BEST!")
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
        
        print()
    
    # Results summary
    print("=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)
    
    results_df = pd.DataFrame(results).sort_values('f1_score', ascending=False)
    print("\nAll configurations ranked by F1-Score:")
    print(results_df[['config', 'accuracy', 'f1_score', 'n_clusters', 'n_noise']].to_string(index=False))
    
    # Best model details
    if best_config:
        print("\n" + "=" * 80)
        print("BEST CONFIGURATION")
        print("=" * 80)
        print(f"\nName: {best_config['name']}")
        print(f"F1-Score: {best_f1:.4f}")
        print(f"\nParameters:")
        print(f"  hdbscan_min_cluster_size: {best_config['min_cluster_size']}")
        print(f"  hdbscan_min_samples: {best_config['min_samples']}")
        print(f"  hdbscan_cluster_selection_epsilon: {best_config['cluster_selection_epsilon']}")
        print(f"  hdbscan_cluster_selection_method: '{best_config['cluster_selection_method']}'")
        
        # Detailed metrics
        print("\n" + "-" * 40)
        print("Detailed Classification Report:")
        print("-" * 40)
        print(classification_report(best_y_true, best_y_pred, 
                                   target_names=['OUT (0)', 'IN (1)'],
                                   zero_division=0))
        
        print("\nConfusion Matrix:")
        cm = confusion_matrix(best_y_true, best_y_pred)
        print(f"                Predicted")
        print(f"                OUT    IN")
        print(f"Actual  OUT   {cm[0,0]:5d} {cm[0,1]:5d}")
        print(f"        IN    {cm[1,0]:5d} {cm[1,1]:5d}")
        
        # Calculate improvement
        baseline_f1 = results_df[results_df['config'] == 'BASELINE (current)']['f1_score'].values
        if len(baseline_f1) > 0:
            improvement = (best_f1 - baseline_f1[0]) / baseline_f1[0] * 100
            print(f"\n{'=' * 80}")
            print(f"IMPROVEMENT: {improvement:+.2f}%")
            print(f"  Baseline: {baseline_f1[0]:.4f}")
            print(f"  Best:     {best_f1:.4f}")
            print(f"{'=' * 80}")
        
        # Save recommended config
        print("\n" + "-" * 40)
        print("To apply this configuration:")
        print("-" * 40)
        print("\nUpdate config/config.yaml:")
        print("\nfeature_engineering:")
        print(f"  hdbscan_min_cluster_size: {best_config['min_cluster_size']}")
        print(f"  hdbscan_min_samples: {best_config['min_samples']}")
        print(f"  hdbscan_cluster_selection_epsilon: {best_config['cluster_selection_epsilon']}")
        print(f"  hdbscan_cluster_selection_method: '{best_config['cluster_selection_method']}'")
        
        print("\nThen retrain:")
        print("  python src/train_mlflow.py")
    
    print(f"\n✓ Completed: {datetime.now().strftime('%H:%M:%S')}")
    
    return results_df, best_config


if __name__ == "__main__":
    results_df, best_config = quick_tune()
    
    # Save results
    results_df.to_csv('quick_tuning_results.csv', index=False)
    print(f"\n✓ Results saved to: quick_tuning_results.csv")
