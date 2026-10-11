from PySide6 import QtWidgets

from sections.account_table import AccountTable
from sections.base import Section, set_state

SEARCH_FIELDS = ("page/app", "username", "email", "account_type", "region", "rank")


class SearchSection(Section):
    title = "Search"

    def __init__(self, vault, user):
        super().__init__(vault, user)
        self._accounts = []

        self.lineedit_search = QtWidgets.QLineEdit()
        self.lineedit_search.setPlaceholderText("Type to filter by app, username, email…")
        self.lineedit_search.setClearButtonEnabled(True)
        # filtra mientras escribís: no hay botón de buscar
        self.lineedit_search.textChanged.connect(self._apply_filter)

        self.table = AccountTable(vault, user)
        self.label_empty = QtWidgets.QLabel()

        self.main_layout.addWidget(self.lineedit_search)
        self.main_layout.addWidget(self.table, 1)
        self.main_layout.addWidget(self.label_empty)

    def refresh(self) -> None:
        self._accounts = self.vault.list_accounts(self.user)
        self._apply_filter(self.lineedit_search.text())

    def _apply_filter(self, text: str) -> None:
        query = text.strip().lower()
        matches = [
            account for account in self._accounts
            if not query or any(query in (account.get(f) or "").lower() for f in SEARCH_FIELDS)
        ]
        self.table.set_accounts(matches)

        self.table.setVisible(bool(matches))
        self.label_empty.setVisible(not matches)
        if not self._accounts:
            set_state(self.label_empty, "muted", "No accounts yet. Add one from the 'Add' section.")
        else:
            set_state(self.label_empty, "muted", f"No accounts match “{text.strip()}”.")
