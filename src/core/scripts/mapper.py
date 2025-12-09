# scripts/map_dataset.py
import sys
from pathlib import Path
import csv

# asegurar que podemos importar libs/*
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from libs.paths import DATASET_DIR, RESULTS_DIR
from libs.naming import parse_structure_name


def main():
    csv_path = RESULTS_DIR / "structures.csv"

    xyz_files = sorted(DATASET_DIR.glob("*.xyz"))
    if not xyz_files:
        print(f"⚠ No se encontraron .xyz en {DATASET_DIR}")
        return

    rows = []
    for xyz in xyz_files:
        size_nm, dopant, dopant_count, percent = parse_structure_name(xyz.name)
        rows.append({
            "id": xyz.stem,
            "filename": xyz.name,
            "path": str(xyz),
            "size_nm": size_nm,
            "dopant": dopant,
            "dopant_count": dopant_count,
            "percent": percent,
        })

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["id", "filename", "path", "size_nm",
                        "dopant", "dopant_count", "percent"]
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"📄 Mapa de estructuras guardado en {csv_path}")


if __name__ == "__main__":
    main()
