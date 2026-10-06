from pathlib import Path
import core
import sys
from PySide6 import QtCore, QtWidgets

BASE_DIR = Path(__file__).resolve().parent
DATA = BASE_DIR / "prueba" / "reg.json"
KEY = BASE_DIR / "prueba" / "key_prueba.key"



class LoginWidget(QtWidgets.QWidget):
    def __init__(self, vault: core.PasswordVault):
        super().__init__()
        
        self.vault = vault

        self.button_login = QtWidgets.QPushButton("Login") 
        self.button_register = QtWidgets.QPushButton("Register") 
        self.lineedit_password = QtWidgets.QLineEdit("Password")
        self.combobox_users = QtWidgets.QComboBox()
        self.combobox_users.addItems(self.vault.list_users())

        self.label_error = QtWidgets.QLabel("")


        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.button_login)
        self.layout.addWidget(self.button_register)
        self.layout.addWidget(self.lineedit_password)
        self.layout.addWidget(self.combobox_users)
        self.layout.addWidget(self.label_error)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    login = LoginWidget(core.PasswordVault(DATA, KEY))
    login.resize(800, 600)
    login.show()
    sys.exit(app.exec())