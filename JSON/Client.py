#Based from: https://morioh.com/p/1d5fd6c04b58

import UI as ui
import socket
import time, datetime
import random
import threading
import re
import JSONParser as jparser

HEADER = 128
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
IP = ""
PORT = 8080
ADDR = ("", 0)
QUIET = False
LATENCY_TOTAL = 0
LATENCY_CTR = 0

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lock = threading.Semaphore(205)

RFID_SIZE = 1000
RFID_LIST = []
TIME_LIMIT = 10

def setup_client():
    global IP
    global PORT
    global ADDR
    IP = input("Enter Target Server IP: ")
    ADDR = (IP, PORT)

def load_ids():
    global RFID_SIZE
    global RFID_LIST
    if input("Use ID List? (Y/N): ").lower() == 'y':
        f = open(input("Enter IDs File: "), 'r')
        while True:
            line = f.readline()
            if not line:
                break
            RFID_LIST.append(re.sub("\n","",line))
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
    print(f"DB: {RFID_SIZE} IDs")

def random_id():
    global RFID_LIST
    global RFID_SIZE
    return RFID_LIST[random.randint(0,RFID_SIZE-1)]

def generate_devid():
    id = random.getrandbits(128)
    dev_id = "%032x\n" % id
    return dev_id[0:7]

def send(msg):
    jsonstring = jparser.writejson("DEV_ID", "TAP", msg)
    message = jsonstring.encode(FORMAT)
    lock.acquire()
    client.send(message)
    server_reply = client.recv(HEADER).decode(FORMAT)
    lock.release()
    return server_reply #Replies from server

def client_worker(thread_id): #For Simulator Only
    global QUIET
    global LATENCY_TOTAL
    global LATENCY_CTR
    while True:
        id = random_id()
        start = time.time()
        ret = send(id)
        parsedval = jparser.cleanresponse(ret)
        latency = round(time.time()-start,2)
        lock.acquire()
        LATENCY_TOTAL += latency
        LATENCY_CTR += 1
        lock.release()
        if not QUIET:
            ui.standardPrint(["Thread " + str(thread_id)], "", id, parsedval, f"({latency}ms)")
            #print(f"{str(datetime.datetime.now()):26s} [Thread ID {str(thread_id):4s}]: {id:32s} - {parsedval:5s} ({round(time.time()-start,2)}ms)")
        if "Unparsable" in parsedval or "Malformed" in parsedval: 
            time.sleep(random.randint(1,TIME_LIMIT)) #slow down the thread

def main():
    global QUIET
    global LATENCY_CTR
    global LATENCY_TOTAL
    ui.header("CLIENT")
    setup_client()
    load_ids()
    threads = int(input("Enter no. of threads: "))
    if input("Quiet Mode (Y/N): ").lower() == "y":
        QUIET = True
    client.connect(ADDR)
    print("Running Threads...")
    for t in range(threads):
        thread = threading.Thread(target=client_worker, args=([t]))
        thread.start()
        #time.sleep(100/1000)
    while True and QUIET:
        if LATENCY_CTR != 0:
            ui.header("CLIENT")
            print(f"No. of Threads: {threads}")
            print(f"No. of Samples: {LATENCY_CTR}")
            print(f"Average Latency: {(LATENCY_TOTAL/LATENCY_CTR):0f}ms")
            time.sleep(1)

if __name__ == "__main__":
    main()