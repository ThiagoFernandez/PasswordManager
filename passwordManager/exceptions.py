from datetime import datetime

class VaultException(Exception):
    """Clase base para todas las excepciones del gestor de contraseñas."""
    pass

class UserNotFoundException(VaultException):
    """Excepción lanzada cuando un usuario no es encontrado."""
    pass

class UserAlreadyExistsException(VaultException):
    """Excepción lanzada cuando un usuario ya existe."""
    pass

class WrongPasswordException(VaultException):
    """Excepción lanzada cuando la contraseña proporcionada es incorrecta."""

    def __init__(self, attempts_left):

        super().__init__(f"Wrong password. Attempts left: {attempts_left}")

        self.attempts_left = attempts_left


class BannedUserException(VaultException):
    """Excepción lanzada cuando un usuario está baneado."""

    def __init__(self, ban_until: datetime):

        super().__init__(f"User banned until: {ban_until.strftime('%Y-%m-%d %H:%M:%S')}")
        self.ban_until = ban_until

class AccountNotFoundException(VaultException):
    """Excepción lanzada cuando una cuenta no es encontrada."""
    pass

class InvalidUsernameException(VaultException):
    """Excepción lanzada cuando un nombre de usuario es inválido."""
    pass

class WeakPasswordException(VaultException):
    """Excepción lanzada cuando una contraseña es débil."""

    def __init__(self, broken_rules):

        super().__init__(f"Weak password. Broken rules: {', '.join(broken_rules)}")
        self.broken_rules = broken_rules

class EmptyFieldException(VaultException):
    """Excepción lanzada cuando un campo requerido está vacío."""

    def __init__(self, field_name):

        super().__init__(f"The field '{field_name}' cannot be empty.")
        self.field_name = field_name

class BrokenJsonFileException(VaultException):
    """Excepción lanzada cuando el archivo JSON está roto o malformado."""
    # distingue de archivo vacio, que es un caso aparte y no es un error de formato

    def __init__(self, file_path):

        super().__init__(f"The JSON file at '{file_path}' is broken or malformed.")
        self.file_path = file_path

class MissingKeyFileException(VaultException):
    """Excepción lanzada cuando falta el archivo de clave."""
    
    def __init__(self, key_path):

        super().__init__(f"The key file at '{key_path}' is missing.")
        self.key_path = key_path

class BrokenKeyFileException(VaultException):
    """Excepción lanzada cuando el archivo de clave está roto o malformado."""
    
    def __init__(self, key_path):

        super().__init__(f"The key file at '{key_path}' is broken or malformed.")
        self.key_path = key_path

class CannotSaveDataException(VaultException):
    """Excepción lanzada cuando no se puede guardar el archivo de datos."""
    
    def __init__(self, data_path, original_exception):

        super().__init__(f"Cannot save data to '{data_path}': {original_exception}")
        self.data_path = data_path
        self.original_exception = original_exception