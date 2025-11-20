"""
Model Registry Manager CLI
Command-line tool for managing MLflow model registry
"""
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)

import argparse
from src.model_registry import ModelRegistry


def main():
    parser = argparse.ArgumentParser(description="Manage MLflow Model Registry")
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Register command
    register_parser = subparsers.add_parser('register', help='Register latest model')
    register_parser.add_argument('--run-id', type=str, help='Specific run ID to register')
    register_parser.add_argument('--name', type=str, default='bus-passenger-classifier',
                                help='Model name')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all registered models')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Get model information')
    info_parser.add_argument('--name', type=str, required=True, help='Model name')
    info_parser.add_argument('--version', type=int, help='Model version')
    info_parser.add_argument('--stage', type=str, choices=['Staging', 'Production', 'Archived'],
                            help='Model stage')
    
    # Promote command
    promote_parser = subparsers.add_parser('promote', help='Promote model to stage')
    promote_parser.add_argument('--name', type=str, default='bus-passenger-classifier',
                               help='Model name')
    promote_parser.add_argument('--version', type=int, required=True, help='Model version')
    promote_parser.add_argument('--stage', type=str, required=True,
                               choices=['None', 'Staging', 'Production', 'Archived'],
                               help='Target stage')
    
    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Compare two model versions')
    compare_parser.add_argument('--name', type=str, default='bus-passenger-classifier',
                               help='Model name')
    compare_parser.add_argument('--v1', type=int, required=True, help='First version')
    compare_parser.add_argument('--v2', type=int, required=True, help='Second version')
    
    # Load command
    load_parser = subparsers.add_parser('load', help='Load production model')
    load_parser.add_argument('--name', type=str, default='bus-passenger-classifier',
                            help='Model name')
    
    args = parser.parse_args()
    
    registry = ModelRegistry()
    
    if args.command == 'register':
        if args.run_id:
            registry.register_model(args.run_id, args.name)
        else:
            # Register latest
            from src.model_registry import register_latest_model
            register_latest_model()
    
    elif args.command == 'list':
        registry.list_registered_models()
    
    elif args.command == 'info':
        registry.get_model_info(args.name, version=args.version, stage=args.stage)
    
    elif args.command == 'promote':
        registry.promote_model(args.name, args.version, args.stage)
    
    elif args.command == 'compare':
        registry.compare_models(args.name, args.v1, args.v2)
    
    elif args.command == 'load':
        model = registry.load_production_model(args.name)
        if model:
            print(f"\n[INFO] Model type: {type(model)}")
            print(f"[INFO] Model has {len(model.steps)} steps")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
