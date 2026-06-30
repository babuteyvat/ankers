import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QLabel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(700, 300, 1400, 1000)
        self.initUI()

    def initUI(self):
        easy_button = QPushButton("Easy", self)
        easy_button.setGeometry(1000, 200, 300, 150)
        good_button = QPushButton("Good", self)
        good_button.setGeometry(700, 200, 300, 150)
        hard_button = QPushButton("Hard", self)
        hard_button.setGeometry(400, 200, 300, 150)
        again_button = QPushButton("Again", self)
        again_button.setGeometry(100, 200, 300, 150)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())