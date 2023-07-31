#Based from: https://morioh.com/p/1d5fd6c04b58

import UI as ui
import socket 
import threading
import os, platform
import time, datetime
import re
import JSONParser as jparser

FILE = ""
LASTUPDATE = 0
HEADER = 128
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
IP = ""
PORT = 8080
ADDR = ("", 0)
QUIET = False
LIMIT = 100000
DEFAULTLIMIT = 100000
UPDATE_CYCLE = 30 #in seconds

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lock = threading.Semaphore(200)
dbMemory = [] #Will hold all IDs Registered IDs; Acts as database
premises = [] #Will hold all IDs in Premises

def setup_server():
    global IP,PORT,ADDR,QUIET
    ui.header("SERVER")
    IP = input("Enter Server IP: ")
    ADDR = (IP, PORT)
    server.bind(ADDR)
    if input("Quiet Mode (y/n): ").lower() == "y":
        QUIET = True

def load_memory():
    global FILE
    FILE = input("Enter IDs File: ")
    with open(FILE, 'r') as f:
        lines = f.readlines()
        for line in lines:
            dbMemory.append(re.sub("\n","",line))
        f.close()
    return

def add_user(id:str):
    id = re.sub("ADD=","",id)
    if id in dbMemory:
        return "!ADDED"
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
    global QUIET
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
                response = jparser.errjson("SERV","Malformed RCV")
            else: 
                parsed = jparser.readjson(rcv)
                if parsed == None:
                    response = jparser.errjson("SERV","Unparseable RCV")
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
                ui.standardPrint(addr, parsedcmd, parsedval, jparser.readjson(response)["val"], f"({len(premises)}/{LIMIT})")
            conn.send(response.encode(FORMAT))
        except Exception as e:
            ui.exception(rcv, e, addr)
            response = jparser.errjson("SERV","SRV Exception")
            conn.close()
            lock.release()
            return
        lock.release()
    conn.close()
    return

def update_db():
    global LASTUPDATE
    global FILE
    global dbMemory
    LASTUPDATE = time.time()
    while True:
        if time.time() - LASTUPDATE >= UPDATE_CYCLE:
            ui.standardPrint("localhost", "UDB", "Updating DB File...", "ONGOING", "")
            try:
                f = open(FILE, mode="w")
                lock.acquire()
                dbMemory = list(dict.fromkeys(dbMemory))
                for id in dbMemory:
                    f.write(id + "\n")
                lock.release()
                f.flush()
                f.close()
                ui.standardPrint("localhost", "UDB", "DB File Update", "OK", "")
            except Exception as fileExcept:
                ui.standardPrint("localhost", "UDB", "DB File Update", "FAILED", "")
                ui.exception("updateDB", fileExcept, "localhost")
                continue
            LASTUPDATE = time.time()

def start():
    setup_server()
    load_memory()
    print("FILE:", FILE)
    server.listen()
    print("")
    print(f"DB Updates every {UPDATE_CYCLE} seconds.")
    print(f"DB Memory: {len(dbMemory)} IDs")
    print(f"Server is LISTENING on {IP}:{PORT}...")
    print("")
    dbThread = threading.Thread(target=update_db)
    dbThread.start()
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

def main():
    print("Server is STARTING...")
    start()

if __name__ == "__main__":
    main()
