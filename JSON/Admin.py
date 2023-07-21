#Based from: https://morioh.com/p/1d5fd6c04b58

import UI as ui
import socket
import re
import time, datetime
import threading
import JSONParser as jparser

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
    msg = jparser.writejson("ADMIN","ADD",id)
    response = send(msg)
    parsedval = jparser.cleanresponse(response)
    ui.header("ADMIN")
    print("ID:",id,parsedval)
    ui.getch()

def remove():
    ui.header("ADMIN")
    id = input("Enter ID to REMOVE: ")
    msg = jparser.writejson("ADMIN","REM",id)
    response = send(msg)
    parsedval = jparser.cleanresponse(response)
    ui.header("ADMIN")
    print("ID:",id,parsedval)
    ui.getch()

set_monitor = False
def monitor_thread():
    global set_monitor
    while set_monitor:
        ui.header("ADMIN")
        msg = jparser.writejson("ADMIN","MON","_")
        response = send(msg)
        parsedval = jparser.cleanresponse(response)
        print("P = Premises\nL = Limit\nDB = Database Mem.\n")
        print(f"Updated at {datetime.datetime.now()}")
        print(f"{parsedval}")
        print("\nPress Enter to return...")
        time.sleep(1)

def monitor():
    global set_monitor
    mon_thread = threading.Thread(target=monitor_thread)
    set_monitor = True
    mon_thread.start()
    input("")
    set_monitor = False
    mon_thread.join()
    return

def search():
    ui.header("ADMIN")
    id = input("Enter ID to search: ")
    msg = jparser.writejson("ADMIN","SER",id)
    response = send(msg)
    parsedval = jparser.cleanresponse(response)
    ui.header("ADMIN")
    print(f"ID: {parsedval}")
    ui.getch()

def setlim():
    valid = False
    limit = ""
    while not valid:
        ui.header("ADMIN")
        msg = jparser.writejson("ADMIN","MON","")
        response = send(msg)
        parsedval = jparser.cleanresponse(response)
        print(f"{parsedval} people in premises\n")
        limit = input("Set limit: ")
        if re.match("^[-+]?[0-9]+$",limit):
            valid = True
    msg = jparser.writejson("ADMIN","LIM", limit)
    response = send(msg)
    parsedval = jparser.cleanresponse(response)
    print(f"\n{parsedval}")
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