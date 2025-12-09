
def parse_structure_name(filename: str):
    """
    Parsea nombres de estructuras del tipo:
      1.5nm-10Bdoped-7percent.xyz
      1nm-Bdoped-1.5percent.xyz
      2nm-0pure-0percent.xyz
      weird_name.xyz    (soportado)

    Devuelve SIEMPRE:
      size_nm, dopant, dopant_count, percent

    Con defaults seguros:
      size_nm = None
      dopant = "unknown"
      dopant_count = 0
      percent = 0.0
    """
    # quitar extensión
    name = filename.replace(".xyz", "")
    parts = name.split("-")

    # === DEFAULTS ===
    size_nm = None
    dopant = "unknown"
    dopant_count = 0
    percent = 0.0

    # --- SIZE ---
    try:
        size_part = parts[0]
        if "nm" in size_part:
            size_nm = float(size_part.replace("nm", ""))
    except Exception:
        pass

    # --- DOPANT ---
    dopant_token = None
    for p in parts[1:]:
        if "doped" in p.lower() or "pure" in p.lower():
            dopant_token = p
            break

    if dopant_token:
        if "pure" in dopant_token.lower():
            dopant = "pure"
            dopant_count = 0
        else:
            core = dopant_token.replace("doped", "")
            letters = "".join(ch for ch in core if ch.isalpha())
            digits  = "".join(ch for ch in core if ch.isdigit())
            if letters:
                dopant = letters
            if digits:
                dopant_count = int(digits)
            elif dopant != "pure":
                dopant_count = 1

    # --- PERCENT ---
    percent_token = None
    for p in parts:
        if "percent" in p.lower():
            percent_token = p
            break

    if percent_token:
        try:
            percent_str = (
                percent_token.lower()
                .replace("percent", "")
                .replace("--", "-")
                .strip()
            )
            if percent_str:
                percent = float(percent_str)
        except Exception:
            pass

    return size_nm, dopant, dopant_count, percent
