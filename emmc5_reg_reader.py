#!/usr/bin/python

# Define device specific information here
vendor = "sandisk"
capacity = "32G"

# In the future this information is acquired through ADB
f_data = open("./raw_data/ext_csd_" + vendor)
test_hex = f_data.readline()[:-1]
f_data.close()

# Open register map file
f_ecsd_map = open("./map/ecsd.map", 'r')
f_result = open("./result/" + vendor + "_" + capacity, 'w')

pos_cur = 1024
for line in f_ecsd_map:
    if line[0] != '#':
        tokens = line.split(",")
        size_cur = int(tokens[2], 10)
        # Need to check if the size_cur is empty in the future
        # Peel off the right number of bytes
        value_cur = ""
        for i in range(0, size_cur):
            pos_cur = pos_cur - 2
            value_cur = value_cur + test_hex[pos_cur: pos_cur + 2]
        f_result.write(value_cur + "\n")

# Close register map file
f_ecsd_map.close()
f_result.close()

