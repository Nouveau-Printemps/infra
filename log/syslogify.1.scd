SYSLOGIFY(1)

# NAME

syslogify - transforms raw logs into syslog entries.

# SYNOPSIS

syslogify [*-h*]

syslogify [*-s*] [*-i* _ident_] [*-f* _facility_] [*-l* _level_] _regex_ _log_...

# OPTIONS

_regex_
	is the _regex_(3) used to parse the raw logs.
	It must have two groups.
	The first contains the log level.
	The second is the content logged.
	Everything else is ignored.

_log_ is the log to use.

*-s* strip escape codes from the input.

*-i* _ident_
	set the ident of the entry.

*-f* _facility_
	set the facility containing the entry (do not start with LOG_).
	This option is case insensitive.

*-l* _level_
	set a custom name for a log level.
	_level_ must follow this pattern:
		_name_:_syslog_
	where _name_ is the name used in the log and _syslog_ is the _syslog_(3) name (but do not start with LOG_).
	This option is case insensitive.

*-h* prints the help.

# EXAMPLES

```
syslogify "(\w+) (.+)" INFO This is an example
```

logs "This is an example" in the user's facility with log level INFO.

```
syslogify -i test -f news "(\w+) (.+)" INFO This is an example
```

logs "This is an example" in the news' facility with log level INFO with the ident "test".

```
syslogify -l warn:warning -l trace:debug "(\w+) (.+)" WARN This is a warning
```

logs "This is a warning" in the user's facility with log level WARNING.

```
python syslogify.py -s -l warn:warning ".* \[(\w+)] (.*)" $(printf "\\e[38;5;244m2026-04-24 14:10:29 \\e[0m[\\e[38;5;11mWARN\\e[0m] \\e[38;5;244minternal/mux.go:93 - \\e[0m\\e[38;5;11minvalid request\\e[0m\\e[38;5;244m uri=/.git/config status=429 duration=4.248µs \\e[0m")
```

logs "internal/mux.go:93 - invalid request uri=/.git/config status=429 duration=4.248µs" in the user's facility with log
level WARNING.

# SEE ALSO

_syslog_(3), _regex_(3)

# AUTHORS

Maintained by William Hergès <@anhgelus.world>.
