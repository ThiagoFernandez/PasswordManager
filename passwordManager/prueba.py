import os
from pathlib import Path
import core


BASE_DIR = Path(__file__).resolve().parent
DATA = BASE_DIR / "prueba" / "reg.json"
KEY = BASE_DIR / "prueba" / "key_prueba.key"


# Arrancar siempre de cero, así la prueba da lo mismo cada vez
if os.path.exists(DATA):
    os.remove(DATA)


v = core.PasswordVault(DATA, KEY)


def probar(nombre, funcion):
    try:
        funcion()
        print(nombre, "-> OK, sin excepción")
    except Exception as e:
        print(nombre, "->", type(e).__name__, ":", e)


# ============================================================
# REGISTER / LOGIN
# ============================================================

v.register("ana", "Abcdefghij1!")


probar(
    "1. usuario fantasma",
    lambda: v.login("fantasma", "x")
)

probar(
    "2. login correcto",
    lambda: v.login("ana", "Abcdefghij1!")
)

probar(
    "3. clave mal (1)",
    lambda: v.login("ana", "mal")
)

probar(
    "4. clave mal (2)",
    lambda: v.login("ana", "mal")
)

probar(
    "5. clave mal (3)",
    lambda: v.login("ana", "mal")
)

probar(
    "6. baneada, clave MAL",
    lambda: v.login("ana", "mal")
)

probar(
    "7. baneada, clave BUENA",
    lambda: v.login("ana", "Abcdefghij1!")
)


print(
    "estado de ana:",
    v.data["ana"]["login_attempts"],
    v.data["ana"]["banUntil"]
)


# Simulo que ya pasaron los 5 minutos
v.data["ana"]["banUntil"] = 0


probar(
    "8. ban vencido, clave BUENA",
    lambda: v.login("ana", "Abcdefghij1!")
)


# ============================================================
# ADD ACCOUNT
# ============================================================

print("\n--- add_account ---")


# A. Primera cuenta
id1 = v.add_account(
    "ana",
    "Steam",
    "zanto",
    "z@mail.com",
    "clave123"
)

print("id1:", id1)


probar(
    "A. app vacía",
    lambda: v.add_account(
        "ana",
        "",
        "zanto",
        "z@mail.com",
        "x"
    )
)


# B. Otra cuenta Steam idéntica
id2 = v.add_account(
    "ana",
    "Steam",
    "zanto",
    "z@mail.com",
    "clave123"
)

print("id2:", id2)
print("id1 != id2:", id1 != id2)


# C. Usuario "fantasma"
probar(
    "C. usuario fantasma",
    lambda: v.add_account(
        "fantasma",
        "Steam",
        "zanto",
        "z@mail.com",
        "clave123"
    )
)


# D. Usuario " ana " con espacios
probar(
    "D. usuario con espacios",
    lambda: v.add_account(
        " ana ",
        "Steam",
        "zanto",
        "z@mail.com",
        "clave123"
    )
)


# E. Cuenta con type="main"
id3 = v.add_account(
    "ana",
    "Steam",
    "zanto2",
    "z2@mail.com",
    "clave456",
    account_type="main"
)

print("id3:", id3)

# ============================================================
# LIST ACCOUNTS
# ============================================================

print("\n--- list_accounts ---")

accounts = v.list_accounts("ana")


# 1. Ninguna trae la contraseña
print("\n1. ¿Alguna cuenta trae password?")

for account in accounts:
    print("password" in account)

print("Resultado:", any("password" in account for account in accounts))


# 2. Son copias
print("\n2. Las cuentas son copias")

accounts[0]["email"] = "email_modificado@mail.com"

print("Email en copia:", accounts[0]["email"])
print(
    "Email original:",
    v.data["ana"]["accounts"][0]["email"]
)


# 3. Usuario fantasma
print("\n3. Usuario fantasma")

probar(
    "list_accounts usuario fantasma",
    lambda: v.list_accounts("fantasma")
)


# 4. Los opcionales llegan bien
print("\n4. Cuenta con account_type='main'")

account_id3 = next(
    account
    for account in accounts
    if account["id"] == id3
)

print("Cuenta id3:")
print(account_id3)


# Mostrar las cuentas guardadas
print("\n--- cuentas de ana ---")
print(v.data["ana"]["accounts"])
