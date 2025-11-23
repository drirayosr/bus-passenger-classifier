"""
Model Registry with MLflow
Register, version, and manage trained models
"""

import warnings

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient
import joblib
import os
from datetime import datetime
import json


class ModelRegistry:
    """Manage models in MLflow Registry"""

    def __init__(self, tracking_uri="mlruns"):
        self.tracking_uri = tracking_uri
        mlflow.set_tracking_uri(tracking_uri)
        self.client = MlflowClient()

    def register_model(self, run_id, model_name="bus-passenger-classifier"):
        """
        Register a model from an MLflow run

        Args:
            run_id: MLflow run ID containing the model
            model_name: Name for the registered model

        Returns:
            ModelVersion object
        """
        print(f"\n[*] Registering model from run: {run_id}")

        # Register the model
        model_uri = f"runs:/{run_id}/model"

        try:
            model_version = mlflow.register_model(model_uri, model_name)
            print(f"[OK] Model registered: {model_name}")
            print(f"    Version: {model_version.version}")
            print(f"    Status: {model_version.status}")
            return model_version
        except Exception as e:
            print(f"[ERROR] Failed to register model: {e}")
            return None

    def get_latest_run(self, experiment_name="bus_passenger_classification"):
        """Get the most recent run from an experiment"""
        experiment = mlflow.get_experiment_by_name(experiment_name)
        if not experiment:
            print(f"[ERROR] Experiment '{experiment_name}' not found")
            return None

        runs = mlflow.search_runs(
            experiment_ids=[experiment.experiment_id],
            order_by=["start_time DESC"],
            max_results=1,
        )

        if len(runs) == 0:
            print(f"[ERROR] No runs found in experiment '{experiment_name}'")
            return None

        return runs.iloc[0]

    def promote_model(self, model_name, version, stage):
        """
        Promote a model version to a specific stage

        Args:
            model_name: Name of the registered model
            version: Version number to promote
            stage: 'Staging', 'Production', or 'Archived'
        """
        valid_stages = ["None", "Staging", "Production", "Archived"]
        if stage not in valid_stages:
            print(f"[ERROR] Invalid stage. Must be one of: {valid_stages}")
            return False

        print(f"\n[*] Promoting {model_name} v{version} to {stage}")

        try:
            self.client.transition_model_version_stage(
                name=model_name,
                version=version,
                stage=stage,
                archive_existing_versions=(stage == "Production"),
            )
            print(f"[OK] Model promoted to {stage}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to promote model: {e}")
            return False

    def list_registered_models(self):
        """List all registered models"""
        print("\n" + "=" * 60)
        print("Registered Models")
        print("=" * 60)

        models = self.client.search_registered_models()

        if not models:
            print("No registered models found.")
            return []

        for model in models:
            print(f"\nModel: {model.name}")
            print(f"  Description: {model.description or 'N/A'}")
            print(f"  Latest Versions:")

            for version in model.latest_versions:
                print(f"    v{version.version} - Stage: {version.current_stage}")
                print(f"              Status: {version.status}")
                print(f"              Run ID: {version.run_id}")

        return models

    def get_model_info(self, model_name, version=None, stage=None):
        """
        Get information about a registered model

        Args:
            model_name: Name of the model
            version: Specific version number (optional)
            stage: Stage name (e.g., 'Production') (optional)
        """
        try:
            if version:
                model_version = self.client.get_model_version(model_name, version)
                self._print_model_version(model_version)
                return model_version
            elif stage:
                versions = self.client.get_latest_versions(model_name, stages=[stage])
                if versions:
                    self._print_model_version(versions[0])
                    return versions[0]
                else:
                    print(f"[WARNING] No model found in {stage} stage")
                    return None
            else:
                # Get latest version
                versions = self.client.get_latest_versions(model_name)
                if versions:
                    self._print_model_version(versions[0])
                    return versions[0]
                else:
                    print(f"[WARNING] No versions found for {model_name}")
                    return None
        except Exception as e:
            print(f"[ERROR] Failed to get model info: {e}")
            return None

    def _print_model_version(self, model_version):
        """Print model version details"""
        print(f"\nModel: {model_version.name}")
        print(f"  Version: {model_version.version}")
        print(f"  Stage: {model_version.current_stage}")
        print(f"  Status: {model_version.status}")
        print(f"  Run ID: {model_version.run_id}")
        print(f"  Source: {model_version.source}")

    def load_production_model(self, model_name="bus-passenger-classifier"):
        """Load the production model"""
        print(f"\n[*] Loading production model: {model_name}")

        try:
            model_uri = f"models:/{model_name}/Production"
            model = mlflow.sklearn.load_model(model_uri)
            print(f"[OK] Production model loaded")
            return model
        except Exception as e:
            print(f"[ERROR] Failed to load production model: {e}")
            print("[INFO] Trying to load latest version instead...")

            try:
                model_uri = f"models:/{model_name}/latest"
                model = mlflow.sklearn.load_model(model_uri)
                print(f"[OK] Latest model loaded")
                return model
            except Exception as e2:
                print(f"[ERROR] Failed to load latest model: {e2}")
                return None

    def compare_models(self, model_name, version1, version2):
        """Compare metrics between two model versions"""
        print(f"\n" + "=" * 60)
        print(f"Comparing {model_name} v{version1} vs v{version2}")
        print("=" * 60)

        try:
            mv1 = self.client.get_model_version(model_name, version1)
            mv2 = self.client.get_model_version(model_name, version2)

            # Get run metrics
            run1 = self.client.get_run(mv1.run_id)
            run2 = self.client.get_run(mv2.run_id)

            print(f"\nVersion {version1} (Stage: {mv1.current_stage}):")
            self._print_metrics(run1.data.metrics)

            print(f"\nVersion {version2} (Stage: {mv2.current_stage}):")
            self._print_metrics(run2.data.metrics)

            # Compare key metrics
            print("\nComparison:")
            for metric in ["f1_score", "accuracy", "precision_out", "recall_out"]:
                if metric in run1.data.metrics and metric in run2.data.metrics:
                    v1_val = run1.data.metrics[metric]
                    v2_val = run2.data.metrics[metric]
                    diff = v2_val - v1_val
                    symbol = "↑" if diff > 0 else "↓" if diff < 0 else "="
                    print(
                        f"  {metric:20s}: {v1_val:.4f} vs {v2_val:.4f} ({symbol} {abs(diff):.4f})"
                    )

        except Exception as e:
            print(f"[ERROR] Failed to compare models: {e}")

    def _print_metrics(self, metrics):
        """Print metrics dictionary"""
        for key, value in sorted(metrics.items()):
            print(f"  {key:20s}: {value:.4f}")


def register_latest_model():
    """Register the most recent training run"""
    registry = ModelRegistry()

    # Get latest run
    print("[*] Finding latest training run...")
    latest_run = registry.get_latest_run()

    if latest_run is None:
        print("[ERROR] No training runs found. Please run training first:")
        print("  python -m src.train_mlflow")
        return

    print(f"[OK] Found run: {latest_run['run_id']}")
    print(f"    F1 Score: {latest_run['metrics.f1_score']:.4f}")
    print(f"    Accuracy: {latest_run['metrics.accuracy']:.4f}")
    print(f"    Started: {latest_run['start_time']}")

    # Register the model
    model_version = registry.register_model(
        run_id=latest_run["run_id"], model_name="bus-passenger-classifier"
    )

    if model_version:
        print("\n[*] Model registered successfully!")
        print(f"    Name: bus-passenger-classifier")
        print(f"    Version: {model_version.version}")
        print("\nNext steps:")
        print("  1. Review the model in MLflow UI")
        print("  2. Promote to Staging:")
        print(
            f"     python registry_manager.py --promote {model_version.version} --stage Staging"
        )
        print("  3. After validation, promote to Production:")
        print(
            f"     python registry_manager.py --promote {model_version.version} --stage Production"
        )


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--register":
        register_latest_model()
    else:
        # Interactive mode
        registry = ModelRegistry()
        registry.list_registered_models()
