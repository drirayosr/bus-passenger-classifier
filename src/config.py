"""
Configuration loader for the MLOps pipeline
Loads parameters from config.yaml
"""

import yaml
from pathlib import Path
from typing import Dict, Any


def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file

    Args:
        config_path: Path to config.yaml file

    Returns:
        Dictionary with configuration parameters

    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file is invalid
    """
    config_file = Path(config_path)

    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    try:
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
        return config
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in config file: {e}")


def get_data_paths(config: Dict[str, Any]) -> tuple:
    """
    Extract data paths from config

    Args:
        config: Configuration dictionary

    Returns:
        Tuple of (passengers_path, bus_path, processed_path)
    """
    data_config = config.get("data", {})
    return (
        data_config.get("passengers_path"),
        data_config.get("bus_path"),
        data_config.get("processed_output"),
    )


def get_preprocessing_params(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract preprocessing parameters from config

    Args:
        config: Configuration dictionary

    Returns:
        Dictionary with preprocessing parameters
    """
    return config.get("preprocessing", {})


def get_model_params(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract model parameters from config

    Args:
        config: Configuration dictionary

    Returns:
        Dictionary with model parameters
    """
    return config.get("feature_engineering", {})


def get_mlflow_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract MLflow configuration from config

    Args:
        config: Configuration dictionary

    Returns:
        Dictionary with MLflow settings
    """
    return config.get("mlflow", {})


# Example usage
if __name__ == "__main__":
    config = load_config()
    print("Configuration loaded successfully!")
    print(f"Passengers path: {config['data']['passengers_path']}")
    print(f"AOI buffer: {config['preprocessing']['aoi_buffer_m']}m")
    print(f"PCA components: {config['feature_engineering']['pca_n_components']}")
