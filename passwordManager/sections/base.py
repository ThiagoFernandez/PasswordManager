from PySide6 import QtCore, QtWidgets

import core


def paint(label: QtWidgets.QLabel, state: str) -> None:
    """Pinta un label según su estado ("error", "success", "warning", "muted" o "").

    El color lo decide style.qss con el selector QLabel[state="..."];
    unpolish/polish hace que Qt vuelva a leer la propiedad.
    """
    label.setProperty("state", state)
    label.style().unpolish(label)
    label.style().polish(label)


def set_state(label: QtWidgets.QLabel, state: str, text: str = "") -> None:
    """Pinta el label y le pone el texto (como texto plano, nunca HTML)."""
    paint(label, state)
    label.setTextFormat(QtCore.Qt.PlainText)
    label.setText(text)


class Section(QtWidgets.QWidget):
    """Madre de las 5 secciones: todas reciben el vault y el usuario activo."""

    # cualquier sección que cambie cuentas lo avisa, y la ventana principal
    # refresca a las demás
    accounts_changed = QtCore.Signal()

    title = "Section"

    def __init__(self, vault: core.PasswordVault, user: str):
        super().__init__()
        self.vault = vault
        self.user = user

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(24, 24, 24, 24)
        self.main_layout.setSpacing(12)

        header = QtWidgets.QLabel(self.title)
        header.setObjectName("sectionTitle")
        self.main_layout.addWidget(header)

        self.label_message = QtWidgets.QLabel("")
        self.label_message.setWordWrap(True)
        # texto plano: un nombre de app como "<b>x</b>" no se interpreta como HTML
        self.label_message.setTextFormat(QtCore.Qt.PlainText)

    def refresh(self) -> None:
        """Vuelve a leer las cuentas del vault. Cada sección lo redefine si lo necesita."""

    def show_error(self, text: str) -> None:
        set_state(self.label_message, "error", text)

    def show_success(self, text: str) -> None:
        set_state(self.label_message, "success", text)

    def clear_message(self) -> None:
        set_state(self.label_message, "", "")
