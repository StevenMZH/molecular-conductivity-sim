from PySide6.QtWidgets import QMainWindow, QApplication


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Molecular Conductivity Simulator")
        self.setGeometry(100, 100, 800, 600)
