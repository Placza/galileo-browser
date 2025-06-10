#The app file is for rendering the GUI and linking the browser's logic with it

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton, QMainWindow
from PySide6.QtGui import QIcon, QPixmap
from . import network as network
from . import view as view

class Browser(QMainWindow):
    def __init__(self, width, height):
        super().__init__()
        self.setMinimumSize(width, height)
        self.setWindowTitle('Galileo')
        
        self.renderUI()

    #Connects to the internet and loads the view's content
    def search_web(self):
        addr = self.search_bar
        default_text = self.search_bar.placeholderText()
        if addr.text() != default_text:
            url = network.URL(addr.text())
            content = network.Socket(url).load_content()
            self.view.load(content)
        
    def renderUI(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        header_layout = QHBoxLayout()
        header = QWidget()
        header.setLayout(header_layout)
        header.setStyleSheet('background-color: lightgray;')
        header.setFixedHeight(60)
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText('Start searching the web by writing an address')
        self.search_bar.setStyleSheet('background-color: black;')
        self.search_bar.returnPressed.connect(self.search_web)
        
        pixmap = QPixmap('assets/magnifier.png')
        search_icon = QIcon(pixmap)
        search_button = QPushButton()
        search_button.setStyleSheet('background-color: white;')
        search_button.setIcon(search_icon)
        search_button.clicked.connect(self.search_web)
        header_layout.addWidget(search_button)
        header_layout.addWidget(self.search_bar)
        main_layout.addWidget(header)
        
        self.view = view.View(self.width(), self.height() - 60)
        main_layout.addWidget(self.view)

        
        self.setCentralWidget(main_widget)

        
        
        