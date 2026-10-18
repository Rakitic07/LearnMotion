import { esc } from "../util.js";

const hashOf = (n) => ((Math.imul(n + 7, 2654435761) ^ Math.imul(n, 40503)) >>> 0).toString(16).padStart(8, "0").slice(0, 7);

export function tokenize(line) {
  const out = [];
  const re = /"([^"]*)"|'([^']*)'|(\S+)/g;
  let m;
  while ((m = re.exec(line))) out.push(m[1] ?? m[2] ?? m[3]);
  return out;
}

export class GitSim {
  constructor() {
    this.commits = new Map();
    this.order = [];
    this.branches = { main: null };
    this.lanes = { main: 0 };
    this.tags = {};
    this.head = { ref: "main" };
    this.reflog = [];
    this.n = 0;
  }

  // ------------------------------------------------------------- helpers
  headId() {
    return this.head.ref ? this.branches[this.head.ref] : this.head.det;
  }
  laneFor(name) {
    if (!(name in this.lanes)) this.lanes[name] = Math.max(-1, ...Object.values(this.lanes)) + 1;
    return this.lanes[name];
  }
  newCommit(parents, msg, extra = {}) {
    const id = hashOf(++this.n);
    const lane = this.head.ref ? this.laneFor(this.head.ref) : this.laneFor("(detached)");
    this.commits.set(id, { id, parents: parents.filter(Boolean), msg, lane, seq: this.n, ...extra });
    this.order.push(id);
    return id;
  }
  moveHead(id, why) {
    if (this.head.ref) this.branches[this.head.ref] = id;
    else this.head.det = id;
    this.log(why);
  }
  log(why) {
    this.reflog.push({ id: this.headId(), why });
  }
  ancestors(id) {
    const seen = new Set();
    const stack = id ? [id] : [];
    while (stack.length) {
      const c = stack.pop();
      if (!c || seen.has(c)) continue;
      seen.add(c);
      stack.push(...this.commits.get(c).parents);
    }
    return seen;
  }
  isAncestor(a, b) {
    return !!a && this.ancestors(b).has(a);
  }
  reachable() {
    const all = new Set();
    [...Object.values(this.branches), ...Object.values(this.tags), this.headId()].forEach((id) => this.ancestors(id).forEach((c) => all.add(c)));
    return all;
  }
  /** Commits on `tip` that are not on `base`, oldest first. */
  only(tip, base) {
    const exclude = this.ancestors(base);
    return [...this.ancestors(tip)].filter((c) => !exclude.has(c)).sort((a, b) => this.commits.get(a).seq - this.commits.get(b).seq);
  }
  chainMsgs(ref) {
    return [...this.ancestors(this.resolve(ref))].map((c) => this.commits.get(c).msg);
  }
  resolve(spec) {
    if (!spec) throw new Error("missing revision");
    const at = /^(HEAD|[\w./-]+)@\{(\d+)\}$/.exec(spec);
    if (at) {
      const e = this.reflog[this.reflog.length - 1 - +at[2]];
      if (!e) throw new Error(`reflog has only ${this.reflog.length} entries`);
      return e.id;
    }
    const m = /^([^~^]+)((?:[~^]\d*)*)$/.exec(spec);
    if (!m) throw new Error(`bad revision '${spec}'`);
    let id;
    const base = m[1];
    if (base === "HEAD" || base === "@") id = this.headId();
    else if (base in this.branches) id = this.branches[base];
    else if (base in this.tags) id = this.tags[base];
    else {
      const hits = this.order.filter((c) => c.startsWith(base));
      if (hits.length === 1 && base.length >= 4) id = hits[0];
      else throw new Error(`unknown revision '${base}'`);
    }
    if (!id) throw new Error(`'${base}' has no commits yet`);
    for (const [, op, num] of m[2].matchAll(/([~^])(\d*)/g)) {
      const k = num === "" ? 1 : +num;
      if (op === "~") {
        for (let i = 0; i < k; i++) {
          id = this.commits.get(id).parents[0];
          if (!id) throw new Error(`'${spec}' goes past the first commit`);
        }
      } else if (k > 0) {
        id = this.commits.get(id).parents[k - 1];
        if (!id) throw new Error(`'${spec}': no parent ${k}`);
      }
    }
    return id;
  }
  short(id) {
    const c = this.commits.get(id);
    return `${id} ${c.msg}`;
  }

  // ------------------------------------------------------------- commands
  exec(line) {
    const argv = tokenize(line.trim());
    if (!argv.length) return "";
    if (argv[0] !== "git") throw new Error(`only git commands are simulated (got '${argv[0]}')`);
    const [cmd, ...args] = argv.slice(1);
    const fn = this[`git_${(cmd || "").replace(/-/g, "_")}`];
    if (!fn) throw new Error(`'${cmd || ""}' is not supported here. Type 'help'.`);
    return fn.call(this, args) ?? "";
  }
  flag(args, ...names) {
    const i = args.findIndex((a) => names.includes(a));
    if (i < 0) return false;
    args.splice(i, 1);
    return true;
  }
  opt(args, ...names) {
    const i = args.findIndex((a) => names.includes(a));
    if (i < 0) return null;
    const v = args[i + 1];
    args.splice(i, 2);
    return v;
  }

  git_init() {
    return "Initialized empty Git repository (simulated). You are on 'main'.";
  }
  git_add(args) {
    return `staged ${args.join(" ") || "nothing"} (the simulator tracks commits, not files)`;
  }
  git_restore() {
    return "working tree restored (files are not simulated)";
  }
  git_commit(args) {
    const amend = this.flag(args, "--amend");
    this.flag(args, "--allow-empty", "-a", "--no-edit");
    let msg = this.opt(args, "-m", "-am");
    const parent = this.headId();
    if (amend) {
      if (!parent) throw new Error("nothing to amend");
      const old = this.commits.get(parent);
      const id = this.newCommit(old.parents, msg || old.msg);
      this.moveHead(id, `commit (amend): ${msg || old.msg}`);
      return `[${this.head.ref || "detached HEAD"} ${id}] ${msg || old.msg} (amended ${parent})`;
    }
    msg ||= `commit ${this.n + 1}`;
    const id = this.newCommit([parent], msg);
    this.moveHead(id, `commit: ${msg}`);
    return `[${this.head.ref || "detached HEAD"} ${id}] ${msg}`;
  }
  git_branch(args) {
    const del = this.flag(args, "-d", "-D", "--delete");
    const force = this.flag(args, "-f", "--force");
    if (!args.length) {
      const names = Object.keys(this.branches);
      return [...(this.head.ref ? [] : [`* (HEAD detached at ${this.head.det})`]), ...names.map((b) => `${b === this.head.ref ? "*" : " "} ${b}${this.branches[b] ? "" : " (no commits)"}`)].join("\n");
    }
    const [name, start] = args;
    if (del) {
      if (!(name in this.branches)) throw new Error(`branch '${name}' not found`);
      if (name === this.head.ref) throw new Error(`cannot delete the branch '${name}' you are on`);
      const id = this.branches[name];
      delete this.branches[name];
      return `Deleted branch ${name} (was ${id}).`;
    }
    if (name in this.branches && !force) throw new Error(`a branch named '${name}' already exists`);
    this.branches[name] = this.resolve(start || "HEAD");
    this.laneFor(name);
    return force ? `Reset branch '${name}' to ${this.branches[name]}` : "";
  }
  checkoutTo(target, create, startPoint) {
    const from = this.head.ref || this.head.det;
    if (create) {
      if (target in this.branches) throw new Error(`a branch named '${target}' already exists`);
      this.branches[target] = this.resolve(startPoint || "HEAD");
      this.laneFor(target);
      this.head = { ref: target };
      this.log(`checkout: moving from ${from} to ${target}`);
      return `Switched to a new branch '${target}'`;
    }
    if (target in this.branches) {
      this.head = { ref: target };
      this.log(`checkout: moving from ${from} to ${target}`);
      return `Switched to branch '${target}'`;
    }
    const id = this.resolve(target);
    this.head = { det: id };
    this.log(`checkout: moving from ${from} to ${target}`);
    return `HEAD is now at ${this.short(id)}\nYou are in 'detached HEAD' state. New commits will not belong to any branch.`;
  }
  git_switch(args) {
    const create = this.opt(args, "-c", "-C", "--create");
    if (create) return this.checkoutTo(create, true, args[0]);
    if (this.flag(args, "--detach", "-d")) {
      const id = this.resolve(args[0] || "HEAD");
      const from = this.head.ref || this.head.det;
      this.head = { det: id };
      this.log(`checkout: moving from ${from} to ${args[0] || "HEAD"}`);
      return `HEAD is now at ${this.short(id)}`;
    }
    if (args[0] === "-") return this.git_checkout(["-"]);
    if (!(args[0] in this.branches)) throw new Error(`invalid reference: ${args[0] || ""}. Use 'git switch --detach <commit>' for commits.`);
    return this.checkoutTo(args[0]);
  }
  git_checkout(args) {
    if (args.includes("--")) return "file checkout is not simulated";
    const create = this.opt(args, "-b", "-B");
    if (create) return this.checkoutTo(create, true, args[0]);
    if (args[0] === "-") {
      const prev = [...this.reflog].reverse().find((e) => e.why.startsWith("checkout: moving from"));
      const from = prev && /moving from (\S+)/.exec(prev.why);
      if (!from) throw new Error("no previous branch");
      return this.checkoutTo(from[1]);
    }
    return this.checkoutTo(args[0]);
  }
  git_merge(args) {
    const noff = this.flag(args, "--no-ff");
    const ffOnly = this.flag(args, "--ff-only");
    const msg = this.opt(args, "-m");
    const theirs = this.resolve(args[0]);
    const ours = this.headId();
    if (this.isAncestor(theirs, ours)) return "Already up to date.";
    if (!ours || (this.isAncestor(ours, theirs) && !noff)) {
      this.moveHead(theirs, `merge ${args[0]}: Fast-forward`);
      return `Updating ${ours}..${theirs}\nFast-forward`;
    }
    if (ffOnly) throw new Error("Not possible to fast-forward, aborting.");
    const id = this.newCommit([ours, theirs], msg || `Merge branch '${args[0]}'${this.head.ref ? ` into ${this.head.ref}` : ""}`, { merge: true });
    this.moveHead(id, `merge ${args[0]}`);
    return `Merge made by the 'ort' strategy. [${id}]`;
  }
  git_rebase(args) {
    if (args.includes("-i") || args.includes("--interactive")) throw new Error("interactive rebase is not simulated: use 'git reset --soft <base>' then one commit to squash");
    const onto = this.opt(args, "--onto");
    const upstream = this.resolve(args[0]);
    const newBase = onto ? this.resolve(onto) : upstream;
    const ours = this.headId();
    const replay = this.only(ours, upstream).filter((c) => !this.commits.get(c).merge);
    if (!replay.length && this.isAncestor(newBase, ours)) return "Current branch is up to date.";
    let tip = newBase;
    for (const c of replay) tip = this.newCommit([tip], this.commits.get(c).msg, { from: c });
    this.moveHead(tip, `rebase (finish): onto ${args[0]}`);
    return `Successfully rebased and updated ${this.head.ref ? `refs/heads/${this.head.ref}` : "HEAD"}. Replayed ${replay.length} commit${replay.length === 1 ? "" : "s"} with new hashes.`;
  }
  git_reset(args) {
    const mode = this.flag(args, "--hard") ? "hard" : this.flag(args, "--soft") ? "soft" : (this.flag(args, "--mixed"), "mixed");
    const id = this.resolve(args[0] || "HEAD");
    this.moveHead(id, `reset: moving to ${args[0] || "HEAD"}`);
    const note = { soft: "changes kept staged", mixed: "changes kept in working tree", hard: "working tree reset" }[mode];
    return `HEAD is now at ${this.short(id)} (${mode}: ${note})`;
  }
  git_revert(args) {
    this.flag(args, "--no-edit");
    const id = this.resolve(args[0]);
    const c = this.commits.get(id);
    const nid = this.newCommit([this.headId()], `Revert "${c.msg}"`, { reverts: id });
    this.moveHead(nid, `revert: ${c.msg}`);
    return `[${this.head.ref || "detached HEAD"} ${nid}] Revert "${c.msg}"`;
  }
  git_cherry_pick(args) {
    const out = [];
    for (const spec of args) {
      const src = this.resolve(spec);
      const c = this.commits.get(src);
      const nid = this.newCommit([this.headId()], c.msg, { from: src });
      this.moveHead(nid, `cherry-pick: ${c.msg}`);
      out.push(`[${this.head.ref || "detached HEAD"} ${nid}] ${c.msg}`);
    }
    if (!out.length) throw new Error("nothing to cherry-pick");
    return out.join("\n");
  }
  git_tag(args) {
    if (this.flag(args, "-d")) {
      delete this.tags[args[0]];
      return `Deleted tag '${args[0]}'`;
    }
    this.opt(args, "-m");
    this.flag(args, "-a");
    if (!args.length) return Object.keys(this.tags).join("\n");
    if (args[0] in this.tags) throw new Error(`tag '${args[0]}' already exists`);
    this.tags[args[0]] = this.resolve(args[1] || "HEAD");
    return "";
  }
  git_log(args) {
    const all = this.flag(args, "--all");
    this.flag(args, "--oneline", "--graph", "--decorate");
    const n = +(this.opt(args, "-n") || 0);
    const ids = new Set();
    const tips = all ? [...Object.values(this.branches), ...Object.values(this.tags), this.headId()] : [this.resolve(args[0] || "HEAD")];
    tips.forEach((t) => this.ancestors(t).forEach((c) => ids.add(c)));
    let list = [...ids].sort((a, b) => this.commits.get(b).seq - this.commits.get(a).seq);
    if (n) list = list.slice(0, n);
    if (!list.length) return "(no commits yet)";
    return list.map((id) => `${id} ${this.decor(id)}${this.commits.get(id).msg}`).join("\n");
  }
  decor(id) {
    const refs = [];
    if (this.headId() === id) refs.push(this.head.ref ? `HEAD -> ${this.head.ref}` : "HEAD");
    Object.entries(this.branches).forEach(([b, c]) => c === id && b !== this.head.ref && refs.push(b));
    Object.entries(this.tags).forEach(([t, c]) => c === id && refs.push(`tag: ${t}`));
    return refs.length ? `(${refs.join(", ")}) ` : "";
  }
  git_status() {
    if (!this.head.ref) return `HEAD detached at ${this.head.det}\nnothing to commit (simulated)`;
    return `On branch ${this.head.ref}${this.branches[this.head.ref] ? "" : "\n\nNo commits yet"}\nnothing to commit (simulated)`;
  }
  git_reflog() {
    if (!this.reflog.length) return "(empty)";
    return [...this.reflog].reverse().map((e, i) => `${e.id ?? "0000000"} HEAD@{${i}}: ${e.why}`).join("\n");
  }
  git_show(args) {
    const id = this.resolve(args[0] || "HEAD");
    const c = this.commits.get(id);
    return `commit ${id} ${this.decor(id)}\n${c.parents.length > 1 ? `Merge: ${c.parents.join(" ")}\n` : ""}\n    ${c.msg}`;
  }
}

export const HELP = `Supported (simulated) commands:
  git commit -m "msg" [--amend]      git branch [-d|-f] [name] [start]
  git switch [-c] <branch>           git switch --detach <commit>
  git checkout [-b] <branch|commit>  git merge [--no-ff|--ff-only] <ref>
  git rebase [--onto X] <upstream>   git reset [--soft|--mixed|--hard] <ref>
  git revert <ref>                   git cherry-pick <ref...>
  git tag [name] [ref]               git log [--oneline] [--all] [-n N]
  git status | reflog | show <ref>   clear | help | undo
Refs: branch, tag, hash prefix, HEAD, HEAD~2, HEAD^2, HEAD@{1}`;

// ===================================================================== graph
export function graphSvg(sim) {
  const ids = sim.order;
  if (!ids.length) return `<div class="muted git-empty">No commits yet. Try <code>git commit -m "init"</code>.</div>`;
  const live = sim.reachable();
  const usedLanes = [...new Set(ids.map((id) => sim.commits.get(id).lane))].sort((a, b) => a - b);
  const laneY = new Map(usedLanes.map((l, i) => [l, i]));
  const DX = 74, DY = 66, PX = 40, PY = 54;
  const pos = new Map(ids.map((id, i) => [id, { x: PX + i * DX, y: PY + laneY.get(sim.commits.get(id).lane) * DY }]));
  const W = PX * 2 + (ids.length - 1) * DX + 60;
  const H = PY + (usedLanes.length - 1) * DY + 58;
  const head = sim.headId();
  const labels = new Map();
  const add = (id, html) => id && (labels.get(id) || labels.set(id, []).get(id)).push(html);
  Object.entries(sim.branches).forEach(([b, id]) => add(id, `<tspan class="${b === sim.head.ref ? "cur" : ""}">${esc(b)}${b === sim.head.ref ? "*" : ""}</tspan>`));
  Object.entries(sim.tags).forEach(([t, id]) => add(id, `<tspan class="tag">#${esc(t)}</tspan>`));
  if (!sim.head.ref) add(head, `<tspan class="cur">HEAD</tspan>`);

  const edges = ids.flatMap((id) => sim.commits.get(id).parents.map((p, k) => {
    const a = pos.get(p), b = pos.get(id);
    const mid = (a.x + b.x) / 2;
    const d = a.y === b.y ? `M${a.x},${a.y} L${b.x},${b.y}` : `M${a.x},${a.y} C${mid},${a.y} ${mid},${b.y} ${b.x},${b.y}`;
    return `<path d="${d}" class="g-edge ${live.has(id) ? "" : "dead"} ${k ? "merge" : ""}"/>`;
  }));
  const nodes = ids.map((id) => {
    const c = sim.commits.get(id);
    const { x, y } = pos.get(id);
    const lbl = labels.get(id);
    return `<g class="g-node ${live.has(id) ? "" : "dead"} ${id === head ? "head" : ""} ${c.merge ? "merge" : ""}" style="--lane:${c.lane % 6}">
      <title>${esc(id)} ${esc(c.msg)}${c.from ? ` (copy of ${c.from})` : ""}</title>
      <circle cx="${x}" cy="${y}" r="${id === head ? 13 : 11}"/>
      <text x="${x}" y="${y + 28}" class="g-msg">${esc(c.msg.length > 11 ? c.msg.slice(0, 10) + "…" : c.msg)}</text>
      <text x="${x}" y="${y + 41}" class="g-id">${id}</text>
      ${lbl ? `<text x="${x}" y="${y - 20}" class="g-ref">${lbl.join(" ")}</text>` : ""}
    </g>`;
  });
  return `<svg class="git-graph" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" role="img" aria-label="commit graph">${edges.join("")}${nodes.join("")}</svg>`;
}
