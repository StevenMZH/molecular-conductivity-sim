# scripts/analyze_gaps.py
import sys
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

from libs.paths import RESULTS_DIR, PLOTS_DIR, STRUCT_CSV, LEVELS_CSV


def main():
    if not STRUCT_CSV.exists() or not LEVELS_CSV.exists():
        print("Faltan structures.csv o xtb_levels.csv. Ejecuta mapper y normalizer primero.")
        return

    df_structs = pd.read_csv(STRUCT_CSV)
    df_levels  = pd.read_csv(LEVELS_CSV)

    df = df_structs.merge(df_levels, on="id", how="inner")
    out_csv = RESULTS_DIR / "xtb_gaps_parsed.csv"
    df.to_csv(out_csv, index=False, encoding="utf-8")
    print(f"Dataset completo guardado en {out_csv}")

    # === Plot 1: Gap vs % dopaje (por dopante) ===
    plt.figure(figsize=(8, 6))
    for dopant, sub in df.groupby("dopant"):
        if dopant == "pure":
            continue
        plt.scatter(sub["percent"], sub["GAP_eV"], label=dopant, alpha=0.8)
    plt.xlabel("% dopaje")
    plt.ylabel("Gap (eV)")
    plt.title("Gap electrónico vs % de dopaje (xTB)")
    plt.legend(title="Dopante")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "gap_vs_percent_por_dopante.png", dpi=300)
    plt.close()

    # === Plot 2: Gap vs tamaño por dopante ===
    plt.figure(figsize=(8, 6))
    for dopant, sub in df.groupby("dopant"):
        sub_sorted = sub.sort_values("size_nm")
        plt.plot(sub_sorted["size_nm"], sub_sorted["GAP_eV"],
                 marker="o", linestyle="-", alpha=0.8, label=dopant)
    plt.xlabel("Tamaño del flake (nm)")
    plt.ylabel("Gap (eV)")
    plt.title("Gap electrónico vs tamaño del flake, por dopante")
    plt.legend(title="Dopante")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "gap_vs_size_por_dopante.png", dpi=300)
    plt.close()

    # === Plot 3: solo grafeno puro ===
    df_pure = df[df["dopant"] == "pure"].sort_values("size_nm")
    if not df_pure.empty:
        plt.figure(figsize=(6, 4))
        plt.plot(df_pure["size_nm"], df_pure["GAP_eV"], marker="o")
        plt.xlabel("Tamaño del flake (nm)")
        plt.ylabel("Gap (eV)")
        plt.title("Grafeno puro: Gap vs tamaño (xTB)")
        plt.tight_layout()
        plt.savefig(PLOTS_DIR / "gap_vs_size_pure.png", dpi=300)
        plt.close()


if __name__ == "__main__":
    main()
