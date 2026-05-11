#!/usr/bin/env python3
import os
import os.path as path
import syslog
import subprocess
import sys
import time
import tomllib

args = sys.argv[1:]

if len(args) > 1:
    print("Usage: update-certs [config-file]")
    exit(1)

cfg_path = "/etc/update-certs/config.toml" if len(args) == 0 else args[0]

cfg = {}

with open(cfg_path, "rb") as f:
    cfg = tomllib.load(f)

log = cfg.get("log", {})

facilities = {
    "daemon": syslog.LOG_DAEMON,
    "user": syslog.LOG_USER,
    "auth": syslog.LOG_AUTH,
    "news": syslog.LOG_NEWS,
    "authpriv": syslog.LOG_AUTHPRIV,
    "local0": syslog.LOG_LOCAL0,
    "local1": syslog.LOG_LOCAL1,
    "local2": syslog.LOG_LOCAL2,
    "local3": syslog.LOG_LOCAL3,
    "local4": syslog.LOG_LOCAL4,
    "local5": syslog.LOG_LOCAL5,
    "local6": syslog.LOG_LOCAL6,
    "local7": syslog.LOG_LOCAL7,
}

syslog.openlog(log.get("ident", "update-certs"),
               facility=facilities[log.get("facility", "local0")])

os.chdir(cfg.get("certs", "/var/certs"))

email = cfg.get("email")

permissions = cfg.get("permissions", {})
perm_owner = permissions.get("owner", 0)
perm_group = permissions.get("group", 0)
perm_folder = permissions.get("folder", 0o700)
perm_file = permissions.get("file", 0o600)

environ = os.environ.copy()
token_file = cfg.get("token_file")
if token_file != None and environ.get("INFOMANIAK_ACCESS_TOKEN_FILE") == None:
    environ["INFOMANIAK_ACCESS_TOKEN_FILE"] = token_file

server = environ.get("ACME_SERVER")


def is_wildcard(domain):
    return domain[0] == "*"


def gen_base(group, email, data):
    if len(data) == 0:
        return None
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
            raise ValueError(
                "cannot manage wildcard certificates without a token")
        base.append("--dns")
        base.append("infomaniak")
    base.append(cmd)
    syslog.syslog(syslog.LOG_INFO, " ".join(cmd))
    res = subprocess.run(base, env=environ)
    if res.returncode != 0:
        syslog.syslog(syslog.LOG_ERR, "cannot generate certificates for " +
                      group + ": " + str(res.stdout))
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
            syslog.syslog(syslog.LOG_NOTICE,
                          "certificates sucessfully handled for " + name)
        else:
            continue
        os.chown(name, perm_owner, perm_group)
        os.chmod(name, perm_folder)
        os.chown(root_path, perm_owner, perm_group)
        os.chmod(root_path, perm_folder)
        for e in ext:
            p = f"{file_path}.{e}"
            os.chown(p, perm_owner, perm_group)
            os.chmod(p, perm_file)
    except Exception as e:
        syslog.syslog(syslog.LOG_ERR, str(e))
