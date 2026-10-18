import { $, $$, esc, store, toast } from "../util.js";
import { HOME, ShellSim, permString } from "./shellsim.js";
import { labHero, takeHandoff } from "./common.js";

const shortPath = (p) => (p === HOME ? "~" : p.startsWith(HOME + "/") ? "~" + p.slice(HOME.length) : p);

/** Terminal bound to a ShellSim; onChange(sim, lastOutput) runs after every command. */
function terminal(root, { onChange, quick = [] } = {}) {
  root.insertAdjacentHTML("beforeend", `
    <div class="panel clay term">
      <div class="term-log" id="tlog"></div>
      <form class="term-in" id="tform"><span class="prompt" id="prompt"></span><input id="tinput" autocomplete="off" spellcheck="false" autocapitalize="off" placeholder="ls -la" aria-label="shell command"></form>
      ${quick.length ? `<div class="row quick">${quick.map((q) => `<button type="button" class="btn small" data-cmd="${esc(q)}">${esc(q)}</button>`).join("")}</div>` : ""}
    </div>`);
  let sim = new ShellSim();
  const hist = [];
  let hpos = 0;
  const logEl = $("#tlog", root);
  const promptText = () => `${sim.user}@learn:${shortPath(sim.cwd)}${sim.user === "root" ? "#" : "$"}`;
  const print = (cmd, out) => {
    logEl.insertAdjacentHTML("beforeend", `${cmd !== null ? `<div class="t-cmd"><span class="prompt">${esc(promptText())}</span> ${esc(cmd)}</div>` : ""}${out ? `<pre class="t-out">${esc(out.replace(/\n$/, ""))}</pre>` : ""}`);
    logEl.scrollTop = logEl.scrollHeight;
  };
  const draw = (last = "") => {
    $("#prompt", root).textContent = promptText();
    onChange?.(sim, last);
  };
  const run = (line) => {
    const cmd = line.trim();
    if (!cmd) return;
    if (cmd === "clear") {
      logEl.innerHTML = "";
      sim.hist.push(cmd);
      return draw();
    }
    const before = promptText();
    const out = sim.run(cmd);
    logEl.insertAdjacentHTML("beforeend", `<div class="t-cmd"><span class="prompt">${esc(before)}</span> ${esc(cmd)}</div>${out ? `<pre class="t-out ${sim.last !== 0 ? "bad" : ""}">${esc(out.replace(/\n$/, ""))}</pre>` : ""}`);
    logEl.scrollTop = logEl.scrollHeight;
    draw(out);
  };
  $("#tform", root).onsubmit = (e) => {
    e.preventDefault();
    const v = $("#tinput", root).value;
    if (!v.trim()) return;
    hist.push(v);
    hpos = hist.length;
    $("#tinput", root).value = "";
    run(v);
  };
  $("#tinput", root).onkeydown = (e) => {
    if (e.key === "ArrowUp" && hpos > 0) $("#tinput", root).value = hist[--hpos];
    else if (e.key === "ArrowDown") $("#tinput", root).value = hpos < hist.length - 1 ? hist[++hpos] : ((hpos = hist.length), "");
    else if (e.key === "Tab") {
      const input = $("#tinput", root);
      const m = /(\S*)$/.exec(input.value);
      const word = m[1];
      const slash = word.lastIndexOf("/");
      const dir = sim.lookup(slash >= 0 ? word.slice(0, slash + 1) || "/" : ".");
      const pre = word.slice(slash + 1);
      const hits = dir?.type === "dir" ? Object.keys(dir.children).filter((n) => n.startsWith(pre)) : [];
      if (hits.length === 1) {
        const child = dir.children[hits[0]];
        input.value = input.value.slice(0, input.value.length - pre.length) + hits[0] + (child.type === "dir" ? "/" : " ");
      } else if (hits.length > 1) print(null, hits.join("  "));
    } else return;
    e.preventDefault();
  };
  root.addEventListener("click", (e) => {
    const c = e.target.closest("[data-cmd]")?.dataset.cmd;
    if (!c) return;
    const input = $("#tinput", root);
    if (c.endsWith(" ")) {
      input.value = c;
      input.focus();
    } else run(c);
  });
  draw();
  return {
    run,
    print,
    get sim() { return sim; },
    reset(setup = []) {
      sim = new ShellSim();
      setup.forEach((l) => sim.run(l));
      sim.hist = [];
      logEl.innerHTML = "";
      draw();
    },
  };
}

// ===================================================================== file tree + permission calculator
function treeHtml(sim, path = HOME, depth = 0) {
  const n = sim.lookup(path, false);
  if (!n) return "";
  const kids = n.type === "dir" ? Object.keys(n.children).sort((a, b) => (n.children[b].type === "dir") - (n.children[a].type === "dir") || a.localeCompare(b)) : [];
  return kids.map((k) => {
    const c = n.children[k];
    const p = `${path === "/" ? "" : path}/${k}`;
    const here = sim.cwd === p;
    const icon = c.type === "dir" ? "▸" : c.type === "link" ? "↪" : c.mode & 0o111 ? "⚙" : "·";
    const row = `<div class="ft-row ${c.type} ${here ? "here" : ""}" style="--d:${depth}" data-path="${esc(p)}" data-kind="${c.type}">
      <span class="ft-ic">${icon}</span><span class="ft-name">${esc(k)}${c.type === "link" ? ` <small>→ ${esc(c.target)}</small>` : ""}</span><code class="ft-mode">${permString(c.mode, c.type)}</code></div>`;
    return row + (c.type === "dir" && depth < 3 && sim.can(c, 4) ? treeHtml(sim, p, depth + 1) : "");
  }).join("");
}

const WHO = [["u", "Owner", 6], ["g", "Group", 3], ["o", "Others", 0]];
const BITS = [["r", 4], ["w", 2], ["x", 1]];
function permCalc(root) {
  let mode = 0o644;
  let umask = 0o022;
  root.innerHTML = `
    <h3>Permission calculator</h3>
    <div class="perm-grid">
      <span></span>${BITS.map(([b]) => `<b>${b}</b>`).join("")}
      ${WHO.map(([w, label, s]) => `<span>${label}</span>${BITS.map(([b, v]) => `<label class="perm-bit"><input type="checkbox" data-bit="${v << s}" aria-label="${label} ${b}"><i></i></label>`).join("")}`).join("")}
    </div>
    <div class="row perm-special">
      <label class="check"><input type="checkbox" data-bit="${0o4000}"> setuid</label>
      <label class="check"><input type="checkbox" data-bit="${0o2000}"> setgid</label>
      <label class="check"><input type="checkbox" data-bit="${0o1000}"> sticky</label>
    </div>
    <div class="perm-out">
      <label>Octal<input type="text" id="permOct" maxlength="4" inputmode="numeric"></label>
      <div><span class="muted">ls -l</span><code id="permSym"></code></div>
      <div><span class="muted">command</span><code id="permCmd"></code></div>
    </div>
    <p class="muted perm-explain" id="permExplain"></p>
    <hr>
    <label>umask<input type="text" id="umaskIn" maxlength="4" value="022"></label>
    <p class="muted" id="umaskOut"></p>`;
  const draw = () => {
    $$("[data-bit]", root).forEach((i) => (i.checked = (mode & +i.dataset.bit) !== 0));
    const oct = (mode & 0o7777).toString(8).padStart(mode > 0o777 ? 4 : 3, "0");
    if (document.activeElement !== $("#permOct", root)) $("#permOct", root).value = oct;
    $("#permSym", root).textContent = permString(mode);
    $("#permCmd", root).textContent = `chmod ${oct} file`;
    const say = (s) => [s & 4 && "read", s & 2 && "write", s & 1 && "execute"].filter(Boolean).join(", ") || "nothing";
    $("#permExplain", root).textContent = `Owner can ${say(mode >> 6 & 7)}; group can ${say(mode >> 3 & 7)}; others can ${say(mode & 7)}.${mode & 0o4000 ? " setuid: runs with the owner's privileges (like passwd)." : ""}${mode & 0o1000 ? " sticky: in a shared dir, only owners may delete their files (like /tmp)." : ""}`;
    $("#umaskOut", root).innerHTML = `New files get <code>${(0o666 & ~umask).toString(8).padStart(3, "0")}</code> (${permString(0o666 & ~umask)}), new directories <code>${(0o777 & ~umask).toString(8).padStart(3, "0")}</code> (${permString(0o777 & ~umask, "dir")}).`;
  };
  root.addEventListener("change", (e) => {
    const b = e.target.dataset.bit;
    if (b === undefined) return;
    mode = e.target.checked ? mode | +b : mode & ~+b;
    draw();
  });
  root.addEventListener("input", (e) => {
    if (e.target.id === "permOct" && /^[0-7]{3,4}$/.test(e.target.value)) { mode = parseInt(e.target.value, 8); draw(); }
    if (e.target.id === "umaskIn" && /^[0-7]{3,4}$/.test(e.target.value)) { umask = parseInt(e.target.value, 8); draw(); }
  });
  draw();
  return { set(m) { mode = m; draw(); } };
}

// ===================================================================== sandbox
export function playground(view) {
  view.innerHTML = `
    ${labHero("SH", "mint", "Shell Sandbox", "A simulated Ubuntu box with a real-feeling shell: files, permissions, pipes, redirection, scripts, processes, systemd services and networking tools. Break anything; <b>New machine</b> resets it. Tab completes paths, ↑ recalls history.", `<button class="btn small" id="shReset">New machine</button>`)}
    <div class="lab-grid side-right" style="margin-top:1.2rem">
      <div id="termWrap"></div>
      <aside class="lab-main">
        <div class="panel clay ft"><h3>Files <span class="muted" id="ftCwd"></span></h3><div id="ftree" class="ftree"></div></div>
        <div class="panel clay perm" id="perm"></div>
      </aside>
    </div>`;
  let calc;
  const t = terminal($("#termWrap"), {
    quick: ["ls -la", "cat notes.txt", "grep ERROR logs/app.log", "cut -d' ' -f1 logs/access.log | sort | uniq -c | sort -rn", "ps aux", "systemctl status nginx", "ls -l /etc/shadow", "help"],
    onChange: (sim) => {
      $("#ftree").innerHTML = treeHtml(sim) || `<div class="muted">empty</div>`;
      $("#ftCwd").textContent = shortPath(sim.cwd);
    },
  });
  calc = permCalc($("#perm"));
  $("#ftree").addEventListener("click", (e) => {
    const row = e.target.closest("[data-path]");
    if (!row) return;
    const p = shortPath(row.dataset.path);
    const n = t.sim.lookup(row.dataset.path, false);
    if (n) calc.set(n.mode & 0o7777);
    t.run(row.dataset.kind === "dir" ? `ls -la ${p}` : `cat ${p}`);
  });
  const script = takeHandoff("sh-script");
  if (script) {
    const lines = script.split("\n").map((l) => l.trim()).filter((l) => l && !l.startsWith("#"));
    let i = 0;
    const tick = () => {
      if (i >= lines.length || !document.body.contains($("#tlog"))) return;
      t.run(lines[i++]);
      setTimeout(tick, 380);
    };
    tick();
  } else t.print(null, `Welcome to the Linux sandbox. You are 'learner' in ${HOME}. Try: ls -la, cat notes.txt, help`);
  $("#shReset").onclick = () => t.reset();
}

// ===================================================================== challenges
const lastLines = (out) => out.trim().split("\n").map((l) => l.trim()).filter(Boolean);
const CHALLENGES = [
  {
    title: "Make a home for your project", goal: "Create the nested directory <code>~/projects/demo/src</code> in one command.",
    check: (s) => s.lookup(`${HOME}/projects/demo/src`)?.type === "dir",
    hint: "mkdir needs a flag to create missing parent directories.", solution: ["mkdir -p ~/projects/demo/src"],
  },
  {
    title: "Write a file without an editor", goal: "Create <code>~/projects/demo/README.md</code> containing the line <i>hello linux</i>.",
    setup: ["mkdir -p ~/projects/demo"],
    check: (s) => /hello linux/.test(s.lookup(`${HOME}/projects/demo/README.md`)?.content || ""),
    hint: "echo prints text; > redirects it into a file.", solution: ["echo 'hello linux' > ~/projects/demo/README.md"],
  },
  {
    title: "Count the errors", goal: "Print <b>only the number</b> of lines containing ERROR in <code>logs/app.log</code>.",
    check: (s, out) => {
      const want = s.lookup(`${HOME}/logs/app.log`).content.split("\n").filter((l) => l.includes("ERROR")).length;
      return lastLines(out).at(-1) === String(want);
    },
    hint: "grep can count matches itself, or pipe into wc -l.", solution: ["grep -c ERROR logs/app.log"],
  },
  {
    title: "Find the top talker", goal: "From <code>logs/access.log</code> (first column is the client IP), print the line for the IP with the most requests at the top.",
    check: (s, out) => /^\s*\d+\s+203\.0\.113\.7$/.test(lastLines(out)[0] || "") || lastLines(out)[0] === "203.0.113.7",
    hint: "cut the first field, sort, uniq -c to count, sort -rn, head -1.", solution: ["cut -d' ' -f1 logs/access.log | sort | uniq -c | sort -rn | head -1"],
  },
  {
    title: "Unique cities", goal: "Print the distinct cities from <code>data/users.csv</code> (3rd column), sorted, <b>without</b> the header.",
    check: (_, out) => lastLines(out).join(",") === "Berlin,Delhi,Pune",
    hint: "tail -n +2 skips the header; cut -d, -f3 picks the column; sort -u dedupes.", solution: ["tail -n +2 data/users.csv | cut -d, -f3 | sort -u"],
  },
  {
    title: "Run the backup script", goal: "<code>scripts/backup.sh</code> refuses to run. Make it executable for its owner and run it so <code>~/backup/notes.txt</code> exists.",
    check: (s) => !!s.lookup(`${HOME}/backup/notes.txt`) && (s.lookup(`${HOME}/scripts/backup.sh`).mode & 0o100) !== 0,
    hint: "chmod u+x adds execute for the owner; run it with ./scripts/backup.sh.", solution: ["chmod u+x scripts/backup.sh", "./scripts/backup.sh"],
  },
  {
    title: "Lock down SSH", goal: "SSH refuses keys that others can read. Make <code>~/.ssh</code> mode 700 and <code>~/.ssh/id_demo</code> mode 600.",
    check: (s) => (s.lookup(`${HOME}/.ssh`).mode & 0o777) === 0o700 && (s.lookup(`${HOME}/.ssh/id_demo`)?.mode & 0o777) === 0o600,
    hint: "Octal: 7 = rwx, 6 = rw-, 0 = ---.", solution: ["chmod 700 ~/.ssh", "chmod 600 ~/.ssh/id_demo"],
  },
  {
    title: "Capture the errors", goal: "Run <code>ls /nope</code> so its error message ends up in <code>~/errors.txt</code> instead of the screen.",
    check: (s) => /No such file/.test(s.lookup(`${HOME}/errors.txt`)?.content || ""),
    hint: "Errors go to stream 2 (stderr): redirect it with 2>.", solution: ["ls /nope 2> ~/errors.txt"],
  },
  {
    title: "Stop the runaway", goal: "Something is eating 99% CPU. Find it and stop it.",
    check: (s) => !s.procs.some((p) => p.cmd.includes("runaway")),
    hint: "ps aux or top shows CPU usage; kill sends SIGTERM to a PID.", solution: ["ps aux", "kill 1337"],
  },
  {
    title: "Bring nginx back", goal: "nginx was stopped and <code>curl localhost</code> fails. Start it (you will need root) and make sure it starts on boot.",
    setup: ["sudo systemctl stop nginx", "sudo systemctl disable nginx"],
    check: (s) => s.services.nginx.active && s.services.nginx.enabled,
    hint: "systemctl start and enable; prefix with sudo.", solution: ["sudo systemctl start nginx", "sudo systemctl enable nginx", "curl localhost"],
  },
  {
    title: "Shortcut and cleanup", goal: "Create a symlink <code>~/current</code> pointing to <code>~/projects/demo</code>, and delete every <code>*.tmp</code> file in <code>~/tmp</code> while keeping the rest.",
    setup: ["mkdir -p ~/projects/demo"],
    check: (s) => {
      const link = s.lookup(`${HOME}/current`, false);
      const tmp = s.lookup(`${HOME}/tmp`);
      return link?.type === "link" && s.lookup(`${HOME}/current`) === s.lookup(`${HOME}/projects/demo`) &&
        !Object.keys(tmp.children).some((k) => k.endsWith(".tmp")) && "keep.txt" in tmp.children;
    },
    hint: "ln -s TARGET LINK_NAME; rm with a glob like ~/tmp/*.tmp.", solution: ["ln -s ~/projects/demo ~/current", "rm ~/tmp/*.tmp"],
  },
];

export function lab(view) {
  const done = new Set(store.get("linux-challenges", []));
  let cur = CHALLENGES.findIndex((_, i) => !done.has(i));
  if (cur < 0) cur = 0;
  view.innerHTML = `
    ${labHero("LVL", "lemon", "Shell Challenges", "Eleven real-world tasks on a simulated machine: files, text pipelines, permissions, redirection, processes, services and links. Type real commands; the level checks itself after every command.", `<span class="pill neutral" id="lxDone"></span>`)}
    <div class="filters"><div class="tabs" id="levels"></div></div>
    <div class="panel clay challenge">
      <div><h3 id="cTitle"></h3><p id="cGoal"></p></div>
      <div class="row"><button class="btn small" id="cHint">Hint</button><button class="btn small" id="cSolve">Show solution</button><button class="btn small" id="cReset">Restart level</button></div>
      <div id="cExtra" class="muted"></div>
      <div id="cStatus"></div>
    </div>
    <div id="termWrap" style="margin-top:1rem"></div>`;
  let solved = true;
  let t = null;
  t = terminal($("#termWrap"), {
    quick: ["ls -la", "help", "man grep", "ps aux"],
    onChange: (sim, out) => {
      if (solved || !t) return;
      let ok = false;
      try { ok = !!CHALLENGES[cur].check(sim, out); } catch { ok = false; }
      if (!ok) return;
      solved = true;
      done.add(cur);
      store.set("linux-challenges", [...done]);
      $("#cStatus").innerHTML = `<div class="bug-why good"><b>Level complete!</b> ${cur < CHALLENGES.length - 1 ? `<button class="btn small primary" id="cNext">Next level →</button>` : "You finished every level."}</div>`;
      toast(`Level ${cur + 1} solved`);
      tabs();
    },
  });
  function tabs() {
    $("#levels").innerHTML = CHALLENGES.map((c, i) => `<button data-i="${i}" class="${i === cur ? "active" : ""}" title="${esc(c.title)}">${done.has(i) ? "✓ " : ""}${i + 1}</button>`).join("");
    $("#lxDone").textContent = `${done.size} / ${CHALLENGES.length} solved`;
  }
  function load(i) {
    cur = i;
    const c = CHALLENGES[i];
    solved = true;
    t.reset(c.setup || []);
    solved = false;
    $("#cTitle").textContent = `Level ${i + 1}: ${c.title}`;
    $("#cGoal").innerHTML = c.goal;
    $("#cExtra").innerHTML = "";
    $("#cStatus").innerHTML = "";
    t.print(null, `Fresh machine. You are learner in ~ (${HOME}).`);
    tabs();
  }
  $("#levels").onclick = (e) => {
    const i = e.target.closest("[data-i]")?.dataset.i;
    if (i !== undefined) load(+i);
  };
  $("#cHint").onclick = () => ($("#cExtra").innerHTML = `<b>Hint:</b> ${esc(CHALLENGES[cur].hint)}`);
  $("#cSolve").onclick = () => ($("#cExtra").innerHTML = `<b>One solution:</b> ${CHALLENGES[cur].solution.map((s) => `<button class="btn small" data-run="${esc(s)}"><code>${esc(s)}</code></button>`).join(" ")}`);
  $("#cExtra").addEventListener("click", (e) => {
    const c = e.target.closest("[data-run]")?.dataset.run;
    if (c) t.run(c);
  });
  $("#cReset").onclick = () => load(cur);
  view.addEventListener("click", (e) => {
    if (e.target.id === "cNext") load(cur + 1);
  });
  load(cur);
}

export { CHALLENGES };
