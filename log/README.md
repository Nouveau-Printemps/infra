# syslogify

Simple python scripts that transforms raw logs into syslog entries.

Read the help with `-h` or at `syslogify(1)`.

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

See `syslogify(1)` for more information.
