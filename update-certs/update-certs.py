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

syslog.openlog("update-certs")

cfg_path = args[0]
cfg = {}

# key = domain group
# value = dict[domain, is wildcard]
domains: dict[str, dict[str, bool]] = {}

with open(cfg_path, "rb") as f:
    cfg = tomllib.load(f)
    os.chdir(cfg.get("certs", "/var/certs"))
    for domain in cfg.get("domains", []):
        domain = domain.strip("\n")
        if len(domain) == 0:
            continue
        group = ".".join(domain.split(".")[-2:])
        try:
            os.mkdir(group)
        except FileExistsError:
            0
        wildcard = domain.startswith("*")
        if domains.get(group) == None:
            domains[group] = {domain: wildcard}
        else:
            domains[group][domain] = wildcard

environ = os.environ.copy()
environ["INFOMANIAK_ACCESS_TOKEN_FILE"] = cfg.get("infomaniak_token_file", "")

def gen_base(group, data, star):
    domains = [f"--domains=\"{domain}\"" for (domain, wildcard) in data if star == wildcard]
    if len(domains) == 0:
        return None
    cmd = ["lego", f"--email=\"{cfg.get("email")}\"", f"--path={group}"]
    for v in domains:
        cmd.append(v)
    return cmd

def run(group, data, cmd):
    http = gen_base(group, data, False)
    if http != None:
        http.append("--http")
        http.append("--http.port")
        http.append(cfg.get("http_port", 80))
        http.append(cmd)
        print(http)
        res = subprocess.run(http)
        if res.returncode != 0:
            syslog.syslog(syslog.LOG_ERR, "cannot generate certificates for " + group + ": " + str(res.stderr))
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

for (group, d) in domains.items():
    root_path = path.join(group, "certificates")
    # domain, wildcard
    to_create: set[tuple[str, bool]] = set()
    to_renew: set[tuple[str, bool]] = set()
    for (domain, wildcard) in d.items():
        data = (domain, wildcard)
        domain += ".key"
        if path.exists(path.join(root_path, domain if not wildcard else "_"+domain[1:])):
            to_renew.add(data)
        else:
            to_create.add(data)
    run(group, to_create, "run")
    run(group, to_renew, "renew")
    os.chmod(root_path, 0o700)
    syslog.syslog("certificates generated for " + group)
