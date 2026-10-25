#!/usr/bin/env python3
from functools import reduce
import os
import sys
import re

if len(sys.argv) < 2 or len(sys.argv) > 3:
    print("Usage: ip-analyze <file> [times]")
    exit(1)

file_path = sys.argv[1]
times = int(sys.argv[2]) if len(sys.argv) == 3 else 5

ipv4 = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")

with open(file_path, "r") as f:
    found: dict[str, int] = {}
    for line in f.readlines():
        if not "invalid" in line and not "failed" in line:
            continue
        ips = ipv4.findall(line)
        if len(ips) < 1:
            continue
        ip = ips[0]
        found |= {ips[0]: (found[ip] if ip in found else 0) + 1}

    sus = sorted(filter(lambda v: v[1] > times,
                 found.items()), key=lambda v: v[1])
    for (ip, v) in sus:
        print(ip)
