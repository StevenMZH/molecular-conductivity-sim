from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLabel, QPushButton, QFileDialog, QHBoxLayout
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtCore import Qt
from PySide6.QtCore import Signal
import os
import pathlib


class MainScreen(QWidget):
    PROCESS_SIGNAL: Signal = Signal(pathlib.Path)
 
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # logo and title on the first row
        logo_title_layout = QHBoxLayout()

        logo_svg = QSvgWidget(os.path.join(os.path.dirname(__file__), "assets", "logo.svg"))
        logo_svg.setFixedSize(250, 250)
        logo_title_layout.addWidget(logo_svg)
        
        title = QLabel("Molecular Conductivity Simulator")
        title.setObjectName("Header")
        logo_title_layout.addWidget(title)

        logo_title_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(logo_title_layout)

        # description and instructions
        description = QLabel("Welcome to the Molecular Conductivity Simulator...")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(description)

        instructions = QLabel("To get started, please load your molecular data using a zip file.")
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(instructions)

        # zip button
        select_zip_button = QPushButton("Select Zip File")
        select_zip_button.setObjectName("PrimaryButton")
        select_zip_button.clicked.connect(self.select_zip_files)

        layout.addWidget(select_zip_button)

        self.setLayout(layout)

    def select_zip_files(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Zip Files (*.zip)")

        zip_file = None

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                zip_file = pathlib.Path(selected_files[0])
                print(f"Selected zip file: {zip_file}")

        if not zip_file:
            # no file selected, return
            return

        # send signal with the zip file selected
        self.PROCESS_SIGNAL.emit(zip_file)