from pathlib import Path

# Project Root
ROOT = Path(__file__).resolve().parents[1]


# Inputs
TMP_ROOT = ROOT / "tmp_zip"
DATASET_ZIP = ROOT / "dataset2.zip"


# Dataset
DATASET_DIR = ROOT / "dataset"

# Results
RESULTS_DIR = ROOT / "results"
RESULTS_DIR.mkdir(exist_ok=True)
STRUCT_CSV = RESULTS_DIR / "structures.csv"
LEVELS_CSV  = RESULTS_DIR / "xtb_levels.csv"

# Plots
PLOTS_DIR = ROOT / "plots"
PLOTS_DIR.mkdir(exist_ok=True)


