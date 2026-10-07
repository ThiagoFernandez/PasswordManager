from PySide6 import QtWidgets
import core
import exceptions

class LoginWidget(QtWidgets.QWidget):
    def __init__(self, vault: core.PasswordVault):
        super().__init__()

        self.vault = vault

        self.button_login = QtWidgets.QPushButton("Login")
        self.button_login.clicked.connect(self.login)
        self.button_register = QtWidgets.QPushButton("Register")

        self.lineedit_password = QtWidgets.QLineEdit()
        self.lineedit_password.setPlaceholderText("Write your password here")
        self.lineedit_password.setEchoMode(QtWidgets.QLineEdit.Password) # como pwinput

        self.combobox_users = QtWidgets.QComboBox()
        self.combobox_users.addItems(self.vault.list_users())

        self.label_error = QtWidgets.QLabel("")

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.addWidget(self.combobox_users)
        self.main_layout.addWidget(self.lineedit_password)
        self.main_layout.addWidget(self.button_login)
        self.main_layout.addWidget(self.button_register)
        self.main_layout.addWidget(self.label_error)

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
            self.label_error.setStyleSheet("color: green;")
            self.label_error.setText("OK")

    def _show_error(self, text):
        self.label_error.setStyleSheet("color: red;")
        self.label_error.setText(text)
        self.lineedit_password.clear()
