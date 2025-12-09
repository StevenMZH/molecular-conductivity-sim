"""
Entry point for the application.
"""
import src.ui.main_window as main_window

def main():
    app = main_window.QApplication([])
    window = main_window.MainWindow()
    window.show()
    app.exec()
    

if __name__ == "__main__":
    main()
