"""
Run multiple MLflow experiments with different configurations
Systematically test different hyperparameters
"""

import mlflow
from train_mlflow import train_and_evaluate_with_mlflow
from config import load_config
import yaml


def run_experiment_grid():
    """Run experiments with different hyperparameter configurations"""

    print("=" * 60)
    print("Running MLflow Experiment Grid")
    print("=" * 60)

    # Define experiments to run
    experiments = [
        {
            "name": "baseline_min_cluster_1000",
            "hdbscan_min_cluster_size": 1000,
            "hdbscan_cluster_selection_epsilon": 0.0,
        },
        {
            "name": "optimized_min_cluster_300_eps_0.5",
            "hdbscan_min_cluster_size": 300,
            "hdbscan_cluster_selection_epsilon": 0.5,
        },
        {
            "name": "mid_min_cluster_500_eps_0.5",
            "hdbscan_min_cluster_size": 500,
            "hdbscan_cluster_selection_epsilon": 0.5,
        },
        {
            "name": "small_min_cluster_200_eps_0.0",
            "hdbscan_min_cluster_size": 200,
            "hdbscan_cluster_selection_epsilon": 0.0,
        },
    ]

    # Load base config
    base_config = load_config()

    results_summary = []

    for i, exp_config in enumerate(experiments, 1):
        print(f"\n{'#'*60}")
        print(f"Experiment {i}/{len(experiments)}: {exp_config['name']}")
        print(f"{'#'*60}")

        # Update config
        config = base_config.copy()
        config["feature_engineering"]["hdbscan_min_cluster_size"] = exp_config[
            "hdbscan_min_cluster_size"
        ]
        config["feature_engineering"]["hdbscan_cluster_selection_epsilon"] = exp_config[
            "hdbscan_cluster_selection_epsilon"
        ]

        # Save temporary config
        with open("config/config.yaml", "w") as f:
            yaml.dump(config, f)

        # Run experiment
        try:
            pipeline, results = train_and_evaluate_with_mlflow(
                experiment_name="bus_passenger_classification_grid",
                run_name=exp_config["name"],
            )

            if results:
                results_summary.append(
                    {
                        "name": exp_config["name"],
                        "f1_score": results["f1_score"],
                        "accuracy": results["accuracy"],
                        **exp_config,
                    }
                )
        except Exception as e:
            print(f"[ERROR] Experiment failed: {e}")
            continue

    # Print summary
    print("\n\n" + "=" * 60)
    print("EXPERIMENT GRID SUMMARY")
    print("=" * 60)
    print(f"\n{'Experiment':<45} {'F1 Score':<12} {'Accuracy':<12}")
    print("-" * 60)

    # Sort by F1 score
    results_summary.sort(key=lambda x: x["f1_score"], reverse=True)

    for result in results_summary:
        print(
            f"{result['name']:<45} {result['f1_score']:<12.4f} {result['accuracy']:<12.4f}"
        )

    print("\n" + "=" * 60)
    print("View detailed results in MLflow UI:")
    print("  python start_mlflow_ui.py")
    print("=" * 60)


if __name__ == "__main__":
    run_experiment_grid()
