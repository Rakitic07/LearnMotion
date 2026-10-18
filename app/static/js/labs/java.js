import { $, $$, esc, highlightCode } from "../util.js";
import { codeEditor, labHero, sampleOptions, takeHandoff } from "./common.js";
import { LTS, RELEASES, RULES, TASKS, WARNINGS, hasFlexibleCtor, isCompactSource } from "./javadata.js";

const vLabel = (v) => `Java ${v}${LTS.includes(v) ? " LTS" : ""}`;
const jepLink = (j) => (j ? j.split(/\s*\/\s*/).map((n) => `<a href="https://openjdk.org/jeps/${n}" target="_blank" rel="noopener">JEP ${n}</a>`).join(" / ") : "");

/** Line diff via longest common subsequence. */
export function lineDiff(a, b) {
  const x = a.split("\n");
  const y = b.split("\n");
  const n = x.length;
  const m = y.length;
  const dp = Array.from({ length: n + 1 }, () => new Uint16Array(m + 1));
  for (let i = n - 1; i >= 0; i--) for (let j = m - 1; j >= 0; j--) dp[i][j] = x[i] === y[j] ? dp[i + 1][j + 1] + 1 : Math.max(dp[i + 1][j], dp[i][j + 1]);
  const ops = [];
  let i = 0;
  let j = 0;
  while (i < n && j < m) {
    if (x[i] === y[j]) ops.push({ t: "same", a: x[i++], b: y[j++] });
    else if (dp[i + 1][j] >= dp[i][j + 1]) ops.push({ t: "del", a: x[i++] });
    else ops.push({ t: "add", b: y[j++] });
  }
  while (i < n) ops.push({ t: "del", a: x[i++] });
  while (j < m) ops.push({ t: "add", b: y[j++] });
  return ops;
}

const line = (text, cls, no) => `<div class="dl ${cls}"><span class="dn">${no ?? ""}</span><span class="dc">${text === "" ? " " : highlightCode(text, "java")}</span></div>`;

function sideBySide(ops) {
  let ln = 0;
  let rn = 0;
  const left = [];
  const right = [];
  for (const o of ops) {
    if (o.t === "same") { left.push(line(o.a, "", ++ln)); right.push(line(o.b, "", ++rn)); }
    else if (o.t === "del") left.push(line(o.a, "del", ++ln));
    else right.push(line(o.b, "add", ++rn));
  }
  return [left.join(""), right.join("")];
}

function unified(ops) {
  return ops.map((o) => (o.t === "same" ? line(o.a, "", " ") : o.t === "del" ? line(o.a, "del", "-") : line(o.b, "add", "+"))).join("");
}

// ===================================================================== explorer
export function lab(view) {
  const groups = [...new Set(TASKS.map((t) => t.group))];
  view.innerHTML = `
    ${labHero("JDK", "peach", "Java Version Explorer", "The same task written the way each Java release allows, from Java 7/8 through 11, 14, 17, 18, 21 and 25 LTS. Pick two versions to see a line-by-line diff, or press <b>Play evolution</b> to watch the code modernise.", `<div class="tabs" id="jxMode"><button class="active" data-m="compare">Compare code</button><button data-m="releases">What's new</button></div>`)}
    <div id="jxCompare" class="lab-grid side-left" style="margin-top:1.2rem">
      <aside class="panel clay jx-tasks">
        <select id="jxTaskSel" class="jx-mobile" aria-label="Task">${groups.map((g) => `<optgroup label="${esc(g)}">${TASKS.filter((t) => t.group === g).map((t) => `<option value="${t.id}">${esc(t.title)}</option>`).join("")}</optgroup>`).join("")}</select>
        <div class="jx-list">${groups.map((g) => `<h4>${esc(g)}</h4>${TASKS.filter((t) => t.group === g).map((t) => `<button class="jx-task" data-task="${t.id}">${esc(t.title)}<small>${t.versions.map((v) => v.v).join(" · ")}</small></button>`).join("")}`).join("")}</div>
      </aside>
      <div class="lab-main">
        <div class="panel clay">
          <div class="jx-head"><h3 id="jxTitle"></h3>
            <div class="row">
              <label class="inline">From <select id="jxFrom"></select></label>
              <label class="inline">To <select id="jxTo"></select></label>
              <div class="tabs" id="jxView"><button class="active" data-v="split">Side by side</button><button data-v="unified">Diff</button></div>
              <button class="btn small primary" id="jxPlay">Play evolution</button>
            </div>
          </div>
          <div class="jx-chips" id="jxChips"></div>
          <div id="jxStats" class="muted jx-stats"></div>
          <div id="jxDiff"></div>
          <div class="row" style="margin-top:.8rem"><button class="btn small" id="jxCheck">Check minimum version of the newer code</button></div>
        </div>
      </div>
    </div>
    <div id="jxReleases" hidden style="margin-top:1.2rem"></div>`;
  let task = TASKS[0];
  let from = 0;
  let to = 1;
  let mode = "split";
  let timer = null;
  const stop = () => {
    clearTimeout(timer);
    timer = null;
    $("#jxPlay").textContent = "Play evolution";
  };

  const opts = () => task.versions.map((v, i) => `<option value="${i}">${vLabel(v.v)}</option>`).join("");
  function render(animate = false) {
    const A = task.versions[from];
    const B = task.versions[to];
    const ops = lineDiff(A.code, B.code);
    const adds = ops.filter((o) => o.t === "add").length;
    const dels = ops.filter((o) => o.t === "del").length;
    $("#jxTitle").textContent = task.title;
    $("#jxFrom").value = from;
    $("#jxTo").value = to;
    $("#jxChips").innerHTML = task.versions.map((v, i) => `<button class="jx-chip ${i === to ? "on" : ""} ${i === from ? "from" : ""} ${LTS.includes(v.v) ? "lts" : ""}" data-i="${i}"><b>${v.v}</b>${LTS.includes(v.v) ? "<small>LTS</small>" : ""}</button>`).join(`<span class="jx-arrow">→</span>`);
    $("#jxStats").innerHTML = `<span class="dstat add">+${adds}</span> <span class="dstat del">-${dels}</span> lines · ${A.code.split("\n").length} → ${B.code.split("\n").length} lines`;
    const head = (v, n) => `<div class="jx-pane-head"><span class="pill ${LTS.includes(v.v) ? "beginner" : "neutral"}">${vLabel(v.v)}</span><p>${esc(n)}</p></div>`;
    if (mode === "split") {
      const [l, r] = sideBySide(ops);
      $("#jxDiff").innerHTML = `<div class="jx-split ${animate ? "anim" : ""}"><div class="jx-pane">${head(A, A.note)}<div class="dcode">${l}</div></div><div class="jx-pane">${head(B, B.note)}<div class="dcode">${r}</div></div></div>`;
    } else {
      $("#jxDiff").innerHTML = `<div class="${animate ? "anim" : ""}">${head(B, `${vLabel(A.v)} → ${vLabel(B.v)}: ${B.note}`)}<div class="dcode">${unified(ops)}</div></div>`;
    }
    $$(".jx-task").forEach((b) => b.classList.toggle("active", b.dataset.task === task.id));
    $("#jxTaskSel").value = task.id;
  }
  function pick(id) {
    stop();
    task = TASKS.find((t) => t.id === id) || TASKS[0];
    $("#jxFrom").innerHTML = opts();
    $("#jxTo").innerHTML = opts();
    from = 0;
    to = task.versions.length - 1;
    render();
  }
  view.addEventListener("click", (e) => {
    const t = e.target.closest("[data-task]");
    if (t) pick(t.dataset.task);
    const chip = e.target.closest(".jx-chip");
    if (chip) {
      stop();
      to = +chip.dataset.i;
      from = Math.max(0, to - 1);
      if (to === 0) to = Math.min(1, task.versions.length - 1);
      render(true);
    }
    const m = e.target.closest("#jxView [data-v]");
    if (m) {
      mode = m.dataset.v;
      $$("#jxView button").forEach((b) => b.classList.toggle("active", b === m));
      render();
    }
    const sw = e.target.closest("#jxMode [data-m]");
    if (sw) {
      stop();
      $$("#jxMode button").forEach((b) => b.classList.toggle("active", b === sw));
      $("#jxCompare").hidden = sw.dataset.m !== "compare";
      $("#jxReleases").hidden = sw.dataset.m !== "releases";
    }
  });
  $("#jxTaskSel").onchange = (e) => pick(e.target.value);
  $("#jxFrom").onchange = (e) => { stop(); from = +e.target.value; render(true); };
  $("#jxTo").onchange = (e) => { stop(); to = +e.target.value; render(true); };
  $("#jxPlay").onclick = () => {
    if (timer) return stop();
    $("#jxPlay").textContent = "Stop";
    from = 0;
    to = 1;
    render(true);
    const step = () => {
      if (!document.body.contains($("#jxPlay"))) return;
      if (to >= task.versions.length - 1) return stop();
      from = to;
      to += 1;
      render(true);
      timer = setTimeout(step, 3600);
    };
    timer = setTimeout(step, 3600);
  };
  $("#jxCheck").onclick = () => {
    sessionStorage.setItem("java-code", task.versions[to].code);
    location.hash = "#/java/playground";
  };
  pick(TASKS[0].id);
  releases($("#jxReleases"));
  return stop;
}

function releases(root) {
  const vs = RELEASES.map((r) => r.v);
  root.innerHTML = `
    <div class="panel clay jx-upgrade">
      <h3>Upgrade planner</h3>
      <div class="row">
        <label class="inline">I am on <select id="upFrom">${vs.map((v) => `<option ${v === 8 ? "selected" : ""}>${v}</option>`).join("")}</select></label>
        <label class="inline">moving to <select id="upTo">${vs.map((v) => `<option ${v === 25 ? "selected" : ""}>${v}</option>`).join("")}</select></label>
        <label class="check"><input type="checkbox" id="ltsOnly"> LTS releases only</label>
      </div>
      <p class="muted" id="upSummary"></p>
    </div>
    <div class="jx-timeline" id="jxTimeline"></div>`;
  const draw = () => {
    const a = +$("#upFrom").value;
    const b = +$("#upTo").value;
    const lo = Math.min(a, b);
    const hi = Math.max(a, b);
    const lts = $("#ltsOnly").checked;
    const span = RELEASES.filter((r) => r.v > lo && r.v <= hi);
    const finals = span.flatMap((r) => r.features.filter((f) => !/preview|incubator|experimental/i.test(f[1])));
    $("#upSummary").innerHTML = a === b ? "Pick two different versions." : `Java ${lo} → ${hi} spans <b>${span.length}</b> releases and <b>${finals.length}</b> final features (cards in range are highlighted). LTS stops on the way: ${LTS.filter((v) => v > lo && v <= hi).join(", ") || "none"}.`;
    $("#jxTimeline").innerHTML = RELEASES.filter((r) => !lts || r.lts).map((r) => `
      <article class="jx-rel ${r.lts ? "lts" : ""} ${a !== b && r.v > lo && r.v <= hi ? "inrange" : ""}">
        <header><span class="jx-v">${r.v}</span><div><b>${esc(r.theme)}</b><small>${esc(r.date)}${r.lts ? " · LTS" : ""}</small></div></header>
        <ul>${r.features.map(([j, name, d]) => `<li class="${/preview|incubator|experimental/i.test(name) ? "pre" : ""}"><b>${esc(name)}</b> ${j ? `<span class="jep">${jepLink(j)}</span>` : ""}<p>${esc(d)}</p></li>`).join("")}</ul>
      </article>`).join("");
  };
  root.addEventListener("change", draw);
  draw();
}

// ===================================================================== checker
const STRIP = /"""[\s\S]*?"""|"(?:\\.|[^"\\\n])*"|'(?:\\.|[^'\\\n])+'|\/\*[\s\S]*?\*\/|\/\/[^\n]*/g;
const blank = (m) => m.replace(/[^\n]/g, " ");
const keepQuotes = (m) => (m.startsWith('"') || m.startsWith("'") ? m[0] + blank(m.slice(1, -1)) + m.at(-1) : blank(m));

/** Returns {min, lts, found:[{line, name, v, jep, alt}], warnings:[...]} for a Java source. */
export function analyze(src) {
  const code = src.replace(STRIP, keepQuotes);
  const found = [];
  const lineOf = (text, idx) => text.slice(0, idx).split("\n").length;
  for (const [re, name, v, jep, alt] of RULES) {
    const rawRule = /"|\\\/\\\/\\\/|jwebserver/.test(re.source);
    const text = rawRule ? src : code;
    const m = re.exec(text);
    if (m) found.push({ line: lineOf(text, m.index), name, v, jep, alt, snippet: text.split("\n")[lineOf(text, m.index) - 1].trim() });
  }
  if (isCompactSource(code)) found.push({ line: lineOf(code, code.search(/\bvoid\s+main\s*\(/)), name: "Compact source file / instance main", v: 25, jep: "512", alt: "public class X { public static void main(String[] args) }", snippet: "void main()" });
  if (hasFlexibleCtor(code)) {
    const idx = code.search(/;\s*(super|this)\s*\(/);
    found.push({ line: lineOf(code, idx), name: "Statements before super(...)", v: 25, jep: "513", alt: "static helper inside the super(...) argument", snippet: code.split("\n")[lineOf(code, idx) - 1].trim() });
  }
  found.sort((a, b) => b.v - a.v || a.line - b.line);
  const min = found.length ? Math.max(...found.map((f) => f.v)) : 8;
  const warnings = WARNINGS.filter(([re]) => re.test(src)).map(([, w]) => w);
  return { min, lts: LTS.find((v) => v >= min) ?? LTS.at(-1), found, warnings };
}

const DEFAULT = `import java.util.*;

sealed interface Shape permits Circle, Square {}
record Circle(double r) implements Shape {}
record Square(double side) implements Shape {}

public class Shapes {
    static double area(Shape s) {
        return switch (s) {
            case Circle(double r) -> Math.PI * r * r;
            case Square(double side) -> side * side;
        };
    }

    public static void main(String[] args) {
        var shapes = List.of(new Circle(1), new Square(2));
        String report = """
            Total area: %.2f
            """.formatted(shapes.stream().mapToDouble(Shapes::area).sum());
        System.out.print(report);
        System.out.println(shapes.getFirst());
    }
}`;

export function playground(view, content) {
  const samples = [
    ...TASKS.flatMap((t) => t.versions.map((v) => ({ label: `${t.title} · Java ${v.v}`, code: v.code }))),
    ...sampleOptions(content, ["java"]),
  ];
  view.innerHTML = `
    ${labHero("VER", "lilac", "Java Version Checker", "Paste Java code and see the <b>minimum Java version</b> it needs, the LTS to target, and which line uses which feature (with its JEP and the older way to write it). Detection is static and regex-based; nothing is compiled or executed.")}
    <div class="lab-grid side-right" style="margin-top:1.2rem">
      <div class="panel clay">
        <div class="row"><select id="sample" aria-label="Sample"><option value="">Load a sample…</option>${samples.map((s, i) => `<option value="${i}">${esc(s.label)}</option>`).join("")}</select><button class="btn primary" id="check">Check <kbd>⌘/Ctrl ↵</kbd></button></div>
        <textarea id="code" class="code code-editor" spellcheck="false" rows="18"></textarea>
      </div>
      <aside class="panel clay jv-verdict" id="verdict"></aside>
    </div>
    <div class="panel clay" id="features" style="margin-top:1.2rem"></div>`;
  const ta = $("#code");
  ta.value = takeHandoff("java-code") || DEFAULT;
  const run = () => {
    const r = analyze(ta.value);
    const runs = RELEASES.map((x) => x.v);
    $("#verdict").innerHTML = `
      <div class="jv-min"><span class="muted">Minimum version</span><b>Java ${r.min}</b></div>
      <div class="jv-lts"><span class="muted">Target this LTS</span><b>Java ${r.lts}</b></div>
      <div class="jv-runs">${runs.map((v) => `<span class="${v >= r.min ? "ok" : "no"} ${LTS.includes(v) ? "lts" : ""}" title="${v >= r.min ? "compiles" : "too old"}">${v}</span>`).join("")}</div>
      ${r.warnings.length ? `<div class="jv-warn"><b>Heads up</b>${r.warnings.map((w) => `<p>${esc(w)}</p>`).join("")}</div>` : ""}`;
    $("#features").innerHTML = r.found.length ? `
      <h3>Detected features <span class="muted">(${r.found.length})</span></h3>
      <div class="res-table jv-table-wrap"><table class="jv-table"><thead><tr><th>Line</th><th>Feature</th><th>Since</th><th>JEP</th><th>Before that</th></tr></thead>
      <tbody>${r.found.map((f) => `<tr class="${f.v === r.min ? "max" : ""}"><td><button class="btn small" data-line="${f.line}">${f.line}</button></td><td><b>${esc(f.name)}</b><code>${esc(f.snippet.slice(0, 70))}</code></td><td><span class="pill ${LTS.includes(f.v) ? "beginner" : "neutral"}">${f.v}</span></td><td>${jepLink(f.jep)}</td><td class="muted">${esc(f.alt)}</td></tr>`).join("")}</tbody></table></div>`
      : `<p class="muted">No version-specific features found: this looks like plain Java that compiles on Java 8 (and probably earlier).</p>`;
  };
  $("#features").addEventListener("click", (e) => {
    const n = e.target.closest("[data-line]")?.dataset.line;
    if (!n) return;
    const lines = ta.value.split("\n");
    const start = lines.slice(0, n - 1).join("\n").length + (n > 1 ? 1 : 0);
    ta.focus();
    ta.setSelectionRange(start, start + lines[n - 1].length);
    ta.scrollTop = Math.max(0, (n - 4) * 20);
  });
  codeEditor(ta, run, 4);
  let deb;
  ta.addEventListener("input", () => {
    clearTimeout(deb);
    deb = setTimeout(run, 350);
  });
  $("#check").onclick = run;
  $("#sample").onchange = (e) => {
    if (e.target.value === "") return;
    ta.value = samples[+e.target.value].code;
    run();
  };
  run();
}
