import random

dlsu_start = int(input("Enter starting DLSU ID no.: "))
dlsu_ending = int(input("Enter ending DLSU ID no.: "))
filename = input("Enter output filename: ")
with open(filename, 'a') as f:
    for i in range(dlsu_start,dlsu_ending+1):
        f.write(f"{i}\n")
        f.flush()
    f.close()