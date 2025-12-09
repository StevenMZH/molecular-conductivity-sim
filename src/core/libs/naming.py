# libs/naming.py
def parse_structure_name(filename: str):
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
