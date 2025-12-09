from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QTableView, QHeaderView, QAbstractItemView)
from PySide6.QtGui import QStandardItemModel, QStandardItem, QColor
from PySide6.QtCore import Qt, QThread, Signal, Slot
from typing import List
from pathlib import Path

from src.core.process import process_file
from src.core.helpers import unzip_and_getfilepaths


class ProcessWorker(QThread):
    progress = Signal(int, dict)  # index, result_data
    error = Signal(int, str)  # index, error_message
    started = Signal(int)  # index

    def __init__(self, files: List[Path]):
        super().__init__()
        self.files = files

    def run(self):
        for i, file_path in enumerate(self.files):
            self.started.emit(i)
            try:
                res = process_file(file_path)
                energy = res.get('energy')
                grad_norm = res.get('gradient')
                verdict = "Stable" if energy < -10.0 else "Unstable"
                result_data = {
                    'energy': energy,
                    'gradient': grad_norm,
                    'verdict': verdict
                }
                self.progress.emit(i, result_data)
            except Exception as e:
                self.error.emit(i, str(e))


class ProcessScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.extract_dir: Path | None = None
        self.files: List[Path] = []
        
        # Models for the tables
        self.files_model = QStandardItemModel()
        self.results_model = QStandardItemModel()
        
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        
        title = QLabel("Molecular Conductivity Simulator")
        title.setObjectName("Header")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        content_layout = QHBoxLayout()

        # --- LEFT SIDE: Input Files ---
        left_layout = QVBoxLayout()
        lbl_files = QLabel("Input Structures (.xyz/mol)")
        lbl_files.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(lbl_files)

        self.files_table = QTableView()
        self.files_table.setModel(self.files_model)
        self.files_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.files_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.files_model.setHorizontalHeaderLabels(["Filename", "Status"])
        left_layout.addWidget(self.files_table)

        # --- RIGHT SIDE: CSV/Results ---
        right_layout = QVBoxLayout()
        lbl_results = QLabel("Conductivity Evaluation (Results)")
        lbl_results.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(lbl_results)

        self.results_table = QTableView()
        self.results_table.setModel(self.results_model)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Columns for the scientific data
        self.results_model.setHorizontalHeaderLabels(["Molecule", "Energy (Ha)", "Gradient Norm", "Verdict"])
        right_layout.addWidget(self.results_table)

        # Add panels to content layout (1:2 ratio)
        content_layout.addLayout(left_layout, 1)
        content_layout.addLayout(right_layout, 2)

        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

    def clear_data(self):
        if self.extract_dir and self.extract_dir.exists():
            for file in self.extract_dir.iterdir():
                if file.is_file(): file.unlink()
            self.extract_dir.rmdir()
        
        self.extract_dir = None
        self.files = []
        self.files_model.removeRows(0, self.files_model.rowCount())
        self.results_model.removeRows(0, self.results_model.rowCount())

    def process_zip_file(self, zip_path: Path):
        self.clear_data()
        
        # Extraction
        self.extract_dir = zip_path.parent / (zip_path.stem + "_extracted")
        self.files = unzip_and_getfilepaths(zip_path, self.extract_dir)

        # Populate Left Table first
        for file_path in self.files:
            name_item = QStandardItem(file_path.name)
            status_item = QStandardItem("Pending")
            self.files_model.appendRow([name_item, status_item])

        # Start worker thread
        self.worker = ProcessWorker(self.files)
        self.worker.started.connect(self.on_started)
        self.worker.progress.connect(self.on_progress)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    @Slot(int)
    def on_started(self, index: int):
        self.files_model.item(index, 1).setText("Running...")
        self.files_table.scrollTo(self.files_model.index(index, 0))
        self.files_table.update()

    @Slot(int, dict)
    def on_progress(self, index: int, result_data: dict):
        # Update status
        self.files_model.item(index, 1).setText("Done")
        self.files_model.item(index, 1).setForeground(QColor("green"))

        # Populate Right Table (Results)
        file_path = self.files[index]
        row_items = [
            QStandardItem(file_path.stem),
            QStandardItem(f"{result_data['energy']}"),
            QStandardItem(f"{result_data['gradient']}"),
            QStandardItem(result_data['verdict'])
        ]
        self.results_model.appendRow(row_items)
        self.results_table.scrollToBottom()

    @Slot(int, str)
    def on_error(self, index: int, error_message: str):
        self.files_model.item(index, 1).setText("Error")
        self.files_model.item(index, 1).setForeground(QColor("red"))
        print(f"Error processing {self.files[index].name}: {error_message}")

    def on_exit(self):
        self.clear_data()