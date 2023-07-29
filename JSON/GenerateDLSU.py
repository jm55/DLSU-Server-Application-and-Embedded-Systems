import random
import UI as ui

dlsu_start = int(input("Enter starting DLSU ID no.: "))
dlsu_ending = int(input("Enter ending DLSU ID no.: "))
ctr = 0
filename = input("Enter output filename: ")
with open(filename, 'a') as f:
    for i in range(dlsu_start,dlsu_ending+1):
        f.write(f"{i}\n")
        f.flush()
        ui.header("GenerateDLSU.py")
        print(f"{(ctr/(dlsu_ending-dlsu_start))*100:4f}%")
        ctr += 1
    f.close()