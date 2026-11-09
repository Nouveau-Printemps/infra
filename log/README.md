# syslogify

Simple python scripts that transforms raw logs into syslog entries.

Read the help with `-h` or at `syslogify(8)`.

## Install

It requires `scdoc` to build the documentation.
If `just` is installed, run `just install`.
Otherwise, execute manually commands in `justfile`.

## Usage

syslogify takes two arguments:
- a regex to use containing exactly two groups
- the log to convert

The first group must contain the log level and the second is the content.

For example,
```bash
syslogify "(\w+) (.+)" INFO This is an example
```
will produce a syslog entry with `LOG_INFO` level containing `This is an example`.

You can set ident with `-i` and the facility with `-f`.
```bash
syslogify -i test -f news "(\w+) (.+)" INFO This is an example
```
will produce the same entry, but in the facility `LOG_NEWS` with `test` as ident.

You can set custom name for the level with `-l`:
- the option starts with its name, continue with `:` and finish with the syslog name
- it is case insensitive
```bash
syslogify -l warn:warning -l trace:debug "(\w+) (.+)" WARN This is a warning
```

See `syslogify(8)` for more information.

---

# ip-analyze

Simple script that returns the list of IPv4 contained in a file.
You can filter them with regular expressions.

## Usage

Returns the list of IP that appears at least 15 times in a line containing `invalid user`.
```shell
$ ip-analyze -f "invalid user" /var/log/auth.log 15
0.1.2.3
0.2.3.4
```

Returns the list of IP that appears at least 3 times in a line containing `invalid user` or matching `failed auth$`.
```shell
$ ip-analyze -f "invalid user" -f "failed auth$" /var/log/auth.log 3
0.1.2.3
0.2.3.4
0.1.7.5
```
