"""Linux: from the filesystem to kernel internals. Runnable bash examples use only commands and files the in-browser shell simulator supports."""

from ._dsl import ex, flow, node, pkt, qa, step

CATEGORIES = [
    {"id": "basics", "title": "Basics", "color": "sky", "blurb": "The filesystem and everyday commands."},
    {"id": "security", "title": "Users & Permissions", "color": "rose", "blurb": "Who may read, write and execute."},
    {"id": "text", "title": "Shell & Text", "color": "mint", "blurb": "Pipes, text tools and scripts."},
    {"id": "system", "title": "System", "color": "lemon", "blurb": "Processes, services and networking."},
    {"id": "internals", "title": "Internals", "color": "lilac", "blurb": "Disks, inodes, syscalls and containers."},
]

_F = lambda id, label, x, y, tint="sky", sub="", hidden=False: node(id, label, x, y, tint, sub, "box", hidden)
_P = lambda id, label, x, y, tint="lemon", sub="", hidden=False: node(id, label, x, y, tint, sub, "pill", hidden)
_R = lambda id, label, x, y, tint="mint", sub="", hidden=False: node(id, label, x, y, tint, sub, "round", hidden)

TOPICS = [
    {
        "id": "filesystem", "title": "The Linux Filesystem", "category": "basics", "level": "basic", "code": "FS",
        "tagline": "One tree from /, and almost everything in it is a file.",
        "analogy": "A single library building. Every book, map and even the lights' switchboard has a shelf address starting from the front door (/). Extra buildings (USB drives, network shares) are attached as new wings (mount points), not separate buildings.",
        "what": "Linux has one directory tree rooted at /. Disks and partitions are mounted into it instead of getting drive letters. The Filesystem Hierarchy Standard says where things live: /etc for configuration, /home for users, /var for changing data like logs, /usr for installed software, /tmp for scratch space, /dev for devices, and /proc and /sys for kernel views. Paths are absolute (/etc/hosts) or relative to the current directory (logs/app.log). ~ is your home, . is here, .. is the parent. 'Everything is a file' means devices, pipes and even process information are read and written with the same open/read/write calls.",
        "use_cases": ["Finding a service's configuration in /etc.", "Reading logs in /var/log.", "Understanding where a package installed its binaries.", "Inspecting the kernel's view of a process in /proc/<pid>."],
        "key_points": [
            "/etc config, /var variable data, /home users, /usr programs, /tmp scratch.",
            "Absolute paths start with /; relative paths start from the working directory.",
            "Names are case sensitive and hidden files start with a dot.",
            "/proc and /sys are virtual: no disk behind them, the kernel generates the content.",
        ],
        "examples": [
            ex("Look around", "basic", "Where am I, what is here, and what is in the standard folders?", "bash", """
                pwd
                ls -la
                ls /
                cat /etc/os-release
                cd /var/log && pwd
                cd ~
            """),
            ex("Relative vs absolute", "basic", "Both commands read the same file.", "bash", """
                cat logs/app.log | head -3
                cat /home/learner/logs/app.log | head -3
                cd logs && cat ../notes.txt
                cd ..
            """),
            ex("Everything is a file", "intermediate", "Devices and kernel data are files too.", "bash", """
                echo "gone" > /dev/null
                file /dev/null notes.txt scripts
                tree
            """),
            ex("/proc on a real machine", "advanced", "Kernel-generated files describe each process (run on a real Linux box).", "bash", """
                cat /proc/cpuinfo | grep "model name" | head -1
                cat /proc/meminfo | head -3
                ls /proc/$$          # your shell's own process directory
                cat /proc/$$/status | grep -E "Name|State|VmRSS"
            """, runnable=False),
        ],
        "commands": ["pwd · cd · ls -la", "tree", "file <path>", "cat /etc/os-release", "ls /proc/$$"],
        "gotchas": ["rm -rf with a variable that turns out empty: rm -rf \"$DIR\"/ becomes rm -rf /.", "Spaces in file names need quotes.", "/tmp may be cleared on reboot."],
        "interview": [
            qa("basic", "What lives in /etc, /var and /usr?", "/etc holds host-specific configuration, /var holds data that changes at runtime (logs, spool, caches, databases), and /usr holds installed programs and libraries that are read-only in normal operation."),
            qa("basic", "Absolute vs relative path?", "An absolute path starts at / and means the same thing from anywhere. A relative path is resolved from the current working directory, using . and .. for here and parent."),
            qa("intermediate", "What does 'everything is a file' mean?", "Resources expose a file interface: devices in /dev, process info in /proc, pipes and sockets. The same open, read, write and close calls work on all of them, which makes tools composable."),
            qa("intermediate", "What are /proc and /sys?", "Virtual filesystems generated by the kernel. /proc exposes processes and kernel stats (/proc/<pid>/status, /proc/meminfo); /sys exposes devices and drivers and lets you tune some settings."),
        ],
        "related": ["files-commands", "disks-storage", "kernel-internals"],
        "flow": flow(
            [_F("root", "/", 50, 12, "lilac", "root of everything"), _F("etc", "/etc", 15, 45, "sky", "config"), _F("home", "/home", 38, 45, "mint", "users"),
             _F("var", "/var", 62, 45, "lemon", "logs, data"), _F("proc", "/proc", 85, 45, "rose", "kernel view"), _F("usb", "/mnt/usb", 50, 85, "peach", "mounted disk", True)],
            [("root", "etc"), ("root", "home"), ("root", "var"), ("root", "proc"), ("root", "usb")],
            [
                step("One tree", "Every path starts at <b>/</b>. There are no drive letters.", ["root"]),
                step("Standard places", "<b>/etc</b> configuration, <b>/home</b> user files, <b>/var</b> logs and changing data.", ["etc", "home", "var"], [pkt("root", "etc"), pkt("root", "home"), pkt("root", "var")]),
                step("Virtual files", "<b>/proc</b> has no disk: the kernel generates its files on every read.", ["proc"], [pkt("root", "proc", "read")]),
                step("Mounting", "<b>mount /dev/sdb1 /mnt/usb</b> attaches another filesystem as a branch of the same tree.", ["usb"], [pkt("root", "usb", "mount")], {"usb": {"hidden": False}}),
            ],
        ),
    },
    {
        "id": "files-commands", "title": "Working with Files", "category": "basics", "level": "basic", "code": "FC",
        "tagline": "Create, copy, move, find and delete safely.",
        "analogy": "A filing cabinet: folders (mkdir), photocopies (cp), relabelling or moving folders (mv), the shredder (rm, no recycle bin), and the index cards that tell you where things are (find).",
        "what": "The core file commands are small and composable. mkdir -p creates nested directories, touch creates empty files or updates timestamps, cp copies (-r for directories), mv moves or renames, rm deletes immediately (there is no trash), and find walks the tree with tests such as -name and -type. Globs like *.log are expanded by the shell before the command runs, so the command sees the list of matching names. head, tail, less and wc help you inspect files without opening an editor.",
        "use_cases": ["Setting up a project folder structure.", "Cleaning temporary files.", "Finding every config file named *.conf.", "Taking a quick backup copy before editing."],
        "key_points": [
            "mkdir -p creates parents and does not fail if the directory exists.",
            "rm is permanent: double-check globs with ls first.",
            "Globs are expanded by the shell, not by the command.",
            "find . -name '*.tmp' -delete: quote the pattern so the shell does not expand it.",
        ],
        "examples": [
            ex("Make a project", "basic", "Nested directories, files and a listing.", "bash", """
                mkdir -p ~/projects/demo/src
                touch ~/projects/demo/README.md
                echo "print('hi')" > ~/projects/demo/src/main.py
                tree ~/projects
            """),
            ex("Copy, move, rename", "basic", "Back up a file, then rename it.", "bash", """
                cp notes.txt notes.bak
                mv notes.bak notes.old
                ls -l notes*
            """),
            ex("Check a glob before deleting", "intermediate", "See exactly what the shell will pass to rm.", "bash", """
                ls tmp
                echo rm tmp/*.tmp
                rm tmp/*.tmp
                ls tmp
            """),
            ex("Find things", "intermediate", "Search by name and type.", "bash", """
                find . -name "*.log"
                find . -type d
                find / -name "*.conf"
            """),
            ex("Inspect files", "basic", "First lines, last lines, counts.", "bash", """
                head -n 3 logs/app.log
                tail -n 2 logs/app.log
                wc -l logs/app.log data/users.csv
                du -h logs
            """),
        ],
        "commands": ["mkdir -p a/b/c", "cp -r src dst · mv old new", "rm -r dir (no undo)", "find . -name '*.log' -type f", "head -n 20 · tail -f · wc -l"],
        "gotchas": ["rm -rf / or rm -rf * in the wrong directory: there is no recycle bin.", "mv onto an existing file silently overwrites it (use -i or -n).", "cp without -r refuses directories.", "A glob that matches nothing is passed literally (unless nullglob is set)."],
        "interview": [
            qa("basic", "How do you create a nested directory in one command?", "mkdir -p a/b/c creates every missing parent and succeeds if the path already exists."),
            qa("basic", "cp vs mv on the same filesystem?", "cp writes a new copy of the data. mv on the same filesystem just renames the directory entry (instant, same inode); across filesystems it copies and deletes."),
            qa("intermediate", "Who expands *.txt, the shell or ls?", "The shell. It replaces the glob with matching file names before running the command, so ls receives a list of arguments."),
            qa("intermediate", "How do you delete all .tmp files older than 7 days?", "find /path -name '*.tmp' -type f -mtime +7 -delete (run it without -delete first to preview)."),
        ],
        "related": ["filesystem", "permissions", "pipes-redirection"],
        "flow": flow(
            [_F("sh", "Shell", 15, 50, "lilac", "rm tmp/*.tmp"), _F("glob", "Glob expansion", 45, 25, "lemon", "*.tmp → a.tmp b.tmp"), _F("cmd", "rm", 45, 75, "rose", "argv: a.tmp b.tmp"),
             _F("a", "a.tmp", 80, 20, "sky"), _F("b", "b.tmp", 80, 50, "sky"), _F("k", "keep.txt", 80, 80, "mint")],
            [("sh", "glob"), ("glob", "cmd"), ("cmd", "a"), ("cmd", "b")],
            [
                step("You type a glob", "The shell sees <b>tmp/*.tmp</b> before rm ever runs.", ["sh"]),
                step("Shell expands", "It matches names in tmp/ and substitutes them: <b>tmp/a.tmp tmp/b.tmp</b>.", ["glob", "a", "b"], [pkt("sh", "glob", "*.tmp")]),
                step("rm receives a list", "rm never sees the star, just two file names.", ["cmd"], [pkt("glob", "cmd", "argv")]),
                step("Files removed", "Both .tmp files are unlinked; keep.txt did not match.", ["k"], [pkt("cmd", "a", "unlink"), pkt("cmd", "b", "unlink")], {"a": {"hidden": True}, "b": {"hidden": True}}),
            ],
        ),
    },
    {
        "id": "permissions", "title": "Users, Groups & Permissions", "category": "security", "level": "intermediate", "code": "PM",
        "tagline": "rwx for owner, group and others, plus sudo, umask and special bits.",
        "analogy": "An office building badge system. Each room (file) has an owner, a team (group), and a policy for visitors (others): may they look in (read), rearrange (write), or use the equipment (execute)? Security (root) can open every door.",
        "what": "Every file has an owner, a group and a mode. The mode is three sets of read/write/execute bits for owner, group and others, shown by ls -l as -rwxr-x--- and written in octal as 750 (r=4, w=2, x=1). On directories, r lists names, w creates and deletes entries, and x lets you enter or traverse. chmod changes the mode, chown changes the owner (root only), and umask removes bits from the defaults of new files (666) and directories (777). Special bits: setuid runs a program as its owner (passwd), setgid on a directory makes new files inherit its group, and the sticky bit on /tmp lets only owners delete their files. root (uid 0) bypasses most checks; sudo runs one command as root after checking /etc/sudoers.",
        "use_cases": ["Making a script executable.", "Protecting SSH keys (600) and ~/.ssh (700).", "Shared team directories with setgid.", "Running privileged commands with sudo instead of logging in as root."],
        "key_points": [
            "Octal: 7 rwx, 6 rw-, 5 r-x, 4 r--, 0 ---. 644 files, 755 dirs and scripts.",
            "Deleting a file needs write on the directory, not on the file.",
            "umask 022 gives new files 644 and directories 755.",
            "Prefer sudo for single commands; never chmod 777 to 'fix' a problem.",
        ],
        "examples": [
            ex("Read the mode", "basic", "Decode ls -l output.", "bash", """
                ls -l notes.txt scripts
                stat notes.txt
                id
            """),
            ex("Make a script executable", "basic", "Permission denied until the x bit is set.", "bash", """
                ./scripts/backup.sh
                chmod u+x scripts/backup.sh
                ls -l scripts/backup.sh
                ./scripts/backup.sh
            """),
            ex("Octal vs symbolic", "intermediate", "Two ways to say the same thing.", "bash", """
                touch report.txt
                chmod 640 report.txt
                ls -l report.txt
                chmod g-r,o+r report.txt
                ls -l report.txt
            """),
            ex("Protect SSH files", "intermediate", "SSH refuses keys that other users can read.", "bash", """
                ls -la ~/.ssh
                chmod 700 ~/.ssh
                chmod 600 ~/.ssh/id_demo
                ls -la ~/.ssh
            """),
            ex("umask and root", "advanced", "Defaults for new files, and what sudo changes.", "bash", """
                umask
                umask 077
                touch private.txt
                ls -l private.txt
                cat /etc/shadow
                sudo cat /etc/shadow
                ls -ld /tmp
            """),
        ],
        "commands": ["ls -l · stat · id", "chmod 755 f · chmod u+x,g-w f", "sudo chown user:group f", "umask 022", "chmod g+s shared/ · chmod +t /tmp"],
        "gotchas": ["chmod 777 lets anyone modify or replace the file: almost never the right fix.", "Without x on a directory you cannot cd into it or reach files inside even if you know their names.", "chmod -R 755 makes every file executable; use X (capital) or find -type.", "setuid scripts are ignored by Linux for security; it applies to binaries."],
        "interview": [
            qa("basic", "What does chmod 755 mean?", "Owner rwx (7), group r-x (5), others r-x (5). Typical for directories and executables."),
            qa("intermediate", "What do r, w and x mean on a directory?", "r lists entry names, w creates, renames and deletes entries (with x), and x lets you traverse into it and access entries by name."),
            qa("intermediate", "How does umask work?", "It masks bits off the default mode: files start at 666 and directories at 777. With umask 022, new files get 644 and directories 755."),
            qa("advanced", "Explain setuid, setgid and sticky bit.", "setuid on an executable runs it with the file owner's uid (passwd edits /etc/shadow). setgid on a directory makes new files inherit its group. The sticky bit on a shared directory such as /tmp lets only a file's owner (or root) delete or rename it."),
            qa("advanced", "Why can a user delete a file they do not own?", "Deletion modifies the directory, not the file. If the user has w and x on the directory (and no sticky bit), they can unlink any entry in it."),
        ],
        "related": ["files-commands", "shell-scripting", "processes"],
        "flow": flow(
            [_F("u", "learner", 12, 50, "sky", "uid 1000, groups: learner sudo"), _F("k", "Kernel check", 45, 50, "lilac", "who are you?"),
             _P("own", "owner?", 78, 18, "mint", "rw-"), _P("grp", "group?", 78, 50, "lemon", "r--"), _P("oth", "others", 78, 82, "rose", "---")],
            [("u", "k"), ("k", "own"), ("k", "grp"), ("k", "oth")],
            [
                step("open(\"report.txt\", write)", "A process running as learner asks to write. The file is <b>-rw-r----- root:learner</b>.", ["u"], [pkt("u", "k", "open")]),
                step("Owner?", "The kernel checks the owner first. learner is not root, so the owner bits do not apply.", ["own"], [pkt("k", "own", "uid?")], {"own": {"sub": "no match"}}),
                step("Group?", "learner is in group learner, so only the <b>group bits r--</b> are used. Others are never consulted.", ["grp"], [pkt("k", "grp", "gid?")], {"grp": {"sub": "match: r--"}}),
                step("Denied", "Write is not in r--, so open fails with EACCES: <b>Permission denied</b>. sudo would run the command as uid 0 and pass.", ["k"], set={"k": {"sub": "EACCES", "tint": "rose"}}),
            ],
        ),
    },
    {
        "id": "pipes-redirection", "title": "Pipes & Redirection", "category": "text", "level": "basic", "code": "PR",
        "tagline": "stdin, stdout, stderr, and wiring small tools together.",
        "analogy": "Plumbing. Each tool is a filter with an inlet (stdin) and two outlets, clean water (stdout) and waste (stderr). A pipe | connects one filter's clean outlet to the next filter's inlet; > points an outlet into a bucket (file).",
        "what": "Every process starts with three file descriptors: 0 stdin, 1 stdout and 2 stderr. The shell rewires them before starting a command: > file sends stdout to a file (truncating), >> appends, < file feeds stdin, 2> redirects errors, and 2>&1 sends stderr wherever stdout currently goes. A pipe a | b connects a's stdout to b's stdin; both run at the same time and data streams through a kernel buffer. Exit codes ($?) report success (0) or failure, and && and || chain commands on them. tee copies a stream to a file and onward.",
        "use_cases": ["Counting matches: grep ERROR app.log | wc -l.", "Saving output and errors of a cron job to a log.", "Discarding noise with 2>/dev/null.", "Building one-liners from small tools."],
        "key_points": [
            "Order matters: cmd > out 2>&1 captures both; cmd 2>&1 > out does not.",
            "> truncates the file before the command runs.",
            "Pipes only carry stdout; stderr still goes to the terminal.",
            "&& runs next on success, || on failure, ; always.",
        ],
        "examples": [
            ex("Redirect output", "basic", "Write, append and read back.", "bash", """
                echo "first" > out.txt
                echo "second" >> out.txt
                cat out.txt
                wc -l < out.txt
            """),
            ex("Separate errors", "basic", "stdout and stderr are different streams.", "bash", """
                ls notes.txt /nope
                ls notes.txt /nope 2> errors.txt
                cat errors.txt
                ls notes.txt /nope > all.txt 2>&1
                cat all.txt
            """),
            ex("Pipelines", "intermediate", "Small tools, one stream.", "bash", """
                grep ERROR logs/app.log | wc -l
                cat todo.txt | sort | uniq -c | sort -rn
                ps aux | grep nginx
            """),
            ex("Exit codes and chaining", "intermediate", "Branch on success and failure.", "bash", """
                grep -q timeout logs/app.log && echo "found a timeout"
                grep -q unicorn logs/app.log || echo "no unicorns"
                ls /nope; echo "exit code was $?"
            """),
            ex("tee", "intermediate", "Save a copy and keep going.", "bash", """
                grep ERROR logs/app.log | tee errors.log | wc -l
                cat errors.log
            """),
        ],
        "commands": ["cmd > file · >> file · < file", "cmd 2> err.txt · cmd > all.txt 2>&1", "a | b | c", "cmd1 && cmd2 || cmd3", "cmd | tee copy.txt"],
        "gotchas": ["sort file > file empties the file before sort reads it.", "2>&1 > file sends errors to the terminal, not the file.", "In a pipeline, $? is the exit code of the last command (use set -o pipefail).", "cat file | grep is fine but grep pattern file avoids an extra process."],
        "interview": [
            qa("basic", "What are stdin, stdout and stderr?", "File descriptors 0, 1 and 2 that every process inherits. Programs read input from 0, write normal output to 1 and diagnostics to 2."),
            qa("intermediate", "Why does cmd 2>&1 > file still print errors?", "Redirections apply left to right. 2>&1 duplicates stderr onto the current stdout (the terminal), then > file moves only stdout. Write cmd > file 2>&1 instead."),
            qa("intermediate", "How does a pipe work?", "The shell creates a kernel pipe buffer, connects the left process's stdout to its write end and the right process's stdin to its read end, and runs both concurrently. The writer blocks when the buffer is full."),
            qa("advanced", "What does set -o pipefail change?", "A pipeline's exit status becomes the last non-zero status of any stage, so a failing first command is not hidden by a succeeding last one."),
        ],
        "related": ["text-processing", "shell-scripting"],
        "flow": flow(
            [_F("grep", "grep ERROR app.log", 15, 40, "sky", "fd1 → pipe"), _P("pipe", "pipe buffer", 47, 40, "lemon", "64 KiB"), _F("wc", "wc -l", 80, 40, "mint", "fd0 ← pipe"),
             _F("tty", "terminal", 47, 85, "lilac", "stderr + final stdout")],
            [("grep", "pipe"), ("pipe", "wc"), ("grep", "tty"), ("wc", "tty")],
            [
                step("Shell wires fds", "The shell creates a pipe and starts both processes at once.", ["grep", "wc", "pipe"]),
                step("Stream through", "Matching lines flow from grep's stdout into the buffer and out to wc's stdin.", ["pipe"], [pkt("grep", "pipe", "line"), pkt("pipe", "wc", "line")]),
                step("Errors bypass the pipe", "If app.log were unreadable, grep's <b>stderr</b> would still go straight to the terminal.", ["tty"], [pkt("grep", "tty", "stderr", "rose")]),
                step("Result", "grep closes the pipe, wc sees end-of-file and prints <b>4</b>.", ["wc", "tty"], [pkt("wc", "tty", "4")], {"wc": {"sub": "4"}}),
            ],
        ),
    },
    {
        "id": "text-processing", "title": "grep, sed, awk & Friends", "category": "text", "level": "intermediate", "code": "TX",
        "tagline": "Search, slice, count and transform text streams.",
        "analogy": "A newsroom: grep is the researcher who pulls only relevant articles, cut and awk are editors who extract columns, sort and uniq tally the votes, and sed is the copy editor doing find-and-replace.",
        "what": "Most Linux data is line-oriented text, and a handful of tools cover most needs. grep filters lines by regular expression (-i ignore case, -v invert, -c count, -o only the match, -r recursive). cut extracts fields by delimiter, sort orders lines (-n numeric, -r reverse, -k field, -u unique), uniq collapses adjacent duplicates (-c counts, so sort first), tr translates characters, sed edits streams (s/old/new/g, /re/d), and awk is a small language for field-based reports: awk -F, '$3 == \"Pune\" {print $2}'. Combine them in pipelines for log analysis and quick reports.",
        "use_cases": ["Top IPs in an access log.", "Count errors by type.", "Rewrite a config value with sed.", "Sum a column of a CSV with awk."],
        "key_points": [
            "uniq only merges adjacent lines: sort | uniq -c.",
            "sort -n for numbers, otherwise 10 sorts before 9.",
            "awk fields are $1, $2...; $0 is the whole line; NR the line number.",
            "sed -i edits in place: test without -i first.",
        ],
        "examples": [
            ex("grep essentials", "basic", "Filter, count, invert.", "bash", """
                grep ERROR logs/app.log
                grep -c ERROR logs/app.log
                grep -i "warn" logs/app.log
                grep -v INFO logs/app.log | head -3
                grep -oE "ERROR|WARN" logs/app.log | sort | uniq -c
            """),
            ex("Top talkers", "intermediate", "Classic log analysis pipeline.", "bash", """
                cut -d' ' -f1 logs/access.log | sort | uniq -c | sort -rn | head -3
            """),
            ex("CSV with cut and awk", "intermediate", "Columns, filters and sums.", "bash", """
                head -3 data/users.csv
                tail -n +2 data/users.csv | cut -d, -f3 | sort | uniq -c
                awk -F, '$3 == "Pune" {print $2}' data/users.csv
                awk -F, 'NR > 1 {n++} END {print n}' data/users.csv
            """),
            ex("sed and tr", "intermediate", "Find and replace, delete lines, change case.", "bash", """
                sed 's/learn/master/g' todo.txt
                sed '/permissions/d' todo.txt
                echo "hello linux" | tr a-z A-Z
                echo "a,,b,,c" | tr -s ,
            """),
            ex("Status code report", "advanced", "Count HTTP status codes and total bytes.", "bash", """
                awk '{print $4}' logs/access.log | sort | uniq -c | sort -rn
                awk '{s += $5} END {print s}' logs/access.log
            """),
        ],
        "commands": ["grep -rin 'pattern' dir", "cut -d, -f2,3", "sort | uniq -c | sort -rn", "sed 's/a/b/g' · sed -n '5p'", "awk -F: '{print $1}' /etc/passwd"],
        "gotchas": ["Forgetting sort before uniq.", "Regex special characters (. * [ ]) need escaping or grep -F.", "Different sed flavours: macOS sed -i needs an argument ('' ).", "awk -F' ' treats runs of spaces as one separator; -F'\\t' for tabs."],
        "interview": [
            qa("basic", "How do you count lines matching a pattern?", "grep -c pattern file, or grep pattern file | wc -l."),
            qa("intermediate", "Find the 5 most frequent IPs in an access log.", "awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -5 (or cut -d' ' -f1)."),
            qa("intermediate", "Why sort before uniq?", "uniq compares each line with the previous one only, so duplicates must be adjacent."),
            qa("advanced", "When would you use awk over cut?", "When you need conditions, arithmetic, reformatting or aggregation (sums, counts per key), or when fields are separated by variable whitespace."),
        ],
        "related": ["pipes-redirection", "shell-scripting"],
        "flow": flow(
            [_F("log", "access.log", 10, 50, "slate", "10 lines"), _F("cut", "cut -f1", 30, 50, "sky", "IPs"), _F("sort", "sort", 50, 50, "lemon", "grouped"),
             _F("uniq", "uniq -c", 70, 50, "mint", "counts"), _F("top", "sort -rn | head", 90, 50, "rose", "winner")],
            [("log", "cut"), ("cut", "sort"), ("sort", "uniq"), ("uniq", "top")],
            [
                step("Extract", "<b>cut -d' ' -f1</b> keeps only the first column: the client IP.", ["cut"], [pkt("log", "cut", "line")]),
                step("Group", "<b>sort</b> puts identical IPs next to each other.", ["sort"], [pkt("cut", "sort", "IP")]),
                step("Count", "<b>uniq -c</b> collapses adjacent duplicates and prefixes a count.", ["uniq"], [pkt("sort", "uniq", "IP")], {"uniq": {"sub": "5 203.0.113.7"}}),
                step("Rank", "<b>sort -rn | head -1</b> orders by count descending and keeps the top line.", ["top"], [pkt("uniq", "top", "5 ...")], {"top": {"sub": "203.0.113.7"}}),
            ],
        ),
    },
    {
        "id": "processes", "title": "Processes & Signals", "category": "system", "level": "intermediate", "code": "PS",
        "tagline": "PIDs, fork/exec, ps, top, kill and job control.",
        "analogy": "A restaurant kitchen. Every order is a process with a ticket number (PID). The head chef (init/systemd, PID 1) supervises; new orders are copies of an existing ticket (fork) rewritten for a new dish (exec). Signals are the shouts across the kitchen: 'please stop' (SIGTERM) or 'drop everything now' (SIGKILL).",
        "what": "A process is a running program with its own PID, memory, file descriptors, user and parent (PPID). New processes are created with fork() (copy the parent) and exec() (replace the program). PID 1 (systemd or init) adopts orphans. ps and top show processes, CPU and memory; /proc/<pid> exposes details. Signals are asynchronous notifications: SIGTERM (15) asks a process to exit cleanly, SIGKILL (9) cannot be caught and kills immediately, SIGHUP often means reload, SIGINT is Ctrl+C. Process states include running, sleeping, stopped and zombie (exited but not yet reaped by its parent). nice and renice adjust priority; & and jobs, fg and bg handle job control.",
        "use_cases": ["Finding and stopping a runaway process.", "Gracefully restarting a server with SIGTERM.", "Running a long job in the background.", "Diagnosing high CPU or memory."],
        "key_points": [
            "Try SIGTERM before SIGKILL so the program can clean up.",
            "You can only signal your own processes unless you are root.",
            "Zombies are already dead; fix or restart the parent that is not reaping them.",
            "Load average counts runnable (and uninterruptible) tasks, not CPU percent.",
        ],
        "examples": [
            ex("See what is running", "basic", "Snapshot and live view.", "bash", """
                ps
                ps aux
                top
            """),
            ex("Stop a runaway", "intermediate", "Find the CPU hog and terminate it.", "bash", """
                ps aux | grep runaway
                kill 1337
                ps aux
            """),
            ex("Permissions apply to signals", "intermediate", "nginx's master process belongs to root.", "bash", """
                ps aux | grep nginx
                kill 733
                sudo kill 733
                curl localhost
            """),
            ex("Signals and job control", "advanced", "Real-shell job control and traps.", "bash", """
                sleep 300 &            # background job
                jobs
                kill -TERM %1          # polite
                kill -9 <pid>          # last resort: cannot be caught
                trap 'echo cleaning up; exit' TERM INT   # handle signals in a script
                pgrep -a nginx; pkill -HUP nginx          # reload config
            """, runnable=False),
        ],
        "commands": ["ps aux · ps -ef --forest", "top · htop", "kill PID · kill -9 PID", "pgrep -a name · pkill name", "cmd & · jobs · fg · bg · nohup"],
        "gotchas": ["kill -9 skips cleanup: temp files, locks and buffers may be left behind.", "Killing a parent does not necessarily kill its children.", "Zombie processes cannot be killed; their parent must wait() for them.", "A process holding a deleted file keeps its disk space until it exits."],
        "interview": [
            qa("basic", "What is a PID and a PPID?", "The process ID uniquely identifies a running process; the parent process ID is the process that created it."),
            qa("intermediate", "SIGTERM vs SIGKILL?", "SIGTERM (15) can be caught so the program shuts down cleanly. SIGKILL (9) cannot be caught or ignored; the kernel removes the process immediately, without cleanup."),
            qa("intermediate", "Explain fork and exec.", "fork() duplicates the calling process (copy-on-write memory, same open files). exec() replaces the current program image with a new one. A shell runs a command by forking, then exec'ing the command in the child, and waiting."),
            qa("advanced", "What is a zombie process?", "A process that has exited but whose parent has not yet called wait() to read its exit status. It uses no CPU or memory, only a process table entry. Fix the parent or kill it so PID 1 adopts and reaps the zombie."),
            qa("advanced", "What does load average mean?", "The 1, 5 and 15 minute averages of tasks that are runnable or in uninterruptible sleep (often I/O). Compare it with the number of CPUs."),
        ],
        "related": ["systemd-services", "kernel-internals"],
        "flow": flow(
            [_R("bash", "bash", 15, 30, "sky", "PID 1201"), _R("child", "bash (fork)", 50, 30, "lemon", "PID 1400", True), _R("py", "python3", 50, 75, "rose", "PID 1400", True),
             _F("k", "kernel", 85, 50, "lilac", "signals")],
            [("bash", "child"), ("child", "py"), ("k", "py")],
            [
                step("fork()", "The shell duplicates itself. The child gets a new PID but the same code and open files.", ["bash", "child"], [pkt("bash", "child", "fork")], {"child": {"hidden": False}}),
                step("exec()", "The child replaces its program with python3. Same PID, new code.", ["py"], [pkt("child", "py", "exec")], {"child": {"hidden": True}, "py": {"hidden": False}}),
                step("SIGTERM", "<b>kill 1400</b> asks the kernel to deliver SIGTERM. The program may clean up and exit.", ["k", "py"], [pkt("k", "py", "TERM")]),
                step("Reaped", "The parent's wait() collects the exit status; the process entry disappears (no zombie).", ["bash"], [pkt("py", "bash", "exit 0")], {"py": {"hidden": True}}),
            ],
        ),
    },
    {
        "id": "systemd-services", "title": "systemd & Services", "category": "system", "level": "intermediate", "code": "SV",
        "tagline": "Units, start vs enable, journalctl and boot.",
        "analogy": "A building manager with a binder of instructions (unit files) for every system: how to start the elevators, what must be running first, and what to do if one breaks down (Restart=on-failure). The logbook at the front desk is the journal.",
        "what": "systemd is PID 1 on most distributions. It boots the system and supervises services described by unit files (.service, .socket, .timer, .mount) in /etc/systemd/system and /lib/systemd/system. systemctl start and stop change the current state; enable and disable control whether the unit starts at boot (by creating symlinks into a target's wants). systemctl status shows state, PID, cgroup and recent logs. journalctl -u name reads the structured journal for one unit, -f follows, -b limits to this boot. After editing a unit file, run systemctl daemon-reload. Timers replace many cron jobs.",
        "use_cases": ["Starting nginx and making it start on boot.", "Restarting a crashed app automatically.", "Reading why a service failed.", "Scheduling a nightly backup with a timer."],
        "key_points": [
            "start = now; enable = at boot. Often you want both (enable --now).",
            "Restart=on-failure plus RestartSec gives basic supervision.",
            "journalctl -u svc -n 50 --no-pager is the first debugging step.",
            "daemon-reload after editing unit files.",
        ],
        "examples": [
            ex("Inspect services", "basic", "What is running, and is it enabled?", "bash", """
                systemctl list-units
                systemctl status nginx
                systemctl is-enabled backup
                journalctl -u nginx
            """),
            ex("Stop, start and verify", "intermediate", "Changing state needs root.", "bash", """
                systemctl stop nginx
                sudo systemctl stop nginx
                curl localhost
                sudo systemctl start nginx
                sudo systemctl enable backup
                systemctl status nginx
                curl localhost
            """),
            ex("A unit file", "intermediate", "A supervised web app.", "ini", """
                # /etc/systemd/system/webapp.service
                [Unit]
                Description=Demo web app
                After=network-online.target
                Wants=network-online.target

                [Service]
                User=webapp
                WorkingDirectory=/opt/webapp
                ExecStart=/opt/webapp/bin/server --port 8080
                EnvironmentFile=/etc/webapp/env      # secrets stay out of the unit file
                Restart=on-failure
                RestartSec=3

                [Install]
                WantedBy=multi-user.target
            """, runnable=False),
            ex("A timer instead of cron", "advanced", "Run backup.service every night.", "ini", """
                # /etc/systemd/system/backup.timer
                [Unit]
                Description=Nightly backup

                [Timer]
                OnCalendar=*-*-* 02:00:00
                Persistent=true

                [Install]
                WantedBy=timers.target
                # then: sudo systemctl daemon-reload && sudo systemctl enable --now backup.timer
            """, runnable=False),
        ],
        "commands": ["systemctl status svc", "sudo systemctl start|stop|restart svc", "sudo systemctl enable --now svc", "journalctl -u svc -f", "sudo systemctl daemon-reload"],
        "gotchas": ["Started but not enabled: works until the next reboot.", "Editing a unit without daemon-reload has no effect.", "Putting secrets directly in ExecStart exposes them in ps output; use EnvironmentFile with tight permissions or a credential store.", "Type=simple vs forking mismatch makes systemd think the service died."],
        "interview": [
            qa("basic", "systemctl start vs enable?", "start launches the unit now. enable makes it start automatically at boot (by linking it into a target). enable --now does both."),
            qa("intermediate", "A service fails to start. How do you debug it?", "systemctl status svc for the state and last log lines, journalctl -u svc -b for full logs, check the unit with systemctl cat svc, try ExecStart by hand as the service user, then fix, daemon-reload and restart."),
            qa("intermediate", "How do you make a service restart if it crashes?", "Restart=on-failure (or always) and RestartSec in the [Service] section, plus StartLimitBurst/IntervalSec to avoid restart storms."),
            qa("advanced", "Why is systemd PID 1 important?", "PID 1 starts everything, adopts orphaned processes and reaps zombies. systemd also places each service in its own cgroup, so it can track, limit and stop all of its processes."),
        ],
        "related": ["processes", "kernel-internals"],
        "flow": flow(
            [_F("boot", "Kernel boot", 10, 50, "slate"), _R("sd", "systemd", 35, 50, "lilac", "PID 1"), _F("tgt", "multi-user.target", 62, 20, "lemon", "wants: nginx, ssh"),
             _F("ng", "nginx.service", 88, 20, "mint", "inactive"), _F("j", "journal", 62, 82, "sky", "logs")],
            [("boot", "sd"), ("sd", "tgt"), ("tgt", "ng"), ("ng", "j")],
            [
                step("PID 1", "The kernel starts <b>systemd</b> as the first process.", ["boot", "sd"], [pkt("boot", "sd", "exec")]),
                step("Targets", "systemd works toward multi-user.target, which <b>wants</b> every enabled unit.", ["tgt"], [pkt("sd", "tgt")]),
                step("Start in order", "Dependencies (After=, Requires=) decide the order; nginx starts in its own cgroup.", ["ng"], [pkt("tgt", "ng", "start")], {"ng": {"sub": "active (running)"}}),
                step("Logs", "stdout and stderr of the service land in the journal: <b>journalctl -u nginx</b>.", ["j"], [pkt("ng", "j", "log")]),
            ],
        ),
    },
    {
        "id": "shell-scripting", "title": "Shell Scripting", "category": "text", "level": "intermediate", "code": "SH",
        "tagline": "Variables, quoting, conditions, loops and safe scripts.",
        "analogy": "Writing a recipe for someone else's kitchen: list exactly what to do, handle 'if we are out of eggs', and stop immediately when something goes wrong instead of serving a half-cooked dish.",
        "what": "A shell script is a text file of commands, usually starting with a shebang (#!/usr/bin/env bash) and made executable with chmod +x. Variables are assigned without spaces (name=value) and expanded with \"$name\"; always double-quote expansions to avoid word splitting. $1, $2 and $@ are arguments, $? is the last exit code, ${var:-default} supplies defaults. Conditions use [[ ... ]] or test, loops use for and while, and functions group logic. Production scripts start with set -euo pipefail so failures stop the script, unset variables are errors and pipelines report failures. Secrets come from the environment or a secret manager, never from the script itself.",
        "use_cases": ["Automating backups and deploys.", "Glue between tools in CI pipelines.", "Container entrypoints.", "One-off data cleanup."],
        "key_points": [
            "Quote variables: \"$file\" not $file.",
            "set -euo pipefail at the top of real scripts.",
            "Use $(command) for command substitution, not backticks.",
            "Check scripts with shellcheck.",
        ],
        "examples": [
            ex("Run a script", "basic", "Executable bit and arguments.", "bash", """
                cat scripts/hello.sh
                ./scripts/hello.sh
                ./scripts/hello.sh Ada
                bash scripts/hello.sh Linus
            """),
            ex("Variables and quoting", "basic", "Expansion rules in one place.", "bash", """
                name="Ada Lovelace"
                echo "Hello $name"
                echo 'Hello $name'
                echo "Default: ${missing:-guest}"
                export STAGE=dev
                env | grep STAGE
            """),
            ex("Write and run your own", "intermediate", "Create a script without an editor.", "bash", """
                echo 'echo "files in logs:"' > count.sh
                echo 'ls logs | wc -l' >> count.sh
                chmod +x count.sh
                ./count.sh
            """),
            ex("A safe script", "advanced", "Strict mode, functions, loops, traps.", "bash", """
                #!/usr/bin/env bash
                set -euo pipefail

                LOG_DIR="${1:-/var/log/myapp}"
                : "${API_TOKEN:?set API_TOKEN in the environment}"   # never hardcode secrets

                cleanup() { rm -f "$tmp"; }
                tmp="$(mktemp)"
                trap cleanup EXIT

                compress_old() {
                  local dir="$1"
                  find "$dir" -name '*.log' -mtime +7 -print0 |
                    while IFS= read -r -d '' f; do
                      gzip -- "$f"
                      echo "compressed $f" >> "$tmp"
                    done
                }

                if [[ -d "$LOG_DIR" ]]; then
                  compress_old "$LOG_DIR"
                  echo "done: $(wc -l < "$tmp") files"
                else
                  echo "no such dir: $LOG_DIR" >&2
                  exit 1
                fi
            """, runnable=False),
        ],
        "commands": ["#!/usr/bin/env bash", "set -euo pipefail", "\"$var\" · ${var:-default} · $(cmd)", "[[ -f file ]] && echo yes", "for f in *.log; do ...; done"],
        "gotchas": ["Unquoted variables split on spaces and expand globs.", "cd somewhere || exit, otherwise later rm runs in the wrong place.", "Hardcoded tokens in scripts end up in Git history; read them from the environment.", "Windows line endings (\\r\\n) break the shebang: bad interpreter."],
        "interview": [
            qa("basic", "What does the shebang line do?", "#! tells the kernel which interpreter runs the file when it is executed directly, for example #!/usr/bin/env bash finds bash on the PATH."),
            qa("intermediate", "Why quote \"$var\"?", "Unquoted expansions undergo word splitting and globbing, so a file name with spaces becomes several arguments and * may expand. Quoting passes the value as one argument."),
            qa("intermediate", "What does set -euo pipefail do?", "-e exits on a failing command, -u treats unset variables as errors, and pipefail makes a pipeline fail if any stage fails. Together they stop scripts from continuing in a broken state."),
            qa("advanced", "How should a script handle secrets?", "Read them from environment variables, files with tight permissions, or a secret manager at runtime; never hardcode them, never echo them, and avoid passing them as command-line arguments (visible in ps)."),
        ],
        "related": ["pipes-redirection", "permissions", "text-processing"],
        "flow": flow(
            [_F("file", "backup.sh", 12, 50, "slate", "#!/usr/bin/env bash"), _F("k", "kernel execve", 40, 20, "lilac", "x bit? shebang?"), _R("bash", "bash", 70, 20, "sky", "reads lines"),
             _F("cmd1", "mkdir -p ~/backup", 70, 55, "mint"), _F("cmd2", "cp notes.txt", 70, 85, "mint"), _F("exit", "exit 0", 92, 55, "lemon")],
            [("file", "k"), ("k", "bash"), ("bash", "cmd1"), ("cmd1", "cmd2"), ("cmd2", "exit")],
            [
                step("./backup.sh", "The kernel checks the execute bit; without it you get Permission denied.", ["file", "k"], [pkt("file", "k", "execve")]),
                step("Shebang", "The first line names the interpreter, so the kernel actually runs <b>bash backup.sh</b>.", ["bash"], [pkt("k", "bash", "#!")]),
                step("Line by line", "bash executes each command; with <b>set -e</b> the first failure stops the script.", ["cmd1", "cmd2"], [pkt("bash", "cmd1"), pkt("cmd1", "cmd2")]),
                step("Exit code", "The script's exit status is the last command's status, checked by callers with $?.", ["exit"], [pkt("cmd2", "exit", "0")]),
            ],
        ),
    },
    {
        "id": "networking", "title": "Networking Tools", "category": "system", "level": "intermediate", "code": "NW",
        "tagline": "Interfaces, routes, ports, DNS and debugging connectivity.",
        "analogy": "Mailing a letter: your address (IP on an interface), the post office that knows where to forward letters for other towns (default route), the directory enquiry service (DNS), and the numbered apartment doors where each service listens (ports).",
        "what": "Each network interface has addresses (ip addr). The routing table (ip route) decides which interface and gateway reach a destination; the default route handles everything else. DNS turns names into addresses using /etc/hosts first and then the resolvers in /etc/resolv.conf (dig, getent hosts). Services listen on ports; ss -tlnp shows which process listens where. Debug connectivity layer by layer: is the interface up, can you ping the gateway, does DNS resolve, is the port open (curl, nc), is a firewall (nftables, iptables, security groups) dropping packets?",
        "use_cases": ["Checking which process is using port 80.", "Debugging 'cannot connect' errors.", "Pointing a hostname at a test server via /etc/hosts.", "Testing an HTTP endpoint from a server."],
        "key_points": [
            "ss replaces netstat; ip replaces ifconfig and route.",
            "Connection refused = reachable host, nothing listening. Timeout = filtered or unreachable.",
            "Listening on 127.0.0.1 is local only; 0.0.0.0 accepts from any interface.",
            "/etc/hosts wins over DNS by default (nsswitch.conf).",
        ],
        "examples": [
            ex("Addresses and routes", "basic", "Who am I on the network?", "bash", """
                hostname
                ip addr
                ip route
                cat /etc/hosts
            """),
            ex("Ports and listeners", "intermediate", "Which services are listening?", "bash", """
                ss -tlnp
                curl -I localhost
                sudo systemctl stop nginx
                ss -tlnp
                curl localhost
                sudo systemctl start nginx
            """),
            ex("Reachability and DNS", "intermediate", "Ping and resolve.", "bash", """
                ping -c 2 10.0.0.1
                ping -c 2 10.0.0.99
                dig db.internal
            """),
            ex("Real-world debugging", "advanced", "A checklist on a real host.", "bash", """
                ip -br addr                       # interfaces up with addresses?
                ip route get 10.0.2.15            # which route and source IP?
                getent hosts api.internal         # what the system resolver returns
                nc -vz api.internal 443           # TCP port open?
                curl -sv https://api.internal/health -o /dev/null
                sudo tcpdump -ni eth0 port 443 -c 20
                sudo nft list ruleset | less      # firewall
            """, runnable=False),
        ],
        "commands": ["ip addr · ip route", "ss -tlnp", "ping -c 3 host", "dig name · getent hosts name", "curl -v url · nc -vz host port"],
        "gotchas": ["Ping blocked does not mean the host is down (ICMP is often filtered).", "A service bound to 127.0.0.1 is unreachable from other machines.", "Stale /etc/hosts entries silently override DNS.", "curl -k disables TLS verification: use it only for debugging, never in scripts."],
        "interview": [
            qa("basic", "How do you find which process listens on port 8080?", "ss -tlnp | grep 8080 (or sudo lsof -i :8080)."),
            qa("intermediate", "Connection refused vs connection timed out?", "Refused: the host answered with a TCP reset because nothing listens on that port. Timed out: no answer at all, usually a firewall dropping packets or a routing problem."),
            qa("intermediate", "How does name resolution work on Linux?", "nsswitch.conf sets the order, usually files (/etc/hosts) then dns, which queries the resolvers in /etc/resolv.conf (often systemd-resolved)."),
            qa("advanced", "How would you debug 'my app cannot reach the database'?", "Go layer by layer: DNS (getent hosts db), route (ip route get), TCP (nc -vz db 5432), firewall/security group rules, then TLS and credentials, and check the DB listens on the right interface."),
        ],
        "related": ["systemd-services", "processes"],
        "flow": flow(
            [_F("app", "curl db.internal", 10, 50, "sky"), _F("hosts", "/etc/hosts", 35, 18, "lemon", "db.internal → 10.0.0.5"), _F("route", "routing table", 35, 82, "lilac", "default via 10.0.0.1"),
             _F("nic", "eth0", 62, 50, "slate", "10.0.2.15"), _F("db", "db server", 90, 50, "mint", ":5432 listening")],
            [("app", "hosts"), ("app", "route"), ("route", "nic"), ("nic", "db")],
            [
                step("Resolve", "The resolver checks <b>/etc/hosts</b> first, then DNS.", ["hosts"], [pkt("app", "hosts", "db.internal?")]),
                step("Route", "The kernel picks a route and source address for 10.0.0.5.", ["route", "nic"], [pkt("app", "route"), pkt("route", "nic")]),
                step("TCP handshake", "SYN goes out eth0; if something listens on the port, SYN-ACK comes back.", ["db"], [pkt("nic", "db", "SYN"), pkt("db", "nic", "SYN-ACK", "mint")]),
                step("Or not", "No listener: <b>RST</b> (connection refused). Firewall drop: silence until timeout.", ["db"], [pkt("db", "nic", "RST", "rose")], {"db": {"sub": "nothing on :5432"}}),
            ],
        ),
    },
    {
        "id": "disks-storage", "title": "Disks, Inodes & Links", "category": "internals", "level": "advanced", "code": "DK",
        "tagline": "Partitions, mounts, inodes, hard links and symlinks.",
        "analogy": "A warehouse. The inode is the inventory card for a box (size, owner, where it sits). Directory entries are labels pointing at cards; a hard link is a second label on the same card, a symlink is a sticky note saying 'see aisle 7'. A box is thrown away only when no labels point at its card.",
        "what": "Block devices (/dev/sda, /dev/nvme0n1) are split into partitions, formatted with a filesystem (ext4, xfs) and mounted into the tree (mount, /etc/fstab). Inside a filesystem, each file's metadata (mode, owner, size, timestamps, data block pointers) lives in an inode; directory entries map names to inode numbers. A hard link is another name for the same inode (same filesystem only), so data is freed when the link count reaches zero and no process holds it open. A symbolic link is a tiny file containing a path; it can cross filesystems and can dangle. df shows free space per filesystem, df -i free inodes, du sums usage by directory. LVM adds flexible volumes on top of disks.",
        "use_cases": ["Adding a data disk and mounting it at boot.", "Finding what fills the disk.", "Atomic deploys by switching a 'current' symlink.", "Explaining 'disk full' when df shows free space (inodes exhausted)."],
        "key_points": [
            "Names live in directories; metadata lives in the inode.",
            "Hard link: same inode, same filesystem. Symlink: a path, can dangle.",
            "Deleted-but-open files still use space (lsof +L1).",
            "Use UUIDs in /etc/fstab, not /dev/sdX names.",
        ],
        "examples": [
            ex("Inodes and hard links", "intermediate", "Two names, one file.", "bash", """
                echo "v1" > config.txt
                ln config.txt config.hard
                ls -li config.txt config.hard
                echo "v2" >> config.hard
                cat config.txt
                rm config.txt
                cat config.hard
            """),
            ex("Symlinks", "intermediate", "A pointer by path, which can break.", "bash", """
                mkdir -p releases/v1 releases/v2
                ln -s releases/v1 current
                ls -l current
                ln -sfn releases/v2 current
                ls -l current
                ln -s missing.txt broken
                cat broken
            """),
            ex("Space usage", "basic", "Filesystems and directories.", "bash", """
                df -h
                du -h logs
                stat logs/app.log
            """),
            ex("Add a disk on a real server", "advanced", "Partition, format, mount, persist.", "bash", """
                lsblk -f
                sudo parted /dev/sdb --script mklabel gpt mkpart data ext4 0% 100%
                sudo mkfs.ext4 -L data /dev/sdb1
                sudo mkdir -p /data
                sudo blkid /dev/sdb1                  # copy the UUID
                echo 'UUID=<uuid> /data ext4 defaults,noatime 0 2' | sudo tee -a /etc/fstab
                sudo mount -a && df -h /data
                df -i /data                           # inode usage
                sudo lsof +L1                         # deleted files still held open
            """, runnable=False),
        ],
        "commands": ["df -h · df -i · du -sh *", "lsblk -f · blkid", "mount · /etc/fstab", "ln target name · ln -s target name", "ls -li · stat file"],
        "gotchas": ["Disk full but df shows space: check df -i for inode exhaustion (millions of tiny files).", "Deleting a big log that a process still writes frees nothing; truncate it or restart the process.", "A typo in /etc/fstab can stop boot: test with mount -a.", "Relative symlinks resolve from the link's directory, not yours."],
        "interview": [
            qa("intermediate", "What is an inode?", "The on-disk structure holding a file's metadata (type, mode, owner, size, timestamps, link count) and pointers to its data blocks. The file name is not in the inode; it lives in a directory entry."),
            qa("intermediate", "Hard link vs symbolic link?", "A hard link is an additional directory entry for the same inode: same filesystem, works if the original name is deleted. A symlink is a separate file containing a path: crosses filesystems, can point at directories, breaks if the target moves."),
            qa("advanced", "df says the disk is full but du finds far less. Why?", "Usually a deleted file still held open by a process (lsof +L1), files hidden under a mount point, or reserved blocks. Restart or truncate the holder to free the space."),
            qa("advanced", "Why can you get 'No space left on device' with free blocks?", "The filesystem ran out of inodes (df -i), typically from huge numbers of small files such as caches or mail spools."),
        ],
        "related": ["filesystem", "kernel-internals"],
        "flow": flow(
            [_F("n1", "config.txt", 15, 25, "sky", "dir entry"), _F("n2", "config.hard", 15, 75, "sky", "dir entry", True), _F("ino", "inode 1051", 50, 50, "lilac", "links: 1"),
             _F("data", "data blocks", 85, 50, "mint", "v1"), _F("sym", "current → releases/v1", 50, 90, "lemon", "symlink (own inode)", True)],
            [("n1", "ino"), ("n2", "ino"), ("ino", "data")],
            [
                step("A name points at an inode", "The directory maps <b>config.txt</b> to inode 1051, which points at the data.", ["n1", "ino", "data"], [pkt("n1", "ino"), pkt("ino", "data")]),
                step("Hard link", "<b>ln config.txt config.hard</b> adds a second name for the same inode.", ["n2", "ino"], [pkt("n2", "ino")], {"n2": {"hidden": False}, "ino": {"sub": "links: 2"}}),
                step("Delete one name", "<b>rm config.txt</b> removes only that entry. Data stays while links > 0.", ["ino"], set={"n1": {"hidden": True}, "ino": {"sub": "links: 1"}}),
                step("Symlinks are different", "A symlink stores a path in its own inode; if the target moves, it dangles.", ["sym"], set={"sym": {"hidden": False}}),
            ],
        ),
    },
    {
        "id": "kernel-internals", "title": "Kernel, Syscalls & Containers", "category": "internals", "level": "advanced", "code": "KN",
        "tagline": "User vs kernel space, syscalls, /proc, cgroups and namespaces.",
        "analogy": "A hotel. Guests (processes) cannot walk into the kitchen or the vault; they call the front desk (system calls) and staff (the kernel) do it for them. Namespaces give each guest a private-looking floor; cgroups cap how much room service they may order.",
        "what": "The kernel runs in privileged mode and manages CPU scheduling, memory (virtual memory, page cache, swap), devices and filesystems. Programs run in user space and request services through system calls such as open, read, write, fork, execve, mmap and socket; strace shows them. Virtual memory gives each process its own address space; the OOM killer picks a victim when memory runs out. Containers are ordinary processes with two kernel features: namespaces isolate what a process can see (pid, net, mnt, uts, ipc, user), and cgroups (v2) limit and account for what it can use (cpu, memory, io, pids). Capabilities split root's power into pieces, and seccomp filters which syscalls are allowed.",
        "use_cases": ["Debugging a hung program with strace.", "Understanding Docker and Kubernetes resource limits.", "Explaining an OOMKilled container.", "Tuning kernel parameters with sysctl."],
        "key_points": [
            "Containers share the host kernel; VMs run their own.",
            "Namespaces = what you can see. cgroups = how much you can use.",
            "Memory limit exceeded in a cgroup triggers the OOM killer for that cgroup.",
            "Drop capabilities and use seccomp rather than running containers privileged.",
        ],
        "examples": [
            ex("Look at the kernel", "basic", "Version, uptime and memory from the simulator.", "bash", """
                uname -a
                uptime
                free -h
                df -h
            """),
            ex("Trace system calls", "advanced", "What a program asks the kernel to do (real Linux).", "bash", """
                strace -f -e trace=openat,read,write cat /etc/hostname
                strace -c ls /             # syscall counts and time
                cat /proc/$$/limits        # per-process limits
                sysctl vm.swappiness
            """, runnable=False),
            ex("Namespaces by hand", "advanced", "A container without Docker.", "bash", """
                sudo unshare --pid --fork --mount-proc --uts --net bash
                hostname sandbox && hostname   # only this namespace changes
                ps aux                         # PID 1 is your bash
                ip addr                        # only a loopback interface
                lsns                           # (from the host) list namespaces
            """, runnable=False),
            ex("cgroups v2 limits", "advanced", "Cap memory and CPU for a process group.", "bash", """
                sudo mkdir /sys/fs/cgroup/demo
                echo 200M | sudo tee /sys/fs/cgroup/demo/memory.max
                echo "50000 100000" | sudo tee /sys/fs/cgroup/demo/cpu.max   # 50% of one CPU
                echo $$ | sudo tee /sys/fs/cgroup/demo/cgroup.procs
                cat /sys/fs/cgroup/demo/memory.current
                # docker run --memory=200m --cpus=0.5 ... writes these same files
            """, runnable=False),
        ],
        "commands": ["uname -r · uptime · free -h", "strace -f -p PID", "cat /proc/PID/status", "lsns · unshare · nsenter", "systemd-cgls · /sys/fs/cgroup"],
        "gotchas": ["--privileged containers can reach host devices: almost root on the host.", "Free memory looks low because Linux uses spare RAM as page cache; check 'available'.", "Containers see the host's CPU count in /proc unless the runtime virtualizes it, which confuses some runtimes' thread pools.", "strace slows the traced program a lot; avoid it on hot production paths."],
        "interview": [
            qa("intermediate", "What is a system call?", "The controlled entry point from user space into the kernel (open, read, write, fork, execve, mmap...). The CPU switches to privileged mode, the kernel does the work and returns a result or an error code."),
            qa("intermediate", "Container vs virtual machine?", "A container is a group of processes on the host kernel isolated with namespaces and limited by cgroups, so it is light and fast. A VM runs its own kernel on virtualized hardware: stronger isolation, more overhead."),
            qa("advanced", "Namespaces vs cgroups?", "Namespaces control visibility: a process gets its own PID tree, network stack, mounts, hostname and users. cgroups control resources: CPU shares and quotas, memory limits, I/O and pid counts, with accounting."),
            qa("advanced", "A container was OOMKilled. What happened?", "Its cgroup reached memory.max, reclaim could not free enough, and the kernel's OOM killer terminated a process in that cgroup. Raise the limit or reduce memory use (heap settings, leaks, caches)."),
            qa("advanced", "Why does free show little free memory on a healthy server?", "Linux uses otherwise idle RAM for the page cache. That memory is reclaimable, so 'available' is the number to watch, not 'free'."),
        ],
        "related": ["processes", "disks-storage", "systemd-services"],
        "flow": flow(
            [_R("app", "nginx", 15, 30, "sky", "user space"), _F("sc", "syscall", 15, 75, "lemon", "write(fd, buf)"), _F("k", "Linux kernel", 50, 75, "lilac", "scheduler, VM, VFS"),
             _F("ns", "namespaces", 85, 25, "mint", "own pid / net / mnt", True), _F("cg", "cgroup", 85, 75, "rose", "memory.max 200M", True)],
            [("app", "sc"), ("sc", "k"), ("k", "ns"), ("k", "cg")],
            [
                step("User space", "nginx cannot touch hardware directly; it holds file descriptors and memory.", ["app"]),
                step("System call", "To send bytes it calls <b>write()</b>; the CPU traps into the kernel.", ["sc", "k"], [pkt("app", "sc"), pkt("sc", "k", "trap")]),
                step("Namespaces", "In a container the same process sees its own PID 1, network and filesystem.", ["ns"], [pkt("k", "ns")], {"ns": {"hidden": False}}),
                step("cgroups", "Its cgroup caps memory and CPU; exceeding memory.max triggers the OOM killer.", ["cg"], [pkt("k", "cg", "limit")], {"cg": {"hidden": False}}),
            ],
        ),
    },
]

SCENARIOS = [
    {"level": "intermediate", "topic": "processes", "q": "A server's CPU is pinned at 100% and the app is slow.", "a": "top or ps aux --sort=-%cpu to find the process, check what it is doing (strace -p, logs), then fix the cause. Stop it with SIGTERM, and only use SIGKILL if it ignores TERM. If it is a service, systemctl restart it and look at journalctl for why."},
    {"level": "advanced", "topic": "disks-storage", "q": "The disk is 100% full, but deleting old logs freed nothing.", "a": "A process still holds the deleted files open. sudo lsof +L1 lists them; restart or reload that process (or truncate via /proc/<pid>/fd). Then set up logrotate with copytruncate or a reload, and check df -i in case inodes are exhausted."},
    {"level": "intermediate", "topic": "permissions", "q": "A deploy script fails with Permission denied when run by the CI user.", "a": "Check ls -l on the script (x bit), on every parent directory (x to traverse) and on files it writes, plus id for the CI user's groups. Fix with chmod u+x, group ownership or setgid on a shared directory. Do not chmod 777 or run the whole pipeline as root."},
    {"level": "intermediate", "topic": "networking", "q": "The web app works with curl on the server but not from your laptop.", "a": "It is probably bound to 127.0.0.1 (ss -tlnp shows the address). Bind to 0.0.0.0 or the public interface, then check the host firewall (nft/ufw), cloud security groups and any reverse proxy."},
    {"level": "advanced", "topic": "kernel-internals", "q": "A container keeps restarting with exit code 137.", "a": "137 = 128 + 9 (SIGKILL), usually the cgroup OOM killer. Check dmesg or kubectl describe for OOMKilled and memory.current vs memory.max. Raise the limit, cap heap sizes to fit (for example JVM MaxRAMPercentage), or fix the leak."},
    {"level": "basic", "topic": "systemd-services", "q": "Your service runs fine but is gone after every reboot.", "a": "It was started but not enabled. sudo systemctl enable --now svc, and make sure the unit's [Install] section has WantedBy=multi-user.target."},
]

from .linux_more import CATEGORIES as _MORE_CATEGORIES, SCENARIOS as _MORE_SCENARIOS, TOPICS as _MORE_TOPICS

CATEGORIES += _MORE_CATEGORIES
TOPICS += _MORE_TOPICS
SCENARIOS += _MORE_SCENARIOS
