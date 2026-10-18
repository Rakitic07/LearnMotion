import { $, esc, store, toast } from "../util.js";
import { GitSim, HELP, graphSvg } from "./gitsim.js";
import { labHero, takeHandoff } from "./common.js";

/** Terminal + live graph bound to one GitSim. Returns controls for the caller. */
function terminal(root, { onChange, quick = [] } = {}) {
  root.innerHTML = `
    <div class="panel clay git-graph-wrap"><div class="git-graph-scroll" id="graph"></div>
      <div class="git-legend muted"><span><i class="lg head"></i>HEAD</span><span><i class="lg merge"></i>merge commit</span><span><i class="lg dead"></i>unreachable (only the reflog remembers it)</span></div></div>
    <div class="panel clay term">
      <div class="term-log" id="tlog"></div>
      <form class="term-in" id="tform"><span class="prompt" id="prompt">main $</span><input id="tinput" autocomplete="off" spellcheck="false" placeholder="git commit -m &quot;init&quot;" aria-label="git command"></form>
      ${quick.length ? `<div class="row quick">${quick.map((q) => `<button type="button" class="btn small" data-cmd="${esc(q)}">${esc(q)}</button>`).join("")}</div>` : ""}
    </div>`;
  let sim = new GitSim();
  let snapshots = [];
  const hist = [];
  let hpos = 0;
  const logEl = $("#tlog", root);

  const print = (cmd, out, bad) => {
    logEl.insertAdjacentHTML("beforeend", `${cmd !== null ? `<div class="t-cmd"><span class="prompt">${esc(sim.head.ref || sim.head.det)} $</span> ${esc(cmd)}</div>` : ""}${out ? `<pre class="t-out ${bad ? "bad" : ""}">${esc(out)}</pre>` : ""}`);
    logEl.scrollTop = logEl.scrollHeight;
  };
  const draw = () => {
    $("#graph", root).innerHTML = graphSvg(sim);
    const g = $("#graph", root);
    g.scrollLeft = g.scrollWidth;
    $("#prompt", root).textContent = `${sim.head.ref || `(${sim.head.det})`} $`;
    onChange?.(sim);
  };
  const clone = (s) => {
    const c = Object.assign(new GitSim(), structuredClone({ ...s, commits: undefined }));
    c.commits = new Map([...s.commits].map(([k, v]) => [k, { ...v, parents: [...v.parents] }]));
    return c;
  };
  const run = (line, echo = true) => {
    const cmd = line.trim().replace(/\s+#.*$/, "");
    if (!cmd || cmd.startsWith("#")) return true;
    if (cmd === "clear") {
      logEl.innerHTML = "";
      return true;
    }
    if (cmd === "help") {
      print(cmd, HELP);
      return true;
    }
    if (cmd === "undo") {
      if (!snapshots.length) return print(cmd, "nothing to undo", true), false;
      sim = snapshots.pop();
      print(cmd, "restored the previous state");
      draw();
      return true;
    }
    const before = clone(sim);
    try {
      const promptLine = echo ? cmd : null;
      const out = sim.exec(cmd);
      snapshots.push(before);
      if (snapshots.length > 50) snapshots.shift();
      print(promptLine, out);
      draw();
      return true;
    } catch (err) {
      sim = before;
      print(echo ? cmd : null, `fatal: ${err.message}`, true);
      return false;
    }
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
    else return;
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
    get sim() { return sim; },
    reset(setup = []) {
      sim = new GitSim();
      snapshots = [];
      logEl.innerHTML = "";
      setup.forEach((l) => {
        try { sim.exec(l); } catch (err) { console.error(l, err); }
      });
      draw();
    },
    print,
  };
}

// ===================================================================== sandbox
export function playground(view) {
  view.innerHTML = `
    ${labHero("GIT", "peach", "Git Sandbox", "A simulated repository with a live commit graph. Branch, merge, rebase, reset, revert and cherry-pick, then watch exactly how the graph and the refs move. <code>undo</code> rewinds a step; faded commits are unreachable.", `<button class="btn small" id="gReset">New repo</button>`)}
    <div id="term" style="margin-top:1.2rem"></div>`;
  const t = terminal($("#term"), { quick: ['git commit -m "', "git switch -c ", "git switch main", "git merge ", "git rebase main", "git log --oneline --all", "git reflog", "undo", "help"] });
  const script = takeHandoff("git-script");
  if (script) {
    const lines = script.split("\n").map((l) => l.trim()).filter((l) => l && !l.startsWith("#"));
    let i = 0;
    const tick = () => {
      if (i >= lines.length) return;
      const l = lines[i++];
      if (!l.startsWith("git ")) t.print(l, "(skipped: only git commands are simulated)");
      else t.run(l);
      setTimeout(tick, 420);
    };
    tick();
  } else {
    t.print(null, 'Welcome! Type "help" for commands, or start with:  git commit -m "init"');
  }
  $("#gReset").onclick = () => t.reset();
}

// ===================================================================== challenges
const base = ['git commit -m "init"'];
const CHALLENGES = [
  {
    title: "First commits", goal: "Make <b>main</b> have 3 commits.", setup: [],
    check: (s) => s.branches.main && s.ancestors(s.branches.main).size >= 3,
    hint: "git commit -m \"…\" creates a commit and moves the current branch forward.",
    solution: ['git commit -m "init"', 'git commit -m "add readme"', 'git commit -m "add app"'],
  },
  {
    title: "Branch out", goal: "Create a <b>feature</b> branch with 2 commits that main does not have. main must stay at <i>init</i>.", setup: base,
    check: (s) => s.branches.feature && s.only(s.branches.feature, s.branches.main).length >= 2 && s.ancestors(s.branches.main).size === 1,
    hint: "git switch -c feature creates and switches in one step.",
    solution: ["git switch -c feature", 'git commit -m "f1"', 'git commit -m "f2"'],
  },
  {
    title: "Fast-forward", goal: "Bring <b>main</b> up to <b>feature</b> without creating a merge commit.",
    setup: [...base, "git switch -c feature", 'git commit -m "f1"', 'git commit -m "f2"', "git switch main"],
    check: (s) => s.branches.main === s.branches.feature && ![...s.ancestors(s.branches.main)].some((c) => s.commits.get(c).merge),
    hint: "main has no new commits, so merging just slides the pointer.",
    solution: ["git merge feature"],
  },
  {
    title: "True merge", goal: "Both branches moved on. Merge <b>feature</b> into <b>main</b> with a merge commit.",
    setup: [...base, "git switch -c feature", 'git commit -m "f1"', "git switch main", 'git commit -m "m1"'],
    check: (s) => s.commits.get(s.branches.main)?.parents.length === 2 && s.isAncestor(s.branches.feature, s.branches.main),
    hint: "Switch to main, then merge. A merge commit has two parents.",
    solution: ["git merge feature"],
  },
  {
    title: "Linear history", goal: "Replay <b>feature</b> on top of the latest <b>main</b> so history is a straight line (no merge commits).",
    setup: [...base, "git switch -c feature", 'git commit -m "f1"', 'git commit -m "f2"', "git switch main", 'git commit -m "m1"', "git switch feature"],
    check: (s) => s.isAncestor(s.branches.main, s.branches.feature) && ![...s.ancestors(s.branches.feature)].some((c) => s.commits.get(c).merge) && s.chainMsgs("feature").includes("f2"),
    hint: "Rebase copies your commits onto a new base (new hashes!).",
    solution: ["git rebase main"],
  },
  {
    title: "Undo a local commit", goal: "The last commit <i>oops</i> was never pushed. Make <b>main</b> point at <i>good</i> again.",
    setup: [...base, 'git commit -m "good"', 'git commit -m "oops"'],
    check: (s) => s.commits.get(s.branches.main)?.msg === "good",
    hint: "Private history can be rewritten: move the branch back one commit.",
    solution: ["git reset --hard HEAD~1"],
  },
  {
    title: "Undo a shared commit", goal: "<i>bad change</i> is already pushed. Undo it <b>without rewriting history</b>.",
    setup: [...base, 'git commit -m "bad change"', 'git commit -m "later"'],
    check: (s) => {
      const tip = s.commits.get(s.branches.main);
      return tip?.msg === 'Revert "bad change"' && s.chainMsgs("main").includes("later");
    },
    hint: "Add a new commit that inverts the bad one. HEAD~1 is the bad commit.",
    solution: ["git revert HEAD~1"],
  },
  {
    title: "Backport a hotfix", goal: "<b>release</b> needs the <i>hotfix</i> commit from main, but not <i>feature-x</i>.",
    setup: [...base, "git branch release", 'git commit -m "feature-x"', 'git commit -m "hotfix"', "git switch release"],
    check: (s) => s.branches.release && s.chainMsgs("release").includes("hotfix") && !s.chainMsgs("release").includes("feature-x"),
    hint: "Copy exactly one commit onto the current branch.",
    solution: ["git cherry-pick main"],
  },
  {
    title: "Squash WIP", goal: "Turn the three <i>wip</i> commits on <b>feature</b> into one commit called <i>add login</i>.",
    setup: [...base, "git switch -c feature", 'git commit -m "wip 1"', 'git commit -m "wip 2"', 'git commit -m "wip 3"'],
    check: (s) => {
      const only = s.branches.feature ? s.only(s.branches.feature, s.branches.main) : [];
      return only.length === 1 && s.commits.get(only[0]).msg === "add login";
    },
    hint: "A soft reset moves the branch back but keeps the changes staged; then commit once.",
    solution: ["git reset --soft HEAD~3", 'git commit -m "add login"'],
  },
  {
    title: "Rescue detached work", goal: "You committed on a detached HEAD. Keep that work on a branch named <b>experiment</b>.",
    setup: [...base, 'git commit -m "c2"', "git checkout HEAD~1", 'git commit -m "try A"', 'git commit -m "try B"'],
    check: (s) => s.branches.experiment && s.chainMsgs("experiment").includes("try B"),
    hint: "A branch is just a name for a commit. Create one where HEAD is.",
    solution: ["git switch -c experiment"],
  },
  {
    title: "Reflog to the rescue", goal: "Someone ran <code>git reset --hard HEAD~1</code> and lost <i>important</i>. Bring it back onto <b>main</b>.",
    setup: [...base, 'git commit -m "important"', "git reset --hard HEAD~1"],
    check: (s) => s.commits.get(s.branches.main)?.msg === "important",
    hint: "git reflog lists where HEAD has been. HEAD@{1} was one move ago.",
    solution: ["git reflog", "git reset --hard HEAD@{1}"],
  },
];

export function lab(view) {
  const done = new Set(store.get("git-challenges", []));
  let cur = CHALLENGES.findIndex((_, i) => !done.has(i));
  if (cur < 0) cur = 0;

  view.innerHTML = `
    ${labHero("LVL", "lemon", "Git Challenges", "Eleven puzzles from first commit to reflog rescue. Each one starts from a prepared repository; reach the goal using real git commands and the level is checked automatically.", `<span class="pill neutral" id="gDone"></span>`)}
    <div class="filters"><div class="tabs" id="levels"></div></div>
    <div class="panel clay challenge">
      <div><h3 id="cTitle"></h3><p id="cGoal"></p></div>
      <div class="row"><button class="btn small" id="cHint">Hint</button><button class="btn small" id="cSolve">Show solution</button><button class="btn small" id="cReset">Restart level</button></div>
      <div id="cExtra" class="muted"></div>
      <div id="cStatus"></div>
    </div>
    <div id="term" style="margin-top:1rem"></div>`;

  let solved = false;
  let t = null;
  t = terminal($("#term"), {
    quick: ["git log --oneline --all", "git status", "git reflog", "undo", "help"],
    onChange: (sim) => {
      const c = CHALLENGES[cur];
      if (!c || solved || !t) return;
      let ok = false;
      try { ok = !!c.check(sim); } catch { ok = false; }
      if (!ok) return;
      solved = true;
      done.add(cur);
      store.set("git-challenges", [...done]);
      $("#cStatus").innerHTML = `<div class="bug-why good"><b>Level complete!</b> ${cur < CHALLENGES.length - 1 ? `<button class="btn small primary" id="cNext">Next level →</button>` : "You finished every level."}</div>`;
      toast(`Level ${cur + 1} solved`);
      tabs();
    },
  });

  function tabs() {
    $("#levels").innerHTML = CHALLENGES.map((c, i) => `<button data-i="${i}" class="${i === cur ? "active" : ""}" title="${esc(c.title)}">${done.has(i) ? "✓ " : ""}${i + 1}</button>`).join("");
    $("#gDone").textContent = `${done.size} / ${CHALLENGES.length} solved`;
  }
  function load(i) {
    cur = i;
    const c = CHALLENGES[i];
    solved = true;
    t.reset(c.setup);
    solved = false;
    $("#cTitle").textContent = `Level ${i + 1}: ${c.title}`;
    $("#cGoal").innerHTML = c.goal;
    $("#cExtra").innerHTML = "";
    $("#cStatus").innerHTML = "";
    t.print(null, c.setup.length ? `Prepared with:\n${c.setup.map((l) => "  " + l).join("\n")}` : "Empty repository on branch main.");
    tabs();
  }
  $("#levels").onclick = (e) => {
    const i = e.target.closest("[data-i]")?.dataset.i;
    if (i !== undefined) load(+i);
  };
  $("#cHint").onclick = () => ($("#cExtra").innerHTML = `<b>Hint:</b> ${esc(CHALLENGES[cur].hint)}`);
  $("#cSolve").onclick = () => ($("#cExtra").innerHTML = `<b>One solution:</b> ${CHALLENGES[cur].solution.map((s) => `<button class="btn small" data-cmd="${esc(s)}"><code>${esc(s)}</code></button>`).join(" ")}`);
  $("#cExtra").addEventListener("click", (e) => {
    const c = e.target.closest("[data-cmd]")?.dataset.cmd;
    if (c) t.run(c);
  });
  $("#cReset").onclick = () => load(cur);
  view.addEventListener("click", (e) => {
    if (e.target.id === "cNext") load(cur + 1);
  });
  load(cur);
}

export { CHALLENGES };
