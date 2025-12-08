import csv
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
CSV_FILE = RESULTS / "xtb_gaps_full.csv"

def extract_from_file(filepath: Path):
    """
    Extrae HOMO, LUMO y GAP (eV) desde un archivo de salida de xTB
    usando:
      - la línea 'HOMO-LUMO GAP' (para gap)
      - la tabla de orbitales (para HOMO y LUMO)
    Devuelve (HOMO_eV, LUMO_eV, GAP_eV)
    """
    homo = None
    lumo = None
    gap = None
    mos = []  # (occ, energy_eV)

    # patrón típico de tabla de orbitales:
    #  index  occ      E(Ha)        E(eV)
    mo_line = re.compile(
        r"^\s*\d+\s+([0-9.]+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)"
    )

    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            up = line.upper()

            # GAP
            if "HOMO-LUMO GAP" in up:
                parts = line.split()
                for i, p in enumerate(parts):
                    if "EV" in p.upper() and i > 0:
                        try:
                            gap = float(parts[i-1])
                        except ValueError:
                            pass

            # Tabla de MOs
            m = mo_line.match(line)
            if m:
                try:
                    occ = float(m.group(1))
                    e_ev = float(m.group(3))
                    mos.append((occ, e_ev))
                except ValueError:
                    pass

    # Si hay tabla de MOs, calculamos HOMO y LUMO
    if mos:
        mos_sorted = sorted(mos, key=lambda x: x[1])  # por energía
        occupied = [e for occ, e in mos_sorted if occ > 1e-3]
        virtual  = [e for occ, e in mos_sorted if occ < 1e-3]

        if occupied:
            homo_calc = max(occupied)
        else:
            homo_calc = None

        lumo_calc = None
        if homo_calc is not None and virtual:
            # primer virtual por encima del HOMO
            for e in virtual:
                if e > homo_calc:
                    lumo_calc = e
                    break
            # si no encontramos, tomamos el más bajo virtual
            if lumo_calc is None:
                lumo_calc = min(virtual)

        # sólo si no estaban ya definidos por otra vía
        if homo is None:
            homo = homo_calc
        if lumo is None:
            lumo = lumo_calc

        # si no había gap, y sí HOMO/LUMO, lo calculamos
        if gap is None and (homo is not None) and (lumo is not None):
            gap = lumo - homo

    return homo, lumo, gap


def main():
    rows = []

    for subdir in sorted(RESULTS.iterdir()):
        if not subdir.is_dir():
            continue

        # el nombre del directorio coincide con el stem del xyz
        nombre_xyz = subdir.name + ".xyz"

        # buscar outputs en orden de preferencia
        candidates = [
            subdir / "xtb_sp.out",
            subdir / "xtb_opt.out",
            subdir / "xtbopt.log",
        ]
        filepath = None
        for c in candidates:
            if c.exists():
                filepath = c
                break

        if filepath is None:
            print(f"⚠ No hay output que leer en {subdir}")
            continue

        homo, lumo, gap = extract_from_file(filepath)
        print(f"{nombre_xyz}: HOMO={homo}, LUMO={lumo}, GAP={gap}")

        rows.append({
            "archivo": nombre_xyz,
            "HOMO_eV": homo,
            "LUMO_eV": lumo,
            "GAP_Ev": gap,
        })

    if rows:
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

        print(f"\n📄 Resultados guardados en {CSV_FILE}")
    else:
        print("⚠ No se extrajo nada; revisa que haya outputs de xTB en 'results/'.")


if __name__ == "__main__":
    main()
