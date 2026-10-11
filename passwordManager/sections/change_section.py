from PySide6 import QtWidgets

import exceptions
from sections.account_picker import AccountPicker
from sections.base import Section, set_state
from sections.password_input import PasswordInput


class ChangeSection(Section):
    title = "Change a password"

    def __init__(self, vault, user):
        super().__init__(vault, user)

        self.picker = AccountPicker()
        self.password = PasswordInput()
        self.password.textChanged.connect(self._update_save_button)

        self.button_save = QtWidgets.QPushButton("Change password")
        self.button_save.setObjectName("primaryButton")
        self.button_save.clicked.connect(self.save)

        self.label_empty = QtWidgets.QLabel()
        set_state(self.label_empty, "muted", "No accounts yet. Add one from the 'Add' section.")

        self.form_box = QtWidgets.QWidget()
        form = QtWidgets.QFormLayout(self.form_box)
        form.setContentsMargins(0, 0, 0, 0)
        form.addRow("Account", self.picker)
        form.addRow("New password", self.password)

        self.main_layout.addWidget(self.form_box)
        self.main_layout.addWidget(self.button_save)
        self.main_layout.addWidget(self.label_empty)
        self.main_layout.addWidget(self.label_message)
        self.main_layout.addStretch(1)
        self._update_save_button()

    def refresh(self) -> None:
        accounts = self.vault.list_accounts(self.user)
        self.picker.set_accounts(accounts)
        has_accounts = bool(accounts)
        self.form_box.setVisible(has_accounts)
        self.button_save.setVisible(has_accounts)
        self.label_empty.setVisible(not has_accounts)
        self.clear_message()

    def _update_save_button(self, *_) -> None:
        self.button_save.setEnabled(bool(self.password.text().strip()))

    def save(self) -> None:
        account_id = self.picker.current_id()
        if account_id is None:
            return

        answer = QtWidgets.QMessageBox.question(
            self, "Change password",
            f"Replace the password of {self.picker.currentText()}?",
        )
        if answer != QtWidgets.QMessageBox.Yes:
            return

        try:
            self.vault.change_password(self.user, account_id, self.password.text())
        except exceptions.VaultException as e:
            self.show_error(str(e))
            return

        self.password.clear()
        self.accounts_changed.emit()
        self.show_success("Password changed.")
