import { $, esc, highlightCode } from "../util.js";
import { pyResultHtml, runPython } from "../runners.js";
import { codeEditor, labHero, sampleOptions, takeHandoff } from "./common.js";

const VIZ_DEFAULT = `a = [1, 2, 3]
b = a            # same object, two names
b.append(4)
c = a[:]         # a real copy
c.append(5)

def total(xs):
    s = 0
    for x in xs:
        s += x
    return s

print(a, b, c)
print(total(c))`;

const RUN_DEFAULT = `name = input("Your name: ")
langs = {"python": 1991, "go": 2009, "rust": 2010}
print(f"Hi {name}!")
for lang, year in sorted(langs.items(), key=lambda kv: kv[1]):
    print(f"{lang:<8} {year}")`;

const samplesSelect = (samples) =>
  `<select id="sample" style="flex:1 1 260px;max-width:100%"><option value="">Load a sample from the lessons…</option>${samples.map((s, i) => `<option value="${i}">${esc(s.label)}</option>`).join("")}</select>`;

// ===================================================================== visualizer
export function lab(view, content) {
  const samples = sampleOptions(content, ["python"]);
  let steps = [];
  let idx = 0;
  let lines = [];
  let timer;

  view.innerHTML = `
    ${labHero("VIZ", "sky", "Code Visualizer", "Run Python line by line. See which line is about to execute, every frame on the call stack, each variable's value and which names point at the <b>same object</b> (matching colour = same id). Perfect for mutability, scope and recursion.")}
    <div class="panel clay" style="margin-top:1.2rem">
      <div class="row">${samplesSelect(samples)}<button class="btn primary" id="viz">Visualize <kbd>⌘/Ctrl ↵</kbd></button></div>
      <textarea id="code" class="code code-editor" spellcheck="false" rows="10"></textarea>
    </div>
    <div id="vizOut" hidden>
      <div class="filters">
        <button class="btn small" id="first">⏮</button><button class="btn small" id="prev">◀ Prev</button>
        <button class="btn small primary" id="play">Play</button><button class="btn small" id="next">Next ▶</button><button class="btn small" id="last">⏭</button>
        <input type="range" id="scrub" min="0" value="0" style="flex:1 1 200px">
        <span class="muted" id="stepLbl"></span>
      </div>
      <div class="lab-grid halves">
        <div class="panel clay"><h3>Code</h3><div class="viz-code" id="vizCode"></div></div>
        <div class="panel clay"><h3>Frames</h3><div id="frames"></div><h3 style="margin-top:1rem">Output</h3><pre class="term-out" id="vizStdout"></pre></div>
      </div>
      <div id="vizErr"></div>
    </div>`;

  const ta = $("#code");
  ta.value = takeHandoff("py-code") || VIZ_DEFAULT;
  codeEditor(ta, () => visualize(), 4);
  $("#sample").onchange = (e) => {
    if (e.target.value !== "") ta.value = samples[+e.target.value].code;
  };

  const palette = new Map();
  const colorFor = (id) => {
    if (!palette.has(id)) palette.set(id, palette.size % 8);
    return palette.get(id);
  };

  const draw = () => {
    const s = steps[idx];
    if (!s) return;
    const prev = steps[idx - 1];
    $("#scrub").value = idx;
    $("#stepLbl").textContent = `step ${idx + 1} / ${steps.length}${s.event === "return" ? ` · ${s.stack.at(-1).func} returns ${s.returned}` : s.event === "exception" ? " · exception" : ""}`;
    $("#vizCode").innerHTML = lines.map((ln, i) => {
      const n = i + 1;
      const cls = n === s.line ? (s.event === "return" ? "cur ret" : "cur") : prev && n === prev.line ? "prev" : "";
      return `<div class="vl ${cls}"><span class="ln">${n}</span><span class="src">${ln || " "}</span></div>`;
    }).join("");
    $("#vizCode .cur")?.scrollIntoView({ block: "nearest" });
    const counts = {};
    s.stack.forEach((f) => Object.values(f.vars).forEach((v) => (counts[v.id] = (counts[v.id] || 0) + 1)));
    $("#frames").innerHTML = s.stack.map((f, fi) => `
      <div class="frame ${fi === s.stack.length - 1 ? "top" : ""}">
        <div class="frame-h"><b>${esc(f.func === "<module>" ? "global" : f.func + "()")}</b><span class="muted">line ${f.line}</span></div>
        ${Object.entries(f.vars).length ? Object.entries(f.vars).map(([k, v]) => `
          <div class="var ${prev && !prevHas(prev, fi, k, v) ? "changed" : ""}">
            <code>${esc(k)}</code>
            <span class="vtype">${esc(v.type)}</span>
            <span class="vrepr">${esc(v.repr)}</span>
            ${counts[v.id] > 1 && !["int", "str", "bool", "float", "NoneType"].includes(v.type) ? `<span class="alias a${colorFor(v.id)}" title="object id ${v.id}">shared</span>` : ""}
          </div>`).join("") : `<div class="muted">no variables yet</div>`}
      </div>`).join("");
    $("#vizStdout").textContent = s.stdout || "";
  };
  const prevHas = (prev, fi, k, v) => {
    const pv = prev.stack[fi]?.vars[k];
    return pv && pv.repr === v.repr && pv.id === v.id;
  };
  const stop = () => {
    clearInterval(timer);
    timer = null;
    $("#play").textContent = "Play";
  };
  const go = (i) => {
    idx = Math.max(0, Math.min(steps.length - 1, i));
    draw();
  };

  async function visualize() {
    stop();
    $("#viz").disabled = true;
    const r = await runPython(ta.value, { trace: true });
    $("#viz").disabled = false;
    steps = r.steps || [];
    lines = highlightCode(ta.value, "python").split("\n");
    palette.clear();
    $("#vizOut").hidden = false;
    $("#scrub").max = Math.max(0, steps.length - 1);
    const errHtml = r.error ? pyResultHtml({ ...r, stdout: "" }) : "";
    $("#vizErr").innerHTML = (r.truncated ? `<div class="bug-why bad">Trace truncated: only the first ${steps.length} steps are shown.</div>` : "") + errHtml;
    if (!steps.length) {
      $("#vizCode").innerHTML = `<div class="muted">Nothing to step through.</div>`;
      $("#frames").innerHTML = "";
      return;
    }
    go(0);
  }

  $("#viz").onclick = visualize;
  $("#prev").onclick = () => { stop(); go(idx - 1); };
  $("#next").onclick = () => { stop(); go(idx + 1); };
  $("#first").onclick = () => { stop(); go(0); };
  $("#last").onclick = () => { stop(); go(steps.length - 1); };
  $("#scrub").oninput = (e) => { stop(); go(+e.target.value); };
  $("#play").onclick = () => {
    if (timer) return stop();
    if (idx >= steps.length - 1) idx = -1;
    $("#play").textContent = "Pause";
    timer = setInterval(() => {
      go(idx + 1);
      if (idx >= steps.length - 1) stop();
    }, 650);
  };
  const keys = (e) => {
    if (e.target.matches("textarea, input, select") || $("#vizOut").hidden) return;
    if (e.key === "ArrowRight") $("#next").click();
    if (e.key === "ArrowLeft") $("#prev").click();
  };
  document.addEventListener("keydown", keys);
  visualize();
  return () => {
    clearInterval(timer);
    document.removeEventListener("keydown", keys);
  };
}

// ===================================================================== runner
export function playground(view, content) {
  const samples = sampleOptions(content, ["python"]);
  view.innerHTML = `
    ${labHero("PY", "mint", "Python Runner", "Python 3 in an isolated subprocess: no network, no files outside a temp folder, CPU and memory limits, 6 second timeout. Provide stdin for <code>input()</code>.")}
    <div class="lab-grid side-right" style="margin-top:1.2rem">
      <div class="panel clay">
        <div class="row">${samplesSelect(samples)}<button class="btn" id="toViz">Visualize</button><button class="btn primary" id="run">Run <kbd>⌘/Ctrl ↵</kbd></button></div>
        <textarea id="code" class="code code-editor" spellcheck="false" rows="16"></textarea>
      </div>
      <aside class="panel clay"><h3>stdin</h3><textarea id="stdin" class="code short" rows="5" placeholder="One line per input() call">Ada</textarea>
        <p class="muted" style="font-size:.8rem">Standard library only. Try <code>import this</code>, dataclasses, itertools, asyncio.</p></aside>
    </div>
    <div class="panel clay" id="out" style="margin-top:1.2rem"><span class="muted">Output appears here.</span></div>`;
  const ta = $("#code");
  ta.value = takeHandoff("py-code") || RUN_DEFAULT;
  const run = async () => {
    $("#run").disabled = true;
    $("#out").innerHTML = `<span class="muted">Running…</span>`;
    const r = await runPython(ta.value, { stdin: $("#stdin").value });
    $("#run").disabled = false;
    $("#out").innerHTML = pyResultHtml(r);
  };
  codeEditor(ta, run, 4);
  $("#run").onclick = run;
  $("#sample").onchange = (e) => {
    if (e.target.value !== "") ta.value = samples[+e.target.value].code;
  };
  $("#toViz").onclick = () => {
    sessionStorage.setItem("py-code", ta.value);
    location.hash = "#/python/lab";
  };
}
