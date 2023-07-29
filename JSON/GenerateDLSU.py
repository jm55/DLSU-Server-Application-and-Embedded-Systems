import random
import UI as ui

dlsu_start = int(input("Enter starting DLSU ID no.: "))
dlsu_ending = int(input("Enter ending DLSU ID no.: "))
if dlsu_ending < dlsu_start:
    print("Correcting ending ID no...")
    dlsu_ending *= 10
    print(f"Set to {dlsu_ending}")
filename = input("Enter output filename: ")
writable = ""
with open(filename, 'a') as f:
    for i in range(dlsu_start,dlsu_ending+1):
        writable += f"{i}\n"
    print("Writing to file...")
    f.write(writable)
    print("Flushing to file...")
    f.flush()
    f.close()
print(f"IDs {dlsu_start} to {dlsu_ending} ({dlsu_ending-dlsu_start} IDs) Generated!")