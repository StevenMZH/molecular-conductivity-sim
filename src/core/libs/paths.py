from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DATASET_DIR = ROOT / "dataset"
RESULTS_DIR = ROOT / "results"
PLOTS_DIR = ROOT / "plots"

RESULTS_DIR.mkdir(exist_ok=True)
PLOTS_DIR.mkdir(exist_ok=True)

