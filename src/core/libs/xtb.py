# libs/xtb_io.py
from pathlib import Path
import subprocess
import re

def run_xtb_opt(xyz: Path, outdir: Path, nprocs: int = 4) -> None:
    """
    Optimización geométrica con xTB.
    Guarda la salida en xtb_opt.out
    """
    outdir.mkdir(exist_ok=True)
    cmd = ["xtb", str(xyz), "--opt", "--parallel", str(nprocs)]
    print(f"  -> Ejecutando: {' '.join(cmd)}  (cwd={outdir})")
    with open(outdir / "xtb_opt.out", "w", encoding="utf-8", errors="ignore") as f:
        subprocess.run(cmd, cwd=outdir, stdout=f, stderr=f)


def run_xtb_sp(xyzopt: Path, outdir: Path) -> None:
    """
    Single point sobre la geometría optimizada.
    Guarda la salida en xtb_sp.out
    """
    cmd = ["xtb", str(xyzopt), "--sp"]
    print(f"  -> Ejecutando: {' '.join(cmd)}  (cwd={outdir})")
    with open(outdir / "xtb_sp.out", "w", encoding="utf-8", errors="ignore") as f:
        subprocess.run(cmd, cwd=outdir, stdout=f, stderr=f)


def extract_levels_from_output(filepath: Path):
    """
    Extrae HOMO, LUMO y GAP (eV) desde un output de xTB.
    Usa:
      - línea 'HOMO-LUMO GAP'
      - tabla de MO para HOMO/LUMO si hace falta.
    """
    homo = None
    lumo = None
    gap = None
    mos = []

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

            # Tabla de MO
            m = mo_line.match(line)
            if m:
                try:
                    occ = float(m.group(1))
                    e_ev = float(m.group(3))
                    mos.append((occ, e_ev))
                except ValueError:
                    pass

    if mos:
        mos_sorted = sorted(mos, key=lambda x: x[1])
        occupied = [e for occ, e in mos_sorted if occ > 1e-3]
        virtual  = [e for occ, e in mos_sorted if occ < 1e-3]

        homo_calc = max(occupied) if occupied else None
        lumo_calc = None
        if homo_calc is not None and virtual:
            for e in virtual:
                if e > homo_calc:
                    lumo_calc = e
                    break
            if lumo_calc is None:
                lumo_calc = min(virtual)

        if homo is None:
            homo = homo_calc
        if lumo is None:
            lumo = lumo_calc
        if gap is None and homo is not None and lumo is not None:
            gap = lumo - homo

    return homo, lumo, gap


def extract_levels_from_dir(outdir: Path):
    """
    Busca xtb_sp.out / xtb_opt.out / xtbopt.log dentro de un directorio
    y llama a extract_levels_from_output.
    """
    candidates = [
        outdir / "xtb_sp.out",
        outdir / "xtb_opt.out",
        outdir / "xtbopt.log",
    ]
    filepath = next((c for c in candidates if c.exists()), None)
    if filepath is None:
        print(f"  ⚠ No se encontró ningún output en {outdir}")
        return None, None, None

    return extract_levels_from_output(filepath)
