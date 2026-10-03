import exceptions
import json
import hashlib
import secrets
import string
import uuid

from cryptography.fernet import Fernet
from pathlib import Path
from datetime import datetime, timedelta

MINIMUM_LENGTH = 12
MAXIMUM_LENGTH = 64
MAX_LOGIN_ATTEMPTS = 3
BAN_TIME = 300 # Tiempo de ban en segundos (5 minutos)

# funciones sueltas
def validate_password(password) -> dict[str, bool]:
    pass

def generate_password(length=MINIMUM_LENGTH) -> str:
    pass


# clase 
class PasswordVault:
    # Clase principal del gestor de contraseñas.
    # carga datos y cipher de usuarios y contraseñas
    def __init__(self, data_path: str, key_path: str):
        self.data  = self._load_data(data_path)
        self.cipher = self._load_cipher(key_path)
        self.data_path = data_path
        self.key_path = key_path
        

    # metodos publicos

    def login(self, user:str, password:str) -> None: 
        pass

    def list_users(self) -> list[str]:
        pass

    def list_accounts(self, user:str) -> list[dict]:
        pass

    def get_password(self, user:str, account_id:str) -> str:
        pass

    def register(self, user:str, password:str) -> None:
        pass

    def add_account(self, user:str, app:str, username:str, email:str, password:str, type: str | None = None, region: str | None = None, rank: str | None = None) -> str: # devuelve el uuid de la cuenta creada
        pass

    def change_password(self, user:str, account_id:str, new_password:str) -> None:
        pass

    def delete_account(self, user:str, account_id:str) -> None:
        pass   

    # metodos privado
    def _save_data(self) -> None:
        pass

    def _load_data(self, data_path: str) -> dict:
        pass

    def _load_cipher(self, key_path: str) -> Fernet:
        pass