import re
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"

# Cambia aquí si tu archivo se llama distinto
CSV_IN = RESULTS / "xtb_gaps_full.csv"
CSV_OUT = RESULTS / "xtb_gaps_parsed.csv"
PLOTS_DIR = ROOT / "plots"
PLOTS_DIR.mkdir(exist_ok=True)


def parse_name(filename: str):
    """
    Parsea nombres tipo:
      1.5nm-10Bdoped-7percent.xyz
      1nm-Bdoped-1.5percent.xyz
      1nm-Ndoped--1.5percent.xyz
      2nm-0pure-0percent.xyz

    Devuelve: size_nm, dopant, dopant_count, percent
    """
    name = filename.replace(".xyz", "")
    parts = name.split("-")

    # tamaño (ej: '1.5nm' -> 1.5)
    size_part = parts[0]
    size_nm = float(size_part.replace("nm", ""))

    # token que contiene 'doped' o 'pure'
    dopant_token = None
    for p in parts[1:]:
        if "doped" in p.lower() or "pure" in p.lower():
            dopant_token = p
            break

    percent_part = None
    for p in parts:
        if "percent" in p.lower():
            percent_part = p
            break

    # porcentaje
    percent_str = (
        percent_part.lower()
        .replace("percent", "")
        .replace("--", "-")
        .strip()
    )
    percent = float(percent_str)

    # caso grafeno puro
    if "pure" in dopant_token.lower():
        dopant = "pure"
        dopant_count = 0
    else:
        # ej: '10Bdoped' o 'Bdoped'
        core = dopant_token.replace("doped", "")
        letters = "".join(ch for ch in core if ch.isalpha())  # B, N, O, P, S
        digits = "".join(ch for ch in core if ch.isdigit())   # 10, 2, ...

        dopant = letters  # elemento dopante
        dopant_count = int(digits) if digits else 1

    return size_nm, dopant, dopant_count, percent


def main():
    df = pd.read_csv(CSV_IN)

    # parsear columnas nuevas
    sizes = []
    dopants = []
    counts = []
    percents = []

    for fname in df["archivo"]:
        size_nm, dopant, dopant_count, percent = parse_name(fname)
        sizes.append(size_nm)
        dopants.append(dopant)
        counts.append(dopant_count)
        percents.append(percent)

    df["size_nm"] = sizes
    df["dopant"] = dopants
    df["dopant_count"] = counts
    df["percent"] = percents

    # guardar versión enriquecida
    df.to_csv(CSV_OUT, index=False)
    print(f"Guardado CSV enriquecido en: {CSV_OUT}")

    # ====== PLOT 1: GAP vs % dopaje por dopante ======
    plt.figure(figsize=(8, 6))
    for dopant, sub in df.groupby("dopant"):
        if dopant == "pure":
            continue
        plt.scatter(sub["percent"], sub["GAP_Ev"], label=dopant, alpha=0.8)

    plt.xlabel("% dopaje")
    plt.ylabel("Gap (eV)")
    plt.title("Gap electrónico vs % de dopaje (xTB)")
    plt.legend(title="Dopante")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "gap_vs_percent_por_dopante.png", dpi=300)
    plt.close()
    print("Guardado: gap_vs_percent_por_dopante.png")

    # ====== PLOT 2: GAP vs tamaño para cada dopante ======
    plt.figure(figsize=(8, 6))
    for dopant, sub in df.groupby("dopant"):
        # ordenamos por tamaño
        sub_sorted = sub.sort_values("size_nm")
        plt.plot(sub_sorted["size_nm"], sub_sorted["GAP_Ev"],
                 marker="o", linestyle="-", alpha=0.8, label=dopant)

    plt.xlabel("Tamaño del flake (nm)")
    plt.ylabel("Gap (eV)")
    plt.title("Gap electrónico vs tamaño del flake, por dopante")
    plt.legend(title="Dopante")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "gap_vs_size_por_dopante.png", dpi=300)
    plt.close()
    print("Guardado: gap_vs_size_por_dopante.png")

    # ====== PLOT 3: Comparar solo sistemas puros (chequear tendencia con tamaño) ======
    df_pure = df[df["dopant"] == "pure"].sort_values("size_nm")
    if not df_pure.empty:
        plt.figure(figsize=(6, 4))
        plt.plot(df_pure["size_nm"], df_pure["GAP_Ev"],
                 marker="o", linestyle="-")
        plt.xlabel("Tamaño del flake (nm)")
        plt.ylabel("Gap (eV)")
        plt.title("Grafeno puro: Gap vs tamaño (xTB)")
        plt.tight_layout()
        plt.savefig(PLOTS_DIR / "gap_vs_size_pure.png", dpi=300)
        plt.close()
        print("Guardado: gap_vs_size_pure.png")


if __name__ == "__main__":
    main()
