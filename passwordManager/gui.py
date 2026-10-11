import sys
from pathlib import Path

from cryptography.fernet import Fernet
from PySide6 import QtCore, QtWidgets

import core
import exceptions
import gui_config
import secure_clipboard
from login_widget import LoginWidget
from main_widget import MainWidget
from register_widget import RegisterWidget


BASE_DIR = Path(__file__).resolve().parent

# Empaquetado con PyInstaller, el programa se descomprime en una carpeta temporal
# que se borra al cerrar. Por eso:
#   - los recursos de solo lectura (style.qss) se leen de esa carpeta (sys._MEIPASS),
#   - los datos y la key viven AL LADO DEL .exe, que es lo único que persiste.
FROZEN = getattr(sys, "frozen", False)
RESOURCE_DIR = Path(getattr(sys, "_MEIPASS", BASE_DIR))

if FROZEN:
    DATA_DIR = Path(sys.executable).resolve().parent
    DATA = DATA_DIR / "dataNoTocar.json"
    KEY = DATA_DIR / "key.key"
else:
    DATA = BASE_DIR / "prueba" / "reg.json"
    KEY = BASE_DIR / "prueba" / "key_prueba.key"

STYLE = RESOURCE_DIR / "style.qss"

APP_TITLE = "Password Manager"

# eventos que cuentan como "el usuario está usando la app"
ACTIVITY_EVENTS = {
    QtCore.QEvent.KeyPress,
    QtCore.QEvent.MouseButtonPress,
    QtCore.QEvent.MouseMove,
    QtCore.QEvent.Wheel,
}


class AppWindow(QtWidgets.QMainWindow):
    def __init__(self, vault):
        super().__init__()

        self.vault = vault
        self.active_user = None
        self.main = None   # la MainWidget de la sesión activa (None si no hay sesión)

        self.login = LoginWidget(vault)
        self.register = RegisterWidget(vault)

        self.login.register_requested.connect(self.show_register)
        self.login.login_successful.connect(self.on_login)

        self.register.back_requested.connect(self.show_login)
        self.register.user_created.connect(self.on_user_created)

        # login y registro se muestran como una tarjeta centrada, no estirados a toda la ventana
        self.login_page = centered_card(self.login, APP_TITLE, "Log in to your vault")
        self.register_page = centered_card(self.register, "Create a user", "Your master password protects everything else")

        self.stack = QtWidgets.QStackedWidget()
        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.register_page)

        self.setCentralWidget(self.stack)
        self.setStatusBar(QtWidgets.QStatusBar())
        self.setWindowTitle(APP_TITLE)

        # timeout de inactividad: la sesión vive en la GUI, así que el timer también
        self.inactivity_timer = QtCore.QTimer(self)
        self.inactivity_timer.setSingleShot(True)
        self.inactivity_timer.setInterval(gui_config.INACTIVITY_TIMEOUT_MS)
        self.inactivity_timer.timeout.connect(self.on_inactivity)
        # escucha los eventos de toda la app para reiniciar el timer
        QtWidgets.QApplication.instance().installEventFilter(self)

        self.resize(1000, 650)

    def show_login(self, select=None):
        self.login.refresh_users(select=select)
        self.stack.setCurrentWidget(self.login_page)

    def on_user_created(self, username):
        self.show_login(select=username)

    def show_register(self):
        self.register.reset()
        self.stack.setCurrentWidget(self.register_page)

    def on_login(self, username):
        self.active_user = username
        # una MainWidget nueva por sesión: no hereda nada del usuario anterior
        self.main = MainWidget(self.vault, username)
        self.main.logout_requested.connect(self.logout)
        self.stack.addWidget(self.main)
        self.stack.setCurrentWidget(self.main)
        self.setWindowTitle(f"{APP_TITLE} — {username}")
        self.inactivity_timer.start()

    def logout(self, notice=None):
        self.inactivity_timer.stop()
        self.active_user = None
        secure_clipboard.clear_if_ours()

        if self.main is not None:
            self.stack.removeWidget(self.main)
            self.main.deleteLater()   # libera la pantalla y todo lo que mostraba
            self.main = None

        self.setWindowTitle(APP_TITLE)
        self.statusBar().clearMessage()
        self.show_login()
        if notice:
            self.login.show_notice(notice)

    def on_inactivity(self):
        if self.active_user is not None:
            self.logout(notice="Session expired due to inactivity. Log in again.")

    def eventFilter(self, watched, event):
        if self.active_user is not None and event.type() in ACTIVITY_EVENTS:
            self.inactivity_timer.start()   # start() sobre un timer activo lo reinicia
        return super().eventFilter(watched, event)


def centered_card(content: QtWidgets.QWidget, title: str, subtitle: str) -> QtWidgets.QWidget:
    """Envuelve una pantalla en una tarjeta de ancho fijo centrada en la ventana."""
    card = QtWidgets.QFrame()
    card.setObjectName("card")
    card.setFixedWidth(420)

    label_title = QtWidgets.QLabel(title)
    label_title.setObjectName("cardTitle")
    label_subtitle = QtWidgets.QLabel(subtitle)
    label_subtitle.setObjectName("cardSubtitle")
    label_subtitle.setWordWrap(True)

    card_layout = QtWidgets.QVBoxLayout(card)
    card_layout.setContentsMargins(28, 28, 28, 28)
    card_layout.addWidget(label_title)
    card_layout.addWidget(label_subtitle)
    card_layout.addSpacing(8)
    content.setObjectName("cardContent")
    card_layout.addWidget(content)

    page = QtWidgets.QWidget()
    page_layout = QtWidgets.QGridLayout(page)
    page_layout.addWidget(card, 0, 0, QtCore.Qt.AlignCenter)
    return page


def ensure_key_on_first_run() -> None:
    """Primera vez que se abre la app: si no hay key NI datos, crea la key.

    Respeta la decisión de la Fase 0 (nunca generar una key sola): el peligro era
    una key nueva que no descifra datos viejos. Si no existe el archivo de datos,
    no hay nada viejo que perder. Si hay datos y falta la key, la app sigue
    cortando con MissingKeyFileException, como antes.
    """
    if KEY.exists() or DATA.exists():
        return
    KEY.parent.mkdir(parents=True, exist_ok=True)
    KEY.write_bytes(Fernet.generate_key())


def load_style(app: QtWidgets.QApplication) -> None:
    try:
        app.setStyleSheet(STYLE.read_text(encoding="utf-8"))
    except OSError:
        pass   # sin estilos la app funciona igual, solo se ve más simple


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    app.setApplicationName(APP_TITLE)
    load_style(app)

    try:
        ensure_key_on_first_run()
        vault = core.PasswordVault(DATA, KEY)
    except OSError as e:
        QtWidgets.QMessageBox.critical(None, "Error", f"Couldn't create the key file:\n{e}")
        sys.exit(1)
    except exceptions.VaultException as e:
        QtWidgets.QMessageBox.critical(
            None,
            "Error",
            f"Couldn't open the vault:\n{e}"
        )
        sys.exit(1)

    window = AppWindow(vault)
    window.show()

    sys.exit(app.exec())
