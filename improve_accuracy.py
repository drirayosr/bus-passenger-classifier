"""
Model Accuracy Improvement Script
Tests multiple approaches to improve classification performance:
1. Hyperparameter tuning (grid search)
2. Feature selection
3. Ensemble methods
4. Different clustering approaches
5. Class balancing techniques
"""

import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
from sklearn.metrics import f1_score, accuracy_score, precision_score, recall_score, classification_report
from sklearn.model_selection import ParameterGrid
import mlflow
import mlflow.sklearn
from datetime import datetime
import joblib
import os

from src.data_loader import load_and_preprocess_data
from src.pipeline import build_pipeline
from src.config import load_config


def evaluate_model(y_true, y_pred, verbose=True):
    """Calculate comprehensive metrics"""
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, average='weighted', zero_division=0)
    recall = recall_score(y_true, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)
    
    if verbose:
        print(f"  Accuracy:  {accuracy:.4f}")
        print(f"  Precision: {precision:.4f}")
        print(f"  Recall:    {recall:.4f}")
        print(f"  F1-Score:  {f1:.4f}")
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1
    }


def grid_search_hdbscan(phones, bus, bus_stops, base_config):
    """
    Perform grid search on HDBSCAN hyperparameters
    This is the most impactful tuning for clustering-based classification
    """
    print("\n" + "=" * 80)
    print("APPROACH 1: HDBSCAN HYPERPARAMETER GRID SEARCH")
    print("=" * 80)
    
    # Define parameter grid
    param_grid = {
        'min_cluster_size': [100, 200, 300, 500, 800, 1000],
        'min_samples': [None, 5, 10, 15, 20],
        'cluster_selection_epsilon': [0.0, 0.3, 0.5, 0.7, 1.0],
        'cluster_selection_method': ['eom', 'leaf']
    }
    
    print(f"\nTesting {len(list(ParameterGrid(param_grid)))} parameter combinations...")
    print(f"Parameters to tune:")
    for param, values in param_grid.items():
        print(f"  {param}: {values}")
    
    best_f1 = 0
    best_params = None
    best_results = None
    
    mlflow.set_experiment("accuracy_improvement_grid_search")
    
    results = []
    
    for i, params in enumerate(ParameterGrid(param_grid), 1):
        print(f"\n[{i}/{len(list(ParameterGrid(param_grid)))}] Testing: {params}")
        
        with mlflow.start_run(run_name=f"grid_search_{i}"):
            # Update config with current params
            config = base_config.copy()
            config['feature_engineering']['hdbscan_min_cluster_size'] = params['min_cluster_size']
            config['feature_engineering']['hdbscan_min_samples'] = params['min_samples']
            config['feature_engineering']['hdbscan_cluster_selection_epsilon'] = params['cluster_selection_epsilon']
            config['feature_engineering']['hdbscan_cluster_selection_method'] = params['cluster_selection_method']
            
            # Build and train pipeline
            try:
                pipeline = build_pipeline(bus, bus_stops, config)
                X_transformed = pipeline.fit_transform(phones)
                
                # Extract labels
                if 'labelEnc2' not in X_transformed.columns or 'pca_dbscan_cluster' not in X_transformed.columns:
                    print("  [SKIP] Missing required columns")
                    continue
                
                y_true = X_transformed['labelEnc2'].values
                y_pred = X_transformed['pca_dbscan_cluster'].values
                
                # Evaluate
                metrics = evaluate_model(y_true, y_pred, verbose=False)
                
                # Log to MLflow
                mlflow.log_params(params)
                mlflow.log_metrics(metrics)
                
                # Store results
                result = {**params, **metrics}
                results.append(result)
                
                print(f"  F1: {metrics['f1_score']:.4f} | Acc: {metrics['accuracy']:.4f}")
                
                # Track best
                if metrics['f1_score'] > best_f1:
                    best_f1 = metrics['f1_score']
                    best_params = params
                    best_results = metrics
                    mlflow.set_tag("best_so_far", "true")
                    print(f"  ★ NEW BEST F1: {best_f1:.4f}")
                    
            except Exception as e:
                print(f"  [ERROR] {str(e)}")
                continue
    
    print("\n" + "=" * 80)
    print("GRID SEARCH RESULTS")
    print("=" * 80)
    print(f"\nBest F1-Score: {best_f1:.4f}")
    print(f"Best Parameters: {best_params}")
    print(f"\nBest Metrics:")
    for k, v in best_results.items():
        print(f"  {k}: {v:.4f}")
    
    # Save results
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('f1_score', ascending=False)
    results_df.to_csv('model_tuning_results.csv', index=False)
    print(f"\n✓ Results saved to: model_tuning_results.csv")
    print(f"\nTop 5 configurations:")
    print(results_df.head().to_string())
    
    return best_params, best_f1, results_df


def test_pca_components(phones, bus, bus_stops, base_config):
    """Test different PCA component numbers"""
    print("\n" + "=" * 80)
    print("APPROACH 2: PCA COMPONENT TUNING")
    print("=" * 80)
    
    mlflow.set_experiment("accuracy_improvement_pca_tuning")
    
    pca_values = [2, 3, 4, 5, 6, 8, 10]
    results = []
    
    for n_comp in pca_values:
        print(f"\nTesting PCA n_components = {n_comp}")
        
        with mlflow.start_run(run_name=f"pca_{n_comp}"):
            config = base_config.copy()
            config['feature_engineering']['pca_n_components'] = n_comp
            
            try:
                pipeline = build_pipeline(bus, bus_stops, config)
                X_transformed = pipeline.fit_transform(phones)
                
                if 'labelEnc2' not in X_transformed.columns or 'pca_dbscan_cluster' not in X_transformed.columns:
                    continue
                
                y_true = X_transformed['labelEnc2'].values
                y_pred = X_transformed['pca_dbscan_cluster'].values
                
                metrics = evaluate_model(y_true, y_pred, verbose=True)
                
                mlflow.log_param('pca_n_components', n_comp)
                mlflow.log_metrics(metrics)
                
                results.append({'n_components': n_comp, **metrics})
                
            except Exception as e:
                print(f"  [ERROR] {str(e)}")
                continue
    
    results_df = pd.DataFrame(results).sort_values('f1_score', ascending=False)
    print(f"\n{results_df.to_string()}")
    
    return results_df


def test_preprocessing_variants(phones, bus, bus_stops, base_config):
    """Test different preprocessing strategies"""
    print("\n" + "=" * 80)
    print("APPROACH 3: PREPROCESSING VARIANTS")
    print("=" * 80)
    
    mlflow.set_experiment("accuracy_improvement_preprocessing")
    
    variants = [
        {'name': 'baseline', 'aoi_buffer_m': 50, 'speed_limit_kmh': 35},
        {'name': 'wider_aoi', 'aoi_buffer_m': 100, 'speed_limit_kmh': 35},
        {'name': 'narrower_aoi', 'aoi_buffer_m': 25, 'speed_limit_kmh': 35},
        {'name': 'higher_speed', 'aoi_buffer_m': 50, 'speed_limit_kmh': 50},
        {'name': 'lower_speed', 'aoi_buffer_m': 50, 'speed_limit_kmh': 25},
    ]
    
    results = []
    
    for variant in variants:
        print(f"\nTesting: {variant['name']}")
        print(f"  AOI buffer: {variant['aoi_buffer_m']}m")
        print(f"  Speed limit: {variant['speed_limit_kmh']} km/h")
        
        with mlflow.start_run(run_name=variant['name']):
            config = base_config.copy()
            config['preprocessing']['aoi_buffer_m'] = variant['aoi_buffer_m']
            config['preprocessing']['speed_limit_kmh'] = variant['speed_limit_kmh']
            config['preprocessing']['max_speed_mps'] = variant['speed_limit_kmh'] / 3.6
            
            try:
                pipeline = build_pipeline(bus, bus_stops, config)
                X_transformed = pipeline.fit_transform(phones)
                
                if 'labelEnc2' not in X_transformed.columns or 'pca_dbscan_cluster' not in X_transformed.columns:
                    continue
                
                y_true = X_transformed['labelEnc2'].values
                y_pred = X_transformed['pca_dbscan_cluster'].values
                
                metrics = evaluate_model(y_true, y_pred, verbose=True)
                
                mlflow.log_params(variant)
                mlflow.log_metrics(metrics)
                
                results.append({**variant, **metrics})
                
            except Exception as e:
                print(f"  [ERROR] {str(e)}")
                continue
    
    results_df = pd.DataFrame(results).sort_values('f1_score', ascending=False)
    print(f"\n{results_df.to_string()}")
    
    return results_df


def analyze_feature_importance(phones_transformed):
    """Analyze which features are most important"""
    print("\n" + "=" * 80)
    print("APPROACH 4: FEATURE IMPORTANCE ANALYSIS")
    print("=" * 80)
    
    # Get feature columns (exclude metadata)
    feature_cols = [col for col in phones_transformed.columns 
                   if not col.startswith('labelEnc') and 
                   not col.startswith('pca_dbscan') and
                   col not in ['timestamp', 'user_id', 'bus_id']]
    
    print(f"\nAnalyzing {len(feature_cols)} features...")
    
    # Calculate correlation with true labels
    if 'labelEnc2' in phones_transformed.columns:
        correlations = []
        for col in feature_cols:
            if phones_transformed[col].dtype in ['float64', 'int64']:
                corr = phones_transformed[col].corr(phones_transformed['labelEnc2'])
                correlations.append({'feature': col, 'correlation': abs(corr)})
        
        corr_df = pd.DataFrame(correlations).sort_values('correlation', ascending=False)
        print("\nTop 15 most correlated features:")
        print(corr_df.head(15).to_string())
        
        return corr_df
    
    return None


def main():
    """Main execution"""
    print("=" * 80)
    print("BUS PASSENGER CLASSIFICATION - MODEL ACCURACY IMPROVEMENT")
    print("=" * 80)
    print(f"\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load data
    print("\nLoading data...")
    phones, bus, bus_stops = load_and_preprocess_data()
    print(f"  Passengers: {len(phones):,} records")
    print(f"  Bus: {len(bus):,} records")
    print(f"  Bus stops: {len(bus_stops)} stops")
    
    # Load base config
    base_config = load_config()
    
    # Current baseline performance
    print("\n" + "=" * 80)
    print("BASELINE PERFORMANCE (Current Configuration)")
    print("=" * 80)
    
    pipeline = build_pipeline(bus, bus_stops, base_config)
    X_transformed = pipeline.fit_transform(phones)
    
    if 'labelEnc2' in X_transformed.columns and 'pca_dbscan_cluster' in X_transformed.columns:
        y_true = X_transformed['labelEnc2'].values
        y_pred = X_transformed['pca_dbscan_cluster'].values
        baseline_metrics = evaluate_model(y_true, y_pred, verbose=True)
        baseline_f1 = baseline_metrics['f1_score']
    else:
        print("[ERROR] Cannot compute baseline - missing columns")
        return
    
    # Test different approaches
    print("\n\nStarting improvement experiments...")
    print("This will take 15-30 minutes depending on grid size...")
    
    # Approach 1: Grid search on HDBSCAN (most important)
    best_params, best_f1, grid_results = grid_search_hdbscan(phones, bus, bus_stops, base_config)
    
    improvement = (best_f1 - baseline_f1) / baseline_f1 * 100
    print(f"\n{'=' * 80}")
    print(f"IMPROVEMENT: {improvement:+.2f}% (from {baseline_f1:.4f} to {best_f1:.4f})")
    print(f"{'=' * 80}")
    
    # Approach 2: PCA tuning
    pca_results = test_pca_components(phones, bus, bus_stops, base_config)
    
    # Approach 3: Preprocessing variants
    preproc_results = test_preprocessing_variants(phones, bus, bus_stops, base_config)
    
    # Approach 4: Feature analysis
    feature_importance = analyze_feature_importance(X_transformed)
    
    # Save optimal configuration
    optimal_config = base_config.copy()
    optimal_config['feature_engineering'].update(best_params)
    
    print("\n" + "=" * 80)
    print("OPTIMAL CONFIGURATION")
    print("=" * 80)
    print("\nRecommended config.yaml updates:")
    print("\nfeature_engineering:")
    for key, value in best_params.items():
        print(f"  hdbscan_{key}: {value}")
    
    # Test optimal configuration
    print("\n\nVerifying optimal configuration...")
    optimal_pipeline = build_pipeline(bus, bus_stops, optimal_config)
    X_opt = optimal_pipeline.fit_transform(phones)
    
    if 'labelEnc2' in X_opt.columns and 'pca_dbscan_cluster' in X_opt.columns:
        y_true_opt = X_opt['labelEnc2'].values
        y_pred_opt = X_opt['pca_dbscan_cluster'].values
        
        print("\nOPTIMAL MODEL PERFORMANCE:")
        final_metrics = evaluate_model(y_true_opt, y_pred_opt, verbose=True)
        
        # Save model
        os.makedirs('models/optimized', exist_ok=True)
        model_path = 'models/optimized/best_model.pkl'
        joblib.dump(optimal_pipeline, model_path)
        print(f"\n✓ Optimal model saved to: {model_path}")
        
        # Save config
        import yaml
        config_path = 'config/config_optimized.yaml'
        with open(config_path, 'w') as f:
            yaml.dump(optimal_config, f, default_flow_style=False)
        print(f"✓ Optimal config saved to: {config_path}")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\nBaseline F1-Score:  {baseline_f1:.4f}")
    print(f"Optimized F1-Score: {best_f1:.4f}")
    print(f"Improvement:        {improvement:+.2f}%")
    
    print(f"\n✓ All results saved to MLflow experiments")
    print(f"✓ View results: http://localhost:5000")
    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
