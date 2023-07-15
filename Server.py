#Based from: https://morioh.com/p/1d5fd6c04b58

import socket 
import threading
import os, platform
import time, datetime

HEADER = 128
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
IP = ""
PORT = 8080
ADDR = ("", 0)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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
    header()
    IP = input("Enter Server IP: ")
    ADDR = (IP, PORT)
    server.bind(ADDR)

def handle_client(conn, addr):
    #print(f"[NEW CONNECTION] {addr} connected.")
    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if len(msg_length) >= 3: 
            try:
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode(FORMAT)
                print(f"{datetime.datetime.now()} | [{addr[0]}]: {msg}")
                conn.send("OK".encode(FORMAT)) #Reply to client
            except:
                conn.send("ERROR".encode(FORMAT)) #Reply to client
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