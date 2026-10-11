from PySide6 import QtCore, QtWidgets


def account_label(account: dict) -> str:
    return f"{account['page/app']} — {account['username']} ({account['email']})"


class AccountPicker(QtWidgets.QComboBox):
    """Combo de cuentas que muestra un texto legible pero guarda el id de cada una.

    Change y Delete lo usan: el usuario elige por nombre, el vault recibe el id.
    """

    def set_accounts(self, accounts: list[dict]) -> None:
        current = self.current_id()
        self.clear()
        for account in accounts:
            self.addItem(account_label(account), account["id"])
        # si la cuenta que estaba elegida sigue existiendo, queda elegida
        index = self.findData(current)
        if index >= 0:
            self.setCurrentIndex(index)

    def current_id(self) -> str | None:
        return self.currentData(QtCore.Qt.UserRole)
