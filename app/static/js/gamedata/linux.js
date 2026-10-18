export const WORDS = [
  { answer: "KERNEL", term: "Kernel", clue: "Core of the OS that manages CPU, memory and devices" },
  { answer: "SHELL", term: "Shell", clue: "Program that reads your commands, such as bash or zsh" },
  { answer: "ROOT", term: "root", clue: "User with uid 0 who bypasses permission checks" },
  { answer: "SUDO", term: "sudo", clue: "Run a single command as another user, usually root" },
  { answer: "INODE", term: "Inode", clue: "On-disk record with a file's metadata but not its name" },
  { answer: "SYMLINK", term: "Symbolic link", clue: "A tiny file that stores a path to another file" },
  { answer: "HARDLINK", term: "Hard link", clue: "A second name for the same inode" },
  { answer: "MOUNT", term: "mount", clue: "Attach a filesystem to a directory in the tree" },
  { answer: "FSTAB", term: "/etc/fstab", clue: "File listing filesystems to mount at boot" },
  { answer: "CHMOD", term: "chmod", clue: "Change a file's permission bits" },
  { answer: "CHOWN", term: "chown", clue: "Change a file's owner and group" },
  { answer: "UMASK", term: "umask", clue: "Bits removed from the default mode of new files" },
  { answer: "STICKY", term: "Sticky bit", clue: "Lets only owners delete their files in /tmp" },
  { answer: "SETUID", term: "setuid", clue: "Makes a program run with its owner's privileges, like passwd" },
  { answer: "PIPE", term: "Pipe", clue: "Connects one command's stdout to the next command's stdin" },
  { answer: "STDERR", term: "stderr", clue: "File descriptor 2, where error messages go" },
  { answer: "GREP", term: "grep", clue: "Print lines that match a pattern" },
  { answer: "AWK", term: "awk", clue: "Field-based text processing language" },
  { answer: "SED", term: "sed", clue: "Stream editor for find and replace" },
  { answer: "UNIQ", term: "uniq", clue: "Collapses adjacent duplicate lines; -c counts them" },
  { answer: "XARGS", term: "xargs", clue: "Turns input lines into arguments for another command" },
  { answer: "PID", term: "PID", clue: "Number that identifies a running process" },
  { answer: "FORK", term: "fork()", clue: "System call that duplicates the calling process" },
  { answer: "EXEC", term: "exec()", clue: "System call that replaces a process's program" },
  { answer: "ZOMBIE", term: "Zombie", clue: "Exited process whose parent has not yet called wait()" },
  { answer: "SIGKILL", term: "SIGKILL", clue: "Signal 9: cannot be caught or ignored" },
  { answer: "SIGTERM", term: "SIGTERM", clue: "Signal 15: the polite request to exit" },
  { answer: "SYSTEMD", term: "systemd", clue: "Init system and service manager running as PID 1" },
  { answer: "JOURNALCTL", term: "journalctl", clue: "Reads logs from the systemd journal" },
  { answer: "CRON", term: "cron", clue: "Classic daemon that runs scheduled jobs" },
  { answer: "SHEBANG", term: "Shebang", clue: "The #! first line that names a script's interpreter" },
  { answer: "SYSCALL", term: "System call", clue: "How user programs ask the kernel to do work" },
  { answer: "CGROUP", term: "cgroup", clue: "Kernel feature that limits CPU and memory for a group of processes" },
  { answer: "NAMESPACE", term: "Namespace", clue: "Kernel feature that isolates what a process can see" },
  { answer: "PROC", term: "/proc", clue: "Virtual filesystem with per-process kernel information" },
  { answer: "SWAP", term: "Swap", clue: "Disk space used when RAM is full" },
];

export const RUSH = [
  { task: "Create a/b/c including missing parents", answer: "mkdir -p a/b/c", wrong: ["mkdir a/b/c", "mkdir -r a/b/c", "touch a/b/c"] },
  { task: "Count lines containing ERROR in app.log", answer: "grep -c ERROR app.log", wrong: ["grep -v ERROR app.log", "wc ERROR app.log", "cat -c ERROR app.log"] },
  { task: "Make deploy.sh executable for its owner", answer: "chmod u+x deploy.sh", wrong: ["chmod 644 deploy.sh", "chown +x deploy.sh", "chmod o-x deploy.sh"] },
  { task: "Show the last 50 lines of a log and keep following it", answer: "tail -n 50 -f app.log", wrong: ["head -50 app.log", "cat -f app.log", "less -50 app.log"] },
  { task: "Send only errors of a command to errors.txt", answer: "cmd 2> errors.txt", wrong: ["cmd > errors.txt", "cmd | errors.txt", "cmd 1> errors.txt"] },
  { task: "Capture both stdout and stderr into all.log", answer: "cmd > all.log 2>&1", wrong: ["cmd 2>&1 > all.log", "cmd >> 2 all.log", "cmd | tee 2"] },
  { task: "Find which process listens on port 80", answer: "ss -tlnp", wrong: ["ping -p 80", "ps -p 80", "df -p 80"] },
  { task: "Ask process 4242 to exit gracefully", answer: "kill 4242", wrong: ["kill -9 4242", "rm 4242", "stop 4242"] },
  { task: "Start nginx now and at every boot", answer: "sudo systemctl enable --now nginx", wrong: ["systemctl start nginx", "sudo service nginx boot", "nginx --daemon"] },
  { task: "Read the last logs of the nginx service", answer: "journalctl -u nginx -n 50", wrong: ["cat /etc/nginx", "systemctl logs nginx", "dmesg nginx"] },
  { task: "Create a symlink current pointing at releases/v2", answer: "ln -s releases/v2 current", wrong: ["ln current releases/v2", "cp -s releases/v2 current", "mv releases/v2 current"] },
  { task: "Show disk usage of each filesystem in human units", answer: "df -h", wrong: ["du -h /", "free -h", "lsblk -h"] },
  { task: "Find all .log files under /var", answer: "find /var -name '*.log'", wrong: ["grep -r .log /var", "ls -R *.log", "locate -d /var log"] },
  { task: "Third column of a comma-separated file", answer: "cut -d, -f3 file.csv", wrong: ["cut -f3 file.csv", "awk -F: '{print $3}' file.csv", "sort -k3 file.csv"] },
  { task: "Count duplicate lines in todo.txt", answer: "sort todo.txt | uniq -c", wrong: ["uniq -c todo.txt", "wc -d todo.txt", "grep -c todo.txt"] },
  { task: "Replace every 'foo' with 'bar' in a stream", answer: "sed 's/foo/bar/g'", wrong: ["sed 's/foo/bar/'", "tr foo bar", "grep -r foo bar"] },
  { task: "Stop a script at the first failing command", answer: "set -e", wrong: ["set -x", "exit 0", "trap -e"] },
  { task: "Run as root just this one command", answer: "sudo apt update", wrong: ["su apt update", "root apt update", "chmod 777 apt"] },
  { task: "Free inodes on each filesystem", answer: "df -i", wrong: ["du -i", "ls -i", "stat -f"] },
  { task: "List a process tree with parents and children", answer: "ps -ef --forest", wrong: ["top -tree", "ls /proc -R", "pstree --kill"] },
];

export const BUGS = [
  {
    symptom: "The backup script deletes the wrong directory when BACKUP_DIR is not set.",
    lang: "bash",
    code: `#!/usr/bin/env bash
BACKUP_DIR=$1
rm -rf $BACKUP_DIR/*
cp -r /srv/data/* $BACKUP_DIR/`,
    bug: [2],
    why: "With no argument, $BACKUP_DIR is empty and the line becomes rm -rf /*. Add set -euo pipefail, require the argument (${1:?usage: backup DIR}) and quote it: rm -rf -- \"${BACKUP_DIR:?}\"/*.",
  },
  {
    symptom: "The cron job's errors never appear in job.log.",
    lang: "bash",
    code: `# crontab
0 2 * * * /opt/job.sh 2>&1 > /var/log/job.log`,
    bug: [1],
    why: "Redirections apply left to right: 2>&1 points stderr at the original stdout (cron's mail), then > moves only stdout. Use > /var/log/job.log 2>&1.",
  },
  {
    symptom: "SSH refuses to use the key: 'UNPROTECTED PRIVATE KEY FILE!'",
    lang: "bash",
    code: `$ ls -la ~/.ssh
drwxr-xr-x  learner learner  .ssh
-rw-r--r--  learner learner  id_ed25519
-rw-r--r--  learner learner  id_ed25519.pub`,
    bug: [2],
    why: "The private key is readable by group and others. chmod 600 ~/.ssh/id_ed25519 (and chmod 700 ~/.ssh). The .pub file may stay 644.",
  },
  {
    symptom: "Counting unique visitors returns far too many lines.",
    lang: "bash",
    code: `cut -d' ' -f1 access.log | uniq -c | sort -rn | head`,
    bug: [0],
    why: "uniq only merges adjacent duplicates. Sort first: cut -d' ' -f1 access.log | sort | uniq -c | sort -rn | head.",
  },
  {
    symptom: "Every file in the web root became executable after a 'quick fix'.",
    lang: "bash",
    code: `sudo chown -R www-data:www-data /var/www
sudo chmod -R 777 /var/www`,
    bug: [1],
    why: "777 lets every user modify the site and makes all files executable. Use 755 for directories and 644 for files: find /var/www -type d -exec chmod 755 {} + and -type f -exec chmod 644 {} +.",
  },
  {
    symptom: "A loop over file names breaks on 'My Report.pdf'.",
    lang: "bash",
    code: `for f in $(ls *.pdf); do
  cp $f /archive/
done`,
    bug: [0, 1],
    why: "Parsing ls output and unquoted variables split names on spaces. Use the glob directly and quote: for f in *.pdf; do cp -- \"$f\" /archive/; done.",
  },
  {
    symptom: "The service runs after systemctl start but is gone after reboot.",
    lang: "ini",
    code: `[Unit]
Description=Web app

[Service]
ExecStart=/opt/app/server
Restart=on-failure`,
    bug: [5],
    why: "There is no [Install] section, so systemctl enable has nothing to link. Add [Install] WantedBy=multi-user.target, then sudo systemctl enable --now app.",
  },
  {
    symptom: "Security review flagged this deploy script.",
    lang: "bash",
    code: `#!/usr/bin/env bash
set -euo pipefail
DB_PASSWORD="EXAMPLE-ONLY-not-a-real-secret"
psql "postgresql://app:$DB_PASSWORD@db.internal/app" -f migrate.sql`,
    bug: [2, 3],
    why: "A hardcoded password ends up in Git history and the full URL shows up in ps output. Read it at runtime from the environment or a secret manager (PGPASSWORD from a protected file, or ~/.pgpass with mode 600), and rotate the leaked one.",
  },
];

export const META = {
  rushLabel: "Shell Rush",
  rushIntro: "Pick the command that does the job.",
  rushMono: true,
  bugLabel: "Shell Bug Hunt",
  bugNoun: "symptom",
};
