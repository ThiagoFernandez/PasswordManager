from PySide6 import QtWidgets, QtCore
import core
from sections.base import paint
import exceptions


class LoginWidget(QtWidgets.QWidget):

    register_requested = QtCore.Signal()
    login_successful = QtCore.Signal(str)

    def __init__(self, vault: core.PasswordVault):
        super().__init__()

        self.vault = vault

        self.button_login = QtWidgets.QPushButton("Login")
        self.button_login.setObjectName("primaryButton")
        self.button_login.clicked.connect(self.login)

        self.button_register = QtWidgets.QPushButton("Register")
        self.button_register.clicked.connect(self.register_requested)

        self.lineedit_password = QtWidgets.QLineEdit()
        self.lineedit_password.setPlaceholderText("Write your password here")
        self.lineedit_password.setEchoMode(QtWidgets.QLineEdit.Password) # es como pwinput
        self.lineedit_password.returnPressed.connect(self.login)

        self.combobox_users = QtWidgets.QComboBox()

        self.label_error = QtWidgets.QLabel("")

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.addWidget(self.combobox_users)
        self.main_layout.addWidget(self.lineedit_password)
        self.main_layout.addWidget(self.button_login)
        self.main_layout.addWidget(self.button_register)
        self.main_layout.addWidget(self.label_error)

        self.refresh_users()

    def login(self):
        password_login = self.lineedit_password.text()
        user_login = self.combobox_users.currentText()

        try:
            self.vault.login(user_login, password_login)

        except exceptions.WrongPasswordException as e:
            self._show_error(
                f"Wrong password. Attempts left: {e.attempts_left}"
            )

        except exceptions.BannedUserException as e:
            self._show_error(
                f"User is banned until: {e.ban_until.strftime('%Y-%m-%d %H:%M:%S')}"
            )

        except exceptions.VaultException as e:
            self._show_error(f"Error: {e}")

        else:
            paint(self.label_error, "success")
            self.label_error.setText("OK")
            self.login_successful.emit(user_login)

    def _show_error(self, text):
        paint(self.label_error, "error")
        self.label_error.setText(text)
        self.lineedit_password.clear()
        
    def refresh_users(self, select=None):
        self.combobox_users.clear()
        self.combobox_users.addItems(self.vault.list_users())

        has_users = self.combobox_users.count() > 0

        self.button_login.setEnabled(has_users)
        self.lineedit_password.setEnabled(has_users)
        self.lineedit_password.clear()

        if not has_users:
            self._show_error("No users yet. Register one first.")
            return

        self.clear_message()

        if select is not None:
            index = self.combobox_users.findText(select)
            if index >= 0:
                self.combobox_users.setCurrentIndex(index)

    def clear_message(self):
        self.label_error.clear()
        paint(self.label_error, "")

    def show_notice(self, text):
        # mensaje que viene de afuera (ej. sesión expirada); va después de refresh_users
        paint(self.label_error, "warning")
        self.label_error.setText(text)