import sys
from pathlib import Path

from PySide6 import QtWidgets

import core
from login_widget import LoginWidget


BASE_DIR = Path(__file__).resolve().parent
DATA = BASE_DIR / "prueba" / "reg.json"
KEY = BASE_DIR / "prueba" / "key_prueba.key"


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    try:
        vault = core.PasswordVault(DATA, KEY)
    except Exception as e:
        QtWidgets.QMessageBox.critical(
            None,
            "Error",
            f"No se pudo crear el vault:\n{e}"
        )
        sys.exit(1)

    login = LoginWidget(vault)
    login.resize(800, 600)
    login.show()

    sys.exit(app.exec())
