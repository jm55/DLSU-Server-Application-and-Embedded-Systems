import platform, os
import datetime

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

def exception(cause:str, e:Exception, addr:str):
    print("------------------------------")
    if cause: print("EXCEPTION:", cause)
    print("Error:", e)
    print("Traceback:", e.with_traceback)
    print("Client:", addr)
    print("------------------------------")

def standardPrint(addr, cmd:str, val:str, res:str, rate:str):
    if addr == "localhost":
        addr = ["localhost", "0"]
    if cmd == "TAP":
        print(f"{str(datetime.datetime.now()):26s} [{addr[0]:15s}]: {str(val):32s} - {res:7s} {rate}", flush=False)
    elif cmd == "ADD" or cmd == "REMOVE":
        print(f"{str(datetime.datetime.now()):26s} [{addr[0]:15s}]: {str(val):32s} - {res:7s} {rate}", flush=False)
    elif cmd != "MON":
        print(f"{str(datetime.datetime.now()):26s} [{addr[0]:15s}]: {cmd} {str(val)} - {res:7s} {rate}", flush=False)
    return