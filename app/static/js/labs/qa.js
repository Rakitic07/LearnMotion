import { $, esc, highlightCode, store, toast } from "../util.js";
import { pyResultHtml, runPython } from "../runners.js";
import { codeEditor, labHero, sampleOptions, takeHandoff } from "./common.js";

// ===================================================================== functions under test
// Each function is modelled in JS with explicit tracing: t.L(i) marks source line i as executed and
// t.B(id, cond) records the outcome of decision `id`. Mutants are selected by id inside run().

class PyRaise extends Error {
  constructor(type, message) {
    super(message);
    this.pyType = type;
  }
}
const round2 = (x) => Math.round(x * 100) / 100;

export const FUNCS = [
  {
    id: "shipping",
    name: "shipping_cost",
    title: "Shipping cost",
    blurb: "Base 5.0, +4 for parcels over 10 kg, doubled for intl or +3 for EU, +10 express (only up to 20 kg). Raises ValueError for weight <= 0.",
    params: [
      { name: "weight", type: "num", def: "5" },
      { name: "zone", type: "enum", options: ["domestic", "eu", "intl"], def: "domestic" },
      { name: "express", type: "bool", def: "False" },
    ],
    expectHint: "e.g. 9.0 or ValueError",
    expectOptions: ["ValueError"],
    src: [
      "def shipping_cost(weight, zone, express):",
      "    if weight <= 0:",
      '        raise ValueError("weight must be positive")',
      "    cost = 5.0",
      "    if weight > 10:",
      "        cost += 4  # heavy parcel surcharge",
      '    if zone == "intl":',
      "        cost *= 2",
      '    elif zone == "eu":',
      "        cost += 3",
      "    if express and weight <= 20:",
      "        cost += 10",
      "    return round(cost, 2)",
    ],
    decisions: [
      { id: "d1", line: 1, label: "weight <= 0" },
      { id: "d2", line: 4, label: "weight > 10" },
      { id: "d3", line: 6, label: 'zone == "intl"' },
      { id: "d4", line: 8, label: 'zone == "eu"' },
      { id: "d5", line: 10, label: "express and weight <= 20" },
    ],
    mutants: [
      { id: "m1", line: 1, kind: "relational", code: "    if weight < 0:", hint: "Only a test with weight exactly 0 can tell < from <=." },
      { id: "m2", line: 4, kind: "relational", code: "    if weight >= 10:", hint: "Test weight exactly 10: the surcharge must not apply there." },
      { id: "m3", line: 9, kind: "removed statement", code: "        pass  # EU surcharge removed", hint: "Any EU parcel would expose the missing +3." },
      { id: "m4", line: 10, kind: "removed condition", code: "    if express:", hint: "Express on a parcel heavier than 20 kg must not add 10." },
      { id: "m5", line: 10, kind: "relational", code: "    if express and weight < 20:", hint: "Test express at exactly 20 kg." },
      { id: "m6", line: 7, kind: "arithmetic", code: "        cost += 2", hint: "Any intl parcel checks the doubling." },
    ],
    maxTests: 5,
    hints: {
      boundary: [
        "weight has edges at 0, 10 and 20. Test exactly on each edge: that is where < and <= behave differently.",
        "weight = 0 must raise ValueError. A tiny positive weight such as 0.1 is the first valid value.",
        "Express only applies up to 20 kg: try 20 and 21 with express = True.",
      ],
      partition: [
        "zone has three equivalence classes: domestic, eu and intl. Each needs at least one test.",
        "weight splits into invalid (<= 0), light (up to 10), heavy (10 to 20) and very heavy (over 20).",
        "express True and express False are separate classes. One test can cover several classes at once.",
      ],
    },
    solution: [
      { args: { weight: "0", zone: "domestic", express: "False" }, expect: "ValueError" },
      { args: { weight: "10", zone: "intl", express: "False" }, expect: "10.0" },
      { args: { weight: "20", zone: "eu", express: "True" }, expect: "22.0" },
      { args: { weight: "21", zone: "domestic", express: "True" }, expect: "9.0" },
    ],
    run({ weight: w, zone, express }, t, m) {
      t.L(1);
      if (t.B("d1", m === "m1" ? w < 0 : w <= 0)) {
        t.L(2);
        throw new PyRaise("ValueError", "weight must be positive");
      }
      t.L(3);
      let cost = 5.0;
      t.L(4);
      if (t.B("d2", m === "m2" ? w >= 10 : w > 10)) {
        t.L(5);
        cost += 4;
      }
      t.L(6);
      if (t.B("d3", zone === "intl")) {
        t.L(7);
        cost = m === "m6" ? cost + 2 : cost * 2;
      } else {
        t.L(8);
        if (t.B("d4", zone === "eu")) {
          t.L(9);
          if (m !== "m3") cost += 3;
        }
      }
      t.L(10);
      const light = m === "m5" ? w < 20 : w <= 20;
      if (t.B("d5", m === "m4" ? express : express && light)) {
        t.L(11);
        cost += 10;
      }
      t.L(12);
      return round2(cost);
    },
  },
  {
    id: "password",
    name: "password_strength",
    title: "Password strength",
    blurb: 'Shorter than 8 characters is "weak". Otherwise one point each for a digit, an uppercase letter and a symbol: 2 or more points is "strong", else "medium".',
    params: [{ name: "pw", type: "str", def: "" }],
    expectHint: "weak, medium or strong",
    expectOptions: ["weak", "medium", "strong"],
    src: [
      "def password_strength(pw):",
      "    if len(pw) < 8:",
      '        return "weak"',
      "    score = 0",
      "    if any(c.isdigit() for c in pw):",
      "        score += 1",
      "    if any(c.isupper() for c in pw):",
      "        score += 1",
      "    if any(not c.isalnum() for c in pw):",
      "        score += 1",
      "    if score >= 2:",
      '        return "strong"',
      '    return "medium"',
    ],
    decisions: [
      { id: "d1", line: 1, label: "len(pw) < 8" },
      { id: "d2", line: 4, label: "has a digit" },
      { id: "d3", line: 6, label: "has an uppercase letter" },
      { id: "d4", line: 8, label: "has a symbol" },
      { id: "d5", line: 10, label: "score >= 2" },
    ],
    mutants: [
      { id: "m1", line: 1, kind: "relational", code: "    if len(pw) <= 8:", hint: "A password of exactly 8 characters separates < from <=." },
      { id: "m2", line: 10, kind: "constant", code: "    if score >= 3:", hint: "You need a password scoring exactly 2 points." },
      { id: "m3", line: 5, kind: "removed statement", code: "        pass  # digit point removed", hint: "A strong password whose second point comes from a digit." },
      { id: "m4", line: 2, kind: "return value", code: '        return "medium"', hint: "Any short password checks this return value." },
      { id: "m5", line: 8, kind: "negated condition", code: "    if any(c.isalnum() for c in pw):", hint: "A long password with exactly one point and no symbol." },
    ],
    maxTests: 4,
    hints: {
      boundary: [
        "Length 7 versus 8 is the edge between weak and everything else.",
        "Score 1 versus 2 decides medium versus strong: build one password worth exactly 1 point and one worth exactly 2.",
      ],
      partition: [
        "Character classes: digits, uppercase letters and symbols. Turn each one on and off.",
        "All short passwords form one class: their content does not matter, so one test is enough.",
      ],
    },
    solution: [
      { args: { pw: "abcdefg" }, expect: "weak" },
      { args: { pw: "Abcdefg1" }, expect: "strong" },
      { args: { pw: "abcdefg1" }, expect: "medium" },
      { args: { pw: "abcdefg!" }, expect: "medium" },
    ],
    run({ pw }, t, m) {
      const len = [...pw].length;
      t.L(1);
      if (t.B("d1", m === "m1" ? len <= 8 : len < 8)) {
        t.L(2);
        return m === "m4" ? "medium" : "weak";
      }
      t.L(3);
      let score = 0;
      t.L(4);
      if (t.B("d2", /\p{Nd}/u.test(pw))) {
        t.L(5);
        if (m !== "m3") score += 1;
      }
      t.L(6);
      if (t.B("d3", /\p{Lu}/u.test(pw))) {
        t.L(7);
        score += 1;
      }
      t.L(8);
      if (t.B("d4", m === "m5" ? /[\p{L}\p{N}]/u.test(pw) : /[^\p{L}\p{N}]/u.test(pw))) {
        t.L(9);
        score += 1;
      }
      t.L(10);
      if (t.B("d5", m === "m2" ? score >= 3 : score >= 2)) {
        t.L(11);
        return "strong";
      }
      t.L(12);
      return "medium";
    },
  },
  {
    id: "leap",
    name: "is_leap",
    title: "Leap year",
    blurb: "Gregorian rule: divisible by 400 is leap, otherwise divisible by 100 is not, otherwise divisible by 4 is leap.",
    params: [{ name: "year", type: "int", def: "2024" }],
    expectHint: "True or False",
    expectOptions: ["True", "False"],
    src: [
      "def is_leap(year):",
      "    if year % 400 == 0:",
      "        return True",
      "    if year % 100 == 0:",
      "        return False",
      "    if year % 4 == 0:",
      "        return True",
      "    return False",
    ],
    decisions: [
      { id: "d1", line: 1, label: "year % 400 == 0" },
      { id: "d2", line: 3, label: "year % 100 == 0" },
      { id: "d3", line: 5, label: "year % 4 == 0" },
    ],
    mutants: [
      { id: "m1", line: 1, kind: "removed condition", code: "    if False:  # 400 rule removed", hint: "A year divisible by 400." },
      { id: "m2", line: 3, kind: "constant", code: "    if year % 200 == 0:", hint: "A century that is not divisible by 200 or 400, such as 1900." },
      { id: "m3", line: 5, kind: "constant", code: "    if year % 2 == 0:", hint: "An even year that is not divisible by 4, such as 2002. Odd years cannot catch this." },
      { id: "m4", line: 7, kind: "return value", code: "    return True", hint: "Any year not divisible by 4." },
      { id: "m5", line: 4, kind: "return value", code: "        return True", hint: "A century year that is not divisible by 400." },
    ],
    maxTests: 4,
    hints: {
      boundary: [
        "For divisibility rules the edges are the multiples: 4, 100 and 400.",
        "A century such as 1900 sits on the 100 edge, and 2000 sits on the 400 edge.",
      ],
      partition: [
        "Four classes: divisible by 400; by 100 but not 400; by 4 but not 100; not by 4.",
        "Not divisible by 4 has sub-classes: an odd year cannot tell % 4 from % 2, but an even year like 2002 can.",
      ],
    },
    solution: [
      { args: { year: "2000" }, expect: "True" },
      { args: { year: "1900" }, expect: "False" },
      { args: { year: "2024" }, expect: "True" },
      { args: { year: "2002" }, expect: "False" },
    ],
    run({ year }, t, m) {
      const div = (n) => year % n === 0;
      t.L(1);
      if (t.B("d1", m === "m1" ? false : div(400))) {
        t.L(2);
        return true;
      }
      t.L(3);
      if (t.B("d2", div(m === "m2" ? 200 : 100))) {
        t.L(4);
        return m === "m5";
      }
      t.L(5);
      if (t.B("d3", div(m === "m3" ? 2 : 4))) {
        t.L(6);
        return true;
      }
      t.L(7);
      return m === "m4";
    },
  },
  {
    id: "discount",
    name: "discount",
    title: "Discount calculator",
    blurb: 'Members get 10% off. Coupon "SAVE20" adds 20% on orders of 100 or more. The total discount is capped at 25%. Negative totals raise ValueError.',
    params: [
      { name: "total", type: "num", def: "50" },
      { name: "is_member", type: "bool", def: "False" },
      { name: "coupon", type: "str", def: "" },
    ],
    expectHint: "e.g. 45.0 or ValueError",
    expectOptions: ["ValueError"],
    src: [
      "def discount(total, is_member, coupon):",
      "    if total < 0:",
      '        raise ValueError("total must not be negative")',
      "    pct = 0",
      "    if is_member:",
      "        pct = 10",
      '    if coupon == "SAVE20" and total >= 100:',
      "        pct += 20",
      "    if pct > 25:",
      "        pct = 25",
      "    return round(total * (100 - pct) / 100, 2)",
    ],
    decisions: [
      { id: "d1", line: 1, label: "total < 0" },
      { id: "d2", line: 4, label: "is_member" },
      { id: "d3", line: 6, label: 'coupon == "SAVE20" and total >= 100' },
      { id: "d4", line: 8, label: "pct > 25" },
    ],
    mutants: [
      { id: "m1", line: 6, kind: "relational", code: '    if coupon == "SAVE20" and total > 100:', hint: "Use the coupon on a total of exactly 100." },
      { id: "m2", line: 8, kind: "constant", code: "    if pct > 30:", hint: "A member with SAVE20 reaches 30%: the cap must bring it back to 25%." },
      { id: "m3", line: 6, kind: "removed condition", code: '    if coupon == "SAVE20":', hint: "Use the coupon on a total below 100." },
      { id: "m4", line: 5, kind: "constant", code: "        pct = 5", hint: "A member whose discount is not capped." },
      { id: "m5", line: 1, kind: "relational", code: "    if total <= 0:", hint: "A total of exactly 0 is valid and costs 0." },
    ],
    maxTests: 5,
    hints: {
      boundary: [
        "total has two edges: -1 versus 0 (error versus valid) and 99 versus 100 for the coupon.",
        "The cap sits at 25%: a member using SAVE20 reaches 30% and must be capped.",
      ],
      partition: [
        "Classes: member or not; coupon SAVE20, no coupon, or an unknown coupon.",
        "A valid coupon below the 100 threshold is its own class.",
      ],
    },
    solution: [
      { args: { total: "-1", is_member: "False", coupon: "" }, expect: "ValueError" },
      { args: { total: "0", is_member: "False", coupon: "" }, expect: "0.0" },
      { args: { total: "100", is_member: "False", coupon: "SAVE20" }, expect: "80.0" },
      { args: { total: "99", is_member: "True", coupon: "SAVE20" }, expect: "89.1" },
      { args: { total: "200", is_member: "True", coupon: "SAVE20" }, expect: "150.0" },
    ],
    run({ total, is_member, coupon }, t, m) {
      t.L(1);
      if (t.B("d1", m === "m5" ? total <= 0 : total < 0)) {
        t.L(2);
        throw new PyRaise("ValueError", "total must not be negative");
      }
      t.L(3);
      let pct = 0;
      t.L(4);
      if (t.B("d2", is_member)) {
        t.L(5);
        pct = m === "m4" ? 5 : 10;
      }
      t.L(6);
      const big = m === "m1" ? total > 100 : total >= 100;
      if (t.B("d3", coupon === "SAVE20" && (m === "m3" || big))) {
        t.L(7);
        pct += 20;
      }
      t.L(8);
      if (t.B("d4", pct > (m === "m2" ? 30 : 25))) {
        t.L(9);
        pct = 25;
      }
      t.L(10);
      return round2((total * (100 - pct)) / 100);
    },
  },
];

// ===================================================================== pure evaluation helpers
export function fmtOut(v) {
  if (typeof v === "boolean") return v ? "True" : "False";
  if (typeof v === "number") return String(Object.is(v, -0) ? 0 : v);
  return String(v);
}

/** Normalises what the learner typed as the expected result so it compares with fmtOut(). */
export function normExpected(raw) {
  let s = String(raw ?? "").trim();
  const q = s.match(/^(["'])(.*)\1$/);
  if (q) return q[2];
  if (/^-?(\d+\.?\d*|\.\d+)$/.test(s)) return String(Number(s));
  if (/^true$/i.test(s)) return "True";
  if (/^false$/i.test(s)) return "False";
  const err = s.match(/^(?:raises\s+)?(valueerror|typeerror)$/i);
  if (err) s = err[1].toLowerCase() === "valueerror" ? "ValueError" : "TypeError";
  return s;
}

export function parseArgs(fn, raw = {}) {
  const args = {};
  let error = null;
  for (const p of fn.params) {
    const v = raw[p.name] ?? "";
    if (p.type === "num" || p.type === "int") {
      const s = String(v).trim();
      const n = Number(s);
      if (s === "" || !Number.isFinite(n)) error ??= `${p.name} must be a number`;
      else if (p.type === "int" && !Number.isInteger(n)) error ??= `${p.name} must be a whole number`;
      args[p.name] = n;
    } else if (p.type === "bool") {
      args[p.name] = v === true || /^true$/i.test(String(v));
    } else if (p.type === "enum") {
      if (!p.options.includes(v)) error ??= `${p.name} must be one of ${p.options.join(", ")}`;
      args[p.name] = String(v);
    } else {
      args[p.name] = String(v);
    }
  }
  return { args, error };
}

export const executableLines = (fn) =>
  fn.src.map((l, i) => (i > 0 && l.trim() && !/^\s*(#|else:)/.test(l) ? i : -1)).filter((i) => i >= 0);

const NOOP = { L() {}, B: (_, v) => !!v };

/** Runs one case on the original (mutant = null, traced) or on a mutant (untraced). */
export function runCase(fn, args, mutant = null) {
  const lines = new Set();
  const outcomes = new Set();
  const t = mutant ? NOOP : {
    L: (n) => lines.add(n),
    B: (id, v) => {
      outcomes.add(`${id}:${v ? "T" : "F"}`);
      return !!v;
    },
  };
  let out;
  try {
    out = fmtOut(fn.run(args, t, mutant));
  } catch (e) {
    if (!(e instanceof PyRaise)) throw e;
    out = e.pyType;
  }
  return { out, lines, outcomes };
}

const pct = (a, b) => (b ? Math.round((a / b) * 100) : 0);

function prepare(fn, cases) {
  return (cases || []).map((c, i) => {
    const { args, error } = parseArgs(fn, c.args);
    const expected = normExpected(c.expect);
    if (error || !expected) return { i, valid: false, error: error || "missing expected result", expected, lines: new Set(), outcomes: new Set() };
    const r = runCase(fn, args);
    return { i, valid: true, args, expected, actual: r.out, pass: r.out === expected, lines: r.lines, outcomes: r.outcomes };
  });
}

function covOf(fn, results) {
  const exec = executableLines(fn);
  const lineHit = new Set();
  const brHit = new Set();
  for (const r of results) {
    if (!r.valid) continue;
    r.lines.forEach((l) => lineHit.add(l));
    r.outcomes.forEach((o) => brHit.add(o));
  }
  const hitLines = exec.filter((l) => lineHit.has(l)).length;
  const brTotal = fn.decisions.length * 2;
  return {
    lineHit,
    brHit,
    lines: { hit: hitLines, total: exec.length, pct: pct(hitLines, exec.length) },
    branches: { hit: brHit.size, total: brTotal, pct: pct(brHit.size, brTotal) },
  };
}

function mutOf(fn, results) {
  const passing = results.filter((r) => r.valid && r.pass);
  const mutants = fn.mutants.map((m) => {
    const killer = passing.find((r) => runCase(fn, r.args, m.id).out !== r.expected);
    return { ...m, killed: !!killer, by: killer ? killer.i : null };
  });
  const killed = mutants.filter((m) => m.killed).length;
  return { mutants, killed, total: mutants.length, pct: pct(killed, mutants.length) };
}

/** Line and branch coverage of a suite. cases: [{ args: { param: rawString }, expect: rawString }] */
export const coverage = (fn, cases) => covOf(fn, prepare(fn, cases));

/** A mutant is killed when some test that passes on the original code fails on the mutant. */
export const mutationReport = (fn, cases) => mutOf(fn, prepare(fn, cases));

export function evaluateSuite(fn, cases = []) {
  const results = prepare(fn, cases);
  const cov = covOf(fn, results);
  const mutation = mutOf(fn, results);
  const allPass = results.length > 0 && results.every((r) => r.valid && r.pass);
  const checks = [
    { label: "100% branch coverage", ok: cov.branches.hit === cov.branches.total },
    { label: `All ${mutation.total} mutants killed`, ok: mutation.killed === mutation.total },
    { label: `At most ${fn.maxTests} tests (you have ${cases.length})`, ok: cases.length > 0 && cases.length <= fn.maxTests },
    { label: "Every test passes", ok: allPass },
  ];
  return { results, ...cov, mutation, checks, met: checks.every((c) => c.ok) };
}

const pyStr = (s) => `"${String(s).replace(/\\/g, "\\\\").replace(/"/g, '\\"')}"`;
const fmtArg = (p, v) => (p.type === "bool" ? (v ? "True" : "False") : p.type === "num" || p.type === "int" ? fmtOut(v) : pyStr(v));
export const callText = (fn, args) => `${fn.name}(${fn.params.map((p) => fmtArg(p, args[p.name])).join(", ")})`;

// ===================================================================== Coverage Lab
const SUITES_KEY = "qa-cov-suites";
const DONE_KEY = "qa-cov-done";
const FN_KEY = "qa-cov-fn";

const meter = (label, hit, total, p) => `
  <div class="qa-metric">
    <div class="qa-metric-h"><span>${esc(label)}</span><b>${p}%</b></div>
    <div class="qa-bar ${p === 100 ? "full" : ""}"><i style="width:${p}%"></i></div>
    <div class="muted qa-metric-sub">${hit} / ${total}</div>
  </div>`;

function fieldHtml(p) {
  const id = `qaP_${p.name}`;
  const label = `<label for="${id}"><code>${esc(p.name)}</code></label>`;
  if (p.type === "bool" || p.type === "enum") {
    const opts = p.type === "bool" ? ["True", "False"] : p.options;
    return `<div class="qa-field">${label}<select id="${id}" name="${esc(p.name)}">${opts.map((o) => `<option${o === p.def ? " selected" : ""}>${esc(o)}</option>`).join("")}</select></div>`;
  }
  const type = p.type === "str" ? "text" : "number";
  const step = p.type === "int" ? "1" : "any";
  return `<div class="qa-field">${label}<input id="${id}" name="${esc(p.name)}" type="${type}"${type === "number" ? ` step="${step}"` : ""} value="${esc(p.def)}" autocomplete="off" spellcheck="false"></div>`;
}

export function lab(view) {
  const suites = store.get(SUITES_KEY, {});
  const done = store.get(DONE_KEY, {});
  let fn = FUNCS.find((f) => f.id === store.get(FN_KEY, "")) || FUNCS[0];
  let focus = null;
  const hintIdx = { boundary: 0, partition: 0 };

  view.innerHTML = `
    ${labHero("COV", "sky", "Coverage Lab", "Write test cases for small functions and watch which lines and branches they execute. Then run <b>mutation testing</b>: small deliberate bugs (mutants) are injected, and a good suite fails on every one of them. Reach 100% branch coverage and kill every mutant within the test budget.")}
    <div class="qa-fns" id="qaFns" role="tablist" aria-label="Function under test"></div>
    <div id="qaBody"></div>`;

  const cases = () => (suites[fn.id] ||= []);
  const save = () => store.set(SUITES_KEY, suites);

  const renderFns = () => {
    $("#qaFns").innerHTML = FUNCS.map((f) => `
      <button class="btn small qa-fn${f === fn ? " active" : ""}" data-fn="${f.id}" role="tab" aria-selected="${f === fn}">
        ${esc(f.title)}${done[f.id] ? ` <span class="pill ok">done</span>` : ""}
      </button>`).join("");
  };

  const renderBody = () => {
    hintIdx.boundary = hintIdx.partition = 0;
    focus = null;
    $("#qaBody").innerHTML = `
      <div class="lab-grid halves qa-top">
        <div class="panel clay">
          <h3>Code under test</h3>
          <p class="muted qa-blurb">${esc(fn.blurb)}</p>
          <div class="qa-code" id="qaCode"></div>
          <div class="qa-legend muted">
            <span><i class="qa-sw hit"></i>executed</span><span><i class="qa-sw miss"></i>never executed</span>
            <span><span class="qa-br on">T</span><span class="qa-br on">F</span> branch outcome seen</span>
            <span><span class="qa-mk">M</span> has a mutant</span>
          </div>
          <div id="qaFocus"></div>
        </div>
        <div class="panel clay">
          <h3>Add a test case</h3>
          <form id="qaForm" class="qa-form" autocomplete="off">
            ${fn.params.map(fieldHtml).join("")}
            <div class="qa-field qa-expect">
              <label for="qaExpect">expected</label>
              <input id="qaExpect" name="__expect" type="text" placeholder="${esc(fn.expectHint)}" list="qaExpOpts" spellcheck="false">
              <datalist id="qaExpOpts">${fn.expectOptions.map((o) => `<option value="${esc(o)}">`).join("")}</datalist>
            </div>
            <div class="qa-form-actions"><button class="btn primary" type="submit">Add test</button><span class="qa-form-msg" id="qaFormMsg" role="status"></span></div>
          </form>
          <div class="qa-metrics" id="qaMetrics"></div>
          <div class="row qa-hint-btns">
            <button class="btn small" data-act="hint" data-kind="boundary">Boundary value hint</button>
            <button class="btn small" data-act="hint" data-kind="partition">Equivalence class hint</button>
          </div>
          <div id="qaHint"></div>
          <div id="qaUncovered"></div>
        </div>
      </div>
      <div class="panel clay qa-suite-panel">
        <div class="row"><h3>Test suite</h3><span class="spacer"></span>
          <button class="btn small" data-act="solution">Show a solution</button>
          <button class="btn small danger" data-act="clear">Clear suite</button>
        </div>
        <div id="qaSuite"></div>
      </div>
      <div class="lab-grid halves qa-bottom">
        <div class="panel clay">
          <h3>Mutation testing</h3>
          <p class="muted qa-blurb">Each mutant is a copy of the function with one small change. It is <b>killed</b> when at least one passing test returns a different result on it. A surviving mutant is a bug your suite would not notice.</p>
          <div id="qaMuts"></div>
        </div>
        <div class="panel clay">
          <h3>Challenge</h3>
          <div id="qaChallenge"></div>
        </div>
      </div>`;
    $("#qaForm").onsubmit = (e) => {
      e.preventDefault();
      addCase();
    };
    refresh();
  };

  const addCase = () => {
    const raw = {};
    fn.params.forEach((p) => (raw[p.name] = $(`#qaP_${p.name}`).value));
    const expect = $("#qaExpect").value;
    const msg = $("#qaFormMsg");
    const { error } = parseArgs(fn, raw);
    if (error || !expect.trim()) {
      msg.textContent = error || "Enter the expected result.";
      msg.className = "qa-form-msg bad";
      return;
    }
    cases().push({ args: raw, expect: expect.trim() });
    save();
    msg.textContent = `Added test #${cases().length}.`;
    msg.className = "qa-form-msg good";
    $("#qaExpect").value = "";
    refresh();
  };

  const refresh = () => {
    const list = cases();
    const ev = evaluateSuite(fn, list);
    if (focus !== null && !ev.results[focus]?.valid) focus = null;
    const f = focus !== null ? ev.results[focus] : null;
    const lineSet = f ? f.lines : ev.lineHit;
    const brSet = f ? f.outcomes : ev.brHit;
    const exec = new Set(executableLines(fn));
    const hl = highlightCode(fn.src.join("\n"), "python").split("\n");

    $("#qaCode").innerHTML = hl.map((h, i) => {
      const dec = fn.decisions.find((d) => d.line === i);
      const cls = !exec.has(i) ? "" : lineSet.has(i) ? "hit" : list.length || f ? "miss" : "";
      const badges = dec ? ["T", "F"].map((o) => `<span class="qa-br ${brSet.has(`${dec.id}:${o}`) ? "on" : "off"}" title="${esc(dec.label)} was ${o === "T" ? "true" : "false"}">${o}</span>`).join("") : "";
      const mk = fn.mutants.some((m) => m.line === i) ? `<span class="qa-mk" title="A mutant changes this line">M</span>` : "";
      return `<div class="qa-ln ${cls}"><span class="ln">${i + 1}</span><span class="src">${h || " "}</span><span class="qa-brs">${badges}${mk}</span></div>`;
    }).join("");
    $("#qaFocus").innerHTML = f
      ? `<div class="qa-focus-note"><span>Showing the path of test #${f.i + 1}: <code>${esc(callText(fn, f.args))}</code></span><button class="btn small" data-act="unfocus">Show whole suite</button></div>`
      : "";

    $("#qaMetrics").innerHTML = meter("Line coverage", ev.lines.hit, ev.lines.total, ev.lines.pct)
      + meter("Branch coverage", ev.branches.hit, ev.branches.total, ev.branches.pct)
      + meter("Mutation score", ev.mutation.killed, ev.mutation.total, ev.mutation.pct);

    const missing = fn.decisions.flatMap((d) => ["T", "F"].filter((o) => !ev.brHit.has(`${d.id}:${o}`)).map((o) => ({ d, o })));
    $("#qaUncovered").innerHTML = list.length && missing.length
      ? `<div class="qa-uncovered"><b>Branch outcomes not covered yet</b><ul>${missing.map(({ d, o }) => `<li>line ${d.line + 1}: <code>${esc(d.label)}</code> never ${o === "T" ? "true" : "false"}</li>`).join("")}</ul></div>`
      : "";

    $("#qaSuite").innerHTML = list.length ? `
      <div class="qa-table-wrap"><table class="qa-table">
        <thead><tr><th>#</th><th>Call</th><th>Expected</th><th>Actual</th><th>Result</th><th></th></tr></thead>
        <tbody>${ev.results.map((r) => {
          const c = list[r.i];
          if (!r.valid) {
            return `<tr class="bad"><td>${r.i + 1}</td><td colspan="3"><code>${esc(JSON.stringify(c.args))}</code></td><td><span class="pill bad">invalid</span> <span class="muted">${esc(r.error)}</span></td>
              <td class="qa-actions"><button class="btn small" data-act="del" data-i="${r.i}" aria-label="Delete test ${r.i + 1}">Delete</button></td></tr>`;
          }
          return `<tr class="${r.pass ? "" : "bad"}${focus === r.i ? " focus" : ""}">
            <td>${r.i + 1}</td>
            <td><code>${esc(callText(fn, r.args))}</code></td>
            <td><code>${esc(r.expected)}</code></td>
            <td><code>${esc(r.actual)}</code></td>
            <td>${r.pass ? `<span class="pill ok">pass</span>` : `<span class="pill bad">fail</span>`}</td>
            <td class="qa-actions"><button class="btn small${focus === r.i ? " active" : ""}" data-act="focus" data-i="${r.i}">Path</button><button class="btn small" data-act="del" data-i="${r.i}" aria-label="Delete test ${r.i + 1}">Delete</button></td>
          </tr>`;
        }).join("")}</tbody>
      </table></div>
      ${ev.results.some((r) => r.valid && !r.pass) ? `<p class="muted qa-note">A failing test means the expected value disagrees with the code. Fix the expectation (or you found a bug). Failing tests do not count toward killing mutants.</p>` : ""}`
      : `<p class="muted">No tests yet. Add a case above: pick inputs, type the result you expect, and see what it covers. Coverage is 0% and every mutant survives.</p>`;

    $("#qaMuts").innerHTML = `<div class="qa-mut-score"><b>${ev.mutation.killed} / ${ev.mutation.total}</b> killed <span class="muted">(${ev.mutation.pct}% mutation score)</span></div>` + ev.mutation.mutants.map((m, k) => `
      <div class="qa-mut ${m.killed ? "killed" : "survived"}">
        <div class="qa-mut-h"><b>M${k + 1}</b><span class="muted">${esc(m.kind)} · line ${m.line + 1}</span><span class="spacer"></span>
          ${m.killed ? `<span class="pill ok">killed by #${m.by + 1}</span>` : `<span class="pill bad">survived</span>`}</div>
        <div class="qa-diff"><div class="del"><span>-</span><code>${highlightCode(fn.src[m.line].trim(), "python")}</code></div><div class="add"><span>+</span><code>${highlightCode(m.code.trim(), "python")}</code></div></div>
        ${!m.killed && list.length ? `<details class="qa-mut-hint"><summary>How could a test catch it?</summary><p>${esc(m.hint)}</p></details>` : ""}
      </div>`).join("");

    $("#qaChallenge").innerHTML = `
      <p>Goal for <code>${esc(fn.name)}</code>: <b>100% branch coverage</b> and <b>every mutant killed</b> with at most <b>${fn.maxTests} tests</b>, all passing.</p>
      <ul class="qa-checks">${ev.checks.map((c) => `<li class="${c.ok ? "ok" : ""}"><span class="pill ${c.ok ? "ok" : "warn"}">${c.ok ? "yes" : "not yet"}</span> ${esc(c.label)}</li>`).join("")}</ul>
      ${ev.met ? `<div class="bug-why good"><b>Challenge complete.</b> Your suite is small, covers every branch and catches every injected bug.</div>`
        : done[fn.id] ? `<p class="muted">You completed this challenge before.</p>` : ""}
      <p class="muted qa-note">Note: 100% coverage alone does not guarantee a strong suite. Try reaching it while some mutants still survive.</p>`;

    if (ev.met && !done[fn.id]) {
      done[fn.id] = true;
      store.set(DONE_KEY, done);
      renderFns();
      toast(`Challenge complete: ${fn.title}`);
    }
  };

  view.onclick = (e) => {
    const fb = e.target.closest("[data-fn]");
    if (fb) {
      fn = FUNCS.find((f) => f.id === fb.dataset.fn) || fn;
      store.set(FN_KEY, fn.id);
      renderFns();
      renderBody();
      return;
    }
    const b = e.target.closest("[data-act]");
    if (!b) return;
    const i = +b.dataset.i;
    const act = b.dataset.act;
    if (act === "del") {
      cases().splice(i, 1);
      save();
      focus = null;
    } else if (act === "focus") {
      focus = focus === i ? null : i;
    } else if (act === "unfocus") {
      focus = null;
    } else if (act === "clear") {
      if (cases().length && !confirm("Remove every test for this function?")) return;
      suites[fn.id] = [];
      save();
      focus = null;
    } else if (act === "solution") {
      if (cases().length && !confirm("Replace your suite with a sample solution?")) return;
      suites[fn.id] = fn.solution.map((c) => ({ args: { ...c.args }, expect: c.expect }));
      save();
      focus = null;
    } else if (act === "hint") {
      const kind = b.dataset.kind;
      const list = fn.hints[kind];
      const text = list[hintIdx[kind] % list.length];
      hintIdx[kind]++;
      $("#qaHint").innerHTML = `<div class="qa-hint"><span class="pill neutral">${kind === "boundary" ? "boundary values" : "equivalence classes"}</span> ${esc(text)}</div>`;
      return;
    } else return;
    refresh();
  };

  renderFns();
  renderBody();
  return () => {
    view.onclick = null;
  };
}

// ===================================================================== Test Runner
const T_SETUP = `import unittest


class ShoppingCart:
    def __init__(self):
        self.items = {}

    def add(self, name, price, qty=1):
        if qty <= 0:
            raise ValueError("qty must be positive")
        _, have = self.items.get(name, (price, 0))
        self.items[name] = (price, have + qty)

    def total(self):
        return sum(price * qty for price, qty in self.items.values())


class CartTest(unittest.TestCase):
    def setUp(self):
        # Runs before EVERY test, so each test gets a fresh cart.
        self.cart = ShoppingCart()
        self.cart.add("apple", 0.5, qty=4)

    def tearDown(self):
        # Runs after every test, even when the test fails.
        self.cart = None

    def test_total(self):
        self.assertEqual(self.cart.total(), 2.0)

    def test_same_item_accumulates(self):
        self.cart.add("apple", 0.5, qty=2)
        self.assertEqual(self.cart.items["apple"], (0.5, 6))

    def test_rejects_zero_quantity(self):
        with self.assertRaises(ValueError):
            self.cart.add("pear", 1.0, qty=0)

    @unittest.skip("demo of a skipped test")
    def test_coupons(self):
        pass


if __name__ == "__main__":
    unittest.main()
`;

const T_SUBTEST = `import unittest


def is_leap(year):
    # Bug on purpose: forgets the "divisible by 400" rule.
    return year % 4 == 0 and year % 100 != 0


class LeapYearTest(unittest.TestCase):
    CASES = [
        (2024, True),   # divisible by 4
        (2023, False),  # not divisible by 4
        (1900, False),  # century, not divisible by 400
        (2000, True),   # divisible by 400: this case fails
        (2400, True),   # and so does this one
    ]

    def test_cases(self):
        # subTest reports every failing case and keeps going.
        for year, expected in self.CASES:
            with self.subTest(year=year):
                self.assertEqual(is_leap(year), expected)

    def test_rejects_text(self):
        with self.assertRaises(TypeError):
            is_leap("2024")
`;

const T_MOCK = `import unittest
from unittest import mock


def get_rate(currency):
    # Imagine an HTTP call here. Tests must never reach it.
    raise ConnectionError("network is disabled in tests")


def to_eur(amount_usd):
    return round(amount_usd * get_rate("EUR"), 2)


class Checkout:
    def __init__(self, gateway):
        self.gateway = gateway  # injected dependency

    def pay(self, amount):
        if amount <= 0:
            raise ValueError("amount must be positive")
        receipt = self.gateway.charge(amount=amount, currency="USD")
        return receipt["id"]


class MockingTest(unittest.TestCase):
    # Patch the name where it is looked up: this module (__main__).
    @mock.patch("__main__.get_rate", return_value=0.5)
    def test_patch_replaces_function(self, fake_rate):
        self.assertEqual(to_eur(10), 5.0)
        fake_rate.assert_called_once_with("EUR")

    def test_side_effect_simulates_failure(self):
        with mock.patch("__main__.get_rate", side_effect=TimeoutError("slow")):
            with self.assertRaises(TimeoutError):
                to_eur(10)

    def test_injected_mock_records_calls(self):
        gateway = mock.Mock()
        gateway.charge.return_value = {"id": "rcpt-1"}
        self.assertEqual(Checkout(gateway).pay(20), "rcpt-1")
        gateway.charge.assert_called_once_with(amount=20, currency="USD")

    def test_no_charge_for_invalid_amount(self):
        gateway = mock.Mock()
        with self.assertRaises(ValueError):
            Checkout(gateway).pay(0)
        gateway.charge.assert_not_called()

    def test_unpatched_call_errors(self):
        # Without a patch the real dependency runs: reported as ERROR.
        to_eur(10)
`;

const T_EXC = `import unittest


class InsufficientFunds(Exception):
    def __init__(self, needed):
        super().__init__(f"need {needed} more")
        self.needed = needed


class Account:
    def __init__(self, balance=0):
        self.balance = balance

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("amount must be positive")
        if amount > self.balance:
            raise InsufficientFunds(amount - self.balance)
        self.balance -= amount
        return self.balance


class AccountTest(unittest.TestCase):
    def test_rejects_negative(self):
        with self.assertRaises(ValueError):
            Account(10).withdraw(-5)

    def test_message_matches(self):
        with self.assertRaisesRegex(ValueError, "positive"):
            Account(10).withdraw(0)

    def test_exception_carries_details(self):
        with self.assertRaises(InsufficientFunds) as ctx:
            Account(10).withdraw(25)
        self.assertEqual(ctx.exception.needed, 15)

    def test_balance_unchanged_after_failure(self):
        acct = Account(10)
        with self.assertRaises(InsufficientFunds):
            acct.withdraw(11)
        self.assertEqual(acct.balance, 10)

    def test_wrong_on_purpose(self):
        # FAILS: withdrawing the whole balance is allowed. Fix the test.
        with self.assertRaises(InsufficientFunds):
            Account(10).withdraw(10)

    def test_error_not_failure(self):
        # An unexpected exception is an ERROR, not a FAIL.
        Account(10).withdraw("ten")
`;

const T_FLAKY = `import random
import unittest
from unittest import mock


def roll():
    return random.randint(1, 6)


def got_a_six(rolls):
    return any(roll() == 6 for _ in range(rolls))


class DiceTest(unittest.TestCase):
    def test_flaky_unseeded(self):
        # Passes only about half the time: it depends on luck.
        # Press "Run 5 times" and watch it flip between pass and fail.
        self.assertTrue(got_a_six(4))

    def test_seeded_is_repeatable(self):
        random.seed(1234)
        first = [roll() for _ in range(10)]
        random.seed(1234)
        second = [roll() for _ in range(10)]
        self.assertEqual(first, second)

    def test_mocked_randomness(self):
        with mock.patch("random.randint", return_value=6):
            self.assertTrue(got_a_six(1))

    def test_property_holds_for_any_roll(self):
        rolls = [roll() for _ in range(200)]
        self.assertTrue(all(1 <= r <= 6 for r in rolls))
`;

export const TEMPLATES = [
  { id: "setup", label: "TestCase with setUp and tearDown", code: T_SETUP },
  { id: "subtest", label: "Parametrised cases with subTest", code: T_SUBTEST },
  { id: "mock", label: "Mocking with unittest.mock", code: T_MOCK },
  { id: "exceptions", label: "Testing exceptions", code: T_EXC },
  { id: "flaky", label: "A flaky test: random with and without seed", code: T_FLAKY },
];

const HARNESS = String.raw`import json as _qa_json, sys as _qa_sys, time as _qa_time, traceback as _qa_tb, types as _qa_types, unittest as _qa_unittest

_qa_src = __QA_SRC__
_qa_unittest.main = lambda *a, **k: None
_qa_mod = _qa_types.ModuleType("__main__")
_qa_sys.modules["__main__"] = _qa_mod
_qa_rows = []


def _qa_emit(obj):
    print("@@QA " + _qa_json.dumps(obj))


class _QAResult(_qa_unittest.TextTestResult):
    def startTest(self, test):
        self._qa_t0 = _qa_time.perf_counter()
        super().startTest(test)

    def _qa(self, test, status, err=None, name=None):
        ms = (_qa_time.perf_counter() - getattr(self, "_qa_t0", _qa_time.perf_counter())) * 1000
        detail = self._exc_info_to_string(err, test) if isinstance(err, tuple) else str(err or "")
        _qa_rows.append({"id": name or test.id(), "status": status, "ms": round(ms, 2), "detail": detail[-1500:]})

    def addSuccess(self, test):
        super().addSuccess(test)
        self._qa(test, "pass")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._qa(test, "fail", err)

    def addError(self, test, err):
        super().addError(test, err)
        self._qa(test, "error", err)

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self._qa(test, "skip", reason)

    def addExpectedFailure(self, test, err):
        super().addExpectedFailure(test, err)
        self._qa(test, "xfail", err)

    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test)
        self._qa(test, "xpass")

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        if err is not None:
            failed = test.failureException is not None and issubclass(err[0], test.failureException)
            self._qa(test, "fail" if failed else "error", err, subtest.id())


def _qa_run():
    try:
        exec(compile(_qa_src, "<tests>", "exec"), _qa_mod.__dict__)
    except SystemExit:
        pass
    except BaseException as e:
        frames = [f for f in _qa_tb.extract_tb(e.__traceback__) if f.filename == "<tests>"]
        syntax = isinstance(e, SyntaxError)
        line = e.lineno if syntax else (frames[-1].lineno if frames else None)
        msg = e.msg if syntax else str(e)
        _qa_emit({"error": {"type": type(e).__name__, "message": msg, "line": line, "trace": "".join(_qa_tb.format_list(frames)) + type(e).__name__ + ": " + msg}})
        return
    loader = _qa_unittest.TestLoader()
    suite = _qa_unittest.TestSuite()
    seen = set()
    for obj in list(vars(_qa_mod).values()):
        if isinstance(obj, type) and issubclass(obj, _qa_unittest.TestCase) and obj.__module__ == "__main__" and obj not in seen:
            seen.add(obj)
            suite.addTests(loader.loadTestsFromTestCase(obj))
    if not seen:
        print("No unittest.TestCase classes found: the code ran, but there were no tests to run.")
    t0 = _qa_time.perf_counter()
    res = _qa_unittest.TextTestRunner(stream=_qa_sys.stdout, verbosity=2, resultclass=_QAResult).run(suite)
    for row in _qa_rows:
        _qa_emit(row)
    _qa_emit({"summary": {"ran": res.testsRun, "ok": res.wasSuccessful(), "classes": len(seen), "ms": round((_qa_time.perf_counter() - t0) * 1000, 2)}})


_qa_run()
`;

/** Wraps learner code so its TestCases run via TextTestRunner(stream=sys.stdout, verbosity=2) without sys.exit. */
export const wrapTests = (code) => HARNESS.replace("__QA_SRC__", () => JSON.stringify(String(code)));

const VERBOSE = /^(\w+) \(([\w.]+)\)(?: \[.*\])?(?: \(.*\))? \.\.\. (ok|FAIL|ERROR|skipped.*|expected failure|unexpected success)\s*$/;
const STATUS_OF = { ok: "pass", FAIL: "fail", ERROR: "error", "expected failure": "xfail", "unexpected success": "xpass" };

/** Splits runner stdout into result rows, summary, harness error and the plain text output. */
export function parseRunnerOutput(stdout) {
  const rows = [];
  const text = [];
  let summary = null;
  let error = null;
  for (const line of String(stdout || "").split("\n")) {
    if (line.startsWith("@@QA ")) {
      try {
        const o = JSON.parse(line.slice(5));
        if (o.summary) summary = o.summary;
        else if (o.error) error = o.error;
        else if (o.id) rows.push(o);
        continue;
      } catch {
        /* not ours: keep as text */
      }
    }
    text.push(line);
  }
  if (!rows.length && !summary) {
    for (const line of text) {
      const m = line.match(VERBOSE);
      if (m) rows.push({ id: `${m[2]}`, status: STATUS_OF[m[3]] || "skip", ms: null, detail: "" });
    }
  }
  return {
    rows: rows.map((r) => ({ ...r, name: String(r.id).replace(/^__main__\./, "") })),
    summary,
    error,
    text: text.join("\n").replace(/\n+$/, "\n"),
  };
}

export function tally(rows) {
  const c = { pass: 0, fail: 0, error: 0, skip: 0, xfail: 0, xpass: 0 };
  rows.forEach((r) => (c[r.status] = (c[r.status] || 0) + 1));
  return c;
}

const STATUS_PILL = { pass: "ok", fail: "bad", error: "bad", skip: "neutral", xfail: "warn", xpass: "warn" };
const STATUS_LABEL = { pass: "pass", fail: "fail", error: "error", skip: "skipped", xfail: "expected failure", xpass: "unexpected success" };
const pillFor = (s) => `<span class="pill ${STATUS_PILL[s] || "neutral"}">${esc(STATUS_LABEL[s] || s)}</span>`;
const msText = (ms) => (ms === null || ms === undefined ? "-" : `${ms < 1 ? ms.toFixed(2) : ms.toFixed(1)} ms`);
const firstLine = (detail) => {
  const lines = String(detail || "").trim().split("\n");
  return lines[lines.length - 1] || "";
};

function summaryHtml(parsed) {
  const { rows, summary } = parsed;
  if (!rows.length) return `<p class="muted">${summary ? "No tests ran. Define a class that extends <code>unittest.TestCase</code> with methods named <code>test_...</code>." : "No test results."}</p>`;
  const c = tally(rows);
  const ok = summary ? summary.ok : c.fail + c.error === 0;
  return `
    <div class="qa-sum">
      <span class="qa-verdict ${ok ? "ok" : "bad"}">${ok ? "OK" : "FAILED"}</span>
      <span class="qa-count ok"><b>${c.pass}</b> passed</span>
      <span class="qa-count bad"><b>${c.fail}</b> failed</span>
      <span class="qa-count bad"><b>${c.error}</b> errors</span>
      <span class="qa-count"><b>${c.skip}</b> skipped</span>
      ${c.xfail || c.xpass ? `<span class="qa-count"><b>${c.xfail + c.xpass}</b> expected-failure</span>` : ""}
      <span class="spacer"></span>
      <span class="muted">${summary ? `${summary.ran} run · ${msText(summary.ms)}` : ""}</span>
    </div>
    <div class="qa-table-wrap"><table class="qa-table qa-results">
      <thead><tr><th>Test</th><th>Status</th><th>Time</th><th>Details</th></tr></thead>
      <tbody>${rows.map((r) => `
        <tr class="${r.status === "fail" || r.status === "error" ? "bad" : ""}">
          <td><code>${esc(r.name)}</code></td>
          <td>${pillFor(r.status)}</td>
          <td class="num">${msText(r.ms)}</td>
          <td>${r.detail ? (r.status === "skip" ? `<span class="muted">${esc(r.detail)}</span>` : `<details><summary>${esc(firstLine(r.detail))}</summary><pre class="term-out">${esc(r.detail)}</pre></details>`) : ""}</td>
        </tr>`).join("")}</tbody>
    </table></div>`;
}

/** Groups several runs by test name; a test that both passed and failed is flaky. */
export function aggregateRuns(runs) {
  const by = new Map();
  runs.forEach((p, k) => p.rows.forEach((r) => {
    if (!by.has(r.name)) by.set(r.name, { name: r.name, statuses: Array(runs.length).fill(null), ms: [] });
    const e = by.get(r.name);
    e.statuses[k] = r.status;
    if (r.ms !== null && r.ms !== undefined) e.ms.push(r.ms);
  }));
  return [...by.values()].map((e) => {
    const seen = e.statuses.filter(Boolean);
    const passes = seen.filter((s) => s === "pass").length;
    const flaky = passes > 0 && seen.some((s) => s === "fail" || s === "error");
    return { ...e, passes, flaky, avg: e.ms.length ? e.ms.reduce((a, b) => a + b, 0) / e.ms.length : null };
  });
}

function repeatHtml(runs) {
  const agg = aggregateRuns(runs);
  if (!agg.length) return `<p class="muted">No tests ran.</p>`;
  const flaky = agg.filter((a) => a.flaky).length;
  return `
    <div class="qa-sum">
      <span class="qa-verdict ${flaky ? "bad" : "ok"}">${flaky ? `${flaky} flaky` : "stable"}</span>
      <span class="muted">${runs.length} runs of the same code. A test that both passes and fails without any change is flaky.</span>
    </div>
    <div class="qa-table-wrap"><table class="qa-table qa-results">
      <thead><tr><th>Test</th><th>Runs</th><th>Passed</th><th>Avg time</th></tr></thead>
      <tbody>${agg.map((a) => `
        <tr class="${a.flaky ? "bad" : ""}">
          <td><code>${esc(a.name)}</code> ${a.flaky ? `<span class="pill warn">flaky</span>` : ""}</td>
          <td><span class="qa-runs">${a.statuses.map((s) => `<i class="qa-run ${s || "none"}" title="${esc(STATUS_LABEL[s] || "did not run")}"></i>`).join("")}</span></td>
          <td>${a.passes} / ${runs.length}</td>
          <td class="num">${msText(a.avg)}</td>
        </tr>`).join("")}</tbody>
    </table></div>`;
}

const MAX_SRC = 15000;

export function playground(view, content) {
  const samples = sampleOptions(content, ["python"]);
  view.innerHTML = `
    ${labHero("TEST", "mint", "Test Runner", "Write code and its <code>unittest</code> tests in one file. The runner collects every <code>TestCase</code>, runs it with <code>TextTestRunner(verbosity=2)</code> in an isolated Python process and shows a pass, fail and error summary with timings.")}
    <div class="lab-grid side-right qa-runner">
      <div class="panel clay">
        <div class="row qa-runner-bar">
          <select id="qaTpl" aria-label="Load a template"><option value="">Load a template…</option>${TEMPLATES.map((t, i) => `<option value="${i}">${esc(t.label)}</option>`).join("")}</select>
          ${samples.length ? `<select id="qaSample" aria-label="Load a lesson sample"><option value="">Load a lesson sample…</option>${samples.map((s, i) => `<option value="${i}">${esc(s.label)}</option>`).join("")}</select>` : ""}
        </div>
        <textarea id="qaCodeEd" class="code code-editor" spellcheck="false" rows="20" aria-label="Python code and tests"></textarea>
        <div class="row qa-runner-bar">
          <button class="btn primary" id="qaRun">Run tests <kbd>⌘/Ctrl ↵</kbd></button>
          <button class="btn" id="qaRepeat">Run 5 times</button>
          <span class="muted" id="qaStatus" role="status"></span>
        </div>
      </div>
      <aside class="panel clay">
        <h3>How it works</h3>
        <ul class="tips">
          <li>Every class extending <code>unittest.TestCase</code> is collected; methods starting with <code>test</code> run in name order.</li>
          <li><b>FAIL</b> means an assertion did not hold. <b>ERROR</b> means the test crashed with an unexpected exception.</li>
          <li><code>unittest.main()</code> is ignored, so the file can stay runnable elsewhere.</li>
          <li>Patch names in this file as <code>"__main__.name"</code>.</li>
          <li><b>Run 5 times</b> reveals flaky tests: same code, different results.</li>
          <li>Standard library only, 6 second limit per run.</li>
        </ul>
      </aside>
    </div>
    <div class="panel clay qa-suite-panel"><h3>Results</h3><div id="qaSummary"><p class="muted">Run the tests to see a summary.</p></div></div>
    <div class="panel clay qa-suite-panel"><h3>Output</h3><div id="qaOut"><span class="muted">Runner output appears here.</span></div></div>`;

  const ta = $("#qaCodeEd");
  ta.value = takeHandoff("py-code") || store.get("qa-runner-code", "") || TEMPLATES[0].code;
  let busy = false;

  const once = async () => {
    const r = await runPython(wrapTests(ta.value));
    const parsed = parseRunnerOutput(r.stdout || "");
    const error = r.error || parsed.error;
    return { r: { ...r, ok: !error, error, stdout: parsed.text }, parsed };
  };

  const guard = () => {
    if (!ta.value.trim()) return "Nothing to run.";
    if (ta.value.length > MAX_SRC) return `Code is longer than ${MAX_SRC} characters.`;
    return "";
  };

  const setBusy = (on, msg = "") => {
    busy = on;
    $("#qaRun").disabled = $("#qaRepeat").disabled = on;
    $("#qaStatus").textContent = msg;
  };

  const run = async () => {
    if (busy) return;
    const bad = guard();
    if (bad) return ($("#qaStatus").textContent = bad);
    store.set("qa-runner-code", ta.value);
    setBusy(true, "Running…");
    const { r, parsed } = await once();
    setBusy(false);
    $("#qaSummary").innerHTML = summaryHtml(parsed);
    $("#qaOut").innerHTML = pyResultHtml(r);
  };

  const repeat = async () => {
    if (busy) return;
    const bad = guard();
    if (bad) return ($("#qaStatus").textContent = bad);
    store.set("qa-runner-code", ta.value);
    const runs = [];
    let last;
    for (let k = 0; k < 5; k++) {
      setBusy(true, `Run ${k + 1} of 5…`);
      last = await once();
      if (last.r.error) break;
      runs.push(last.parsed);
    }
    setBusy(false);
    $("#qaSummary").innerHTML = last.r.error ? summaryHtml(last.parsed) : repeatHtml(runs);
    $("#qaOut").innerHTML = pyResultHtml(last.r);
  };

  codeEditor(ta, run, 4);
  $("#qaRun").onclick = run;
  $("#qaRepeat").onclick = repeat;
  $("#qaTpl").onchange = (e) => {
    if (e.target.value !== "") ta.value = TEMPLATES[+e.target.value].code;
    e.target.value = "";
  };
  if (samples.length) {
    $("#qaSample").onchange = (e) => {
      if (e.target.value !== "") ta.value = samples[+e.target.value].code;
      e.target.value = "";
    };
  }
}
