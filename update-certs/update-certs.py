#!/usr/bin/env python3
import os
import os.path as path
import syslog
import subprocess
import sys
import time
import tomllib

args = sys.argv[1:]

if len(args) != 1:
    print("Usage: update-certs <config-file>")
    exit(1)

syslog.openlog("update-certs", facility=syslog.LOG_LOCAL1)

cfg = {}

with open(args[0], "rb") as f:
    cfg = tomllib.load(f)

os.chdir(cfg.get("certs", "/var/certs"))

environ = os.environ.copy()
environ["INFOMANIAK_ACCESS_TOKEN_FILE"] = cfg.get("infomaniak_token_file", "")

server = environ.get("ACME_SERVER")

def is_wildcard(domain):
    return domain[0] == "*"

def gen_base(group, data, star):
    if len(data) == 0: return None
    cmd = ["lego", "--email", cfg.get("email"), "--path", group, "-a", "--pem"]
    if server != None: 
        cmd.append("--server") 
        cmd.append(server)
    for domain in data[::-1]:
        if star == is_wildcard(domain): 
            cmd.append("-d")
            cmd.append(domain)
    return cmd

def run(group, data, cmd):
    http = gen_base(group, data, False)
    if http != None:
        http.append("--http")
        http.append("--http.port")
        http.append(":" + str(cfg.get("http_port", 80)))
        http.append(cmd)
        print(http)
        res = subprocess.run(http)
        if res.returncode != 0:
            syslog.syslog(syslog.LOG_ERR, "cannot generate certificates for " + group + ": " + str(res.stderr))
            return False
    dns = gen_base(group, data, True)
    if dns != None:
        if environ["INFOMANIAK_ACCESS_TOKEN_FILE"] == "":
            syslog.syslog(syslog.LOG_ERR, "cannot manage wildcard certificates without a token file")
            exit(3)
        dns.append("--dns")
        dns.append("infomaniak")
        dns.append(cmd)
        res = subprocess.run(dns, env = environ)
        if res.returncode != 0:
            syslog.syslog(syslog.LOG_ERR, "cannot generate certificates for " + group + ": " + str(res.stderr))
            return False
    return True

for group in cfg.get("group", []):
    root_path = path.join(group["name"], "certificates")
    renew = path.exists(root_path)
    if run(group["name"], group["domains"], "renew" if path.exists(root_path) else "run"):
        syslog.syslog("certificates generated for " + group)
    else: 
        continue
    os.chmod(group["name"], 0o700)
    os.chmod(root_path, 0o700)
