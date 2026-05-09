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

email = cfg.get("email")

environ = os.environ.copy()
token_file = cfg.get("infomaniak_token_file")
if token_file != None and environ.get("INFOMANIAK_ACCESS_TOKEN_FILE") == None:
    environ["INFOMANIAK_ACCESS_TOKEN_FILE"] = token_file

server = environ.get("ACME_SERVER")

def is_wildcard(domain):
    return domain[0] == "*"

def gen_base(group, email, data):
    if len(data) == 0: return None
    cmd = ["lego", "--email", email, "--path", group, "-a", "--pem"]
    if server != None: 
        cmd.append("--server") 
        cmd.append(server)
    wildcard = False
    for domain in data:
        wildcard = wildcard or is_wildcard(domain)
        cmd.append("-d")
        cmd.append(domain)
    return cmd, wildcard

def run(group, email, data, cmd):
    base, has_wildcard = gen_base(group, email, data)
    if base == None:
        return False
    base.append("--http")
    base.append("--http.port")
    base.append(":" + str(cfg.get("http_port", 80)))
    if has_wildcard:
        if environ.get("INFOMANIAK_ACCESS_TOKEN_FILE") == None and environ.get("INFOMANIAK_ACCESS_TOKEN") == None:
            syslog.syslog(syslog.LOG_ERR, "cannot manage wildcard certificates without a token")
            exit(3)
        base.append("--dns")
        base.append("infomaniak")
    base.append(cmd)
    print(base)
    res = subprocess.run(base, env = environ)
    if res.returncode != 0:
        syslog.syslog(syslog.LOG_ERR, "cannot generate certificates for " + group + ": " + str(res.stdout))
        return False
    return True

ext = ["crt", "issuer.crt", "json", "key", "pem"]

for group in cfg.get("group", []):
    name = group["name"]
    folder = group.get("folder", name)
    root_path = path.join(folder, "certificates")
    domains = group["domains"]
    file_path = path.join(root_path, domains[0])
    syslog.syslog(syslog.LOG_NOTICE, "handling certificates for " + name)
    try:
        if run(folder, group.get("email", email), domains, "renew" if path.exists(file_path + ".key") else "run"):
            syslog.syslog("certificates sucessfully handled for " + name)
        else: 
            continue
        os.chmod(name, 0o700)
        os.chmod(root_path, 0o700)
        for e in ext:
            os.chmod(f"{file_path}.{e}", 0o600)
    except Exception as e:
        syslog.syslog(syslog.LOG_ERR, str(e))
