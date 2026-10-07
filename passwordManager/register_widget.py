from PySide6 import QtWidgets, QtCore
import core
import exceptions


class RegisterWidget(QtWidgets.QWidget):

    back_requested = QtCore.Signal()
    user_created = QtCore.Signal(str)

    def __init__(self, vault: core.PasswordVault):
        super().__init__()

        self.vault = vault

        self.lineedit_username = QtWidgets.QLineEdit()
        self.lineedit_username.setPlaceholderText("Write your username here")

        self.lineedit_password = QtWidgets.QLineEdit()
        self.lineedit_password.setPlaceholderText("Write your password here")
        self.lineedit_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineedit_password.textChanged.connect(self.update_rules)

        self.lineedit_password_repeat = QtWidgets.QLineEdit()
        self.lineedit_password_repeat.setPlaceholderText(
            "Write again your password here"
        )
        self.lineedit_password_repeat.setEchoMode(QtWidgets.QLineEdit.Password)

        self.rule_labels = {}

        for rule in core.validate_password("").keys():
            label = QtWidgets.QLabel(rule)
            label.setStyleSheet("color: gray;")
            self.rule_labels[rule] = label

        self.button_create_user = QtWidgets.QPushButton("Create user")
        self.button_create_user.clicked.connect(self.create_user)

        self.button_back = QtWidgets.QPushButton("Back")
        self.button_back.clicked.connect(self.back)

        self.label_error = QtWidgets.QLabel("")

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.addWidget(self.lineedit_username)
        self.main_layout.addWidget(self.lineedit_password)

        for label in self.rule_labels.values():
            self.main_layout.addWidget(label)

        self.main_layout.addWidget(self.lineedit_password_repeat)
        self.main_layout.addWidget(self.button_create_user)
        self.main_layout.addWidget(self.button_back)
        self.main_layout.addWidget(self.label_error)

    def update_rules(self, password: str):
        if password.strip() == "":
            for rule in self.rule_labels:
                self.rule_labels[rule].setStyleSheet("color: gray;")
        else:
            rules = core.validate_password(password)

            for rule, passed in rules.items():
                if passed:
                    self.rule_labels[rule].setStyleSheet("color: green;")
                else:
                    self.rule_labels[rule].setStyleSheet("color: red;")

    def create_user(self):
        password = self.lineedit_password.text()
        password_repeat = self.lineedit_password_repeat.text()

        if password != password_repeat:
            self._show_error("Passwords don't match")
            return

        username = self.lineedit_username.text().strip()

        try:
            self.vault.register(username, password)

        except exceptions.EmptyFieldException as e:
            self._show_error(
                f"The field '{e.field_name}' cannot be empty"
            )

        except exceptions.UserAlreadyExistsException:
            self._show_error(
                f"The username {username} already exists"
            )

        except exceptions.WeakPasswordException:
            self._show_error(
                "Password doesn't meet the rules"
            )

        except exceptions.VaultException as e:
            self._show_error(f"Error: {e}")

        else:
            self.label_error.setStyleSheet("color: green;")
            self.label_error.setText("User created successfully")

            self.lineedit_username.clear()
            self.lineedit_password.clear()
            self.lineedit_password_repeat.clear()

            self.user_created.emit(username)

    def back(self):
        self.back_requested.emit()

    def _show_error(self, text):
        self.label_error.setStyleSheet("color: red;")
        self.label_error.setText(text)
        self.lineedit_password.clear()
        self.lineedit_password_repeat.clear()