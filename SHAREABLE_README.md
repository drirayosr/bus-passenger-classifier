# Bus Passenger Classification - Shareable Version

This repository contains a clean, ready-to-share version of the Bus Passenger Classification MLOps project. It includes all necessary code, configuration, and documentation for easy setup and reproducibility. Large, sensitive, or temporary files are excluded.

## Included
- All source code (in `src/`, `api/`, `dashboard/`)
- Main configuration (`config/config.yaml`)
- Sample data: `bus.csv`, `passengers.csv`, and `quick_tuning_results.csv`
- Jupyter notebook: `AAU_Worshop_whosOnBus.ipynb`
- Modular requirements (`requirements/`)
- Main README and documentation (`README.md`, `docs/`, `report/`)
- CI/CD configuration (`.github/workflows/ci.yml`)
- Docker setup (`Dockerfile`, `docker-compose.yml`)
- Prefect, MLflow, and DVC configuration (excluding large data)
- Tests (`tests/`)

## Excluded
- Large datasets (see `data/` for structure, but not included)
- Model artifacts and experiment logs (`models/`, `mlruns/`, `predictions/`)
- Temporary, cache, and environment files (`venv/`, `__pycache__/`, `.pytest_cache/`, etc.)
- Any files listed in `.gitignore`

## Quick Start
See the main `README.md` for setup and usage instructions.

---

**To share this project:**
1. Ensure your local repository is clean: `git status` should show no uncommitted changes.
2. Push to a new GitHub repository.
3. Share the repository link with your professor.

---

For any issues, see the documentation in `docs/` or open an issue in your GitHub repository.
