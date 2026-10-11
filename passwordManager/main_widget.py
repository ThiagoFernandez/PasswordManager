from PySide6 import QtCore, QtWidgets

import core
from sections.add_section import AddSection
from sections.all_section import AllSection
from sections.change_section import ChangeSection
from sections.delete_section import DeleteSection
from sections.search_section import SearchSection

# el orden de la barra lateral ES el orden del stack: la fila N muestra la página N
SECTIONS = [
    ("📋  All", AllSection),
    ("🔍  Search", SearchSection),
    ("➕  Add", AddSection),
    ("✏️  Change", ChangeSection),
    ("🗑  Delete", DeleteSection),
]


class MainWidget(QtWidgets.QWidget):
    """Pantalla principal de una sesión: barra lateral + una página por sección.

    Se crea una nueva en cada login y se descarta en el logout, así no queda
    nada del usuario anterior.
    """

    logout_requested = QtCore.Signal()

    def __init__(self, vault: core.PasswordVault, user: str):
        super().__init__()

        self.stack = QtWidgets.QStackedWidget()
        self.sections = []

        self.sidebar = QtWidgets.QListWidget()
        self.sidebar.setObjectName("sidebar")

        for name, section_class in SECTIONS:
            section = section_class(vault, user)
            # cualquier sección que cambie cuentas → se refrescan todas
            section.accounts_changed.connect(self.refresh_all)
            self.sections.append(section)
            self.stack.addWidget(section)
            self.sidebar.addItem(name)

        # señal → slot de Qt, sin función propia en el medio
        self.sidebar.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.sidebar.currentRowChanged.connect(self._on_section_changed)

        label_user = QtWidgets.QLabel(f"🔐  {user}")
        label_user.setObjectName("sidebarUser")
        label_user.setTextFormat(QtCore.Qt.PlainText)

        button_logout = QtWidgets.QPushButton("Logout")
        button_logout.setObjectName("logoutButton")
        button_logout.clicked.connect(self.logout_requested)

        side_panel = QtWidgets.QFrame()
        side_panel.setObjectName("sidePanel")
        side_panel.setFixedWidth(200)
        side_layout = QtWidgets.QVBoxLayout(side_panel)
        side_layout.setContentsMargins(12, 16, 12, 16)
        side_layout.addWidget(label_user)
        side_layout.addWidget(self.sidebar, 1)
        side_layout.addWidget(button_logout)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(side_panel)
        layout.addWidget(self.stack, 1)

        self.refresh_all()
        self.sidebar.setCurrentRow(0)

    def refresh_all(self) -> None:
        for section in self.sections:
            section.refresh()

    def _on_section_changed(self, row: int) -> None:
        # al entrar a una sección, que muestre datos frescos y sin mensajes viejos
        if 0 <= row < len(self.sections):
            self.sections[row].refresh()
