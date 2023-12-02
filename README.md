# NSAPDEV-NSEMBED - Final-Proj
 
## Project Description

The project is called Crowd Counting System (CCS) which is a crowd logging system that makes use of an RFID reader to keep track of the number of people that are within a particular location by monitoring the number of people entering and exiting a particular premise. 

The inspiration for this project is found in the situations during COVID-19 where the need for crowd population management of a particular place is necessary to maintain social distancing or to prevent conditions such as overcrowding in public spaces or events that can lead to devastating and deadly stampedes.

![Crowd](/images/1.png?raw=true "Crowd")

The applications of the project can be for Crowd Management Systems, Visitor Counters, or Physical User Access Control (UAC) Systems which can be applied in concert halls, stadiums, arenas, terminals, train stations (e.g., ticket gates), and other places where crowds converge whilst still requiring a controlled manner of access.

## Project Capability and Scope

### Capabilities of the Project
- The project shall be capable of counting the entry and exit of people in a certain premises.
- The project shall be capable of handling multiple entry and exit points at the same time while ensuring reliable counting and high throughput.
- The project shall be capable of accurately and reliably keeping track of how many persons entered the set premises, and possibly, even who had entered the premises (i.e., ideal for security applications).
### Scope of the Project
- The scope for the server application side is limited to, at most, handling 200 entry/exit points at the same time, which is similar to the number of entry/exit points at Tokyo's Shinjuku Station.
- The scope for communication protocols used between the embedded devices and the server is limited to IP-based communication.
- The scope for the transaction recording mechanism will be software-defined to reduce the hardware quantity requirement.

## System Overview and Architecture

### Overall Logical Architecture

![Architecture](/images/2.png?raw=true "Architecture")

The project’s overall logical architecture is similar to the project’s intention of acting as entry/exit monitors on a given premise. The overall architecture can be divided into the embedded system and the server. The overall architecture also follows a software-defined to limit the need for excessive hardware while still being able to achieve the required objectives.

The embedded system will primarily consist of a microcontroller and an RFID reader where each of these is placed on different entry/exit points of a certain premises, to which such embedded systems are connected to the server through WiFi which then uses IP-based communication to transmit/receive data to and from the server.

The server will handle the recording and display of all registered entries and exits on the premises. As mentioned in the scope of this project, the server application is expected to handle multiple simultaneous connections and transaction attempts reliably. However, to keep in line with the objectives of the project, the server also limits the number of people that can enter the premises by returning a “LIMIT” response whenever the attempted entry will result in exceeding entry limits.

### Server Software Architecture

The server software architecture will be primarily written in Python and will include the use of libraries that will enable network communications, concurrency, and file handling. Specifically, socket, threading, os, time, and re. The socket module provides access to the properties that will allow communication across a network. The threading library will create the threads needed to accurately count the number of people entering and exiting places. The rest of the libraries—os, time, and re—are used for other functions of the server which are more related to data management. 

The server software architecture is a multi-threaded client-server architecture that consists of five layers. Every time a client connects to the server (Client Connection), be it an embedded client or an admin, the system creates a dedicated thread for the client via the Connection Manager. This thread delegates the execution of the necessary instructions associated with the request being made on behalf of the client which is handled by the Client Handler of the server. The Client Handler then executes the appropriate modules to obtain a server response to deliver back to the client. It also holds most of the critical sections of the server application, hence some locks are acquired and released before and after those sections of the server application.

![Server Architecture](/images/3.png?raw=true "Server Architecture")

The descriptions of the different command modules of the server application are as listed below. These commands/modules are also reflected in the JSON string that will be passed between the server and the client.

| Module   | Description                                                                                       |
|----------|---------------------------------------------------------------------------------------------------|
| `ADD`      | Adding a user to the DB Memory, and subsequently the DB text file.                              |
| `REMOVE`   | Removing a user to the DB Memory, and subsequently the DB text file.                            |
| `MONITOR`  | Returns a query of statistics regarding the current crowd capacity and the number of known IDs. |
| `SETLIMIT` | Sets the value of the crowd control capacity limiter.                                           |
| `SEARCH`   | Searches for a given ID and returns if it is in the DB Memory or not.                           |
| `TAP`      | Returns a tap query whether a given ID has entered, exited, or is invalid.                      |

The server relies on a multi-threaded design such that every client attempting to connect will be considered a thread by the server to which the method attached to the thread will attempt to complete the transaction based on the received command. The code below shows the server creating new `transaction` threads for every connection the server accepts.

```
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
```

The transactions are handled by the handle_client() method which contains concurrency and handling of critical resources of the server. The code is as shown below:

```
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
```

The list of all important methods found in Server.py is listed below.

| Method            | Description                                                                                                                                                                                                                                                |
|-------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `start()`         | Delegates the runtime of the server by listening to connection attempts to which it launches a respective thread for that accepted connection.                                                                                                             |
| `handle_client()` | Handles the thread call which completes the transaction calls by the client depending on the input received.                                                                                                                                               |
| `load_memory() `  | Loads the given ‘DB’ text file to the memory as a list.                                                                                                                                                                                                    |
| `setup_server()`  | Setups the server connection such as IP address and port no.                                                                                                                                                                                               |
| `update_db() `    | Executes updates to the ‘DB’ file based on the ID list found in memory. Execution will be made on a separate function (probably via start()) and may be event driven (i.e., when there are new IDs in the memory) or time-driven (i.e., per elapsed time). |

It is expected that the server will eventually experience errors especially if there are too many consecutive transactions for the server to handle. Hence, for any error that may occur, the server will simply respond “ERROR” back to the client to indicate that the transaction was not able to conclude appropriately.
The JSON string format and its keys’ description are as shown below: 

`{"dev_id":"deviceID", "cmd":"command", "val":"value"}`

| Key    | Value Description                                                                                                                                                                                                                                                     |
|--------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| dev_id | Contains the device name of the client device that sent the JSON string. Useful for identifying which embedded device sent the data. For the server and admin clients, the dev_id is set as “SERVER” and “ADMIN” respectively.                                        |
| cmd    | Contains the command is sent by the client to the server (i.e., ADD, REM MON, LIM, SER, TAP). Only two commands are sent by the embedded device which are SER and TAP. The admin client can send all commands except for TAP. Errors are designated with an ERR value |
| val    | Contains the value associated with the command. The command MON for the embedded system will only contain an empty string value.                                                                                                                                      |

The server uses the following Python libraries which are shown in the table below.

| Library    | Description                                                    |
|------------|----------------------------------------------------------------|
| UI         | A custom library that handles UI displays and mechanisms.      |
| JSONParser | A custom library that handles JSON encoding and decoding.      |
| socket     | A Python library used to handle websockets programming         |
| re         | A Python library used to handle regex functions                |
| time       | A Python library used to handle sleep calls.                   |
| datetime   | A Python library used to handle date & time data               |
| threading  | A Python library used to handle threads and thread management. |

### Client Hardware and Software Architecture

The primary client hardware architecture will be composed of an RFID reader connected to a microcontroller, with the RC522 and ESP32 being the specific hardware of choice. In the system, this hardware pair will be responsible for capturing data from RFID cards which will then be transmitted to the server for processing. A Python equivalent was also made to simulate multiple transactions occurring at the same time. The client will simply send the ID number detected by the RFID to the server to which it will receive either one of four responses:

| Response | Description                                                                 |
|----------|-----------------------------------------------------------------------------|
| ENTER    | ID No. received is valid and is allowed to enter the premises. (LED: GREEN) |
| EXIT     | ID No. received is valid and will exit the premises. (LED: YELLOW)          |
| LIMIT    | ID No. received is valid but the premises are already full. (LED: RED)      |
| INVALID  | ID No. received is invalid. (LED: RED)                                      |

A client simulator was created to enable testing and evaluation of the server application’s reliability and performance. The client simulator was designed to be able to execute multiple threads that will simulate multiple people tapping their RFID on the system simultaneously. The libraries used by the Python client are found in the table below.

| Library    | Description                                                    |
|------------|----------------------------------------------------------------|
| UI         | A custom library that handles UI displays and mechanisms.      |
| JSONParser | A custom library that handles JSON encoding and decoding.      |
| socket     | A Python library used to handle websockets programming         |
| re         | A Python library used to handle regex functions                |
| time       | A Python library used to handle sleep calls.                   |
| datetime   | A Python library used to handle date & time data               |
| threading  | A Python library used to handle threads and thread management. |

Additionally, an admin console was also created which can manage the server’s operational parameters. The admin can access the server to either add, remove, or search for users. The admin console can also monitor and set the limit of how many people can be inside a certain premise. Do note that the admin console also uses similar libraries as found in the normal client. 

The admin commands and expected server responses are as follows:

| Command | Expected Server Response                                                       | Description                                                                 |
|---------|--------------------------------------------------------------------------------|-----------------------------------------------------------------------------|
| ADD     | ADDED/!ADDED                                                                   | Adds an ID to the DB Memory                                                 |
| REM     | REMOVED/!REMOVED                                                               | Removes an ID to the DB Memory                                              |
| MON     | P:{People in Premises}/L:{Limit}/DB:{DB Memory} Formatted as “P:{}/L:{}/DB:{}” | Queries number of people in premise, entry limit, and size of DB in memory. |
| LIM     | LIMIT SET = {LIMIT}                                                            | Sets new entry limits                                                       |
| SER     | FOUND/NOT FOUND                                                                | Searches for ID                                                             |

The client has also an embedded system equivalent which is handled by the ESP32 microcontroller. The specifications of the client hardware (embedded system) are as follows:
- ESP32 (Microcontroller)
    - A low-cost and low-power microcontroller with Wi-Fi and Bluetooth connection capabilities.
    - It is powered by an either single or dual-core Tensilica Xtensa 32-bit LX6 microprocessor and is designed for Internet of Things applications.
    - The ESP32 features an 802.11b/g/n HT-40 Wi-Fi transceiver for wireless communications which will be relied upon for communicating with the server.
    - Pin multiplexing is an option for the ESP32. This allows multiple peripherals to share a single GPIO pin. In total, there are 30 available pins on the ESP32-C3-32S variant. A diagram of the available pins, along with their functions may be found below.
- RC522 (RFID)
    - Based on MFRC522, it is a low-cost and easy-to-interface RFID reader.
    - Usually paired with a rewritable RFID card with 1 KB of storage
    - Uses 13.56MHz frequency to communicate with RFID tags and follows the ISO 14443A Standard.
    - Uses either SPI, I2C, or UART serial communication protocols which makes it readily compatible with ESP32.
    - Features eight pins for GPIO communication. Notably, it has an interrupt pin available which can be useful for setting triggers once the RFID reader detects an RFID card/tag.
    
The table below shows the libraries used by the ESP32 client.

| Library/API   | Description                                                                                    |
|---------------|------------------------------------------------------------------------------------------------|
| MFRC522.h     | It is a library used for reading and writing to an RFID card/tag                               |
| SPI.h         | It is a library used for allowing communication with serial devices and setting up serial pins |
| FreeRTOS      | It is an API used for thread creation, control, and management                                 |
| ArduinoJson.h | It is a library used for building and parsing JSON formatted data                              |
| WiFi.h        | It is a library used for WiFi connection and client management                                 |

![Block Diagram](/images/4.png?raw=true "Block Diagram")