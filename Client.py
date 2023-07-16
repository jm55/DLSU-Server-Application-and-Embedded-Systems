#Based from: https://morioh.com/p/1d5fd6c04b58

import socket
import platform, os
import time, datetime
import random
import threading

HEADER = 128
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
IP = ""
PORT = 8080
ADDR = ("", 0)
QUIET = False

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lock = threading.Lock()

RFID_SIZE = 1000
RFID_LIST = []
TIME_LIMIT = 10

def cls():
    if platform.system() == "Linux":
        os.system("clear")
    elif platform.system() == "Windows":
        os.system("cls")

def header():
    cls()
    print("Client.py")
    print("Escalona, Estebal, Fortiz")
    print("")

def setup_client():
    global IP
    global PORT
    global ADDR
    IP = input("Enter Target Server IP: ")
    ADDR = (IP, PORT)
    client.connect(ADDR)

def load_ids():
    global RFID_SIZE
    global RFID_LIST
    if input("Use existing ID list? (y/n): ").lower() == 'y':
        f = open(input("Input filename/file path: "), 'r')
        while True:
            line = f.readline()
            if not line:
                break
            RFID_LIST.append(line)
        RFID_SIZE = len(RFID_LIST)
    else:
        RFID_SIZE = int(input("Enter no. of IDs to generate: "))
        for i in range(RFID_SIZE):
            valid = False
            while not valid: #To prevent duplicate IDs from being generated
                newID = "%032x" % random.getrandbits(128)
                if newID not in RFID_LIST:
                    RFID_LIST.append(newID)
                    valid = True
    print(RFID_LIST)

def random_id():
    global RFID_LIST
    global RFID_SIZE
    return RFID_LIST[random.randint(0,RFID_SIZE-1)]

def send(msg):
    message = msg.encode(FORMAT)
    client.send(message)
    server_reply = client.recv(2048).decode(FORMAT)
    return server_reply #Replies from server

def client_worker(thread_id): #For Simulator Only
    global QUIET
    while True:
        id = random_id()
        start = time.time()
        ret = send(id)
        if not QUIET:
            print(f"{str(datetime.datetime.now()):26s} [Thread ID {str(thread_id):4s}] | Tapped: {id:32s} - {ret:5s} ({round(time.time()-start,2)}ms)")
        #time.sleep(random_time(time_limit)) #arbitrary sleep to simulate delay to next possible tap of same id

def main():
    global QUIET
    header()
    load_ids()
    setup_client()
    threads = int(input("Enter no. of threads: "))
    if input("Quiet Mode (Y/N): ").lower() == "y":
        QUIET = True
    for t in range(threads):
        thread = threading.Thread(target=client_worker, args=([t]))
        thread.start()

if __name__ == "__main__":
    main()