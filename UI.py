import platform, os

def cls():
    if platform.system() == "Linux":
        os.system("clear")
    elif platform.system() == "Windows":
        os.system("cls")

def header(file):
    cls()
    print(f"{file}.py")
    print("Escalona, Estebal, Fortiz")
    print("")

def getch():
    input("Press Enter to continue...")