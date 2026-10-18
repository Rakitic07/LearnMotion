// A small, deterministic Linux shell simulator: virtual filesystem, permissions, pipes, redirection, processes and services.

const HOME = "/home/learner";
const GROUPS = { learner: ["learner", "sudo", "dev"], root: ["root"] };

const APP_LOG = `2026-10-17 09:00:01 INFO  server started on :8080
2026-10-17 09:00:04 INFO  connected to postgres
2026-10-17 09:01:12 WARN  slow query (812 ms) on /orders
2026-10-17 09:02:30 ERROR payment gateway timeout
2026-10-17 09:02:31 INFO  retrying payment
2026-10-17 09:03:45 ERROR payment gateway timeout
2026-10-17 09:05:00 INFO  health check ok
2026-10-17 09:06:10 WARN  cache miss ratio 41%
2026-10-17 09:07:22 ERROR disk usage above 90%
2026-10-17 09:08:00 INFO  user login alice
2026-10-17 09:08:30 INFO  user login bob
2026-10-17 09:09:15 ERROR null user id in /profile
2026-10-17 09:10:00 INFO  health check ok
`;
const ACCESS_LOG = `203.0.113.7 GET /index.html 200 5120
198.51.100.23 GET /login 200 2048
203.0.113.7 POST /login 302 128
192.0.2.44 GET /api/orders 200 8800
203.0.113.7 GET /api/orders 200 9100
198.51.100.23 GET /api/orders 500 312
203.0.113.7 GET /api/cart 200 1400
192.0.2.44 GET /api/cart 404 210
203.0.113.7 GET /logout 200 96
198.51.100.23 GET /index.html 200 5120
`;
const USERS_CSV = `id,name,city,role
1,Asha,Pune,admin
2,Ben,Berlin,dev
3,Chen,Pune,dev
4,Diya,Delhi,ops
5,Eli,Berlin,dev
6,Fatima,Delhi,admin
7,Gus,Pune,ops
`;

const DOCS = {
  pwd: "print the current directory", cd: "change directory", ls: "list files (-l long, -a hidden, -i inodes)", mkdir: "make directories (-p parents)",
  rmdir: "remove empty directories", touch: "create a file or update its time", echo: "print arguments", cat: "print files (-n numbers)",
  rm: "remove files (-r recursive, -f force)", cp: "copy (-r recursive)", mv: "move or rename", ln: "link files (-s symbolic)",
  chmod: "change mode: 755, u+x, go-w, +t", chown: "change owner (needs sudo)", umask: "show or set default permission mask",
  head: "first lines (-n N)", tail: "last lines (-n N, -n +N from line N)", wc: "count lines/words/bytes (-l -w -c)",
  grep: "search text (-i -v -n -c -r -o -E)", sort: "sort lines (-r -n -u -t X -k N)", uniq: "collapse duplicates (-c count)",
  cut: "select fields (-d X -f N)", tr: "translate characters (a-z A-Z, -d)", sed: "stream edit: s/a/b/g, /re/d, -n Np", awk: "fields: '{print $1}', -F, END",
  find: "find files: find . -name '*.log' -type f", xargs: "build commands from stdin", tee: "write to file and stdout (-a)",
  seq: "print a sequence", ps: "processes (ps aux)", kill: "send a signal: kill -9 PID", top: "process snapshot",
  whoami: "current user", id: "user and group ids", sudo: "run as root", env: "environment", export: "set a variable",
  history: "command history", which: "locate a command", man: "short help", stat: "file details incl. inode", file: "guess file type",
  du: "disk usage (-sh)", df: "filesystem usage (-h)", free: "memory usage (-h)", uname: "kernel info (-a)", hostname: "host name",
  uptime: "time since boot", date: "current date", systemctl: "services: status|start|stop|restart|enable|disable", journalctl: "service logs: -u unit -n N",
  ip: "network: ip addr, ip route", ss: "sockets: ss -tlnp", ping: "ping -c N host", curl: "HTTP client", dig: "DNS lookup",
  basename: "strip directory", dirname: "strip file name", tree: "directory tree", bash: "run a script", sh: "run a script",
  clear: "clear the screen", help: "list commands", set: "shell options (set -euo pipefail)", printf: "formatted print: printf '%s\\n' a b",
  unset: "remove a variable", less: "page through a file (prints it here)", more: "page through a file", nano: "editor (not simulated)", vim: "editor (not simulated)", true: "exit 0", false: "exit 1", sleep: "wait (instant here)", diff: "compare two files",
};

const fileNode = (content, mode = 0o644, owner = "learner", group = owner) => ({ type: "file", content, mode, owner, group });
const dirNode = (children = {}, mode = 0o755, owner = "learner", group = owner) => ({ type: "dir", children, mode, owner, group });

function seed() {
  const root = (c, mode = 0o755) => dirNode(c, mode, "root", "root");
  return root({
    bin: root({}), usr: root({ bin: root({}) }),
    etc: root({
      hostname: fileNode("learn\n", 0o644, "root", "root"),
      hosts: fileNode("127.0.0.1 localhost\n127.0.1.1 learn\n10.0.0.5 db.internal\n", 0o644, "root", "root"),
      passwd: fileNode("root:x:0:0:root:/root:/bin/bash\nwww-data:x:33:33:www-data:/var/www:/usr/sbin/nologin\nlearner:x:1000:1000:Learner:/home/learner:/bin/bash\n", 0o644, "root", "root"),
      shadow: fileNode("root:*:20000:0:99999:7:::\nlearner:!:20000:0:99999:7:::\n# password hashes live here; only root can read this file\n", 0o640, "root", "shadow"),
      "os-release": fileNode('NAME="Ubuntu"\nVERSION="24.04 LTS (Noble Numbat)"\nID=ubuntu\n', 0o644, "root", "root"),
      fstab: fileNode("UUID=1b2c-root  /      ext4  defaults  0 1\nUUID=7f3a-data  /data  xfs   defaults,noatime  0 2\n", 0o644, "root", "root"),
      nginx: root({ "nginx.conf": fileNode("worker_processes auto;\nevents { worker_connections 1024; }\nhttp {\n  server { listen 80; root /var/www/html; }\n}\n", 0o644, "root", "root") }),
    }),
    home: root({
      learner: dirNode({
        ".bashrc": fileNode("export EDITOR=vim\nalias ll='ls -la'\n"),
        ".ssh": dirNode({ id_demo: fileNode("demo key placeholder (not a real key)\n") }, 0o755),
        "notes.txt": fileNode("Linux is a kernel.\nEverything is a file.\nPipes connect small tools.\n"),
        "todo.txt": fileNode("learn pipes\nlearn permissions\nlearn systemd\nlearn pipes\n"),
        logs: dirNode({ "app.log": fileNode(APP_LOG), "access.log": fileNode(ACCESS_LOG) }),
        data: dirNode({ "users.csv": fileNode(USERS_CSV) }),
        scripts: dirNode({
          "backup.sh": fileNode("#!/bin/bash\n# copy notes into ~/backup\nmkdir -p ~/backup\ncp ~/notes.txt ~/backup/\necho \"backup done\"\n", 0o644),
          "hello.sh": fileNode('#!/bin/bash\nname=${1:-world}\necho "hello $name"\n', 0o755),
        }),
        tmp: dirNode({ "a.tmp": fileNode("x\n"), "b.tmp": fileNode("y\n"), "keep.txt": fileNode("keep me\n") }),
        "runaway.py": fileNode("while True:\n    pass\n"),
      }, 0o750),
    }),
    root: root({}, 0o700),
    tmp: root({}, 0o1777),
    var: root({
      log: root({ syslog: fileNode("Oct 17 09:00:00 learn systemd[1]: Started nginx.service\nOct 17 09:00:01 learn sshd[412]: Server listening on 0.0.0.0 port 22\n", 0o640, "root", "adm") }),
      www: root({ html: root({ "index.html": fileNode("<h1>Welcome to nginx</h1>\n", 0o644, "root", "root") }) }),
    }),
    dev: root({ null: fileNode("", 0o666, "root", "root") }),
  });
}

const modeStr = (n) => {
  const t = n.type === "dir" ? "d" : n.type === "link" ? "l" : "-";
  const m = n.mode;
  const tri = (v, special, ch) => `${v & 4 ? "r" : "-"}${v & 2 ? "w" : "-"}${special ? (v & 1 ? ch : ch.toUpperCase()) : v & 1 ? "x" : "-"}`;
  return t + tri((m >> 6) & 7, m & 0o4000, "s") + tri((m >> 3) & 7, m & 0o2000, "s") + tri(m & 7, m & 0o1000, "t");
};
export const permString = (mode, type = "file") => modeStr({ type, mode });

function globRe(p) {
  return new RegExp("^" + p.replace(/[.+^${}()|[\]\\]/g, "\\$&").replace(/\*/g, ".*").replace(/\?/g, ".") + "$");
}

class ShellError extends Error {}

export class ShellSim {
  constructor() {
    this.root = seed();
    this.inode = 1000;
    this.walkAll((n) => this.adopt(n));
    this.cwd = HOME;
    this.user = "learner";
    this.vars = { HOME, USER: "learner", SHELL: "/bin/bash", PATH: "/usr/local/bin:/usr/bin:/bin", LANG: "C.UTF-8" };
    this.umaskV = 0o022;
    this.last = 0;
    this.hist = [];
    this.services = { nginx: { active: true, enabled: true, port: 80 }, ssh: { active: true, enabled: true, port: 22 }, cron: { active: true, enabled: true }, backup: { active: false, enabled: false } };
    this.procs = [
      { pid: 1, user: "root", cpu: 0.0, mem: 0.3, cmd: "/sbin/init" },
      { pid: 412, user: "root", cpu: 0.0, mem: 0.2, cmd: "sshd: /usr/sbin/sshd -D", svc: "ssh" },
      { pid: 588, user: "root", cpu: 0.0, mem: 0.1, cmd: "/usr/sbin/cron -f", svc: "cron" },
      { pid: 733, user: "root", cpu: 0.0, mem: 0.4, cmd: "nginx: master process", svc: "nginx" },
      { pid: 734, user: "www-data", cpu: 0.3, mem: 0.6, cmd: "nginx: worker process", svc: "nginx" },
      { pid: 1201, user: "learner", cpu: 0.0, mem: 0.1, cmd: "-bash" },
      { pid: 1337, user: "learner", cpu: 99.2, mem: 1.2, cmd: "python3 runaway.py" },
    ];
    this.nextPid = 2000;
    this.journal = { nginx: ["Started nginx.service - A high performance web server."], ssh: ["Server listening on 0.0.0.0 port 22."], cron: ["Started cron.service."], backup: [] };
  }

  // ------------------------------------------------------------- filesystem
  adopt(n) {
    n.ino ??= ++this.inode;
    n.nlink ??= 1;
    n.mtime ??= "Oct 17 09:00";
  }
  walkAll(fn, n = this.root) {
    fn(n);
    if (n.type === "dir") Object.values(n.children).forEach((c) => this.walkAll(fn, c));
  }
  abs(p) {
    if (p === undefined || p === "") return this.cwd;
    if (p === "~" || p.startsWith("~/")) p = HOME + p.slice(1);
    const parts = (p.startsWith("/") ? p : `${this.cwd}/${p}`).split("/");
    const out = [];
    for (const s of parts) {
      if (!s || s === ".") continue;
      if (s === "..") out.pop();
      else out.push(s);
    }
    return "/" + out.join("/");
  }
  lookup(p, follow = true, depth = 0) {
    const path = this.abs(p);
    let n = this.root;
    const segs = path.split("/").filter(Boolean);
    for (let i = 0; i < segs.length; i++) {
      if (n.type === "link") n = this.lookup(n.target, true, depth + 1);
      if (!n || n.type !== "dir") return null;
      n = n.children[segs[i]];
      if (!n) return null;
      if (n.type === "link" && (follow || i < segs.length - 1)) {
        if (depth > 8) throw new ShellError("Too many levels of symbolic links");
        const base = "/" + segs.slice(0, i).join("/");
        n = this.lookup(n.target.startsWith("/") ? n.target : `${base}/${n.target}`, true, depth + 1);
        if (!n) return null;
      }
    }
    return n;
  }
  parent(p) {
    const path = this.abs(p);
    const i = path.lastIndexOf("/");
    const dir = this.lookup(path.slice(0, i) || "/");
    return { dir, name: path.slice(i + 1), path };
  }
  can(n, bit) {
    if (this.user === "root") return bit !== 1 || n.type === "dir" || (n.mode & 0o111) !== 0;
    if (n.owner === this.user) return ((n.mode >> 6) & bit) !== 0;
    if ((GROUPS[this.user] || []).includes(n.group)) return ((n.mode >> 3) & bit) !== 0;
    return (n.mode & bit) !== 0;
  }
  need(n, bit, path, cmd) {
    if (!this.can(n, bit)) throw new ShellError(`${cmd}: ${path}: Permission denied`);
  }
  read(p, cmd = "cat") {
    const n = this.lookup(p);
    if (!n) throw new ShellError(`${cmd}: ${p}: No such file or directory`);
    if (n.type === "dir") throw new ShellError(`${cmd}: ${p}: Is a directory`);
    this.need(n, 4, p, cmd);
    return n.content;
  }
  write(p, text, append = false, cmd = "bash") {
    if (this.abs(p) === "/dev/null") return;
    const existing = this.lookup(p);
    if (existing) {
      if (existing.type === "dir") throw new ShellError(`${cmd}: ${p}: Is a directory`);
      this.need(existing, 2, p, cmd);
      existing.content = append ? existing.content + text : text;
      existing.mtime = this.now();
      return;
    }
    const { dir, name } = this.parent(p);
    if (!dir || dir.type !== "dir") throw new ShellError(`${cmd}: ${p}: No such file or directory`);
    this.need(dir, 2, p, cmd);
    dir.children[name] = this.mk(fileNode(text, 0o666 & ~this.umaskV, this.user, this.user === "root" ? "root" : this.user));
  }
  mk(n) {
    this.adopt(n);
    n.mtime = this.now();
    return n;
  }
  now() {
    const d = new Date();
    return `${d.toLocaleString("en-US", { month: "short" })} ${String(d.getDate()).padStart(2)} ${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
  }
  sizeOf(n) {
    return n.type === "dir" ? 4096 : n.type === "link" ? n.target.length : new TextEncoder().encode(n.content).length;
  }

  // ------------------------------------------------------------- parsing
  expandVar(s, i) {
    if (s[i + 1] === "?") return [String(this.last), i + 2];
    if (s[i + 1] === "$") return ["1201", i + 2];
    if (s[i + 1] === "{") {
      const j = s.indexOf("}", i);
      if (j < 0) return ["$", i + 1];
      const inner = s.slice(i + 2, j);
      const m = /^(\w+)(?::-(.*))?$/.exec(inner);
      const v = m ? this.vars[m[1]] ?? "" : "";
      return [v === "" && m?.[2] !== undefined ? m[2] : v, j + 1];
    }
    const m = /^[A-Za-z_]\w*|^[0-9]/.exec(s.slice(i + 1));
    if (!m) return ["$", i + 1];
    return [this.vars[m[0]] ?? "", i + 1 + m[0].length];
  }
  scan(line) {
    const toks = [];
    let cur = null;
    let i = 0;
    const word = () => (cur ||= { v: "", q: false, glob: false });
    const push = () => {
      if (cur) toks.push({ t: "w", ...cur });
      cur = null;
    };
    while (i < line.length) {
      const c = line[i];
      if (c === " " || c === "\t") { push(); i++; continue; }
      if (c === "#" && !cur) break;
      if (line.startsWith("2>&1", i)) { push(); toks.push({ t: "op", v: "2>&1" }); i += 4; continue; }
      if (!cur && (line.startsWith("2>>", i) || line.startsWith("2>", i))) { const v = line.startsWith("2>>", i) ? "2>>" : "2>"; push(); toks.push({ t: "op", v }); i += v.length; continue; }
      const two = line.slice(i, i + 2);
      if (["&&", "||", ">>"].includes(two)) { push(); toks.push({ t: "op", v: two }); i += 2; continue; }
      if ("|;><&".includes(c)) { push(); toks.push({ t: "op", v: c }); i++; continue; }
      if (c === "'") {
        const j = line.indexOf("'", i + 1);
        if (j < 0) throw new ShellError("syntax error: unterminated quote");
        word().v += line.slice(i + 1, j);
        cur.q = true;
        i = j + 1;
        continue;
      }
      if (c === '"') {
        word().q = true;
        let j = i + 1;
        while (j < line.length && line[j] !== '"') {
          if (line[j] === "\\" && j + 1 < line.length) { cur.v += line[j + 1]; j += 2; continue; }
          if (line[j] === "$") { const [v, n] = this.expandVar(line, j); cur.v += v; j = n; continue; }
          cur.v += line[j++];
        }
        if (j >= line.length) throw new ShellError("syntax error: unterminated quote");
        i = j + 1;
        continue;
      }
      if (c === "\\") { word().v += line[i + 1] ?? ""; i += 2; continue; }
      if (c === "$") { const [v, n] = this.expandVar(line, i); word().v += v; i = n; continue; }
      if (c === "~" && !cur && (i + 1 >= line.length || "/ ".includes(line[i + 1]))) { word().v += HOME; i++; continue; }
      if (c === "*" || c === "?") word().glob = true;
      word().v += c;
      i++;
    }
    push();
    return toks;
  }
  glob(tok) {
    if (!tok.glob || tok.q) return [tok.v];
    const p = tok.v;
    const slash = p.lastIndexOf("/");
    const dirPart = slash >= 0 ? p.slice(0, slash + 1) : "";
    const pat = p.slice(slash + 1);
    const dir = this.lookup(dirPart || ".");
    if (!dir || dir.type !== "dir") return [p];
    const re = globRe(pat);
    const hits = Object.keys(dir.children).filter((n) => re.test(n) && (!n.startsWith(".") || pat.startsWith("."))).sort();
    return hits.length ? hits.map((h) => dirPart + h) : [p];
  }

  // ------------------------------------------------------------- execution
  /** Runs one input line; returns combined terminal text. */
  run(line, depth = 0) {
    if (depth === 0 && line.trim()) this.hist.push(line);
    let lists;
    try {
      lists = this.splitLists(line);
    } catch (e) {
      this.last = 2;
      return `bash: ${e.message}\n`;
    }
    let out = "";
    for (const { op, text } of lists) {
      if (op === "&&" && this.last !== 0) continue;
      if (op === "||" && this.last === 0) continue;
      let toks;
      try {
        toks = this.scan(text);
      } catch (e) {
        this.last = 2;
        return out + `bash: ${e.message}\n`;
      }
      if (toks.length) out += this.pipeline(toks, depth);
    }
    return out;
  }
  /** Splits on ; && || & outside quotes so each part is expanded only when it runs. */
  splitLists(line) {
    const parts = [];
    let op = null;
    let buf = "";
    let q = null;
    for (let i = 0; i < line.length; i++) {
      const c = line[i];
      if (q) {
        if (c === "\\" && q === '"') { buf += c + (line[i + 1] ?? ""); i++; continue; }
        if (c === q) q = null;
        buf += c;
        continue;
      }
      if (c === "'" || c === '"') { q = c; buf += c; continue; }
      if (c === "\\") { buf += c + (line[i + 1] ?? ""); i++; continue; }
      if (c === "#" && (!buf || /\s$/.test(buf))) break;
      const two = line.slice(i, i + 2);
      if (two === "&&" || two === "||") { parts.push({ op, text: buf }); op = two; buf = ""; i++; continue; }
      if (c === ";" || (c === "&" && line[i - 1] !== ">" && line[i + 1] !== ">")) { parts.push({ op, text: buf }); op = ";"; buf = ""; continue; }
      buf += c;
    }
    if (q) throw new ShellError("syntax error: unterminated quote");
    parts.push({ op, text: buf });
    return parts.filter((p) => p.text.trim());
  }
  pipeline(toks, depth) {
    const cmds = [[]];
    toks.forEach((t) => (t.t === "op" && t.v === "|" ? cmds.push([]) : cmds.at(-1).push(t)));
    let input = "";
    let term = "";
    for (let k = 0; k < cmds.length; k++) {
      const words = [];
      const redir = [];
      const ct = cmds[k];
      for (let i = 0; i < ct.length; i++) {
        const t = ct[i];
        if (t.t === "op") {
          if (t.v === "2>&1") { redir.push({ op: "2>&1" }); continue; }
          const target = ct[i + 1];
          if (!target || target.t !== "w") { this.last = 2; return term + "bash: syntax error near unexpected token\n"; }
          redir.push({ op: t.v, file: target.v });
          i++;
        } else words.push(...this.glob(t));
      }
      if (!words.length && !redir.length) { this.last = 2; return term + "bash: syntax error near unexpected token `|'\n"; }
      let stdin = k > 0 ? input : "";
      let res;
      try {
        const inR = redir.find((r) => r.op === "<");
        if (inR) stdin = this.read(inR.file, "bash");
        this.piping = k < cmds.length - 1 || redir.some((r) => r.op === ">" || r.op === ">>");
        res = this.exec(words, stdin, depth);
        this.piping = false;
      } catch (e) {
        if (!(e instanceof ShellError)) throw e;
        res = { out: "", err: e.message + "\n", code: 1 };
      }
      let { out = "", err = "", code = 0 } = res;
      try {
        const both = redir.some((r) => r.op === "2>&1");
        for (const r of redir) {
          if (r.op === ">" || r.op === ">>") {
            this.write(r.file, out + (both ? err : ""), r.op === ">>");
            out = "";
            if (both) err = "";
          } else if (r.op === "2>" || r.op === "2>>") {
            this.write(r.file, err, r.op === "2>>");
            err = "";
          }
        }
        if (both && err) { out += err; err = ""; }
      } catch (e) {
        if (!(e instanceof ShellError)) throw e;
        err += `bash: ${e.message.replace(/^bash: /, "")}\n`;
        code = 1;
      }
      term += err;
      input = out;
      this.last = code;
    }
    return term + input;
  }
  exec(words, stdin, depth) {
    let [cmd, ...args] = words;
    if (/^[A-Za-z_]\w*=/.test(cmd) && !args.length) {
      const i = cmd.indexOf("=");
      this.vars[cmd.slice(0, i)] = cmd.slice(i + 1);
      return {};
    }
    if (cmd === "sudo") {
      if (!args.length) return { err: "usage: sudo command\n", code: 1 };
      const prev = this.user;
      this.user = "root";
      try {
        return this.exec(args, stdin, depth);
      } finally {
        this.user = prev;
      }
    }
    if (cmd.includes("/") || ["bash", "sh"].includes(cmd)) return this.script(cmd, args, depth);
    const fn = this[`c_${cmd.replace(/-/g, "_")}`];
    if (!fn || !(cmd in DOCS)) return { err: `${cmd}: command not found\n`, code: 127 };
    return fn.call(this, args, stdin) || {};
  }
  script(cmd, args, depth) {
    let path = cmd;
    let viaShell = false;
    if (["bash", "sh"].includes(cmd)) {
      if (!args.length) return { err: "interactive subshells are not simulated\n", code: 1 };
      path = args.shift();
      viaShell = true;
    }
    const n = this.lookup(path);
    if (!n) return { err: `bash: ${path}: No such file or directory\n`, code: 127 };
    if (n.type === "dir") return { err: `bash: ${path}: Is a directory\n`, code: 126 };
    if (!viaShell && !this.can(n, 1)) return { err: `bash: ${path}: Permission denied\n`, code: 126 };
    this.need(n, 4, path, "bash");
    if (depth > 4) return { err: "bash: maximum script depth reached\n", code: 1 };
    const saved = { ...this.vars };
    args.forEach((a, i) => (this.vars[String(i + 1)] = a));
    this.vars["0"] = path;
    let out = "";
    let code = 0;
    for (const l of n.content.split("\n")) {
      if (!l.trim() || l.trim().startsWith("#")) continue;
      if (/^\s*exit\b/.test(l)) { code = +(l.trim().split(/\s+/)[1] || 0); break; }
      out += this.run(l, depth + 1);
      code = this.last;
      if (/^\s*set -e/.test(n.content) && code !== 0) break;
    }
    this.vars = { ...saved, ...Object.fromEntries(Object.entries(this.vars).filter(([k]) => !/^\d$/.test(k))) };
    return { out, code };
  }

  // ------------------------------------------------------------- helpers for commands
  flags(args, known) {
    const f = {};
    const rest = [];
    let stop = false;
    for (const a of args) {
      if (!stop && a === "--") { stop = true; continue; }
      if (!stop && /^-[A-Za-z]+$/.test(a) && [...a.slice(1)].every((c) => known.includes(c))) [...a.slice(1)].forEach((c) => (f[c] = true));
      else rest.push(a);
    }
    return [f, rest];
  }
  opt(args, name) {
    const i = args.indexOf(name);
    if (i < 0) {
      const j = args.findIndex((a) => a.startsWith(name) && a.length > name.length && name.length === 2);
      if (j < 0) return null;
      const v = args[j].slice(2);
      args.splice(j, 1);
      return v;
    }
    const v = args[i + 1];
    args.splice(i, 2);
    return v;
  }
  inputOf(files, stdin, cmd) {
    return files.length ? files.map((f) => this.read(f, cmd)).join("") : stdin;
  }
  lines(text) {
    const l = text.split("\n");
    if (l.at(-1) === "") l.pop();
    return l;
  }
  join(lines) {
    return lines.length ? lines.join("\n") + "\n" : "";
  }

  // ------------------------------------------------------------- commands
  c_pwd() { return { out: this.cwd + "\n" }; }
  c_cd([p]) {
    const target = this.abs(p ?? HOME);
    const n = this.lookup(target);
    if (!n) return { err: `bash: cd: ${p}: No such file or directory\n`, code: 1 };
    if (n.type !== "dir") return { err: `bash: cd: ${p}: Not a directory\n`, code: 1 };
    if (!this.can(n, 1)) return { err: `bash: cd: ${p}: Permission denied\n`, code: 1 };
    this.cwd = target;
    this.vars.PWD = target;
  }
  c_ls(args) {
    const [f, paths] = this.flags(args, "laihR1dt");
    const show = paths.length ? paths : ["."];
    const out = [];
    let err = "";
    const fmt = (name, n) => {
      const size = this.sizeOf(n);
      const sz = f.h && size >= 1024 ? (size / 1024).toFixed(1) + "K" : String(size);
      return `${f.i ? String(n.ino).padStart(5) + " " : ""}${modeStr(n)} ${n.nlink} ${n.owner.padEnd(8)} ${n.group.padEnd(8)} ${sz.padStart(5)} ${n.mtime} ${name}${n.type === "link" ? ` -> ${n.target}` : ""}`;
    };
    show.forEach((p) => {
      const n = this.lookup(p, false);
      if (!n) { err += `ls: cannot access '${p}': No such file or directory\n`; return; }
      const target = n.type === "link" ? this.lookup(p) : n;
      if (!target || target.type !== "dir" || f.d || (f.l && n.type === "link" && !p.endsWith("/"))) { out.push(f.l ? fmt(p, n) : p); return; }
      if (!this.can(target, 4)) { err += `ls: cannot open directory '${p}': Permission denied\n`; return; }
      if (show.length > 1) out.push(`${out.length ? "\n" : ""}${p}:`);
      const names = Object.keys(target.children).filter((x) => f.a || !x.startsWith(".")).sort();
      const all = f.a ? [".", "..", ...names] : names;
      if (f.l) {
        out.push(`total ${names.length * 4}`);
        all.forEach((x) => out.push(fmt(x, x === "." ? target : x === ".." ? this.lookup(this.abs(p) + "/..") : target.children[x])));
      } else if (all.length) out.push(f[1] || this.piping ? all.join("\n") : all.map((x) => (target.children[x]?.type === "dir" ? x + "/" : x)).join("  "));
    });
    return { out: this.join(out), err, code: err ? 2 : 0 };
  }
  c_mkdir(args) {
    const [f, paths] = this.flags(args, "p");
    let err = "";
    for (const p of paths) {
      const abs = this.abs(p);
      const segs = abs.split("/").filter(Boolean);
      for (let i = 1; i <= segs.length; i++) {
        const sub = "/" + segs.slice(0, i).join("/");
        const n = this.lookup(sub);
        const last = i === segs.length;
        if (n) {
          if (last && !f.p) err += `mkdir: cannot create directory '${p}': File exists\n`;
          if (n.type !== "dir") { err += `mkdir: '${sub}': Not a directory\n`; break; }
          continue;
        }
        if (!last && !f.p) { err += `mkdir: cannot create directory '${p}': No such file or directory\n`; break; }
        const { dir, name } = this.parent(sub);
        if (!this.can(dir, 2)) { err += `mkdir: cannot create directory '${p}': Permission denied\n`; break; }
        dir.children[name] = this.mk(dirNode({}, 0o777 & ~this.umaskV, this.user, this.user));
      }
    }
    return { err, code: err ? 1 : 0 };
  }
  c_rmdir(args) {
    for (const p of args) {
      const n = this.lookup(p, false);
      if (!n) return { err: `rmdir: failed to remove '${p}': No such file or directory\n`, code: 1 };
      if (n.type !== "dir") return { err: `rmdir: failed to remove '${p}': Not a directory\n`, code: 1 };
      if (Object.keys(n.children).length) return { err: `rmdir: failed to remove '${p}': Directory not empty\n`, code: 1 };
      const { dir, name } = this.parent(p);
      this.need(dir, 2, p, "rmdir");
      delete dir.children[name];
    }
  }
  c_touch(args) {
    for (const p of args) {
      const n = this.lookup(p);
      if (n) { this.need(n, 2, p, "touch"); n.mtime = this.now(); }
      else this.write(p, "", false, "touch");
    }
  }
  c_echo(args) {
    let nl = "\n";
    if (args[0] === "-n") { nl = ""; args = args.slice(1); }
    if (args[0] === "-e") args = args.slice(1).map((a) => a.replace(/\\n/g, "\n").replace(/\\t/g, "\t"));
    return { out: args.join(" ") + nl };
  }
  c_cat(args, stdin) {
    const [f, files] = this.flags(args, "n");
    let text = "";
    let err = "";
    if (!files.length) text = stdin;
    for (const p of files) {
      try { text += this.read(p); } catch (e) { err += e.message + "\n"; }
    }
    if (f.n) text = this.join(this.lines(text).map((l, i) => `${String(i + 1).padStart(6)}\t${l}`));
    return { out: text, err, code: err ? 1 : 0 };
  }
  removeNode(p, recursive, force, cmd = "rm") {
    const n = this.lookup(p, false);
    if (!n) {
      if (force) return;
      throw new ShellError(`${cmd}: cannot remove '${p}': No such file or directory`);
    }
    if (n.type === "dir" && !recursive) throw new ShellError(`${cmd}: cannot remove '${p}': Is a directory`);
    const { dir, name, path } = this.parent(p);
    if (path === "/" || path === HOME) throw new ShellError(`${cmd}: refusing to remove '${p}' in the simulator`);
    this.need(dir, 2, p, cmd);
    if ((dir.mode & 0o1000) && this.user !== "root" && n.owner !== this.user && dir.owner !== this.user) throw new ShellError(`${cmd}: cannot remove '${p}': Operation not permitted (sticky bit)`);
    n.nlink = Math.max(0, n.nlink - 1);
    delete dir.children[name];
  }
  c_rm(args) {
    const [f, paths] = this.flags(args, "rRfiv");
    let err = "";
    for (const p of paths) {
      try { this.removeNode(p, f.r || f.R, f.f); } catch (e) { err += e.message + "\n"; }
    }
    return { err, code: err ? 1 : 0 };
  }
  clone(n) {
    if (n.type === "dir") return this.mk(dirNode(Object.fromEntries(Object.entries(n.children).map(([k, c]) => [k, this.clone(c)])), n.mode, this.user, this.user));
    if (n.type === "link") return this.mk({ type: "link", target: n.target, mode: 0o777, owner: this.user, group: this.user });
    return this.mk(fileNode(n.content, n.mode, this.user, this.user));
  }
  place(src, dst, node, cmd) {
    const d = this.lookup(dst);
    let parent, name;
    if (d && d.type === "dir") {
      parent = d;
      name = this.abs(src).split("/").pop();
    } else {
      ({ dir: parent, name } = this.parent(dst));
      if (!parent || parent.type !== "dir") throw new ShellError(`${cmd}: cannot create '${dst}': No such file or directory`);
    }
    this.need(parent, 2, dst, cmd);
    parent.children[name] = node;
  }
  c_cp(args) {
    const [f, paths] = this.flags(args, "rRpav");
    if (paths.length < 2) return { err: "cp: missing destination file operand\n", code: 1 };
    const dst = paths.pop();
    for (const s of paths) {
      const n = this.lookup(s);
      if (!n) return { err: `cp: cannot stat '${s}': No such file or directory\n`, code: 1 };
      if (n.type === "dir" && !(f.r || f.R || f.a)) return { err: `cp: -r not specified; omitting directory '${s}'\n`, code: 1 };
      if (n.type === "file") this.need(n, 4, s, "cp");
      this.place(s, dst, this.clone(n), "cp");
    }
  }
  c_mv(args) {
    const [, paths] = this.flags(args, "fiv");
    if (paths.length < 2) return { err: "mv: missing destination file operand\n", code: 1 };
    const dst = paths.pop();
    for (const s of paths) {
      const n = this.lookup(s, false);
      if (!n) return { err: `mv: cannot stat '${s}': No such file or directory\n`, code: 1 };
      const { dir, name } = this.parent(s);
      this.need(dir, 2, s, "mv");
      this.place(s, dst, n, "mv");
      if (dir.children[name] === n && this.lookup(dst) !== dir) delete dir.children[name];
    }
  }
  c_ln(args) {
    const [f, paths] = this.flags(args, "sfnv");
    const target = paths[0];
    let linkName = paths[1];
    if (!target || !linkName) return { err: "ln: missing file operand\n", code: 1 };
    const existing = this.lookup(linkName, !f.n);
    if (existing?.type === "dir") linkName = `${linkName.replace(/\/$/, "")}/${target.split("/").filter(Boolean).pop()}`;
    if (this.lookup(linkName, false)) {
      if (!f.f) return { err: `ln: failed to create link '${linkName}': File exists\n`, code: 1 };
      this.removeNode(linkName, false, true, "ln");
    }
    const { dir, name } = this.parent(linkName);
    if (!dir) return { err: `ln: failed to create link '${linkName}': No such file or directory\n`, code: 1 };
    this.need(dir, 2, linkName, "ln");
    if (f.s) {
      dir.children[name] = this.mk({ type: "link", target, mode: 0o777, owner: this.user, group: this.user });
      return;
    }
    const n = this.lookup(target);
    if (!n) return { err: `ln: failed to access '${target}': No such file or directory\n`, code: 1 };
    if (n.type === "dir") return { err: `ln: ${target}: hard link not allowed for directory\n`, code: 1 };
    n.nlink++;
    dir.children[name] = n;
  }
  parseMode(spec, old, isDir) {
    if (/^[0-7]{3,4}$/.test(spec)) return parseInt(spec, 8);
    let mode = old;
    for (const part of spec.split(",")) {
      const m = /^([ugoa]*)([+\-=])([rwxXst]*)$/.exec(part);
      if (!m) throw new ShellError(`chmod: invalid mode: '${spec}'`);
      const who = m[1] || "a";
      const shifts = [...new Set([...who].flatMap((w) => (w === "a" ? [6, 3, 0] : [{ u: 6, g: 3, o: 0 }[w]])))];
      let bits = 0;
      for (const c of m[3]) {
        const v = c === "r" ? 4 : c === "w" ? 2 : c === "x" || (c === "X" && (isDir || old & 0o111)) ? 1 : 0;
        shifts.forEach((s) => (bits |= v << s));
        if (c === "s") bits |= (shifts.includes(6) ? 0o4000 : 0) | (shifts.includes(3) ? 0o2000 : 0);
        if (c === "t") bits |= 0o1000;
      }
      if (m[2] === "+") mode |= bits;
      else if (m[2] === "-") mode &= ~bits;
      else {
        const mask = shifts.reduce((a, s) => a | (7 << s), 0);
        mode = (mode & ~mask) | bits;
      }
    }
    return mode;
  }
  c_chmod(args) {
    const [f, rest] = this.flags(args, "Rv");
    const [spec, ...paths] = rest;
    if (!spec || !paths.length) return { err: "chmod: missing operand\n", code: 1 };
    const apply = (p, n) => {
      if (n.owner !== this.user && this.user !== "root") throw new ShellError(`chmod: changing permissions of '${p}': Operation not permitted`);
      n.mode = this.parseMode(spec, n.mode, n.type === "dir");
      if (f.R && n.type === "dir") Object.entries(n.children).forEach(([k, c]) => apply(`${p}/${k}`, c));
    };
    let err = "";
    for (const p of paths) {
      const n = this.lookup(p);
      if (!n) { err += `chmod: cannot access '${p}': No such file or directory\n`; continue; }
      try { apply(p, n); } catch (e) { err += e.message + "\n"; }
    }
    return { err, code: err ? 1 : 0 };
  }
  c_chown(args) {
    const [f, rest] = this.flags(args, "R");
    const [spec, ...paths] = rest;
    if (!spec || !paths.length) return { err: "chown: missing operand\n", code: 1 };
    if (this.user !== "root") return { err: `chown: changing ownership of '${paths[0]}': Operation not permitted\n`, code: 1 };
    const [owner, group] = spec.split(":");
    const apply = (n) => {
      if (owner) n.owner = owner;
      if (group) n.group = group;
      if (f.R && n.type === "dir") Object.values(n.children).forEach(apply);
    };
    for (const p of paths) {
      const n = this.lookup(p);
      if (!n) return { err: `chown: cannot access '${p}': No such file or directory\n`, code: 1 };
      apply(n);
    }
  }
  c_umask([v]) {
    if (!v) return { out: this.umaskV.toString(8).padStart(4, "0") + "\n" };
    if (!/^[0-7]{3,4}$/.test(v)) return { err: `bash: umask: ${v}: invalid octal number\n`, code: 1 };
    this.umaskV = parseInt(v, 8);
  }
  headTail(args, stdin, head) {
    let n = 10;
    let fromStart = false;
    const rest = [];
    for (let i = 0; i < args.length; i++) {
      const a = args[i];
      if (a === "-n") {
        const v = args[++i] || "10";
        fromStart = v.startsWith("+");
        n = parseInt(v, 10);
      } else if (/^-\d+$/.test(a)) n = +a.slice(1);
      else rest.push(a);
    }
    const ls = this.lines(this.inputOf(rest, stdin, head ? "head" : "tail"));
    return { out: this.join(head ? ls.slice(0, n) : fromStart ? ls.slice(Math.max(0, n - 1)) : ls.slice(-n)) };
  }
  c_head(args, stdin) { return this.headTail(args, stdin, true); }
  c_tail(args, stdin) { return this.headTail(args, stdin, false); }
  c_wc(args, stdin) {
    const [f, files] = this.flags(args, "lwc");
    const any = f.l || f.w || f.c;
    const row = (text, name) => {
      const cols = [];
      if (!any || f.l) cols.push((text.match(/\n/g) || []).length);
      if (!any || f.w) cols.push(text.split(/\s+/).filter(Boolean).length);
      if (!any || f.c) cols.push(new TextEncoder().encode(text).length);
      return (cols.length === 1 && !name ? String(cols[0]) : cols.map((c) => String(c).padStart(7)).join(" ")) + (name ? ` ${name}` : "");
    };
    if (!files.length) return { out: row(stdin) + "\n" };
    return { out: this.join(files.map((p) => row(this.read(p, "wc"), p))) };
  }
  c_grep(args, stdin) {
    const [f, rest] = this.flags(args, "ivncrlEoFwHhq");
    const pattern = rest.shift();
    if (pattern === undefined) return { err: "usage: grep [-ivncrloq] PATTERN [FILE...]\n", code: 2 };
    let re;
    try {
      const src = f.F ? pattern.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") : pattern.replace(/\\\|/g, "|").replace(/\\([(){}+?])/g, f.E ? "\\$1" : "$1");
      re = new RegExp(f.w ? `\\b(?:${src})\\b` : src, f.i ? "gi" : "g");
    } catch {
      return { err: `grep: invalid pattern '${pattern}'\n`, code: 2 };
    }
    const sources = [];
    let err = "";
    const add = (p) => {
      const n = this.lookup(p);
      if (!n) { err += `grep: ${p}: No such file or directory\n`; return; }
      if (n.type === "dir") {
        if (!f.r) { err += `grep: ${p}: Is a directory\n`; return; }
        Object.keys(n.children).sort().forEach((k) => add(`${p.replace(/\/$/, "")}/${k}`));
        return;
      }
      try { sources.push([p, this.read(p, "grep")]); } catch (e) { err += e.message + "\n"; }
    };
    if (rest.length) rest.forEach(add);
    else if (f.r) add(".");
    else sources.push([null, stdin]);
    const multi = (sources.length > 1 || f.r) && !f.h;
    const out = [];
    let total = 0;
    for (const [name, text] of sources) {
      let count = 0;
      this.lines(text).forEach((l, i) => {
        re.lastIndex = 0;
        const hit = re.test(l);
        if (hit === !!f.v) return;
        count++;
        if (f.c || f.l) return;
        const prefix = (multi && name ? `${name}:` : "") + (f.n ? `${i + 1}:` : "");
        if (f.o && !f.v) (l.match(re) || []).forEach((m) => out.push(prefix + m));
        else out.push(prefix + l);
      });
      total += count;
      if (f.c) out.push((multi && name ? `${name}:` : "") + count);
      if (f.l && count) out.push(name ?? "(standard input)");
    }
    return { out: f.q ? "" : this.join(out), err, code: err ? 2 : total ? 0 : 1 };
  }
  c_sort(args, stdin) {
    const [f, rest] = this.flags(args, "rnuf");
    const sep = this.opt(rest, "-t");
    const key = this.opt(rest, "-k");
    let ls = this.lines(this.inputOf(rest, stdin, "sort"));
    const field = (l) => {
      if (!key) return l;
      const k = parseInt(key, 10) - 1;
      const parts = sep ? l.split(sep) : l.trim().split(/\s+/);
      return parts.slice(k).join(sep || " ");
    };
    const cmp = f.n
      ? (a, b) => (parseFloat(field(a)) || 0) - (parseFloat(field(b)) || 0) || a.localeCompare(b)
      : (a, b) => (f.f ? field(a).toLowerCase() : field(a)) < (f.f ? field(b).toLowerCase() : field(b)) ? -1 : field(a) > field(b) ? 1 : 0;
    ls.sort(cmp);
    if (f.r) ls.reverse();
    if (f.u) ls = ls.filter((l, i) => i === 0 || field(l) !== field(ls[i - 1]));
    return { out: this.join(ls) };
  }
  c_uniq(args, stdin) {
    const [f, rest] = this.flags(args, "cdu");
    const ls = this.lines(this.inputOf(rest, stdin, "uniq"));
    const groups = [];
    ls.forEach((l) => (groups.length && groups.at(-1)[0] === l ? groups.at(-1)[1]++ : groups.push([l, 1])));
    const kept = groups.filter(([, n]) => (f.d ? n > 1 : f.u ? n === 1 : true));
    return { out: this.join(kept.map(([l, n]) => (f.c ? `${String(n).padStart(7)} ${l}` : l))) };
  }
  c_cut(args, stdin) {
    const rest = [...args];
    const d = this.opt(rest, "-d") ?? "\t";
    const spec = this.opt(rest, "-f");
    if (!spec) return { err: "cut: you must specify a list of fields (-f)\n", code: 1 };
    const want = (i) => spec.split(",").some((r) => {
      const [a, b] = r.split("-");
      const lo = a === "" ? 1 : +a;
      const hi = b === undefined ? lo : b === "" ? Infinity : +b;
      return i >= lo && i <= hi;
    });
    return { out: this.join(this.lines(this.inputOf(rest, stdin, "cut")).map((l) => (l.includes(d) ? l.split(d).filter((_, i) => want(i + 1)).join(d) : l))) };
  }
  c_tr(args, stdin) {
    const expand = (s) => s.replace(/(.)-(.)/g, (_, a, b) => Array.from({ length: b.charCodeAt(0) - a.charCodeAt(0) + 1 }, (_, i) => String.fromCharCode(a.charCodeAt(0) + i)).join("")).replace(/\\n/g, "\n");
    if (args[0] === "-d") {
      const set = new Set(expand(args[1] || ""));
      return { out: [...stdin].filter((c) => !set.has(c)).join("") };
    }
    if (args[0] === "-s") {
      const set = new Set(expand(args[1] || ""));
      return { out: [...stdin].filter((c, i, a) => !(set.has(c) && a[i - 1] === c)).join("") };
    }
    const [a, b] = [expand(args[0] || ""), expand(args[1] || "")];
    return { out: [...stdin].map((c) => { const i = a.indexOf(c); return i < 0 ? c : b[Math.min(i, b.length - 1)] ?? c; }).join("") };
  }
  c_sed(args, stdin) {
    const [f, rest] = this.flags(args, "nE");
    const script = rest.shift();
    if (!script) return { err: "usage: sed 's/old/new/g' [file]\n", code: 1 };
    const ls = this.lines(this.inputOf(rest, stdin, "sed"));
    let m;
    if ((m = /^s(.)(.*?)\1(.*?)\1([gi]*)$/.exec(script))) {
      const re = new RegExp(m[2].replace(/\\([(){}+?|])/g, f.E ? "\\$1" : "$1"), m[4].includes("g") ? (m[4].includes("i") ? "gi" : "g") : m[4].includes("i") ? "i" : "");
      const rep = m[3].replace(/\\(\d)/g, "$$$1").replace(/&/g, "$$&");
      return { out: this.join(ls.map((l) => l.replace(re, rep))) };
    }
    if ((m = /^\/(.*)\/d$/.exec(script))) return { out: this.join(ls.filter((l) => !new RegExp(m[1]).test(l))) };
    if ((m = /^\/(.*)\/p$/.exec(script)) && f.n) return { out: this.join(ls.filter((l) => new RegExp(m[1]).test(l))) };
    if ((m = /^(\d+)(?:,(\d+))?p$/.exec(script)) && f.n) return { out: this.join(ls.slice(+m[1] - 1, +(m[2] || m[1]))) };
    if ((m = /^(\d+)d$/.exec(script))) return { out: this.join(ls.filter((_, i) => i !== +m[1] - 1)) };
    return { err: `sed: unsupported script '${script}' (try s/a/b/g, /re/d, -n 'Np')\n`, code: 1 };
  }
  c_awk(args, stdin) {
    const rest = [...args];
    let fs = this.opt(rest, "-F");
    const prog = rest.shift();
    if (!prog) return { err: "usage: awk [-F sep] '{print $1}' [file]\n", code: 1 };
    const ls = this.lines(this.inputOf(rest, stdin, "awk"));
    const m = /^\s*(?:\/(.*?)\/|(\$\d+|NR|NF)\s*(==|!=|>=|<=|>|<)\s*("[^"]*"|[\d.]+))?\s*(?:\{(.*?)\})?\s*(?:END\s*\{(.*)\})?\s*$/.exec(prog);
    if (!m) return { err: "awk: this simulator supports: [/re/ | $N op value] {print ...} [END {print ...}]\n", code: 2 };
    const [, re, lhs, op, rhs, body = "print $0", end] = m;
    const vars = {};
    const out = [];
    const split = (l) => (fs ? l.split(fs === "\\t" ? "\t" : fs) : l.trim().split(/\s+/));
    const val = (tok, fields, nr) => {
      tok = tok.trim();
      if (tok === "$0") return fields.line;
      if (/^\$\d+$/.test(tok)) return fields[+tok.slice(1) - 1] ?? "";
      if (tok === "NR") return nr;
      if (tok === "NF") return fields.length;
      if (/^".*"$/.test(tok)) return tok.slice(1, -1);
      if (/^[\d.]+$/.test(tok)) return +tok;
      return vars[tok] ?? "";
    };
    const run = (stmts, fields, nr) => {
      for (const s of stmts.split(";").map((x) => x.trim()).filter(Boolean)) {
        let mm;
        if ((mm = /^print\s*(.*)$/.exec(s))) out.push((mm[1] || "$0").split(",").map((t) => t.trim().split(/\s+/).map((x) => val(x, fields, nr)).join("")).join(" "));
        else if ((mm = /^(\w+)\s*\+=\s*(.+)$/.exec(s))) vars[mm[1]] = (+vars[mm[1]] || 0) + (+val(mm[2], fields, nr) || 0);
        else if ((mm = /^(\w+)\+\+$/.exec(s))) vars[mm[1]] = (+vars[mm[1]] || 0) + 1;
        else throw new ShellError(`awk: unsupported statement '${s}'`);
      }
    };
    ls.forEach((line, i) => {
      const fields = split(line);
      fields.line = line;
      if (re !== undefined && !new RegExp(re).test(line)) return;
      if (lhs) {
        const a = val(lhs, fields, i + 1);
        const b = val(rhs, fields, i + 1);
        const [x, y] = typeof b === "number" ? [+a, b] : [String(a), b];
        const ok = { "==": x == y, "!=": x != y, ">": x > y, "<": x < y, ">=": x >= y, "<=": x <= y }[op];
        if (!ok) return;
      }
      if (m[5] !== undefined || !end) run(body, fields, i + 1);
    });
    if (end) { const fields = []; fields.line = ""; run(end, fields, ls.length); }
    return { out: this.join(out) };
  }
  c_find(args) {
    const rest = [...args];
    const start = rest[0] && !rest[0].startsWith("-") ? rest.shift() : ".";
    const name = this.opt(rest, "-name");
    const iname = this.opt(rest, "-iname");
    const type = this.opt(rest, "-type");
    const del = rest.includes("-delete");
    const root = this.lookup(start);
    if (!root) return { err: `find: '${start}': No such file or directory\n`, code: 1 };
    const out = [];
    const walk = (p, n) => {
      const base = p.split("/").pop();
      const okName = name ? globRe(name).test(base) : iname ? new RegExp(globRe(iname).source, "i").test(base) : true;
      const okType = !type || (type === "f" ? n.type === "file" : type === "d" ? n.type === "dir" : type === "l" ? n.type === "link" : true);
      if (okName && okType) out.push(p);
      if (n.type === "dir" && this.can(n, 4)) Object.keys(n.children).sort().forEach((k) => walk(`${p.replace(/\/$/, "")}/${k}`, n.children[k]));
    };
    walk(start, root);
    if (del) {
      out.reverse().forEach((p) => this.removeNode(p, true, true, "find"));
      return {};
    }
    return { out: this.join(out) };
  }
  c_xargs(args, stdin) {
    const items = stdin.split(/\s+/).filter(Boolean);
    const cmd = args.length ? args : ["echo"];
    const r = this.exec([...cmd, ...items], "", 1);
    return r;
  }
  c_tee(args, stdin) {
    const [f, files] = this.flags(args, "a");
    files.forEach((p) => this.write(p, stdin, f.a, "tee"));
    return { out: stdin };
  }
  c_seq(args) {
    const [a, b] = args.length > 1 ? [+args[0], +args[1]] : [1, +args[0]];
    if (!Number.isFinite(a) || !Number.isFinite(b) || b - a > 10000) return { err: "seq: invalid range\n", code: 1 };
    return { out: this.join(Array.from({ length: Math.max(0, b - a + 1) }, (_, i) => String(a + i))) };
  }
  liveProcs() {
    return this.procs.filter((p) => !p.svc || this.services[p.svc]?.active);
  }
  c_ps(args) {
    const all = args.some((a) => /a|e/.test(a));
    const list = all ? this.liveProcs() : this.liveProcs().filter((p) => p.user === "learner");
    if (args.some((a) => a.includes("u")) || all) {
      return { out: this.join(["USER         PID %CPU %MEM COMMAND", ...list.map((p) => `${p.user.padEnd(10)} ${String(p.pid).padStart(5)} ${p.cpu.toFixed(1).padStart(4)} ${p.mem.toFixed(1).padStart(4)} ${p.cmd}`)]) };
    }
    return { out: this.join(["    PID TTY          TIME CMD", ...list.map((p) => `${String(p.pid).padStart(7)} pts/0    00:00:${p.cpu > 50 ? "42" : "00"} ${p.cmd.split(" ")[0]}`)]) };
  }
  c_top() {
    const list = [...this.liveProcs()].sort((a, b) => b.cpu - a.cpu);
    const load = list.reduce((s, p) => s + p.cpu, 0) / 100;
    return { out: this.join([`top - load average: ${load.toFixed(2)}, ${(load * 0.8).toFixed(2)}, ${(load * 0.6).toFixed(2)}   (snapshot)`, "    PID USER      %CPU %MEM COMMAND", ...list.map((p) => `${String(p.pid).padStart(7)} ${p.user.padEnd(9)} ${p.cpu.toFixed(1).padStart(4)} ${p.mem.toFixed(1).padStart(4)} ${p.cmd}`)]) };
  }
  c_kill(args) {
    const sig = args[0]?.startsWith("-") ? args.shift().slice(1).toUpperCase() : "TERM";
    if (sig === "L") return { out: " 1) SIGHUP  2) SIGINT  9) SIGKILL 15) SIGTERM 18) SIGCONT 19) SIGSTOP\n" };
    let err = "";
    for (const a of args) {
      const p = this.liveProcs().find((x) => String(x.pid) === a);
      if (!p) { err += `bash: kill: (${a}) - No such process\n`; continue; }
      if (p.user !== this.user && this.user !== "root") { err += `bash: kill: (${a}) - Operation not permitted\n`; continue; }
      if (["19", "STOP", "SIGSTOP", "0"].includes(sig)) continue;
      if (p.pid === 1) { err += "bash: kill: (1) - init ignores this signal\n"; continue; }
      if (p.svc) {
        this.services[p.svc].active = false;
        this.journal[p.svc].push(`${p.svc}.service: Main process exited, code=killed, status=${sig === "9" || sig === "KILL" ? "9/KILL" : "15/TERM"}`);
      } else this.procs = this.procs.filter((x) => x !== p);
    }
    return { err, code: err ? 1 : 0 };
  }
  c_whoami() { return { out: this.user + "\n" }; }
  c_id() {
    return { out: this.user === "root" ? "uid=0(root) gid=0(root) groups=0(root)\n" : "uid=1000(learner) gid=1000(learner) groups=1000(learner),27(sudo),1001(dev)\n" };
  }
  c_env() { return { out: this.join(Object.entries(this.vars).filter(([k]) => !/^\d$/.test(k)).map(([k, v]) => `${k}=${v}`)) }; }
  c_export(args) {
    if (!args.length) return this.c_env();
    for (const a of args) {
      const i = a.indexOf("=");
      if (i > 0) this.vars[a.slice(0, i)] = a.slice(i + 1);
    }
  }
  c_history() { return { out: this.join(this.hist.map((h, i) => `${String(i + 1).padStart(5)}  ${h}`)) }; }
  c_which(args) {
    return { out: this.join(args.filter((a) => a in DOCS).map((a) => `/usr/bin/${a}`)), code: args.every((a) => a in DOCS) ? 0 : 1 };
  }
  c_man([c]) {
    return c in DOCS ? { out: `${c} - ${DOCS[c]}\n` } : { err: `No manual entry for ${c || ""}\n`, code: 16 };
  }
  c_help() {
    return { out: "Simulated commands:\n" + this.join(Object.keys(DOCS).sort().map((k) => `  ${k.padEnd(11)} ${DOCS[k]}`)) + "Plus: pipes |, > >> < 2> 2>&1, && || ;, $VAR, globs *.log, ./script.sh, sudo.\n" };
  }
  c_stat([p]) {
    const n = this.lookup(p ?? "", false);
    if (!p || !n) return { err: `stat: cannot statx '${p ?? ""}': No such file or directory\n`, code: 1 };
    const kind = n.type === "dir" ? "directory" : n.type === "link" ? "symbolic link" : n.content ? "regular file" : "regular empty file";
    return { out: `  File: ${p}${n.type === "link" ? ` -> ${n.target}` : ""}\n  Size: ${this.sizeOf(n)}\t\t${kind}\n Inode: ${n.ino}\tLinks: ${n.nlink}\nAccess: (${(n.mode & 0o7777).toString(8).padStart(4, "0")}/${modeStr(n)})  Uid: ${n.owner}  Gid: ${n.group}\nModify: ${n.mtime}\n` };
  }
  c_file(paths) {
    if (!paths.length) return { err: "Usage: file FILE...\n", code: 1 };
    const out = paths.map((p) => {
      const n = this.lookup(p);
      if (!n) return `${p}: cannot open (No such file or directory)`;
      if (n.type === "dir") return `${p}: directory`;
      if (p.startsWith("/dev/")) return `${p}: character special`;
      const c = n.content;
      return `${p}: ${c.startsWith("#!/bin/bash") ? "Bourne-Again shell script, ASCII text executable" : c.startsWith("<") ? "HTML document, ASCII text" : !c ? "empty" : "ASCII text"}`;
    });
    return { out: this.join(out) };
  }
  c_du(args) {
    const [f, paths] = this.flags(args, "sh");
    const size = (n) => (n.type === "dir" ? 4096 + Object.values(n.children).reduce((s, c) => s + size(c), 0) : this.sizeOf(n));
    return { out: this.join((paths.length ? paths : ["."]).map((p) => {
      const n = this.lookup(p);
      if (!n) return `du: cannot access '${p}'`;
      const b = size(n);
      return `${f.h ? (b / 1024).toFixed(1) + "K" : Math.ceil(b / 1024)}\t${p}`;
    })) };
  }
  c_df() {
    return { out: "Filesystem      Size  Used Avail Use% Mounted on\n/dev/sda1        40G   36G  4.0G  90% /\n/dev/sdb1       200G   61G  139G  31% /data\ntmpfs           2.0G     0  2.0G   0% /dev/shm\n" };
  }
  c_free() {
    return { out: "               total        used        free      shared  buff/cache   available\nMem:           7.7Gi       3.1Gi       1.2Gi       112Mi       3.4Gi       4.3Gi\nSwap:          2.0Gi          0B       2.0Gi\n" };
  }
  c_uname(args) { return { out: args.includes("-a") ? "Linux learn 6.8.0-45-generic #45-Ubuntu SMP PREEMPT_DYNAMIC x86_64 GNU/Linux\n" : args.includes("-r") ? "6.8.0-45-generic\n" : "Linux\n" }; }
  c_hostname() { return { out: "learn\n" }; }
  c_uptime() { return { out: ` ${this.now().slice(-5)}:00 up 3 days,  4:12,  1 user,  load average: ${(this.liveProcs().reduce((s, p) => s + p.cpu, 0) / 100).toFixed(2)}, 0.80, 0.61\n` }; }
  c_date() { return { out: new Date().toString().replace(/ \(.*\)$/, "") + "\n" }; }
  c_basename([p = ""]) { return { out: p.replace(/\/+$/, "").split("/").pop() + "\n" }; }
  c_dirname([p = ""]) { const i = p.replace(/\/+$/, "").lastIndexOf("/"); return { out: (i < 0 ? "." : i === 0 ? "/" : p.slice(0, i)) + "\n" }; }
  c_set() { return {}; }
  c_unset(args) { args.forEach((a) => delete this.vars[a]); }
  c_less(args, stdin) { return this.c_cat(args, stdin); }
  c_more(args, stdin) { return this.c_cat(args, stdin); }
  c_nano() { return { err: "editors are not simulated: use  echo 'text' > file  or  cat >> file\n", code: 1 }; }
  c_vim() { return this.c_nano(); }
  c_printf([fmt = "", ...rest]) {
    const f = fmt.replace(/\\n/g, "\n").replace(/\\t/g, "\t");
    const slots = (f.match(/%[sd]/g) || []).length;
    if (!slots) return { out: f };
    let out = "";
    for (let i = 0; i < Math.max(1, Math.ceil(rest.length / slots)); i++) {
      let k = 0;
      out += f.replace(/%[sd]/g, () => rest[i * slots + k++] ?? "");
    }
    return { out };
  }
  c_true() { return { code: 0 }; }
  c_false() { return { code: 1 }; }
  c_sleep() { return {}; }
  c_clear() { return {}; }
  c_diff([a, b]) {
    if (!a || !b) return { err: "diff: missing operand\n", code: 2 };
    const x = this.lines(this.read(a, "diff"));
    const y = this.lines(this.read(b, "diff"));
    const out = [];
    const max = Math.max(x.length, y.length);
    for (let i = 0; i < max; i++) {
      if (x[i] === y[i]) continue;
      out.push(`${i + 1}c${i + 1}`);
      if (x[i] !== undefined) out.push(`< ${x[i]}`);
      out.push("---");
      if (y[i] !== undefined) out.push(`> ${y[i]}`);
    }
    return { out: this.join(out), code: out.length ? 1 : 0 };
  }
  c_tree([p = "."]) {
    const n = this.lookup(p);
    if (!n || n.type !== "dir") return { err: `${p} [error opening dir]\n`, code: 2 };
    const out = [p];
    let dirs = 0, files = 0;
    const walk = (d, prefix) => {
      const names = Object.keys(d.children).filter((k) => !k.startsWith(".")).sort();
      names.forEach((k, i) => {
        const c = d.children[k];
        const lastOne = i === names.length - 1;
        out.push(`${prefix}${lastOne ? "└── " : "├── "}${k}${c.type === "link" ? ` -> ${c.target}` : ""}`);
        if (c.type === "dir") { dirs++; if (this.can(c, 4)) walk(c, prefix + (lastOne ? "    " : "│   ")); } else files++;
      });
    };
    walk(n, "");
    out.push("", `${dirs} directories, ${files} files`);
    return { out: this.join(out) };
  }
  c_systemctl(args) {
    const [action, unitRaw] = args;
    const unit = unitRaw?.replace(/\.(service|timer)$/, "");
    if (action === "list-units" || !action) {
      return { out: this.join(["UNIT              ACTIVE   SUB      DESCRIPTION", ...Object.entries(this.services).map(([k, s]) => `${(k + ".service").padEnd(17)} ${(s.active ? "active" : "inactive").padEnd(8)} ${(s.active ? "running" : "dead").padEnd(8)} ${k}`)]) };
    }
    const s = this.services[unit];
    if (!s) return { err: `Unit ${unitRaw}.service could not be found.\n`, code: 4 };
    if (action === "status" || action === "is-active" || action === "is-enabled") {
      if (action === "is-active") return { out: (s.active ? "active" : "inactive") + "\n", code: s.active ? 0 : 3 };
      if (action === "is-enabled") return { out: (s.enabled ? "enabled" : "disabled") + "\n", code: s.enabled ? 0 : 1 };
      return { out: `● ${unit}.service\n     Loaded: loaded (/lib/systemd/system/${unit}.service; ${s.enabled ? "enabled" : "disabled"})\n     Active: ${s.active ? "active (running)" : "inactive (dead)"}\n${this.join((this.journal[unit] || []).slice(-3).map((l) => `Oct 17 learn ${unit}: ${l}`))}`, code: s.active ? 0 : 3 };
    }
    if (this.user !== "root") return { err: `Failed to ${action} ${unit}.service: Access denied (try sudo)\n`, code: 1 };
    if (action === "start" || action === "restart") { s.active = true; this.journal[unit].push(`Started ${unit}.service.`); }
    else if (action === "stop") { s.active = false; this.journal[unit].push(`Stopped ${unit}.service.`); }
    else if (action === "enable") { s.enabled = true; return { out: `Created symlink /etc/systemd/system/multi-user.target.wants/${unit}.service.\n` }; }
    else if (action === "disable") { s.enabled = false; return { out: `Removed /etc/systemd/system/multi-user.target.wants/${unit}.service.\n` }; }
    else if (action === "reload" || action === "daemon-reload") return {};
    else return { err: `Unknown command verb ${action}.\n`, code: 1 };
  }
  c_journalctl(args) {
    const rest = [...args];
    const unit = this.opt(rest, "-u")?.replace(/\.service$/, "");
    const n = +(this.opt(rest, "-n") || 20);
    const lines = unit ? (this.journal[unit] || []).map((l) => `Oct 17 learn ${unit}[${unit.length * 100}]: ${l}`) : Object.entries(this.journal).flatMap(([k, ls]) => ls.map((l) => `Oct 17 learn ${k}: ${l}`));
    return { out: this.join(lines.slice(-n)) || "-- No entries --\n" };
  }
  c_ip([sub]) {
    if (sub === "route" || sub === "r") return { out: "default via 10.0.0.1 dev eth0 proto dhcp\n10.0.0.0/24 dev eth0 proto kernel scope link src 10.0.0.12\n" };
    return { out: "1: lo: <LOOPBACK,UP> mtu 65536\n    inet 127.0.0.1/8 scope host lo\n2: eth0: <BROADCAST,MULTICAST,UP> mtu 1500\n    inet 10.0.0.12/24 brd 10.0.0.255 scope global eth0\n" };
  }
  c_ss() {
    const rows = Object.entries(this.services).filter(([, s]) => s.port && s.active).map(([k, s]) => `LISTEN 0      511    0.0.0.0:${String(s.port).padEnd(5)}  0.0.0.0:*   users:(("${k === "ssh" ? "sshd" : k}"))`);
    return { out: this.join(["State  Recv-Q Send-Q Local Address:Port  Peer Address:Port Process", ...rows]) };
  }
  c_ping(args) {
    const rest = [...args];
    const count = +(this.opt(rest, "-c") || 3);
    const host = rest[0];
    if (!host) return { err: "ping: usage error: Destination address required\n", code: 1 };
    if (host === "10.0.0.99") return { out: `PING ${host}: 56 data bytes\n\n--- ${host} ping statistics ---\n${count} packets transmitted, 0 received, 100% packet loss\n`, code: 1 };
    const ip = host === "localhost" ? "127.0.0.1" : host === "db.internal" ? "10.0.0.5" : /^\d/.test(host) ? host : "93.184.215.14";
    return { out: `PING ${host} (${ip}) 56(84) bytes of data.\n${this.join(Array.from({ length: Math.min(count, 10) }, (_, i) => `64 bytes from ${ip}: icmp_seq=${i + 1} ttl=56 time=${(host.includes("local") ? 0.04 : 11 + i * 0.7).toFixed(1)} ms`))}\n--- ${host} ping statistics ---\n${count} packets transmitted, ${count} received, 0% packet loss\n` };
  }
  c_curl(args) {
    const url = args.filter((a) => !a.startsWith("-")).pop() || "";
    const head = args.includes("-I") || args.includes("-i");
    if (/localhost|127\.0\.0\.1/.test(url)) {
      if (!this.services.nginx.active) return { err: `curl: (7) Failed to connect to localhost port 80: Connection refused\n`, code: 7 };
      return { out: (head ? "HTTP/1.1 200 OK\nServer: nginx\nContent-Type: text/html\n\n" : "") + (args.includes("-I") ? "" : this.lookup("/var/www/html/index.html")?.content ?? "") };
    }
    if (!url) return { err: "curl: no URL specified\n", code: 2 };
    return { err: `curl: (6) Could not resolve host: ${url.replace(/^https?:\/\//, "").split("/")[0]} (the simulator has no internet)\n`, code: 6 };
  }
  c_dig(args) {
    const host = args.find((a) => !a.startsWith("+") && !a.startsWith("-")) || "";
    const ip = host === "db.internal" ? "10.0.0.5" : "93.184.215.14";
    return { out: `;; QUESTION SECTION:\n;${host}.\t\tIN\tA\n\n;; ANSWER SECTION:\n${host}.\t300\tIN\tA\t${ip}\n\n;; Query time: 12 msec\n;; SERVER: 127.0.0.53#53\n` };
  }
}

export { HOME, DOCS };
