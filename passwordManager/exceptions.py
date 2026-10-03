from datetime import datetime

class VaultException(Exception):
    """Clase base para todas las excepciones del gestor de contraseñas."""
    pass

class UserNotFoundException(VaultException):
    """Excepción lanzada cuando un usuario no es encontrado."""
    pass

class UserExistsException(VaultException):
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
