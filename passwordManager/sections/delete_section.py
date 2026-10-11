from PySide6 import QtCore, QtWidgets

import exceptions
from sections.account_picker import AccountPicker, account_label
from sections.base import Section, set_state

DETAIL_FIELDS = [
    ("App", "page/app"), ("Username", "username"), ("Email", "email"),
    ("Type", "account_type"), ("Region", "region"), ("Rank", "rank"),
]


class DeleteSection(Section):
    title = "Delete an account"

    def __init__(self, vault, user):
        super().__init__(vault, user)
        self._accounts = {}

        self.picker = AccountPicker()
        self.picker.currentIndexChanged.connect(self._show_details)

        # antes de borrar, el usuario ve qué está por borrar
        self.label_details = QtWidgets.QLabel()
        self.label_details.setObjectName("details")
        self.label_details.setTextFormat(QtCore.Qt.PlainText)

        self.button_delete = QtWidgets.QPushButton("Delete account")
        self.button_delete.setObjectName("dangerButton")
        self.button_delete.clicked.connect(self.delete)

        self.label_empty = QtWidgets.QLabel()
        set_state(self.label_empty, "muted", "No accounts to delete.")

        self.main_layout.addWidget(self.picker)
        self.main_layout.addWidget(self.label_details)
        self.main_layout.addWidget(self.button_delete)
        self.main_layout.addWidget(self.label_empty)
        self.main_layout.addWidget(self.label_message)
        self.main_layout.addStretch(1)

    def refresh(self) -> None:
        accounts = self.vault.list_accounts(self.user)
        self._accounts = {account["id"]: account for account in accounts}
        self.picker.set_accounts(accounts)

        has_accounts = bool(accounts)
        for widget in (self.picker, self.label_details, self.button_delete):
            widget.setVisible(has_accounts)
        self.label_empty.setVisible(not has_accounts)
        self._show_details()

    def _show_details(self, *_) -> None:
        account = self._accounts.get(self.picker.current_id())
        if account is None:
            self.label_details.clear()
            return
        lines = [f"{name}: {account[key]}" for name, key in DETAIL_FIELDS if account.get(key)]
        self.label_details.setText("\n".join(lines))

    def delete(self) -> None:
        account_id = self.picker.current_id()
        account = self._accounts.get(account_id)
        if account is None:
            return

        answer = QtWidgets.QMessageBox.warning(
            self, "Delete account",
            f"Delete {account_label(account)}?\nThis can't be undone.",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel,
            QtWidgets.QMessageBox.Cancel,
        )
        if answer != QtWidgets.QMessageBox.Yes:
            return

        try:
            self.vault.delete_account(self.user, account_id)
        except exceptions.VaultException as e:
            self.show_error(str(e))
            return

        self.accounts_changed.emit()
        self.show_success(f"'{account['page/app']}' deleted.")
