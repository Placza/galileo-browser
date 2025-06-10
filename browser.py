#Main file - starts the app

if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication
    from src import app 

    app_instance = QApplication(sys.argv)
    browser = app.Browser(800, 600)
    browser.show()

    sys.exit(app_instance.exec())