import random
import UI as ui

ids = []
rfid_tag_size = int(input("Enter number of RFID tag nos. to generate: "))
filename = input("Enter output filename: ")
print("Generating IDs...")
writable = ""
with open(filename, 'w') as f:
    for i in range(rfid_tag_size):
        valid = False
        while not valid:
            id = random.getrandbits(128)
            if id not in ids:
                ids.append(id)
                writable += "%032x\n" % id #results to 32 char hash
                valid = True
    print("Writing to file...")
    f.write(writable)
    print("Flushing to file...")
    f.flush()
    f.close()
print(f"{rfid_tag_size} ID Nos. Generated!")