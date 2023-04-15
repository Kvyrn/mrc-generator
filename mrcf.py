import sys

"""
Usage: 
python3 mrcf.py <input file> <description>

Example input file:
ftp 235
z1 30
z2 65
z3 83
z4 98
z5 113
z6 135
z7 200
-----------
5:00 z1
5x {
    0:30 z2
    1:00 z3
    2x {
        0:15 z5
        0:15 150%
    }
    3x {
        0:20 100w
        1:00 59
    }
}
"""

header = """[COURSE HEADER]
VERSION = 2
UNITS = ENGLISH
DESCRIPTION = {description}
FILE NAME = {file_name}
MINUTES PERCENT
[END COURSE HEADER]
[COURSE DATA]"""
footer = "[END COURSE DATA]"

if len(sys.argv) not in [2, 3]:
    print("Invalid arguments", file=sys.stderr)
    exit(1)

file_name = sys.argv[1]
description = sys.argv[2]

with open(file_name, 'r') as f:
    lines = f.readlines()
output_file_path = file_name.rsplit(".", 1)[0] + ".mrc"
output_file_name = output_file_path.rsplit("/", 1)[1] if "/" in output_file_path else output_file_path

lines = [l.strip().lower() for l in lines]
lines = list(filter(lambda l: len(l)>0, lines))

# Find index of seperator
sep = None
for i in range(len(lines)):
    if lines[i].startswith('-'):
        sep = i
if sep is None:
    print("Missing seperator", file=sys.stderr)
    exit(1)

parameters = lines[:sep]
ftp = None
zones = [None]*7
for line in parameters:
    if line.startswith("ftp"):
        [_, ftp] = line.split(" ")
        ftp = int(ftp)
    elif line.startswith("z"):
        index = int(line[1])
        zones[index-1] = int(line.split(" ")[1])

if ftp is None or len([l for l in zones if l is None]) != 0:
    print("Missing zone definitions", file=sys.stderr)
    exit(1)

lines = lines[sep + 1:]

offset = 0

def parse():
    global offset
    data = []
    while offset < len(lines):
        line = lines[offset]
        offset += 1
        if 'x' in line:
            repeat = int(line.partition("x")[0])
            out = parse() * repeat
            data.extend(out)
        elif '}' in line:
            return data
        else:
            data.append(line)
    return data

def parse_power(p):
    if p.startswith("z"):
        index = int(p[1])
        return zones[index-1]
    elif p.endswith("%"):
        return int(p[:-1])
    elif p.endswith("w"):
        return int(int(p[:-1])*100/ftp)
    else:
        return int(p)


steps = parse()
# print("\n".join(steps))

with open(output_file_path, "w+") as file:
    print(header.format(file_name=output_file_name, description=description), file=file)
    offset = 0
    for line in steps:
        [length, power] = line.split(' ')
        power = parse_power(power)
        [minutes, seconds] = length.split(':')
        length = int(minutes) + int(seconds)/60

        print(f"{offset:.2f} {power}",file=file)
        offset += length
        print(f"{offset:.2f} {power}",file=file)
    print(footer, file=file)
