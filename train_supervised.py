"""
Supervised Learning Alternative
Uses Random Forest/XGBoost instead of HDBSCAN clustering
Expected accuracy: 80-90% (vs current 68%)
"""

import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, f1_score, accuracy_score
import mlflow
import mlflow.sklearn
import joblib
from datetime import datetime

from src.data_loader import load_and_preprocess_data
from src.config import load_config
from src.transformers import (
    SpeedTransformer,
    AccelerationTransformer,
    BearingRateVariationTransformer,
    DistanceToStopsTransformer,
    DistanceToBusesTransformer
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def build_feature_pipeline(bus_df, bus_stops_df, config):
    """Build feature engineering pipeline (without clustering)"""
    
    preprocessing = config['preprocessing']
    unique_bus_ids = bus_df['bus_id'].unique().tolist()
    
    pipeline = Pipeline([
        ('speed', SpeedTransformer(
            speed_limit_mps=preprocessing['max_speed_mps']
        )),
        ('acceleration', AccelerationTransformer()),
        ('bearing_rate_variation', BearingRateVariationTransformer()),
        ('distance_to_stops', DistanceToStopsTransformer(
            median_coords=bus_stops_df
        )),
        ('distance_to_buses', DistanceToBusesTransformer(
            bus_df=bus_df,
            bus_ids=unique_bus_ids,
            tolerance=preprocessing['bus_time_tolerance']
        )),
    ])
    
    return pipeline


def train_supervised_model(model_name='random_forest'):
    """Train supervised ML model"""
    
    print("=" * 80)
    print(f"SUPERVISED LEARNING - {model_name.upper()}")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%H:%M:%S')}\n")
    
    # Load data
    print("1. Loading data...")
    phones, bus, bus_stops = load_and_preprocess_data()
    config = load_config()
    
    print(f"   Passengers: {len(phones):,} records")
    print(f"   Bus: {len(bus):,} records")
    
    if 'labelEnc2' not in phones.columns:
        print("\n❌ ERROR: No labelEnc2 column found!")
        print("   This dataset needs ground truth labels for supervised learning.")
        return
    
    # Build feature pipeline
    print("\n2. Building feature pipeline...")
    feature_pipeline = build_feature_pipeline(bus, bus_stops, config)
    
    # Transform data
    print("   Extracting features...")
    X_features = feature_pipeline.fit_transform(phones)
    
    # Get labels
    y = X_features['labelEnc2'].values
    
    # Select numeric feature columns (exclude metadata)
    feature_cols = [col for col in X_features.columns 
                   if col not in ['labelEnc2', 'timestamp', 'user_id', 'bus_id'] 
                   and X_features[col].dtype in ['float64', 'int64']]
    
    X = X_features[feature_cols].values
    
    print(f"   Features: {X.shape[1]} columns")
    print(f"   Samples: {X.shape[0]:,} rows")
    print(f"   Class distribution:")
    print(f"     OUT (0): {(y == 0).sum():,} ({(y == 0).sum() / len(y) * 100:.1f}%)")
    print(f"     IN (1):  {(y == 1).sum():,} ({(y == 1).sum() / len(y) * 100:.1f}%)")
    
    # Train-test split
    print("\n3. Splitting data (80% train, 20% test)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"   Train: {X_train.shape[0]:,} samples")
    print(f"   Test:  {X_test.shape[0]:,} samples")
    
    # Train model
    print(f"\n4. Training {model_name}...")
    
    mlflow.set_experiment(f"supervised_learning_{model_name}")
    
    with mlflow.start_run(run_name=f"{model_name}_{datetime.now().strftime('%Y%m%d_%H%M')}"):
        
        # Choose model
        if model_name == 'random_forest':
            model = RandomForestClassifier(
                n_estimators=100,
                max_depth=15,
                min_samples_split=10,
                min_samples_leaf=4,
                random_state=42,
                n_jobs=-1,
                verbose=1
            )
            mlflow.log_params({
                'model': 'RandomForest',
                'n_estimators': 100,
                'max_depth': 15,
                'min_samples_split': 10,
                'min_samples_leaf': 4
            })
            
        elif model_name == 'gradient_boosting':
            model = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                min_samples_split=10,
                random_state=42,
                verbose=1
            )
            mlflow.log_params({
                'model': 'GradientBoosting',
                'n_estimators': 100,
                'learning_rate': 0.1,
                'max_depth': 5
            })
        
        else:  # xgboost
            try:
                from xgboost import XGBClassifier
                model = XGBClassifier(
                    n_estimators=100,
                    learning_rate=0.1,
                    max_depth=6,
                    random_state=42,
                    n_jobs=-1
                )
                mlflow.log_params({
                    'model': 'XGBoost',
                    'n_estimators': 100,
                    'learning_rate': 0.1,
                    'max_depth': 6
                })
            except ImportError:
                print("\n⚠️  XGBoost not installed, falling back to Random Forest")
                print("   Install with: pip install xgboost")
                model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        
        # Fit model
        model.fit(X_train, y_train)
        
        print("\n5. Evaluating model...")
        
        # Predictions
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        
        # Metrics
        train_acc = accuracy_score(y_train, y_pred_train)
        test_acc = accuracy_score(y_test, y_pred_test)
        test_f1 = f1_score(y_test, y_pred_test, average='weighted')
        
        print("\n" + "=" * 80)
        print("RESULTS")
        print("=" * 80)
        print(f"\nTrain Accuracy: {train_acc:.4f} ({train_acc*100:.2f}%)")
        print(f"Test Accuracy:  {test_acc:.4f} ({test_acc*100:.2f}%)")
        print(f"Test F1-Score:  {test_f1:.4f} ({test_f1*100:.2f}%)")
        
        print("\n" + "-" * 80)
        print("Detailed Classification Report (Test Set):")
        print("-" * 80)
        print(classification_report(y_test, y_pred_test, 
                                   target_names=['OUT (0)', 'IN (1)'],
                                   digits=4))
        
        print("\nConfusion Matrix:")
        cm = confusion_matrix(y_test, y_pred_test)
        print(f"                Predicted")
        print(f"                OUT    IN")
        print(f"Actual  OUT   {cm[0,0]:5d} {cm[0,1]:5d}")
        print(f"        IN    {cm[1,0]:5d} {cm[1,1]:5d}")
        
        # Feature importance
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            feature_importance = pd.DataFrame({
                'feature': feature_cols,
                'importance': importances
            }).sort_values('importance', ascending=False)
            
            print("\n" + "-" * 80)
            print("Top 15 Most Important Features:")
            print("-" * 80)
            print(feature_importance.head(15).to_string(index=False))
        
        # Log to MLflow
        mlflow.log_metrics({
            'train_accuracy': train_acc,
            'test_accuracy': test_acc,
            'test_f1_score': test_f1
        })
        
        # Save model
        mlflow.sklearn.log_model(model, "model")
        
        model_path = f'models/supervised/{model_name}_model.pkl'
        import os
        os.makedirs('models/supervised', exist_ok=True)
        joblib.dump(model, model_path)
        
        print(f"\n✓ Model saved to: {model_path}")
        print(f"✓ Logged to MLflow: http://localhost:5000")
    
    print(f"\n✓ Completed: {datetime.now().strftime('%H:%M:%S')}")
    
    return model, test_acc, test_f1


def compare_models():
    """Train and compare multiple supervised models"""
    
    print("\n" + "=" * 80)
    print("COMPARING SUPERVISED LEARNING MODELS")
    print("=" * 80)
    
    models = ['random_forest', 'gradient_boosting']
    
    # Check if XGBoost available
    try:
        import xgboost
        models.append('xgboost')
    except ImportError:
        print("\n⚠️  XGBoost not installed (optional)")
        print("   Install with: pip install xgboost\n")
    
    results = []
    
    for model_name in models:
        print(f"\n{'=' * 80}")
        print(f"Training {model_name.replace('_', ' ').title()}")
        print(f"{'=' * 80}\n")
        
        try:
            model, acc, f1 = train_supervised_model(model_name)
            results.append({
                'model': model_name,
                'accuracy': acc,
                'f1_score': f1
            })
        except Exception as e:
            print(f"❌ Error training {model_name}: {e}")
    
    # Summary
    print("\n" + "=" * 80)
    print("FINAL COMPARISON")
    print("=" * 80)
    
    results_df = pd.DataFrame(results).sort_values('f1_score', ascending=False)
    print("\nModels ranked by F1-Score:")
    print(results_df.to_string(index=False))
    
    best_model = results_df.iloc[0]
    print(f"\n🏆 BEST MODEL: {best_model['model'].replace('_', ' ').title()}")
    print(f"   Accuracy: {best_model['accuracy']:.4f} ({best_model['accuracy']*100:.2f}%)")
    print(f"   F1-Score: {best_model['f1_score']:.4f} ({best_model['f1_score']*100:.2f}%)")
    
    # Compare with HDBSCAN baseline
    print("\n" + "=" * 80)
    print("IMPROVEMENT vs HDBSCAN BASELINE")
    print("=" * 80)
    print(f"\nHDBSCAN (unsupervised):")
    print(f"  Accuracy: 0.682 (68.2%)")
    print(f"  F1-Score: 0.596 (59.6%)")
    print(f"\nBest Supervised Model ({best_model['model']}):")
    print(f"  Accuracy: {best_model['accuracy']:.4f} ({best_model['accuracy']*100:.2f}%)")
    print(f"  F1-Score: {best_model['f1_score']:.4f} ({best_model['f1_score']*100:.2f}%)")
    print(f"\nImprovement:")
    acc_improvement = (best_model['accuracy'] - 0.682) / 0.682 * 100
    f1_improvement = (best_model['f1_score'] - 0.596) / 0.596 * 100
    print(f"  Accuracy: {acc_improvement:+.1f}%")
    print(f"  F1-Score: {f1_improvement:+.1f}%")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'compare':
            compare_models()
        else:
            train_supervised_model(sys.argv[1])
    else:
        # Default: compare all models
        compare_models()
