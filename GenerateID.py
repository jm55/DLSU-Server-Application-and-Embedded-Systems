import random

rfid_tag_size = 1000

with open('IDs.txt', 'a') as f:
    for i in range(rfid_tag_size):
        f.write("%032x" % random.getrandbits(128))
        f.flush()
    f.close()