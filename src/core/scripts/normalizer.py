# scripts/normalize_xtb.py
import sys
import csv
from pathlib import Path

from libs.paths import RESULTS_DIR, STRUCT_CSV, LEVELS_CSV
from libs.xtb import run_xtb_opt, run_xtb_sp, extract_levels_from_dir


def main():
    if not STRUCT_CSV.exists():
        print(f"No se encontró {STRUCT_CSV}. Ejecuta primero map_dataset.py")
        return

    rows = []
    with open(STRUCT_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        struct = list(reader)

    for s in struct:
        struct_id = s["id"]
        xyz_path = Path(s["path"])
        outdir = RESULTS_DIR / struct_id

        print(f"\nProcesando {xyz_path.name}")
        # 1. Optimizar
        run_xtb_opt(xyz_path, outdir)

        # 2. Single point con geometría optimizada
        xyz_opt = outdir / "xtbopt.xyz"
        if not xyz_opt.exists():
            print(f"  ⚠ No se encontró xtbopt.xyz en {outdir}, se omite.")
            continue

        run_xtb_sp(xyz_opt, outdir)

        # 3. Extraer niveles
        homo, lumo, gap = extract_levels_from_dir(outdir)
        print(f"  HOMO={homo}, LUMO={lumo}, GAP={gap}")

        rows.append({
            "id": struct_id,
            "HOMO_eV": homo,
            "LUMO_eV": lumo,
            "GAP_eV": gap,
        })

    if rows:
        with open(LEVELS_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f, fieldnames=["id", "HOMO_eV", "LUMO_eV", "GAP_eV"]
            )
            writer.writeheader()
            writer.writerows(rows)
        print(f"\nNiveles electrónicos guardados en {LEVELS_CSV}")
    else:
        print("⚠ No se generó ningún resultado.")


if __name__ == "__main__":
    main()
