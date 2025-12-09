import zipfile
import shutil
from pathlib import Path

from libs.paths import ROOT, DATASET_DIR, RESULTS_DIR, PLOTS_DIR, TMP_ROOT, DATASET_ZIP
from scripts.mapper import main as run_mapper
from scripts.normalizer import main as run_normalizer
from scripts.analyze_gaps import main as run_analyze


def clean_dirs():
    DATASET_DIR.mkdir(exist_ok=True)
    RESULTS_DIR.mkdir(exist_ok=True)
    PLOTS_DIR.mkdir(exist_ok=True)

    for f in DATASET_DIR.glob("*.xyz"):
        f.unlink()

    for item in RESULTS_DIR.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        elif item.suffix.lower() in {".csv", ".txt"}:
            item.unlink()

    for img in PLOTS_DIR.glob("*"):
        if img.is_file():
            img.unlink()


def extract_zip_to_tmp(DATASET_ZIP: Path) -> Path:
    tmp_dir = TMP_ROOT / DATASET_ZIP.stem
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(DATASET_ZIP, "r") as zf:
        zf.extractall(tmp_dir)

    return tmp_dir


def copy_xyz_from_tmp_to_dataset(tmp_dir: Path):
    count = 0
    for xyz in tmp_dir.rglob("*.xyz"):
        shutil.copy2(xyz, DATASET_DIR / xyz.name)
        count += 1
    print(f"Copiados {count} archivos .xyz a {DATASET_DIR}")
    if count == 0:
        print("No se encontraron .xyz en el zip. ¿Estructura correcta?")


def process_zip():
    if not DATASET_ZIP.exists():
        print(f"El archivo zip no existe: {DATASET_ZIP}")
        return

    print("=== Pipeline desde ZIP ===")
    print(f"Zip de entrada: {DATASET_ZIP}")

    clean_dirs()

    tmp_dir = extract_zip_to_tmp(DATASET_ZIP)
    print(f"Descomprimido en: {tmp_dir}")

    copy_xyz_from_tmp_to_dataset(tmp_dir)

    run_mapper()
    run_normalizer()
    run_analyze()

    print("\nPipeline completado.")
