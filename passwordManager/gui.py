import sys
from pathlib import Path

from PySide6 import QtWidgets

import core
import exceptions
from login_widget import LoginWidget
from register_widget import RegisterWidget


BASE_DIR = Path(__file__).resolve().parent
DATA = BASE_DIR / "prueba" / "reg.json"
KEY = BASE_DIR / "prueba" / "key_prueba.key"


class AppWindow(QtWidgets.QMainWindow):
    def __init__(self, vault):
        super().__init__()

        self.active_user = None

        self.login = LoginWidget(vault)
        self.register = RegisterWidget(vault)

        self.login.register_requested.connect(self.show_register)
        self.login.login_successful.connect(self.on_login)

        self.register.back_requested.connect(self.show_login)
        self.register.user_created.connect(self.on_user_created)

        self.stack = QtWidgets.QStackedWidget()
        self.stack.addWidget(self.login)
        self.stack.addWidget(self.register)

        self.setCentralWidget(self.stack)

        self.resize(800, 600)

    def show_register(self):
        self.stack.setCurrentWidget(self.register)

    def show_login(self):
        self.stack.setCurrentWidget(self.login)

    def on_user_created(self, username):
        self.login.refresh_users()
        self.login.combobox_users.setCurrentText(username)
        self.stack.setCurrentWidget(self.login)

    def on_login(self, username):
        self.active_user = username
        self.setWindowTitle(f"Bienvenido, {username}")


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    try:
        vault = core.PasswordVault(DATA, KEY)
    except exceptions.VaultException as e:
        QtWidgets.QMessageBox.critical(
            None,
            "Error",
            f"No se pudo crear el vault:\n{e}"
        )
        sys.exit(1)

    window = AppWindow(vault)
    window.show()

    sys.exit(app.exec())
