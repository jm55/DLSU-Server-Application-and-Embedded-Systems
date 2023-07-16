import random

rfid_tag_size = int(input("Enter number of RFID tag nos. to generate: "))
filename = input("Enter output filename: ")
with open(filename, 'a') as f:
    for i in range(rfid_tag_size):
        f.write("%032x\n" % random.getrandbits(128))
        f.flush()
    f.close()