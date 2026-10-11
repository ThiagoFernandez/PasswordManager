from PySide6 import QtCore, QtWidgets

import gui_config

# La última contraseña que copió la app. Solo se borra el portapapeles si
# todavía contiene esa contraseña: si el usuario copió otra cosa después, no se toca.
_last_copied = None


def copy_secret(text: str) -> None:
    global _last_copied
    QtWidgets.QApplication.clipboard().setText(text)
    _last_copied = text
    QtCore.QTimer.singleShot(gui_config.CLIPBOARD_CLEAR_MS, clear_if_ours)


def clear_if_ours() -> None:
    global _last_copied
    clipboard = QtWidgets.QApplication.clipboard()
    if _last_copied is not None and clipboard.text() == _last_copied:
        clipboard.clear()
    _last_copied = None
