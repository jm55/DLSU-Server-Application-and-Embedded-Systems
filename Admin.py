#Based from: https://morioh.com/p/1d5fd6c04b58

import UI as ui
import socket
import re
import time, datetime
import threading

HEADER = 128
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
IP = ""
PORT = 8080
ADDR = ("", 0)

RFID_SIZE = 1000
RFID_LIST = []
TIME_LIMIT = 10

def setup_client():
    global IP, PORT, ADDR
    IP = input("Enter Target Server IP: ")
    ADDR = (IP, PORT)

def send(msg):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    message = msg.encode(FORMAT)
    client.send(message)
    server_reply = client.recv(2048).decode(FORMAT)
    client.send(DISCONNECT_MESSAGE.encode(FORMAT))
    return server_reply #Replies from server

def add():
    ui.header("ADMIN")
    id = input("Enter ID to ADD: ")
    msg = f"ADD={id}"
    response = send(msg)
    ui.header("ADMIN")
    print("ID:",id,response)
    ui.getch()

def remove():
    ui.header("ADMIN")
    id = input("Enter ID to REMOVE: ")
    msg = f"REM={id}"
    response = send(msg)
    ui.header("ADMIN")
    print("ID:",id,response)
    ui.getch()

monitor = False
def monitor_thread():
    global monitor
    while monitor:
        ui.header("ADMIN")
        msg = f"MON="
        response = send(msg)
        print("P = Premises\nL = Limit\nDB = Database Mem.\n")
        print(f"Updated at {datetime.datetime.now()}")
        print(f"{response}")
        print("Press Enter to return...")
        time.sleep(1)

def monitor():
    global monitor
    mon_thread = threading.Thread(target=monitor_thread)
    monitor = True
    mon_thread.start()
    input("")
    monitor = False
    mon_thread.join()
    return

def search():
    ui.header("ADMIN")
    id = input("Enter ID to search: ")
    msg = f"SER={id}"
    response = send(msg)
    print(f"{response}")
    ui.getch()

def setlim():
    valid = False
    limit = ""
    while not valid:
        ui.header("ADMIN")
        msg = f"MON="
        response = send(msg)
        print(f"{response} people in premises")
        limit = input("Set limit: ")
        if re.match("^[-+]?[0-9]+$",limit):
            valid = True
    msg = f"LIM={limit}"
    response = send(msg)
    print(f"{response}")
    ui.getch()

def menu():
    ret = True
    global IP, PORT
    ui.header("ADMIN")
    print(f"Server: {IP}:{PORT}")
    print("1 - ADD\n2 - REMOVE\n3 - MONITOR\n4 - SEARCH\n5 - SET LIMIT\n0 - EXIT")
    choice = input("Enter choice: ")
    if choice == "1":
        add()
    elif choice == "2":
        remove()
    elif choice == "3":
        monitor()
    elif choice == "4":
        search()
    elif choice == "5":
        setlim()
    elif choice == "0":
        ret = False
    return ret

def main():
    ui.header("ADMIN")
    setup_client()
    running = True
    while running:
        running = menu()

if __name__ == "__main__":
    main()