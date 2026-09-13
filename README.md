# PasswordManager

Gestor de contraseñas de línea de comandos con soporte para varios usuarios, escrito en Python.
Cifra cada contraseña con Fernet (AES-128-CBC + HMAC-SHA256), pide una contraseña maestra por
usuario y bloquea la cuenta cinco minutos después de tres intentos fallidos.

> **Proyecto de aprendizaje.** Está hecho para practicar criptografía aplicada y manejo de
> estado en disco, no para reemplazar a Bitwarden o KeePass. Leé
> [Limitaciones de seguridad](#limitaciones-de-seguridad) antes de guardar una contraseña de verdad.

---

## Features

- **Varios usuarios en un mismo archivo** — cada uno con su contraseña maestra y su propio conjunto de cuentas
- **Contraseñas cifradas en reposo** — se descifran solo en el momento de mostrarlas
- **Tres intentos y bloqueo de 5 minutos** — el bloqueo se guarda con marca de tiempo, así que sobrevive a cerrar el programa
- **Expiración por inactividad** — pasado el tiempo configurado, vuelve a pedir login
- **Generador con `secrets`** — 16 caracteres, garantizando mayúscula, minúscula, dígito y símbolo
- **Validador de contraseñas propias** — cinco reglas, y te dice cuál falla en vez de un “inválida” genérico
- **Campos opcionales por cuenta** — `type`, `region` y `rank`, útiles para cuentas de juegos o servicios con perfiles
- **Alta, búsqueda, cambio, borrado y listado** de cuentas, con confirmación antes de escribir a disco

---

## Requisitos

**Python 3.12+** (usa f-strings con comillas anidadas del mismo tipo, PEP 701)

```bash
pip install -r requirements.txt
```

`pwinput` para enmascarar la contraseña al tipearla y `cryptography` para el cifrado.

---

## Primera vez

```bash
git clone https://github.com/ThiagoFernandez/PasswordManager.git
cd PasswordManager
pip install -r requirements.txt
```

Generá tu clave de cifrado antes de la primera corrida:

```bash
python -c "from cryptography.fernet import Fernet; open('key.key','wb').write(Fernet.generate_key())"
```

Y arrancá:

```bash
python passwordManager/app.py
```

La primera pantalla te deja registrar un usuario. El archivo de datos se crea solo.

**La clave no se comparte y no se commitea.** Si la perdés, no hay forma de recuperar las
contraseñas guardadas: Fernet no tiene puerta de atrás.

---

## Estructura

```
PasswordManager/
├── key.key              # clave Fernet — no se commitea
├── dataNoTocar.json     # tus cuentas cifradas — no se commitea
├── requirements.txt
└── passwordManager/
    └── app.py           # toda la app
```

Las rutas se calculan desde la ubicación del script, así que podés ejecutarlo desde cualquier
carpeta sin que se creen archivos sueltos.

---

## Formato de datos

```json
{
    "thiago": {
        "userPassword": "<hash de la contraseña maestra>",
        "banUntil": 0,
        "accounts": [
            {
                "page/app": "steam",
                "username": "thiago",
                "email": "thiago@ejemplo.com",
                "password": "<token Fernet>",
                "region": "LATAM"
            }
        ]
    }
}
```

`banUntil` es un timestamp Unix: `0` significa sin bloqueo.

---

## Limitaciones de seguridad

Las conozco y están acá a propósito, porque son la diferencia entre un ejercicio y una
herramienta que se pueda usar en serio:

- **La clave vive al lado de los datos.** Cualquiera con acceso a la carpeta descifra todo. Lo
  correcto es derivar la clave de la contraseña maestra con PBKDF2 y no guardar ningún `key.key`.
- **La contraseña maestra se hashea con SHA-256 sin sal**, que es barato de romper por fuerza
  bruta. Corresponde PBKDF2, bcrypt o argon2.
- **Las contraseñas se imprimen en pantalla** al buscarlas o al listarlas, así que quedan en el
  scrollback de la terminal.
- **Ni `key.key` ni el archivo de datos deben subirse al repo.** El `.gitignore` los cubre.

---

## Próximos pasos

- Derivar la clave de la contraseña maestra con PBKDF2 y eliminar el archivo de clave
- Reemplazar el SHA-256 de la maestra por PBKDF2
- Interfaz gráfica: lista de cuentas con buscador, copiado al portapapeles que se limpie solo y
  bloqueo por inactividad con la ventana abierta
