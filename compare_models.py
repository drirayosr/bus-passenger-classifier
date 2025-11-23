"""
Model Comparison Summary
Compares HDBSCAN baseline vs Supervised Learning results
"""

import mlflow
import pandas as pd

print("=" * 80)
print("MODEL PERFORMANCE COMPARISON")
print("=" * 80)

# Get MLflow tracking URI
mlflow_uri = "http://localhost:5000"
mlflow.set_tracking_uri(mlflow_uri)

print(f"\nMLflow Tracking URI: {mlflow_uri}")
print("\nFetching experiment results...")

try:
    # Get HDBSCAN baseline experiments
    client = mlflow.tracking.MlflowClient()
    
    print("\n" + "=" * 80)
    print("1. HDBSCAN BASELINE (Unsupervised Clustering)")
    print("=" * 80)
    
    try:
        baseline_exp = client.get_experiment_by_name("bus_passenger_classification")
        if baseline_exp:
            baseline_runs = client.search_runs(
                experiment_ids=[baseline_exp.experiment_id],
                order_by=["metrics.f1_score DESC"],
                max_results=1
            )
            
            if baseline_runs:
                run = baseline_runs[0]
                print(f"\nBest HDBSCAN Run:")
                print(f"  Run ID: {run.info.run_id[:8]}...")
                print(f"  Accuracy:  {run.data.metrics.get('accuracy', 0):.4f} ({run.data.metrics.get('accuracy', 0)*100:.2f}%)")
                print(f"  F1-Score:  {run.data.metrics.get('f1_score', 0):.4f} ({run.data.metrics.get('f1_score', 0)*100:.2f}%)")
                print(f"  Precision: {run.data.metrics.get('precision', 0):.4f}")
                print(f"  Recall:    {run.data.metrics.get('recall', 0):.4f}")
                
                baseline_acc = run.data.metrics.get('accuracy', 0.682)
                baseline_f1 = run.data.metrics.get('f1_score', 0.596)
            else:
                print("\n  Using reported baseline:")
                print(f"  Accuracy:  0.682 (68.2%)")
                print(f"  F1-Score:  0.596 (59.6%)")
                baseline_acc = 0.682
                baseline_f1 = 0.596
        else:
            print("\n  Using reported baseline:")
            print(f"  Accuracy:  0.682 (68.2%)")
            print(f"  F1-Score:  0.596 (59.6%)")
            baseline_acc = 0.682
            baseline_f1 = 0.596
    except:
        print("\n  Using reported baseline:")
        print(f"  Accuracy:  0.682 (68.2%)")
        print(f"  F1-Score:  0.596 (59.6%)")
        baseline_acc = 0.682
        baseline_f1 = 0.596
    
    # Get supervised learning experiments
    print("\n" + "=" * 80)
    print("2. SUPERVISED LEARNING (Random Forest, Gradient Boosting, XGBoost)")
    print("=" * 80)
    
    supervised_results = []
    
    for model_name in ['random_forest', 'gradient_boosting', 'xgboost']:
        try:
            exp = client.get_experiment_by_name(f"supervised_learning_{model_name}")
            if exp:
                runs = client.search_runs(
                    experiment_ids=[exp.experiment_id],
                    order_by=["metrics.test_f1_score DESC"],
                    max_results=1
                )
                
                if runs:
                    run = runs[0]
                    result = {
                        'model': model_name.replace('_', ' ').title(),
                        'train_accuracy': run.data.metrics.get('train_accuracy', 0),
                        'test_accuracy': run.data.metrics.get('test_accuracy', 0),
                        'test_f1_score': run.data.metrics.get('test_f1_score', 0),
                        'run_id': run.info.run_id[:8]
                    }
                    supervised_results.append(result)
                    
                    print(f"\n{result['model']}:")
                    print(f"  Train Accuracy: {result['train_accuracy']:.4f} ({result['train_accuracy']*100:.2f}%)")
                    print(f"  Test Accuracy:  {result['test_accuracy']:.4f} ({result['test_accuracy']*100:.2f}%)")
                    print(f"  Test F1-Score:  {result['test_f1_score']:.4f} ({result['test_f1_score']*100:.2f}%)")
                    print(f"  Run ID: {result['run_id']}...")
        except Exception as e:
            print(f"\n{model_name.replace('_', ' ').title()}: No runs found")
    
    if supervised_results:
        # Find best supervised model
        best_supervised = max(supervised_results, key=lambda x: x['test_f1_score'])
        
        print("\n" + "=" * 80)
        print("3. BEST MODEL")
        print("=" * 80)
        print(f"\n🏆 {best_supervised['model']}")
        print(f"  Test Accuracy:  {best_supervised['test_accuracy']:.4f} ({best_supervised['test_accuracy']*100:.2f}%)")
        print(f"  Test F1-Score:  {best_supervised['test_f1_score']:.4f} ({best_supervised['test_f1_score']*100:.2f}%)")
        
        # Calculate improvement
        acc_improvement = ((best_supervised['test_accuracy'] - baseline_acc) / baseline_acc) * 100
        f1_improvement = ((best_supervised['test_f1_score'] - baseline_f1) / baseline_f1) * 100
        
        print("\n" + "=" * 80)
        print("4. IMPROVEMENT SUMMARY")
        print("=" * 80)
        
        print(f"\n{'Metric':<20} {'HDBSCAN':<15} {best_supervised['model']:<20} {'Improvement':<15}")
        print("-" * 80)
        print(f"{'Accuracy':<20} {baseline_acc:.4f} ({baseline_acc*100:.1f}%){'':<4} "
              f"{best_supervised['test_accuracy']:.4f} ({best_supervised['test_accuracy']*100:.1f}%){'':<4} "
              f"{acc_improvement:+.1f}%")
        print(f"{'F1-Score':<20} {baseline_f1:.4f} ({baseline_f1*100:.1f}%){'':<4} "
              f"{best_supervised['test_f1_score']:.4f} ({best_supervised['test_f1_score']*100:.1f}%){'':<4} "
              f"{f1_improvement:+.1f}%")
        
        print("\n" + "=" * 80)
        print("5. RECOMMENDATIONS")
        print("=" * 80)
        
        if best_supervised['test_f1_score'] > baseline_f1 + 0.05:  # 5% improvement
            print(f"\n✅ SWITCH TO {best_supervised['model'].upper()}")
            print(f"   The supervised model significantly outperforms HDBSCAN.")
            print(f"   F1-Score improvement: {f1_improvement:+.1f}%")
            print(f"\nNext steps:")
            print(f"1. Deploy the {best_supervised['model']} model to production")
            print(f"2. Update API to use: models/supervised/{best_supervised['model'].lower().replace(' ', '_')}_model.pkl")
            print(f"3. Update Prefect workflows to retrain supervised model")
            print(f"4. Monitor performance in production")
        else:
            print(f"\n⚠️  MARGINAL IMPROVEMENT")
            print(f"   Supervised model shows {f1_improvement:+.1f}% improvement.")
            print(f"   Consider:")
            print(f"   1. Further hyperparameter tuning")
            print(f"   2. Adding more features")
            print(f"   3. Ensemble methods (combine HDBSCAN + supervised)")
    else:
        print("\n❌ No supervised learning results found.")
        print("\nRun models with:")
        print("  python train_supervised.py compare")
    
    print("\n" + "=" * 80)
    print("View detailed results in MLflow:")
    print(f"  {mlflow_uri}")
    print("=" * 80)

except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nMake sure MLflow server is running:")
    print("  python start_mlflow_ui.py")
