from PySide6 import QtWidgets

from sections.account_table import AccountTable
from sections.base import Section, set_state


class AllSection(Section):
    title = "All accounts"

    def __init__(self, vault, user):
        super().__init__(vault, user)

        self.label_count = QtWidgets.QLabel()
        self.table = AccountTable(vault, user)
        self.label_empty = QtWidgets.QLabel()
        set_state(self.label_empty, "muted", "No accounts yet. Add one from the 'Add' section.")

        self.main_layout.addWidget(self.label_count)
        self.main_layout.addWidget(self.table, 1)
        self.main_layout.addWidget(self.label_empty)

    def refresh(self) -> None:
        accounts = self.vault.list_accounts(self.user)
        self.table.set_accounts(accounts)

        has_accounts = bool(accounts)
        self.table.setVisible(has_accounts)
        self.label_empty.setVisible(not has_accounts)
        set_state(self.label_count, "muted", f"{len(accounts)} account(s)")
