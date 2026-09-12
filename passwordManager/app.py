#LIBRERIAS
import random, json, string, hashlib, pwinput, time, datetime
from cryptography.fernet import Fernet

def checkInactivity(t):
    timeout = 60 # cambialo como vos quieras gordito
    if time.time() - t >= timeout:
        print("Session expired. Please login again")
        return userSelector()

    return

def showPageApp(a):
    cont = 0
    for i in data[a]["accounts"]:
        cont+= 1
        print(f'{cont}. {data[a]["accounts"][cont-1]["page/app"]}')
    while True:
        try:
            pageApp = int(input(f"Choose an option between 1 - {cont}\n(-1 to return to the menu): ")) - 1
            if 0 <= pageApp < cont:
                break
            elif pageApp == -2:
                print("back to the main menu")
                break
            else:
                print("Invalid option, please try again.")
        except ValueError:
            print("The option must be a number")
    return pageApp


#INICIO
def optionSelector():
    while True:
        try:
            option = int(input("Choose an option between 1-8: "))
            while option not in[1, 2, 3, 4, 5, 6, 7, 8]:
                option = int(input("INVALID OPTION | TRY AGAIN\nChoose an option between 1-8: "))
            break
        except ValueError:
            print("The option must be a number")
    return option

def userSelector():
    print(f"{'Welcome to the user selector':-^60}\n1. Login\n2. Register\n3. Exit")
    while True:
        try:
            option = int(input("Choose an option between 1-2-3: "))
            if 1 <= option <= 2:
                break
            elif option == 3:
                return "exit"
            else:
                print("Please, the option must be between 1-2")
        except ValueError:
            print("The option must be a number")

    if option == 1:
        while True:
            print("Who are you?")
            cont = 1
            for user in users:
                print(f"{cont}. {user}")
                cont+=1
            print(f"{cont}. Exit")
            try:
                User = int(input(f"Choose an option between 1 - {len(users)}: "))
                if User == cont:
                    return "exit"
                tempActiveUser = users[User-1]
                if time.time() < data[tempActiveUser]["banUntil"]:
                    banTime=datetime.datetime.fromtimestamp(data[tempActiveUser]["banUntil"])
                    print(f"User's still banned\nBan until {banTime.strftime('%Y-%m-%d %H:%M:%S')}\nTry another user")
                else:
                    data[tempActiveUser]["banUntil"] = 0
                    with open("../../dataNoTocar.json", "w") as f:
                        json.dump(data, f, indent=4)
                    break
            except ValueError:
                print("The option must be a number")
            except IndexError:
                print(f"The options must be between 1 - {len(users)}")

        attempt = 0
        while True:
            if attempt != 3:
                checkPassword = pwinput.pwinput(prompt="Write your user password: ", mask="*")
                hashPass = hashlib.sha256(checkPassword.encode("utf-8")).hexdigest()
                if hashPass == data[tempActiveUser]["userPassword"]:
                    break
                else:
                    print("WRONG PASSWORD | TRY AGAIN")
                    attempt+=1
            else:
                ban = datetime.datetime.now() + datetime.timedelta(minutes= 5)
                banTs = int(ban.timestamp())
                data[tempActiveUser]["banUntil"] = banTs
                with open("../../dataNoTocar.json", "w") as f:
                    json.dump(data, f, indent=4)
                print(f"BANHAMMER!\n5 minutes ban")
                return "banned"
        print("succesfull login")
        return tempActiveUser

    else:
        newUser = input("Choose a name: ")
        while True:
            newPass = pwinput.pwinput(prompt="Create a password: ", mask="*")
            checkNewPass = pwinput.pwinput(prompt="Write it again to confirm: ", mask="*")
            if newPass == checkNewPass:
                hashpass = hashlib.sha256(newPass.encode("utf-8")).hexdigest()
                data[newUser] = {
                    "userPassword": hashpass,
                    "accounts": []
                }
                with open("../../dataNoTocar.json", "w") as f:
                    json.dump(data, f, indent=4)
                tempActiveUser = newUser
                return tempActiveUser
            else:
                print("The passwords do not match")
# CLAVES Y CIFRADO
def saveKey(): #llamarla solo la primera vez que usas el programa
    key = Fernet.generate_key()
    with open("key.key", "wb") as f:
        f.write(key)

def loadKey():
    """Carga la clave desde el archivo key.key"""
    with open("key.key", "rb") as f:
        return f.read()

#/////////////////////////////

def pedirCampo(name):
    value = input(f"Write your {name}: ").strip()
    while value == "":
        value = input(f"NOT ALLOWED EMPTY TEXT\nWrite your {name}: ").strip()
    return value

#opciones
#option 1
def searchPassword(a):
    print(f"{'Welcome to the password searcher':-^60}\nWhich page or app are you looking for?")
    pageApp = showPageApp(activeUser)
    if pageApp == -2:
        return
    else:
        encryptedPassword = data[a]["accounts"][pageApp]["password"]
        decryptedPassword = cipher.decrypt(encryptedPassword.encode()).decode()
        print(f'The password for {data[a]["accounts"][pageApp]["page/app"]} is {decryptedPassword}')
        return print("back to the main menu")

#option 2
def addAccount(a):
    print(f"{'Welcome to the account adder':-^68}\nWhich page or app are you adding?")

    newAppPage = input("Write the name: ").strip()
    while newAppPage == "":
        newAppPage = input("NOT ALLOWED EMPTY TEXT\nWrite the name: ").strip()

    opcionales = {
        "type": "Do you need a type?",
        "region": "Do you need a region?",
        "rank": "Do you need a rank?"
    }

    extra_fields = {}
    keys = list(opcionales.keys())
    cont=0
    while cont < len(keys):
        campo = keys[cont]
        pregunta = opcionales[campo]
        respuesta = input(f"{pregunta}\nyes or no\n(-1 to go back): ").strip().lower()

        if respuesta == "-1":
            if cont > 0:
                cont-=1
                continue
            else:
                print("You are at the first field, cannot go back further")
                continue
        if respuesta == "yes":
            valor = input(f"Write your {campo}: ")
            extra_fields[campo] = valor
        cont+=1

    newUsername = pedirCampo("username")
    newEmail = pedirCampo("email")
    newPassword = pedirCampo("password")

    encryptedPassword = cipher.encrypt(newPassword.encode()).decode()
    newAccount = {
        "page/app": newAppPage,
        "username": newUsername,
        "email": newEmail,
        "password": encryptedPassword,
        **extra_fields
    }

    print("\nNew account has been created:", newAccount)
    option = input("Do you want to save it?\nyes or no: ").strip().lower()
    if option == "yes":
        data[a]["accounts"].append(newAccount)
        with open("../../dataNoTocar.json", "w") as f:
            json.dump(data, f, indent=4)
        print("The account has been saved")
    return print("back to the main menu")

#option 3
def changePassword(a):
    while True:
        print(f"{'Welcome to the password changer':-^60}\nWhich page or app are you looking for?")
        pageApp = showPageApp(activeUser)
        if pageApp == -2:
            return
        else:
            print(f"{data[a]["accounts"][pageApp]}\nIs this the account you want to change the password?")
            option = input("yes or no: ").strip().lower()

            if option=="yes":
                newPassword = input("Write the new password: ")
                while newPassword=="":
                    newPassword = input(f"The password cannot be empty\nWrite the new password: ")
                cipherNewPassword= cipher.encrypt(newPassword.encode()).decode()
                data[a]["accounts"][pageApp]["password"] = cipherNewPassword
                print(f"Result: {data[a]["accounts"][pageApp]}")
                confirm = input(f"Do you want to confirm?\nyes or no: ").strip().lower()
                with open("../../dataNoTocar.json", "w") as f:
                    json.dump(data, f, indent=4)
                print("The password has been changed and saved")
                return print("back to the main menu")


#option 4
def createPassword(a):
    print(f"{'Welcome to the passwordCreator':-^60}\nFor what page do you want to create a password?: ")
    print(f"These are some rules to create a password:\n1. Include highercase\n2. Include lowercase\n3. Include symbols(ex:@, #, &, $)\n4. Minimun lenght of 12 characters\n5. Include numbers")
    mode = input("Do you want to us to randomize the password?\nyes or no: ").strip().lower()

    if mode == "yes":
        randomPassword = [
            random.choice(string.ascii_uppercase),
            random.choice(string.ascii_lowercase),
            random.choice(string.digits),
            random.choice(string.punctuation)
    ]

        todos = string.ascii_letters + string.digits + string.punctuation
        while len(randomPassword) < 12:
            randomPassword.append(random.choice(todos))

        random.shuffle(randomPassword)
        randomPassword = "".join(randomPassword)

        print(f"Result: {randomPassword}")
        option = input("Do you want to use it?\nyes or no: ").strip().lower()
        if option == "yes":
            print("Choose the page or app")
            cont = 0
            for i in data[a]["accounts"]:
                cont += 1

                print(f"{cont}. {data[a]["accounts"][cont-1]['page/app']}")
            while True:
                try:
                    pageApp = int(input(f"Choose an option between 1 - {cont}: ")) - 1
                    if 0 <= pageApp < cont:
                        break
                    else:
                        print("Invalid option, please try again.")
                except ValueError:
                    print("The option must be a number")
            cipherRandomPassword = cipher.encrypt(randomPassword.encode()).decode()
            data[a]["accounts"][pageApp]["password"] = cipherRandomPassword
            print(f"result: {data[a]["accounts"][pageApp]}")
            with open("../../dataNoTocar.json", "w") as f:
                json.dump(data, f, indent=4)
            return print("back to the main menu")
        else:
            return print("back to the main menu")

    else:
        while True:
            passwordCreated = input("\nWrite your new password: ")

        # reglas calculadas en base a lo que acaba de escribir
            rules = {
                "At least one uppercase": any(c.isupper() for c in passwordCreated),
                "At least one lowercase": any(c.islower() for c in passwordCreated),
                "At least one number": any(c.isdigit() for c in passwordCreated),
                "At least one symbol": any(c in string.punctuation for c in passwordCreated),
                "Minimum length of 12": len(passwordCreated) >= 12
            }

            for rule, passed in rules.items():
                print(f"{rule}: {'PASSED' if passed else 'FAILED'}")

            if all(rules.values()):
                print("Strong password created!")
                break
            else:
                print("Weak password, please try again.")

        option = input("Do you want to use it?\nyes or no: ").strip().lower()
        if option=="yes":
            print("Choose the page or app")
            pageApp = showPageApp(activeUser)
            if pageApp == -2: # lazy fix
                return
            cypherPasswordCreated = cipher.encrypt(passwordCreated.encode()).decode()
            data[a]["accounts"][pageApp]["password"] = cypherPasswordCreated
            print(f"result: {data[a]["accounts"][pageApp]}")
            with open("../../dataNoTocar.json", "w") as f:
                json.dump(data, f, indent=4)
            return print("back to the main menu")
        else:
            return print("back to the main menu")

#option 5
def deleteAccount(a):
    print(f"{'Welcome to the password deleter':-^60}\nFor what page do you want to delete a password?: ")
    pageApp = showPageApp(activeUser)
    if pageApp == -2:
        return # lazy fix
    print(f"{data[a]["accounts"][pageApp]}\nIs this the account you want to delete?")
    option = input("yes or no: ").strip().lower()
    if option == "yes":
        del data[a]["accounts"][pageApp]
        option = input(f"Do you want to confirm the changes?\nyes or no: ").strip().lower()
        if option == "yes":
            with open("../../dataNoTocar.json", "w") as f:
                json.dump(data, f, indent=4)
            print("The change has been done")
    return print("back to the main menu")
#option 7
def allThePasswords(a):
    cont = 0
    for cuenta in data[a]["accounts"]:
        cont+=1
        encryptedPassword = data[a]["accounts"][cont-1]["password"]
        decryptedPassword = cipher.decrypt(encryptedPassword.encode()).decode()
        print(f"{cont}. Page/App: {cuenta['page/app']} | User: {cuenta['username']} | Password: {decryptedPassword}")
    return print("back to the main menu")


#start
try:
    with open("../../dataNoTocar.json", "r") as f:
        data = json.load(f)
except FileNotFoundError:
    print("No data file found. Creating a new one...")
    data = {}
    with open("../../dataNoTocar.json", "w") as f:
        json.dump(data, f, indent=4)
except json.JSONDecodeError:
    print("Empty file, starting...")
    data = {}


users = list(data.keys())

#saveKey()
key = loadKey()
cipher = Fernet(key)



#user selector

activeUser = userSelector()
while activeUser == "banned":
    activeUser = userSelector()

lastAction = time.time()

print(activeUser)
#main menu
if activeUser != "exit":
    while True:
        print(f"{'MAIN MENU':-^19}")
        print("1. Search a password\n2. Add an account\n3. Change a password\n4. Create a password\n5. Delete a password\n6. Hash a password\n7. All the passwords\n8. Exit")

        match optionSelector():
            case 1:
                checkInactivity(lastAction)
                print("1. You've selected the option 1 - Search a password")
                searchPassword(activeUser)
                lastAction = time.time()
            case 2:
                checkInactivity(lastAction)
                print("2. You've selected the option 2 - Add an account")
                addAccount(activeUser)
                lastAction = time.time()
            case 3:
                checkInactivity(lastAction)
                print("3. You've selected the option 3 - Change a password")
                changePassword(activeUser)
                lastAction = time.time()
            case 4:
                checkInactivity(lastAction)
                print("4. You've selected the option 4 - Create a password")
                createPassword(activeUser)
                lastAction = time.time()
            case 5:
                checkInactivity(lastAction)
                print("5. You've selected the option 5 - Delete an account")
                deleteAccount(activeUser)
                lastAction = time.time()
            case 6:
                print("6. You've selected the option 6 - Hash a password")
                #no me convence
            case 7:
                checkInactivity(lastAction)
                print("7. You've selected the option 7 - All the passwords")
                allThePasswords(activeUser)
                lastAction = time.time()
            case 8:
                print("8. You've selected the option 8 - Exit")
                break
