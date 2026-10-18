"""More linux topics, appended to the core module."""

from ._dsl import chain, ex, qa, topic

CATEGORIES = [
    {"id": "admin", "title": "Administration", "color": "peach", "blurb": "Boot, packages, scheduling, logs and time."},
    {"id": "remote", "title": "Remote & Network", "color": "sky", "blurb": "SSH, file transfer, DNS and firewalls."},
    {"id": "perf", "title": "Performance", "color": "slate", "blurb": "Memory, CPU, I/O and finding the bottleneck."},
]

_BATCH_1 = [
    topic(
        "boot-process", "Boot Process: UEFI to systemd", "admin", "advanced", "BT",
        "Firmware, bootloader, kernel, initramfs, then systemd brings up targets.",
        "Opening a shop in the morning. The landlord unlocks the building (firmware), the manager picks today's plan (GRUB), the staff arrive (kernel), a temporary crew sets up the tills so the real ones can work (initramfs), and the shift lead starts every station in the right order (systemd).",
        "Booting is a relay. UEFI firmware initialises hardware, checks Secure Boot signatures and runs a bootloader from the EFI System Partition (a small FAT32 partition mounted at /boot/efi). GRUB2 (or systemd-boot) shows a menu, loads the kernel image (vmlinuz) and an initramfs into memory, and passes the kernel command line (root=UUID=..., quiet, ro). The kernel decompresses itself, initialises CPUs, memory and built-in drivers, then unpacks the initramfs: a tiny root filesystem with the modules and tools needed to find the real root disk (LVM, RAID, LUKS, NVMe drivers). Once the real root is mounted, it switches root and execs /sbin/init, which is systemd on modern distributions. systemd reads unit files and starts everything required by the default target, usually multi-user.target (servers) or graphical.target (desktops), in parallel according to dependencies. Targets replace SysV runlevels: rescue.target is roughly runlevel 1, multi-user.target runlevel 3 and graphical.target runlevel 5.",
        ["Recovering a server that drops to an emergency shell after a disk change.", "Adding a kernel parameter such as systemd.unit=rescue.target or mitigations settings.", "Finding which service makes boot slow with systemd-analyze blame.", "Rebuilding the initramfs after adding a storage driver."],
        [
            "UEFI -> bootloader (GRUB) -> kernel + initramfs -> switch_root -> systemd (PID 1).",
            "Kernel command line is in /proc/cmdline; GRUB defaults live in /etc/default/grub.",
            "initramfs exists so the kernel can reach a root disk that needs modules or unlocking.",
            "systemctl get-default / set-default chooses the target reached at boot.",
            "systemd-analyze blame and critical-chain show where boot time goes.",
        ],
        [
            ex("Inspect how this box booted", "intermediate", "Kernel version, command line, default target and slow units (real Linux).", "bash", """
                uname -r
                cat /proc/cmdline
                systemctl get-default
                systemd-analyze
                systemd-analyze blame | head -n 10
                systemd-analyze critical-chain
            """, runnable=False),
            ex("Change kernel parameters and targets", "advanced", "Edit GRUB defaults, regenerate the config, switch targets.", "bash", """
                sudo nano /etc/default/grub            # GRUB_CMDLINE_LINUX="... quiet"
                sudo update-grub                        # Debian/Ubuntu
                sudo grub2-mkconfig -o /boot/grub2/grub.cfg   # RHEL/Fedora
                sudo systemctl set-default multi-user.target
                sudo systemctl isolate rescue.target    # switch now (drops users)
                journalctl -b -1 -p err                 # errors from the previous boot
            """, runnable=False),
            ex("Rebuild the initramfs", "advanced", "Needed after adding storage drivers or changing crypttab.", "bash", """
                lsinitramfs /boot/initrd.img-$(uname -r) | grep nvme   # Debian/Ubuntu
                sudo update-initramfs -u
                sudo dracut --force                                     # RHEL/Fedora
            """, runnable=False),
        ],
        ["cat /proc/cmdline", "systemctl get-default", "systemd-analyze blame", "journalctl -b -1 -p err", "sudo update-grub · update-initramfs -u"],
        ["A wrong UUID in /etc/fstab can drop boot into emergency mode; use nofail for non-critical disks.", "Editing grub.cfg directly is overwritten on the next update; edit /etc/default/grub and regenerate.", "Secure Boot rejects unsigned kernels or out-of-tree modules unless you enrol a key (MOK)."],
        [
            qa("basic", "List the stages of a Linux boot.", "Firmware (UEFI or BIOS) initialises hardware and runs the bootloader. GRUB loads the kernel and initramfs. The kernel initialises hardware, mounts the initramfs, finds and mounts the real root, then runs /sbin/init (systemd), which starts units for the default target."),
            qa("intermediate", "What is the initramfs for?", "It is a temporary root filesystem loaded by the bootloader. It contains the drivers and tools needed to locate and mount the real root (LVM, RAID, LUKS, network root), after which the kernel switches root and runs the real init."),
            qa("intermediate", "How do systemd targets relate to runlevels?", "Targets are named groups of units that represent a system state. rescue.target is like runlevel 1, multi-user.target like 3 and graphical.target like 5. systemctl set-default chooses the boot target and systemctl isolate switches immediately."),
            qa("advanced", "A server boots into emergency mode after adding a disk. How do you fix it?", "Log in at the emergency shell, read journalctl -xb for the failing mount, and check /etc/fstab for a wrong UUID or a missing device (blkid lists real UUIDs). Fix the entry or add nofail, run mount -a to test, then reboot."),
            qa("advanced", "How do you find what makes boot slow?", "systemd-analyze shows firmware, loader, kernel and userspace time. systemd-analyze blame lists units by start time, and critical-chain shows the dependency path that actually delayed the default target."),
        ],
        ["systemd-services", "kernel-internals", "disks-storage"],
        chain(
            ("UEFI", "POST, Secure Boot", "Firmware", "Firmware checks hardware and runs the signed bootloader from the <b>EFI System Partition</b>."),
            ("GRUB", "menu, cmdline", "Bootloader", "GRUB loads <b>vmlinuz</b> and the <b>initramfs</b> and passes root=UUID=... on the command line.", "load"),
            ("Kernel", "drivers, memory", "Kernel init", "The kernel sets up CPUs and memory and unpacks the initramfs as a temporary root.", "exec"),
            ("initramfs", "find real root", "Early userspace", "Loads storage modules, assembles LVM/RAID, unlocks LUKS, mounts the real root and calls switch_root.", "mount"),
            ("systemd", "PID 1", "Init", "systemd becomes PID 1 and resolves the unit dependency graph.", "exec"),
            ("Target", "multi-user", "Default target", "Services wanted by <b>multi-user.target</b> start in parallel; login prompts appear.", "start"),
        ),
    ),
    topic(
        "package-management", "Package Management: apt, dnf, rpm", "admin", "basic", "PK",
        "Install, update and verify software from signed repositories.",
        "An app store run by your distribution. The catalogue (repository metadata) lists every app and what it depends on; the store clerk (apt or dnf) fetches the right versions, checks the seal (GPG signature) and installs everything in order.",
        "Distributions ship software as packages: .deb files on Debian and Ubuntu, .rpm files on RHEL, Fedora and SUSE. Low-level tools (dpkg, rpm) install a single file and track which files it owns. High-level tools (apt, dnf, zypper) resolve dependencies, download from repositories configured in /etc/apt/sources.list.d or /etc/yum.repos.d, and verify each package with the repository's GPG key. apt update refreshes the catalogue, apt upgrade installs newer versions, and apt install or remove change individual packages; dnf combines refresh and install. You can ask which package owns a file (dpkg -S, rpm -qf), list a package's files (dpkg -L, rpm -ql) and verify installed files against the package database (rpm -V, debsums). Pinning or version locks keep critical packages from moving, and unattended-upgrades or dnf-automatic apply security fixes automatically.",
        ["Installing nginx or postgres on a fresh server.", "Applying security updates across a fleet.", "Finding which package provides a missing command or file.", "Holding a kernel or database version during an upgrade freeze."],
        [
            "apt update refreshes metadata; apt upgrade changes installed packages.",
            "dpkg/rpm handle single files; apt/dnf resolve dependencies from repos.",
            "Repositories are trusted through GPG signing keys; never disable signature checks.",
            "dpkg -S /path or rpm -qf /path tells you which package owns a file.",
            "apt-mark hold / dnf versionlock freeze a package version.",
        ],
        [
            ex("Debian and Ubuntu", "basic", "Refresh, search, install, inspect and clean up.", "bash", """
                sudo apt update
                apt search ripgrep
                sudo apt install -y ripgrep
                apt show ripgrep
                dpkg -L ripgrep | head
                dpkg -S /usr/bin/rg
                sudo apt remove ripgrep && sudo apt autoremove
            """, runnable=False),
            ex("RHEL, Fedora and Rocky", "basic", "The same tasks with dnf and rpm.", "bash", """
                sudo dnf check-update
                sudo dnf install -y nginx
                rpm -qi nginx
                rpm -ql nginx | head
                rpm -qf /usr/sbin/nginx
                sudo rpm -V nginx          # verify files against the package database
                dnf history
            """, runnable=False),
            ex("Holds and security updates", "intermediate", "Freeze a version and automate security patches.", "bash", """
                sudo apt-mark hold postgresql-16
                apt-mark showhold
                sudo apt install unattended-upgrades
                sudo dpkg-reconfigure -plow unattended-upgrades
                sudo dnf install 'dnf-command(versionlock)' && sudo dnf versionlock add kernel
            """, runnable=False),
        ],
        ["apt update && apt upgrade", "apt install · apt remove · apt autoremove", "dnf install · dnf history", "dpkg -S file · rpm -qf file", "apt-mark hold pkg"],
        ["apt upgrade without apt update installs nothing new: the catalogue is stale.", "curl | sudo bash installers bypass package signatures and tracking; prefer signed repositories.", "Mixing repositories from different releases (or PPAs) can break dependency resolution.", "Removing a package with autoremove may pull out libraries other manual installs still need."],
        [
            qa("basic", "Difference between apt update and apt upgrade?", "apt update downloads fresh package lists from the repositories. apt upgrade then installs newer versions of already installed packages based on those lists."),
            qa("basic", "dpkg vs apt (or rpm vs dnf)?", "dpkg and rpm install, remove and query individual package files without resolving dependencies. apt and dnf are front ends that find packages in repositories, resolve and download dependencies and then call the low-level tool."),
            qa("intermediate", "How do you find which package installed /usr/bin/rg?", "dpkg -S /usr/bin/rg on Debian-based systems or rpm -qf /usr/bin/rg on RPM-based systems. To find a package for a file that is not installed yet, use apt-file search or dnf provides."),
            qa("intermediate", "How are repository packages trusted?", "Repositories publish metadata signed with a GPG key that the system trusts (in /etc/apt/keyrings or rpm --import). The client verifies the metadata signature and package checksums (SHA-256) before installing."),
            qa("advanced", "How do you keep a database version from changing during upgrades?", "Hold it: apt-mark hold postgresql-16 or dnf versionlock add postgresql. Upgrade it deliberately later, after testing, and remove the hold."),
        ],
        ["systemd-services", "filesystem", "shell-scripting"],
        chain(
            ("apt update", "fetch metadata", "Refresh catalogue", "apt downloads signed package lists from each configured repository."),
            ("Verify", "GPG signature", "Trust check", "Metadata signatures are checked against keys in <b>/etc/apt/keyrings</b>.", "lists"),
            ("Resolve", "dependency graph", "Dependency solve", "apt install nginx computes every library and version needed.", "plan"),
            ("Download", ".deb + SHA-256", "Fetch packages", "Packages are downloaded and their checksums verified.", "debs"),
            ("dpkg", "unpack, scripts", "Install", "dpkg unpacks files, records ownership and runs maintainer scripts (for example to start the service).", "install"),
        ),
    ),
    topic(
        "users-groups", "Managing Users & Groups", "security", "basic", "UG",
        "Accounts live in /etc/passwd, /etc/shadow and /etc/group; manage them with useradd and usermod.",
        "A company directory. /etc/passwd is the staff list (name, badge number, desk), /etc/shadow is the locked drawer with password hashes, and /etc/group lists the teams. HR (root) adds people and moves them between teams.",
        "Each account has a username, a numeric uid, a primary gid, a home directory and a login shell, stored as colon-separated fields in /etc/passwd. Password hashes (yescrypt or SHA-512 crypt on modern systems) are in /etc/shadow, readable only by root and the shadow group, along with ageing data. Groups and their members are in /etc/group. useradd -m creates a user and home directory, usermod -aG adds supplementary groups (-a is critical, otherwise existing groups are replaced), passwd sets a password and userdel -r removes a user and home. System accounts (uid below 1000) run services and usually have /usr/sbin/nologin as shell. id shows a user's uid, gid and groups; group changes only apply to new login sessions. getent passwd queries every configured source (local files, LDAP, SSSD) through NSS.",
        ["Onboarding a new engineer with the right groups.", "Creating a locked system account for a service.", "Auditing who has a login shell or sudo membership.", "Off-boarding: locking and removing accounts safely."],
        [
            "/etc/passwd fields: name:x:uid:gid:comment:home:shell.",
            "usermod -aG docker alice appends; without -a it replaces the group list.",
            "Service accounts: useradd --system --shell /usr/sbin/nologin.",
            "Group membership changes need a new login (or newgrp) to apply.",
            "getent passwd/group also sees LDAP or SSSD users, cat only sees local files.",
        ],
        [
            ex("Read the account databases", "basic", "Who exists, which shells they use and what groups you are in.", "bash", """
                whoami
                id
                cat /etc/passwd
                cut -d: -f1,3,7 /etc/passwd
                awk -F: '$3 >= 1000 {print $1}' /etc/passwd
                grep learner /etc/passwd
                ls -l /etc/shadow
                cat /etc/shadow
            """),
            ex("Create and manage accounts", "intermediate", "Users, groups and a service account (real Linux, needs root).", "bash", """
                sudo useradd -m -s /bin/bash -c "Alice Dev" alice
                sudo passwd alice
                sudo groupadd developers
                sudo usermod -aG developers,docker alice
                id alice
                sudo useradd --system --no-create-home --shell /usr/sbin/nologin appsvc
                getent passwd appsvc
            """, runnable=False),
            ex("Lock and remove", "intermediate", "Off-boarding without losing evidence first.", "bash", """
                sudo usermod -L -e 1 alice      # lock password and expire the account
                sudo chage -l alice
                sudo pkill -u alice             # end running sessions
                sudo tar czf /root/alice-home.tgz /home/alice
                sudo userdel -r alice
            """, runnable=False),
        ],
        ["id · whoami · getent passwd user", "useradd -m -s /bin/bash user", "usermod -aG group user", "passwd user · chage -l user", "userdel -r user"],
        ["usermod -G group (without -a) silently removes all other supplementary groups.", "Editing /etc/passwd by hand risks corruption; use vipw or the user tools.", "Deleting a user leaves files owned by the numeric uid; a future user with that uid inherits them."],
        [
            qa("basic", "Where are users and passwords stored?", "/etc/passwd stores the account record (name, uid, gid, home, shell) and is world-readable. Password hashes and ageing data live in /etc/shadow, readable only by root and the shadow group."),
            qa("basic", "How do you add an existing user to a group?", "sudo usermod -aG groupname user. The -a appends; without it the user's supplementary group list is replaced. The user must log in again for the change to apply."),
            qa("intermediate", "Primary vs supplementary group?", "The primary group (gid in /etc/passwd) is assigned to files the user creates. Supplementary groups (listed in /etc/group) grant extra access, such as sudo or docker."),
            qa("intermediate", "What is a system account and why use nologin?", "A low-uid account that exists only to run a service with least privilege. Its shell is /usr/sbin/nologin and it has no password, so nobody can log in as it interactively."),
            qa("advanced", "Why might cat /etc/passwd not show a user who can log in?", "The user comes from another NSS source such as LDAP or SSSD. getent passwd user queries all sources configured in /etc/nsswitch.conf."),
        ],
        ["permissions", "sudo-sudoers", "special-permissions"],
        chain(
            ("login alice", "name + password", "Login", "alice types her name and password at a prompt or over SSH."),
            ("NSS", "nsswitch.conf", "Look up account", "NSS finds alice in <b>/etc/passwd</b> (or LDAP): uid 1001, home, shell.", "getpwnam"),
            ("PAM", "check shadow", "Authenticate", "PAM hashes the password and compares it with <b>/etc/shadow</b>.", "verify"),
            ("Groups", "/etc/group", "Collect groups", "Supplementary groups are loaded: developers, docker.", "initgroups"),
            ("Shell", "uid=1001", "Session", "The shell starts with alice's uid and groups; the kernel uses them for every permission check.", "exec"),
        ),
    ),
    topic(
        "sudo-sudoers", "sudo & the sudoers File", "security", "intermediate", "SU",
        "Grant specific root commands to specific users, with an audit trail.",
        "A building manager's key cabinet. Instead of handing everyone the master key (root password), the manager signs out particular keys to particular people, and the log book records every checkout.",
        "sudo runs a command as another user, root by default, after checking policy in /etc/sudoers and files in /etc/sudoers.d. A rule reads who where = (as_whom) what, for example alice ALL=(root) /usr/bin/systemctl restart nginx, and %admin ALL=(ALL:ALL) ALL grants a whole group full access. The user authenticates with their own password (cached for a few minutes), so nobody needs to share the root password, and every invocation is logged to the journal or /var/log/auth.log. Always edit with visudo, which locks the file and refuses to save syntax errors that would lock everyone out. NOPASSWD removes the password prompt and should be limited to narrow commands used by automation. Commands that can spawn shells (vim, less, find -exec, tar --checkpoint-action) allow escaping to a full root shell, so restrict rules to exact commands and arguments. sudo -l shows what you may run; sudo -i or sudo -s open root shells.",
        ["Letting on-call engineers restart one service without full root.", "Giving a CI deploy user a narrow passwordless command.", "Auditing who ran which privileged command.", "Disabling direct root SSH login while keeping admin access."],
        [
            "Edit only with visudo (or visudo -f /etc/sudoers.d/file).",
            "Rule syntax: user host=(runas) command; %group for groups.",
            "Users authenticate with their own password; the root password stays secret.",
            "Every sudo call is logged; that audit trail is a key reason to prefer sudo over su.",
            "Commands with shell escapes (vim, less, find) effectively grant full root.",
        ],
        [
            ex("Without and with privilege", "basic", "Who you are and what root-only files look like.", "bash", """
                whoami
                id
                ls -l /etc/shadow
                cat /etc/shadow
            """),
            ex("Write a narrow sudo rule", "intermediate", "A drop-in file validated by visudo (real Linux).", "bash", """
                sudo visudo -f /etc/sudoers.d/oncall
                # %oncall ALL=(root) /usr/bin/systemctl restart nginx, /usr/bin/journalctl -u nginx
                # deploy  ALL=(root) NOPASSWD: /usr/local/bin/deploy-app
                sudo chmod 0440 /etc/sudoers.d/oncall
                sudo visudo -c                  # check every sudoers file
                sudo -l -U alice                # what alice may run
            """, runnable=False),
            ex("Audit sudo usage", "intermediate", "Find recent privileged commands.", "bash", """
                sudo journalctl _COMM=sudo --since today
                sudo grep sudo /var/log/auth.log | tail -n 20
                sudo -k                         # drop your cached credentials
            """, runnable=False),
        ],
        ["sudo cmd · sudo -u user cmd", "sudo -l", "sudo visudo -f /etc/sudoers.d/x", "sudo visudo -c", "journalctl _COMM=sudo"],
        ["A syntax error in sudoers written without visudo can lock out every admin.", "sudo echo x > /root/file fails: the redirect runs in your unprivileged shell. Use echo x | sudo tee /root/file.", "Allowing an editor or pager via sudo lets the user spawn a root shell (:!sh).", "Wildcards in command arguments can match far more than intended."],
        [
            qa("basic", "sudo vs su?", "su switches to another user (default root) and needs that user's password. sudo runs a single command as another user after checking sudoers policy and asks for your own password, with every call logged."),
            qa("intermediate", "Why use visudo?", "It locks the file, opens it in an editor and validates the syntax before saving. A broken sudoers file can stop everyone from using sudo, which on servers without a root password means losing admin access."),
            qa("intermediate", "Why does sudo echo hi > /etc/motd fail?", "The redirection is performed by your own shell before sudo runs, so it lacks permission. Use echo hi | sudo tee /etc/motd or sudo sh -c 'echo hi > /etc/motd'."),
            qa("advanced", "What is risky about NOPASSWD rules?", "Anyone who gets that user's session can run the command as root with no prompt. Keep NOPASSWD to exact, non-interactive commands with fixed arguments, and never allow editors, shells or interpreters."),
        ],
        ["users-groups", "permissions", "logs-journald"],
        chain(
            ("sudo cmd", "as alice", "Request", "alice runs <b>sudo systemctl restart nginx</b>."),
            ("sudoers", "match rule", "Policy", "sudo finds a matching rule in <b>/etc/sudoers.d/oncall</b>.", "lookup"),
            ("PAM", "alice password", "Authenticate", "alice confirms with her own password (cached about 15 minutes).", "auth"),
            ("Log", "journal", "Audit", "The command, user and working directory are logged.", "record"),
            ("Run as root", "uid 0", "Execute", "The command runs as root; nothing else gains privilege.", "exec"),
        ),
    ),
    topic(
        "special-permissions", "setuid, setgid & the Sticky Bit", "security", "advanced", "SP",
        "Three extra mode bits that change who a program runs as and who may delete files.",
        "setuid is a valet ticket: anyone handing it over gets the car parked as the valet. setgid on a shared folder is a team stamp on every document filed there. The sticky bit is a shared fridge rule: you may only take out food you put in.",
        "Beyond rwx there are three special bits, written as a leading octal digit. setuid (4000) on an executable makes it run with the file owner's uid instead of the caller's; passwd uses it to update /etc/shadow as root. setgid (2000) on an executable runs it with the file's group; on a directory it makes new files inherit the directory's group, which keeps shared project folders consistent. The sticky bit (1000) on a directory means only the file owner, the directory owner or root may delete or rename entries, which is why /tmp is mode 1777. ls -l shows them as s in the user or group execute slot and t in the others slot; a capital S or T means the bit is set but execute is not. Linux ignores setuid on scripts, and nosuid mount options disable it on whole filesystems. Because setuid binaries are a classic privilege escalation path, audit them regularly with find / -perm -4000.",
        ["A shared team directory where every file belongs to the team group.", "World-writable scratch space that users cannot clean out for each other.", "Understanding why passwd or ping can do privileged work.", "Security audits for unexpected setuid binaries."],
        [
            "4 = setuid, 2 = setgid, 1 = sticky: chmod 2775 dir, chmod 1777 dir.",
            "ls shows s/t; uppercase S/T means the execute bit underneath is missing.",
            "setgid on a directory: new files inherit the directory group.",
            "Sticky directory: only owners (or root) can delete their entries.",
            "Audit with find / -perm -4000 -type f; mount untrusted disks nosuid.",
        ],
        [
            ex("Shared directory with setgid and sticky", "intermediate", "Group inheritance plus delete protection.", "bash", """
                mkdir shared
                chmod 2775 shared
                ls -ld shared
                chmod +t shared
                ls -ld shared
                stat shared
                ls -ld /tmp
            """),
            ex("Reading s and S", "advanced", "The setuid bit with and without execute.", "bash", """
                touch tool
                chmod 4755 tool
                ls -l tool
                chmod u-x tool
                ls -l tool
                stat tool
            """),
            ex("Audit setuid binaries", "advanced", "Find every setuid/setgid file on a real system.", "bash", """
                sudo find / -xdev -perm -4000 -type f -exec ls -l {} \\; 2>/dev/null
                sudo find / -xdev -perm -2000 -type f 2>/dev/null
                ls -l /usr/bin/passwd           # -rwsr-xr-x root root
                findmnt -o TARGET,OPTIONS | grep nosuid
            """, runnable=False),
        ],
        ["chmod u+s file · chmod 4755 file", "chmod g+s dir · chmod 2775 dir", "chmod +t dir · chmod 1777 dir", "find / -perm -4000 -type f", "mount -o nosuid,nodev"],
        ["setuid on a shell script is ignored by Linux; use a small binary or a sudo rule instead.", "Copying a file drops the setuid bit, but chmod -R with octal can add it everywhere by mistake.", "A setuid root binary with a bug is a direct path to root; keep the list short."],
        [
            qa("intermediate", "What does setuid do and give an example?", "When a setuid executable runs, the process's effective uid becomes the file's owner. /usr/bin/passwd is setuid root so ordinary users can update their own hash in /etc/shadow."),
            qa("intermediate", "Why does /tmp have mode 1777?", "Everyone needs to create files there (777), but the sticky bit (1) stops users deleting or renaming files they do not own."),
            qa("intermediate", "How do you make a team directory where files stay in the team's group?", "chgrp team dir and chmod 2775 dir. setgid on the directory makes new files and subdirectories inherit the team group; a umask of 002 keeps them group-writable."),
            qa("advanced", "What does a capital S in ls -l mean?", "The setuid (or setgid) bit is set but the corresponding execute bit is not, so it has no useful effect. It usually indicates a mistake."),
            qa("advanced", "Why audit setuid files?", "Any setuid root program runs with root privileges for every user, so a vulnerability or a planted binary gives local privilege escalation. Track them with find / -perm -4000 and mount removable or user-writable filesystems with nosuid."),
        ],
        ["permissions", "users-groups", "acls"],
        chain(
            ("learner runs", "uid 1000", "Caller", "learner runs <b>/usr/bin/passwd</b>, mode -rwsr-xr-x root."),
            ("exec()", "setuid bit", "Kernel exec", "The kernel sees the setuid bit and sets the effective uid to the file owner.", "exec"),
            ("euid = 0", "real uid 1000", "Privileged", "The process now acts as root but remembers the real user.", "euid"),
            ("/etc/shadow", "write hash", "Do the job", "passwd updates only learner's hash and exits.", "write"),
        ),
    ),
    topic(
        "acls", "Access Control Lists (ACLs)", "security", "advanced", "AC",
        "Per-user and per-group permissions beyond owner/group/others.",
        "The owner/group/others model is a door with three keys. An ACL is a guest list taped to the door: Bob may read, the auditors group may read and write, everyone else follows the normal rules.",
        "POSIX ACLs extend the classic mode bits with named entries: user:bob:r--, group:auditors:rw-. setfacl -m adds or changes entries and getfacl shows them; ls -l marks files with ACLs with a trailing +. The mask entry is the maximum permission any named user, named group or the owning group can get, and chmod on the group bits actually changes the mask, which can silently reduce ACL access. Default ACLs on a directory (setfacl -d -m) are inherited by new files and subdirectories, which solves shared-directory permission problems more precisely than setgid plus umask. ACLs are supported by ext4, XFS and Btrfs and are honoured by the kernel on every access check. Backups and copies must preserve them (cp -a, rsync -A, tar --acls), otherwise the extra access disappears silently.",
        ["Giving one contractor read access to a project without adding them to its group.", "A shared upload directory where a web server and a deploy user both need write.", "Default permissions that new files in a directory inherit.", "Auditing unusual access on sensitive paths."],
        [
            "setfacl -m u:bob:rx file adds an entry; setfacl -x u:bob file removes it.",
            "A + after the mode in ls -l means an ACL exists; read it with getfacl.",
            "The mask caps named entries; chmod g=... rewrites the mask.",
            "Default ACLs (-d) apply to newly created children only.",
            "Preserve ACLs with cp -a, rsync -A and tar --acls.",
        ],
        [
            ex("Grant one extra user", "intermediate", "Add, inspect and remove a named entry (real Linux).", "bash", """
                touch report.csv
                setfacl -m u:bob:r report.csv
                getfacl report.csv
                ls -l report.csv               # -rw-r--r--+  (note the +)
                setfacl -x u:bob report.csv
                setfacl -b report.csv          # remove all ACL entries
            """, runnable=False),
            ex("Default ACLs for a shared directory", "advanced", "New files automatically grant the deploy user write access.", "bash", """
                sudo mkdir -p /srv/uploads
                sudo setfacl -m u:www-data:rwx,u:deploy:rwx /srv/uploads
                sudo setfacl -d -m u:www-data:rwx,u:deploy:rwx /srv/uploads
                getfacl /srv/uploads
                sudo -u deploy touch /srv/uploads/new.txt && getfacl /srv/uploads/new.txt
            """, runnable=False),
            ex("Backups that keep ACLs", "advanced", "Copy tools drop ACLs unless asked.", "bash", """
                getfacl -R /srv/uploads > uploads.acl
                rsync -aA /srv/uploads/ backup:/srv/uploads/
                tar --acls -czf uploads.tgz /srv/uploads
                setfacl --restore=uploads.acl
            """, runnable=False),
        ],
        ["getfacl file", "setfacl -m u:bob:rx file", "setfacl -d -m g:team:rwx dir", "setfacl -x u:bob file · setfacl -b file", "rsync -aA · tar --acls"],
        ["chmod 750 on a file with ACLs changes the mask and may cut named users' access.", "Default ACLs do not change existing files; apply with setfacl -R -m as well.", "Some tools and network filesystems ignore POSIX ACLs entirely."],
        [
            qa("intermediate", "When would you use an ACL instead of a group?", "When access needs to be granted to a specific user or second group without restructuring group membership, for example one contractor reading one directory. Groups are simpler to audit, so use ACLs for exceptions."),
            qa("intermediate", "How do you see whether a file has an ACL?", "ls -l shows a + after the permission string. getfacl file prints the owner, group, named entries, mask and other entries."),
            qa("advanced", "What is the ACL mask?", "It is the upper bound on permissions granted by named user entries, named group entries and the owning group. Effective permission is the entry ANDed with the mask, and chmod on group bits rewrites the mask."),
            qa("advanced", "What is a default ACL?", "An ACL set on a directory with setfacl -d that is copied to files and subdirectories created inside it. It gives consistent inherited permissions without relying on each user's umask."),
        ],
        ["permissions", "special-permissions", "users-groups"],
        chain(
            ("open()", "bob, read", "Request", "bob opens report.csv for reading."),
            ("Owner?", "no", "Owner entry", "bob is not the owner, so owner bits do not apply.", "uid"),
            ("Named user", "user:bob:r--", "ACL entry", "A named entry for bob exists: <b>r--</b>.", "match"),
            ("Mask", "mask::r-x", "Cap", "Effective = entry AND mask = r--.", "and"),
            ("Allowed", "read ok", "Result", "Read succeeds; a write would still be denied.", "ok"),
        ),
    ),
    topic(
        "links-hard-soft", "Hard Links vs Symbolic Links", "basics", "intermediate", "LN",
        "Two names for one inode, or a pointer to a path.",
        "A hard link is a second front door into the same house: close one, the house is still reachable. A symbolic link is a signpost with an address painted on it: move the house and the sign points at an empty lot.",
        "A directory entry maps a name to an inode, and the inode holds the data and metadata. A hard link (ln target name) adds another name for the same inode, so both names are equal: neither is the original, the link count rises, and the data is freed only when the last name is removed and no process holds it open. Hard links cannot cross filesystems and cannot point to directories. A symbolic link (ln -s target name) is a tiny file containing a path; the kernel follows it on access. Symlinks can cross filesystems, point to directories and be relative or absolute, but they break (dangle) if the target moves or is deleted. ls -li shows inode numbers and link counts; readlink -f resolves the final target. Symlinks are everywhere in practice: /etc/alternatives, current -> releases/v42 deploy patterns and systemd's enable mechanism.",
        ["Atomic deploys by switching a current symlink between release directories.", "Keeping one config file referenced from several paths.", "Space-saving snapshots with hard links (rsync --link-dest).", "Understanding why deleting a file did not free space."],
        [
            "Hard link: same inode, link count +1, same filesystem only, files only.",
            "Symlink: separate inode holding a path; can dangle.",
            "rm removes a name; data is freed when link count and open handles reach 0.",
            "Relative symlinks resolve from the link's directory, not your cwd.",
            "ln -sfn new current switches a symlink in one step.",
        ],
        [
            ex("Create both kinds", "basic", "Compare inode numbers and link counts.", "bash", """
                ln notes.txt hard.txt
                ln -s notes.txt soft.txt
                ls -li notes.txt hard.txt soft.txt
                stat hard.txt
                cat soft.txt
            """),
            ex("Delete the original", "intermediate", "The hard link survives; the symlink dangles.", "bash", """
                ln notes.txt hard.txt
                ln -s notes.txt soft.txt
                rm notes.txt
                cat hard.txt
                cat soft.txt
                ls -l soft.txt
            """),
            ex("Directory links", "intermediate", "Symlinks to directories work; hard links do not.", "bash", """
                ln -s /var/log logdir
                ls logdir
                ls -l logdir
                ln logs hardlogs
            """),
        ],
        ["ln target name", "ln -s target name", "ls -li", "readlink -f name", "ln -sfn releases/v2 current"],
        ["rm -rf symlink/ (with a trailing slash) can delete the target directory's contents.", "Moving a relative symlink to another directory can break it.", "Some backup tools follow symlinks and copy huge trees twice."],
        [
            qa("basic", "Hard link vs soft link?", "A hard link is another directory entry for the same inode, so it is indistinguishable from the original and survives its deletion. A soft link is a separate file containing a path; it can cross filesystems and point at directories but breaks if the target disappears."),
            qa("intermediate", "Why can't you hard link a directory?", "It could create cycles in the tree and break tools that assume a strict hierarchy (find, fsck, du). The kernel forbids it; only . and .. are directory hard links."),
            qa("intermediate", "Why can't hard links cross filesystems?", "Inode numbers are only unique within one filesystem, and a hard link is just a name pointing at an inode number."),
            qa("advanced", "How do you switch a deploy atomically with symlinks?", "Create the new link under a temporary name and rename it over the old one: ln -s releases/v42 current.tmp && mv -T current.tmp current. rename() is atomic, so requests see either the old or the new release."),
        ],
        ["disks-storage", "filesystem", "files-commands"],
        chain(
            ("notes.txt", "name", "Name", "A directory entry maps <b>notes.txt</b> to inode 1042."),
            ("inode 1042", "links: 2", "Inode", "The inode holds data and a link count. <b>hard.txt</b> also points here.", "ln"),
            ("soft.txt", "path text", "Symlink", "A separate inode whose content is the path <b>notes.txt</b>.", "ln -s"),
            ("rm notes", "links: 1", "Unlink", "Removing notes.txt drops the count to 1: hard.txt still works, soft.txt dangles.", "rm"),
        ),
    ),
    topic(
        "find-xargs", "find, locate & xargs", "basics", "intermediate", "FX",
        "Search the tree by name, type, size or age and act on the results.",
        "find is a librarian walking every shelf with a checklist; locate is the card catalogue printed last night (fast, maybe stale); xargs is the assistant who takes the list and hands the books to the right desk in batches.",
        "find walks a directory tree and evaluates tests left to right: -name and -iname match globs, -type f/d/l filters by kind, -size +100M by size, -mtime +7 by age in days, -user and -perm by ownership and mode. Actions include -print (default), -delete and -exec cmd {} \\; or the faster -exec cmd {} + which batches arguments. Quote patterns so the shell does not expand them first. locate queries a database built by updatedb, so it is instant but misses recent files. xargs reads items from stdin and runs a command with them as arguments, in batches that respect the kernel's argument length limit; -P runs in parallel. File names with spaces or newlines break naive pipelines, so pair find -print0 with xargs -0. Always preview with -print before adding -delete.",
        ["Deleting logs older than 14 days.", "Finding the largest files when a disk fills.", "Running a linter or checksum on every matching file.", "Locating a config file by name quickly."],
        [
            "Quote globs: find . -name '*.log', not find . -name *.log.",
            "-exec cmd {} + batches; -exec cmd {} \\; runs once per file.",
            "find -print0 | xargs -0 handles spaces and newlines safely.",
            "Run without -delete first; put -delete last in the expression.",
            "locate is fast but only as fresh as the last updatedb.",
        ],
        [
            ex("Search by name and type", "basic", "Quote the patterns so find sees them.", "bash", """
                find . -name "*.log"
                find . -type d
                find . -type f -name "*.tmp"
                find / -name "*.conf"
            """),
            ex("Act on results with xargs", "intermediate", "Count lines in every log, then delete temp files.", "bash", """
                find logs -type f | xargs wc -l
                find tmp -name "*.tmp"
                find tmp -name "*.tmp" | xargs rm
                ls tmp
            """),
            ex("Real-world cleanups", "advanced", "Age, size, safe names and parallelism (real Linux).", "bash", """
                find /var/log/app -name '*.log' -mtime +14 -print
                find /var/log/app -name '*.log' -mtime +14 -delete
                sudo find / -xdev -type f -size +500M -exec ls -lh {} + 2>/dev/null
                find . -name '*.jpg' -print0 | xargs -0 -P 4 -n 20 sha256sum
                sudo updatedb && locate nginx.conf
            """, runnable=False),
        ],
        ["find . -name '*.log' -type f", "find /path -mtime +7 -delete", "find . -size +100M", "find . -print0 | xargs -0 cmd", "locate name · updatedb"],
        ["An unquoted -name *.log is expanded by the shell if a match exists in the current directory.", "-delete before the tests (find . -delete -name x) deletes everything.", "xargs without -0 splits on spaces, so 'my file.txt' becomes two arguments."],
        [
            qa("basic", "How do you find all .conf files under /etc?", "find /etc -type f -name '*.conf'. Quoting the pattern makes find do the matching instead of the shell."),
            qa("intermediate", "-exec {} \\; vs -exec {} +?", "\\; runs the command once per file. + appends as many file names as fit and runs the command a few times, which is much faster for large result sets."),
            qa("intermediate", "Why use find -print0 | xargs -0?", "Null bytes cannot appear in file names, so using them as separators handles names with spaces, quotes or newlines correctly."),
            qa("intermediate", "find vs locate?", "find walks the filesystem live and supports rich tests, but is slow on large trees. locate searches a prebuilt database, which is instant but misses files created since the last updatedb."),
            qa("advanced", "How do you delete files older than 30 days safely?", "Preview with find /path -type f -mtime +30 -print, then rerun with -delete as the last action. Restrict with -xdev, -name and -type so a mistake cannot walk into other filesystems."),
        ],
        ["files-commands", "pipes-redirection", "grep-regex"],
        chain(
            ("find logs", "walk tree", "Walk", "find descends into every directory under the start path."),
            ("Tests", "-type f -name", "Filter", "Each entry is tested left to right; failures stop early.", "entry"),
            ("Paths", "stdout", "Emit", "Matching paths are printed, one per line (or NUL-separated).", "match"),
            ("xargs", "batch argv", "Batch", "xargs packs paths into as few command lines as the kernel allows.", "pipe"),
            ("wc -l", "run once", "Act", "The command runs with the batch as arguments.", "exec"),
        ),
    ),
    topic(
        "archives-compression", "Archives & Compression: tar, gzip, zstd", "basics", "basic", "AR",
        "Bundle a tree into one file, then squeeze it.",
        "Moving house: tar packs everything into labelled boxes in one truck (keeping which room each item came from), and gzip or zstd vacuum-seals the boxes so the truck is smaller.",
        "tar (tape archive) concatenates files with their paths, permissions, owners and timestamps into a single stream; it does not compress by itself. Compression is a filter: -z gzip, -j bzip2, -J xz and --zstd zstd. c creates, x extracts, t lists, f names the archive file, and v prints names. gzip is universal and fast, xz compresses smallest but slowly, and zstd gives gzip-like ratios several times faster and supports multithreading (-T0), which makes it the modern default for backups and packages. -C changes directory before extracting, and --exclude skips patterns. Paths stored relative (tar -C /srv -czf app.tgz app) are safer than absolute ones. Always verify integrity with a strong checksum such as sha256sum, and be careful extracting untrusted archives: they may contain ../ paths or overwrite files (GNU tar strips leading / by default).",
        ["Backing up a directory before an upgrade.", "Shipping logs to support.", "Distributing release artifacts with checksums.", "Streaming a directory to another host over SSH."],
        [
            "tar -czf out.tgz dir (create), tar -xzf out.tgz -C dest (extract), tar -tzf (list).",
            "zstd: tar --zstd -cf out.tar.zst dir; fast, good ratio, multithreaded.",
            "Store relative paths with -C so extraction lands where you choose.",
            "Publish sha256sum checksums next to archives; never MD5 or SHA-1.",
            "List untrusted archives before extracting them.",
        ],
        [
            ex("Look before you pack", "basic", "Sizes and file lists in the simulator.", "bash", """
                du -sh logs data
                find logs -type f
                ls -l logs
            """),
            ex("Create, list, extract", "basic", "The everyday tar commands (real Linux).", "bash", """
                tar -czvf logs.tgz logs/
                tar -tzf logs.tgz
                mkdir -p restore && tar -xzf logs.tgz -C restore
                tar --zstd -cf logs.tar.zst logs/
                zstd -T0 -19 big.sql            # multithreaded, high ratio
                sha256sum logs.tgz > logs.tgz.sha256 && sha256sum -c logs.tgz.sha256
            """, runnable=False),
            ex("Stream over SSH", "intermediate", "No temporary file on either side.", "bash", """
                tar -C /srv -czf - app | ssh backup 'cat > /backups/app-$(date +%F).tgz'
                ssh web1 'tar -C /var/log -czf - nginx' | tar -xzf - -C ./web1-logs
            """, runnable=False),
        ],
        ["tar -czf a.tgz dir · tar -xzf a.tgz -C dest", "tar -tzf a.tgz", "tar --zstd -cf a.tar.zst dir", "gzip -k f · zstd -T0 f", "sha256sum -c file.sha256"],
        ["tar -czf dir.tgz dir dir.tgz can try to include the archive in itself.", "gzip file replaces the original unless -k is given.", "Extracting as root preserves owners from the archive; use --no-same-owner for untrusted ones."],
        [
            qa("basic", "Does tar compress?", "No. tar bundles files and metadata into one stream. Compression is applied by a filter such as gzip (-z), xz (-J) or zstd (--zstd)."),
            qa("basic", "How do you extract a .tar.gz into a specific directory?", "tar -xzf archive.tar.gz -C /target/dir. List it first with tar -tzf to see the paths it contains."),
            qa("intermediate", "gzip vs xz vs zstd?", "gzip is fast and universally available. xz gives the smallest files but is slow to compress. zstd is close to xz in ratio at high levels and much faster than gzip at default levels, with multithreading."),
            qa("intermediate", "How do you verify an archive was not corrupted or tampered with?", "Compare a SHA-256 checksum (sha256sum -c) published through a trusted channel, and ideally verify a GPG or Sigstore signature. MD5 and SHA-1 are broken for this purpose."),
        ],
        ["files-commands", "scp-rsync", "disks-storage"],
        chain(
            ("logs/", "files + metadata", "Source", "A directory tree with permissions and timestamps."),
            ("tar", "one stream", "Bundle", "tar writes headers and contents into a single stream.", "files"),
            ("zstd", "compress -T0", "Compress", "The stream is compressed on all cores.", "stream"),
            ("logs.tar.zst", "+ sha256", "Archive", "One file plus a SHA-256 checksum to verify later.", "bytes"),
        ),
    ),
    topic(
        "job-control", "Job Control: bg, fg, nohup", "system", "basic", "JC",
        "Run, pause, background and detach commands from your shell.",
        "A cook with several pans. Ctrl-Z moves a pan off the heat (stopped), bg puts it back on a back burner (running, unattended), fg brings it to the front, and nohup or tmux hands the pan to another cook so it keeps going after you leave.",
        "An interactive shell runs each pipeline as a job in its own process group. Appending & starts it in the background; Ctrl-Z sends SIGTSTP to stop the foreground job; jobs lists jobs with numbers; bg %1 resumes a stopped job in the background and fg %1 brings it to the foreground. Background jobs that try to read the terminal are stopped (SIGTTIN). When the terminal closes, the shell sends SIGHUP to its jobs, which usually kills them. nohup cmd & ignores SIGHUP and writes output to nohup.out; disown removes a job from the shell's table so it is not signalled. For anything long-running, prefer tmux or screen (which keep a session you can reattach) or a proper systemd service or systemd-run unit, which gives logs, restarts and resource limits.",
        ["Pausing an editor to run a quick command.", "Keeping a long data migration alive after logging out.", "Running several builds in parallel from one shell.", "Reattaching to a session after an SSH drop."],
        [
            "cmd & backgrounds; Ctrl-Z stops; bg/fg resume; jobs lists.",
            "%1, %+ and %- refer to jobs; kill %1 signals a job.",
            "Closing the terminal sends SIGHUP to jobs; nohup or disown avoids it.",
            "tmux new -s work, detach with Ctrl-b d, reattach with tmux attach -t work.",
            "Long-lived work belongs in systemd (systemd-run --unit=x cmd).",
        ],
        [
            ex("Foreground and background", "basic", "Stop, resume and list jobs (real interactive bash).", "bash", """
                sleep 300 &
                jobs -l
                vim notes.txt          # press Ctrl-Z to stop it
                jobs
                bg %2                  # (vim would stop again: it needs the terminal)
                fg %2
                kill %1
            """, runnable=False),
            ex("Survive logout", "intermediate", "nohup, disown, tmux and systemd-run.", "bash", """
                nohup ./migrate.sh > migrate.log 2>&1 &
                ./long-task.sh & disown
                tmux new -s work           # Ctrl-b d to detach
                tmux attach -t work
                systemd-run --user --unit=reindex ./reindex.sh
                journalctl --user -u reindex -f
            """, runnable=False),
        ],
        ["cmd & · jobs -l", "Ctrl-Z · bg %1 · fg %1", "kill %1", "nohup cmd > log 2>&1 &", "tmux new -s name · tmux attach"],
        ["nohup does not redirect stderr unless you do; output may land in nohup.out in the cwd.", "A background job that reads stdin stops silently; redirect stdin from /dev/null.", "disown and nohup do not survive a reboot; use a service for that."],
        [
            qa("basic", "How do you move a running command to the background?", "Press Ctrl-Z to stop it, then run bg to resume it in the background. jobs lists jobs and fg brings one back."),
            qa("intermediate", "Why do background jobs die when you close SSH?", "The terminal hangup causes the shell to send SIGHUP to its jobs, and the default action is to terminate. nohup makes the command ignore SIGHUP; disown stops the shell from sending it."),
            qa("intermediate", "nohup vs tmux?", "nohup only detaches one command from hangups, and you cannot interact with it again. tmux keeps a whole terminal session alive on the server that you can detach from and reattach to later."),
            qa("advanced", "When should a job become a systemd service instead?", "When it must survive reboots, restart on failure, log to the journal or have resource limits. systemd-run can launch a transient unit for one-off long tasks."),
        ],
        ["processes", "signals-kill", "systemd-services"],
        chain(
            ("Running", "foreground", "Start", "A command holds the terminal in the foreground."),
            ("Ctrl-Z", "SIGTSTP", "Stop", "The terminal sends SIGTSTP; the job is stopped.", "TSTP"),
            ("bg %1", "SIGCONT", "Resume", "bg sends SIGCONT and lets it run without the terminal.", "CONT"),
            ("Logout", "SIGHUP", "Hangup", "Closing the terminal sends SIGHUP unless nohup or disown was used.", "HUP"),
            ("tmux", "detached", "Persist", "A tmux session keeps running and can be reattached.", "attach"),
        ),
    ),
]

_BATCH_2 = [
    topic(
        "grep-regex", "grep & Regular Expressions", "text", "intermediate", "GR",
        "Find lines that match a pattern, from fixed strings to extended regex.",
        "A metal detector over a beach of text. Fixed-string mode looks for one exact coin; a regular expression describes a shape (any ring with a 3-digit engraving), and the flags decide whether to report the spot, count the finds or list only the beaches that had any.",
        "grep prints lines that match a pattern. Basic regular expressions (BRE, the default) treat ?, +, {, |, ( and ) as literals unless escaped; grep -E uses extended regular expressions (ERE) where they are operators; grep -F matches fixed strings with no regex at all, which is fastest and safest for user input; grep -P enables Perl syntax such as \\d and lookarounds on GNU grep. Anchors ^ and $ pin to line start and end, [0-9] and [[:space:]] are character classes, . is any character and * means zero or more of the previous item. Useful flags: -i ignore case, -v invert, -n line numbers, -c count, -o print only the matched part, -w whole words, -r recursive, -l files with matches, -A/-B/-C context lines and -q quiet (exit status only). The exit code is 0 for a match, 1 for none and 2 for an error, which makes grep -q a natural test in scripts. ripgrep (rg) is a faster recursive alternative that respects .gitignore.",
        ["Pulling error lines with context out of a log.", "Counting HTTP 5xx responses.", "Checking in a script whether a config already contains a line.", "Finding every file in a repo that mentions a function."],
        [
            "Quote patterns in single quotes so the shell leaves them alone.",
            "-E for alternation and +; -F for literal strings; -P for \\d and lookarounds.",
            "^ and $ anchor; -w matches whole words only.",
            "Exit codes: 0 match, 1 no match, 2 error; grep -q for tests.",
            "-o extracts just the match, great for feeding sort | uniq -c.",
        ],
        [
            ex("Everyday searches", "basic", "Line numbers, counts, inversion and case.", "bash", """
                grep -n ERROR logs/app.log
                grep -c ERROR logs/app.log
                grep -v INFO logs/app.log
                grep -i payment logs/app.log
                grep -rl ERROR logs
            """),
            ex("Extended regex", "intermediate", "Alternation, anchors, character classes and only-matching.", "bash", """
                grep -E "WARN|ERROR" logs/app.log
                grep "^203" logs/access.log
                grep -E " 5[0-9][0-9] " logs/access.log
                grep -oE "[0-9]+ ms" logs/app.log
                grep -w dev data/users.csv
                grep -oE "^[0-9.]+" logs/access.log | sort | uniq -c
            """),
            ex("grep in scripts", "intermediate", "Use the exit code instead of the output.", "bash", """
                grep -q timeout logs/app.log && echo "timeouts present"
                grep -q unicorn logs/app.log || echo "no unicorns"
                grep -c ERROR logs/app.log logs/access.log
            """),
            ex("Context and Perl regex", "advanced", "GNU grep extras on a real system.", "bash", """
                grep -C 2 'payment gateway' /var/log/app.log
                grep -P '\\d{3} ms' /var/log/app.log
                grep -rn --include='*.py' 'def handler' src/
                rg -n 'TODO|FIXME' --type py
            """, runnable=False),
        ],
        ["grep -n · -c · -v · -i · -w", "grep -E 'a|b' · grep -F 'literal'", "grep -o pattern | sort | uniq -c", "grep -rn pattern dir", "grep -q pattern file && ..."],
        ["Unquoted patterns with * or $ are expanded by the shell first.", "In BRE, a+ means 'a followed by a literal plus'; use -E.", "grep -r follows no symlinks by default but can still scan huge trees like node_modules; use --exclude-dir or rg.", "A pattern like . or .* matches everything; check what you are counting."],
        [
            qa("basic", "How do you count lines containing ERROR?", "grep -c ERROR file. It counts matching lines, not occurrences; for occurrences use grep -o ERROR file | wc -l."),
            qa("intermediate", "BRE vs ERE?", "In basic regex, ?, +, {}, | and () are literal unless backslash-escaped. Extended regex (grep -E) treats them as operators, which is easier to read for alternation and repetition."),
            qa("intermediate", "When use grep -F?", "When the pattern is a literal string, especially user input with dots or brackets. It avoids regex interpretation, so it is faster and cannot be tricked into catastrophic backtracking."),
            qa("intermediate", "What exit codes does grep return?", "0 when at least one line matched, 1 when none matched and 2 on errors such as a missing file. Scripts use grep -q in if statements to test without printing."),
            qa("advanced", "How do you extract and rank the most frequent IPs?", "grep -oE '^[0-9.]+' access.log | sort | uniq -c | sort -rn | head. -o prints only the match, uniq -c counts adjacent duplicates after sorting and sort -rn ranks them."),
        ],
        ["text-processing", "pipes-redirection", "sed-editing"],
        chain(
            ("Pattern", "-E ' 5[0-9]{2} '", "Compile", "grep compiles the regex once into a matching automaton."),
            ("Read line", "access.log", "Scan", "Each line is read in turn.", "line"),
            ("Match?", "regex engine", "Test", "The engine tests the line; -v would invert the answer.", "test"),
            ("Output", "-n -o -c", "Report", "Flags decide: print the line, just the match or only a count.", "hit"),
            ("Exit code", "0 / 1 / 2", "Status", "0 if anything matched, 1 if nothing, 2 on errors.", "$?"),
        ),
    ),
    topic(
        "sed-editing", "sed: Stream Editing", "text", "intermediate", "SD",
        "Substitute, delete and print lines without opening an editor.",
        "A copy editor on a conveyor belt. Every line passes under their pen once: they may rewrite a word (s), throw the line away (d) or only pass along the lines you asked for (-n p), and they never go back.",
        "sed reads input one line at a time into a pattern space, applies its script and prints the result. The most used command is s/regex/replacement/flags, where g replaces every match, i ignores case and & or \\1 in the replacement insert the whole match or a captured group. Addresses select lines: a number (3), a range (3,5), a regex (/ERROR/), or $ for the last line, so /^#/d deletes comments and sed -n '10,20p' prints a slice. -E enables extended regex so groups need no backslashes. -i edits files in place; GNU sed accepts -i.bak to keep a backup, and BSD/macOS sed needs -i ''. Any character can be the delimiter (s|/usr|/opt|), which avoids escaping slashes in paths. For anything beyond line-local edits, awk or a real script is usually clearer.",
        ["Changing a config value across many files.", "Stripping comments and blank lines from a config.", "Printing a line range from a big log.", "Normalising formats before further processing."],
        [
            "s/old/new/ first match per line; add g for all.",
            "Addresses: N, N,M, /re/, $; commands p, d, s.",
            "-n suppresses automatic printing, so use it with p.",
            "-E for (groups) and +; \\1 refers to the first group.",
            "-i edits in place: test without it first, keep a backup.",
        ],
        [
            ex("Substitute and delete", "basic", "Replace values and drop lines.", "bash", """
                sed 's/Pune/Mumbai/g' data/users.csv
                sed '/INFO/d' logs/app.log
                sed '1d' data/users.csv
                sed 's/ERROR/CRITICAL/' logs/app.log | grep CRITICAL
            """),
            ex("Print slices", "intermediate", "-n with p prints only what you select.", "bash", """
                sed -n '3,5p' logs/app.log
                sed -n '/timeout/p' logs/app.log
                sed -n '1p' data/users.csv
            """),
            ex("Groups and a safe edit", "intermediate", "Capture groups with -E, then write to a new file and diff.", "bash", """
                sed -E 's/([0-9]+) ms/\\1ms/' logs/app.log | grep ms
                sed 's/Pune/Mumbai/g' data/users.csv > users2.csv
                diff data/users.csv users2.csv
            """),
            ex("In-place edits on a real system", "advanced", "GNU sed with backups and custom delimiters.", "bash", """
                sudo sed -i.bak 's/^#\\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
                sed -i 's|/usr/local/app|/opt/app|g' deploy/*.conf
                sed -E '/^\\s*(#|$)/d' /etc/nginx/nginx.conf   # strip comments and blank lines
                sed -i '' 's/foo/bar/' file.txt                  # macOS/BSD syntax
            """, runnable=False),
        ],
        ["sed 's/a/b/g' file", "sed -n '10,20p' file", "sed '/^#/d' file", "sed -E 's/(x+)/[\\1]/' file", "sed -i.bak 's/a/b/' file"],
        ["sed -i on a symlink replaces it with a regular file on some versions; use --follow-symlinks.", "GNU and BSD sed differ on -i and some escapes; scripts break when moved to macOS.", "Greedy .* can swallow more than intended; use [^,]* style classes."],
        [
            qa("basic", "How do you replace all occurrences of foo with bar in a file?", "sed 's/foo/bar/g' file prints the result; sed -i 's/foo/bar/g' file edits in place. Without g only the first match on each line changes."),
            qa("intermediate", "How do you print lines 10 to 20?", "sed -n '10,20p' file. -n stops sed from printing every line, and p prints the addressed range."),
            qa("intermediate", "How do you replace a path containing slashes?", "Use another delimiter: sed 's|/usr/local|/opt|g'. Any character after s becomes the delimiter."),
            qa("advanced", "What is the difference between GNU and BSD sed -i?", "GNU sed takes an optional suffix attached to -i (-i or -i.bak). BSD and macOS sed require an argument, so -i '' means no backup; portable scripts write to a temp file and mv it."),
        ],
        ["text-processing", "grep-regex", "awk-reports"],
        chain(
            ("Input", "line by line", "Read", "sed reads one line into the <b>pattern space</b>."),
            ("Address?", "/ERROR/ or 3,5", "Select", "The script's address decides whether the command applies to this line.", "line"),
            ("Command", "s, d, p", "Edit", "s rewrites, d drops the line, p prints it.", "match"),
            ("Output", "stdout or -i", "Write", "The edited line is printed (or written back with -i).", "line"),
        ),
    ),
    topic(
        "awk-reports", "awk: Fields & Reports", "text", "intermediate", "AW",
        "A tiny language for column-oriented text: filter, compute, summarise.",
        "A spreadsheet that works on a stream. Each line is a row, $1, $2... are cells, a pattern is a filter, and the END block is the totals row at the bottom.",
        "awk splits each input line into fields ($1, $2, ... with $0 the whole line) using whitespace or the separator set by -F. A program is a list of pattern { action } pairs: the action runs for lines where the pattern is true, and either part may be omitted. Patterns can be regexes (/ERROR/), comparisons ($4 >= 500) or expressions using built-in variables: NR (record number), NF (field count), FS and OFS (input and output separators). Variables need no declaration and start as 0 or empty, so sum += $5 or count[$1]++ just work. BEGIN runs before input and END after it, which is where totals and averages are printed. awk also has printf, associative arrays and string functions (length, substr, split, tolower), making it ideal for quick log analytics and CSV reports. For quoted CSV with embedded commas, use a real CSV parser.",
        ["Top client IPs and request counts from an access log.", "Summing bytes or durations in a column.", "Filtering rows of a CSV by a field value.", "Reformatting columns for another tool."],
        [
            "awk -F, sets the separator; $NF is the last field.",
            "pattern { action }: both optional; default action prints $0.",
            "NR > 1 skips a header line.",
            "END { print sum } for totals; arrays count[$1]++ for group-by.",
            "Use single quotes around the program so $1 reaches awk.",
        ],
        [
            ex("Pick and filter columns", "basic", "Fields, comparisons and header skipping.", "bash", """
                awk '{print $1, $4}' logs/access.log
                awk -F, '$3 == "Pune" {print $2}' data/users.csv
                awk -F, 'NR > 1 {print $2, $4}' data/users.csv
                awk '$4 >= 400 {print $1, $3, $4}' logs/access.log
            """),
            ex("Totals and counts", "intermediate", "Sum a column, count matches, count lines.", "bash", """
                awk '{s += $5} END {print s}' logs/access.log
                awk '/ERROR/ {n++} END {print n}' logs/app.log
                awk 'END {print NR}' logs/app.log
                awk '{print $1}' logs/access.log | sort | uniq -c | sort -rn
            """),
            ex("Group-by with arrays", "advanced", "Bytes per IP and average latency (full awk).", "bash", """
                awk '{bytes[$1] += $5} END {for (ip in bytes) printf "%-15s %8d\\n", ip, bytes[ip]}' access.log
                awk -F, 'NR > 1 {n[$3]++} END {for (c in n) print c, n[c]}' users.csv
                awk '/slow query/ {gsub(/[()]/, ""); s += $6; c++} END {if (c) print "avg ms:", s / c}' app.log
            """, runnable=False),
        ],
        ["awk '{print $1}' file", "awk -F, '$3 == \"x\"' file", "awk '{s += $5} END {print s}'", "awk 'NR > 1' file", "awk '{c[$1]++} END {for (k in c) print k, c[k]}'"],
        ["Double-quoting the program lets the shell expand $1 to the script's first argument.", "Default FS splits on runs of whitespace; -F' ' and -F'\\t' behave differently.", "Comparisons are numeric only if both sides look numeric; '10' < '9' as strings."],
        [
            qa("basic", "Print the second column of a CSV.", "awk -F, '{print $2}' file.csv. -F sets the field separator; $2 is the second field."),
            qa("intermediate", "What are NR and NF?", "NR is the current record (line) number across all input; NF is the number of fields in the current record, so $NF is the last field."),
            qa("intermediate", "How do you sum a column?", "awk '{s += $5} END {print s}' file. Variables start at 0, the main block accumulates and END prints after all input."),
            qa("advanced", "How do you count requests per IP in awk alone?", "awk '{c[$1]++} END {for (ip in c) print c[ip], ip}' access.log | sort -rn. Associative arrays act like a hash map keyed by the IP."),
        ],
        ["text-processing", "sort-cut-tr", "grep-regex"],
        chain(
            ("Line", "203.0.113.7 GET..", "Read", "awk reads one record."),
            ("Split", "$1 .. $NF", "Fields", "The line is split on FS into numbered fields.", "split"),
            ("Pattern", "$4 >= 400", "Filter", "The pattern is evaluated; false skips the action.", "test"),
            ("Action", "s += $5", "Compute", "The action prints or updates variables and arrays.", "match"),
            ("END", "print s", "Summarise", "After the last line, END prints totals.", "eof"),
        ),
    ),
    topic(
        "sort-cut-tr", "sort, uniq, cut, tr & wc", "text", "basic", "SC",
        "The small tools that slice, order, count and translate text.",
        "Kitchen utensils: cut is the knife that takes one slice, sort lines things up, uniq removes repeats standing next to each other, tr swaps one ingredient for another and wc counts what is on the plate.",
        "These tools each do one thing and compose through pipes. cut -d, -f2,3 selects delimited fields (or -c for character ranges). sort orders lines: -n numeric, -r reverse, -u unique, -k N sort by field N, -t sets the separator and -h understands human sizes like 4K and 2G. uniq collapses adjacent duplicates, so it is almost always preceded by sort; -c prefixes counts, -d shows only duplicates and -u only unique lines. tr translates or deletes characters from stdin (tr a-z A-Z, tr -d '\\r', tr -s ' ' to squeeze spaces) and does not take file arguments. wc counts lines, words and bytes (-l, -w, -c). Together they answer most 'how many of each' questions: cut | sort | uniq -c | sort -rn | head is the classic frequency report.",
        ["Frequency of values in a column.", "Deduplicating a list.", "Converting Windows line endings or case.", "Quick sanity counts on files."],
        [
            "sort | uniq -c | sort -rn: the frequency idiom.",
            "sort -t, -k3 sorts by the third comma-separated field.",
            "sort -n for numbers, -h for human sizes (du -h | sort -h).",
            "tr only reads stdin: tr a-z A-Z < file.",
            "wc -l counts newline characters, so a file without a final newline counts one less.",
        ],
        [
            ex("Sort and deduplicate", "basic", "Order, unique values and counts.", "bash", """
                sort todo.txt
                sort -u todo.txt
                sort todo.txt | uniq -c | sort -rn
                sort todo.txt | uniq -d
            """),
            ex("Cut columns and rank them", "basic", "Which city appears most?", "bash", """
                cut -d, -f2,3 data/users.csv
                cut -d, -f3 data/users.csv | sort | uniq -c | sort -rn
                sort -t, -k3 data/users.csv
                wc -l data/users.csv
            """),
            ex("Translate characters", "intermediate", "Case changes, deletion and counting.", "bash", """
                tr a-z A-Z < notes.txt
                tr -d aeiou < notes.txt
                wc -w notes.txt
                cat notes.txt | wc -c
            """),
        ],
        ["cut -d, -f2 file", "sort -t, -k3 -n file", "sort | uniq -c | sort -rn | head", "tr a-z A-Z < file · tr -d '\\r'", "wc -l · wc -w · wc -c"],
        ["uniq without sort misses duplicates that are not adjacent.", "sort uses the locale; set LC_ALL=C for byte-order, faster and reproducible results.", "cut cannot handle quoted CSV fields containing the delimiter."],
        [
            qa("basic", "Why sort before uniq?", "uniq only compares each line to the previous one, so duplicates must be adjacent. Sorting groups identical lines together."),
            qa("basic", "How do you count lines in a file?", "wc -l file. It counts newline characters, so a last line without a trailing newline is not counted."),
            qa("intermediate", "How do you sort by the third column numerically?", "sort -t, -k3,3n file for comma-separated data, or sort -k3,3n for whitespace-separated. -k3,3 limits the key to just that field."),
            qa("intermediate", "How do you remove Windows carriage returns?", "tr -d '\\r' < in.txt > out.txt (or dos2unix). The \\r characters otherwise break scripts and comparisons."),
        ],
        ["text-processing", "awk-reports", "pipes-redirection"],
        chain(
            ("users.csv", "rows", "Input", "Rows like <b>3,Chen,Pune,dev</b>."),
            ("cut -f3", "city", "Slice", "Keep only the city column.", "rows"),
            ("sort", "group equal", "Order", "Identical cities become adjacent.", "cities"),
            ("uniq -c", "count runs", "Count", "Each run collapses to a count.", "sorted"),
            ("sort -rn", "top first", "Rank", "Highest counts first: <b>4 Pune</b>.", "counts"),
        ),
    ),
    topic(
        "env-path", "Environment Variables & PATH", "text", "basic", "EV",
        "Key=value settings inherited by every child process, and how commands are found.",
        "A briefing packet handed to every new employee. Each process gets a copy of its parent's packet (environment); changing your copy does not change your manager's. PATH is the list of offices to check, in order, when someone asks for a tool by name.",
        "Every process has an environment: a list of NAME=value strings copied from its parent at fork and exec. Shell variables are local until exported; export NAME=value marks them for inheritance, and a child can never change its parent's environment. PATH is a colon-separated list of directories searched left to right for commands without a slash; the first match wins, which hash -r or a new shell refreshes. which and type -a show which file will run. Common variables include HOME, USER, SHELL, LANG/LC_ALL (locale), EDITOR, TZ and TMPDIR. ${VAR:-default} substitutes a default when unset or empty and ${VAR:?msg} fails loudly. VAR=value cmd sets a variable for one command only. Secrets in environment variables are visible to the same user via /proc/<pid>/environ and are easily leaked into logs or crash reports, so prefer files with tight permissions or a secrets manager.",
        ["Adding ~/bin or a tool directory to PATH.", "Configuring an app with DATABASE_URL-style settings.", "Running one command with a different locale or timezone.", "Debugging 'command not found' or the wrong version running."],
        [
            "export makes a variable visible to child processes.",
            "Children inherit a copy; they cannot change the parent.",
            "PATH is searched left to right; the first match wins.",
            "${VAR:-default} for defaults, ${VAR:?error} to require a value.",
            "VAR=x cmd sets VAR only for that command.",
        ],
        [
            ex("Read and set variables", "basic", "Inspect, export, use and remove.", "bash", """
                echo $HOME
                echo $PATH
                env
                export GREETING=hello
                echo "$GREETING, $USER"
                unset GREETING
                echo "greeting is ${GREETING:-unset}"
            """),
            ex("Find commands on PATH", "basic", "Which file runs when you type a name?", "bash", """
                which ls grep
                PROJECT=demo
                echo "project=$PROJECT shell=$SHELL"
                export PATH=$HOME/bin:$PATH
                echo $PATH
            """),
            ex("Inheritance on a real shell", "intermediate", "Local vs exported, one-shot variables and /proc.", "bash", """
                LOCAL=1; export SHARED=2
                bash -c 'echo "local=$LOCAL shared=$SHARED"'    # local= shared=2
                TZ=Asia/Kolkata date
                LC_ALL=C sort big.txt > sorted.txt
                type -a python3
                tr '\\0' '\\n' < /proc/$$/environ | head
            """, runnable=False),
        ],
        ["env · printenv VAR", "export VAR=value", "unset VAR", "echo ${VAR:-default}", "which cmd · type -a cmd"],
        ["Putting . or a world-writable directory early in PATH lets others plant fake commands.", "Changes in a script do not affect your interactive shell unless you source it.", "Secrets in env vars show up in ps e, /proc/<pid>/environ, debug pages and crash dumps."],
        [
            qa("basic", "Shell variable vs environment variable?", "A shell variable exists only in the current shell. After export it becomes part of the environment and is copied into every child process started from that shell."),
            qa("basic", "How does the shell find a command?", "Builtins, aliases and functions are checked first. Otherwise, for a name without a slash, each directory in PATH is searched left to right and the first executable match is run."),
            qa("intermediate", "Why can't a script change its caller's environment?", "The script runs in a child process with a copy of the environment. Changes die with the child; to affect the current shell, source the file instead (. ./env.sh)."),
            qa("intermediate", "How do you give a variable a default?", "${VAR:-default} expands to default when VAR is unset or empty; ${VAR:=default} also assigns it; ${VAR:?message} aborts with an error when it is missing."),
            qa("advanced", "Why are environment variables a weak place for secrets?", "They are inherited by every child, readable by the same user through /proc/<pid>/environ, and commonly dumped by debug tooling and error reporters. Mount secrets as files with mode 600 or fetch them from a secrets manager at runtime."),
        ],
        ["shell-startup-files", "shell-scripting", "processes"],
        chain(
            ("Shell", "export X=1", "Parent", "The shell marks X for export."),
            ("fork()", "copy env", "Fork", "The child receives a copy of the environment.", "env"),
            ("PATH search", "/usr/bin ...", "Lookup", "The command name is searched through each PATH directory in order.", "name"),
            ("execve()", "argv + envp", "Exec", "The program starts with the copied environment; its changes stay private.", "exec"),
        ),
    ),
    topic(
        "shell-startup-files", "Shell Startup Files (.bashrc, .profile)", "text", "intermediate", "SF",
        "Which files bash reads for login, interactive and non-interactive shells.",
        "A hotel check-in. The full check-in (login shell) goes through the lobby desk (/etc/profile, ~/.profile). Walking into your room again later (a new interactive terminal) only reads the note on the door (~/.bashrc). A delivery robot (a script) reads nothing at all.",
        "bash decides what to read by how it was started. A login shell (SSH session, console login, bash -l) reads /etc/profile, then the first of ~/.bash_profile, ~/.bash_login or ~/.profile. An interactive non-login shell (a new terminal tab on most desktops, or running bash) reads /etc/bash.bashrc and ~/.bashrc. Non-interactive shells (scripts, cron, ssh host cmd) read neither, except the file named in BASH_ENV. Convention: put environment variables and PATH changes in ~/.profile (inherited by everything in the session) and aliases, functions and prompt settings in ~/.bashrc, and have ~/.bash_profile source ~/.bashrc. zsh uses ~/.zprofile, ~/.zshrc and ~/.zshenv instead. Changes apply to new shells; source ~/.bashrc reloads the current one. /etc/profile.d/*.sh is the place for system-wide additions from packages.",
        ["Making a PATH change apply to SSH and cron-launched shells consistently.", "Adding aliases and a prompt.", "Debugging 'works in my terminal, not in cron'.", "Shipping a system-wide setting via /etc/profile.d."],
        [
            "Login shell: /etc/profile then ~/.bash_profile or ~/.profile.",
            "Interactive non-login: ~/.bashrc.",
            "Scripts and cron read neither: set what they need explicitly.",
            "Env vars in ~/.profile; aliases and prompt in ~/.bashrc.",
            "source ~/.bashrc applies changes to the current shell.",
        ],
        [
            ex("Look at your dotfiles", "basic", "Hidden files in home and what .bashrc contains.", "bash", """
                ls -la ~
                cat ~/.bashrc
                grep -n alias ~/.bashrc
                echo $SHELL
            """),
            ex("Append a PATH entry safely", "intermediate", "Single quotes keep the variables literal until the shell starts.", "bash", """
                echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
                tail -n 1 ~/.bashrc
                mkdir -p ~/bin
                cat ~/.bashrc
            """),
            ex("Which files ran?", "advanced", "Trace startup on a real system.", "bash", """
                shopt -q login_shell && echo login || echo non-login
                echo $-                                   # contains i when interactive
                bash -lixc exit 2>&1 | grep -E '^\\+* (\\.|source)'
                cat ~/.bash_profile                       # [ -f ~/.bashrc ] && . ~/.bashrc
                ls /etc/profile.d/
            """, runnable=False),
        ],
        ["source ~/.bashrc", "bash -l (login) · bash -i (interactive)", "shopt login_shell", "ls /etc/profile.d", "echo $-"],
        ["If ~/.bash_profile exists, bash ignores ~/.profile entirely for login shells.", "Printing output from .bashrc breaks scp and rsync, which start non-interactive shells that may source it.", "Using double quotes when appending (echo \"export PATH=$PATH\") freezes today's PATH into the file."],
        [
            qa("basic", ".bashrc vs .bash_profile?", ".bash_profile (or .profile) is read by login shells, once per session. .bashrc is read by interactive non-login shells, such as new terminal windows. Most setups source .bashrc from .bash_profile."),
            qa("intermediate", "Why does a command work in my terminal but not in cron?", "cron runs a non-interactive, non-login shell with a minimal environment and a short PATH, so nothing from .bashrc or .profile applies. Use absolute paths or set PATH and other variables in the crontab or script."),
            qa("intermediate", "How do you apply a .bashrc change without logging out?", "source ~/.bashrc (or . ~/.bashrc) runs it in the current shell. Starting a new shell works too."),
            qa("advanced", "Where should a package put a system-wide environment variable?", "In /etc/profile.d/name.sh, which /etc/profile sources for login shells; for non-shell programs, /etc/environment or systemd's environment.d is read by PAM or the session manager."),
        ],
        ["env-path", "shell-scripting", "cron-timers"],
        chain(
            ("SSH login", "login shell", "Start", "An SSH session starts a <b>login</b> shell."),
            ("/etc/profile", "+ profile.d", "System", "System-wide settings and /etc/profile.d/*.sh run first.", "read"),
            ("~/.profile", "env, PATH", "User login", "Your PATH and exported variables are set.", "read"),
            ("~/.bashrc", "aliases, prompt", "Interactive", "Sourced for interactive shells: aliases, functions, PS1.", "source"),
            ("Prompt", "ready", "Ready", "The prompt appears; scripts started later inherit only the exported environment.", "PS1"),
        ),
    ),
    topic(
        "exit-codes-strict-mode", "Exit Codes & set -euo pipefail", "text", "intermediate", "EX",
        "Every command reports success or failure; strict mode makes scripts stop on it.",
        "Each worker on an assembly line raises a green (0) or red (non-zero) flag when done. By default the line keeps running even after a red flag. Strict mode is a supervisor who stops the line at the first red flag, including flags raised in the middle of a pipeline.",
        "Every process exits with a status from 0 to 255: 0 means success and anything else means failure, with meaning defined by the program. The shell stores the last status in $?. Conventions: 1 general error, 2 misuse (grep, bash syntax), 126 found but not executable, 127 command not found, and 128+N killed by signal N, so 130 is Ctrl-C (SIGINT) and 137 is SIGKILL. && runs the next command only on success and || only on failure. In scripts, set -e exits on an unhandled failure, set -u treats unset variables as errors and set -o pipefail makes a pipeline fail if any stage fails, not just the last. set -e has exceptions (commands in if conditions, before && or ||, and in some subshells), so it is a safety net rather than error handling. Combine strict mode with trap '...' ERR or EXIT for cleanup and clear messages, and use exit with meaningful codes in your own scripts.",
        ["Making deploy scripts stop at the first failure.", "Branching on whether grep found something.", "Diagnosing a container exit code like 137 or 143.", "Reporting failure correctly to CI or cron."],
        [
            "0 = success; $? holds the last status.",
            "126 not executable, 127 not found, 128+N killed by signal N.",
            "set -e exit on error, -u unset vars, -o pipefail any stage fails.",
            "set -e is skipped inside if, while, && and || conditions.",
            "Use trap cleanup EXIT for temp files and locks.",
        ],
        [
            ex("Read exit codes", "basic", "Success, failure and a missing file.", "bash", """
                true
                echo "true -> $?"
                false
                echo "false -> $?"
                ls /nope
                echo "ls -> $?"
                grep -q kernel notes.txt
                echo "grep -> $?"
            """),
            ex("Branch on status", "basic", "&& and || react to the previous exit code.", "bash", """
                grep -q timeout logs/app.log && echo "timeouts found"
                grep -q unicorn notes.txt || echo "no match, grep returned 1"
                mkdir -p build && echo "build dir ready"
                set -euo pipefail
            """),
            ex("A strict script with cleanup", "advanced", "The standard header for production bash.", "bash", """
                #!/usr/bin/env bash
                set -euo pipefail
                IFS=$'\\n\\t'
                tmp=$(mktemp -d)
                trap 'rm -rf "$tmp"' EXIT
                trap 'echo "failed at line $LINENO (exit $?)" >&2' ERR
                curl -fsS https://example.com/data.json -o "$tmp/data.json"
                grep -c '"id"' "$tmp/data.json" | tee count.txt
                exit 0
            """, runnable=False),
        ],
        ["echo $?", "cmd && ok || fail", "set -euo pipefail", "trap 'cleanup' EXIT", "exit 3"],
        ["cmd | tee log hides cmd's failure without pipefail.", "local var=$(failing) masks the failure because local itself succeeds; declare first, assign second.", "set -e does not fire inside functions called from an if condition."],
        [
            qa("basic", "What does exit code 127 mean?", "Command not found: the shell searched PATH and found nothing. 126 means the file exists but is not executable."),
            qa("intermediate", "What does set -euo pipefail do?", "-e exits on an unhandled non-zero status, -u makes expanding an unset variable an error and -o pipefail makes a pipeline return the last non-zero status of any stage instead of only the last command's."),
            qa("intermediate", "A container exited with 137. Why?", "137 = 128 + 9, so it received SIGKILL, typically from the OOM killer or a forced stop after a grace period. 143 = 128 + 15 is SIGTERM, a normal graceful stop request."),
            qa("advanced", "When does set -e not stop a script?", "When the failing command is part of an if, while or until condition, is followed by && or ||, is negated with !, or is anything but the last stage of a pipeline without pipefail. Explicit checks remain necessary for critical steps."),
        ],
        ["shell-scripting", "pipes-redirection", "bash-advanced"],
        chain(
            ("Command", "curl -f ...", "Run", "A command runs inside a strict script."),
            ("Exit 22", "HTTP 404", "Status", "curl -f returns 22 because the server answered 404.", "$?"),
            ("set -e", "non-zero", "Detect", "Strict mode sees an unhandled failure.", "fail"),
            ("trap ERR", "log line no.", "Report", "The ERR trap prints the line number to stderr.", "ERR"),
            ("trap EXIT", "cleanup", "Clean up", "The EXIT trap removes temp files; the script exits 22.", "exit"),
        ),
    ),
    topic(
        "bash-advanced", "Bash Arrays, Functions, Traps & Here-docs", "text", "advanced", "BA",
        "Structure larger scripts: arrays, functions, traps, here-docs and process substitution.",
        "Moving from a recipe card to a cookbook. Functions are reusable sub-recipes, arrays are labelled containers of ingredients, traps are the smoke alarm that cleans up when something burns, and here-docs are pre-written notes you pin to a command.",
        "Indexed arrays (arr=(a b c), \"${arr[@]}\", ${#arr[@]}) hold lists without word-splitting surprises, and associative arrays (declare -A m; m[key]=v) give a map. Functions (name() { ...; }) take positional parameters $1, $@ and should use local for their variables; return sets a status, not a value, so output is captured with $(name). trap runs code on signals and pseudo-signals: EXIT for cleanup, ERR on failure, INT/TERM to shut down gracefully. A here-document (<<EOF ... EOF) feeds a block of text to stdin; quoting the delimiter (<<'EOF') disables expansion, and <<-EOF strips leading tabs. Here-strings (<<< \"$var\") pass one string. Process substitution <(cmd) presents a command's output as a file path, so diff <(sort a) <(sort b) compares sorted outputs without temp files, and while read loops fed by < <(cmd) keep variables in the current shell. Always quote expansions, prefer [[ ]] over [ ], and lint with shellcheck.",
        ["Iterating over file names with spaces safely.", "Writing a config file from a template inside a script.", "Graceful shutdown and cleanup in long-running scripts.", "Comparing two command outputs without temp files."],
        [
            "\"${arr[@]}\" expands each element as one word; always quote it.",
            "local inside functions; return is a status code (0-255).",
            "trap 'cleanup' EXIT runs on normal exit, errors and most signals.",
            "<<'EOF' is literal; <<EOF expands variables and $(...).",
            "<(cmd) is a file path backed by a pipe; great with diff and while read.",
        ],
        [
            ex("Arrays and functions", "intermediate", "Safe iteration and a function with locals (real bash).", "bash", """
                files=("my report.txt" "notes.txt")
                echo "count: ${#files[@]}"
                for f in "${files[@]}"; do echo "-> $f"; done
                declare -A port=([web]=80 [ssh]=22)
                for k in "${!port[@]}"; do echo "$k=${port[$k]}"; done
                greet() { local name=${1:-world}; echo "hello $name"; }
                greet; greet Asha
            """, runnable=False),
            ex("Here-docs and here-strings", "intermediate", "Write a file from a template, with and without expansion.", "bash", """
                app=web; port=8080
                cat > app.conf <<EOF
                name=$app
                listen=$port
                EOF
                cat <<'EOF'
                literal: $HOME is not expanded here
                EOF
                tr a-z A-Z <<< "here string"
            """, runnable=False),
            ex("Traps and process substitution", "advanced", "Cleanup, graceful stop and diffing command output.", "bash", """
                tmp=$(mktemp)
                trap 'rm -f "$tmp"; echo cleaned' EXIT
                trap 'echo "stopping"; exit 130' INT TERM
                diff <(sort a.txt) <(sort b.txt)
                while read -r ip count; do echo "$ip $count"; done < <(awk '{print $1}' access.log | sort | uniq -c)
                shellcheck deploy.sh
            """, runnable=False),
        ],
        ["arr=(a b) · \"${arr[@]}\" · ${#arr[@]}", "declare -A map", "f() { local x=$1; }", "trap 'cleanup' EXIT INT TERM", "cat <<'EOF' · diff <(a) <(b)"],
        ["$arr without [@] gives only the first element.", "cmd | while read ...; do count++; done loses count: the loop runs in a subshell. Use < <(cmd).", "Indenting a here-doc body with spaces breaks <<-, which only strips tabs."],
        [
            qa("intermediate", "How do you loop over file names that contain spaces?", "Store them in an array and iterate with for f in \"${files[@]}\", or use find -print0 with while IFS= read -r -d '' f. Unquoted $(ls) splits on spaces and expands globs."),
            qa("intermediate", "How do you return a value from a bash function?", "Print it and capture with result=$(myfunc). return only sets an exit status between 0 and 255."),
            qa("advanced", "What is process substitution?", "<(cmd) runs cmd with its output connected to a pipe and substitutes a path like /dev/fd/63, so tools that need file names can read command output. >(cmd) is the reverse for writing."),
            qa("advanced", "What is the difference between <<EOF and <<'EOF'?", "With an unquoted delimiter the body undergoes parameter, command and arithmetic expansion. Quoting the delimiter passes the body literally, which is safer for templates containing $."),
            qa("advanced", "Why use trap ... EXIT?", "It runs once when the script ends for any reason (success, error under set -e, or a trapped signal), so temporary files, locks and background children are always cleaned up."),
        ],
        ["shell-scripting", "exit-codes-strict-mode", "signals-kill"],
        chain(
            ("main()", "set -euo", "Script", "A strict script calls functions in order."),
            ("Array", "\"${files[@]}\"", "Iterate", "Each element is passed as one argument, spaces intact.", "items"),
            ("Function", "local vars", "Work", "A function processes each file with local variables.", "call"),
            ("Signal", "SIGTERM", "Interrupt", "systemd asks the script to stop.", "TERM"),
            ("trap", "EXIT cleanup", "Clean up", "Traps remove temp files and exit with 143.", "trap"),
        ),
    ),
    topic(
        "signals-kill", "Signals & kill", "system", "intermediate", "SG",
        "Asynchronous notifications to processes: stop, continue, reload or terminate.",
        "Tapping someone on the shoulder with different cards. TERM says 'please wrap up', HUP says 'reread your instructions', STOP freezes them mid-step, and KILL is security escorting them out without a word.",
        "A signal is a small numbered message the kernel delivers to a process. Each has a default action (terminate, ignore, stop or core dump), and processes may install handlers for most of them, except SIGKILL (9) and SIGSTOP (19), which cannot be caught or ignored. kill PID sends SIGTERM (15) by default, asking for a graceful shutdown; kill -9 forces termination without cleanup, flushing or closing connections. SIGINT (2) is Ctrl-C, SIGTSTP is Ctrl-Z, SIGHUP (1) is a terminal hangup and is conventionally used by daemons to reload configuration, SIGCHLD tells a parent its child exited, and SIGUSR1/2 are application-defined. pkill and killall match by name, and kill -0 PID only tests whether the process exists and you may signal it. You may only signal your own processes unless you are root. systemd's stop sends SIGTERM, waits TimeoutStopSec (default 90 s) and then sends SIGKILL; containers follow the same pattern with docker stop and Kubernetes terminationGracePeriodSeconds.",
        ["Stopping a runaway process.", "Reloading nginx configuration without dropping connections.", "Graceful shutdown handling in containers.", "Pausing and resuming a heavy batch job."],
        [
            "kill sends TERM by default; escalate to -9 only if TERM fails.",
            "KILL and STOP cannot be caught, blocked or ignored.",
            "HUP is commonly 'reload config' for daemons.",
            "Exit code 128+N after death by signal N (137 = KILL, 143 = TERM).",
            "kill -0 PID checks existence and permission without sending anything.",
        ],
        [
            ex("Find and stop a runaway", "basic", "Identify the CPU hog, then send TERM.", "bash", """
                kill -l
                top
                ps aux | grep runaway
                kill 1337
                ps aux | grep runaway
            """),
            ex("Permissions and missing processes", "intermediate", "You can only signal your own processes.", "bash", """
                ps aux
                kill 412
                kill -9 99999
                whoami
            """),
            ex("Signals on a real system", "advanced", "Reload, pause, resume and trap.", "bash", """
                sudo kill -HUP "$(cat /run/nginx.pid)"     # reload config
                kill -STOP 4242 && sleep 10 && kill -CONT 4242
                pkill -TERM -f 'python3 worker.py'
                kill -0 4242 && echo alive
                trap 'echo got TERM; exit 0' TERM; sleep 1000 & wait
            """, runnable=False),
        ],
        ["kill PID (TERM) · kill -9 PID", "kill -HUP PID (reload)", "pkill -f pattern · killall name", "kill -STOP / -CONT PID", "kill -l"],
        ["kill -9 skips cleanup: lost buffered writes, stale lock files and orphaned children.", "A shell script as PID 1 in a container ignores TERM unless it traps it, so stops take the full grace period.", "pkill -f matches the whole command line and can hit more processes than intended; preview with pgrep -af."],
        [
            qa("basic", "SIGTERM vs SIGKILL?", "SIGTERM (15) asks the process to exit and can be handled for graceful shutdown. SIGKILL (9) is enforced by the kernel immediately and cannot be caught, so no cleanup happens."),
            qa("intermediate", "Which signals cannot be caught?", "SIGKILL and SIGSTOP. The kernel acts on them directly so an administrator can always terminate or pause a process."),
            qa("intermediate", "Why is SIGHUP used to reload configuration?", "Daemons have no controlling terminal, so the hangup signal would otherwise be unused. By convention they catch it, reread config files and reopen logs without restarting."),
            qa("advanced", "Why does docker stop take 10 seconds for some containers?", "docker stop sends SIGTERM to PID 1 and waits 10 s before SIGKILL. If PID 1 is a shell or app that does not handle TERM (PID 1 gets no default handlers), nothing happens until the KILL. Use exec in entrypoints, an init like tini, or handle TERM."),
        ],
        ["processes", "job-control", "systemd-services"],
        chain(
            ("kill 1337", "SIGTERM", "Send", "You ask the kernel to deliver SIGTERM to PID 1337."),
            ("Kernel", "permission ok", "Check", "Same uid (or root), so the signal is queued.", "TERM"),
            ("Handler?", "trap / default", "Deliver", "The process runs its handler or the default action.", "deliver"),
            ("Exit 143", "128 + 15", "Graceful", "It cleans up and exits; the parent sees status 143.", "exit"),
            ("kill -9", "if stuck", "Force", "Only if it ignores TERM: SIGKILL, no cleanup.", "KILL"),
        ),
    ),
    topic(
        "logs-journald", "Logs: journald, syslog & logrotate", "admin", "intermediate", "LG",
        "Where logs go, how to query them and how to stop them filling the disk.",
        "A building's security desk. journald is the camera system that records everything with timestamps and labels, rsyslog copies selected footage to the classic binders in /var/log, and logrotate boxes up old binders, shrinks them and shreds the oldest.",
        "On systemd distributions, journald collects messages from the kernel, services' stdout and stderr, syslog calls and its own API, storing them in an indexed binary journal with metadata such as unit, PID, priority and boot ID. journalctl queries it: -u unit, -b current boot, -p err priority, --since and --until time ranges, -f follow, -o json for machines. The journal is persistent if /var/log/journal exists, and size is capped with SystemMaxUse in journald.conf. rsyslog (or syslog-ng) often still writes text files such as /var/log/syslog, auth.log or messages and can forward to a central server. Applications that write their own files (nginx access logs, app logs) need logrotate, which runs daily and renames, compresses and deletes old files, then signals the app to reopen (postrotate) or uses copytruncate. Centralise logs off the host (Loki, Elasticsearch, a cloud service), protect them with tight permissions, and never log secrets or tokens.",
        ["Reading why a service failed to start.", "Investigating authentication failures.", "Preventing a disk-full outage from unbounded logs.", "Shipping logs to a central system for search and alerts."],
        [
            "journalctl -u nginx -b -p warning --since '1 hour ago'.",
            "Persistent journal: /var/log/journal; cap with SystemMaxUse.",
            "Text logs in /var/log usually need group adm or root to read.",
            "logrotate: rotate, compress, delaycompress, postrotate reload.",
            "Deleting a log a process holds open frees nothing; reopen or truncate.",
        ],
        [
            ex("Read logs you can access", "basic", "System logs are protected; your app logs are not.", "bash", """
                ls -l /var/log
                cat /var/log/syslog
                tail -n 3 logs/app.log
                grep ERROR logs/app.log | wc -l
                grep -E "WARN|ERROR" logs/app.log | awk '{print $3}' | sort | uniq -c
            """),
            ex("journalctl queries", "intermediate", "Filter by unit, boot, priority and time (real Linux).", "bash", """
                journalctl -u nginx -n 50 --no-pager
                journalctl -b -p err
                journalctl --since "2026-10-17 09:00" --until "2026-10-17 10:00"
                journalctl -u nginx -f
                journalctl -k | tail                    # kernel messages
                journalctl --disk-usage && sudo journalctl --vacuum-size=500M
            """, runnable=False),
            ex("A logrotate policy", "intermediate", "Rotate an app's logs daily, keep two weeks.", "bash", """
                cat /etc/logrotate.d/myapp
                # /var/log/myapp/*.log {
                #     daily
                #     rotate 14
                #     compress
                #     delaycompress
                #     missingok
                #     notifempty
                #     create 0640 myapp adm
                #     postrotate
                #         systemctl reload myapp >/dev/null 2>&1 || true
                #     endscript
                # }
                sudo logrotate -d /etc/logrotate.d/myapp   # dry run
                sudo logrotate -f /etc/logrotate.d/myapp   # force now
            """, runnable=False),
        ],
        ["journalctl -u svc -b -p err", "journalctl -f · --since '10 min ago'", "journalctl --vacuum-size=500M", "logrotate -d /etc/logrotate.d/app", "tail -F /var/log/app.log"],
        ["Without /var/log/journal the journal is volatile and lost on reboot on some distros.", "copytruncate can lose lines written during the copy; prefer reopen via a signal.", "Logging request bodies or headers can leak passwords and tokens into long-lived storage."],
        [
            qa("basic", "How do you see the logs of a systemd service?", "journalctl -u service-name, often with -n 100, -f to follow, -b for the current boot and -p err for errors only."),
            qa("intermediate", "What does logrotate do?", "Run daily from a timer or cron, it renames current log files, compresses old ones, deletes those beyond the retention count and runs hooks so the application reopens its log file."),
            qa("intermediate", "journald vs rsyslog?", "journald stores structured, indexed binary logs with metadata and is queried with journalctl. rsyslog is the traditional daemon writing text files in /var/log and forwarding to remote servers; many systems run both, with journald feeding rsyslog."),
            qa("advanced", "The disk is full of logs and rm did not help. Why?", "The process still has the deleted file open, so its blocks stay allocated. Find it with lsof +L1, then restart or signal the process to reopen logs, or truncate the open file; then fix rotation."),
        ],
        ["systemd-services", "disks-storage", "troubleshooting-slow-server"],
        chain(
            ("Service", "stdout/stderr", "Emit", "nginx writes errors to stderr and access logs to files."),
            ("journald", "indexed journal", "Collect", "stderr, kernel and syslog messages land in the journal with metadata.", "msg"),
            ("journalctl", "-u -p --since", "Query", "Filter by unit, priority, boot and time.", "query"),
            ("logrotate", "daily", "Rotate", "File logs are rotated, compressed and pruned.", "files"),
            ("Central", "Loki / ELK", "Ship", "An agent forwards logs off the host for search and alerting.", "ship"),
        ),
    ),
]

_BATCH_3 = [
    topic(
        "cron-timers", "Scheduling: cron & systemd Timers", "admin", "intermediate", "CR",
        "Run jobs on a schedule with crontab lines or timer units.",
        "An office wall calendar versus a smart assistant. cron is the calendar: a line per recurring task, checked every minute. A systemd timer is the assistant: it also remembers missed appointments while you were away, writes a report of each run and can stop a task that runs too long.",
        "cron reads per-user crontabs (crontab -e, stored under /var/spool/cron) and system files in /etc/crontab and /etc/cron.d, and checks every minute. A line has five time fields (minute, hour, day of month, month, day of week) followed by a command: */15 * * * * runs every 15 minutes and 30 2 * * 1-5 at 02:30 on weekdays. Jobs run with a minimal environment and a short PATH, with no terminal, and output is mailed or lost unless redirected. systemd timers pair a .timer unit with a .service unit: OnCalendar=*-*-* 02:30 for wall-clock schedules, OnBootSec or OnUnitActiveSec for relative ones, Persistent=true to catch up after downtime and RandomizedDelaySec to spread load. Timers log to the journal, inherit unit features like resource limits, sandboxing and dependencies, and are listed with systemctl list-timers. Use flock or the service's own single-instance behaviour to prevent overlapping runs, and always use absolute paths.",
        ["Nightly backups and database dumps.", "Rotating or cleaning temporary data.", "Periodic health checks or report generation.", "Catch-up jobs on laptops or servers that were down."],
        [
            "Cron fields: min hour dom mon dow command.",
            "Cron has a tiny PATH and no profile: use absolute paths and redirect output.",
            "Timers: .timer + .service; OnCalendar, Persistent=true.",
            "systemctl list-timers shows last and next runs.",
            "Prevent overlap with flock -n /run/job.lock cmd.",
        ],
        [
            ex("crontab basics", "basic", "Edit, list and write a safe job line (real Linux).", "bash", """
                crontab -l
                crontab -e
                # m  h  dom mon dow  command
                # */15 *  *   *   *   /usr/local/bin/healthcheck >> /var/log/health.log 2>&1
                # 30  2  *   *   1-5 flock -n /run/backup.lock /usr/local/bin/backup.sh
                ls /etc/cron.d /etc/cron.daily
                grep CRON /var/log/syslog | tail
            """, runnable=False),
            ex("A systemd timer", "intermediate", "Nightly backup that catches up after downtime.", "bash", """
                cat /etc/systemd/system/backup.service
                # [Service]
                # Type=oneshot
                # ExecStart=/usr/local/bin/backup.sh
                cat /etc/systemd/system/backup.timer
                # [Timer]
                # OnCalendar=*-*-* 02:30
                # Persistent=true
                # RandomizedDelaySec=10m
                # [Install]
                # WantedBy=timers.target
                sudo systemctl daemon-reload
                sudo systemctl enable --now backup.timer
                systemctl list-timers
                journalctl -u backup.service -n 20
            """, runnable=False),
            ex("Test schedules", "advanced", "Check what a calendar expression means before trusting it.", "bash", """
                systemd-analyze calendar "Mon..Fri *-*-* 02:30"
                systemd-analyze calendar --iterations=3 "*:0/15"
                sudo systemctl start backup.service      # run once now
            """, runnable=False),
        ],
        ["crontab -e · crontab -l", "*/5 * * * * /abs/path/cmd >> log 2>&1", "systemctl list-timers", "systemd-analyze calendar 'expr'", "flock -n /run/x.lock cmd"],
        ["% in a crontab line is a newline unless escaped as \\%; date +%F breaks silently.", "A job that works in your shell fails in cron because PATH and variables differ.", "Overlapping runs of slow jobs pile up; add flock or use a timer with a oneshot service."],
        [
            qa("basic", "What does 0 3 * * 0 mean in cron?", "At minute 0 of hour 3 on any day of the month, any month, on day-of-week 0 (Sunday): every Sunday at 03:00."),
            qa("intermediate", "Why does my cron job fail but the script works manually?", "cron uses a minimal environment: short PATH, no .bashrc or .profile, different working directory and no terminal. Use absolute paths, set needed variables and redirect output to a log to see the error."),
            qa("intermediate", "Advantages of systemd timers over cron?", "Runs are logged in the journal with exit status, Persistent=true catches up missed runs, randomised delays spread load, and the service gets systemd features such as dependencies, resource limits and sandboxing."),
            qa("advanced", "How do you stop a job from running twice at once?", "Wrap it with flock -n /run/job.lock so a second instance exits immediately, or use a systemd timer: a oneshot service will not start again while the previous run is still active."),
        ],
        ["systemd-services", "shell-scripting", "shell-startup-files"],
        chain(
            ("backup.timer", "OnCalendar 02:30", "Schedule", "systemd computes the next elapse time."),
            ("Elapse", "02:30 + delay", "Trigger", "At the time (plus a random delay) the timer fires.", "tick"),
            ("backup.service", "oneshot", "Run", "The paired service runs the script with its own limits.", "start"),
            ("Journal", "exit status", "Record", "Output and exit code are logged; list-timers shows LAST and NEXT.", "log"),
        ),
    ),
    topic(
        "time-ntp", "Time, Timezones & NTP (chrony)", "admin", "basic", "TM",
        "Keep clocks correct and comparable across machines.",
        "An orchestra needs one tuning fork. NTP servers are the tuning fork, chrony is each musician listening and gently adjusting, and timezones are only how the score is printed for each country: the underlying beat (UTC) is the same.",
        "The kernel keeps time as UTC seconds since the epoch; timezones are a presentation layer from the tz database (/usr/share/zoneinfo) selected by /etc/localtime or the TZ variable. timedatectl shows and sets the timezone and whether NTP synchronisation is active. chrony (chronyd) is the default NTP client on most modern distributions; it disciplines the clock by slewing (gradual speed adjustment) rather than jumping, and can step on boot if the offset is large. systemd-timesyncd is a lighter SNTP client. Accurate time matters far beyond log readability: TLS certificate validation, Kerberos, TOTP codes, distributed databases, and correlating logs across hosts all fail or mislead when clocks drift. Servers should log in UTC, use several NTP sources or a cloud provider's local time service, and alert on large offsets. date formats time, uptime reports how long since boot, and hwclock reads the battery-backed RTC.",
        ["Correlating logs from several servers during an incident.", "Fixing TLS errors caused by a wrong clock.", "Setting the timezone on a new server.", "Monitoring clock offset in a cluster."],
        [
            "Kernel time is UTC; timezones only change display.",
            "timedatectl: timezone, NTP status, RTC.",
            "chronyc tracking / sources: offset and peers.",
            "Slew small offsets, step only at boot or deliberately.",
            "Log in UTC with ISO 8601 timestamps.",
        ],
        [
            ex("Look at the clock", "basic", "Date, uptime and time-stamped log lines.", "bash", """
                date
                uptime
                grep "09:02" logs/app.log
                head -n 1 logs/app.log
            """),
            ex("Timezone and NTP status", "intermediate", "timedatectl and chrony on a real server.", "bash", """
                timedatectl
                sudo timedatectl set-timezone UTC
                chronyc tracking
                chronyc sources -v
                date -u +%Y-%m-%dT%H:%M:%SZ
                TZ=Asia/Kolkata date
            """, runnable=False),
            ex("Configure chrony", "advanced", "Pool servers and a step at boot.", "bash", """
                grep -E '^(pool|server|makestep)' /etc/chrony/chrony.conf
                # pool 2.pool.ntp.org iburst
                # makestep 1.0 3
                sudo systemctl restart chronyd
                chronyc makestep          # force a step now (use with care)
            """, runnable=False),
        ],
        ["date · date -u", "timedatectl · set-timezone UTC", "chronyc tracking · chronyc sources", "TZ=Region/City date", "hwclock --show"],
        ["Stepping the clock backwards confuses software that assumes monotonic wall time.", "Containers share the host kernel clock; you cannot fix time inside one container.", "Daylight saving makes local-time cron jobs run twice or not at all on change days."],
        [
            qa("basic", "Why should servers use UTC?", "UTC has no daylight saving jumps and is the same everywhere, so logs from different regions line up and scheduled jobs run predictably."),
            qa("intermediate", "What does chrony do?", "It queries NTP servers, estimates the local clock's offset and drift and adjusts the clock smoothly by slewing, stepping only when allowed (for example at boot)."),
            qa("intermediate", "How can a wrong clock break TLS?", "Certificate validation compares the current time with notBefore and notAfter. A clock far in the past or future makes valid certificates appear not yet valid or expired."),
            qa("advanced", "Slewing vs stepping?", "Slewing speeds up or slows the clock slightly until the offset disappears, keeping time monotonic. Stepping jumps the clock immediately, which is fast but can make timestamps go backwards."),
        ],
        ["logs-journald", "tls-openssl", "cron-timers"],
        chain(
            ("NTP pool", "stratum 2", "Sources", "chrony queries several NTP servers."),
            ("chronyd", "offset, drift", "Estimate", "It measures round-trip delay and offset for each source.", "NTP"),
            ("Kernel clock", "slew", "Adjust", "The kernel clock is sped up or slowed down slightly.", "adjtime"),
            ("Apps", "UTC + TZ", "Use", "Logs, TLS and tokens rely on the corrected clock.", "time"),
        ),
    ),
    topic(
        "ssh-keys", "SSH: Keys, Config & Tunnels", "remote", "intermediate", "SK",
        "Encrypted remote shells with ed25519 keys, a tidy ~/.ssh/config and port forwarding.",
        "A key-card building. Your private key is the card that never leaves your pocket, authorized_keys is the reception list of card IDs allowed in, ~/.ssh/config is your address book of buildings, and a tunnel is a private corridor through the building to a room you could not reach from the street.",
        "SSH gives encrypted, authenticated remote shells, commands and file transfer. Key authentication is preferred over passwords: ssh-keygen -t ed25519 creates a private key (protect it with a passphrase) and a .pub public key, which goes into ~/.ssh/authorized_keys on the server (ssh-copy-id does this). Permissions matter: ~/.ssh should be 700 and private keys 600, or ssh refuses them. ssh-agent holds decrypted keys in memory so you type the passphrase once; forward the agent only to hosts you trust, and prefer ProxyJump for bastions. ~/.ssh/config defines aliases with HostName, User, Port, IdentityFile and ProxyJump. Tunnels: -L 5432:db:5432 forwards a local port to a remote target, -R exposes a local service on the remote side and -D 1080 creates a SOCKS proxy. On the server, harden sshd_config: PasswordAuthentication no, PermitRootLogin no, and keep OpenSSH updated so modern key exchange (including hybrid post-quantum sntrup761x25519 or mlkem768x25519) is negotiated. Verify host key fingerprints on first connect; they protect against man-in-the-middle attacks.",
        ["Passwordless, secure logins to servers.", "Reaching a private database through a bastion.", "Running remote commands from scripts and CI.", "Exposing a local dev server to a remote machine temporarily."],
        [
            "ssh-keygen -t ed25519 -C 'you@laptop'; protect the key with a passphrase.",
            "~/.ssh 700, private key 600, authorized_keys 600.",
            "ProxyJump bastion instead of agent forwarding where possible.",
            "-L local forward, -R remote forward, -D SOCKS proxy.",
            "Server: PasswordAuthentication no, PermitRootLogin no.",
        ],
        [
            ex("Fix key permissions", "basic", "SSH refuses keys other users can read.", "bash", """
                ls -la ~/.ssh
                chmod 700 ~/.ssh
                chmod 600 ~/.ssh/id_demo
                ls -la ~/.ssh
                stat ~/.ssh/id_demo
            """),
            ex("Create and install an ed25519 key", "basic", "Generate, copy to a server, log in (real Linux).", "bash", """
                ssh-keygen -t ed25519 -C "learner@laptop" -f ~/.ssh/id_ed25519
                ssh-copy-id -i ~/.ssh/id_ed25519.pub deploy@203.0.113.10
                ssh -i ~/.ssh/id_ed25519 deploy@203.0.113.10
                eval "$(ssh-agent -s)" && ssh-add ~/.ssh/id_ed25519
                ssh-keygen -lf ~/.ssh/id_ed25519.pub     # SHA256 fingerprint
            """, runnable=False),
            ex("~/.ssh/config and tunnels", "intermediate", "Aliases, a bastion and port forwarding.", "bash", """
                cat ~/.ssh/config
                # Host bastion
                #     HostName 203.0.113.10
                #     User deploy
                #     IdentityFile ~/.ssh/id_ed25519
                # Host db-private
                #     HostName 10.0.0.5
                #     User deploy
                #     ProxyJump bastion
                ssh db-private
                ssh -N -L 5432:10.0.0.5:5432 bastion     # psql -h localhost now reaches the private DB
                ssh -N -R 8080:localhost:3000 bastion    # bastion:8080 -> your laptop:3000
                ssh -N -D 1080 bastion                   # SOCKS proxy
            """, runnable=False),
            ex("Harden the server", "advanced", "sshd settings and a config test.", "bash", """
                sudo grep -E '^(PasswordAuthentication|PermitRootLogin|PubkeyAuthentication)' /etc/ssh/sshd_config
                # PasswordAuthentication no
                # PermitRootLogin no
                # PubkeyAuthentication yes
                sudo sshd -t && sudo systemctl reload ssh
                ssh -Q kex | grep -E 'mlkem|sntrup'      # post-quantum hybrid KEX available?
            """, runnable=False),
        ],
        ["ssh-keygen -t ed25519", "ssh-copy-id user@host", "ssh -J bastion target", "ssh -L 8080:internal:80 host", "sshd -t && systemctl reload ssh"],
        ["Never share or commit a private key; if one leaks, remove its line from every authorized_keys.", "Agent forwarding (-A) lets root on the remote host use your keys while you are connected.", "Blindly accepting a changed host key defeats SSH's protection against man-in-the-middle attacks.", "Leave the current session open while changing sshd_config so a mistake cannot lock you out."],
        [
            qa("basic", "How does SSH key authentication work?", "The server has your public key in authorized_keys. During login it sends a challenge that only the matching private key can sign; the private key never leaves your machine."),
            qa("intermediate", "Why ed25519 over RSA?", "Ed25519 keys are small, fast, have no weak parameter choices and resist several implementation pitfalls. If RSA is required for compatibility, use at least 3072 bits."),
            qa("intermediate", "What does ssh -L 5432:db:5432 bastion do?", "It listens on local port 5432 and forwards each connection through the encrypted SSH session to bastion, which connects to db:5432. Clients connect to localhost:5432."),
            qa("advanced", "ProxyJump vs agent forwarding?", "ProxyJump makes the bastion relay a TCP stream while authentication to the final host happens end-to-end from your machine. Agent forwarding exposes your agent socket on the bastion, where a root user could use your keys."),
            qa("advanced", "How do you harden sshd?", "Disable password and root login, allow only key authentication, restrict users with AllowUsers or AllowGroups, keep OpenSSH updated for modern ciphers and hybrid post-quantum key exchange, limit exposure with a firewall or VPN, and validate with sshd -t before reloading."),
        ],
        ["networking", "scp-rsync", "firewall"],
        chain(
            ("Client", "id_ed25519", "Connect", "ssh connects to the server on port 22."),
            ("Key exchange", "hybrid PQ KEX", "Encrypt", "Both sides agree on session keys; you verify the host key fingerprint.", "KEX"),
            ("Challenge", "sign with key", "Authenticate", "The server asks for a signature only your private key can make.", "sig"),
            ("Server check", "authorized_keys", "Verify", "The signature is checked against your public key.", "pubkey"),
            ("Shell / tunnel", "-L -R -D", "Session", "You get a shell, or forwarded ports through the encrypted channel.", "chan"),
        ),
    ),
    topic(
        "scp-rsync", "Copying Over the Network: scp & rsync", "remote", "intermediate", "RS",
        "Move files between hosts securely, and only send what changed.",
        "scp is a courier who carries the whole parcel every time. rsync is a courier who first phones ahead, asks which pages the recipient already has, and only carries the changed pages.",
        "scp copies files over SSH with a cp-like syntax (scp file host:/path, scp -r dir host:), and modern OpenSSH implements it on the SFTP protocol. rsync also runs over SSH but compares source and destination first, using size and modification time (or checksums with -c) and a rolling-checksum delta algorithm to transfer only changed blocks, which makes repeated syncs fast and resumable. -a (archive) preserves permissions, times, symlinks and ownership; -v and --progress show work; -z compresses in transit; --delete removes files at the destination that no longer exist at the source; -n (dry run) shows what would happen. A trailing slash on the source matters: rsync -a src/ dest copies the contents of src, while rsync -a src dest creates dest/src. Add -AX to keep ACLs and extended attributes and --link-dest for space-efficient snapshot backups. For interactive browsing, sftp offers a file-manager style session.",
        ["Deploying a build directory to servers.", "Nightly backups to another host.", "Migrating data between servers with minimal downtime.", "Grabbing a log file from a remote machine."],
        [
            "rsync -avz src/ host:/dest/ sends only differences.",
            "Trailing slash on the source copies contents, not the directory.",
            "Always try --delete with -n (dry run) first.",
            "-a preserves perms, times and links; add -AX for ACLs and xattrs.",
            "scp is fine for one-off copies; rsync for anything repeated or large.",
        ],
        [
            ex("The local idea rsync automates", "basic", "Copy a tree, change the source, see the difference.", "bash", """
                mkdir -p backup
                cp -r logs backup/
                cp notes.txt backup/
                tree backup
                echo "Kernels schedule processes." >> notes.txt
                diff notes.txt backup/notes.txt
            """),
            ex("scp and rsync", "intermediate", "One-off copies and incremental syncs (real Linux).", "bash", """
                scp app.tgz deploy@web1:/tmp/
                scp -r deploy@web1:/var/log/nginx ./web1-logs
                rsync -avz --progress ./dist/ deploy@web1:/srv/app/
                rsync -avzn --delete ./dist/ deploy@web1:/srv/app/   # dry run
                rsync -avz --delete ./dist/ deploy@web1:/srv/app/
            """, runnable=False),
            ex("Snapshot backups with hard links", "advanced", "Each day looks complete but unchanged files share inodes.", "bash", """
                today=$(date +%F)
                rsync -aAX --delete --link-dest=/backups/latest /srv/data/ /backups/$today/
                ln -sfn /backups/$today /backups/latest
                du -sh /backups/*          # later snapshots are small
            """, runnable=False),
        ],
        ["scp file user@host:/path", "rsync -avz src/ host:/dest/", "rsync -avzn --delete src/ dest/", "rsync -aAX --link-dest=prev src/ snap/", "sftp user@host"],
        ["rsync -a src dest vs src/ dest: one creates dest/src, the other merges contents.", "--delete with the wrong destination path deletes real data; dry-run first.", "rsync between hosts needs rsync installed on both ends."],
        [
            qa("basic", "scp vs rsync?", "Both copy over SSH. scp always transfers whole files; rsync compares source and destination and sends only what changed, supports resumable transfers, deletion and dry runs."),
            qa("intermediate", "What does the trailing slash do in rsync?", "rsync -a src/ dest copies the contents of src into dest. Without the slash, rsync -a src dest creates dest/src."),
            qa("intermediate", "How does rsync decide what to send?", "By default it skips files whose size and modification time match. For changed files it uses a rolling checksum to find matching blocks and sends only the differing parts; -c forces full checksum comparison."),
            qa("advanced", "How do you build space-efficient daily backups with rsync?", "Use --link-dest pointing at the previous snapshot. Unchanged files become hard links to the previous copy, so each snapshot is a full tree while only changed files use new space."),
        ],
        ["ssh-keys", "archives-compression", "links-hard-soft"],
        chain(
            ("Source", "dist/", "Scan", "rsync lists files with sizes and mtimes."),
            ("Compare", "size + mtime", "Diff", "The receiver reports what it already has.", "file list"),
            ("Delta", "rolling checksum", "Blocks", "For changed files only differing blocks are computed.", "sums"),
            ("SSH", "encrypted", "Transfer", "Deltas travel over an SSH channel, optionally compressed.", "delta"),
            ("Dest", "/srv/app/", "Apply", "Files are rebuilt and renamed into place atomically.", "write"),
        ),
    ),
    topic(
        "networking-tools", "Network Troubleshooting Tools", "remote", "intermediate", "NT",
        "ip, ss, ping, dig, curl and tcpdump: test each layer in turn.",
        "Diagnosing a dead phone line by walking outward: is the phone plugged in (ip link), does it have a number (ip addr), can it reach the exchange (ip route, ping), does the directory know the name (dig), does the person answer (ss, curl), and what is actually said on the wire (tcpdump).",
        "Troubleshoot networks layer by layer. ip link and ip addr show interfaces, state and addresses; ip route shows the routing table and ip route get 1.1.1.1 shows which route and source address a packet would use. ping tests ICMP reachability and latency (but many hosts block ICMP), and mtr or tracepath show the path hop by hop. ss -tlnp lists listening TCP sockets with owning processes, and ss -tn state established shows live connections. dig queries DNS directly, bypassing caches, and curl -v shows connection, TLS and HTTP stages, with -w timing variables to see where time goes. nc -zv host port tests a TCP port quickly. tcpdump -i eth0 -nn port 443 captures packets for deep inspection, and the capture can be opened in Wireshark. Older net-tools commands (ifconfig, netstat, route) are deprecated in favour of iproute2.",
        ["'The site is down': find which layer is broken.", "Checking which process listens on a port.", "Measuring DNS, TCP, TLS and server time for a request.", "Capturing traffic to prove where packets are lost."],
        [
            "Work bottom-up: link, address, route, DNS, port, application.",
            "ss -tlnp: listening TCP sockets with processes.",
            "curl -v and -w timings break down connect, TLS and first byte.",
            "ping failure is not proof of an outage; ICMP may be filtered.",
            "tcpdump -nn avoids slow reverse DNS while capturing.",
        ],
        [
            ex("Reachability and HTTP", "basic", "Simulated hosts, DNS and the local web server.", "bash", """
                cat /etc/hosts
                ping -c 2 localhost
                ping -c 1 10.0.0.99
                dig db.internal
                curl -I http://localhost
                curl http://localhost
            """),
            ex("Layer by layer on a real host", "intermediate", "Interfaces, routes, sockets and timing.", "bash", """
                ip -br link
                ip -br addr
                ip route get 1.1.1.1
                ss -tlnp
                ss -tn state established '( dport = :443 )'
                nc -zv db.internal 5432
                curl -s -o /dev/null -w 'dns=%{time_namelookup} connect=%{time_connect} tls=%{time_appconnect} ttfb=%{time_starttransfer}\\n' https://example.com
                mtr -rwc 20 example.com
            """, runnable=False),
            ex("Capture packets", "advanced", "See what really crosses the wire.", "bash", """
                sudo tcpdump -i eth0 -nn port 5432 -c 20
                sudo tcpdump -i any -nn 'tcp[tcpflags] & tcp-syn != 0 and port 443'
                sudo tcpdump -i eth0 -w /tmp/web.pcap port 80   # open in Wireshark
            """, runnable=False),
        ],
        ["ip -br addr · ip route get IP", "ss -tlnp · ss -tn", "ping -c 3 host · mtr host", "curl -v · curl -w '%{time_connect}'", "tcpdump -i eth0 -nn port 443"],
        ["A service listening on 127.0.0.1 is unreachable from other hosts even if the firewall is open.", "tcpdump on a busy interface without filters can drop packets and fill the disk.", "Cloud security groups block traffic before it reaches the host, so host tools see nothing."],
        [
            qa("basic", "How do you see which process is listening on port 80?", "sudo ss -tlnp | grep ':80' (or lsof -i :80). -t TCP, -l listening, -n numeric, -p process."),
            qa("intermediate", "Ping works but curl to port 443 hangs. What next?", "ICMP reachability is fine, so check the TCP port: nc -zv host 443 or curl -v to see whether the connect or TLS stage hangs. Then check ss on the server, host firewall rules and cloud security groups."),
            qa("intermediate", "How do you break down where an HTTP request spends time?", "curl -w with time_namelookup, time_connect, time_appconnect and time_starttransfer shows DNS, TCP connect, TLS handshake and server time to first byte."),
            qa("advanced", "When would you use tcpdump?", "When higher-level tools disagree or you need proof: to see whether SYNs arrive, whether replies leave, retransmissions, resets or unexpected source addresses. Filter narrowly by host and port and write to a pcap for Wireshark."),
        ],
        ["networking", "dns-resolution", "firewall"],
        chain(
            ("ip link/addr", "interface up?", "Link", "Is the interface up with the right address?"),
            ("ip route", "gateway", "Route", "Is there a route and the expected source IP?", "route"),
            ("dig", "name -> IP", "DNS", "Does the name resolve to the right address?", "DNS"),
            ("nc / ss", "port open?", "Transport", "Does the TCP port accept connections, and who listens?", "SYN"),
            ("curl -v", "TLS + HTTP", "Application", "Does the app answer correctly, and how fast?", "GET"),
            ("tcpdump", "packets", "Proof", "Capture to see exactly what crosses the wire.", "pcap"),
        ),
    ),
    topic(
        "dns-resolution", "Name Resolution: hosts, resolv.conf, nsswitch", "remote", "intermediate", "DN",
        "How a hostname becomes an IP on a Linux box.",
        "Looking up a phone number. First your own sticky note on the fridge (/etc/hosts), then the family address book cache (systemd-resolved), then the operator (the DNS server in resolv.conf). nsswitch.conf is the house rule saying in which order to check them.",
        "Programs usually resolve names through the C library's getaddrinfo, which follows /etc/nsswitch.conf: a line like hosts: files dns means check /etc/hosts first, then DNS. /etc/hosts maps names to addresses statically and wins over DNS when listed first, which is handy for testing and dangerous when forgotten. DNS settings live in /etc/resolv.conf (nameserver, search domains, options ndots and timeout); on systemd systems it often points at the local stub 127.0.0.53 managed by systemd-resolved, inspected with resolvectl status. getent hosts name follows exactly the same path as applications, while dig and nslookup query DNS servers directly and ignore /etc/hosts and nsswitch. Search domains append suffixes to short names, and ndots (5 in Kubernetes) controls when that happens, which can multiply lookups. Caching happens in systemd-resolved, nscd or the application itself (the JVM caches successful lookups), so record changes can take a TTL or a restart to appear.",
        ["Debugging 'works with dig but the app cannot resolve it'.", "Temporarily pointing a name at a test server.", "Understanding slow lookups in Kubernetes pods.", "Configuring internal search domains."],
        [
            "nsswitch.conf decides the order: files (hosts) then dns.",
            "getent hosts name = what apps see; dig = what DNS says.",
            "127.0.0.53 in resolv.conf means systemd-resolved is the stub.",
            "Search domains + ndots can turn one lookup into several.",
            "TTLs and app-level caches delay the effect of DNS changes.",
        ],
        [
            ex("Static entries and DNS", "basic", "Compare /etc/hosts with a DNS query.", "bash", """
                cat /etc/hosts
                grep db.internal /etc/hosts
                dig db.internal
                dig example.com +short
                ping -c 1 db.internal
            """),
            ex("The resolver path on a real system", "intermediate", "What applications actually use.", "bash", """
                grep '^hosts:' /etc/nsswitch.conf      # hosts: files dns
                cat /etc/resolv.conf
                resolvectl status
                getent hosts db.internal
                dig @1.1.1.1 example.com A +short
                dig example.com +trace
            """, runnable=False),
            ex("Caches and Kubernetes ndots", "advanced", "Why a lookup is slow or stale.", "bash", """
                resolvectl statistics
                sudo resolvectl flush-caches
                cat /etc/resolv.conf     # inside a pod: search ns.svc.cluster.local ... options ndots:5
                dig +search api.example.com
                getent ahosts api.example.com.       # trailing dot skips search domains
            """, runnable=False),
        ],
        ["getent hosts name", "dig name · dig @server name", "cat /etc/resolv.conf", "resolvectl status · flush-caches", "grep hosts /etc/nsswitch.conf"],
        ["A stale /etc/hosts entry silently overrides DNS for that host.", "Editing /etc/resolv.conf by hand is overwritten when it is managed by systemd-resolved or NetworkManager.", "dig succeeding does not prove the app can resolve: it bypasses nsswitch and /etc/hosts."],
        [
            qa("basic", "What is /etc/hosts for?", "Static name to IP mappings checked before DNS (when nsswitch lists files first). Useful for local overrides and tests, but easy to forget."),
            qa("intermediate", "Why might dig resolve a name but curl fails?", "dig queries a DNS server directly. curl uses getaddrinfo, which follows nsswitch.conf and may hit /etc/hosts, a different search domain or a local cache. Compare with getent hosts name."),
            qa("intermediate", "What does nameserver 127.0.0.53 mean?", "The system uses systemd-resolved as a local caching stub resolver; the real upstream servers are shown by resolvectl status."),
            qa("advanced", "Why are DNS lookups slow in Kubernetes pods?", "Pods use ndots:5 with several search domains, so a name with fewer than five dots is tried with each suffix first, causing multiple failed queries. Use fully qualified names with a trailing dot or lower ndots."),
        ],
        ["networking", "networking-tools", "users-groups"],
        chain(
            ("App", "getaddrinfo()", "Ask", "curl asks libc to resolve db.internal."),
            ("nsswitch", "files dns", "Order", "nsswitch.conf says: check files first, then DNS.", "lookup"),
            ("/etc/hosts", "10.0.0.5", "Files", "A static match ends the lookup here.", "files"),
            ("resolved", "127.0.0.53", "Cache", "Otherwise the local stub answers from cache or forwards.", "dns"),
            ("DNS server", "A record, TTL", "Upstream", "The upstream server answers; the result is cached for its TTL.", "query"),
        ),
    ),
    topic(
        "firewall", "Firewalls: nftables, iptables & ufw", "remote", "advanced", "FW",
        "Filter packets in the kernel with default-deny rules.",
        "A building's front desk with a rule book. Each visitor (packet) is checked against the rules top to bottom: known regulars (established connections) walk in, deliveries to the loading dock (port 443) are allowed, and everyone else is turned away by default.",
        "Linux filters packets in the kernel with netfilter. nftables (nft) is the modern interface, replacing iptables, ip6tables and ebtables with one syntax and atomic rule set loading; on many distributions the iptables command is now a compatibility layer over nftables. Rules live in tables and chains attached to hooks: input (to this host), forward (routed through) and output (from this host), plus prerouting and postrouting for NAT. Connection tracking lets you write stateful rules: accept ct state established,related first, then allow specific new connections, then drop everything else (policy drop). Front ends simplify common cases: ufw on Ubuntu (ufw default deny incoming; ufw allow from 203.0.113.0/24 to any port 22) and firewalld on RHEL with zones. Restrict administrative ports such as SSH and databases to known source ranges rather than the whole internet, and remember cloud security groups and Kubernetes network policies are separate layers. Always keep a way back in before applying a default-deny policy remotely.",
        ["Allowing only HTTP/HTTPS publicly and SSH from an office range.", "Blocking an abusive IP quickly.", "NAT for containers or a home router.", "Auditing what a server actually exposes."],
        [
            "Default deny inbound; allow established,related; then explicit allows.",
            "nft list ruleset shows everything; load atomically from a file.",
            "Never open SSH or database ports to 0.0.0.0/0; restrict source CIDRs.",
            "ufw and firewalld are front ends over netfilter.",
            "Host firewall, cloud security groups and k8s policies are separate layers.",
        ],
        [
            ex("ufw on Ubuntu", "basic", "Default deny with a restricted SSH rule.", "bash", """
                sudo ufw default deny incoming
                sudo ufw default allow outgoing
                sudo ufw allow from 203.0.113.0/24 to any port 22 proto tcp
                sudo ufw allow 443/tcp
                sudo ufw enable
                sudo ufw status numbered
            """, runnable=False),
            ex("An nftables rule set", "advanced", "Stateful, default-drop input chain loaded atomically.", "bash", """
                cat /etc/nftables.conf
                # table inet filter {
                #   chain input {
                #     type filter hook input priority 0; policy drop;
                #     ct state established,related accept
                #     iif lo accept
                #     ip saddr 203.0.113.0/24 tcp dport 22 accept
                #     tcp dport { 80, 443 } accept
                #     icmp type echo-request limit rate 5/second accept
                #   }
                # }
                sudo nft -c -f /etc/nftables.conf      # check syntax
                sudo nft -f /etc/nftables.conf
                sudo nft list ruleset
            """, runnable=False),
            ex("Inspect and block", "intermediate", "What is open, and a quick block.", "bash", """
                sudo ss -tlnp
                sudo iptables -S                       # legacy view (may be nft-backed)
                sudo nft add rule inet filter input ip saddr 198.51.100.23 drop
                sudo firewall-cmd --list-all           # RHEL firewalld
            """, runnable=False),
        ],
        ["nft list ruleset", "nft -c -f file · nft -f file", "ufw status numbered", "ufw allow from CIDR to any port 22", "firewall-cmd --list-all"],
        ["Enabling a default-deny policy over SSH without an allow rule for your session locks you out.", "Docker inserts its own NAT and forward rules, so published container ports can bypass ufw.", "Mixing iptables-legacy and nftables rules leads to confusing, partly ignored policies."],
        [
            qa("intermediate", "What does a stateful firewall rule like ct state established,related accept do?", "It accepts packets belonging to connections already allowed (replies and related flows such as ICMP errors), so you only need rules for new connections and can drop everything else."),
            qa("intermediate", "iptables vs nftables?", "nftables is the successor: one tool for IPv4, IPv6 and bridging, sets and maps, and atomic rule set replacement. iptables remains available, often as a compatibility frontend that writes nftables rules."),
            qa("advanced", "Why might a Docker-published port be reachable despite ufw deny?", "Docker adds NAT and forward rules that handle the traffic before ufw's input rules see it. Bind published ports to 127.0.0.1, use the DOCKER-USER chain, or put a firewall in front."),
            qa("advanced", "How do you safely apply a firewall change on a remote server?", "Validate syntax (nft -c), keep an existing SSH session open, schedule an automatic rollback (for example a timer that restores the old rules in 5 minutes), apply, test a new connection, then cancel the rollback."),
        ],
        ["networking", "networking-tools", "ssh-keys"],
        chain(
            ("Packet", "SYN to :22", "Arrive", "A new TCP connection arrives on eth0."),
            ("conntrack", "new flow", "Track", "Connection tracking marks it as <b>new</b>.", "SYN"),
            ("input chain", "rules in order", "Match", "Rules are evaluated top to bottom.", "check"),
            ("Source ok?", "203.0.113.0/24", "Decide", "Source is in the admin range: accept.", "match"),
            ("Policy drop", "everything else", "Default", "Anything not matched is dropped silently.", "drop"),
        ),
    ),
    topic(
        "tls-openssl", "TLS Certificates & openssl Inspection", "security", "advanced", "TL",
        "Read, verify and troubleshoot X.509 certificates and TLS connections.",
        "A passport check. The certificate is the passport (name, photo = public key, expiry date), the issuing CA is the government that signed it, and the chain is the stamp trail back to a government you already trust. You check the dates, the name, the security features and whether it was self-printed.",
        "TLS authenticates servers with X.509 certificates: a public key plus subject names (the SAN list), validity dates, an issuer and a signature from that issuer. Clients build a chain from the leaf through intermediates to a trusted root in the system store (/etc/ssl/certs or /etc/pki/tls) and check names, dates and revocation. openssl x509 -text -noout -in cert.pem decodes a certificate; review notAfter and notBefore (expired or not-yet-valid certificates break connections), the public key (RSA at least 2048 bits, or EC on P-256 or stronger), the signature algorithm (SHA-2 such as sha256WithRSAEncryption or ecdsa-with-SHA256, never MD5 or SHA-1) and whether Issuer equals Subject (self-signed, acceptable only for development or explicitly configured internal trust). openssl s_client -connect host:443 -servername host shows the served chain and the negotiated protocol and cipher; servers should prefer TLS 1.3 with AEAD suites like TLS_AES_256_GCM_SHA384 and disable TLS 1.0/1.1. Never paste private keys into tickets or repos: keep them mode 600, ideally in a KMS or HSM, and automate renewal (ACME, cert-manager) and expiry monitoring.",
        ["Diagnosing 'certificate has expired' or hostname mismatch errors.", "Auditing certificates for weak keys or SHA-1 signatures.", "Checking which TLS version and cipher a server negotiates.", "Verifying a chain before deploying a renewed certificate."],
        [
            "Inspect: openssl x509 -text -noout -in cert.pem.",
            "Check expiry, key size (RSA 2048+ / EC P-256+), SHA-2 signature and self-signed status.",
            "SAN must contain the hostname; CN alone is ignored by modern clients.",
            "openssl s_client -connect host:443 -servername host -tls1_3 tests the live server.",
            "Private keys: never shared or committed; 600 perms; prefer KMS/HSM.",
        ],
        [
            ex("Inspect a certificate file", "intermediate", "The four checks every certificate deserves (real Linux).", "bash", """
                openssl x509 -text -noout -in cert.pem
                openssl x509 -noout -dates -in cert.pem              # notBefore / notAfter
                openssl x509 -noout -checkend 2592000 -in cert.pem   # fails if expiring within 30 days
                openssl x509 -noout -text -in cert.pem | grep -E 'Public-Key|Signature Algorithm'
                openssl x509 -noout -subject -issuer -in cert.pem    # identical => self-signed
                openssl x509 -noout -ext subjectAltName -in cert.pem
                openssl x509 -noout -fingerprint -sha256 -in cert.pem
            """, runnable=False),
            ex("Test a live TLS endpoint", "advanced", "Chain, protocol and cipher actually negotiated.", "bash", """
                openssl s_client -connect example.com:443 -servername example.com -tls1_3 </dev/null
                openssl s_client -connect example.com:443 -servername example.com -showcerts </dev/null \\
                  | openssl x509 -noout -dates -issuer -subject
                openssl verify -CAfile chain.pem cert.pem
                curl -v --tlsv1.3 https://example.com -o /dev/null
            """, runnable=False),
            ex("A short-lived dev certificate", "advanced", "Self-signed EC P-256 with SHA-256, for local development only.", "bash", """
                openssl req -x509 -newkey ec -pkeyopt ec_paramgen_curve:P-256 -sha256 -days 30 \\
                  -nodes -keyout dev.key -out dev.crt -subj "/CN=localhost" -addext "subjectAltName=DNS:localhost"
                chmod 600 dev.key
                openssl x509 -text -noout -in dev.crt     # Issuer == Subject: self-signed, never for production
                sha256sum dev.crt
            """, runnable=False),
        ],
        ["openssl x509 -text -noout -in cert.pem", "openssl x509 -noout -dates -checkend 2592000", "openssl s_client -connect h:443 -servername h", "openssl verify -CAfile chain.pem cert.pem", "update-ca-certificates"],
        ["Serving the leaf without its intermediate works in some browsers (cached) and fails in curl and apps.", "A clock that is wrong makes valid certificates look expired.", "Disabling verification (curl -k, verify=False) to 'fix' errors removes all protection against interception.", "Pasting a private key anywhere public means the key is compromised; revoke and reissue."],
        [
            qa("intermediate", "What do you check when reviewing a certificate?", "Validity dates (not expired, not before its start), that the SAN covers the hostname, the key strength (RSA at least 2048 bits or EC P-256 or stronger), a SHA-2 based signature algorithm, the issuer chain to a trusted root and whether it is self-signed. openssl x509 -text -noout -in cert.pem shows all of these."),
            qa("intermediate", "What is a certificate chain?", "The leaf certificate is signed by an intermediate CA, which is signed by a root CA in the client's trust store. Servers must send the leaf and intermediates; clients already have the root."),
            qa("advanced", "How do you see which TLS version and cipher a server negotiates?", "openssl s_client -connect host:443 -servername host prints the protocol and cipher; add -tls1_3 or -tls1_2 to test specific versions. Modern servers should negotiate TLS 1.3 with AEAD suites such as TLS_AES_256_GCM_SHA384."),
            qa("advanced", "When is a self-signed certificate acceptable?", "For local development, tests, or internal services where clients are explicitly configured to trust that certificate or a private CA. Public-facing services need certificates from a publicly trusted CA."),
            qa("advanced", "A client says 'unable to get local issuer certificate'. What is wrong?", "The client cannot build a chain to a trusted root: usually the server is not sending its intermediate certificate, or the client's CA bundle lacks the issuing root (common with private CAs). Check with openssl s_client -showcerts and fix the served chain or the trust store."),
        ],
        ["networking-tools", "time-ntp", "ssh-keys"],
        chain(
            ("ClientHello", "TLS 1.3, SNI", "Hello", "The client offers TLS 1.3, key shares and the server name."),
            ("Certificate", "leaf + inter.", "Present", "The server sends its certificate chain and signs the handshake.", "chain"),
            ("Verify chain", "to trusted root", "Trust", "The client validates signatures (SHA-2) up to a root in its store.", "verify"),
            ("Check fields", "SAN, dates, key", "Validate", "Hostname in SAN, within validity dates, adequate key size.", "check"),
            ("Session", "AES-256-GCM", "Encrypt", "Traffic flows encrypted with an AEAD cipher.", "data"),
        ),
    ),
    topic(
        "selinux-apparmor", "Mandatory Access Control: SELinux & AppArmor", "security", "advanced", "SE",
        "Kernel-enforced policy that limits what even root-owned services may touch.",
        "Regular permissions are locks on each door, chosen by each owner. Mandatory access control is the building's security policy: even if a door is unlocked, a cleaner's badge only opens the floors on their route, and the policy is set centrally, not by the cleaner.",
        "Discretionary access control (owner, group, mode) lets owners decide access, so a compromised root process can do anything. Mandatory access control adds a second, central policy enforced by the kernel through Linux Security Modules. SELinux (RHEL, Fedora, Android) labels every process and file with a context such as system_u:system_r:httpd_t and allows only interactions the policy permits, for example httpd_t reading httpd_sys_content_t. Modes are enforcing, permissive (log only) and disabled; getenforce shows the mode, ls -Z and ps -Z show labels, restorecon fixes labels, semanage fcontext and semanage port change policy mappings, and booleans (setsebool -P httpd_can_network_connect on) toggle common options. Denials appear as AVC messages in the audit log; ausearch -m avc and audit2why explain them. AppArmor (Ubuntu, Debian, SUSE) uses path-based profiles per program, in enforce or complain mode, managed with aa-status, aa-complain and aa-enforce. The right response to a denial is to fix labels or grant a narrow rule, not to disable the system.",
        ["Containing a compromised web server so it cannot read home directories.", "Serving web content from a non-default directory under SELinux.", "Confining a custom daemon with an AppArmor profile.", "Explaining 'permission denied' that persists despite correct chmod."],
        [
            "MAC is checked after normal permissions; both must allow.",
            "SELinux: labels (user:role:type:level); type enforcement does the work.",
            "ls -Z, ps -Z, restorecon -Rv, semanage fcontext, setsebool -P.",
            "Denials: ausearch -m avc -ts recent; audit2why explains.",
            "AppArmor: path-based profiles; aa-status, complain vs enforce.",
        ],
        [
            ex("Diagnose an SELinux denial", "intermediate", "A web root moved to /srv/www returns 403 (RHEL family).", "bash", """
                getenforce
                ls -Zd /srv/www /var/www/html
                sudo ausearch -m avc -ts recent | audit2why
                sudo semanage fcontext -a -t httpd_sys_content_t '/srv/www(/.*)?'
                sudo restorecon -Rv /srv/www
                sudo setsebool -P httpd_can_network_connect on   # app proxies to a backend
            """, runnable=False),
            ex("AppArmor profiles", "intermediate", "See and tune confinement on Ubuntu.", "bash", """
                sudo aa-status
                ls /etc/apparmor.d/
                sudo aa-complain /usr/sbin/nginx     # log only while you test
                sudo journalctl -k | grep apparmor | tail
                sudo aa-enforce /usr/sbin/nginx
            """, runnable=False),
        ],
        ["getenforce · sestatus", "ls -Z · ps -Z", "restorecon -Rv path", "semanage fcontext -a -t type 'path(/.*)?'", "aa-status · aa-complain · aa-enforce"],
        ["setenforce 0 or disabling SELinux to fix one app removes protection for every service.", "mv keeps the old SELinux label, cp creates a new one; moved files often need restorecon.", "Permissive mode on in production hides attacks while logging them."],
        [
            qa("intermediate", "DAC vs MAC?", "Discretionary access control lets file owners set permissions, and root bypasses it. Mandatory access control is a system-wide policy enforced by the kernel that even root processes cannot override, limiting damage from a compromised service."),
            qa("intermediate", "chmod is correct but Apache still gets permission denied on RHEL. Why?", "SELinux is denying it: the files probably have the wrong type label (for example user_home_t instead of httpd_sys_content_t). Check ausearch -m avc, then set the correct context with semanage fcontext and restorecon."),
            qa("advanced", "SELinux vs AppArmor?", "SELinux labels every object and enforces type rules, which is very fine-grained but more complex. AppArmor confines individual programs with path-based profiles, which is simpler to write but depends on file paths."),
            qa("advanced", "What is permissive mode for?", "The policy is evaluated and denials are logged but not enforced. It is used briefly to develop or debug policy, then the system goes back to enforcing."),
        ],
        ["permissions", "special-permissions", "namespaces-cgroups"],
        chain(
            ("httpd_t", "nginx process", "Subject", "nginx runs in the <b>httpd_t</b> domain."),
            ("DAC check", "rwx ok", "Permissions", "Classic owner/group/mode checks pass.", "open"),
            ("LSM hook", "SELinux", "MAC check", "The kernel asks SELinux: may httpd_t read this file type?", "check"),
            ("File label", "user_home_t", "Object", "The file is labelled user_home_t, not web content.", "label"),
            ("AVC deny", "audit log", "Denied", "Access is denied and an AVC record explains why.", "deny"),
        ),
    ),
    topic(
        "file-descriptors", "File Descriptors & lsof", "internals", "intermediate", "FD",
        "The small integers every process uses for files, sockets and pipes.",
        "A cloakroom ticket system. When a process opens something it gets a numbered ticket (0, 1, 2, 3...). It never handles the coat directly, it just shows the ticket. lsof is the attendant's list of which tickets are out and to whom.",
        "When a process opens a file, socket, pipe or device, the kernel returns a file descriptor: the lowest free integer in that process's table, pointing to an open file description with an offset and flags. Every process starts with 0 (stdin), 1 (stdout) and 2 (stderr); shell redirections simply rewire these before exec. File descriptors are inherited across fork and exec unless marked close-on-exec. /proc/<pid>/fd lists them as symlinks, and lsof shows open files system-wide: lsof -p PID, lsof -i :443 for sockets, lsof +L1 for deleted-but-open files. Each process has a limit (ulimit -n, LimitNOFILE in systemd) and the system a global one (fs.file-max); busy servers with many connections need higher limits, and 'Too many open files' (EMFILE) usually means either a low limit or a descriptor leak. A deleted file stays on disk until every descriptor to it is closed, a classic reason why disk space is not freed.",
        ["Finding which process holds a file or port.", "Recovering space held by deleted log files.", "Raising limits for a high-connection server.", "Finding a descriptor leak in an application."],
        [
            "0 stdin, 1 stdout, 2 stderr; new opens get the lowest free number.",
            "ls -l /proc/PID/fd shows what each fd points to.",
            "lsof -p PID · lsof -i :PORT · lsof +L1 (deleted but open).",
            "ulimit -n and systemd LimitNOFILE cap per-process fds.",
            "Steadily growing fd counts signal a leak.",
        ],
        [
            ex("The three standard descriptors", "basic", "Redirect fd 1 and fd 2 separately and together.", "bash", """
                ls notes.txt /nope 2> err.txt
                cat err.txt
                ls notes.txt /nope > all.txt 2>&1
                cat all.txt
                echo "discarded" > /dev/null
                wc -l < logs/app.log
            """),
            ex("Inspect open files", "intermediate", "/proc and lsof on a real system.", "bash", """
                ls -l /proc/$$/fd
                exec 3> /tmp/demo.txt; echo hi >&3; ls -l /proc/$$/fd/3; exec 3>&-
                sudo lsof -p "$(pgrep -o nginx)" | head
                sudo lsof -i :443
                sudo lsof +L1                          # deleted files still open
                ls /proc/$(pgrep -o nginx)/fd | wc -l
            """, runnable=False),
            ex("Limits", "advanced", "Per-process and per-service file descriptor limits.", "bash", """
                ulimit -n
                ulimit -Hn
                cat /proc/$(pgrep -o nginx)/limits | grep 'open files'
                sudo systemctl edit nginx              # [Service] LimitNOFILE=65536
                cat /proc/sys/fs/file-nr               # allocated, unused, max
            """, runnable=False),
        ],
        ["ls -l /proc/PID/fd", "lsof -p PID · lsof -i :PORT", "lsof +L1", "ulimit -n · LimitNOFILE=", "exec 3>file · exec 3>&-"],
        ["ulimit changes in a shell do not affect services started by systemd; use LimitNOFILE.", "Truncating a deleted-but-open file via /proc/PID/fd/N frees space without restart, but the app keeps writing at its old offset.", "Leaked sockets in CLOSE_WAIT mean the app never closed its side."],
        [
            qa("basic", "What is a file descriptor?", "A per-process integer handle returned by open, socket or pipe that refers to a kernel open-file object. Reads, writes and closes use the number, and 0, 1, 2 are stdin, stdout and stderr."),
            qa("intermediate", "How do you find which process has a port open?", "sudo lsof -i :PORT or sudo ss -tlnp 'sport = :PORT'. Both show the PID and program."),
            qa("intermediate", "What causes 'Too many open files'?", "The process hit its RLIMIT_NOFILE. Either the limit is too low for the workload (raise LimitNOFILE or ulimit -n) or the application leaks descriptors, which shows as a steadily growing count in /proc/PID/fd."),
            qa("advanced", "Why doesn't deleting a large log free disk space?", "Deleting removes the name, but the inode stays allocated while any process has it open. lsof +L1 finds it; restarting or signalling the process to reopen logs releases the space."),
        ],
        ["pipes-redirection", "proc-sys", "disks-storage"],
        chain(
            ("open()", "app.log", "Open", "The process asks the kernel to open app.log."),
            ("fd 3", "lowest free", "Descriptor", "The kernel returns 3, since 0, 1 and 2 are taken.", "fd"),
            ("Open file", "offset, flags", "Kernel object", "fd 3 points to an open-file object with the current offset.", "ref"),
            ("Inode", "data on disk", "File", "The open file references the inode; rm only removes the name.", "inode"),
            ("close(3)", "free slot", "Close", "Only after the last close is a deleted file's space freed.", "close"),
        ),
    ),
]

_BATCH_4 = [
    topic(
        "proc-sys", "/proc & /sys Deep Dive", "internals", "advanced", "PC",
        "Virtual filesystems where the kernel publishes processes, statistics and tunables.",
        "A car's diagnostic port. Nothing is stored there; plugging in a reader (cat) asks the engine computer for live values, and a few writable pins let a mechanic change settings while the engine runs.",
        "/proc (procfs) and /sys (sysfs) are generated by the kernel on every read and use no disk. /proc/<pid>/ describes each process: status (state, memory, threads, uid), cmdline, environ, fd/ (open descriptors), maps and smaps (memory mappings), limits, cgroup, ns/ (namespaces) and stack. System-wide files include /proc/cpuinfo, /proc/meminfo, /proc/loadavg, /proc/stat, /proc/pressure/* (PSI stall information), /proc/net/ and /proc/cmdline. /proc/sys/ holds kernel tunables that sysctl reads and writes (vm.swappiness is /proc/sys/vm/swappiness). /sys is a structured view of devices, drivers, buses and kernel objects: /sys/class/net/eth0/statistics for interface counters, /sys/block/sda/queue/scheduler for the I/O scheduler, and /sys/fs/cgroup for cgroup v2 control files. Tools like ps, top, free, ss and lsblk are mostly friendly front ends over these files, so reading them directly is a reliable fallback in minimal containers.",
        ["Inspecting a process in a container that lacks ps or lsof.", "Reading memory or pressure stall data for monitoring.", "Tuning kernel parameters at runtime.", "Reading network interface counters or disk queue settings."],
        [
            "/proc/<pid>/{status,cmdline,fd,maps,limits,cgroup} describe one process.",
            "/proc/meminfo, loadavg, pressure/{cpu,memory,io} describe the system.",
            "/proc/sys/* is what sysctl reads and writes.",
            "/sys exposes devices, drivers and cgroups as small files.",
            "Values are generated on read: no disk, always current.",
        ],
        [
            ex("Process details from /proc", "intermediate", "What ps and lsof read under the hood (real Linux).", "bash", """
                cat /proc/$$/status | grep -E 'Name|State|VmRSS|Threads'
                tr '\\0' ' ' < /proc/$$/cmdline; echo
                ls -l /proc/$$/fd
                cat /proc/$$/limits | head -n 8
                readlink /proc/$$/ns/net /proc/$$/ns/pid
                cat /proc/$$/cgroup
            """, runnable=False),
            ex("System-wide views", "advanced", "Memory, load, pressure and network counters.", "bash", """
                head -n 5 /proc/meminfo
                cat /proc/loadavg
                cat /proc/pressure/memory /proc/pressure/io
                cat /sys/class/net/eth0/statistics/rx_bytes
                cat /sys/block/sda/queue/scheduler
                cat /proc/sys/vm/swappiness && sysctl vm.swappiness
            """, runnable=False),
        ],
        ["cat /proc/PID/status", "ls -l /proc/PID/fd", "cat /proc/meminfo · /proc/loadavg", "cat /proc/pressure/memory", "ls /sys/class/net · /sys/block"],
        ["/proc/<pid>/environ and cmdline can expose secrets passed as arguments or env vars.", "Writes to /proc/sys or /sys are lost on reboot unless persisted in /etc/sysctl.d or udev rules.", "Inside containers, /proc/meminfo and cpuinfo may show host values, not the cgroup limits."],
        [
            qa("intermediate", "What is /proc?", "A virtual filesystem the kernel generates on demand. It exposes per-process directories (/proc/<pid>) and system information such as meminfo, loadavg and cpuinfo, plus tunables under /proc/sys."),
            qa("intermediate", "/proc vs /sys?", "/proc started as process information and accumulated many system files over time. /sys is the structured sysfs view of the kernel device model: devices, drivers, buses, block queues and cgroups, typically one value per file."),
            qa("advanced", "How do you see what a process has open without lsof?", "ls -l /proc/<pid>/fd lists every descriptor as a symlink to its file, socket or pipe; /proc/<pid>/net/tcp and fdinfo give further detail."),
            qa("advanced", "What is PSI in /proc/pressure?", "Pressure stall information: the share of time tasks were stalled waiting for CPU, memory or I/O over 10 s, 60 s and 300 s windows. It is a more direct saturation signal than load average."),
        ],
        ["kernel-internals", "file-descriptors", "kernel-modules-sysctl"],
        chain(
            ("cat", "/proc/1234/status", "Read", "A tool opens a file under /proc."),
            ("procfs", "no disk", "VFS", "The VFS routes the read to the procfs driver.", "read"),
            ("Kernel data", "task_struct", "Generate", "procfs formats live kernel structures into text.", "query"),
            ("Output", "VmRSS: 51200 kB", "Return", "Fresh values every read; nothing is cached on disk.", "text"),
        ),
    ),
    topic(
        "memory-management", "Memory: Page Cache, Swap & the OOM Killer", "perf", "advanced", "MM",
        "Read free correctly, understand swap and know why the OOM killer fires.",
        "A desk in a library. Your working papers are application memory; the books you recently fetched and left on the desk are page cache (instantly reusable shelf space if you need room). Swap is a slow storeroom down the hall, and when the desk and storeroom are both full the librarian (OOM killer) removes the person using the most space.",
        "Linux uses spare RAM as page cache for file data, so free memory looks low on a healthy system; the available column estimates what applications can still get without swapping. Anonymous memory (heap, stacks) can only be reclaimed by swapping it out, while clean page cache can simply be dropped. vm.swappiness (0-200, default 60) biases reclaim between the two. Processes have virtual size (VSZ, address space) and resident set size (RSS, pages in RAM); shared libraries make RSS overcount, so PSS in smaps_rollup is fairer. When memory cannot be reclaimed, the kernel's OOM killer picks a victim by oom_score (mostly memory usage, adjustable with oom_score_adj) and sends SIGKILL; with cgroups, the limit can be hit inside a container while the host has plenty free. Watch available memory, swap-in/swap-out rates (vmstat si/so), major page faults and /proc/pressure/memory rather than free alone. Early-warning tools like systemd-oomd act on pressure before the kernel OOM killer does.",
        ["Deciding whether a server actually needs more RAM.", "Explaining OOMKilled containers and exit code 137.", "Tuning swap on database hosts.", "Finding which process is leaking memory."],
        [
            "Watch available, not free: page cache is reclaimable.",
            "RSS = resident; VSZ = address space; PSS shares libraries fairly.",
            "Swap activity (si/so) matters more than swap used.",
            "OOM killer sends SIGKILL to the highest oom_score; check dmesg.",
            "cgroup memory.max can OOM a container while the host is fine.",
        ],
        [
            ex("Read memory usage", "basic", "Totals, top consumers and a snapshot.", "bash", """
                free -h
                ps aux
                top
            """),
            ex("Deeper memory checks", "advanced", "Reclaim, swapping and OOM evidence on a real host.", "bash", """
                free -h
                vmstat 1 5                                  # si/so columns = swap in/out
                grep -E 'MemAvailable|Cached|SwapTotal|SwapFree|Dirty' /proc/meminfo
                ps -eo pid,comm,rss,vsz --sort=-rss | head
                cat /proc/$(pgrep -o java)/smaps_rollup | grep -E 'Rss|Pss'
                sudo dmesg -T | grep -i -E 'out of memory|oom-kill'
                cat /proc/pressure/memory
            """, runnable=False),
            ex("Swap and OOM tuning", "advanced", "Swap files, swappiness and protecting critical processes.", "bash", """
                sudo fallocate -l 2G /swapfile && sudo chmod 600 /swapfile
                sudo mkswap /swapfile && sudo swapon /swapfile
                swapon --show
                sudo sysctl vm.swappiness=10
                echo -500 | sudo tee /proc/$(pgrep -o postgres)/oom_score_adj
                cat /sys/fs/cgroup/system.slice/myapp.service/memory.events   # oom_kill count
            """, runnable=False),
        ],
        ["free -h", "vmstat 1", "ps -eo pid,comm,rss --sort=-rss", "dmesg -T | grep -i oom", "swapon --show · sysctl vm.swappiness"],
        ["echo 3 > /proc/sys/vm/drop_caches only hurts performance; it is not a fix for anything.", "JVMs and other runtimes size heaps from host RAM unless told about the container limit.", "Zero swap means no buffer: the OOM killer fires sooner and harder."],
        [
            qa("basic", "Why does free show almost no free memory on a healthy server?", "Linux uses idle RAM as page cache. That memory is reclaimed instantly when applications need it, so the available column is the meaningful number."),
            qa("intermediate", "RSS vs VSZ?", "VSZ is the total virtual address space mapped by the process, including untouched and shared regions. RSS is the memory actually resident in RAM, which still double-counts shared pages; PSS divides shared pages among users."),
            qa("intermediate", "What does the OOM killer do?", "When memory cannot be reclaimed for an allocation, the kernel chooses a process with the highest oom_score (mostly by memory use, adjusted by oom_score_adj) and kills it with SIGKILL, logging the event in dmesg."),
            qa("advanced", "Is using swap bad?", "Swap used is not itself bad: idle pages moved out free RAM for cache. Continuous swapping (high si/so in vmstat, rising memory pressure) is bad because it stalls processes on disk I/O."),
            qa("advanced", "A container is OOMKilled but the node has free memory. Why?", "The container's cgroup reached its own memory.max limit. The kernel OOM-kills inside that cgroup regardless of host free memory; raise the limit or reduce usage, for example by sizing the heap to the limit."),
        ],
        ["kernel-internals", "proc-sys", "troubleshooting-slow-server"],
        chain(
            ("Allocate", "malloc + touch", "Demand", "An app touches new pages; the kernel needs free frames."),
            ("Reclaim", "drop page cache", "Cheap reclaim", "Clean page cache is dropped first.", "need"),
            ("Swap out", "anon pages", "Costly reclaim", "Idle anonymous pages move to swap (si/so rises).", "evict"),
            ("No memory", "limit reached", "Exhausted", "Nothing more can be reclaimed in time.", "fail"),
            ("OOM killer", "SIGKILL victim", "Kill", "The highest oom_score process is killed; dmesg records it.", "KILL"),
        ),
    ),
    topic(
        "cpu-load", "CPU, Load Average & top", "perf", "intermediate", "LD",
        "What load average really measures and how to find the busy process.",
        "A supermarket with N checkouts (CPU cores). Load average is the average number of customers being served or waiting in line. A load of 4 on 4 checkouts is busy but fine; 12 on 4 means long queues. On Linux, customers stuck waiting for the stockroom (disk I/O) are counted too.",
        "Load average (uptime, top, /proc/loadavg) is an exponentially damped average over 1, 5 and 15 minutes of tasks that are runnable or in uninterruptible sleep (D state, usually waiting on disk or NFS). Compare it with the number of CPUs (nproc): load far above core count means queueing, but high load with idle CPU points to I/O waits. top and htop show per-process %CPU (100% means one full core), and the summary line breaks CPU time into us (user), sy (kernel), ni (niced), id (idle), wa (I/O wait), hi/si (interrupts) and st (steal, time taken by the hypervisor). mpstat -P ALL shows per-core usage and reveals a single-threaded hot spot, and pidstat 1 tracks per-process usage over time. ps -eo pid,comm,%cpu --sort=-%cpu gives a quick snapshot. nice and renice change scheduling priority; cgroups (CPUQuota in systemd, CPU limits in containers) cap usage, and throttling (nr_throttled in cpu.stat) can make apps slow even when the host is idle.",
        ["Deciding whether a server is CPU-bound or I/O-bound.", "Finding the process eating CPU.", "Spotting a single-threaded bottleneck on a many-core box.", "Detecting CPU steal on virtual machines or throttling in containers."],
        [
            "Load counts runnable + D-state tasks; compare with nproc.",
            "%CPU 100 = one full core; 400 on a 4-core box is all of it.",
            "High wa or many D-state tasks: look at disks, not CPU.",
            "st (steal) > a few percent: noisy neighbours or undersized VM.",
            "Container slow at low host CPU: check cgroup throttling.",
        ],
        [
            ex("Find the CPU hog", "basic", "Load, a snapshot, sorting by %CPU, then the fix.", "bash", """
                uptime
                top
                ps aux | sort -k3 -rn | head -n 3
                kill 1337
                uptime
            """),
            ex("Per-core and per-process views", "intermediate", "Distinguish CPU saturation from I/O waits (real Linux).", "bash", """
                nproc
                cat /proc/loadavg
                mpstat -P ALL 1 3
                pidstat -u 1 5
                ps -eo pid,stat,comm,%cpu --sort=-%cpu | head
                ps -eo pid,stat,comm | awk '$2 ~ /D/'     # tasks stuck in I/O
            """, runnable=False),
            ex("Priorities and limits", "advanced", "Lower a job's priority and check container throttling.", "bash", """
                nice -n 10 ./batch-report.sh
                sudo renice +15 -p 4242
                sudo systemctl set-property backup.service CPUQuota=50%
                cat /sys/fs/cgroup/system.slice/backup.service/cpu.stat   # nr_throttled, throttled_usec
            """, runnable=False),
        ],
        ["uptime · cat /proc/loadavg · nproc", "top · htop (P sort CPU, M sort mem)", "ps -eo pid,comm,%cpu --sort=-%cpu", "mpstat -P ALL 1 · pidstat 1", "nice -n 10 cmd · renice"],
        ["Load average is not CPU percent; a load of 8 can mean idle CPUs and blocked disks.", "top's first iteration %CPU is since boot on some tools; look at later refreshes.", "An app at exactly 100% on a multi-core box is often single-threaded, so adding cores will not help."],
        [
            qa("basic", "What does a load average of 4.0 mean?", "On average four tasks were running or waiting to run (or waiting uninterruptibly on I/O) over that window. Compared with nproc: on 4 cores it is full utilisation, on 16 it is light."),
            qa("intermediate", "Load is high but CPU is mostly idle. Why?", "Linux load includes tasks in uninterruptible sleep, typically waiting on disk or network filesystems. Check wa in top, iostat for disk saturation and ps for processes in D state."),
            qa("intermediate", "What is CPU steal time?", "Time a virtual CPU wanted to run but the hypervisor ran something else. Sustained steal indicates oversubscribed hosts or burstable instance credits running out."),
            qa("advanced", "A container is slow but node CPU is low. What do you check?", "CPU throttling from its cgroup quota: cpu.stat nr_throttled and throttled_usec. Short bursts exceeding the quota are throttled for the rest of each period; raise or remove the limit, or reduce thread counts."),
        ],
        ["processes", "memory-management", "troubleshooting-slow-server"],
        chain(
            ("Tasks", "R + D state", "Count", "The kernel counts runnable and uninterruptible tasks."),
            ("Load avg", "1, 5, 15 min", "Average", "Damped averages appear in uptime and /proc/loadavg.", "sample"),
            ("vs nproc", "4 cores", "Compare", "Load above core count means queueing.", "ratio"),
            ("top", "us sy wa st", "Break down", "CPU time split shows user, kernel, I/O wait or steal.", "split"),
            ("Process", "%CPU sort", "Culprit", "Sort by %CPU to find the busy process.", "PID"),
        ),
    ),
    topic(
        "performance-tools", "Performance Tools: vmstat, iostat, sar, perf, strace", "perf", "advanced", "PT",
        "Measure before guessing: system-wide counters, per-device I/O, history, profiling and syscall tracing.",
        "A doctor's kit. vmstat is the pulse and blood pressure, iostat the X-ray of each organ (disk), sar the patient's history chart, perf the scan that shows which muscle is working hardest, and strace the stethoscope on a single heartbeat.",
        "vmstat 1 prints one line per second: run queue (r), blocked (b), swap in/out (si/so), block I/O (bi/bo), interrupts, context switches and CPU split, which is the fastest whole-system overview. iostat -xz 1 (sysstat) shows per-device utilisation, IOPS (r/s, w/s), throughput, average wait (r_await, w_await) and queue size; on SSDs and NVMe, latency and queue depth matter more than %util. iotop and pidstat -d show I/O per process. sar records the same counters every 10 minutes when sysstat collection is enabled, so you can ask what happened at 03:00 yesterday (sar -u, -r, -d, -n DEV). perf top and perf record -g sample stack traces across the kernel and user space to show where CPU time goes; flame graphs visualise the result. strace -p PID -f traces system calls of one process (slow, use briefly), and strace -c summarises counts and time per syscall; ltrace does the same for library calls, and bpftrace and the BCC tools (execsnoop, opensnoop, biolatency) give low-overhead tracing on modern kernels. Brendan Gregg's USE method (utilisation, saturation, errors per resource) organises which tool to run.",
        ["First 60 seconds on a slow server.", "Proving a disk is the bottleneck.", "Finding a hot function in a CPU-bound service.", "Seeing why a process hangs (which syscall is it stuck in?)."],
        [
            "vmstat 1: r (run queue), b (blocked), si/so, wa at a glance.",
            "iostat -xz 1: await and aqu-sz per device; %util misleads on SSDs.",
            "sar keeps history; enable sysstat collection before you need it.",
            "perf record -g + flame graph for CPU profiles.",
            "strace -c for a quick syscall summary; it slows the target a lot.",
        ],
        [
            ex("The 60-second checklist", "intermediate", "System-wide counters in order (real Linux, sysstat installed).", "bash", """
                uptime
                dmesg -T | tail
                vmstat 1 5
                mpstat -P ALL 1 3
                pidstat 1 3
                iostat -xz 1 3
                free -m
                sar -n DEV 1 3
                sar -n TCP,ETCP 1 3
                top -b -n 1 | head -n 15
            """, runnable=False),
            ex("Disk and per-process I/O", "advanced", "Which device, which process.", "bash", """
                iostat -xz 1 5
                sudo iotop -oPa
                pidstat -d 1 5
                sar -d -f /var/log/sysstat/sa17      # yesterday's disk stats
                sudo biolatency-bpfcc 10 1           # I/O latency histogram (BCC)
            """, runnable=False),
            ex("Profile and trace", "advanced", "Where CPU goes and what a process asks the kernel.", "bash", """
                sudo perf top
                sudo perf record -F 99 -g -p 4242 -- sleep 30 && sudo perf report
                sudo strace -c -p 4242                 # Ctrl-C after a few seconds
                sudo strace -f -tt -e trace=network,openat -p 4242
                sudo execsnoop-bpfcc                   # short-lived processes
            """, runnable=False),
        ],
        ["vmstat 1", "iostat -xz 1 · iotop -o", "sar -u -r -d -n DEV", "perf top · perf record -g", "strace -c -p PID · strace -f -e trace=..."],
        ["strace can slow a process by 10-100x; never leave it attached in production.", "%util 100 on an NVMe device does not mean saturation: it can serve many requests in parallel.", "sar has no data for the incident unless collection was enabled beforehand."],
        [
            qa("intermediate", "What do the r and b columns in vmstat mean?", "r is the number of runnable tasks (running or waiting for CPU); consistently above the CPU count means CPU saturation. b is tasks blocked in uninterruptible sleep, usually on I/O."),
            qa("intermediate", "How do you tell if a disk is the bottleneck?", "iostat -xz 1: rising r_await and w_await, a growing queue (aqu-sz) and high utilisation on that device, combined with high wa in vmstat or tasks in D state. iotop or pidstat -d shows which process causes it."),
            qa("advanced", "perf vs strace?", "perf samples where CPU time is spent (functions and stacks) with low overhead, ideal for CPU-bound problems. strace intercepts every system call of a process, showing what it asks the kernel and where it blocks, but with high overhead."),
            qa("advanced", "What is the USE method?", "For every resource (CPU, memory, disks, network, locks) check Utilisation, Saturation (queueing) and Errors. It gives a systematic checklist instead of guessing, and maps directly to tools like mpstat, vmstat, iostat and sar."),
        ],
        ["cpu-load", "memory-management", "troubleshooting-slow-server"],
        chain(
            ("vmstat", "r b si so wa", "Overview", "Is the pressure on CPU, memory or I/O?"),
            ("mpstat", "per core", "CPU", "Is one core pinned or all of them?", "cpu"),
            ("iostat", "await, aqu-sz", "Disk", "Is a device slow or queueing?", "io"),
            ("sar", "history", "Trend", "When did it start, and does it repeat?", "when"),
            ("perf/strace", "functions, calls", "Drill down", "Profile or trace the guilty process.", "pid"),
        ),
    ),
    topic(
        "troubleshooting-slow-server", "Troubleshooting a Slow Server", "perf", "advanced", "TS",
        "A repeatable path from 'it is slow' to the bottleneck.",
        "A detective at a crime scene. Secure the scene (do not reboot yet), note the time, check the obvious witnesses (load, memory, disk, logs), then narrow down to the suspect process, and only then make an arrest (fix) and write the report (post-mortem).",
        "Start by defining the problem: what is slow, for whom, since when and what changed (deploys, traffic, cron jobs)? Then check resources with the USE method. uptime gives the load trend; dmesg -T shows OOM kills, disk errors and network driver resets. top or htop shows whether CPU time is user, system, iowait or steal and which processes dominate. free -h and vmstat reveal memory pressure and swapping. df -h and df -i catch full filesystems and inode exhaustion, and iostat -xz shows a saturated disk. ss -s and ss -tan summarise connections, revealing exhaustion of ports or a backlog. Application and service logs (journalctl -u, app logs) show errors, timeouts and slow queries, and dependencies such as databases or DNS are frequent root causes. Change one thing at a time, capture evidence (outputs, timestamps) before restarting, and follow up with monitoring and alerting so the next occurrence is caught earlier.",
        ["On-call response to latency alerts.", "Capacity reviews after traffic growth.", "Post-incident analysis and runbooks.", "Interview system design and troubleshooting rounds."],
        [
            "Ask what changed and since when before touching anything.",
            "uptime, dmesg, top, free, df, iostat, ss, logs: in that rough order.",
            "Capture evidence before restarting; restarts destroy clues.",
            "Distinguish CPU, memory, disk, network and dependency bottlenecks.",
            "Close the loop with monitoring and a runbook update.",
        ],
        [
            ex("Triage in the simulator", "intermediate", "Load, top consumers, memory, disk and recent errors.", "bash", """
                uptime
                top
                free -h
                df -h
                du -sh logs data tmp
                ps aux | sort -k3 -rn | head -n 3
                grep ERROR logs/app.log | tail -n 3
                grep -c "slow query" logs/app.log
            """),
            ex("Triage on a real server", "advanced", "The same questions with the full toolset.", "bash", """
                uptime; dmesg -T | tail -n 20
                top -b -n 1 | head -n 20
                vmstat 1 5; free -h
                df -h; df -i
                iostat -xz 1 3
                ss -s; ss -tan state time-wait | wc -l
                journalctl -p err --since "30 min ago"
                curl -s -o /dev/null -w '%{time_total}\\n' http://localhost/health
            """, runnable=False),
        ],
        ["uptime · dmesg -T | tail", "top · vmstat 1", "free -h · df -h · df -i", "iostat -xz 1 · ss -s", "journalctl -p err --since '1 hour ago'"],
        ["Rebooting first may fix symptoms but destroys the evidence needed for a root cause.", "Averages hide outliers; look at p99 latency and per-core or per-device numbers.", "The slow part is often a dependency (database, DNS, external API), not the server you are logged into."],
        [
            qa("intermediate", "A server is slow. What are your first commands?", "uptime for load trend, dmesg -T | tail for kernel errors and OOM kills, top for CPU split and top processes, free -h and vmstat for memory and swapping, df -h and iostat for disk, and the service logs. Then drill into the resource that looks saturated."),
            qa("intermediate", "How do you tell a CPU problem from an I/O problem?", "CPU-bound: high us or sy, run queue above core count, little iowait. I/O-bound: high wa, tasks in D state, high await and queue size in iostat, and load high while CPUs are idle."),
            qa("advanced", "df shows free space but writes fail with 'No space left on device'. Why?", "The filesystem has run out of inodes, typically from millions of tiny files (sessions, caches). df -i confirms it; delete or consolidate the files or rebuild with more inodes."),
            qa("advanced", "What do you do after the immediate fix?", "Write down the timeline and evidence, find the root cause and contributing factors, add monitoring and alerts that would have caught it earlier, update the runbook and schedule the permanent fix. Blameless post-mortems keep this honest."),
        ],
        ["cpu-load", "memory-management", "performance-tools"],
        chain(
            ("Define", "what, since when", "Scope", "Who sees slowness, since when, and what changed?"),
            ("uptime/dmesg", "load, errors", "Overview", "Load trend and kernel errors such as OOM kills.", "check"),
            ("top/vmstat", "CPU, memory", "Resources", "CPU split, swapping and top processes.", "USE"),
            ("df/iostat", "disk", "Storage", "Full filesystems, inodes and slow devices.", "USE"),
            ("Logs/deps", "app, DB, DNS", "Dependencies", "Errors, timeouts and slow queries in logs.", "trace"),
            ("Fix + learn", "runbook", "Resolve", "Fix one thing at a time, then add monitoring.", "fix"),
        ),
    ),
    topic(
        "filesystems-mount", "Filesystems, mount & fstab", "internals", "intermediate", "MT",
        "ext4, XFS and Btrfs, and how they are attached to the tree at boot.",
        "Different kinds of filing cabinets (ext4, XFS, Btrfs) with different drawers and features. mount slots a cabinet into a specific spot in the office (a directory), and /etc/fstab is the floor plan the facilities team follows every morning.",
        "A filesystem organises blocks on a device into files and directories. ext4 is the mature default on Debian and Ubuntu, with journaling and online growth (but not shrinking while mounted). XFS, the RHEL default, scales well for large files and parallel I/O and can grow but never shrink. Btrfs adds copy-on-write, checksums, subvolumes, snapshots and compression. mkfs creates one, blkid and lsblk -f show UUIDs and types, and mount attaches it to a directory, with options such as ro, noatime, nodev, nosuid and noexec. /etc/fstab lists mounts applied at boot: device (preferably UUID=), mount point, type, options, dump and fsck order; nofail keeps boot going if a non-critical disk is missing, and systemd turns each line into a .mount unit. findmnt shows the live mount tree, and mount -a or systemctl daemon-reload plus findmnt --verify test fstab changes before a reboot. Pseudo filesystems (tmpfs, proc, sysfs, overlay for containers) are mounted the same way.",
        ["Adding a new data disk to a server.", "Hardening /tmp with nosuid,nodev,noexec.", "Choosing a filesystem for a database or file server.", "Recovering from a bad fstab line."],
        [
            "Use UUID= in fstab; device names like /dev/sdb can change.",
            "Test with findmnt --verify and mount -a before rebooting.",
            "nofail for optional disks; x-systemd.automount for lazy mounts.",
            "XFS cannot shrink; ext4 shrinks only offline.",
            "noatime reduces writes; nosuid,nodev,noexec harden shared mounts.",
        ],
        [
            ex("Read the mount configuration", "basic", "fstab, usage and fields in the simulator.", "bash", """
                cat /etc/fstab
                df -h
                awk '{print $2, $3, $4}' /etc/fstab
                grep noatime /etc/fstab
            """),
            ex("Add a data disk", "intermediate", "Partition-free XFS on a whole disk, mounted by UUID (real Linux).", "bash", """
                lsblk -f
                sudo mkfs.xfs /dev/nvme1n1
                sudo blkid /dev/nvme1n1
                sudo mkdir -p /data
                echo 'UUID=<uuid-from-blkid> /data xfs defaults,noatime,nofail 0 2' | sudo tee -a /etc/fstab
                sudo findmnt --verify
                sudo mount -a && findmnt /data
            """, runnable=False),
            ex("Mount options and pseudo filesystems", "advanced", "Remounts, tmpfs and checking what is mounted.", "bash", """
                findmnt -t ext4,xfs,btrfs
                sudo mount -o remount,ro /data
                sudo mount -t tmpfs -o size=512M,nosuid,nodev,noexec tmpfs /mnt/scratch
                findmnt -o TARGET,FSTYPE,OPTIONS /tmp
                sudo umount /mnt/scratch || sudo lsof +f -- /mnt/scratch
            """, runnable=False),
        ],
        ["lsblk -f · blkid", "mkfs.ext4 · mkfs.xfs", "mount -o noatime dev dir · umount dir", "findmnt · findmnt --verify", "mount -a"],
        ["A typo in fstab can stop the next boot; always verify and keep console access.", "umount fails with 'target is busy' when a process has files open there; lsof or fuser finds it.", "Mounting over a non-empty directory hides its contents until unmounted."],
        [
            qa("basic", "What is /etc/fstab?", "The table of filesystems mounted at boot: device (UUID), mount point, type, options, dump flag and fsck pass order. systemd generates mount units from it."),
            qa("intermediate", "Why use UUIDs instead of /dev/sdb1?", "Kernel device names depend on discovery order and can change between boots or when disks are added. UUIDs are stored in the filesystem and identify it reliably."),
            qa("intermediate", "ext4 vs XFS?", "Both are mature journaling filesystems. ext4 is the common default and can shrink offline; XFS scales better for large files and parallel workloads but cannot shrink."),
            qa("advanced", "How do you add a disk without risking boot?", "Create the filesystem, get its UUID with blkid, add an fstab entry with nofail, run findmnt --verify and mount -a to test, and confirm with findmnt before any reboot."),
        ],
        ["disks-storage", "lvm-raid", "boot-process"],
        chain(
            ("Device", "/dev/nvme1n1", "Block device", "A raw disk appears in lsblk."),
            ("mkfs.xfs", "UUID assigned", "Format", "A filesystem with a UUID is written.", "mkfs"),
            ("fstab", "UUID=... /data", "Persist", "An fstab line records where and how to mount it.", "entry"),
            ("mount", "/data", "Attach", "mount -a attaches it to the tree; findmnt confirms.", "mount"),
        ),
    ),
    topic(
        "lvm-raid", "LVM & Software RAID", "internals", "advanced", "LV",
        "Flexible volumes on top of disks, and redundancy across them.",
        "LVM is a warehouse that knocks down the walls between storage units: several rented units (disks) become one big floor (volume group) that you partition with movable partitions (logical volumes). RAID is keeping duplicate or parity copies of every box so a burst pipe in one unit loses nothing.",
        "LVM adds a layer between disks and filesystems. Physical volumes (pvcreate on disks or partitions) are pooled into a volume group (vgcreate), from which logical volumes are carved (lvcreate -L 50G -n data vg0). Logical volumes can be grown online (lvextend -r grows the filesystem too), moved between disks (pvmove) and snapshotted for consistent backups; thin pools allow over-provisioning. Software RAID with mdadm combines disks into /dev/md devices: RAID 1 mirrors, RAID 5 and 6 use parity to survive one or two disk failures, and RAID 10 stripes mirrors for performance and redundancy. /proc/mdstat shows array state and rebuild progress; failed disks are marked, removed and replaced with mdadm --manage. RAID protects against disk failure, not deletion, corruption or ransomware, so it never replaces backups. Btrfs and ZFS integrate volume management and RAID into the filesystem with checksums.",
        ["Growing a full filesystem without downtime.", "Surviving a disk failure on a bare-metal server.", "Taking a consistent snapshot before a risky upgrade.", "Combining several disks into one large volume."],
        [
            "PV -> VG -> LV -> filesystem.",
            "lvextend -r -L +20G vg0/data grows LV and filesystem online.",
            "RAID 1 mirror, RAID 5/6 parity, RAID 10 striped mirrors.",
            "cat /proc/mdstat for array health and rebuild progress.",
            "RAID is availability, not backup.",
        ],
        [
            ex("Build and grow an LVM volume", "intermediate", "Two disks, one volume group, a growable volume (real Linux).", "bash", """
                sudo pvcreate /dev/sdb /dev/sdc
                sudo vgcreate vg0 /dev/sdb /dev/sdc
                sudo lvcreate -L 50G -n data vg0
                sudo mkfs.ext4 /dev/vg0/data
                sudo pvs; sudo vgs; sudo lvs
                sudo lvextend -r -L +20G /dev/vg0/data
                sudo lvcreate -s -L 5G -n data-snap /dev/vg0/data    # snapshot before an upgrade
            """, runnable=False),
            ex("Mirror two disks with mdadm", "advanced", "Create, monitor and replace a failed member.", "bash", """
                sudo mdadm --create /dev/md0 --level=1 --raid-devices=2 /dev/sdd /dev/sde
                cat /proc/mdstat
                sudo mdadm --detail /dev/md0
                sudo mdadm --detail --scan | sudo tee -a /etc/mdadm/mdadm.conf
                sudo mdadm /dev/md0 --fail /dev/sde --remove /dev/sde
                sudo mdadm /dev/md0 --add /dev/sdf
                watch cat /proc/mdstat
            """, runnable=False),
        ],
        ["pvs · vgs · lvs", "lvcreate -L 50G -n name vg", "lvextend -r -L +10G vg/lv", "mdadm --detail /dev/md0", "cat /proc/mdstat"],
        ["LVM snapshots slow writes and become invalid if they fill up; remove them after use.", "RAID 5 rebuilds on large disks take long and stress remaining disks; RAID 6 or 10 is safer.", "Forgetting to update mdadm.conf and the initramfs can stop the array assembling at boot."],
        [
            qa("intermediate", "What are PV, VG and LV?", "Physical volumes are disks or partitions initialised for LVM, a volume group pools them, and logical volumes are flexible block devices carved from the group on which you create filesystems."),
            qa("intermediate", "How do you grow a filesystem on LVM?", "Add space to the VG if needed (pvcreate, vgextend), then lvextend -r -L +SIZE vg/lv, which grows the LV and resizes ext4 or XFS online."),
            qa("advanced", "RAID 5 vs RAID 10?", "RAID 5 stripes with one parity block, giving good capacity but slow writes and risky long rebuilds. RAID 10 stripes across mirrors: half the capacity, but faster writes and quicker, safer rebuilds."),
            qa("advanced", "Why is RAID not a backup?", "RAID copies every change instantly, including deletions, corruption and ransomware encryption. Backups are separate, versioned copies, ideally off-host and tested by restoring."),
        ],
        ["disks-storage", "filesystems-mount", "boot-process"],
        chain(
            ("Disks", "sdb, sdc", "Physical", "Raw disks are initialised as physical volumes."),
            ("PV", "pvcreate", "Prepare", "LVM metadata is written to each disk.", "init"),
            ("VG vg0", "pooled space", "Pool", "The PVs form one volume group.", "pool"),
            ("LV data", "lvcreate 50G", "Carve", "A logical volume is carved out and formatted.", "alloc"),
            ("lvextend -r", "+20G online", "Grow", "Later the LV and its filesystem grow without downtime.", "grow"),
        ),
    ),
    topic(
        "namespaces-cgroups", "Namespaces & cgroups in Depth", "internals", "advanced", "NC",
        "The two kernel features every container runtime is built on.",
        "An apartment building. Namespaces are the walls and private mailboxes: each flat has its own address (hostname), its own door numbers (PIDs) and its own phone line (network). cgroups are the utility meters and fuses: each flat gets so much electricity and water before the fuse trips.",
        "Namespaces give a process its own view of a global resource. The main types are pid (own process tree with its own PID 1), net (interfaces, routes, firewall, ports), mnt (mount table), uts (hostname), ipc, user (map container root to an unprivileged host uid) and cgroup and time. unshare creates new namespaces, nsenter joins existing ones (nsenter -t PID -n runs a host tool inside a container's network), and lsns lists them. Control groups v2 organise processes into a single hierarchy under /sys/fs/cgroup, where controllers enforce and account resources: memory.max and memory.high, cpu.max (quota/period) and cpu.weight, io.max, and pids.max against fork bombs. systemd places every service in its own cgroup (systemd-cgls, systemd-cgtop) and exposes limits as unit properties such as MemoryMax and CPUQuota. Container runtimes (runc, crun) combine namespaces, cgroups, capabilities, seccomp and an overlay root filesystem; Kubernetes requests and limits become cgroup settings on the node.",
        ["Debugging a container's network with host tools via nsenter.", "Limiting a noisy service's memory and CPU with systemd.", "Understanding Kubernetes limits, throttling and OOMKilled.", "Building rootless containers with user namespaces."],
        [
            "Namespaces isolate what a process can see; cgroups limit what it can use.",
            "lsns, nsenter -t PID -n -p, unshare --fork --pid --mount-proc.",
            "cgroup v2 files: memory.max, cpu.max, io.max, pids.max.",
            "systemd: MemoryMax=, CPUQuota=, TasksMax= per unit.",
            "User namespaces map container root to an unprivileged host uid.",
        ],
        [
            ex("Explore namespaces", "advanced", "List, create and enter namespaces (real Linux).", "bash", """
                lsns
                readlink /proc/self/ns/pid /proc/self/ns/net
                sudo unshare --fork --pid --mount-proc --uts bash -c 'hostname box; hostname; ps aux'
                pid=$(docker inspect -f '{{.State.Pid}}' web)
                sudo nsenter -t "$pid" -n ss -tlnp        # host ss inside the container's netns
                unshare --user --map-root-user id          # root inside, unprivileged outside
            """, runnable=False),
            ex("cgroup v2 limits through systemd", "advanced", "Inspect and cap a service's resources.", "bash", """
                systemd-cgls --no-pager | head -n 20
                systemd-cgtop -n 1
                sudo systemctl set-property myapp.service MemoryMax=512M CPUQuota=50% TasksMax=200
                cat /sys/fs/cgroup/system.slice/myapp.service/memory.max
                cat /sys/fs/cgroup/system.slice/myapp.service/memory.events
                cat /sys/fs/cgroup/system.slice/myapp.service/cpu.stat
            """, runnable=False),
        ],
        ["lsns · nsenter -t PID -n", "unshare --fork --pid --mount-proc", "systemd-cgls · systemd-cgtop", "systemctl set-property svc MemoryMax=", "cat /sys/fs/cgroup/.../memory.events"],
        ["Containers share the host kernel: a kernel exploit escapes all namespaces.", "Running containers as root without user namespaces means root in the container is root on the host for many resources.", "Tight CPU limits cause throttling and latency spikes even when the node is idle."],
        [
            qa("intermediate", "Which namespaces does a typical container use?", "pid, net, mnt, uts, ipc and cgroup, and optionally user. Together they give it its own process tree, network stack, filesystem view, hostname and IPC objects."),
            qa("advanced", "How do you run tcpdump or ss inside a container that lacks them?", "Find the container's host PID and use nsenter -t PID -n to enter only its network namespace while keeping the host's binaries and filesystem."),
            qa("advanced", "How do Kubernetes limits map to cgroups?", "The memory limit becomes memory.max for the container's cgroup, and the CPU limit becomes cpu.max quota per 100 ms period; CPU requests become cpu.weight. Exceeding memory.max triggers the OOM killer, exceeding the CPU quota causes throttling."),
            qa("advanced", "What do user namespaces add to security?", "They map uid 0 inside the container to an unprivileged uid range on the host, so a process that breaks out of the container still has no root privileges on the host."),
        ],
        ["kernel-internals", "memory-management", "selinux-apparmor"],
        chain(
            ("runc", "create", "Runtime", "The runtime prepares a new container process."),
            ("Namespaces", "pid net mnt uts", "Isolate", "clone() with new namespaces: own PID 1, network and mounts.", "clone"),
            ("cgroup", "memory.max cpu.max", "Limit", "The process joins a cgroup with memory and CPU limits.", "join"),
            ("Security", "caps, seccomp", "Harden", "Capabilities are dropped and a seccomp filter is applied.", "drop"),
            ("Process", "pid 1 in box", "Run", "The app runs isolated and limited on the shared kernel.", "exec"),
        ),
    ),
    topic(
        "kernel-modules-sysctl", "Kernel Modules & sysctl Tuning", "internals", "advanced", "KM",
        "Load drivers at runtime and tune kernel parameters safely and persistently.",
        "A modular synthesizer. The core keyboard (kernel) stays the same, you plug in modules for new sounds (drivers) when needed, and the knobs on the panel (sysctl) adjust behaviour live; writing the settings into the preset book (/etc/sysctl.d) keeps them after a power cycle.",
        "Much of the kernel is built as loadable modules (.ko files under /lib/modules/$(uname -r)): device drivers, filesystems, netfilter pieces. lsmod lists loaded modules, modinfo shows parameters, license and signature, and modprobe loads a module along with its dependencies (modprobe -r removes it). udev loads drivers automatically when hardware appears. Persistent choices go in /etc/modules-load.d (load at boot), /etc/modprobe.d (options, blacklist), and changes needed early in boot may require rebuilding the initramfs. With Secure Boot, modules must be signed by a trusted key. sysctl reads and writes tunables under /proc/sys: net.ipv4.ip_forward=1 for routing, net.core.somaxconn for listen backlogs, vm.swappiness, fs.file-max, kernel.pid_max. sysctl -w changes a value until reboot; files in /etc/sysctl.d/*.conf applied with sysctl --system make it persistent. Change one parameter at a time, record why, and prefer documented defaults unless measurements justify a change.",
        ["Enabling IP forwarding on a router or Kubernetes node.", "Loading br_netfilter and overlay for container networking.", "Raising connection backlogs on a busy web server.", "Blacklisting a buggy driver."],
        [
            "lsmod · modinfo name · modprobe name · modprobe -r name.",
            "/etc/modules-load.d to load at boot; /etc/modprobe.d for options and blacklists.",
            "sysctl -w key=value is temporary; /etc/sysctl.d/*.conf + sysctl --system persists.",
            "Secure Boot requires signed modules.",
            "Tune from measurements, one change at a time.",
        ],
        [
            ex("Which kernel is running?", "basic", "Release and full version string.", "bash", """
                uname -r
                uname -a
                cat /etc/os-release
            """),
            ex("Kubernetes node prerequisites", "intermediate", "Modules and sysctls every node needs (real Linux).", "bash", """
                lsmod | grep -E 'overlay|br_netfilter'
                printf 'overlay\\nbr_netfilter\\n' | sudo tee /etc/modules-load.d/k8s.conf
                sudo modprobe overlay && sudo modprobe br_netfilter
                printf 'net.ipv4.ip_forward = 1\\nnet.bridge.bridge-nf-call-iptables = 1\\n' | sudo tee /etc/sysctl.d/99-k8s.conf
                sudo sysctl --system
                sysctl net.ipv4.ip_forward
            """, runnable=False),
            ex("Inspect and tune", "advanced", "Module details, a temporary sysctl and a blacklist.", "bash", """
                modinfo e1000e | grep -E 'filename|version|signer|parm'
                sysctl net.core.somaxconn
                sudo sysctl -w net.core.somaxconn=4096        # until reboot
                echo 'blacklist nouveau' | sudo tee /etc/modprobe.d/blacklist-nouveau.conf
                sudo update-initramfs -u
            """, runnable=False),
        ],
        ["lsmod · modinfo mod", "modprobe mod · modprobe -r mod", "sysctl key · sysctl -w key=val", "/etc/sysctl.d/99-x.conf + sysctl --system", "/etc/modprobe.d/blacklist-x.conf"],
        ["sysctl -w values vanish on reboot unless also written to /etc/sysctl.d.", "Blindly copying 'performance sysctl' lists from blogs can hurt latency or stability.", "Unsigned or out-of-tree modules fail to load under Secure Boot and taint the kernel."],
        [
            qa("intermediate", "How do you load a kernel module at boot?", "Add its name to a file in /etc/modules-load.d/ (for example k8s.conf). Options go in /etc/modprobe.d/; modprobe name loads it immediately."),
            qa("intermediate", "How do you make a sysctl change permanent?", "Put key = value in a file under /etc/sysctl.d/ and run sysctl --system to apply all files. sysctl -w alone lasts only until reboot."),
            qa("advanced", "Why must Kubernetes nodes enable net.ipv4.ip_forward and br_netfilter?", "Pod traffic is routed between interfaces, which requires IP forwarding, and bridged pod traffic must pass through iptables or nftables so kube-proxy and network policies apply, which br_netfilter enables."),
            qa("advanced", "modprobe vs insmod?", "insmod loads a single .ko file by path and does not resolve dependencies. modprobe looks up modules by name in the module index (depmod), loads dependencies first and applies options from /etc/modprobe.d."),
        ],
        ["kernel-internals", "proc-sys", "boot-process"],
        chain(
            ("modprobe", "br_netfilter", "Request", "modprobe looks up the module by name."),
            ("depmod index", "dependencies", "Resolve", "Dependencies are found and loaded first.", "deps"),
            ("Kernel", "verify signature", "Load", "The kernel checks the signature and links the module in.", "insert"),
            ("sysctl", "/proc/sys/...", "Tune", "New tunables appear; sysctl sets them.", "write"),
            ("sysctl.d", "persist", "Persist", "A file in /etc/sysctl.d reapplies them every boot.", "save"),
        ),
    ),
]

TOPICS = _BATCH_1 + _BATCH_2 + _BATCH_3 + _BATCH_4

SCENARIOS = [
    {"level": "intermediate", "topic": "cron-timers", "q": "A backup script works when you run it by hand but silently does nothing from cron.", "a": "cron runs with a minimal environment: a short PATH, no .bashrc, a different working directory and no terminal. Redirect output to a log (>> /var/log/backup.log 2>&1) to see the error, use absolute paths and set needed variables, and escape % in the crontab line. Consider a systemd timer for journal logging and catch-up runs."},
    {"level": "advanced", "topic": "tls-openssl", "q": "Clients suddenly fail with certificate errors after a renewal.", "a": "Inspect the served chain with openssl s_client -connect host:443 -servername host -showcerts and the file with openssl x509 -text -noout -in cert.pem. Check notBefore and notAfter, that the SAN includes the hostname, that the intermediate is served, the key size (RSA 2048+ or EC P-256+) and a SHA-2 signature. Also confirm the client clock is correct."},
    {"level": "advanced", "topic": "troubleshooting-slow-server", "q": "Load average is 20 on an 8-core server, but CPU usage is only 15%.", "a": "Load includes tasks in uninterruptible sleep, so this is an I/O or network filesystem wait, not CPU. Check wa in top, ps for D-state processes, iostat -xz for a saturated device with high await and dmesg for disk or NFS errors, then find the process with iotop or pidstat -d."},
    {"level": "intermediate", "topic": "ssh-keys", "q": "SSH ignores your new key and still asks for a password.", "a": "Run ssh -v to see which keys are offered. Usually permissions are too open: ~/.ssh must be 700 and authorized_keys and private keys 600, and the home directory must not be group-writable. Also check the key is in the right user's authorized_keys and that sshd allows PubkeyAuthentication; the server's auth log shows the reason."},
    {"level": "advanced", "topic": "memory-management", "q": "A Java service is OOM-killed every few hours, but free -h shows plenty of available memory.", "a": "The kill comes from a cgroup limit, not host exhaustion. Check dmesg and the service's memory.events for oom_kill, compare memory.current with memory.max, and size the JVM to the limit (heap plus metaspace, threads and direct buffers, for example -XX:MaxRAMPercentage=75). Then look for a leak with heap dumps if usage keeps growing."},
    {"level": "intermediate", "topic": "dns-resolution", "q": "dig returns the new IP for a host, but the application still connects to the old one.", "a": "The app does not use dig's path. Check getent hosts name, which follows nsswitch.conf and may hit a stale /etc/hosts entry, systemd-resolved cache (resolvectl flush-caches) or an application-level cache such as the JVM's DNS cache. Wait for the TTL, flush caches or restart the app."},
]
