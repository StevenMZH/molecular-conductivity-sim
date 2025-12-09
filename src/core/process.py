from pathlib import Path
import qcelemental as qcel
import tblite.interface as tb
import io
import contextlib

def process_file(file: Path):
    molecule = qcel.models.Molecule.from_file(str(file))

    xtb = tb.Calculator(method="GFN2-xTB", numbers=molecule.atomic_numbers, positions=molecule.geometry)

    # Capture stdout so it doesnt show on the console
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        result = xtb.singlepoint()
        
    return result
