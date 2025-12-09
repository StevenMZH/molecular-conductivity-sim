from PySide6.QtWidgets import QMainWindow, QStackedLayout, QWidget
from PySide6.QtCore import Slot
import pathlib
from .main_screen import MainScreen
from .process_screen import ProcessScreen


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Molecular Conductivity Simulator")
        self.setGeometry(100, 100, 860, 540)

        self.widget_layout = QStackedLayout()
        self.main_screen = MainScreen()
        self.process_screen = ProcessScreen()
        self.widget_layout.addWidget(self.main_screen)
        self.widget_layout.addWidget(self.process_screen)
        
        self.widget_layout.setCurrentIndex(0)

        widget = QWidget()
        widget.setLayout(self.widget_layout)
        self.setCentralWidget(widget)

        # Connect signals
        self.main_screen.PROCESS_SIGNAL.connect(self.on_process_signal)

    @Slot(pathlib.Path)
    def on_process_signal(self, zip_path: pathlib.Path):
        # once we receive the signal to process a zip file we should swap from main screen to process screen

        print(f"Received zip file to process: {zip_path}")

        self.widget_layout.setCurrentIndex(1)
        self.process_screen.process_zip_file(zip_path)