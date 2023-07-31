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

lock = threading.Lock()
MERGE_LIMITS = 0

def setup_client():
    global IP, PORT, ADDR
    IP = input("Enter Target Server IP: ")
    ADDR = (IP, PORT)

def send(msg):
    completed = False
    server_reply = ""
    while not completed:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(ADDR)
            message = msg.encode(FORMAT)
            client.send(message)
            server_reply = client.recv(2048).decode(FORMAT)
            client.send(DISCONNECT_MESSAGE.encode(FORMAT))
            completed = True
        except Exception as e:
            #ui.exception("Admin Send", e, ADDR[0])
            time.sleep(1/1000)
            continue
    return server_reply #Replies from server

def add_service(id, printable:bool):
    id = re.sub("\n", "", id)
    msg = jparser.writejson("ADMIN","ADD",id)
    response = send(msg)
    if printable:
        print(f"ID: {id} - {jparser.cleanresponse(response)}")

    return jparser.cleanresponse(response)

def add():
    ui.header("ADMIN")
    id = input("Enter ID to ADD: ")
    parsedval = add_service(id, False)
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

def monitor_request():
    msg = jparser.writejson("ADMIN","MON","_")
    response = send(msg)
    parsedval = jparser.cleanresponse(response)
    print("P = Premises\nL = Limit\nDB = Database Mem.\n")
    print(f"Updated at {datetime.datetime.now()}")
    print(f"{parsedval}")

set_monitor = False
def monitor_thread():
    global set_monitor
    while set_monitor:
        ui.header("ADMIN")
        monitor_request()
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

def removeFinished(threads:list):
    lock.acquire()
    for t in threads:
        if not t.is_alive():
            threads.remove(t)
    lock.release()

def merge():
    ui.header("ADMIN")
    mergeFile = input("Enter file to merge to current DB file: ")
    start = 0
    if input("Confirm merge this file to current DB (Y/N): ").capitalize() == "Y":
        ui.header("ADMIN")
        print(f"Merging {mergeFile} to DB...")
        merge_threads = []
        start = time.time()
        with open(mergeFile, 'r') as mf:
            lines = mf.readlines()
            for ctr in range(len(lines)):
                add_service(lines[ctr], False)
                ui.header("ADMIN")
                print(f"{ctr}/{len(lines)} ({((ctr/len(lines))*100):.2f}%) Completed")
    ui.header("ADMIN")
    print(f"Time taken: {(time.time()-start):.2f}s")
    monitor_request()
    ui.getch()
    return

def menu():
    ret = True
    global IP, PORT
    ui.header("ADMIN")
    print(f"Server: {IP}:{PORT}")
    print("1 - ADD\n2 - REMOVE\n3 - MERGE\n4 - MONITOR\n5 - SEARCH\n6 - SET LIMIT\n0 - EXIT")
    choice = input("Enter choice: ")
    if choice == "1":
        add()
    elif choice == "2":
        remove()
    elif choice == "3":
        merge()
    elif choice == "4":
        monitor()
    elif choice == "5":
        search()
    elif choice == "6":
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