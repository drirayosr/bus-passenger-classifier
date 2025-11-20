"""
Script to register trained model to MLflow Model Registry
"""
import mlflow
from mlflow.tracking import MlflowClient
import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from config import load_config


def register_latest_model():
    """Register the latest trained model to Model Registry"""
    
    # Load config
    config = load_config()
    
    # Setup MLflow
    mlflow_uri = os.getenv("MLFLOW_TRACKING_URI", config['mlflow']['tracking_uri'])
    mlflow.set_tracking_uri(mlflow_uri)
    
    client = MlflowClient()
    
    # Get experiment
    experiment_name = config['mlflow']['experiment_name']
    experiment = client.get_experiment_by_name(experiment_name)
    
    if experiment is None:
        print(f"❌ Experiment '{experiment_name}' not found")
        return False
    
    # Get latest run
    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=["start_time DESC"],
        max_results=1
    )
    
    if not runs:
        print("❌ No runs found")
        return False
    
    latest_run = runs[0]
    run_id = latest_run.info.run_id
    
    print(f"✅ Latest run: {run_id}")
    print(f"   F1-score: {latest_run.data.metrics.get('f1_score', 'N/A')}")
    print(f"   Accuracy: {latest_run.data.metrics.get('accuracy', 'N/A')}")
    
    # Register model
    model_name = "bus-passenger-classifier"
    model_uri = f"runs:/{run_id}/model"
    
    try:
        # Register new version
        model_version = mlflow.register_model(model_uri, model_name)
        version = model_version.version
        
        print(f"✅ Model registered as version {version}")
        
        # Get F1 score to decide if we should promote to production
        f1_score = latest_run.data.metrics.get('f1_score', 0)
        
        # Get current production model (if any)
        try:
            prod_versions = client.get_latest_versions(model_name, stages=["Production"])
            if prod_versions:
                current_prod = prod_versions[0]
                current_run = client.get_run(current_prod.run_id)
                current_f1 = current_run.data.metrics.get('f1_score', 0)
                
                print(f"\n📊 Current production model:")
                print(f"   Version: {current_prod.version}")
                print(f"   F1-score: {current_f1:.4f}")
                print(f"\n📊 New model:")
                print(f"   Version: {version}")
                print(f"   F1-score: {f1_score:.4f}")
                
                # Only promote if better
                if f1_score > current_f1:
                    # Archive old production model
                    client.transition_model_version_stage(
                        name=model_name,
                        version=current_prod.version,
                        stage="Archived"
                    )
                    print(f"✅ Archived old production model (v{current_prod.version})")
                    
                    # Promote new model
                    client.transition_model_version_stage(
                        name=model_name,
                        version=version,
                        stage="Production"
                    )
                    print(f"🚀 Promoted new model to Production (v{version})")
                    print(f"   Improvement: +{(f1_score - current_f1):.4f} F1-score")
                else:
                    print(f"⚠️  New model not better than current production")
                    print(f"   Keeping current production model (v{current_prod.version})")
                    # Keep in Staging
                    client.transition_model_version_stage(
                        name=model_name,
                        version=version,
                        stage="Staging"
                    )
            else:
                # No production model yet, promote this one
                client.transition_model_version_stage(
                    name=model_name,
                    version=version,
                    stage="Production"
                )
                print(f"🚀 Promoted to Production (v{version}) - First production model")
        
        except Exception as e:
            print(f"⚠️  Could not compare with production model: {e}")
            print(f"   Model registered as v{version} in None stage")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to register model: {e}")
        return False


if __name__ == "__main__":
    success = register_latest_model()
    sys.exit(0 if success else 1)
