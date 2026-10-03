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
AMOUNT_CHARACTERS = 4 # Cantidad de caracteres que se asegura que estén presentes en la contraseña generada (1 mayúscula, 1 minúscula, 1 número, 1 símbolo)

# funciones sueltas
def validate_password(password: str) -> dict[str, bool]:
    rules = {
                    "At least one uppercase": any(c.isupper() for c in password),
                    "At least one lowercase": any(c.islower() for c in password),
                    "At least one number": any(c.isdigit() for c in password),
                    "At least one symbol": any(c in string.punctuation for c in password),
                    "Minimum length of 12": len(password) >= MINIMUM_LENGTH,
                    "Maximum length of 64": len(password) <= MAXIMUM_LENGTH
                }
    return rules

def generate_password(length: int = MINIMUM_LENGTH) -> str:
    if length < MINIMUM_LENGTH or length > MAXIMUM_LENGTH:
            raise ValueError(f"Password length must be between {MINIMUM_LENGTH} and {MAXIMUM_LENGTH} characters.")

    characters = string.ascii_letters + string.digits + string.punctuation

    password = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.digits),
        secrets.choice(string.punctuation)
    ]

    password += [
        secrets.choice(characters)
        for _ in range(length - AMOUNT_CHARACTERS)
    ]

    secrets.SystemRandom().shuffle(password)

    return ''.join(password)


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