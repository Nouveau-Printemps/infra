#!/usr/bin/env python3
from functools import reduce
import os
import sys
import re
import argparse

parser = argparse.ArgumentParser(
    "ip-analyze",
    description="")
parser.add_argument("-f", "--format", action="append",
                    help="regex to use to verify each line")

input_group = parser.add_argument_group("input")
input_group.add_argument("file", help="file to parse")
input_group.add_argument("times", help="number of times before reporting ip")

args = parser.parse_args()

if args.file == None or args.format == None:
    parser.print_help()
    exit(1)

file_path = args.file
times = int(args.times) if args.times != None else 5

formats = [re.compile(f) for f in args.format]

ipv4 = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")

with open(file_path, "r") as f:
    found: dict[str, int] = {}
    for line in f.readlines():
        if not reduce(lambda acc, form: acc or form.search(line) != None, formats, False):
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
