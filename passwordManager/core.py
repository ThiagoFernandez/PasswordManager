import exceptions
import json
import hashlib
import secrets
import string
import uuid
import os

from cryptography.fernet import Fernet
from pathlib import Path
from datetime import datetime, timedelta

MINIMUM_LENGTH = 12
MAXIMUM_LENGTH = 64
MAX_LOGIN_ATTEMPTS = 3
BAN_TIME = 300 # Tiempo de ban en segundos (5 minutos)


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
        for _ in range(length - len(password))
    ]

    secrets.SystemRandom().shuffle(password)

    return ''.join(password)


# clase 
class PasswordVault:
    # Clase principal del gestor de contraseñas.
    # carga datos y cipher de usuarios y contraseñas
    def __init__(self, data_path: str, key_path: str):
        self.data = self._load_data(data_path)
        self.data_path = data_path
        self.key_path = key_path
        self.cipher = self._load_cipher(key_path)

        if self._migrate_data():
            self._save_data()
        

    # metodos publicos

    def login(self, user:str, password:str) -> None: 
        pass

    def list_users(self) -> list[str]:
        return list(self.data.keys())
        
    def list_accounts(self, user:str) -> list[dict]:
        pass

    def get_password(self, user:str, account_id:str) -> str:
        pass

    def register(self, user:str, password:str) -> None:
        cleaned_user = user.strip()
        if cleaned_user == "":
            raise exceptions.EmptyFieldException("username")
        if cleaned_user in self.data:
            raise exceptions.UserAlreadyExistsException(cleaned_user)
        
        broken_rules = [rule for rule, passed in validate_password(password).items() if not passed]
        if broken_rules:
            raise exceptions.WeakPasswordException(broken_rules)
        
        self.data[cleaned_user] = {
            "userPassword": hashlib.sha256(password.encode("utf-8")).hexdigest(),
            "accounts": [],
            "login_attempts": 0,
            "banUntil": 0
        }
        self._save_data()

    def add_account(self, user:str, app:str, username:str, email:str, password:str, type: str | None = None, region: str | None = None, rank: str | None = None) -> str: # devuelve el uuid de la cuenta creada
        pass

    def change_password(self, user:str, account_id:str, new_password:str) -> None:
        pass

    def delete_account(self, user:str, account_id:str) -> None:
        pass   

    # metodos privado
    def _save_data(self) -> None:
        temp_path = self.data_path + ".tmp"

        try:
            with open(temp_path, "w", encoding="utf-8") as file:
                json.dump(self.data, file, indent=4, ensure_ascii=False)

            os.replace(temp_path, self.data_path)

        except OSError as e:
            raise exceptions.CannotSaveDataException(
                self.data_path, e
            ) from None

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


    def _load_data(self, data_path: str) -> dict:
        try:
            with open(data_path, 'r', encoding='utf-8') as file:
                content = file.read()

                if not content.strip():
                    return {}

                return json.loads(content)

        except FileNotFoundError:
            return {}

        except json.JSONDecodeError:
            raise exceptions.BrokenJsonFileException(data_path) from None


    def _load_cipher(self, key_path: str) -> Fernet:
        try:
            with open(key_path, 'rb') as file:
                key = file.read()

            return Fernet(key)

        except FileNotFoundError:
            raise exceptions.MissingKeyFileException(key_path) from None

        except ValueError:
            raise exceptions.BrokenKeyFileException(key_path) from None

    def _migrate_data(self) -> bool:
        changed = False

        for user_data in self.data.values():
            user_data["accounts"] = user_data.get("accounts", [])
            for account in user_data["accounts"]:
                if "id" not in account:
                    account["id"] = str(uuid.uuid4())
                    changed = True

        return changed

