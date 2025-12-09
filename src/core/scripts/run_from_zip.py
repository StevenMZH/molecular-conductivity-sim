import sys
import zipfile
import shutil
import subprocess
from pathlib import Path

# === RUTAS BÁSICAS DEL PROYECTO ===
ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "dataset"
RESULTS = ROOT / "results"
PLOTS = ROOT / "plots"
TMP_ROOT = ROOT / "tmp_zip"          # carpeta temporal para descomprimir
ZIP = ROOT / "dataset2.zip"

# Nombres de los otros scripts (ajusta si usas otros nombres)
SCRIPT_MAPPER    = ROOT / "scripts" / "mapper.py"
SCRIPT_NORMALIZE = ROOT / "scripts" / "normalizer.py"
SCRIPT_ANALYZE   = ROOT / "scripts" / "analyze_gaps.py"


def clean_dir_for_run():
    """Limpia dataset/, results/ y plots/ para un nuevo run."""
    DATASET.mkdir(exist_ok=True)
    RESULTS.mkdir(exist_ok=True)
    PLOTS.mkdir(exist_ok=True)

    # borrar sólo .xyz en dataset
    for f in DATASET.glob("*.xyz"):
        f.unlink()

    # borrar subcarpetas y csvs previos en results
    for item in RESULTS.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        elif item.suffix.lower() in {".csv", ".txt"}:
            item.unlink()

    # borrar plots anteriores
    for img in PLOTS.glob("*"):
        if img.is_file():
            img.unlink()


def extract_zip_to_tmp(zip_path: Path) -> Path:
    """
    Descomprime el zip en una carpeta temporal dentro de tmp_zip/<nombre_zip>/.
    Devuelve la ruta a esa carpeta.
    """
    tmp_dir = TMP_ROOT / zip_path.stem
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(tmp_dir)

    return tmp_dir


def copy_xyz_from_tmp_to_dataset(tmp_dir: Path):
    """
    Busca recursivamente todos los .xyz en tmp_dir y los copia a dataset/.
    """
    count = 0
    for xyz in tmp_dir.rglob("*.xyz"):
        dest = DATASET / xyz.name
        shutil.copy2(xyz, dest)
        count += 1
    print(f"✅ Copiados {count} archivos .xyz a {DATASET}")
    if count == 0:
        print("⚠ No se encontraron .xyz en el zip. ¿Estructura correcta?")


def run_script(script_path: Path):
    """
    Ejecuta un script de Python usando el mismo intérprete actual.
    """
    print(f"\n▶ Ejecutando: {script_path}")
    subprocess.run([sys.executable, str(script_path)], check=True)


def main():

    zip_path = ZIP
    if not zip_path.exists():
        print(f"⚠ El archivo zip no existe: {zip_path}")
        sys.exit(1)

    print(f"=== Pipeline desde ZIP ===")
    print(f"Zip de entrada: {zip_path}")

    # 1) limpiar carpetas de trabajo
    clean_dir_for_run()

    # 2) descomprimir zip en tmp_zip/<nombre>/
    tmp_dir = extract_zip_to_tmp(zip_path)
    print(f"Descomprimido en: {tmp_dir}")

    # 3) copiar todos los .xyz a dataset/
    copy_xyz_from_tmp_to_dataset(tmp_dir)

    # 4) ejecutar mapper, normalizer y análisis
    run_script(SCRIPT_MAPPER)
    run_script(SCRIPT_NORMALIZE)
    run_script(SCRIPT_ANALYZE)

    print("\n✅ Pipeline completado.")


if __name__ == "__main__":
    main()
