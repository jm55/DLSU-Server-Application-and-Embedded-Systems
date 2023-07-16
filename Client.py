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

rfid_tag_size = 1000
rfid_tags = []
time_limit = 10

def random_id(): #For Simulator Only
    return rfid_tags[random.randint(0,rfid_tag_size-1)]

def random_time(timelimit): #For Simulator Only
    return random.randint(0,timelimit)

def tag_generator(): #For Simulator Only
    for i in range(rfid_tag_size):
        rfid_tags.append("%032x" % random.getrandbits(128))        

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
    header()
    IP = input("Enter Target Server IP: ")
    ADDR = (IP, PORT)
    client.connect(ADDR)
    
def send(msg):
    message = msg.encode(FORMAT)
    #msg_length = len(message)
    #send_length = str(msg_length).encode(FORMAT)
    #end_length += b' ' * (HEADER - len(send_length))
    #client.send(send_length)
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
    tag_generator()
    print(rfid_tags)
    setup_client()
    threads = int(input("Enter no. of threads: "))
    if input("Quiet Mode (Y/N): ").lower() == "y":
        QUIET = True
    for t in range(threads):
        thread = threading.Thread(target=client_worker, args=([t]))
        thread.start()

if __name__ == "__main__":
    main()