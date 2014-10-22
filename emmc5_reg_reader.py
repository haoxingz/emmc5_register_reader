import os, csv

# Define all the commands to collect register data
cmd_cid = "adb shell cat /sys/class/block/mmcblk0/device/cid"
cmd_csd = "adb shell cat /sys/class/block/mmcblk0/device/csd"
cmd_ecsd1 = "adb shell mount -t debugfs none /sys/kernel/debug"
cmd_ecsd2 = "adb shell cat /sys/kernel/debug/mmc0/mmc0:0001/ext_csd"

# Define number of bytes in each register
cid_bits = 128
csd_bits = 126
ecsd_bytes = 512


# Define path to map files
path_cid_map = ".\\map\\cid.csv"
path_csd_map = ".\\map\\csd.csv"
path_ecsd_map = ".\\map\\ecsd.csv"

# Define path to result files
path_result = ".\\result\\"

# Get device specific information
vendor = raw_input("Please enter the eMMC vendor: ")
capacity = raw_input("Please enter the eMMC capacity: ")

# Wait for devices
print "Wait for device..."
os.popen('adb wait-for-device')
dsn = os.popen('adb devices').readlines()[1].split('\t')[0]
print "Device " + dsn + " detected"

# In the future this information is acquired through ADB
print "Reading CID..."
val_cid = os.popen(cmd_cid).readline()[:-2]
print "Reading CSD..."
val_csd = os.popen(cmd_csd).readline()[:-2]
print "Reading EXT-CSD..."
os.popen(cmd_ecsd1).readlines()
val_ecsd = os.popen(cmd_ecsd2).readline()[:-2]

# Load register map
f_cid_map = open(path_cid_map, 'r')
f_csd_map = open(path_csd_map, 'r')
f_ecsd_map = open(path_ecsd_map, 'r')

# Create result file
if not os.path.exists(path_result):
    os.popen("mkdir " + path_result)
f_result = open(path_result + vendor + "_" + capacity + ".csv", 'wb')
result_writer = csv.writer(f_result)


# Parse CID. Basic unit is bit, MSB first
print "Parsing CID value..."
pos_cur = 0
val_cid_bin = format(int(val_cid, 16), '0128b')
result_writer.writerow(('', '', 'CID'))
for line in f_cid_map:
    tokens = line[:-1].split(",")
    try:
        size_cur = int(tokens[2], 10)
        # Peel off the right number of bits
        value_cur = int(val_cid_bin[pos_cur : pos_cur + size_cur], 2)
        value_cur = format(value_cur, '#x')
        pos_cur = pos_cur + size_cur
    except ValueError:
        value_cur = ""    
    result_writer.writerow((tokens[0], tokens[1], tokens[2], tokens[3], value_cur))

# Parse CSD. Basic unit is bit, MSB first
print "Parsing CSD value..."
pos_cur = 0
val_csd_bin = format(int(val_csd, 16), '0128b')
result_writer.writerows(('', ''))
result_writer.writerow(('', '', 'CSD'))
for line in f_csd_map:
    tokens = line[:-1].split(",")
    try:
        size_cur = int(tokens[2], 10)
        # Peel off the right number of bytes
        value_cur = int(val_csd_bin[pos_cur : pos_cur + size_cur], 2)
        value_cur = format(value_cur, '#x')
        pos_cur = pos_cur + size_cur
    except ValueError:
        value_cur = ""
    result_writer.writerow((tokens[0], tokens[1], tokens[2], tokens[3], tokens[4], value_cur))


# Parse ext-CSD. Basic unit is byte. LSB first
print "Parsing ext-CSD value..."
pos_cur = ecsd_bytes*2
result_writer.writerows(('', ''))
result_writer.writerow(('', '', 'EXT-CSD'))
for line in f_ecsd_map:
    tokens = line[:-1].split(",")
    # One line started with "Modes Segment" does not have this field
    try:
        size_cur = int(tokens[2], 10)
        value_cur = ""
        for i in range(0, size_cur):
            pos_cur = pos_cur - 2
            value_cur = value_cur + val_ecsd[pos_cur: pos_cur + 2]
    except ValueError:
        value_cur = ""
    
    # Peel off the right number of bytes
    result_writer.writerow((tokens[0], tokens[1], tokens[2], tokens[3], tokens[4], value_cur))


# Close all the files at last
f_cid_map.close()
f_csd_map.close()
f_ecsd_map.close()
f_result.close()
print "Done!"