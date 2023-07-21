#Based from: https://morioh.com/p/1d5fd6c04b58

import UI as ui
import socket 
import threading
import os, platform
import time, datetime
import re
import JSONParser as jparser

FILE = ""
HEADER = 128
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
IP = ""
PORT = 8080
ADDR = ("", 0)
QUIET = False
LIMIT = 1000
DEFAULTLIMIT = 1000

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

def update_db():
    return

def add_user(id:str):
    id = re.sub("ADD=","",id)
    if id in dbMemory:
        return "!ADDED"
    else:
        dbMemory.append(id)
        return "ADDED"
    
def rem_user(id:str):
    id = re.sub("REM=","",id)
    if id not in dbMemory:
        return "!REMOVED"
    else:
        dbMemory.remove(id)
        return "REMOVED"

def search_user(id:str):
    id = re.sub("SER=","",id)
    try:
        dbMemory.index(id)
        return "FOUND"
    except:
        return "NOT FOUND"

def tap(rcv:str):
    if rcv in dbMemory:
        if rcv not in premises:
            if len(premises) < LIMIT:
                premises.append(rcv)
                return "ENTER"
            else:
                return "LIMIT"
        else:
            premises.remove(rcv)
            return "EXIT"
    else:
        return "INVALID"
    
def monitor():
    return f"P:{len(premises)}/L:{LIMIT}/DB:{len(dbMemory)} {round((len(premises)/LIMIT)*100,2)}% Full", "MONITOR"

def setlimit(limit):
    global LIMIT
    if limit is not None:
        LIMIT = int(limit)
        return f"LIMIT SET = {LIMIT}"
    else:
        return "ERROR OCCURED, CURR VAL RETAINED"

def handle_client(conn, addr):
    connected = True
    while connected:
        response = ""
        parsed = None
        parsedcmd = ""
        parsedval = ""
        lock.acquire()
        try:
            rcv = conn.recv(HEADER).decode(FORMAT)
            if rcv == DISCONNECT_MESSAGE:
                connected = False
            elif not ("{" in rcv and "}" in rcv):
                response = jparser.writejson("SERV","ERR","ERROR")
            else: 
                parsed = jparser.readjson(rcv)
                if parsed == None:
                    response = jparser.writejson("SERV","ERR","ERROR")
                else:
                    parsedcmd = parsed['cmd']
                    parsedval = parsed['val']
                    if parsedcmd == "TAP":
                        response = jparser.writejson("SERV", "RES", tap(parsedval))
                    elif parsedcmd == "ADD":
                        response = jparser.writejson("SERV", "RES", add_user(parsedval))
                    elif parsedcmd == "REM":
                        response = jparser.writejson("SERV", "RES", rem_user(parsedval))
                    elif parsedcmd == "MON":
                        response = jparser.writejson("SERV", "RES", monitor()[0])
                    elif parsedcmd == "LIM":
                        response = jparser.writejson("SERV", "RES", setlimit(parsedval))
                    elif parsedcmd == "SER":
                        response = jparser.writejson("SERV", "RES", search_user(parsedval))
                    #print(response)
            if not QUIET and "DISCONNECT" not in rcv:
                parsedresponse = jparser.readjson(response)["val"]
                if parsedcmd == "TAP":
                    print(f"{str(datetime.datetime.now()):26s} | [{addr[0]:15s}]: {parsedval:32s} - {parsedresponse:7s} ({len(premises)}/{LIMIT})")
                else:
                    print(f"{str(datetime.datetime.now()):26s} | [{addr[0]:15s}]: {parsedcmd:3s} - {parsedresponse:7s} ({len(premises)}/{LIMIT})")
        except Exception as e:
            print("EXCEPTION:", rcv)
            print(e.with_traceback)
            response = jparser.writejson("SERV","ERR","ERROR")
        conn.send(response.encode(FORMAT))
        lock.release()
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

def main():
    print("Server is STARTING...")
    start()

if __name__ == "__main__":
    main()