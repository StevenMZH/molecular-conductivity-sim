from zipfile import ZipFile
import os
import csv
import pathlib
from typing import List



def unzip_and_getfilepaths(zip_file: pathlib.Path, extract_to: pathlib.Path) -> List[pathlib.Path]:
    """
    Descomprime el archivo y devuelve una lista SOLO con las rutas de los archivos encontrados,
    filtrando carpetas para evitar errores de permisos.
    """
    extracted_files = []

    extract_to.mkdir(parents=True, exist_ok=True)

    try:
        with ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
            
            for file_info in zip_ref.infolist():
                # Solo queremos lo que NO sea carpeta.
                if not file_info.is_dir():
                    full_path = extract_to / file_info.filename
                    extracted_files.append(full_path)
                    
    except Exception as e:
        print(f"Error crítico al descomprimir: {e}")
        return []

    return extracted_files

def create_csv(data: List[List[str]], output_path: pathlib.Path) -> None:
    """
    Creates a CSV file from the given data at the specified output path.
    Each item in data represents a row in the CSV file.
    """

    # write data to csv
    with open(output_path, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(data)