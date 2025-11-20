import joblib

# Load latest MLflow results
r = joblib.load('models/results_mlflow_20251120_135259.joblib')

print('='*60)
print('MLFLOW TRAINING RESULTS')
print('='*60)
print(f'\nF1 Score: {r["f1_score"]:.4f}')
print(f'Accuracy: {r["accuracy"]:.4f}')
print(f'Samples: {r["n_samples"]:,}')
print(f'Features: {r["n_features"]}')

print('\nConfusion Matrix:')
cm = r['confusion_matrix']
print(f'                Predicted OUT  Predicted IN')
print(f'Actual OUT:        {cm[0][0]:6d}        {cm[0][1]:6d}')
print(f'Actual IN:         {cm[1][0]:6d}        {cm[1][1]:6d}')

print('\n' + '='*60)
print('Phase 2 MLflow Setup Complete!')
print('='*60)
print('\nNext: Install mlflow to view detailed UI')
print('  pip install mlflow')
print('  python start_mlflow_ui.py')
