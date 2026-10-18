import { esc } from "./util.js";

function hpaCalc(root) {
  root.innerHTML = `
    <div class="widget clay">
      <h3>HPA calculator <span class="pill neutral">interactive</span></h3>
      <p class="muted">Move the sliders to see exactly what the HPA controller would decide.</p>
      <div class="sliders">
        <label>Current replicas <span data-o="cur"></span><input type="range" min="1" max="20" value="4" data-k="cur"></label>
        <label>Current avg CPU (% of request) <span data-o="util"></span><input type="range" min="0" max="300" value="90" data-k="util"></label>
        <label>Target utilization <span data-o="target"></span><input type="range" min="10" max="100" value="60" data-k="target"></label>
        <label>minReplicas <span data-o="min"></span><input type="range" min="1" max="10" value="2" data-k="min"></label>
        <label>maxReplicas <span data-o="max"></span><input type="range" min="1" max="30" value="10" data-k="max"></label>
      </div>
      <div class="grid two" style="align-items:center">
        <div class="formula" data-o="formula"></div>
        <div style="text-align:center"><div class="muted">desired replicas</div><div class="big-number" data-o="desired"></div><div class="muted" data-o="note"></div></div>
      </div>
      <div class="replica-row" data-o="pods"></div>
    </div>`;
  const inputs = [...root.querySelectorAll("input")];
  const out = (k) => root.querySelector(`[data-o="${k}"]`);
  const update = () => {
    const v = Object.fromEntries(inputs.map((i) => [i.dataset.k, +i.value]));
    Object.entries(v).forEach(([k, val]) => out(k) && (out(k).textContent = k === "util" || k === "target" ? `${val}%` : val));
    const ratio = v.util / v.target;
    const raw = Math.ceil(v.cur * ratio);
    let desired = Math.abs(ratio - 1) <= 0.1 ? v.cur : raw;
    let note = Math.abs(ratio - 1) <= 0.1 ? "within 10% tolerance: no change" : "";
    const max = Math.max(v.max, v.min);
    if (desired > max) { desired = max; note = "capped by maxReplicas"; }
    if (desired < v.min) { desired = v.min; note = "floored at minReplicas"; }
    out("formula").innerHTML = `ratio = ${v.util}% / ${v.target}% = <b>${ratio.toFixed(2)}</b><br>desired = ceil(${v.cur} × ${ratio.toFixed(2)}) = <b>${raw}</b><br>clamp to [${v.min}, ${max}] → <b>${desired}</b>`;
    out("desired").textContent = desired;
    out("note").textContent = note || (desired > v.cur ? "scale up" : desired < v.cur ? "scale down (after stabilization window)" : "steady");
    const n = Math.max(desired, v.cur);
    out("pods").innerHTML = Array.from({ length: n }, (_, i) => {
      const cls = i < Math.min(desired, v.cur) ? "" : i < desired ? "new" : "gone";
      return `<div class="mini-pod ${cls}" title="${cls || "existing"}"></div>`;
    }).join("");
  };
  inputs.forEach((i) => i.addEventListener("input", update));
  update();
}

function parseCpu(v) {
  if (!v) return null;
  v = v.trim();
  return v.endsWith("m") ? parseFloat(v) : parseFloat(v) * 1000;
}

function parseMem(v) {
  if (!v) return null;
  const m = v.trim().match(/^([\d.]+)\s*(Ki|Mi|Gi|K|M|G)?$/);
  if (!m) return NaN;
  const mult = { Ki: 1 / 1024, Mi: 1, Gi: 1024, K: 0.000954, M: 0.9537, G: 976.6 }[m[2]] ?? 1 / (1024 * 1024);
  return parseFloat(m[1]) * mult;
}

function qosCalc(root) {
  root.innerHTML = `
    <div class="widget clay">
      <h3>QoS class detector <span class="pill neutral">interactive</span></h3>
      <p class="muted">Type requests/limits for a single-container pod (e.g. <code>250m</code>, <code>1</code>, <code>256Mi</code>). Leave a field empty to omit it.</p>
      <div class="sliders">
        <label>requests.cpu<input type="text" data-k="rc" value="250m"></label>
        <label>limits.cpu<input type="text" data-k="lc" value="500m"></label>
        <label>requests.memory<input type="text" data-k="rm" value="256Mi"></label>
        <label>limits.memory<input type="text" data-k="lm" value="256Mi"></label>
      </div>
      <div class="grid two" style="align-items:center">
        <div style="text-align:center"><div class="muted">QoS class</div><div class="big-number" data-o="cls"></div></div>
        <div class="formula" data-o="why"></div>
      </div>
    </div>`;
  const inputs = [...root.querySelectorAll("input")];
  const update = () => {
    const v = Object.fromEntries(inputs.map((i) => [i.dataset.k, i.value.trim()]));
    const rc = parseCpu(v.rc) ?? parseCpu(v.lc);
    const rm = parseMem(v.rm) ?? parseMem(v.lm);
    const lc = parseCpu(v.lc);
    const lm = parseMem(v.lm);
    let cls;
    let why;
    if (!v.rc && !v.lc && !v.rm && !v.lm) {
      cls = "BestEffort";
      why = "No requests or limits at all. Evicted <b>first</b> under node pressure, and it gets whatever is left over.";
    } else if (lc !== null && lm !== null && rc === lc && rm === lm) {
      cls = "Guaranteed";
      why = "CPU and memory limits are set and requests equal limits (omitted requests default to limits). Evicted <b>last</b>, and eligible for exclusive CPUs with the static CPU manager.";
    } else {
      cls = "Burstable";
      why = "Some requests/limits are set but requests ≠ limits. Evicted after BestEffort, ranked by how far usage exceeds requests.";
    }
    const tips = [];
    if (lm !== null && rm !== null && rm > lm) tips.push("requests.memory > limits.memory is rejected by the API server.");
    if (lc === null && v.rc) tips.push("No CPU limit: no throttling (popular for latency-sensitive apps).");
    if (lm === null && (v.rc || v.rm)) tips.push("No memory limit: the container can use node memory until node pressure eviction.");
    root.querySelector('[data-o="cls"]').textContent = cls;
    root.querySelector('[data-o="why"]').innerHTML = why + (tips.length ? `<br><br>${tips.map((t) => `• ${esc(t)}`).join("<br>")}` : "");
  };
  inputs.forEach((i) => i.addEventListener("input", update));
  update();
}

export const WIDGETS = { "hpa-calc": hpaCalc, "qos-calc": qosCalc };
