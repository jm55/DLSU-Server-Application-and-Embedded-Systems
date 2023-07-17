#Based from: https://morioh.com/p/1d5fd6c04b58

import UI as ui
import socket 
import threading
import os, platform
import time, datetime
import re

FILE = ""
HEADER = 128
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
IP = ""
PORT = 8080
ADDR = ("", 0)
QUIET = False
LIMIT = 1000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lock = threading.Lock()
dbMemory = [] #Will hold all IDs Registered IDs; Acts as database
premises = [] #Will hold all IDs in Premises

def setup_server():
    global IP,PORT,ADDR,QUIET,FILE
    ui.header("SERVER")
    IP = input("Enter Server IP: ")
    ADDR = (IP, PORT)
    server.bind(ADDR)
    if input("Quiet Mode (y/n): ").lower == "y":
        QUIET = True

def load_memory():
    FILE = input("Enter IDs File: ")
    with open(FILE, 'r') as f:
        lines = f.readlines()
        for line in lines:
            dbMemory.append(re.sub("\n","",line))
    return

def handle_client(conn, addr):
    global LIMIT
    connected = True
    while connected:
        lock.acquire()
        response = ""
        rcv = conn.recv(HEADER).decode(FORMAT)
        if rcv == DISCONNECT_MESSAGE:
            connected = False
        elif len(rcv) != 32 and "=" not in rcv:
            print("ERROR: ", rcv)
            response = "ERROR"
        elif (len(rcv) < 32 or len(rcv) < 32+4) and "=" in rcv: #Admin Controls
            if "ADD=" in rcv:
                id = re.sub("ADD=","",rcv)
                dbMemory.append(id)
                response = "ADD"
            if "REM=" in rcv:
                id = re.sub("REM=","",rcv)
                dbMemory.remove(id)
                response = "ADD"
            if "MON=" in rcv:
                rcv = "MONITOR"
                response = f"P:{len(premises)}/L:{LIMIT}/DB:{len(dbMemory)}"
            if "LIM=" in rcv:
                rcv = re.sub("LIM=","",rcv)
                LIMIT = int(rcv)
                response = f"LIMIT SET = {LIMIT}"
            if "SER=" in rcv:
                id = re.sub("SER=","",rcv)
                try:
                    dbMemory.index(id)
                    response = "FOUND"
                except:
                    response = "NOT FOUND"
        else: #Normal ID
            if rcv in dbMemory:
                if rcv not in premises:
                    if len(premises) < LIMIT:
                        premises.append(rcv)
                        response = "ENTER"
                    else:
                        response = "LIMIT"
                else:
                    premises.remove(rcv)
                    response = "EXIT"
            else:
                response = "INVALID"
        lock.release()
        if not QUIET and "DISCONNECT" not in rcv:
            print(f"{str(datetime.datetime.now()):26s} | [{addr[0]:15s}]: {rcv:32s} - {response:7s} ({len(premises)}/{LIMIT})")
        conn.send(response.encode(FORMAT))
    conn.close()

def start():
    setup_server()
    load_memory()
    server.listen()
    print("")
    print(f"DB Memory: {len(dbMemory)} IDs")
    print(f"Server is LISTENING on {IP}:{PORT}...")
    print("")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        #print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

def main():
    print("Server is STARTING...")
    start()

if __name__ == "__main__":
    main()