#Based from: https://morioh.com/p/1d5fd6c04b58

import socket 
import threading
import os, platform
import time, datetime
import re

HEADER = 128
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
IP = ""
PORT = 8080
ADDR = ("", 0)
QUIET = False

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lock = threading.Lock()
premises = [] #Will hold all IDs

def cls():
    if platform.system() == "Linux":
        os.system("clear")
    elif platform.system() == "Windows":
        os.system("cls")

def header():
    cls()
    print("Server.py")
    print("Escalona, Estebal, Fortiz")
    print("")

def setup_server():
    global IP
    global PORT
    global ADDR
    global QUIET
    header()
    IP = input("Enter Server IP: ")
    ADDR = (IP, PORT)
    server.bind(ADDR)
    if input("Quiet Mode (y/n): ").lower == "y":
        QUIET = True

def load_memory():
    return

def handle_client(conn, addr):
    #print(f"[NEW CONNECTION] {addr} connected.")
    connected = True
    while connected:
        id = conn.recv(HEADER).decode(FORMAT)
        if len(id) > 32 or len(id) < 32:
            print(id)
            conn.send("ERROR".encode(FORMAT)) #Reply to client
        else:
            enter = True
            lock.acquire()
            if id not in premises:
                premises.append(id)
                conn.send("ENTER".encode(FORMAT)) #Reply to client
            else:
                premises.remove(id)
                conn.send("EXIT".encode(FORMAT))
                enter = False
            lock.release()
            if not QUIET:
                if enter:
                    print(f"{str(datetime.datetime.now()):26s} | [{addr[0]:15s}]: {id:32s} ENTER ({len(premises)}pax)")
                else:
                    print(f"{str(datetime.datetime.now()):26s} | [{addr[0]:15s}]: {id:32s} EXIT ({len(premises)}pax)")
    conn.close()

def start():
    setup_server()
    server.listen()
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