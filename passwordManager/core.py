import exceptions
import json
import hashlib
import secrets
import string
import uuid
import os

from cryptography.fernet import Fernet, InvalidToken
from pathlib import Path
from datetime import datetime,  timedelta

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
    def __init__(self, data_path: str | Path, key_path: str | Path):
        self.data_path = Path(data_path)
        self.key_path = Path(key_path)

        self.data = self._load_data(self.data_path)
        self.cipher = self._load_cipher(self.key_path)

        if self._migrate_data():
            self._save_data()
        

    # metodos publicos

    def login(self, user: str, password: str) -> None:
        if user not in self.data:
            raise exceptions.UserNotFoundException(user)

        if self.data[user]["banUntil"] > datetime.now().timestamp():
            ban_until = datetime.fromtimestamp(self.data[user]["banUntil"])
            raise exceptions.BannedUserException(ban_until)

        password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()

        if self.data[user]["userPassword"] != password_hash:
            self.data[user]["login_attempts"] += 1
            
            if self.data[user]["login_attempts"] >= MAX_LOGIN_ATTEMPTS:
                self.data[user]["banUntil"] = (
                    datetime.now() + timedelta(seconds=BAN_TIME)
                ).timestamp()
                self.data[user]["login_attempts"] = 0

                self._save_data()
                raise exceptions.BannedUserException(
                    datetime.fromtimestamp(self.data[user]["banUntil"])
                )

            self._save_data()
            raise exceptions.WrongPasswordException(MAX_LOGIN_ATTEMPTS - self.data[user]["login_attempts"])

        self.data[user]["login_attempts"] = 0
        self._save_data()

        

    def list_users(self) -> list[str]:
        return list(self.data.keys())
        
    def list_accounts(self, user:str) -> list[dict]:
        clean_user = user.strip()
        if clean_user not in self.data:
            raise exceptions.UserNotFoundException(clean_user)
        local_list = []
        for account in self.data[clean_user]["accounts"]:
            local_dict = {
                "id": account["id"],
                "page/app": account["page/app"],
                "username": account["username"],
                "email": account["email"],
                "account_type": account.get("account_type"),
                "region": account.get("region"),
                "rank": account.get("rank")
            }
            local_list.append(local_dict)
        return local_list

    def get_password(self, user: str, account_id: str) -> str:
        clean_user = user.strip()

        if clean_user not in self.data:
            raise exceptions.UserNotFoundException(clean_user)

        for account in self.data[clean_user]["accounts"]:
            if account_id == account["id"]:
                try:
                    return self.cipher.decrypt(
                        account["password"].encode("utf-8")
                    ).decode("utf-8")

                except InvalidToken:
                    raise exceptions.InvalidKeyException() from None

        raise exceptions.AccountNotFoundException(account_id)


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

    def add_account(self, user:str, app:str, username:str, email:str, password:str, account_type: str | None = None, region: str | None = None, rank: str | None = None) -> str: # devuelve el uuid de la cuenta creada

        clean_user = user.strip()
        if clean_user not in self.data:
            raise exceptions.UserNotFoundException(clean_user)
        clean_app = app.strip()
        if clean_app == "":
            raise exceptions.EmptyFieldException("app")
        clean_username = username.strip()
        if clean_username == "":
            raise exceptions.EmptyFieldException("username")
        clean_email = email.strip()
        if clean_email == "":
            raise exceptions.EmptyFieldException("email")
        clean_password  = password.strip()
        if clean_password == "":
            raise exceptions.EmptyFieldException("password")
        
        ciphered_password = self.cipher.encrypt(clean_password.encode("utf-8")).decode("utf-8")
        local_data = {
                "id": str(uuid.uuid4()),
                "page/app": clean_app,
                "username": clean_username,
                "email": clean_email,
                "password": ciphered_password
        }

        if account_type is not None:
            local_data["account_type"] = account_type
        if region is not None:
            local_data["region"] = region
        if rank is not None:
            local_data["rank"] = rank

        self.data[clean_user]["accounts"].append(local_data)

        self._save_data()

        return self.data[clean_user]["accounts"][-1]["id"]

    def change_password(self, user: str, account_id: str, new_password: str) -> None:
        clean_user = user.strip()

        if clean_user not in self.data:
            raise exceptions.UserNotFoundException(clean_user)

        clean_password = new_password.strip()

        if clean_password == "":
            raise exceptions.EmptyFieldException("password")

        for account in self.data[clean_user]["accounts"]:
            if account_id == account["id"]:
                account["password"] = self.cipher.encrypt(
                    clean_password.encode("utf-8")
                ).decode("utf-8")

                self._save_data()
                return None

        raise exceptions.AccountNotFoundException(account_id)

    def delete_account(self, user: str, account_id: str) -> None:
        clean_user = user.strip()

        if clean_user not in self.data:
            raise exceptions.UserNotFoundException(clean_user)

        accounts = self.data[clean_user]["accounts"]

        new_accounts = [
            account
            for account in accounts
            if account["id"] != account_id
        ]

        if len(new_accounts) == len(accounts):
            raise exceptions.AccountNotFoundException(account_id)

        self.data[clean_user]["accounts"] = new_accounts

        self._save_data()
  

    # metodos privado
    def _save_data(self) -> None:
        temp_path = self.data_path.with_suffix(self.data_path.suffix + ".tmp")

        try:
            with temp_path.open("w", encoding="utf-8") as file:
                json.dump(
                    self.data,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

            temp_path.replace(self.data_path)

        except OSError as e:
            raise exceptions.CannotSaveDataException(
                str(self.data_path), e
            ) from None

        finally:
            if temp_path.exists():
                temp_path.unlink()

    def _load_data(self, data_path: Path) -> dict:
        try:
            with data_path.open("r", encoding="utf-8") as file:
                content = file.read()

                if not content.strip():
                    return {}

                return json.loads(content)

        except FileNotFoundError:
            return {}

        except json.JSONDecodeError:
            raise exceptions.BrokenJsonFileException(
                str(data_path)
            ) from None

    def _load_cipher(self, key_path: Path) -> Fernet:
        try:
            with key_path.open("rb") as file:
                key = file.read()

            return Fernet(key)

        except FileNotFoundError:
            raise exceptions.MissingKeyFileException(
                str(key_path)
            ) from None

        except ValueError:
            raise exceptions.BrokenKeyFileException(
                str(key_path)
            ) from None

    def _migrate_data(self) -> bool:
        changed = False

        for user_data in self.data.values():
            if "login_attempts" not in user_data:
                user_data["login_attempts"] = 0
                changed = True

            if "banUntil" not in user_data:
                user_data["banUntil"] = 0
                changed = True

            if "accounts" not in user_data:
                user_data["accounts"] = []
                changed = True

            for account in user_data["accounts"]:
                if "id" not in account:
                    account["id"] = str(uuid.uuid4())
                    changed = True

                if "type" in account:
                    account["account_type"] = account.pop("type")
                    changed = True

        return changed



