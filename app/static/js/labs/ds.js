import { $, $$, esc, store } from "../util.js";
import { pyResultHtml, runPython } from "../runners.js";
import { codeEditor, labHero, sampleOptions, takeHandoff } from "./common.js";

// ===================================================================== pure stats helpers
const sorted = (xs) => [...xs].sort((a, b) => a - b);

export const mean = (xs) => (xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : NaN);

export function median(xs) {
  if (!xs.length) return NaN;
  const s = sorted(xs);
  const m = s.length >> 1;
  return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
}

/** Most frequent values (ties included); empty when no value repeats. */
export function mode(xs) {
  const counts = new Map();
  for (const x of xs) counts.set(x, (counts.get(x) || 0) + 1);
  const top = Math.max(0, ...counts.values());
  if (top < 2) return [];
  return sorted([...counts].filter(([, n]) => n === top).map(([v]) => v));
}

export function variance(xs, population = false) {
  const n = xs.length;
  if (n < (population ? 1 : 2)) return NaN;
  const m = mean(xs);
  return xs.reduce((a, x) => a + (x - m) ** 2, 0) / (population ? n : n - 1);
}

/** Sample standard deviation (n - 1) by default, like statistics.stdev; population=true matches pstdev. */
export const std = (xs, population = false) => Math.sqrt(variance(xs, population));

/** Linear interpolation between order statistics (numpy default, statistics.quantiles method="inclusive"). */
export function quantile(xs, q) {
  if (!xs.length) return NaN;
  const s = sorted(xs);
  const h = (s.length - 1) * Math.min(1, Math.max(0, q));
  const lo = Math.floor(h);
  return lo + 1 < s.length ? s[lo] + (h - lo) * (s[lo + 1] - s[lo]) : s[lo];
}

export function pearson(xs, ys) {
  const n = Math.min(xs.length, ys.length);
  if (n < 2) return NaN;
  const mx = mean(xs.slice(0, n));
  const my = mean(ys.slice(0, n));
  let sxy = 0, sxx = 0, syy = 0;
  for (let i = 0; i < n; i++) {
    const dx = xs[i] - mx, dy = ys[i] - my;
    sxy += dx * dy;
    sxx += dx * dx;
    syy += dy * dy;
  }
  return sxx && syy ? sxy / Math.sqrt(sxx * syy) : NaN;
}

/** 1-based ranks; ties share the average rank. */
export function ranks(xs) {
  const idx = xs.map((x, i) => [x, i]).sort((a, b) => a[0] - b[0]);
  const r = new Array(xs.length);
  for (let i = 0; i < idx.length;) {
    let j = i;
    while (j + 1 < idx.length && idx[j + 1][0] === idx[i][0]) j++;
    for (let k = i; k <= j; k++) r[idx[k][1]] = (i + j) / 2 + 1;
    i = j + 1;
  }
  return r;
}

export const spearman = (xs, ys) => pearson(ranks(xs), ranks(ys));

/** Ordinary least squares y = intercept + slope * x. */
export function linreg(xs, ys) {
  const n = Math.min(xs.length, ys.length);
  if (n < 2) return { slope: NaN, intercept: NaN, r2: NaN };
  const mx = mean(xs.slice(0, n));
  const my = mean(ys.slice(0, n));
  let sxy = 0, sxx = 0;
  for (let i = 0; i < n; i++) {
    sxy += (xs[i] - mx) * (ys[i] - my);
    sxx += (xs[i] - mx) ** 2;
  }
  const slope = sxx ? sxy / sxx : NaN;
  const r = pearson(xs, ys);
  return { slope, intercept: my - slope * mx, r2: r * r };
}

// Chebyshev fit of erfc (Numerical Recipes), fractional error below 1.2e-7 everywhere.
function erfc(x) {
  const z = Math.abs(x);
  const t = 1 / (1 + 0.5 * z);
  const r = t * Math.exp(-z * z - 1.26551223 + t * (1.00002368 + t * (0.37409196 + t * (0.09678418 + t * (-0.18628806 + t * (0.27886807 + t * (-1.13520398 + t * (1.48851587 + t * (-0.82215223 + t * 0.17087277)))))))));
  return x >= 0 ? r : 2 - r;
}

export const normalCdf = (z) => 0.5 * erfc(-z / Math.SQRT2);

/** Inverse standard normal CDF (Acklam), relative error below 1.2e-9. */
export function normalInv(p) {
  if (p <= 0) return -Infinity;
  if (p >= 1) return Infinity;
  const a = [-39.69683028665376, 220.9460984245205, -275.9285104469687, 138.357751867269, -30.66479806614716, 2.506628277459239];
  const b = [-54.47609879822406, 161.5858368580409, -155.6989798598866, 66.80131188771972, -13.28068155288572];
  const c = [-0.007784894002430293, -0.3223964580411365, -2.400758277161838, -2.549732539343734, 4.374664141464968, 2.938163982698783];
  const d = [0.007784695709041462, 0.3224671290700398, 2.445134137142996, 3.754408661907416];
  const lo = 0.02425;
  if (p < lo || p > 1 - lo) {
    const q = Math.sqrt(-2 * Math.log(p < lo ? p : 1 - p));
    const v = (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1);
    return p < lo ? v : -v;
  }
  const q = p - 0.5;
  const r = q * q;
  return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1);
}

/** Two-sided two-proportion z-test (pooled SE) plus a Wald CI (unpooled SE) for pB - pA. */
export function zTestTwoProp(nA, cA, nB, cB, alpha = 0.05) {
  const pA = cA / nA, pB = cB / nB, diff = pB - pA;
  const pooled = (cA + cB) / (nA + nB);
  const se0 = Math.sqrt(pooled * (1 - pooled) * (1 / nA + 1 / nB));
  const z = se0 ? diff / se0 : 0;
  const p = se0 ? 2 * normalCdf(-Math.abs(z)) : 1;
  const se = Math.sqrt(pA * (1 - pA) / nA + pB * (1 - pB) / nB);
  const zc = normalInv(1 - alpha / 2);
  return { pA, pB, diff, lift: pA ? diff / pA : NaN, z, p, se, ci: [diff - zc * se, diff + zc * se] };
}

/** Visitors needed per variant to detect an absolute lift of `mde` over `baseline` (two-sided). */
export function sampleSize(baseline, mde, alpha = 0.05, power = 0.8) {
  const p1 = baseline, p2 = baseline + mde;
  if (!(mde > 0) || p1 <= 0 || p2 >= 1) return NaN;
  const pbar = (p1 + p2) / 2;
  const za = normalInv(1 - alpha / 2), zb = normalInv(power);
  const n = (za * Math.sqrt(2 * pbar * (1 - pbar)) + zb * Math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2 / mde ** 2;
  return Math.ceil(n);
}

/** Seeded PRNG (mulberry32) for reproducible simulations; not for anything security related. */
export function rng(seed) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const gauss = (r) => {
  let u = 0;
  while (!u) u = r();
  return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * r());
};

export function histogram(xs, lo, hi, bins) {
  const counts = new Array(bins).fill(0);
  const w = (hi - lo) / bins;
  for (const x of xs) {
    if (x < lo || x > hi) continue;
    counts[Math.min(bins - 1, Math.floor((x - lo) / w))]++;
  }
  return counts;
}

// ===================================================================== shared UI bits
const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));
const fmt = (v, d = 2) => (Number.isFinite(v) ? (+v.toFixed(d)).toString() : "n/a");
const pct = (v, d = 1) => (Number.isFinite(v) ? `${(v * 100).toFixed(d)}%` : "n/a");
const kpis = (items) => items.map(([k, v, tone = "neutral"]) => `<div class="panel clay stat-card"><span class="muted">${esc(k)}</span><b class="pill ${tone}">${esc(v)}</b></div>`).join("");

/** Pointer handling for SVG plots that re-render their own innerHTML while dragging. */
function plotPointer(svg, h) {
  let drag = null;
  const pt = (e) => {
    const p = svg.createSVGPoint();
    p.x = e.clientX;
    p.y = e.clientY;
    return p.matrixTransform(svg.getScreenCTM().inverse());
  };
  svg.addEventListener("pointerdown", (e) => {
    if (e.button > 0) return;
    const dot = e.target.closest("[data-i]");
    if (dot) {
      const i = +dot.dataset.i;
      if (h.removing() || e.shiftKey || e.altKey) return h.remove(i);
      drag = i;
    } else {
      drag = h.add(pt(e));
      if (drag == null) return;
    }
    e.preventDefault();
    svg.setPointerCapture(e.pointerId);
  });
  svg.addEventListener("pointermove", (e) => {
    if (drag != null) h.move(drag, pt(e));
  });
  const end = () => {
    if (drag == null) return;
    drag = null;
    h.done?.();
  };
  svg.addEventListener("pointerup", end);
  svg.addEventListener("pointercancel", end);
}

// ===================================================================== distribution
const DIST_PRESETS = {
  normal: { label: "Normal-ish", note: "Symmetric: mean and median sit together and the box plot is balanced." },
  skewed: { label: "Right-skewed", note: "A long right tail (think incomes or wait times) pulls the mean above the median. Report the median here." },
  bimodal: { label: "Bimodal", note: "Two clusters: the mean and median land in the valley where almost nobody is. Always plot before summarising." },
  outlier: { label: "With outlier", note: "One extreme value moves the mean and inflates the std dev, while the median and IQR barely change. Drag it in and out." },
};

export function distPreset(key) {
  const r = rng({ normal: 11, skewed: 23, bimodal: 37, outlier: 41 }[key]);
  const out = [];
  if (key === "normal") for (let i = 0; i < 30; i++) out.push(50 + 10 * gauss(r));
  if (key === "skewed") for (let i = 0; i < 30; i++) out.push(12 + -14 * Math.log(1 - r()));
  if (key === "bimodal") for (let i = 0; i < 30; i++) out.push((i % 2 ? 72 : 28) + 6 * gauss(r));
  if (key === "outlier") {
    for (let i = 0; i < 19; i++) out.push(42 + 6 * gauss(r));
    out.push(97);
  }
  return out.map((v) => clamp(Math.round(v), 0, 100));
}

export function describe(xs) {
  const q1 = quantile(xs, 0.25), q3 = quantile(xs, 0.75), iqr = q3 - q1;
  const fences = [q1 - 1.5 * iqr, q3 + 1.5 * iqr];
  const inside = xs.filter((x) => x >= fences[0] && x <= fences[1]);
  return {
    n: xs.length, mean: mean(xs), median: median(xs), mode: mode(xs), std: std(xs),
    q1, q3, iqr, fences,
    whiskers: inside.length ? [Math.min(...inside), Math.max(...inside)] : [NaN, NaN],
    outliers: xs.filter((x) => x < fences[0] || x > fences[1]),
  };
}

function distributionTab(pane) {
  const saved = store.get("ds-dist", null);
  let data = Array.isArray(saved) ? saved.filter(Number.isFinite) : distPreset("skewed");
  let note = DIST_PRESETS.skewed.note;
  pane.innerHTML = `
    <div class="filters"><span class="muted">Presets:</span>${Object.entries(DIST_PRESETS).map(([k, p]) => `<button class="btn small" data-preset="${k}">${esc(p.label)}</button>`).join("")}
      <button class="btn small" data-act="clear">Clear</button>
      <label class="check dsx-inline"><input type="checkbox" id="dsxDistRm"> Click a dot to remove</label></div>
    <div class="lab-grid side-right">
      <div class="lab-main">
        <div class="panel clay dsx-plot">
          <svg id="dsxDist" class="dsx-svg" viewBox="0 0 640 300" role="img" aria-label="Dot plot, histogram and box plot of the dataset"></svg>
          <p class="muted dsx-hint">Click empty space to add a value, drag a dot to move it, Shift-click (or tick the box) to remove. Values run 0 to 100.</p>
        </div>
        <div class="dsx-kpis" id="dsxDistStats"></div>
      </div>
      <aside class="panel clay">
        <h3>What it shows</h3>
        <p id="dsxDistNote" class="dsx-note"></p>
        <ul class="clean tips" id="dsxDistTips"></ul>
        <label>Values (edit directly)<textarea id="dsxDistData" class="code short" rows="4" spellcheck="false"></textarea></label>
      </aside>
    </div>`;
  const svg = $("#dsxDist", pane);
  const X0 = 36, X1 = 620, BASE = 196, TOP = 26;
  const sx = (v) => X0 + (v / 100) * (X1 - X0);
  const vx = (px) => clamp(Math.round(((px - X0) / (X1 - X0)) * 100), 0, 100);

  const render = (syncText = true) => {
    const d = describe(data);
    const out = new Set(d.outliers);
    const hist = histogram(data, 0, 100, 10);
    const maxH = Math.max(1, ...hist);
    const bars = hist.map((c, i) => {
      const h = (c / maxH) * (BASE - TOP - 8);
      return `<rect class="dsx-bar" x="${sx(i * 10) + 1}" y="${BASE - h}" width="${sx(10) - sx(0) - 2}" height="${h}" rx="4"/>`;
    }).join("");
    const stack = new Map();
    const order = data.map((v, i) => [v, i]).sort((a, b) => a[0] - b[0]);
    const dots = order.map(([v, i]) => {
      const bin = Math.floor(v / 2);
      const k = stack.get(bin) || 0;
      stack.set(bin, k + 1);
      return `<circle data-i="${i}" class="dsx-dot${out.has(v) ? " out" : ""}" cx="${sx(v)}" cy="${Math.max(TOP, BASE - 6 - k * 10)}" r="5"><title>${v}</title></circle>`;
    }).join("");
    const ticks = Array.from({ length: 11 }, (_, i) => `<line class="dsx-tick" x1="${sx(i * 10)}" x2="${sx(i * 10)}" y1="${BASE}" y2="${BASE + 5}"/><text class="dsx-lbl" x="${sx(i * 10)}" y="${BASE + 18}" text-anchor="middle">${i * 10}</text>`).join("");
    let box = "", lines = "";
    if (data.length) {
      const by = 248;
      box = `<line class="dsx-whisk" x1="${sx(d.whiskers[0])}" x2="${sx(d.q1)}" y1="${by}" y2="${by}"/><line class="dsx-whisk" x1="${sx(d.q3)}" x2="${sx(d.whiskers[1])}" y1="${by}" y2="${by}"/>
        <line class="dsx-whisk" x1="${sx(d.whiskers[0])}" x2="${sx(d.whiskers[0])}" y1="${by - 8}" y2="${by + 8}"/><line class="dsx-whisk" x1="${sx(d.whiskers[1])}" x2="${sx(d.whiskers[1])}" y1="${by - 8}" y2="${by + 8}"/>
        <rect class="dsx-box" x="${sx(d.q1)}" y="${by - 13}" width="${Math.max(1, sx(d.q3) - sx(d.q1))}" height="26" rx="5"/>
        <line class="dsx-med" x1="${sx(d.median)}" x2="${sx(d.median)}" y1="${by - 13}" y2="${by + 13}"/>
        ${d.outliers.map((v) => `<circle class="dsx-dot out" cx="${sx(v)}" cy="${by}" r="4"/>`).join("")}`;
      lines = `<line class="dsx-mean" x1="${sx(d.mean)}" x2="${sx(d.mean)}" y1="${TOP - 10}" y2="${BASE}"/><text class="dsx-lbl mean" x="${sx(d.mean)}" y="${TOP - 13}" text-anchor="middle">mean ${fmt(d.mean, 1)}</text>
        <line class="dsx-med" x1="${sx(d.median)}" x2="${sx(d.median)}" y1="${TOP}" y2="${BASE}"/><text class="dsx-lbl med" x="${sx(d.median)}" y="${292}" text-anchor="middle">median ${fmt(d.median, 1)}</text>`;
    }
    svg.innerHTML = `<rect class="dsx-hit" x="0" y="0" width="640" height="300"/>${bars}${lines}<line class="dsx-axis" x1="${X0}" x2="${X1}" y1="${BASE}" y2="${BASE}"/>${ticks}${box}${dots}
      ${data.length ? "" : `<text class="dsx-lbl" x="320" y="110" text-anchor="middle">Click anywhere to add values</text>`}`;
    const skew = d.mean - d.median;
    const shape = data.length < 3 ? "too few points" : Math.abs(skew) < 0.1 * (d.std || 1) ? "roughly symmetric" : skew > 0 ? "right-skewed" : "left-skewed";
    $("#dsxDistStats", pane).innerHTML = kpis([
      ["n", d.n],
      ["Mean", fmt(d.mean, 2)],
      ["Median", fmt(d.median, 2)],
      ["Mode", d.mode.length ? (d.mode.length > 3 ? `${d.mode.slice(0, 3).join(", ")}, ...` : d.mode.join(", ")) : "none"],
      ["Std dev (sample)", fmt(d.std, 2)],
      ["IQR", data.length ? `${fmt(d.iqr, 2)} (${fmt(d.q1, 1)} to ${fmt(d.q3, 1)})` : "n/a"],
      ["Outliers (1.5 IQR)", d.outliers.length ? sorted(d.outliers).join(", ") : "none", d.outliers.length ? "bad" : "ok"],
      ["Shape", shape, shape.includes("skewed") ? "warn" : "neutral"],
    ]);
    $("#dsxDistNote", pane).textContent = note;
    $("#dsxDistTips", pane).innerHTML = data.length ? [
      `Mean minus median is ${fmt(skew, 2)}. ${Math.abs(skew) < 0.1 * (d.std || 1) ? "They agree, so either is a fair summary." : skew > 0 ? "The mean is pulled up by the high tail." : "The mean is pulled down by the low tail."}`,
      `Outlier fences: below ${fmt(d.fences[0], 1)} or above ${fmt(d.fences[1], 1)} (Q1 - 1.5 IQR, Q3 + 1.5 IQR).`,
      "The box covers the middle 50% of values; whiskers reach the furthest values inside the fences.",
    ].map((t) => `<li>${esc(t)}</li>`).join("") : "";
    const ta = $("#dsxDistData", pane);
    if (syncText && document.activeElement !== ta) ta.value = data.join(", ");
  };
  const save = () => store.set("ds-dist", data);

  plotPointer(svg, {
    removing: () => $("#dsxDistRm", pane).checked,
    add: (p) => {
      if (data.length >= 200 || p.y > 290) return null;
      data.push(vx(p.x));
      render();
      return data.length - 1;
    },
    move: (i, p) => {
      data[i] = vx(p.x);
      render();
    },
    remove: (i) => {
      data.splice(i, 1);
      render();
      save();
    },
    done: save,
  });
  pane.addEventListener("click", (e) => {
    const b = e.target.closest("[data-preset],[data-act]");
    if (!b) return;
    if (b.dataset.act === "clear") {
      data = [];
      note = "Empty dataset. Click the plot to build your own.";
    } else {
      data = distPreset(b.dataset.preset);
      note = DIST_PRESETS[b.dataset.preset].note;
    }
    render();
    save();
  });
  $("#dsxDistData", pane).addEventListener("input", (e) => {
    data = (e.target.value.match(/-?\d+(\.\d+)?/g) || []).slice(0, 200).map((v) => clamp(Math.round(+v), 0, 100));
    render(false);
    save();
  });
  render();
}

// ===================================================================== correlation
const CORR_PRESETS = {
  linear: { label: "Strong positive", note: "Points hug a rising line: r close to +1 and the line explains most of the variance (high R squared)." },
  none: { label: "No relationship", note: "A cloud: r near 0. Random samples still show small non-zero r by chance." },
  curved: { label: "Curved", note: "Always increasing but not straight. Spearman (ranks) is near 1; Pearson only measures the straight-line part." },
  outlier: { label: "Outlier flips r", note: "The cluster trends downward, but one far point drags r positive. Drag it into the cluster and watch r change sign." },
  simpson: { label: "Simpson's paradox", note: "Inside each group the trend is positive, yet pooled together it is negative, because group membership drives both x and y." },
};

export function corrPreset(key) {
  const r = rng({ linear: 5, none: 7, curved: 13, outlier: 17, simpson: 19 }[key]);
  const pts = [];
  const add = (x, y, g = 0) => pts.push({ x: clamp(Math.round(x), 0, 100), y: clamp(Math.round(y), 0, 100), g });
  if (key === "linear") for (let i = 0; i < 25; i++) { const x = 5 + r() * 90; add(x, 10 + 0.8 * x + 7 * gauss(r)); }
  if (key === "none") for (let i = 0; i < 25; i++) add(5 + r() * 90, 5 + r() * 90);
  if (key === "curved") for (let i = 0; i < 22; i++) { const x = 4 + i * 4.3; add(x, 3 + 95 * (x / 100) ** 4 + 2 * gauss(r)); }
  if (key === "outlier") {
    for (let i = 0; i < 14; i++) { const x = 10 + r() * 30; add(x, 50 - 0.6 * x + 5 * gauss(r)); }
    add(95, 95);
  }
  if (key === "simpson") {
    for (let i = 0; i < 12; i++) { const x = 8 + r() * 32; add(x, 42 + 0.9 * x + 5 * gauss(r), 0); }
    for (let i = 0; i < 12; i++) { const x = 58 + r() * 34; add(x, -40 + 0.9 * x + 5 * gauss(r), 1); }
  }
  return pts;
}

function correlationTab(pane) {
  const saved = store.get("ds-corr", null);
  let pts = Array.isArray(saved) ? saved.filter((p) => Number.isFinite(p?.x) && Number.isFinite(p?.y)) : corrPreset("outlier");
  let note = CORR_PRESETS.outlier.note;
  pane.innerHTML = `
    <div class="filters"><span class="muted">Presets:</span>${Object.entries(CORR_PRESETS).map(([k, p]) => `<button class="btn small" data-preset="${k}">${esc(p.label)}</button>`).join("")}
      <button class="btn small" data-act="clear">Clear</button>
      <label class="check dsx-inline"><input type="checkbox" id="dsxCorrRm"> Click a point to remove</label></div>
    <div class="lab-grid halves">
      <div class="panel clay dsx-plot">
        <svg id="dsxCorr" class="dsx-svg dsx-square" viewBox="0 0 420 420" role="img" aria-label="Scatter plot with least-squares line"></svg>
        <p class="muted dsx-hint">Drag points, click empty space to add, Shift-click to remove.</p>
      </div>
      <div class="lab-main">
        <div class="dsx-kpis" id="dsxCorrStats"></div>
        <div class="panel clay"><h3>Reading it</h3><p id="dsxCorrNote" class="dsx-note"></p><ul class="clean tips" id="dsxCorrTips"></ul></div>
      </div>
    </div>`;
  const svg = $("#dsxCorr", pane);
  const P0 = 44, P1 = 404;
  const sx = (v) => P0 + (v / 100) * (P1 - P0);
  const sy = (v) => P1 - (v / 100) * (P1 - P0);
  const toV = (p) => ({ x: clamp(Math.round(((p.x - P0) / (P1 - P0)) * 100), 0, 100), y: clamp(Math.round(((P1 - p.y) / (P1 - P0)) * 100), 0, 100) });
  const lineOf = (xs, ys, cls) => {
    const { slope, intercept } = linreg(xs, ys);
    if (!Number.isFinite(slope)) return "";
    return `<line class="${cls}" x1="${sx(0)}" y1="${sy(intercept)}" x2="${sx(100)}" y2="${sy(intercept + slope * 100)}" clip-path="url(#dsxClip)"/>`;
  };

  const render = () => {
    const xs = pts.map((p) => p.x), ys = pts.map((p) => p.y);
    const groups = [...new Set(pts.map((p) => p.g || 0))].sort();
    const multi = groups.length > 1;
    const grid = [0, 20, 40, 60, 80, 100].map((v) => `<line class="dsx-grid" x1="${sx(v)}" x2="${sx(v)}" y1="${P0}" y2="${P1}"/><line class="dsx-grid" x1="${P0}" x2="${P1}" y1="${sy(v)}" y2="${sy(v)}"/><text class="dsx-lbl" x="${sx(v)}" y="${P1 + 16}" text-anchor="middle">${v}</text><text class="dsx-lbl" x="${P0 - 8}" y="${sy(v) + 4}" text-anchor="end">${v}</text>`).join("");
    const groupLines = multi ? groups.map((g) => {
      const sub = pts.filter((p) => (p.g || 0) === g);
      return lineOf(sub.map((p) => p.x), sub.map((p) => p.y), `dsx-fit g${g} dashed`);
    }).join("") : "";
    svg.innerHTML = `<defs><clipPath id="dsxClip"><rect x="${P0}" y="${P0}" width="${P1 - P0}" height="${P1 - P0}"/></clipPath></defs>
      <rect class="dsx-hit" x="0" y="0" width="420" height="420"/>${grid}
      <text class="dsx-lbl" x="${(P0 + P1) / 2}" y="418" text-anchor="middle">x</text><text class="dsx-lbl" x="12" y="${(P0 + P1) / 2}" text-anchor="middle">y</text>
      ${groupLines}${lineOf(xs, ys, "dsx-fit")}
      ${pts.map((p, i) => `<circle data-i="${i}" class="dsx-pt g${p.g || 0}" cx="${sx(p.x)}" cy="${sy(p.y)}" r="7"><title>(${p.x}, ${p.y})</title></circle>`).join("")}`;
    const r = pearson(xs, ys), rho = spearman(xs, ys), fit = linreg(xs, ys);
    const tone = (v) => (!Number.isFinite(v) ? "neutral" : Math.abs(v) >= 0.7 ? "ok" : Math.abs(v) >= 0.3 ? "warn" : "neutral");
    const items = [
      ["n", pts.length],
      ["Pearson r", fmt(r, 3), tone(r)],
      ["Spearman rho", fmt(rho, 3), tone(rho)],
      ["Least-squares line", Number.isFinite(fit.slope) ? `y = ${fmt(fit.intercept, 2)} ${fit.slope < 0 ? "-" : "+"} ${fmt(Math.abs(fit.slope), 3)}x` : "n/a"],
      ["R squared", fmt(fit.r2, 3)],
    ];
    if (multi) groups.forEach((g) => {
      const sub = pts.filter((p) => (p.g || 0) === g);
      items.push([`r inside group ${"AB"[g] || g}`, fmt(pearson(sub.map((p) => p.x), sub.map((p) => p.y)), 3), tone(pearson(sub.map((p) => p.x), sub.map((p) => p.y)))]);
    });
    $("#dsxCorrStats", pane).innerHTML = kpis(items);
    $("#dsxCorrNote", pane).textContent = note;
    $("#dsxCorrTips", pane).innerHTML = [
      Number.isFinite(fit.r2) ? `The line explains ${pct(fit.r2, 0)} of the variance in y.` : "Add at least two points with different x values.",
      Number.isFinite(r) && Number.isFinite(rho) && Math.abs(rho - r) > 0.15 ? "Pearson and Spearman disagree: look for curvature or an influential point." : "Pearson and Spearman agree, so the pattern is close to linear.",
      "Correlation is not causation: a lurking variable (like the group colour) can create or reverse a trend.",
    ].map((t) => `<li>${esc(t)}</li>`).join("");
  };
  const save = () => store.set("ds-corr", pts);

  plotPointer(svg, {
    removing: () => $("#dsxCorrRm", pane).checked,
    add: (p) => {
      if (pts.length >= 150) return null;
      const v = toV(p);
      const near = pts.reduce((best, q) => (!best || (q.x - v.x) ** 2 + (q.y - v.y) ** 2 < (best.x - v.x) ** 2 + (best.y - v.y) ** 2 ? q : best), null);
      pts.push({ ...v, g: near?.g || 0 });
      render();
      return pts.length - 1;
    },
    move: (i, p) => {
      pts[i] = { ...pts[i], ...toV(p) };
      render();
    },
    remove: (i) => {
      pts.splice(i, 1);
      render();
      save();
    },
    done: save,
  });
  pane.addEventListener("click", (e) => {
    const b = e.target.closest("[data-preset],[data-act]");
    if (!b) return;
    if (b.dataset.act === "clear") {
      pts = [];
      note = "Empty plot. Click to add points and build a pattern.";
    } else {
      pts = corrPreset(b.dataset.preset);
      note = CORR_PRESETS[b.dataset.preset].note;
    }
    render();
    save();
  });
  render();
}

// ===================================================================== A/B test
function abTab(pane) {
  const s = { nA: 2400, cA: 120, nB: 2400, cB: 156, mde: 1, power: 0.8, ...store.get("ds-ab", {}) };
  pane.innerHTML = `
    <div class="lab-grid side-left">
      <aside class="panel clay dsx-form">
        <h3>Variant A (control)</h3>
        <label>Visitors<input type="number" min="1" step="1" data-k="nA"></label>
        <label>Conversions<input type="number" min="0" step="1" data-k="cA"></label>
        <h3>Variant B</h3>
        <label>Visitors<input type="number" min="1" step="1" data-k="nB"></label>
        <label>Conversions<input type="number" min="0" step="1" data-k="cB"></label>
        <hr>
        <label>Minimum detectable effect (percentage points)<input type="number" min="0.1" step="0.1" data-k="mde"></label>
        <label>Power<select data-k="power"><option value="0.8">80%</option><option value="0.9">90%</option></select></label>
        <p class="muted dsx-hint">Significance level 5%, two-sided.</p>
      </aside>
      <div class="lab-main">
        <div class="dsx-kpis" id="dsxAbStats"></div>
        <div class="panel clay dsx-plot"><h3>95% confidence interval for B minus A</h3><svg id="dsxAbCi" class="dsx-svg dsx-wide" viewBox="0 0 640 110" role="img" aria-label="Confidence interval of the difference"></svg></div>
        <div class="panel clay" id="dsxAbVerdict"></div>
      </div>
    </div>`;
  $$("[data-k]", pane).forEach((i) => (i.value = s[i.dataset.k]));

  const render = () => {
    const { nA, cA, nB, cB, mde, power } = s;
    const valid = [nA, nB].every((n) => Number.isInteger(n) && n > 0) && [cA, cB].every((c) => Number.isInteger(c) && c >= 0) && cA <= nA && cB <= nB;
    if (!valid) {
      $("#dsxAbStats", pane).innerHTML = "";
      $("#dsxAbCi", pane).innerHTML = "";
      $("#dsxAbVerdict", pane).innerHTML = `<div class="bug-why bad">Visitors must be whole numbers above 0 and conversions between 0 and the visitor count.</div>`;
      return;
    }
    const t = zTestTwoProp(nA, cA, nB, cB);
    const need = sampleSize(t.pA, mde / 100, 0.05, power);
    const sig = t.p < 0.05;
    const enough = Number.isFinite(need) && Math.min(nA, nB) >= need;
    $("#dsxAbStats", pane).innerHTML = kpis([
      ["Rate A", pct(t.pA, 2)],
      ["Rate B", pct(t.pB, 2)],
      ["Difference", `${t.diff >= 0 ? "+" : ""}${fmt(t.diff * 100, 2)} pp (${t.lift >= 0 ? "+" : ""}${pct(t.lift, 1)} relative)`],
      ["z", fmt(t.z, 3)],
      ["p-value", t.p < 0.0001 ? "< 0.0001" : fmt(t.p, 4), sig ? "ok" : "warn"],
      ["95% CI (pp)", `${fmt(t.ci[0] * 100, 2)} to ${fmt(t.ci[1] * 100, 2)}`, sig ? "ok" : "warn"],
      ["Needed per variant", Number.isFinite(need) ? need.toLocaleString("en-US") : "n/a", enough ? "ok" : "bad"],
    ]);
    const span = Math.max(Math.abs(t.ci[0]), Math.abs(t.ci[1]), mde / 100) * 1.3 || 0.01;
    const X0 = 30, X1 = 610;
    const sx = (v) => X0 + ((v + span) / (2 * span)) * (X1 - X0);
    const tickStep = span * 100 > 6 ? 2 : span * 100 > 3 ? 1 : span * 100 > 1.2 ? 0.5 : 0.2;
    const ticks = [];
    for (let v = -Math.floor((span * 100) / tickStep) * tickStep; v <= span * 100 + 1e-9; v += tickStep) ticks.push(+v.toFixed(2));
    $("#dsxAbCi", pane).innerHTML = `
      <line class="dsx-axis" x1="${X0}" x2="${X1}" y1="70" y2="70"/>
      ${ticks.map((v) => `<line class="dsx-tick" x1="${sx(v / 100)}" x2="${sx(v / 100)}" y1="70" y2="75"/><text class="dsx-lbl" x="${sx(v / 100)}" y="92" text-anchor="middle">${v > 0 ? "+" : ""}${v}</text>`).join("")}
      <rect class="dsx-mde" x="${sx(-mde / 100)}" y="18" width="${sx(mde / 100) - sx(-mde / 100)}" height="56"/>
      <text class="dsx-lbl" x="${sx(mde / 100) + 4}" y="28">MDE band</text>
      <line class="dsx-zero" x1="${sx(0)}" x2="${sx(0)}" y1="12" y2="78"/>
      <line class="dsx-ci ${sig ? "sig" : ""}" x1="${sx(t.ci[0])}" x2="${sx(t.ci[1])}" y1="46" y2="46"/>
      <line class="dsx-ci ${sig ? "sig" : ""}" x1="${sx(t.ci[0])}" x2="${sx(t.ci[0])}" y1="38" y2="54"/><line class="dsx-ci ${sig ? "sig" : ""}" x1="${sx(t.ci[1])}" x2="${sx(t.ci[1])}" y1="38" y2="54"/>
      <circle class="dsx-est" cx="${sx(t.diff)}" cy="46" r="6"/>
      <text class="dsx-lbl" x="${X1}" y="106" text-anchor="end">difference in percentage points</text>`;
    const better = t.diff > 0 ? "higher" : "lower";
    const lines = [];
    if (sig) lines.push(`<b>Significant.</b> B converts ${better} than A by ${fmt(Math.abs(t.diff) * 100, 2)} percentage points. If A and B were truly identical, a gap at least this large would show up only ${t.p < 0.0001 ? "less than 0.01%" : pct(t.p, 2)} of the time, and the 95% interval (${fmt(t.ci[0] * 100, 2)} to ${fmt(t.ci[1] * 100, 2)} pp) does not include zero.`);
    else lines.push(`<b>Not significant.</b> The observed gap of ${fmt(t.diff * 100, 2)} pp could easily be noise (p = ${fmt(t.p, 3)}). The interval ${fmt(t.ci[0] * 100, 2)} to ${fmt(t.ci[1] * 100, 2)} pp includes zero, so B could be worse, the same, or better.`);
    if (Number.isFinite(need)) lines.push(enough
      ? `Sample size is adequate: detecting a ${fmt(mde, 2)} pp change from a ${pct(t.pA, 1)} baseline with ${Math.round(power * 100)}% power needs about ${need.toLocaleString("en-US")} visitors per variant, and you have ${Math.min(nA, nB).toLocaleString("en-US")}.`
      : `Underpowered: detecting a ${fmt(mde, 2)} pp change from a ${pct(t.pA, 1)} baseline with ${Math.round(power * 100)}% power needs about ${need.toLocaleString("en-US")} visitors per variant, and you have ${Math.min(nA, nB).toLocaleString("en-US")}. Fix the sample size up front and do not stop the test the first time p dips below 0.05.`);
    else lines.push("Pick an MDE that keeps baseline + MDE below 100% to get a sample size.");
    lines.push("Statistical significance is not business significance: compare the interval with the smallest lift that would be worth shipping.");
    $("#dsxAbVerdict", pane).innerHTML = `<h3>Verdict</h3>${lines.map((l) => `<p class="dsx-note">${l}</p>`).join("")}`;
  };

  pane.addEventListener("input", (e) => {
    const k = e.target.dataset.k;
    if (!k) return;
    s[k] = e.target.value === "" ? NaN : +e.target.value;
    store.set("ds-ab", s);
    render();
  });
  render();
}

// ===================================================================== central limit theorem
const POPS = {
  skewed: { label: "Skewed (wait times)", make: (r) => -5 * Math.log(1 - r()) },
  uniform: { label: "Uniform", make: (r) => r() * 10 },
  bimodal: { label: "Bimodal", make: (r) => (r() < 0.5 ? 2.5 + 0.8 * gauss(r) : 8 + 1.1 * gauss(r)) },
};

function cltTab(pane) {
  const s = { pop: "skewed", n: 5, seed: 42, ...store.get("ds-clt", {}) };
  let pop, lo, hi, mu, sigma, draw, means, last, timer;
  pane.innerHTML = `
    <div class="lab-grid side-left">
      <aside class="panel clay dsx-form">
        <label>Population<select id="dsxPop">${Object.entries(POPS).map(([k, p]) => `<option value="${k}">${esc(p.label)}</option>`).join("")}</select></label>
        <label>Sample size n <b id="dsxNV"></b><input type="range" id="dsxN" min="1" max="60" step="1"></label>
        <label>Seed<input type="number" id="dsxSeed" min="0" step="1"></label>
        <div class="row dsx-btns">
          <button class="btn small" data-draw="1">Draw 1</button><button class="btn small" data-draw="100">Draw 100</button>
          <button class="btn small" data-draw="1000">Draw 1000</button><button class="btn small primary" id="dsxAuto">Auto</button>
          <button class="btn small" id="dsxReset">Reset</button>
        </div>
        <p class="muted dsx-hint">Each draw takes n values (with replacement) from a synthetic population of 20,000 and records their mean.</p>
      </aside>
      <div class="lab-main">
        <div class="panel clay dsx-plot"><h3>Population</h3><svg id="dsxPopSvg" class="dsx-svg dsx-wide" viewBox="0 0 640 150" role="img" aria-label="Population histogram"></svg></div>
        <div class="panel clay dsx-plot"><h3>Sample means</h3><svg id="dsxMeanSvg" class="dsx-svg" viewBox="0 0 640 230" role="img" aria-label="Histogram of sample means with normal curve"></svg></div>
        <div class="dsx-kpis" id="dsxCltStats"></div>
      </div>
    </div>`;
  const BINS = 40, X0 = 20, X1 = 620;
  const sx = (v) => X0 + ((v - lo) / (hi - lo)) * (X1 - X0);
  const binW = () => (hi - lo) / BINS;

  const build = () => {
    const r = rng(s.seed);
    pop = Array.from({ length: 20000 }, () => POPS[s.pop].make(r));
    lo = Math.min(0, quantile(pop, 0.001));
    hi = quantile(pop, 0.995);
    mu = mean(pop);
    sigma = std(pop, true);
    draw = rng(s.seed * 7919 + 1);
    means = [];
    last = null;
  };
  const sampleOnce = () => {
    const xs = Array.from({ length: s.n }, () => pop[Math.floor(draw() * pop.length)]);
    last = xs;
    means.push(mean(xs));
  };
  const barsSvg = (counts, H, base, cls) => {
    const max = Math.max(1, ...counts);
    const w = (X1 - X0) / BINS;
    return { max, html: counts.map((c, i) => { const h = (c / max) * (base - 14); return `<rect class="${cls}" x="${X0 + i * w + 0.5}" y="${base - h}" width="${Math.max(0.5, w - 1)}" height="${h}" rx="2"/>`; }).join("") };
  };
  const axis = (base) => {
    const step = (hi - lo) > 12 ? 5 : (hi - lo) > 6 ? 2 : 1;
    let out = `<line class="dsx-axis" x1="${X0}" x2="${X1}" y1="${base}" y2="${base}"/>`;
    for (let v = Math.ceil(lo / step) * step; v <= hi; v += step) out += `<text class="dsx-lbl" x="${sx(v)}" y="${base + 15}" text-anchor="middle">${v}</text>`;
    return out;
  };

  const render = () => {
    $("#dsxNV", pane).textContent = s.n;
    const pb = barsSvg(histogram(pop, lo, hi, BINS), 150, 124, "dsx-bar pop");
    $("#dsxPopSvg", pane).innerHTML = `${pb.html}${axis(124)}
      <line class="dsx-mean" x1="${sx(mu)}" x2="${sx(mu)}" y1="8" y2="124"/><text class="dsx-lbl mean" x="${sx(mu) + 5}" y="16">mu ${fmt(mu, 2)}</text>
      ${last ? last.filter((v) => v <= hi).map((v) => `<line class="dsx-samp" x1="${sx(v)}" x2="${sx(v)}" y1="112" y2="124"/>`).join("") : ""}`;
    const mb = barsSvg(histogram(means, lo, hi, BINS), 230, 200, "dsx-bar");
    const se = sigma / Math.sqrt(s.n);
    let curve = "";
    if (means.length >= 5) {
      const k = means.length * binW();
      const pts = [];
      for (let i = 0; i <= 200; i++) {
        const v = lo + ((hi - lo) * i) / 200;
        const dens = Math.exp(-0.5 * ((v - mu) / se) ** 2) / (se * Math.sqrt(2 * Math.PI));
        pts.push(`${sx(v).toFixed(1)},${(200 - Math.min(1.15, (dens * k) / mb.max) * 186).toFixed(1)}`);
      }
      curve = `<polyline class="dsx-curve" points="${pts.join(" ")}"/>`;
    }
    $("#dsxMeanSvg", pane).innerHTML = `${mb.html}${curve}${axis(200)}
      <line class="dsx-mean" x1="${sx(mu)}" x2="${sx(mu)}" y1="8" y2="200"/>
      ${last ? `<circle class="dsx-est" cx="${sx(clamp(means.at(-1), lo, hi))}" cy="200" r="5"/>` : ""}
      ${means.length ? "" : `<text class="dsx-lbl" x="320" y="100" text-anchor="middle">Draw samples to build the sampling distribution</text>`}`;
    const within = means.filter((m) => Math.abs(m - mu) <= 1.96 * se).length;
    $("#dsxCltStats", pane).innerHTML = kpis([
      ["Samples drawn", means.length.toLocaleString("en-US")],
      ["Population mean mu", fmt(mu, 3)],
      ["Mean of sample means", means.length ? fmt(mean(means), 3) : "n/a"],
      ["Population sigma", fmt(sigma, 3)],
      ["SD of sample means", means.length > 1 ? fmt(std(means), 3) : "n/a"],
      ["Theory sigma / sqrt(n)", fmt(se, 3)],
      ["Within mu +/- 1.96 SE", means.length ? `${pct(within / means.length, 1)} (theory 95%)` : "n/a", means.length > 200 && Math.abs(within / means.length - 0.95) < 0.02 ? "ok" : "neutral"],
    ]);
  };
  const stop = () => {
    clearInterval(timer);
    timer = null;
    $("#dsxAuto", pane).textContent = "Auto";
  };
  const reset = () => {
    stop();
    store.set("ds-clt", s);
    build();
    render();
  };

  $("#dsxPop", pane).value = s.pop;
  $("#dsxN", pane).value = s.n;
  $("#dsxSeed", pane).value = s.seed;
  $("#dsxPop", pane).onchange = (e) => { s.pop = e.target.value; reset(); };
  $("#dsxN", pane).oninput = (e) => { s.n = +e.target.value; reset(); };
  $("#dsxSeed", pane).onchange = (e) => { s.seed = Math.max(0, Math.floor(+e.target.value) || 0); e.target.value = s.seed; reset(); };
  $("#dsxReset", pane).onclick = reset;
  pane.addEventListener("click", (e) => {
    const b = e.target.closest("[data-draw]");
    if (!b) return;
    const k = +b.dataset.draw;
    for (let i = 0; i < k && means.length < 50000; i++) sampleOnce();
    render();
  });
  $("#dsxAuto", pane).onclick = () => {
    if (timer) return stop();
    $("#dsxAuto", pane).textContent = "Pause";
    timer = setInterval(() => {
      for (let i = 0; i < 10; i++) sampleOnce();
      render();
      if (means.length >= 5000) stop();
    }, 120);
  };
  build();
  render();
  return stop;
}

// ===================================================================== lab shell
const TABS = [
  ["dist", "Distribution", distributionTab],
  ["corr", "Correlation", correlationTab],
  ["ab", "A/B test", abTab],
  ["clt", "Central limit theorem", cltTab],
];

export function lab(view) {
  let cleanup = null;
  let active = TABS.some(([k]) => k === store.get("ds-lab-tab", "dist")) ? store.get("ds-lab-tab", "dist") : "dist";
  view.innerHTML = `
    ${labHero("STA", "sky", "Stats Explorer", "Build datasets by hand and watch the statistics react: mean versus median, outliers, correlation traps, A/B test significance and the central limit theorem. All data is synthetic and computed in your browser.")}
    <div class="filters"><div class="tabs" id="dsxTabs">${TABS.map(([k, label]) => `<button data-t="${k}">${esc(label)}</button>`).join("")}</div></div>
    <div id="dsxPane" class="dsx-pane"></div>`;
  const show = (k) => {
    cleanup?.();
    active = k;
    store.set("ds-lab-tab", k);
    $$("#dsxTabs button", view).forEach((b) => b.classList.toggle("active", b.dataset.t === k));
    const old = $("#dsxPane", view);
    const pane = old.cloneNode(false);
    old.replaceWith(pane);
    cleanup = TABS.find(([t]) => t === k)[2](pane) || null;
  };
  $("#dsxTabs", view).addEventListener("click", (e) => {
    const b = e.target.closest("button[data-t]");
    if (b && b.dataset.t !== active) show(b.dataset.t);
  });
  show(active);
  return () => cleanup?.();
}

// ===================================================================== data notebook
const CSV_CELL = `import csv, io, statistics
from collections import Counter, defaultdict

# Synthetic coffee-shop orders. Blank fields are missing values.
RAW = """order_id,day,store,item,qty,unit_price,rating
1,Mon,North,Latte,2,3.50,5
2,Mon,North,Espresso,1,2.20,4
3,Mon,South,Latte,1,3.50,
4,Mon,South,Muffin,3,2.80,4
5,Tue,North,Tea,2,1.90,3
6,Tue,South,Latte,1,,5
7,Tue,East,Espresso,2,2.20,4
8,Tue,East,Muffin,1,2.80,2
9,Wed,North,Latte,3,3.50,4
10,Wed,South,Tea,1,1.90,
11,Wed,East,Latte,2,3.50,5
12,Wed,East,Espresso,,2.20,3
13,Thu,North,Muffin,2,2.80,4
14,Thu,South,Espresso,1,2.20,5
15,Thu,East,Tea,2,,3
16,Thu,North,Latte,1,3.50,4
17,Fri,South,Latte,24,3.50,5
18,Fri,East,Muffin,2,2.80,
19,Fri,North,Espresso,2,2.20,4
20,Fri,South,Tea,1,1.90,2
21,Sat,East,Latte,2,3.50,5
22,Sat,North,Muffin,1,2.80,3
23,Sat,South,Espresso,3,2.20,4
24,Sat,East,Tea,1,1.90,4
"""

rows = list(csv.DictReader(io.StringIO(RAW)))
print(f"{len(rows)} rows x {len(rows[0])} columns")
print("columns:", ", ".join(rows[0]))
for r in rows[:3]:
    print(dict(r))`;

const CLEAN_CELL = `missing = Counter(col for r in rows for col, v in r.items() if not v.strip())
print("missing values per column:", dict(missing))

list_price = {}
for r in rows:
    if r["unit_price"]:
        list_price[r["item"]] = float(r["unit_price"])

orders = []
for r in rows:
    if not r["qty"]:
        continue  # no quantity: the order is unusable, drop it
    qty = int(r["qty"])
    price = float(r["unit_price"]) if r["unit_price"] else list_price[r["item"]]
    orders.append({
        "day": r["day"], "store": r["store"], "item": r["item"],
        "qty": qty, "value": round(qty * price, 2),
        "rating": int(r["rating"]) if r["rating"] else None,  # keep as missing
    })
print(f"kept {len(orders)} of {len(rows)} orders")
print("missing prices filled from the item's list price; ratings left as None")`;

const GROUP_CELL = `by_store = defaultdict(list)
for o in orders:
    by_store[o["store"]].append(o["value"])

print(f"{'store':<7}{'orders':>7}{'revenue':>10}{'mean':>8}{'median':>8}")
for store, vals in sorted(by_store.items()):
    print(f"{store:<7}{len(vals):>7}{sum(vals):>10.2f}{statistics.mean(vals):>8.2f}{statistics.median(vals):>8.2f}")

values = [o["value"] for o in orders]
q1, q2, q3 = statistics.quantiles(values, n=4, method="inclusive")
iqr = q3 - q1
outliers = [v for v in values if v < q1 - 1.5 * iqr or v > q3 + 1.5 * iqr]
print()
print(f"order value: mean={statistics.mean(values):.2f} median={statistics.median(values):.2f}")
print(f"stdev (sample)={statistics.stdev(values):.2f} pstdev={statistics.pstdev(values):.2f}")
print(f"Q1={q1:.2f} Q3={q3:.2f} IQR={iqr:.2f} outliers={outliers}")

ratings = [o["rating"] for o in orders if o["rating"] is not None]
print(f"mean rating {statistics.mean(ratings):.2f} from {len(ratings)} of {len(orders)} orders")`;

const CHART_CELL = `qty_by_item = Counter()
for o in orders:
    qty_by_item[o["item"]] += o["qty"]

top = max(qty_by_item.values())
print("units sold per item")
for item, q in qty_by_item.most_common():
    print(f"{item:<9}{'#' * max(1, round(q / top * 30)):<31}{q}")`;

export const STARTER_CELLS = [CSV_CELL, CLEAN_CELL, GROUP_CELL, CHART_CELL];
const MAX_CELLS = 8;
const MARK = (k) => `__import__("sys").stdout.write("\\x1eDSX${k}\\x1e\\n")`;

/** Joins cells 0..upto into one program with a stdout marker before each cell; returns the start line of each cell. */
export function notebookProgram(cells, upto) {
  const parts = [];
  const starts = [];
  let line = 1;
  for (let k = 0; k <= upto; k++) {
    parts.push(MARK(k));
    line++;
    starts.push(line);
    parts.push(cells[k]);
    line += cells[k].split("\n").length;
  }
  return { code: parts.join("\n"), starts };
}

/** Splits a run result into per-cell { stdout, error } using the markers and start lines. */
export function splitNotebookResult(r, starts) {
  const per = starts.map(() => ({ stdout: "", error: null, ran: false }));
  const chunks = (r.stdout || "").split(/\x1eDSX(\d+)\x1e\n/);
  for (let i = 1; i < chunks.length; i += 2) {
    const k = +chunks[i];
    if (per[k]) {
      per[k].ran = true;
      per[k].stdout = chunks[i + 1] || "";
    }
  }
  const cellOf = (line) => {
    let k = 0;
    starts.forEach((s, i) => { if (line >= s) k = i; });
    return k;
  };
  let failed = -1;
  if (r.error && typeof r.error === "object") {
    const e = r.error;
    failed = e.line ? cellOf(e.line) : starts.length - 1;
    const local = (line) => line - starts[cellOf(line)] + 1;
    const remap = (s) => String(s || "")
      .replace(/\(<playground>, line (\d+)\)/g, (_, n) => `(cell ${cellOf(+n) + 1}, line ${local(+n)})`)
      .replace(/detected at line (\d+)/g, (_, n) => `detected at line ${local(+n)}`)
      .replace(/File "<playground>", line (\d+)/g, (_, n) => `Cell ${cellOf(+n) + 1}, line ${local(+n)}`);
    per[failed].ran = true;
    per[failed].error = { ...e, line: e.line ? local(e.line) : null, message: remap(e.message), trace: remap(e.trace) };
  }
  return { per, failed };
}

export function playground(view, content) {
  const samples = sampleOptions(content, ["python"]);
  const saved = store.get("ds-notebook", null);
  let cells = Array.isArray(saved) && saved.length && saved.every((c) => typeof c === "string") ? saved.slice(0, MAX_CELLS) : [...STARTER_CELLS];
  const handoff = takeHandoff("py-code");
  if (handoff) cells = [...cells.slice(0, MAX_CELLS - 1), handoff];
  let outs = cells.map(() => "");
  let counter = 0;
  const counts = cells.map(() => null);
  let busy = false;

  view.innerHTML = `
    ${labHero("NB", "mint", "Data Notebook", "A mini notebook on a synthetic coffee-shop CSV using only the standard library (csv, io, statistics, collections). Each run replays the cells above it, so variables carry over. Ctrl/Cmd+Enter runs the focused cell.")}
    <div class="filters">
      <select id="dsxSample" class="dsx-sample"><option value="">Add a lesson sample as a new cell…</option>${samples.map((s, i) => `<option value="${i}">${esc(s.label)}</option>`).join("")}</select>
      <button class="btn small" id="dsxAdd">Add cell</button>
      <button class="btn small primary" id="dsxRunAll">Run all</button>
      <button class="btn small" id="dsxStarter">Reset to starter</button>
    </div>
    <div id="dsxCells" class="dsx-cells"></div>`;
  const box = $("#dsxCells", view);
  const save = () => store.set("ds-notebook", cells);

  const draw = () => {
    box.innerHTML = cells.map((_, i) => `
      <section class="panel clay dsx-cell" data-c="${i}">
        <div class="dsx-cell-head">
          <span class="dsx-prompt">In [${counts[i] ?? " "}]</span>
          <span class="muted">Cell ${i + 1}</span>
          <span class="spacer"></span>
          <button class="btn small primary" data-run="${i}">Run</button>
          <button class="btn small" data-rm="${i}" ${cells.length <= 1 ? "disabled" : ""} aria-label="Remove cell ${i + 1}">Remove</button>
        </div>
        <textarea class="code code-editor dsx-code" spellcheck="false" rows="${Math.min(18, Math.max(4, cells[i].split("\n").length + 1))}" data-ta="${i}"></textarea>
        <div class="dsx-out" data-out="${i}">${outs[i]}</div>
      </section>`).join("");
    $$("textarea[data-ta]", box).forEach((ta) => {
      const i = +ta.dataset.ta;
      ta.value = cells[i];
      codeEditor(ta, () => run(+ta.dataset.ta, false), 4);
    });
    $("#dsxAdd", view).disabled = cells.length >= MAX_CELLS;
  };

  async function run(upto, all) {
    if (busy) return;
    const { code, starts } = notebookProgram(cells, upto);
    if (code.length > 20000) {
      outs[upto] = `<div class="run-error">The notebook is longer than 20,000 characters. Remove or shorten some cells.</div>`;
      draw();
      return;
    }
    busy = true;
    $$("[data-run], #dsxRunAll", view).forEach((b) => (b.disabled = true));
    const targets = all ? cells.map((_, i) => i) : [upto];
    targets.forEach((i) => {
      const o = $(`[data-out="${i}"]`, box);
      if (o) o.innerHTML = `<span class="muted">Running…</span>`;
    });
    const r = await runPython(code);
    busy = false;
    if (r.error && typeof r.error !== "object") r.error = { type: "Error", message: String(r.error) };
    const { per, failed } = splitNotebookResult(r, starts);
    const ms = r.ms ?? 0;
    const cellHtml = (p) => pyResultHtml({ stdout: p.stdout, error: p.error, ok: !p.error, ms });
    const compileError = failed >= 0 && /SyntaxError|IndentationError|TabError/.test(r.error.type || "");
    if (all) {
      per.forEach((p, i) => {
        counts[i] = p.ran ? ++counter : counts[i];
        outs[i] = p.ran ? cellHtml(p) : `<div class="muted res-meta">${compileError && i < failed ? `Not run: cell ${failed + 1} does not compile, so nothing ran.` : "Not run: an earlier cell failed."}</div>`;
      });
    } else {
      counts[upto] = ++counter;
      if (failed >= 0 && failed < upto) {
        outs[failed] = cellHtml(per[failed]);
        outs[upto] = `<div class="run-error">Cell ${failed + 1} failed while replaying the cells above, so this cell did not run.</div>`;
      } else outs[upto] = cellHtml(per[upto]);
    }
    draw();
  }

  box.addEventListener("input", (e) => {
    const i = e.target.dataset.ta;
    if (i === undefined) return;
    cells[+i] = e.target.value;
    save();
  });
  box.addEventListener("click", (e) => {
    const runB = e.target.closest("[data-run]");
    const rmB = e.target.closest("[data-rm]");
    if (runB) run(+runB.dataset.run, false);
    if (rmB && cells.length > 1) {
      const i = +rmB.dataset.rm;
      cells.splice(i, 1);
      outs.splice(i, 1);
      counts.splice(i, 1);
      save();
      draw();
    }
  });
  const addCell = (code) => {
    if (cells.length >= MAX_CELLS) return;
    cells.push(code);
    outs.push("");
    counts.push(null);
    save();
    draw();
    $$("textarea[data-ta]", box).at(-1)?.focus();
  };
  $("#dsxAdd", view).onclick = () => addCell("# use variables from the cells above, e.g. orders, values\nprint(len(orders))");
  $("#dsxRunAll", view).onclick = () => run(cells.length - 1, true);
  $("#dsxStarter", view).onclick = () => {
    cells = [...STARTER_CELLS];
    outs = cells.map(() => "");
    counts.length = 0;
    cells.forEach(() => counts.push(null));
    save();
    draw();
  };
  $("#dsxSample", view).onchange = (e) => {
    if (e.target.value !== "") addCell(samples[+e.target.value].code);
    e.target.value = "";
  };
  draw();
}
