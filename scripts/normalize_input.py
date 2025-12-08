import os
from pathlib import Path
import subprocess
import csv

# === RUTAS BÁSICAS DEL PROYECTO ===
ROOT = Path(__file__).resolve().parent.parent
DATASET = ROOT / "dataset"       # aquí debes tener los .xyz de entrada
RESULTS = ROOT / "results"       # aquí se guardan subcarpetas y el CSV final
RESULTS.mkdir(exist_ok=True)

CSV_FILE = RESULTS / "xtb_gaps.csv"


# === FUNCIONES PARA CORRER XTB ===

def run_xtb_opt(xyz: Path, outdir: Path) -> None:
    """
    Optimización geométrica con xTB.
    Guarda toda la salida en xtb_opt.out
    """
    outdir.mkdir(exist_ok=True)
    cmd = [
        "xtb",
        str(xyz),
        "--opt",
        "--parallel", "4",
    ]
    print(f"  -> Ejecutando: {' '.join(cmd)}  (cwd={outdir})")
    with open(outdir / "xtb_opt.out", "w", encoding="utf-8", errors="ignore") as f:
        subprocess.run(cmd, cwd=outdir, stdout=f, stderr=f)


def run_xtb_singlepoint(xyzopt: Path, outdir: Path) -> None:
    """
    Single point sobre la geometría optimizada.
    Guarda la salida en xtb_sp.out
    """
    cmd = [
        "xtb",
        str(xyzopt),
        "--sp",
    ]
    print(f"  -> Ejecutando: {' '.join(cmd)}  (cwd={outdir})")
    with open(outdir / "xtb_sp.out", "w", encoding="utf-8", errors="ignore") as f:
        subprocess.run(cmd, cwd=outdir, stdout=f, stderr=f)


# === PARSEO DE HOMO / LUMO / GAP ===

def extract_homo_lumo(outdir: Path):
    """
    Extrae HOMO, LUMO y GAP (en eV) desde los outputs de xTB.
    Busca primero xtb_sp.out, luego xtb_opt.out, luego xtbopt.log.
    Devuelve (HOMO_eV, LUMO_eV, GAP_eV) o (None, None, None) si falla.
    """
    candidates = [
        outdir / "xtb_sp.out",    # singlepoint (preferido)
        outdir / "xtb_opt.out",   # optimización
        outdir / "xtbopt.log",    # último recurso
    ]

    filepath = None
    for c in candidates:
        if c.exists():
            filepath = c
            break

    if filepath is None:
        print(f"  ⚠ No se encontró xtb_sp.out / xtb_opt.out / xtbopt.log en {outdir}")
        return None, None, None

    homo = None
    lumo = None
    gap = None

    # 👇 AQUÍ VA EL ARREGLO IMPORTANTE
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            up = line.upper()

            # GAP
            if "HOMO-LUMO GAP" in up:
                parts = line.split()
                # típicamente: ... GAP :   1.234 eV
                for i, p in enumerate(parts):
                    if "EV" in p.upper() and i > 0:
                        try:
                            gap = float(parts[i - 1])
                        except ValueError:
                            pass

            # Línea de HOMO (evitamos la del GAP)
            if "HOMO-LUMO" in up:
                continue
            if "HOMO" in up and "EV" in up:
                parts = line.split()
                for i, p in enumerate(parts):
                    if "EV" in p.upper() and i > 0:
                        try:
                            homo = float(parts[i - 1])
                        except ValueError:
                            pass

            # Línea de LUMO
            if "LUMO" in up and "EV" in up and "HOMO-LUMO" not in up:
                parts = line.split()
                for i, p in enumerate(parts):
                    if "EV" in p.upper() and i > 0:
                        try:
                            lumo = float(parts[i - 1])
                        except ValueError:
                            pass

    return homo, lumo, gap


# === PROGRAMA PRINCIPAL ===

def main():
    xyz_files = sorted(DATASET.glob("*.xyz"))
    if not xyz_files:
        print(f"⚠ No se encontraron .xyz en {DATASET}")
        return

    rows = []

    for xyz in xyz_files:
        print(f"\nProcesando {xyz.name}")
        outdir = RESULTS / xyz.stem

        # 1. Optimización geométrica
        run_xtb_opt(xyz, outdir)

        # 2. Singlepoint sobre la geometría optimizada
        xyz_opt = outdir / "xtbopt.xyz"
        if not xyz_opt.exists():
            print(f"  ⚠ No se encontró xtbopt.xyz en {outdir}, se omite esta estructura.")
            continue

        run_xtb_singlepoint(xyz_opt, outdir)

        # 3. Extraer niveles electrónicos
        homo, lumo, gap = extract_homo_lumo(outdir)
        print(f"  HOMO = {homo} eV, LUMO = {lumo} eV, GAP = {gap} eV")

        rows.append({
            "archivo": xyz.name,
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
        print("\n⚠ No se generó ningún resultado; revisa los cálculos de xTB.")


if __name__ == "__main__":
    main()
