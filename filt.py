import sys

for line in sys.stdin.readlines():
    line = line.strip()
    if len(line) > 2:
        print line
        
