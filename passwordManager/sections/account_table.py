from PySide6 import QtCore, QtWidgets

import core
import exceptions
import secure_clipboard

HIDDEN = "••••••••"

COLUMNS = [
    ("App", "page/app"),
    ("Username", "username"),
    ("Email", "email"),
    ("Type", "account_type"),
    ("Region", "region"),
    ("Rank", "rank"),
]
PASSWORD_COLUMN = len(COLUMNS)
ACTIONS_COLUMN = PASSWORD_COLUMN + 1


class AccountTable(QtWidgets.QTableWidget):
    """Tabla de cuentas con la contraseña oculta y botones para mostrarla o copiarla.

    Nunca recibe contraseñas de antemano: list_accounts no las trae.
    Cada una se descifra recién cuando el usuario toca Show o Copy.
    """

    def __init__(self, vault: core.PasswordVault, user: str):
        super().__init__(0, len(COLUMNS) + 2)
        self.vault = vault
        self.user = user
        self._revealed = set()   # ids de las cuentas con la contraseña visible

        self.setHorizontalHeaderLabels([name for name, _ in COLUMNS] + ["Password", ""])
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)
        self.setWordWrap(False)

        header = self.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(ACTIONS_COLUMN, QtWidgets.QHeaderView.ResizeToContents)

    def set_accounts(self, accounts: list[dict]) -> None:
        self._revealed.clear()
        self.setRowCount(0)   # descarta las filas y botones de la lista anterior
        self.setRowCount(len(accounts))

        for row, account in enumerate(accounts):
            for col, (_, key) in enumerate(COLUMNS):
                item = QtWidgets.QTableWidgetItem(account.get(key) or "")
                if col == 0:
                    item.setData(QtCore.Qt.UserRole, account["id"])
                self.setItem(row, col, item)

            self.setItem(row, PASSWORD_COLUMN, QtWidgets.QTableWidgetItem(HIDDEN))
            self.setCellWidget(row, ACTIONS_COLUMN, self._actions(account["id"], row))

        self.resizeRowsToContents()

    def _actions(self, account_id: str, row: int) -> QtWidgets.QWidget:
        box = QtWidgets.QWidget()
        box.setObjectName("cellActions")
        layout = QtWidgets.QHBoxLayout(box)
        layout.setContentsMargins(4, 0, 4, 0)
        layout.setSpacing(4)

        button_show = QtWidgets.QPushButton("Show")
        button_show.setObjectName("smallButton")
        button_show.clicked.connect(lambda: self._toggle(account_id, row, button_show))

        button_copy = QtWidgets.QPushButton("Copy")
        button_copy.setObjectName("smallButton")
        button_copy.clicked.connect(lambda: self._copy(account_id))

        layout.addWidget(button_show)
        layout.addWidget(button_copy)
        return box

    def _decrypt(self, account_id: str) -> str | None:
        try:
            return self.vault.get_password(self.user, account_id)
        except exceptions.VaultException as e:
            QtWidgets.QMessageBox.warning(self, "Can't read the password", str(e))
            return None

    def _toggle(self, account_id: str, row: int, button: QtWidgets.QPushButton) -> None:
        if account_id in self._revealed:
            self._revealed.discard(account_id)
            self.item(row, PASSWORD_COLUMN).setText(HIDDEN)
            button.setText("Show")
            return

        password = self._decrypt(account_id)
        if password is None:
            return
        self._revealed.add(account_id)
        self.item(row, PASSWORD_COLUMN).setText(password)
        button.setText("Hide")

    def _copy(self, account_id: str) -> None:
        password = self._decrypt(account_id)
        if password is not None:
            secure_clipboard.copy_secret(password)
            self.window().statusBar().showMessage(
                "Password copied. It will be cleared from the clipboard soon.", 4000
            )
