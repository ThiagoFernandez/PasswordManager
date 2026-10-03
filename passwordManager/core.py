import app
import exceptions
from datetime import datetime, timedelta

MINIMO = 12
MAXIMO = 64
INTENTOS_MAXIMOS = 3
# normalizo a segundos los tiempos de ban y timeout
BAN_TIME = 300 # Tiempo de ban en segundos (5 minutos)
TIMEOUT = 60 # Tiempo de timeout en segundos (1 minuto)

class PasswordVault:
    # Clase principal del gestor de contraseñas.
    # carga datos y cipher de usuarios y contraseñas, maneja intentos de login, baneos y timeouts.
    def __init__(self):
        self.users = {}  # Diccionario para almacenar usuarios y sus contraseñas cifradas
        self.failed_attempts = {}  # Diccionario para rastrear intentos fallidos de inicio de sesión
        self.banned_users = {}  # Diccionario para rastrear usuarios baneados
        self.load_data()  # Cargar datos desde el archivo al iniciar la aplicación