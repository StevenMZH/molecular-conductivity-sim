"""
This screen shows the processing or already processed data, it could be the csv data generated, plots, etc.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QGridLayout, QTableView
from PySide6.QtCore import Qt
from src.core.helpers import unzip_and_getfilepaths
from typing import List
from pathlib import Path

import qcelemental as qcel 
import tblite.interface as tb


class ProcessScreen(QWidget):
    def __init__(self):
        super().__init__()

        self.extract_dir: Path | None = None
        self.files: List[Path] = []
        self.csv: Path | None = None

        self.init_ui()

    def init_ui(self):
        layout = QGridLayout()

        title = QLabel("Data Processing")
        title.setObjectName("Header")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title, 0, 0, 1, 2)

        # xyz files readed from the zip file
        table_label = QLabel("Extracted Files:")
        table_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(table_label, 1, 0)
        self.files_table = QTableView()
        layout.addWidget(self.files_table, 2, 0, 1, 2)

        # csv processed file


        self.setLayout(layout)

    def clear_data(self):
        # delete the unzipped directory
        if self.extract_dir and self.extract_dir.exists():
            for file in self.extract_dir.iterdir():
                file.unlink()
            self.extract_dir.rmdir()
        
        self.extract_dir = None
        self.files = []

    def load_zip_file(self, zip_path: Path):
        # unzip the file and get the file paths
        self.extract_dir = zip_path.parent / (zip_path.stem + "_extracted")
        self.extract_dir.mkdir(exist_ok=True)

        self.files = unzip_and_getfilepaths(zip_path, self.extract_dir)

    def process_zip_file(self, zip_path: Path):
        # clear previous data
        self.clear_data()

        # load new zip file
        self.load_zip_file(zip_path)

        # now that all the files are loaded lets process each one
        for file in self.files:
            pass
        
    def process_file(self, file: Path):
        ...