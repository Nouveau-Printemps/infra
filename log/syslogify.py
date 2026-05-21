#!/usr/bin/env python3
import syslog
import argparse
import re

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

levels = {
    "debug": syslog.LOG_DEBUG,
    "info": syslog.LOG_INFO,
    "notice": syslog.LOG_NOTICE,
    "warning": syslog.LOG_WARNING,
    "err": syslog.LOG_ERR,
    "crit": syslog.LOG_CRIT,
    "alert": syslog.LOG_ALERT,
    "emerg": syslog.LOG_EMERG,
}

parser = argparse.ArgumentParser(
    "syslogify",
    description="Transforms raw log output into valid syslog entries.",
    epilog="See syslogify(1) for more information")
parser.add_argument("-i", "--ident", help="set the ident of the syslog entry.")
parser.add_argument("-f", "--facility",
                    choices=facilities.keys(),
                    help="set the facility of the syslog entry.",
                    default="user")
parser.add_argument("-l", "--level",
                    help="set the string representation of a syslog level.",
                    action="append")
parser.add_argument("regex", help="regex to use for parsing the input.")
parser.add_argument(
    "log", nargs="+", help="log to convert.")
args = parser.parse_args()

regex: re.Pattern = re.compile(args.regex)
log = " ".join(args.log)

for v in args.level if args.level != None else []:
    [k, val] = v.split(":", maxsplit=1)
    levels[k.lower()] = levels[val.lower()]

if args.ident != None:
    syslog.openlog(ident=args.ident, facility=facilities[args.facility])
else:
    syslog.openlog(facility=facilities[args.facility])

res: re.Match[str] | None = regex.search(log)
if res == None:
    syslog.syslog(syslog.LOG_WARNING, "cannot parse: " + log)
    exit(1)

if len(res.groups()) != 2:
    syslog.syslog(syslog.LOG_WARNING, "invalid regex: " +
                  args.regex + ", it must have exactly two groups")
    exit(1)

raw_level = res.group(1)
content = res.group(2)

level = levels.get(raw_level.lower())
if level == None:
    syslog.syslog(syslog.LOG_WARNING, "invalid log level: " + raw_level)
    exit(1)

syslog.syslog(level, content)
