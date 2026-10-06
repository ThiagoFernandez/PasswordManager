import sys

from PySide6 import QtCore, QtWidgets


class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.cont = 0

        self.button = QtWidgets.QPushButton("add")
        self.button2 = QtWidgets.QPushButton("reset")
        self.text = QtWidgets.QLabel("Clicks: 0",
                                     alignment=QtCore.Qt.AlignCenter)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.button2)

        self.button.clicked.connect(self.add_number)
        self.button2.clicked.connect(self.reset)

    def add_number(self):
        self.cont +=1
        self._show_text(self)

    def reset(self):
        self.cont = 0
        self._show_text(self)

    def _show_text(self):
        self.text.setText(str(self.cont))


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MyWidget()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())