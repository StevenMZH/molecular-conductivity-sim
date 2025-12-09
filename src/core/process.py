from pathlib import Path
import qcelemental as qcel
import tblite.interface as tb


def process_file(file: Path):

    molecule = qcel.models.Molecule.from_file(str(file))

    xtb = tb.Calculator(method="GFN2-xTB", numbers=molecule.atomic_numbers, positions=molecule.geometry)

    return xtb.singlepoint()

