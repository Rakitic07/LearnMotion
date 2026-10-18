import { $, $$, copy, esc, highlightCode, store, toast } from "../util.js";
import { codeEditor, labHero } from "./common.js";

// ===================================================================== pure maths helpers (exported for tests)
/** Small seeded PRNG (mulberry32) so datasets and toy weights are reproducible. Not for security. */
export function rng(seed = 1) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export function hashStr(s) {
  let h = 2166136261;
  for (const ch of String(s)) {
    h ^= ch.codePointAt(0);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

const clamp = (v, lo = -1, hi = 1) => Math.min(hi, Math.max(lo, v));

// ---- linear regression
export const mse = (pts, w, b) => pts.reduce((s, p) => s + (w * p.x + b - p.y) ** 2, 0) / Math.max(pts.length, 1);

/** One full-batch gradient descent step on MSE for y = w x + b. */
export function linRegStep(pts, w, b, lr) {
  const n = Math.max(pts.length, 1);
  let gw = 0;
  let gb = 0;
  for (const p of pts) {
    const e = w * p.x + b - p.y;
    gw += 2 * e * p.x;
    gb += 2 * e;
  }
  const nw = w - (lr * gw) / n;
  const nb = b - (lr * gb) / n;
  return { w: nw, b: nb, loss: mse(pts, nw, nb), grad: [gw / n, gb / n] };
}

/** Closed-form least squares, used to mark the bottom of the loss bowl. */
export function linRegSolve(pts) {
  const n = pts.length;
  if (!n) return { w: 0, b: 0 };
  const mx = pts.reduce((s, p) => s + p.x, 0) / n;
  const my = pts.reduce((s, p) => s + p.y, 0) / n;
  const sxx = pts.reduce((s, p) => s + (p.x - mx) ** 2, 0);
  const sxy = pts.reduce((s, p) => s + (p.x - mx) * (p.y - my), 0);
  const w = sxx > 1e-12 ? sxy / sxx : 0;
  return { w, b: my - w * mx };
}

// ---- classification
export const sigmoid = (z) => 1 / (1 + Math.exp(-z));
const clampP = (p) => Math.min(1 - 1e-9, Math.max(1e-9, p));
export const bce = (p, c) => -(c * Math.log(clampP(p)) + (1 - c) * Math.log(1 - clampP(p)));

export const logisticInit = () => ({ kind: "logistic", w: [0, 0], b: 0 });
export const logisticPredict = (m, x, y) => sigmoid(m.w[0] * x + m.w[1] * y + m.b);

/** Full-batch logistic regression step with L2. Returns a new model and the loss before the update. */
export function logisticStep(m, data, lr, l2 = 0) {
  let g0 = 0;
  let g1 = 0;
  let gb = 0;
  let loss = 0;
  for (const d of data) {
    const p = logisticPredict(m, d.x, d.y);
    const e = p - d.c;
    g0 += e * d.x;
    g1 += e * d.y;
    gb += e;
    loss += bce(p, d.c);
  }
  const n = Math.max(data.length, 1);
  return {
    model: { kind: "logistic", w: [m.w[0] - lr * (g0 / n + l2 * m.w[0]), m.w[1] - lr * (g1 / n + l2 * m.w[1])], b: m.b - (lr * gb) / n },
    loss: loss / n + 0.5 * l2 * (m.w[0] ** 2 + m.w[1] ** 2),
  };
}

/** 2 inputs -> `hidden` tanh units -> 1 sigmoid output. */
export function mlpInit(hidden = 8, seed = 7) {
  const r = rng(seed);
  const u = (s) => (r() * 2 - 1) * s;
  return {
    kind: "mlp",
    W1: Array.from({ length: hidden }, () => [u(1.6), u(1.6)]),
    b1: Array.from({ length: hidden }, () => u(0.6)),
    W2: Array.from({ length: hidden }, () => u(1)),
    b2: 0,
  };
}

export function mlpForward(m, x, y) {
  const h = m.W1.map((w, j) => Math.tanh(w[0] * x + w[1] * y + m.b1[j]));
  let z = m.b2;
  for (let j = 0; j < h.length; j++) z += m.W2[j] * h[j];
  return { h, p: sigmoid(z) };
}
export const mlpPredict = (m, x, y) => mlpForward(m, x, y).p;

/** Full-batch backprop step (binary cross-entropy + L2). Returns a new model and the loss before the update. */
export function mlpStep(m, data, lr, l2 = 0) {
  const H = m.W1.length;
  const gW1 = m.W1.map(() => [0, 0]);
  const gb1 = new Array(H).fill(0);
  const gW2 = new Array(H).fill(0);
  let gb2 = 0;
  let loss = 0;
  for (const d of data) {
    const { h, p } = mlpForward(m, d.x, d.y);
    const dz = p - d.c;
    loss += bce(p, d.c);
    gb2 += dz;
    for (let j = 0; j < H; j++) {
      gW2[j] += dz * h[j];
      const dh = dz * m.W2[j] * (1 - h[j] * h[j]);
      gW1[j][0] += dh * d.x;
      gW1[j][1] += dh * d.y;
      gb1[j] += dh;
    }
  }
  const n = Math.max(data.length, 1);
  let reg = 0;
  for (const w of m.W1) reg += w[0] ** 2 + w[1] ** 2;
  for (const w of m.W2) reg += w * w;
  return {
    model: {
      kind: "mlp",
      W1: m.W1.map((w, j) => [w[0] - lr * (gW1[j][0] / n + l2 * w[0]), w[1] - lr * (gW1[j][1] / n + l2 * w[1])]),
      b1: m.b1.map((b, j) => b - (lr * gb1[j]) / n),
      W2: m.W2.map((w, j) => w - lr * (gW2[j] / n + l2 * w)),
      b2: m.b2 - (lr * gb2) / n,
    },
    loss: loss / n + 0.5 * l2 * reg,
  };
}

export const predict = (m, x, y) => (m.kind === "mlp" ? mlpPredict(m, x, y) : logisticPredict(m, x, y));
export const trainStep = (m, data, lr, l2 = 0) => (m.kind === "mlp" ? mlpStep : logisticStep)(m, data, lr, l2);
export const accuracy = (m, data) => (data.length ? data.filter((d) => (predict(m, d.x, d.y) >= 0.5 ? 1 : 0) === d.c).length / data.length : 0);
export const dataLoss = (m, data) => (data.length ? data.reduce((s, d) => s + bce(predict(m, d.x, d.y), d.c), 0) / data.length : 0);

/** Two-class 2D datasets in [-1, 1]^2: "linear", "xor" or "circles". `noise` = fraction of flipped labels. */
export function makeDataset(kind, n = 120, seed = 3, noise = 0) {
  const r = rng(seed);
  const g = () => (r() + r() + r() - 1.5) / 1.5;
  const out = [];
  for (let i = 0; i < n; i++) {
    let x;
    let y;
    let c;
    if (kind === "linear") {
      c = i % 2;
      x = (c ? 0.42 : -0.42) + g() * 0.3;
      y = (c ? -0.32 : 0.36) + g() * 0.3;
    } else if (kind === "xor") {
      const q = i % 4;
      const sx = q & 1 ? 1 : -1;
      const sy = q & 2 ? 1 : -1;
      x = sx * (0.15 + r() * 0.75);
      y = sy * (0.15 + r() * 0.75);
      c = sx * sy > 0 ? 1 : 0;
    } else {
      c = i % 2;
      const rad = c ? r() * 0.38 : 0.6 + r() * 0.3;
      const a = r() * Math.PI * 2;
      x = rad * Math.cos(a);
      y = rad * Math.sin(a);
    }
    if (noise && r() < noise) c = 1 - c;
    out.push({ x: clamp(x, -0.98, 0.98), y: clamp(y, -0.98, 0.98), c });
  }
  return out;
}

// ---- attention and tokens
/** Numerically stable softmax: subtracts the max before exp, so large logits do not overflow. */
export function softmax(xs, temperature = 1) {
  const t = Math.max(temperature, 1e-6);
  const z = xs.map((v) => v / t);
  const m = Math.max(...z);
  const e = z.map((v) => Math.exp(v - m));
  const s = e.reduce((a, b) => a + b, 0);
  return e.map((v) => v / s);
}

const D = 8;
const CONCEPTS = [
  ["animal", ["cat", "cats", "dog", "dogs", "animal", "bird", "fox", "kitten", "puppy", "it", "he", "she", "they"]],
  ["place", ["mat", "street", "road", "home", "house", "park", "table", "floor", "bank", "river", "city", "garden"]],
  ["action", ["sat", "ran", "crossed", "jumped", "slept", "was", "is", "ate", "walked", "chased", "didn't", "barked"]],
  ["quality", ["tired", "happy", "sad", "hungry", "wide", "big", "small", "lazy", "quick", "brown", "old", "loud"]],
  ["function", ["the", "a", "an", "on", "in", "because", "and", "of", "to", "over", "at", "too", "so", "but"]],
];

/** Toy embedding: a hashed random vector plus a hand-picked "concept" direction (real models learn these). */
export function embed(word, d = D) {
  const low = String(word).toLowerCase();
  const r = rng(hashStr(low));
  const v = Array.from({ length: d }, () => (r() * 2 - 1) * 0.6);
  CONCEPTS.forEach(([, list], k) => {
    if (k < d && list.includes(low)) v[k] += 2.2;
  });
  return v;
}

export const positional = (pos, d = D) => Array.from({ length: d }, (_, i) => {
  const f = pos / 10000 ** ((2 * Math.floor(i / 2)) / d);
  return i % 2 ? Math.cos(f) : Math.sin(f);
});

const toyMatrix = (seed, diag) => {
  const r = rng(seed);
  return Array.from({ length: D }, (_, i) => Array.from({ length: D }, (_, j) => (i === j ? diag : 0) + (r() * 2 - 1) * 0.3));
};
const WQ = toyMatrix(11, 1);
const WK = toyMatrix(12, 1);
const WV = toyMatrix(13, 0.9);
const matVec = (v, M) => M[0].map((_, j) => v.reduce((s, vi, i) => s + vi * M[i][j], 0));
const dot = (a, b) => a.reduce((s, v, i) => s + v * b[i], 0);

/** Single-head self-attention over toy embeddings. Returns Q, K, V, raw scores, softmax weights and outputs. */
export function attentionScores(tokens, { causal = false, temperature = 1, scale = true } = {}) {
  const X = tokens.map((t, i) => {
    const pe = positional(i);
    return embed(t).map((v, k) => v + 0.3 * pe[k]);
  });
  const Q = X.map((x) => matVec(x, WQ));
  const K = X.map((x) => matVec(x, WK));
  const V = X.map((x) => matVec(x, WV));
  const s = scale ? Math.sqrt(D) : 1;
  const scores = Q.map((q, i) => K.map((k, j) => (causal && j > i ? -Infinity : dot(q, k) / s)));
  const weights = scores.map((row) => softmax(row, temperature));
  const out = weights.map((w) => V[0].map((_, k) => w.reduce((acc, wj, j) => acc + wj * V[j][k], 0)));
  return { X, Q, K, V, scores, weights, out, d: D };
}

const VOCAB = new Set("the a an and or but to of in on at for with from by is are was were be been it he she they we you i this that these those not no yes can will would should could have has had do does did so because if then than too very cat dog mat sat ran street road animal tired model data train token learn agent code test file word words long split into".split(" "));
const PREFIXES = ["inter", "trans", "under", "over", "pre", "dis", "un", "re"];
const SUFFIXES = ["ization", "ation", "ition", "ably", "ibly", "tion", "sion", "ness", "ment", "able", "ible", "ingly", "ing", "less", "ful", "ize", "est", "ers", "ly", "ed", "er", "s"];

function splitWord(w) {
  const low = w.toLowerCase();
  if (w.length <= 5 || VOCAB.has(low)) return [w];
  const pieces = [];
  let rest = w;
  for (const p of PREFIXES) {
    if (low.startsWith(p) && low.length - p.length >= 4) {
      pieces.push(w.slice(0, p.length));
      rest = w.slice(p.length);
      break;
    }
  }
  let suffix = "";
  const rl = rest.toLowerCase();
  for (const s of SUFFIXES) {
    if (rl.endsWith(s) && rest.length - s.length >= 3) {
      suffix = rest.slice(-s.length);
      rest = rest.slice(0, -s.length);
      break;
    }
  }
  const size = Math.ceil(rest.length / Math.ceil(rest.length / 8));
  for (let i = 0; i < rest.length; i += size) pieces.push(rest.slice(i, i + size));
  if (suffix) pieces.push(suffix);
  return pieces;
}

/** Toy WordPiece-style tokenizer: words, numbers in chunks of 3 digits, punctuation, long words split into pieces. */
export function tokenize(text) {
  const out = [];
  for (const m of String(text).matchAll(/[A-Za-z]+(?:'[A-Za-z]+)?|\d+|[^\sA-Za-z\d]/g)) {
    const w = m[0];
    let parts;
    if (/^\d+$/.test(w)) parts = w.match(/\d{1,3}/g);
    else if (/[A-Za-z]/.test(w)) parts = splitWord(w);
    else parts = [w];
    parts.forEach((p, i) => out.push({ text: p, cont: i > 0, id: hashStr(p.toLowerCase()) % 50000 }));
  }
  return out;
}

// ===================================================================== agent instruction linters (exported for tests)
const unquote = (v) => v.replace(/^(["'])(.*)\1$/, "$2");

/** Minimal YAML frontmatter parser: `key: value`, folded `>`/`|` blocks and `- item` lists. */
export function parseFrontmatter(text) {
  const src = String(text).replace(/\r\n?/g, "\n");
  const m = /^---[ \t]*\n([\s\S]*?)\n---[ \t]*(?:\n|$)/.exec(src);
  const data = Object.create(null);
  if (!m) return { ok: false, data, body: src, raw: "", lines: 0 };
  const lines = m[1].split("\n");
  let key = null;
  for (const line of lines) {
    const kv = /^([A-Za-z_][\w-]*)\s*:\s*(.*)$/.exec(line);
    if (kv) {
      key = kv[1];
      const v = kv[2].trim();
      data[key] = /^[>|][-+]?$/.test(v) ? "" : unquote(v);
      continue;
    }
    if (key && /^\s+\S/.test(line)) {
      const isItem = /^\s+-\s/.test(line);
      const item = unquote(line.trim().replace(/^-\s+/, ""));
      data[key] = data[key] ? `${data[key]}${isItem ? ", " : " "}${item}` : item;
    }
  }
  return { ok: true, data, body: src.slice(m[0].length), raw: m[1], lines: lines.length + 2 };
}

export function codeBlocks(text) {
  const out = [];
  for (const m of String(text).matchAll(/^\s*```([\w+-]*)[^\n]*\n([\s\S]*?)^\s*```[ \t]*$/gm)) out.push({ lang: m[1].toLowerCase(), code: m[2] });
  return out;
}
const stripCode = (text) => String(text).replace(/^\s*```[\s\S]*?^\s*```[ \t]*$/gm, "").replace(/`[^`\n]*`/g, "");

const SECRET_PATTERNS = [
  [/\bsk-[A-Za-z0-9_-]{6,}/, "API key starting with sk-"],
  [/\b[sr]k_(?:live|test)_[A-Za-z0-9]{6,}/, "Stripe-style key"],
  [/\bgh[pousr]_[A-Za-z0-9]{6,}/, "GitHub token"],
  [/\b(?:AKIA|ASIA|AGPA|AIDA|AROA)[0-9A-Z]{8,}/, "AWS access key id"],
  [/-----BEGIN/, "PEM private key or certificate block"],
  [/\bAIza[0-9A-Za-z_-]{10,}/, "Google API key"],
  [/\bxox[abposr]-[A-Za-z0-9-]{6,}/, "Slack token"],
  [/\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}/, "JWT"],
  [/\b[a-z][a-z0-9+.-]*:\/\/[^\s:/@]+:[^\s@/]+@/i, "connection string with a password"],
  [/\b(?:api[_-]?key|secret|token|passw(?:or)?d)\b["']?\s*[:=]\s*["']?(?![<{$])[A-Za-z0-9_\-/+]{12,}/i, "hard-coded credential"],
];

/** Lines that look like credentials: [{line, kind}] (1-based lines). */
export function findSecrets(text) {
  return String(text).split("\n").flatMap((line, i) => {
    const hit = SECRET_PATTERNS.find(([re]) => re.test(line));
    return hit ? [{ line: i + 1, kind: hit[1] }] : [];
  });
}

const VAGUE = /\b(properly|correctly|appropriately|as needed|as appropriate|when necessary|if needed|best practices|clean code|good code|etc|try to|reasonable|reasonably|somehow)\b/gi;
export const findVague = (text) => [...new Set([...stripCode(text).matchAll(VAGUE)].map((m) => m[0].toLowerCase()))];

const TEST_RE = /\b(pytest|jest|vitest|mocha|rspec|phpunit|unittest|go test|cargo test|mvnw? (?:-\S+ )*test|gradlew? test|dotnet test|(?:npm|pnpm|yarn|bun) (?:run )?test|make test|tox|nox)\b/;
const LINT_RE = /\b(lint|ruff|eslint|flake8|black|prettier|gofmt|golangci|clippy|mypy|tsc|rubocop)\b/;
const SETUP_RE = /\b(install|sync|venv|bootstrap|build|compose|make|setup|run)\b/;
const RULE_LINE = /^\s*[-*]\s+((?:never|do not|don't|avoid|ask before|must not|only)\b.*)$/gim;
const HAS_RULE = /^\s*[-*]\s+(?:never|do not|don't|avoid|ask before|must not|only)\b/im;

const check = (label, ok, tip) => ({ label, ok: !!ok, tip });
function summarise(checks, warnings) {
  const passed = checks.filter((c) => c.ok).length;
  return { checks, warnings, passed, total: checks.length, score: Math.round((passed / checks.length) * 100) };
}
const secretCheck = (text) => {
  const s = findSecrets(text);
  return check("No secrets", !s.length, s.map((x) => `Line ${x.line}: possible secret (${x.kind}), move to environment variables.`).join(" ") || "");
};
const vagueCheck = (text) => {
  const v = findVague(text);
  return check("No vague wording", !v.length, `Replace vague words (${v.join(", ")}) with concrete, checkable instructions.`);
};

export function lintAgents(text) {
  const src = String(text);
  const lines = src.split("\n");
  const cmds = codeBlocks(src).map((b) => b.code).join("\n");
  const headings = [...src.matchAll(/^#{1,6}\s+(.+)$/gm)].map((m) => m[1].toLowerCase());
  const checks = [
    check("Project overview", headings.some((h) => /overview|about|project|summary|introduction|architecture/.test(h)), "Start with a short \"## Project overview\": what the app is, the stack and where the main folders live."),
    check("Setup / build commands in code blocks", SETUP_RE.test(cmds), "Put exact setup and build commands inside fenced code blocks so the agent can copy them."),
    check("Test command in a code block", TEST_RE.test(cmds), "Add the exact test command (for example `pytest -q` or `npm test`) in a fenced code block."),
    check("Code style section", headings.some((h) => /style|convention|standard|guideline|formatting/.test(h)), "Add a \"## Code style\" section with concrete conventions (naming, formatting, patterns)."),
    check("Boundaries / do-not rules", HAS_RULE.test(src), "List hard boundaries as bullets starting with Never / Do not / Ask before."),
    check(`Concise (${lines.length} of 150 lines)`, lines.length <= 150, "Keep AGENTS.md under about 150 lines; link to longer docs instead of pasting them."),
    secretCheck(src),
    vagueCheck(src),
  ];
  const warnings = [];
  if (!LINT_RE.test(cmds)) warnings.push("No lint or format command found. Agents self-check better when they can run one.");
  if (!headings.length) warnings.push("No headings: sections make the file easier for both agents and humans to scan.");
  return summarise(checks, warnings);
}

const WHEN_RE = /\b(use (?:it |this (?:skill )?)?(?:when|for|if|whenever|to)|when (?:the )?(?:user|you|asked|working|editing|reviewing)|trigger(?:s|ed)? (?:when|on|by)|whenever)\b/i;

export function lintSkill(text) {
  const src = String(text);
  const fm = parseFrontmatter(src);
  const name = fm.data.name ?? "";
  const desc = fm.data.description ?? "";
  const whenAt = desc.search(WHEN_RE);
  const whatWords = (whenAt >= 0 ? desc.slice(0, whenAt) : desc).split(/\s+/).filter(Boolean).length;
  const steps = (fm.body.match(/^\s*\d+[.)]\s+\S/gm) || []).length;
  const lines = src.split("\n").length;
  const checks = [
    check("YAML frontmatter", fm.ok, "Start the file with a --- block containing name and description."),
    check("name: lowercase-hyphen, max 64 chars", /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(name) && name.length <= 64, name ? `"${name}" must use only lowercase letters, digits and single hyphens, up to 64 characters.` : "Add name: my-skill-name to the frontmatter."),
    check(`description present, max 1024 chars (${desc.length})`, desc.length > 0 && desc.length <= 1024, desc ? "Shorten the description to 1024 characters or fewer." : "Add a description: the agent decides whether to load the skill from it."),
    check("description says what it does", desc && whatWords >= 4, "Open the description with what the skill does, for example \"Extracts tables from PDFs and ...\"."),
    check("description says when to use it", WHEN_RE.test(desc), "Add the trigger: \"Use when the user asks for ...\"."),
    check(`Step-by-step instructions (${steps} numbered steps)`, steps >= 3 || /^#{2,4}\s+step\b/im.test(fm.body), "Write the workflow as a numbered list of at least 3 steps."),
    check("Links extra files (progressive disclosure)", /\]\((?!https?:|#|mailto:)[^)\s]+\.(?:md|py|sh|js|ts|json|txt|ya?ml|csv)\)/i.test(fm.body) || /\b(?:references?|scripts|assets|examples|templates)\/[\w./-]+\.\w+/.test(fm.body), "Move long details into files such as reference.md or scripts/tool.py and link them, so they load only when needed."),
    check(`Under 500 lines (${lines})`, lines < 500, "Split the skill: keep SKILL.md under 500 lines and move detail into linked files."),
    secretCheck(src),
  ];
  const warnings = [];
  if (/\b(I can|I will|I'll|you can)\b/i.test(desc)) warnings.push("Write the description in the third person (\"Generates ...\"), not \"I can\" or \"you can\".");
  if (/\b(anthropic|claude)\b/.test(name)) warnings.push("Avoid reserved words such as \"anthropic\" or \"claude\" in the skill name.");
  const vague = findVague(fm.body);
  if (vague.length) warnings.push(`Vague wording in the body: ${vague.join(", ")}.`);
  return summarise(checks, warnings);
}

export function lintRule(text) {
  const src = String(text);
  const fm = parseFrontmatter(src);
  const d = fm.data;
  const lines = src.split("\n").length;
  const bullets = (fm.body.match(/^\s*[-*]\s+\S/gm) || []).length;
  const always = String(d.alwaysApply ?? "").trim();
  const globs = String(d.globs ?? "").trim();
  const checks = [
    check("YAML frontmatter", fm.ok, "Start the rule with a --- block holding description, globs and alwaysApply."),
    check("description present", String(d.description ?? "").trim().length >= 10, "Add a one-line description; agent-requested rules are picked by it."),
    check("globs field present", "globs" in d, "Add globs: (for example app/**/*.py) or leave it empty explicitly."),
    check("alwaysApply is true or false", /^(true|false)$/.test(always), "Set alwaysApply: true for every chat, or false to attach by globs or description."),
    check(`Short (${lines} of 60 lines)`, lines <= 60, "Rules are injected into context: keep each one under about 60 lines and split big ones."),
    check("Concrete bullets or an example", bullets >= 2 || codeBlocks(fm.body).length > 0, "Give specific bullets or a short code example, not a paragraph of advice."),
    vagueCheck(fm.body),
    secretCheck(src),
  ];
  const warnings = [];
  if (always === "true" && globs) warnings.push("globs are ignored when alwaysApply is true.");
  if (always === "false" && !globs && String(d.description ?? "").trim()) warnings.push("No globs: this is an agent-requested rule, attached only when the agent finds the description relevant.");
  if (always === "false" && !globs && !String(d.description ?? "").trim()) warnings.push("With alwaysApply false, no globs and no description, this rule will never be applied.");
  if (!fm.body.trim()) warnings.push("The rule body is empty.");
  return summarise(checks, warnings);
}

// ===================================================================== safe markdown preview
const CODE_LANG = { bash: "bash", sh: "bash", shell: "bash", zsh: "bash", console: "bash", python: "python", py: "python", yaml: "yaml", yml: "yaml", json: "json", sql: "sql", java: "java" };
const codeHl = (code, lang) => (CODE_LANG[lang] ? highlightCode(code, CODE_LANG[lang]) : esc(code));

/** Inline markdown: `code` and **bold** (and *em*). Everything else is escaped. */
export function inlineMd(s) {
  return String(s).split(/(`[^`]+`)/).map((part, i) => (i % 2
    ? `<code>${esc(part.slice(1, -1))}</code>`
    : esc(part).replace(/\*\*(?=\S)(.+?)\*\*/g, "<strong>$1</strong>").replace(/(^|[^*\w])\*(?=\S)([^*]+?)\*(?![*\w])/g, "$1<em>$2</em>"))).join("");
}

/** Tiny markdown renderer: frontmatter, headings, lists, fenced code, blockquotes, inline code, bold. No raw HTML. */
export function renderMarkdown(src) {
  const text = String(src).replace(/\r\n?/g, "\n");
  const lines = text.split("\n");
  const out = [];
  let para = [];
  let list = null;
  let i = 0;
  const flushPara = () => {
    if (para.length) out.push(`<p>${inlineMd(para.join(" "))}</p>`);
    para = [];
  };
  const closeList = () => {
    if (list) out.push(`</${list}>`);
    list = null;
  };
  const fm = /^---[ \t]*\n([\s\S]*?)\n---[ \t]*(?:\n|$)/.exec(text);
  if (fm) {
    out.push(`<pre class="mlx-fm"><code>${highlightCode(fm[1], "yaml")}</code></pre>`);
    i = fm[1].split("\n").length + 2;
  }
  for (; i < lines.length; i++) {
    const line = lines[i];
    const fence = /^\s*```\s*([\w+-]*)/.exec(line);
    if (fence) {
      flushPara();
      closeList();
      const buf = [];
      i++;
      while (i < lines.length && !/^\s*```\s*$/.test(lines[i])) buf.push(lines[i++]);
      out.push(`<pre class="mlx-pre"><code>${codeHl(buf.join("\n"), fence[1].toLowerCase())}</code></pre>`);
      continue;
    }
    const h = /^(#{1,6})\s+(.*)$/.exec(line);
    if (h) {
      flushPara();
      closeList();
      out.push(`<h${h[1].length}>${inlineMd(h[2].replace(/\s+#+\s*$/, ""))}</h${h[1].length}>`);
      continue;
    }
    if (/^\s*(?:-{3,}|\*{3,}|_{3,})\s*$/.test(line)) {
      flushPara();
      closeList();
      out.push("<hr>");
      continue;
    }
    const li = /^(\s*)(?:([-*+])|(\d+)[.)])\s+(.*)$/.exec(line);
    if (li) {
      flushPara();
      const type = li[2] ? "ul" : "ol";
      if (list !== type) {
        closeList();
        out.push(`<${type}>`);
        list = type;
      }
      const depth = Math.min(3, Math.floor(li[1].replace(/\t/g, "  ").length / 2));
      out.push(`<li${depth ? ` class="d${depth}"` : ""}>${inlineMd(li[4])}</li>`);
      continue;
    }
    const bq = /^\s*>\s?(.*)$/.exec(line);
    if (bq) {
      flushPara();
      closeList();
      out.push(`<blockquote>${inlineMd(bq[1])}</blockquote>`);
      continue;
    }
    if (!line.trim()) {
      flushPara();
      closeList();
      continue;
    }
    closeList();
    para.push(line.trim());
  }
  flushPara();
  closeList();
  return out.join("\n");
}

// ===================================================================== agent loop simulator (pure)
/** Reads the commands and rules an agent would pick up from an AGENTS.md. */
export function extractInstructions(md) {
  const src = String(md || "");
  const cmdLines = codeBlocks(src).flatMap((b) => b.code.split("\n")).map((l) => l.trim()).filter((l) => l && !l.startsWith("#"));
  const find = (re) => cmdLines.find((l) => re.test(l)) || null;
  const rules = [...src.matchAll(RULE_LINE)].map((m) => m[1].trim());
  const styleSec = /^#{1,6}\s+[^\n]*(?:style|convention)[^\n]*\n([\s\S]*?)(?=^#{1,6}\s|$(?![\s\S]))/im.exec(src);
  const style = styleSec ? (styleSec[1].match(/^\s*[-*]\s+(.+)$/m) || [])[1] || null : null;
  return {
    test: find(TEST_RE),
    lint: find(LINT_RE),
    setup: cmdLines.find((l) => /\binstall|sync\b/.test(l)) || null,
    rules,
    style,
    noDeps: rules.find((r) => /dependenc|package|librar/i.test(r)) || null,
    noSecrets: rules.find((r) => /secret|credential|\.env|api key/i.test(r)) || null,
    protectedPath: rules.find((r) => /\b(edit|modify|touch|change|write)\b/i.test(r) && /`[^`]+`/.test(r)) || null,
  };
}

export const AGENT_TASKS = [
  { id: "fix-test", label: "Fix a failing test", goal: "Make the failing date-parser test pass." },
  { id: "endpoint", label: "Add a /health endpoint", goal: "Add GET /health that returns the app version." },
  { id: "upgrade", label: "Upgrade the HTTP client", goal: "Upgrade the HTTP client library to its next major version." },
];

/** Deterministic Plan -> Tool call -> Observation -> Reflect trace for a task, shaped by the AGENTS.md text. */
export function planAgentRun(taskId, md) {
  const I = extractInstructions(md);
  const s = [];
  const plan = (text, cite) => s.push({ phase: "plan", text, cite });
  const tool = (text, code, cite) => s.push({ phase: "tool", text, code, cite });
  const obs = (code) => s.push({ phase: "obs", text: "Tool output", code });
  const reflect = (text, cite) => s.push({ phase: "reflect", text, cite });
  const guessTests = () => {
    tool("No documented test command, so guess the most common one", "npm test");
    obs('npm ERR! Missing script: "test"');
    reflect("Wrong ecosystem. Explore the repository to work out how tests run.");
    tool("List the repository root", "ls");
    obs("app/  tests/  requirements.txt  pyproject.toml  .venv/");
    tool("Try pytest on the global interpreter", "pytest");
    obs("ModuleNotFoundError: No module named 'flask'");
    reflect("The global Python lacks the dependencies. Try the virtualenv.");
    return ".venv/bin/python -m pytest";
  };
  const runTests = (failing) => {
    if (I.test) tool("Run the documented test command", I.test, `test command \`${I.test}\``);
    else tool("Run the tests with the command that worked last time", ".venv/bin/python -m pytest");
    obs(failing || "42 passed in 1.8s");
  };
  const lint = () => {
    if (I.lint) {
      tool("Run the linter before reporting back", I.lint, `lint command \`${I.lint}\``);
      obs("All checks passed!");
    } else reflect("No lint command documented, so formatting is left unverified.");
  };

  if (taskId === "fix-test") {
    plan("Reproduce the failure first, then make the smallest fix that turns it green.");
    if (I.test) {
      tool("Run the documented test command", I.test, `test command \`${I.test}\``);
    } else {
      tool("Run the tests from the virtualenv", guessTests());
    }
    obs("FAILED tests/test_dates.py::test_iso_week - assert 52 == 53\n1 failed, 41 passed");
    reflect("The failure is in ISO week numbering near the end of the year. Read the parser.");
    tool("Read the source file", "read_file app/dates.py");
    obs("41  def iso_week(d):\n42      return d.isocalendar()[1] - 1");
    reflect("Off-by-one: isocalendar() is already 1-based, so the - 1 is wrong.");
    tool("Edit the file", "edit app/dates.py  (line 42: drop the '- 1')", I.style ? `code style: ${I.style}` : null);
    runTests();
    lint();
  } else if (taskId === "endpoint") {
    plan("Find where routes live, follow the existing pattern, add a test, then verify.");
    tool("Search for existing routes", 'grep -rn "Blueprint\\|@bp\\." app/');
    obs("app/routes.py:8: bp = Blueprint(\"api\", __name__)\napp/routes.py:14: @bp.get(\"/items\")");
    if (I.noSecrets) reflect("Read the version from package metadata, never from .env or hard-coded keys.", I.noSecrets);
    else reflect("Read the version from the config file (it also holds other settings).");
    if (I.protectedPath) reflect("Keep the change inside app/routes.py and leave protected paths alone.", I.protectedPath);
    tool("Add the route and a test", "edit app/routes.py   (+ @bp.get(\"/health\"))\nedit tests/test_api.py (+ test_health)", I.style ? `code style: ${I.style}` : null);
    if (!I.test) tool("Find a way to run the tests", guessTests());
    runTests();
    lint();
  } else {
    plan("Bump the library version, reinstall, and fix whatever breaks.");
    if (I.noDeps) {
      reflect("Dependency changes need approval here, so stop before editing anything.", I.noDeps);
      tool("Ask the user", 'ask_user "httpclient 2.x -> 3.0 is a major upgrade with breaking changes. Proceed?"');
      obs("(waiting for the user's answer)");
    } else {
      tool("Edit the requirements file", "edit requirements.txt  (httpclient==2.31 -> httpclient==3.0)");
      tool("Reinstall dependencies", I.setup || "pip install -r requirements.txt");
      obs("Successfully installed httpclient-3.0");
      if (!I.test) tool("Find a way to run the tests", guessTests());
      runTests("FAILED 3 tests: Session.mount() got an unexpected keyword 'retries'");
      reflect("A major upgrade broke three call sites. Nothing says to ask first, so keep going.");
      tool("Rewrite the call sites", "edit app/client.py app/sync.py app/webhooks.py");
      runTests();
      lint();
    }
  }
  const calls = s.filter((x) => x.phase === "tool").length;
  const cited = s.filter((x) => x.cite).length;
  const stopped = taskId === "upgrade" && I.noDeps;
  s.push({ phase: "done", text: stopped ? `Stopped safely after ${calls} tool calls and handed the decision to the user.` : `Finished in ${calls} tool calls. ${cited ? `${cited} decisions came straight from AGENTS.md.` : "Every command was a guess, because there were no instructions."}` });
  return s;
}

// ===================================================================== UI helpers
const reduceMotion = () => typeof matchMedia === "function" && matchMedia("(prefers-reduced-motion: reduce)").matches;
const cssVar = (el, name, fallback) => getComputedStyle(el).getPropertyValue(name).trim() || fallback;
const fmt = (v, d = 3) => (!Number.isFinite(v) ? "overflow" : Math.abs(v) >= 1e4 ? v.toExponential(2) : v.toFixed(d));
const pct = (v) => `${Math.round(v * 100)}%`;
const toView = (el, e) => {
  const r = el.getBoundingClientRect();
  return [((e.clientX - r.left) / r.width) * 100, ((e.clientY - r.top) / r.height) * 100];
};
const lim = (v) => Math.max(-500, Math.min(600, v));
const stat = (label, value, tone = "neutral") => `<div class="panel clay stat-card"><span class="muted">${esc(label)}</span><b class="pill ${tone}">${esc(value)}</b></div>`;

function lossCurve(hist, extra = null) {
  const W = 300;
  const H = 90;
  const all = [...hist, ...(extra || [])].filter((v) => Number.isFinite(v) && v > 0);
  if (hist.length < 2 || !all.length) return `<p class="muted mlx-note">Run a few steps to see the curve.</p>`;
  const lo = Math.log10(Math.min(...all));
  const hi = Math.log10(Math.max(...all));
  const span = hi - lo || 1;
  const line = (h, cls) => {
    const stride = Math.max(1, Math.ceil(h.length / 300));
    const pts = [];
    for (let i = 0; i < h.length; i += stride) {
      const v = h[i];
      const y = Number.isFinite(v) && v > 0 ? H - ((Math.log10(v) - lo) / span) * (H - 6) - 3 : 0;
      pts.push(`${((i / Math.max(h.length - 1, 1)) * W).toFixed(1)},${y.toFixed(1)}`);
    }
    return `<polyline class="${cls}" points="${pts.join(" ")}"/>`;
  };
  return `<svg viewBox="0 0 ${W} ${H}" preserveAspectRatio="none" class="mlx-curve-svg" role="img" aria-label="Loss curve">${line(hist, "mlx-c1")}${extra ? line(extra, "mlx-c2") : ""}</svg>
    <div class="mlx-curve-axis muted"><span>epoch 0</span><span>${hist.length - 1}</span></div>`;
}

function download(name, text) {
  const url = URL.createObjectURL(new Blob([text], { type: "text/markdown" }));
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

// ===================================================================== Lab: gradient descent
const GD_PRESETS = [["Too small", 0.02], ["Good", 0.3], ["Zig-zag", 0.95], ["Too large", 1.4]];
const lrFromSlider = (v) => 10 ** (-3 + (v / 100) * Math.log10(2500));
const sliderFromLr = (lr) => Math.round(((Math.log10(lr) + 3) / Math.log10(2500)) * 100);

function makeLinePoints(seed) {
  const r = rng(seed);
  const w = r() * 1.6 - 0.8;
  const b = r() * 0.8 - 0.4;
  return Array.from({ length: 12 }, (_, i) => {
    const x = -0.9 + (i / 11) * 1.8 + (r() - 0.5) * 0.1;
    return { x: clamp(x, -0.95, 0.95), y: clamp(w * x + b + (r() - 0.5) * 0.45, -0.95, 0.95) };
  });
}

function gdPane(root) {
  const st = { pts: makeLinePoints(4), start: [-2.5, 2.5], w: -2.5, b: 2.5, lr: 0.3, hist: [], path: [], diverged: false, timer: null, seed: 4 };
  root.innerHTML = `
    <div class="lab-grid halves">
      <div class="panel clay">
        <h3>Data and fitted line</h3>
        <p class="muted mlx-note">Drag points to reshape the data, click empty space to add one, double-click a point to remove it. Dashed lines are the errors that MSE squares.</p>
        <div class="mlx-plot"><svg viewBox="0 0 100 100" class="mlx-svg" id="gdData" role="img" aria-label="Scatter plot with regression line"></svg></div>
      </div>
      <div class="panel clay">
        <h3>Loss surface over (w, b)</h3>
        <p class="muted mlx-note">Darker bands mean higher MSE; the ring marks the minimum. Click anywhere to restart gradient descent from that (w, b).</p>
        <div class="mlx-plot"><canvas width="90" height="90" id="gdCanvas"></canvas><svg viewBox="0 0 100 100" class="mlx-svg" id="gdSurf" role="img" aria-label="Loss surface with descent path"></svg>
          <span class="mlx-axis-l mlx-ax-x">w</span><span class="mlx-axis-l mlx-ax-y">b</span></div>
      </div>
    </div>
    <div class="lab-grid side-left mlx-gap">
      <aside class="panel clay mlx-controls">
        <label>Learning rate <b id="gdLrV"></b><input type="range" id="gdLr" min="0" max="100" aria-label="Learning rate"></label>
        <div class="row">${GD_PRESETS.map(([l, v]) => `<button class="btn small" data-lr="${v}">${l}</button>`).join("")}</div>
        <hr>
        <div class="row"><button class="btn small primary" id="gdPlay">Play</button><button class="btn small" id="gdStep">Step</button><button class="btn small" id="gdStep10">10 steps</button></div>
        <div class="row"><button class="btn small" id="gdReset">Reset weights</button><button class="btn small" id="gdNew">New data</button></div>
        <p class="muted mlx-note">Update rule: <code>w -= lr * dL/dw</code>, <code>b -= lr * dL/db</code> with <code>L = mean((w x + b - y)^2)</code>.</p>
      </aside>
      <div class="lab-main">
        <div class="mlx-stats" id="gdStats"></div>
        <div class="panel clay"><h3>Loss over epochs <span class="muted">(log scale)</span></h3><div id="gdCurve" class="mlx-curve"></div><p class="mlx-msg" id="gdMsg"></p></div>
      </div>
    </div>`;
  const dsvg = $("#gdData", root);
  const ssvg = $("#gdSurf", root);
  const canvas = $("#gdCanvas", root);
  const X = (x) => (x + 1) * 50;
  const Y = (y) => lim((1 - y) * 50);
  const SX = (w) => lim(((w + 4) / 8) * 100);
  const SY = (b) => lim(((4 - b) / 8) * 100);

  const drawSurface = () => {
    const N = canvas.width;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    const vals = new Float64Array(N * N);
    let lo = Infinity;
    let hi = -Infinity;
    for (let j = 0; j < N; j++) {
      for (let i = 0; i < N; i++) {
        const v = Math.log(mse(st.pts, -4 + ((i + 0.5) / N) * 8, 4 - ((j + 0.5) / N) * 8) + 1e-4);
        vals[j * N + i] = v;
        lo = Math.min(lo, v);
        hi = Math.max(hi, v);
      }
    }
    ctx.clearRect(0, 0, N, N);
    ctx.fillStyle = cssVar(root, "--primary", "#8f7dff");
    for (let k = 0; k < vals.length; k++) {
      const band = Math.floor(((vals[k] - lo) / (hi - lo || 1)) * 12) / 12;
      ctx.globalAlpha = 0.03 + band * 0.6;
      ctx.fillRect(k % N, Math.floor(k / N), 1, 1);
    }
    ctx.globalAlpha = 1;
  };
  const resetRun = (w = st.start[0], b = st.start[1]) => {
    st.w = w;
    st.b = b;
    st.hist = [mse(st.pts, w, b)];
    st.path = [[w, b]];
    st.diverged = false;
  };
  const status = () => {
    const h = st.hist;
    const n = h.length;
    const p = st.path;
    if (st.diverged) return ["Diverged", "bad", "The loss blew up: each step overshoots the valley by more than the last. Lower the learning rate below about 1."];
    if (n < 2) return ["Ready", "neutral", "Press Step or Play. Try the presets to compare learning rates."];
    if (h[n - 1] > h[n - 2] * 1.000001) return ["Loss rising", "bad", "The loss went up this step, so the learning rate is too high for this curvature."];
    if (n >= 3 && ((p[n - 1][1] - p[n - 2][1]) * (p[n - 2][1] - p[n - 3][1]) < 0 || (p[n - 1][0] - p[n - 2][0]) * (p[n - 2][0] - p[n - 3][0]) < 0)) return ["Zig-zag", "warn", "The path oscillates across the valley: it still converges, but slowly. A slightly smaller rate would go straighter."];
    if (Math.abs(h[n - 2] - h[n - 1]) < 1e-7) return ["Converged", "ok", "The gradient is close to zero, so the weights stop moving: you are at the bottom of the bowl."];
    if (st.lr < 0.05) return ["Crawling", "warn", "Each step is tiny. It will get there, but needs many more epochs."];
    return ["Descending", "ok", "Each step moves downhill along the negative gradient."];
  };
  const draw = () => {
    const opt = linRegSolve(st.pts);
    const fitOk = Number.isFinite(st.w) && Number.isFinite(st.b);
    dsvg.innerHTML = `<line class="mlx-axis" x1="0" y1="50" x2="100" y2="50"/><line class="mlx-axis" x1="50" y1="0" x2="50" y2="100"/>
      ${fitOk ? st.pts.map((p) => `<line class="mlx-resid" x1="${X(p.x)}" y1="${Y(p.y)}" x2="${X(p.x)}" y2="${Y(st.w * p.x + st.b)}"/>`).join("") : ""}
      <line class="mlx-fit ghost" x1="0" y1="${Y(-opt.w + opt.b)}" x2="100" y2="${Y(opt.w + opt.b)}"/>
      ${fitOk ? `<line class="mlx-fit" x1="0" y1="${Y(-st.w + st.b)}" x2="100" y2="${Y(st.w + st.b)}"/>` : ""}
      ${st.pts.map((p, i) => `<circle class="mlx-pt drag" data-i="${i}" cx="${X(p.x)}" cy="${Y(p.y)}" r="2.6"/>`).join("")}`;
    const path = st.path.slice(-400).filter(([w, b]) => Number.isFinite(w) && Number.isFinite(b));
    ssvg.innerHTML = `<circle class="mlx-opt" cx="${SX(opt.w)}" cy="${SY(opt.b)}" r="3"/>
      ${path.length > 1 ? `<polyline class="mlx-path" points="${path.map(([w, b]) => `${SX(w).toFixed(2)},${SY(b).toFixed(2)}`).join(" ")}"/>` : ""}
      ${path.map(([w, b]) => `<circle class="mlx-dot" cx="${SX(w).toFixed(2)}" cy="${SY(b).toFixed(2)}" r=".8"/>`).join("")}
      ${fitOk ? `<circle class="mlx-cur" cx="${SX(st.w)}" cy="${SY(st.b)}" r="2.2"/>` : ""}`;
    const [label, tone, msg] = status();
    const loss = st.hist.at(-1);
    $("#gdLrV", root).textContent = st.lr.toFixed(st.lr < 0.1 ? 3 : 2);
    $("#gdStats", root).innerHTML = [
      stat("Epoch", String(st.hist.length - 1)),
      stat("w (slope)", fmt(st.w)),
      stat("b (intercept)", fmt(st.b)),
      stat("Loss (MSE)", fmt(loss, 4), st.diverged ? "bad" : "neutral"),
      stat("Best possible", fmt(mse(st.pts, opt.w, opt.b), 4), "ok"),
      stat("Status", label, tone),
    ].join("");
    $("#gdCurve", root).innerHTML = lossCurve(st.hist);
    $("#gdMsg", root).textContent = msg;
  };
  const step = (k = 1) => {
    for (let i = 0; i < k && !st.diverged; i++) {
      const r = linRegStep(st.pts, st.w, st.b, st.lr);
      st.w = r.w;
      st.b = r.b;
      st.hist.push(r.loss);
      st.path.push([r.w, r.b]);
      if (!Number.isFinite(r.loss) || r.loss > 1e8) st.diverged = true;
    }
    if (st.hist.length > 5000) st.hist = st.hist.slice(-5000);
  };
  const pause = () => {
    clearTimeout(st.timer);
    st.timer = null;
    $("#gdPlay", root).textContent = "Play";
  };
  const play = () => {
    if (st.timer) return pause();
    $("#gdPlay", root).textContent = "Pause";
    const slow = reduceMotion();
    const tick = () => {
      step(slow ? 5 : 1);
      draw();
      const [label] = status();
      if (st.diverged || label === "Converged" || st.hist.length > 3000) return pause();
      st.timer = setTimeout(tick, slow ? 400 : 60);
    };
    tick();
  };
  const dataChanged = () => {
    drawSurface();
    resetRun(st.w, st.b);
    if (!Number.isFinite(st.w) || !Number.isFinite(st.b) || st.hist[0] > 1e8) resetRun(...st.start);
    draw();
  };

  let drag = null;
  let moved = false;
  dsvg.addEventListener("pointerdown", (e) => {
    const i = e.target.dataset?.i;
    if (i === undefined) return;
    drag = +i;
    moved = false;
    dsvg.setPointerCapture?.(e.pointerId);
    e.preventDefault();
  });
  dsvg.addEventListener("pointermove", (e) => {
    if (drag === null) return;
    const [vx, vy] = toView(dsvg, e);
    st.pts[drag] = { x: clamp(vx / 50 - 1, -0.98, 0.98), y: clamp(1 - vy / 50, -0.98, 0.98) };
    moved = true;
    dataChanged();
  });
  const endDrag = () => { drag = null; };
  dsvg.addEventListener("pointerup", endDrag);
  dsvg.addEventListener("pointercancel", endDrag);
  dsvg.addEventListener("click", (e) => {
    if (moved || e.target.dataset?.i !== undefined) {
      moved = false;
      return;
    }
    const [vx, vy] = toView(dsvg, e);
    if (st.pts.length >= 60) return toast("That is plenty of points", true);
    st.pts.push({ x: clamp(vx / 50 - 1, -0.98, 0.98), y: clamp(1 - vy / 50, -0.98, 0.98) });
    dataChanged();
  });
  dsvg.addEventListener("dblclick", (e) => {
    const i = e.target.dataset?.i;
    if (i === undefined || st.pts.length <= 2) return;
    st.pts.splice(+i, 1);
    dataChanged();
  });
  ssvg.addEventListener("click", (e) => {
    const [vx, vy] = toView(ssvg, e);
    st.start = [(vx / 100) * 8 - 4, 4 - (vy / 100) * 8];
    pause();
    resetRun();
    draw();
  });
  root.addEventListener("click", (e) => {
    const lr = e.target.closest("[data-lr]")?.dataset.lr;
    if (lr) {
      pause();
      st.lr = +lr;
      $("#gdLr", root).value = sliderFromLr(st.lr);
      resetRun();
      draw();
    }
  });
  $("#gdLr", root).addEventListener("input", (e) => {
    st.lr = lrFromSlider(+e.target.value);
    draw();
  });
  $("#gdPlay", root).onclick = play;
  $("#gdStep", root).onclick = () => { pause(); step(1); draw(); };
  $("#gdStep10", root).onclick = () => { pause(); step(10); draw(); };
  $("#gdReset", root).onclick = () => { pause(); resetRun(); draw(); };
  $("#gdNew", root).onclick = () => {
    pause();
    st.seed += 1;
    st.pts = makeLinePoints(st.seed);
    drawSurface();
    resetRun();
    draw();
  };
  $("#gdLr", root).value = sliderFromLr(st.lr);
  drawSurface();
  resetRun();
  draw();
  return { pause, redraw: () => { drawSurface(); draw(); } };
}

// ===================================================================== Lab: classifier
const DATASETS = [["linear", "Linearly separable"], ["xor", "XOR"], ["circles", "Circles"]];
const clsLr = (v) => 10 ** (-2 + (v / 100) * 2.5);
const clsL2 = (v) => (v <= 0 ? 0 : 10 ** (-4 + (v / 100) * 3));

function clsPane(root) {
  const st = { kind: "xor", noise: 0.05, n: 80, model: "mlp", hidden: 8, lrV: 64, l2V: 0, train: [], test: [], m: null, hist: [], testHist: [], timer: null, addClass: 0, showTest: true, seed: 3, initSeed: 7 };
  root.innerHTML = `
    <div class="lab-grid side-left">
      <aside class="panel clay mlx-controls">
        <span class="mlx-lbl">Dataset</span>
        <div class="row">${DATASETS.map(([k, l]) => `<button class="btn small" data-ds="${k}">${l}</button>`).join("")}<button class="btn small" data-ds="clear">Clear</button></div>
        <label>Label noise <b id="clNoiseV"></b><input type="range" id="clNoise" min="0" max="30" aria-label="Label noise"></label>
        <hr>
        <span class="mlx-lbl">Model</span>
        <div class="tabs" id="clModel"><button data-m="logistic">Logistic regression</button><button data-m="mlp">Tiny MLP</button></div>
        <label>Hidden neurons (tanh) <b id="clHidV"></b><input type="range" id="clHid" min="2" max="16" aria-label="Hidden neurons"></label>
        <label>Learning rate <b id="clLrV"></b><input type="range" id="clLr" min="0" max="100" aria-label="Learning rate"></label>
        <label>L2 regularisation <b id="clL2V"></b><input type="range" id="clL2" min="0" max="100" aria-label="L2 regularisation"></label>
        <hr>
        <div class="row"><button class="btn small primary" id="clPlay">Train</button><button class="btn small" id="clStep">+50 epochs</button><button class="btn small" id="clReset">Reset weights</button></div>
        <span class="mlx-lbl">Click on the plot adds</span>
        <div class="tabs" id="clAdd"><button data-c="0">Class A</button><button data-c="1">Class B</button></div>
        <label class="check"><input type="checkbox" id="clShowTest" checked> Show held-out test points</label>
      </aside>
      <div class="lab-main">
        <div class="panel clay">
          <div class="mlx-plot mlx-plot-cls"><canvas width="56" height="56" id="clCanvas"></canvas><svg viewBox="0 0 100 100" class="mlx-svg" id="clSvg" role="img" aria-label="Classifier decision boundary"></svg></div>
          <p class="muted mlx-note">Background colour = predicted class, brighter = more confident. Filled dots train the model; hollow rings are a held-out test set it never sees. Shift-click adds the other class.</p>
        </div>
        <div class="mlx-stats" id="clStats"></div>
        <div class="panel clay"><h3>Loss <span class="muted">(train solid, test dashed, log scale)</span></h3><div id="clCurve" class="mlx-curve"></div><p class="mlx-msg" id="clMsg"></p></div>
      </div>
    </div>`;
  const canvas = $("#clCanvas", root);
  const svg = $("#clSvg", root);
  const lr = () => clsLr(st.lrV);
  const l2 = () => clsL2(st.l2V);

  const initModel = () => {
    st.m = st.model === "mlp" ? mlpInit(st.hidden, st.initSeed) : logisticInit();
    st.hist = [];
    st.testHist = [];
  };
  const loadData = (kind) => {
    st.kind = kind;
    st.train = kind === "clear" ? [] : makeDataset(kind, st.n, st.seed, st.noise);
    st.test = kind === "clear" ? [] : makeDataset(kind, 200, st.seed + 101, st.noise);
    initModel();
  };
  const drawBoundary = () => {
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    const N = canvas.width;
    const A = cssVar(root, "--sky-ink", "#5aa0ff");
    const B = cssVar(root, "--rose-ink", "#ff6f9a");
    ctx.clearRect(0, 0, N, N);
    for (let j = 0; j < N; j++) {
      for (let i = 0; i < N; i++) {
        const p = predict(st.m, -1 + ((i + 0.5) / N) * 2, 1 - ((j + 0.5) / N) * 2);
        ctx.fillStyle = p >= 0.5 ? B : A;
        ctx.globalAlpha = 0.07 + Math.abs(p - 0.5) * 2 * 0.5;
        ctx.fillRect(i, j, 1, 1);
      }
    }
    ctx.globalAlpha = 1;
  };
  const draw = () => {
    drawBoundary();
    const pt = (d, cls) => `<circle class="mlx-pt ${d.c ? "b" : "a"} ${cls}" cx="${((d.x + 1) * 50).toFixed(2)}" cy="${((1 - d.y) * 50).toFixed(2)}" r="${cls === "test" ? 1.5 : 2}"/>`;
    svg.innerHTML = `${st.showTest ? st.test.map((d) => pt(d, "test")).join("") : ""}${st.train.map((d) => pt(d, "")).join("")}`;
    const trAcc = accuracy(st.m, st.train);
    const teAcc = accuracy(st.m, st.test);
    const loss = st.hist.at(-1) ?? dataLoss(st.m, st.train);
    const epochs = st.hist.length;
    const gap = trAcc - teAcc;
    let verdict = ["Untrained", "neutral", "Press Train. Try logistic regression on XOR first, then switch to the MLP."];
    if (!st.train.length) verdict = ["No data", "neutral", "Click on the plot to add points, or pick a dataset."];
    else if (epochs > 0) {
      if (st.model === "logistic" && st.kind !== "linear" && trAcc < 0.85 && epochs > 150) verdict = ["Underfitting", "bad", "Logistic regression can only draw a straight line, which cannot separate this data. Switch to the MLP."];
      else if (st.test.length && gap > 0.08 && epochs > 800) verdict = ["Overfitting", "warn", `Train accuracy beats test by ${Math.round(gap * 100)} points: the boundary is bending around noisy points. Raise L2 or use fewer neurons.`];
      else if (trAcc < 0.75 && epochs > 600) verdict = ["Underfitting", "warn", "Still poor on the training data: add neurons, raise the learning rate or lower L2."];
      else if (trAcc >= 0.97 && (!st.test.length || teAcc >= 0.9)) verdict = ["Fits well", "ok", "High accuracy on both sets. Now raise the label noise and watch whether it starts memorising."];
      else verdict = ["Learning", "ok", "The boundary moves to reduce cross-entropy on the training points."];
    }
    $("#clStats", root).innerHTML = [
      stat("Epochs", String(epochs)),
      stat("Train loss", fmt(loss, 3)),
      stat("Train accuracy", pct(trAcc), trAcc >= 0.9 ? "ok" : "neutral"),
      stat("Test accuracy", st.test.length ? pct(teAcc) : "n/a", st.test.length && teAcc >= 0.9 ? "ok" : "neutral"),
      stat("Parameters", String(st.model === "mlp" ? st.hidden * 4 + 1 : 3)),
      stat("Verdict", verdict[0], verdict[1]),
    ].join("");
    $("#clCurve", root).innerHTML = lossCurve(st.hist, st.test.length ? st.testHist : null);
    $("#clMsg", root).textContent = verdict[2];
    $("#clNoiseV", root).textContent = `${Math.round(st.noise * 100)}%`;
    $("#clHidV", root).textContent = st.model === "mlp" ? st.hidden : "n/a";
    $("#clHid", root).disabled = st.model !== "mlp";
    $("#clLrV", root).textContent = lr().toFixed(lr() < 0.1 ? 3 : 2);
    $("#clL2V", root).textContent = l2() ? l2().toExponential(1) : "0";
    $$("#clModel button", root).forEach((b) => b.classList.toggle("active", b.dataset.m === st.model));
    $$("#clAdd button", root).forEach((b) => b.classList.toggle("active", +b.dataset.c === st.addClass));
    $$("[data-ds]", root).forEach((b) => b.classList.toggle("active", b.dataset.ds === st.kind));
  };
  const step = (k) => {
    if (!st.train.length) return;
    for (let i = 0; i < k; i++) {
      const r = trainStep(st.m, st.train, lr(), l2());
      st.m = r.model;
      st.hist.push(r.loss);
      if (st.test.length) st.testHist.push(dataLoss(st.m, st.test));
    }
  };
  const pause = () => {
    clearTimeout(st.timer);
    st.timer = null;
    $("#clPlay", root).textContent = "Train";
  };
  const play = () => {
    if (st.timer) return pause();
    if (!st.train.length) return toast("Add some points first", true);
    $("#clPlay", root).textContent = "Pause";
    const slow = reduceMotion();
    const tick = () => {
      step(slow ? 60 : 5);
      draw();
      if (st.hist.length >= 20000) return pause();
      st.timer = setTimeout(tick, slow ? 450 : 30);
    };
    tick();
  };
  root.addEventListener("click", (e) => {
    const ds = e.target.closest("[data-ds]")?.dataset.ds;
    if (ds) {
      pause();
      loadData(ds);
      draw();
      return;
    }
    const m = e.target.closest("#clModel [data-m]")?.dataset.m;
    if (m) {
      pause();
      st.model = m;
      initModel();
      draw();
      return;
    }
    const c = e.target.closest("#clAdd [data-c]")?.dataset.c;
    if (c !== undefined) {
      st.addClass = +c;
      draw();
    }
  });
  svg.addEventListener("click", (e) => {
    const [vx, vy] = toView(svg, e);
    if (st.train.length >= 300) return toast("Training set is full", true);
    st.train.push({ x: clamp(vx / 50 - 1, -0.98, 0.98), y: clamp(1 - vy / 50, -0.98, 0.98), c: e.shiftKey ? 1 - st.addClass : st.addClass });
    if (!st.timer) draw();
  });
  root.addEventListener("input", (e) => {
    const id = e.target.id;
    if (id === "clNoise") {
      st.noise = +e.target.value / 100;
      if (st.kind !== "clear") {
        pause();
        loadData(st.kind);
      }
    } else if (id === "clHid") {
      pause();
      st.hidden = +e.target.value;
      initModel();
    } else if (id === "clLr") st.lrV = +e.target.value;
    else if (id === "clL2") st.l2V = +e.target.value;
    else if (id === "clShowTest") st.showTest = e.target.checked;
    else return;
    if (!st.timer) draw();
  });
  $("#clPlay", root).onclick = play;
  $("#clStep", root).onclick = () => { step(50); draw(); };
  $("#clReset", root).onclick = () => { pause(); st.initSeed += 1; initModel(); draw(); };
  $("#clNoise", root).value = st.noise * 100;
  $("#clHid", root).value = st.hidden;
  $("#clLr", root).value = st.lrV;
  $("#clL2", root).value = st.l2V;
  loadData(st.kind);
  draw();
  return { pause, redraw: draw };
}

// ===================================================================== Lab: attention + tokenizer
const TINTS = ["sky", "mint", "lemon", "lilac", "peach", "rose"];

function attnPane(root) {
  const st = { text: "The cat sat on the mat because it was tired", causal: false, scale: true, temp: 1, row: 6, tokText: "Tokenizers split unbelievably long words into reusable pieces, so 2026 costs 2 tokens." };
  root.innerHTML = `
    <div class="lab-grid side-left">
      <aside class="panel clay mlx-controls">
        <label>Sentence<input type="text" id="atText" maxlength="120" aria-label="Sentence"></label>
        <label class="check"><input type="checkbox" id="atCausal"> Causal mask (GPT-style: no peeking ahead)</label>
        <label class="check"><input type="checkbox" id="atScale" checked> Divide scores by sqrt(d)</label>
        <label>Softmax temperature <b id="atTempV"></b><input type="range" id="atTemp" min="10" max="300" aria-label="Softmax temperature"></label>
        <hr>
        <ol class="mlx-explain">
          <li><b>Embed.</b> Each token becomes a vector of ${D} numbers (toy: a hash plus a hand-picked concept direction, plus position).</li>
          <li><b>Q, K, V.</b> Three weight matrices project it into a <i>query</i> (what am I looking for), a <i>key</i> (what do I contain) and a <i>value</i> (what I pass on).</li>
          <li><b>Score.</b> score(i, j) = q<sub>i</sub> . k<sub>j</sub> / sqrt(d). The scaling stops large dot products from saturating softmax.</li>
          <li><b>Softmax.</b> exp(score - max) per row, then divide by the row sum: positive weights that add up to 1.</li>
          <li><b>Mix.</b> Output<sub>i</sub> = sum over j of weight(i, j) x v<sub>j</sub>: a context-aware version of token i.</li>
        </ol>
      </aside>
      <div class="lab-main">
        <div class="panel clay">
          <h3>Attention weights</h3>
          <p class="muted mlx-note">Rows are queries (the token doing the looking), columns are keys (the token being looked at). Every row sums to 1; colour is relative to the row's strongest weight. Click a row to inspect it.</p>
          <div class="mlx-heatwrap"><div class="mlx-heat" id="atHeat"></div></div>
        </div>
        <div class="panel clay" id="atDetail"></div>
      </div>
    </div>
    <div class="panel clay mlx-gap">
      <h3>Tokenizer</h3>
      <p class="muted mlx-note">Models read tokens, not words. This toy WordPiece-style splitter keeps common words whole, splits long words into a stem and affixes (continuations shown with ##), and cuts numbers into 3-digit chunks. Real BPE vocabularies average about 4 English characters per token.</p>
      <textarea id="tkText" class="code code-editor short" rows="3" spellcheck="false" aria-label="Text to tokenize"></textarea>
      <div class="mlx-stats" id="tkStats"></div>
      <div class="mlx-toks" id="tkOut"></div>
    </div>`;
  const drawAttn = () => {
    const all = tokenize(st.text).map((t) => t.text);
    const toks = all.slice(0, 14);
    if (!toks.length) {
      $("#atHeat", root).innerHTML = `<p class="muted">Type a sentence.</p>`;
      $("#atDetail", root).innerHTML = "";
      return;
    }
    st.row = Math.min(st.row, toks.length - 1);
    const A = attentionScores(toks, { causal: st.causal, scale: st.scale, temperature: st.temp });
    const n = toks.length;
    const big = n <= 10;
    $("#atHeat", root).style.setProperty("--n", n);
    $("#atHeat", root).innerHTML = `<span class="mlx-hcorner muted">query / key</span>${toks.map((t) => `<span class="mlx-hcol">${esc(t)}</span>`).join("")}
      ${A.weights.map((row, i) => {
        const top = Math.max(...row);
        return `<button class="mlx-hrow ${i === st.row ? "on" : ""}" data-row="${i}">${esc(toks[i])}</button>${row.map((w, j) => `<span class="mlx-hcell ${i === st.row ? "on" : ""} ${A.scores[i][j] === -Infinity ? "masked" : ""}" style="--w:${(0.85 * (w / top) ** 1.5).toFixed(3)}" title="${esc(toks[i])} -> ${esc(toks[j])}: ${w.toFixed(3)}">${big ? w.toFixed(2).replace(/^0/, "") : ""}</span>`).join("")}`;
      }).join("")}`;
    const i = st.row;
    const order = A.weights[i].map((w, j) => [w, j]).sort((a, b) => b[0] - a[0]);
    const maxAbs = Math.max(...A.out[i].map(Math.abs), 1e-9);
    $("#atDetail", root).innerHTML = `
      <h3>Query "${esc(toks[i])}"</h3>
      ${all.length > 14 ? `<p class="muted mlx-note">Showing the first 14 of ${all.length} tokens.</p>` : ""}
      <div class="res-table mlx-attn-table"><table><thead><tr><th>Key</th><th>q . k / ${st.scale ? `sqrt(${D})` : "1"}</th><th>softmax weight</th></tr></thead><tbody>
        ${A.scores[i].map((s, j) => `<tr><td>${esc(toks[j])}</td><td class="num">${s === -Infinity ? "masked (-inf)" : s.toFixed(3)}</td><td><span class="mlx-bar"><i style="width:${(A.weights[i][j] * 100).toFixed(1)}%"></i></span> ${A.weights[i][j].toFixed(3)}</td></tr>`).join("")}
      </tbody></table></div>
      <p class="mlx-msg">"${esc(toks[i])}" attends most to "${esc(toks[order[0][1]])}" (${order[0][0].toFixed(2)})${order[1] ? ` and "${esc(toks[order[1][1]])}" (${order[1][0].toFixed(2)})` : ""}. Weights sum to ${A.weights[i].reduce((a, b) => a + b, 0).toFixed(3)}.</p>
      <span class="mlx-lbl">Output vector = weighted sum of V rows (${D} dims)</span>
      <div class="mlx-vec">${A.out[i].map((v) => `<span class="${v < 0 ? "neg" : ""}" style="--h:${((Math.abs(v) / maxAbs) * 100).toFixed(0)}%" title="${v.toFixed(3)}"></span>`).join("")}</div>`;
    $("#atTempV", root).textContent = st.temp.toFixed(2);
  };
  const drawTok = () => {
    const toks = tokenize(st.tokText);
    const chars = st.tokText.length;
    const words = (st.tokText.match(/\S+/g) || []).length;
    $("#tkStats", root).innerHTML = [
      stat("Characters", String(chars)),
      stat("Words", String(words)),
      stat("Tokens (toy)", String(toks.length), "ok"),
      stat("Chars per token", toks.length ? (chars / toks.length).toFixed(2) : "0"),
      stat("Real BPE estimate", `~${Math.ceil(chars / 4)} tokens`),
    ].join("");
    let w = -1;
    $("#tkOut", root).innerHTML = toks.map((t) => {
      if (!t.cont) w++;
      return `<span class="mlx-tok tint-${TINTS[w % TINTS.length]}${t.cont ? " cont" : ""}" title="token id ${t.id}">${t.cont ? "<i>##</i>" : ""}${esc(t.text)}</span>`;
    }).join("") || `<span class="muted">Nothing to tokenize.</span>`;
  };
  $("#atText", root).value = st.text;
  $("#atTemp", root).value = st.temp * 100;
  $("#tkText", root).value = st.tokText;
  root.addEventListener("input", (e) => {
    const id = e.target.id;
    if (id === "atText") st.text = e.target.value;
    else if (id === "atCausal") st.causal = e.target.checked;
    else if (id === "atScale") st.scale = e.target.checked;
    else if (id === "atTemp") st.temp = +e.target.value / 100;
    else if (id === "tkText") {
      st.tokText = e.target.value;
      return drawTok();
    } else return;
    drawAttn();
  });
  root.addEventListener("click", (e) => {
    const r = e.target.closest("[data-row]")?.dataset.row;
    if (r === undefined) return;
    st.row = +r;
    drawAttn();
  });
  drawAttn();
  drawTok();
  return { pause() {}, redraw: drawAttn };
}

const LAB_TABS = [["gd", "Gradient descent", gdPane], ["cls", "Classifier", clsPane], ["attn", "Attention", attnPane]];

export function lab(view) {
  const saved = store.get("ml-lab-tab", "gd");
  const current = LAB_TABS.some(([k]) => k === saved) ? saved : "gd";
  view.innerHTML = `
    ${labHero("ML", "sky", "Training Lab", "Watch models learn. Tune a learning rate and see gradient descent converge, zig-zag or diverge; train logistic regression and a tiny neural network live; and look inside self-attention and tokenization. Everything runs in your browser in plain JavaScript.",
      `<div class="tabs" id="mlxLabTabs">${LAB_TABS.map(([k, l]) => `<button data-tab="${k}">${l}</button>`).join("")}</div>`)}
    <div class="mlx">${LAB_TABS.map(([k]) => `<section class="mlx-pane" data-pane="${k}" hidden></section>`).join("")}</div>`;
  const panes = {};
  const show = (k) => {
    Object.values(panes).forEach((p) => p.pause());
    $$("#mlxLabTabs button", view).forEach((b) => b.classList.toggle("active", b.dataset.tab === k));
    $$(".mlx-pane", view).forEach((p) => (p.hidden = p.dataset.pane !== k));
    const el = $(`.mlx-pane[data-pane="${k}"]`, view);
    if (!panes[k]) panes[k] = LAB_TABS.find(([id]) => id === k)[2](el);
    else panes[k].redraw();
    store.set("ml-lab-tab", k);
  };
  $("#mlxLabTabs", view).addEventListener("click", (e) => {
    const k = e.target.closest("[data-tab]")?.dataset.tab;
    if (k) show(k);
  });
  show(current);
  return () => Object.values(panes).forEach((p) => p.pause());
}

// ===================================================================== Playground: Agent Builder
const lines = (...l) => l.join("\n");
const FENCE = "```";

export const TEMPLATES = {
  agents: lines(
    "# AGENTS.md",
    "",
    "## Project overview",
    "Flask + vanilla JavaScript learning app. Python code lives in `app/`, ES modules in `app/static/js/`, tests in `tests/`.",
    "",
    "## Setup",
    `${FENCE}bash`,
    "python -m venv .venv",
    ".venv/bin/pip install -r requirements.txt",
    FENCE,
    "",
    "## Build and run",
    `${FENCE}bash`,
    ".venv/bin/flask --app app run --debug",
    FENCE,
    "",
    "## Test",
    `${FENCE}bash`,
    ".venv/bin/python -m pytest -q",
    FENCE,
    "All tests must pass before you finish a task.",
    "",
    "## Lint",
    `${FENCE}bash`,
    ".venv/bin/ruff check .",
    FENCE,
    "",
    "## Code style",
    "- Python: PEP 8, type hints on public functions, f-strings.",
    "- JavaScript: ES modules, `const` by default, no frameworks or build step.",
    "- Escape user text with `esc()` before inserting HTML.",
    "",
    "## Boundaries",
    "- Never commit secrets; read them from environment variables.",
    "- Do not add or upgrade dependencies without asking first.",
    "- Never edit files in `app/static/vendor/`.",
    "- Ask before deleting files or changing the database schema.",
    "",
  ),
  skill: lines(
    "---",
    "name: release-notes",
    "description: Drafts release notes from merged pull requests and the git log, grouped into features, fixes and breaking changes. Use when the user asks for release notes, a changelog entry or a summary of what shipped since the last tag.",
    "---",
    "",
    "# Release notes",
    "",
    "## Instructions",
    "1. Find the last release tag with `git describe --tags --abbrev=0`.",
    "2. List commits since that tag: `git log <tag>..HEAD --oneline --no-merges`.",
    "3. Group each change under **Features**, **Fixes** or **Breaking changes**.",
    "4. Write one line per change in plain language and include the PR number.",
    "5. Show the draft to the user before writing `CHANGELOG.md`.",
    "",
    "## Additional resources",
    "- Tone and format rules: [reference/style.md](reference/style.md)",
    "- Collect PR titles automatically: run `scripts/collect_prs.py <tag>`",
    "",
    "## Example output",
    `${FENCE}markdown`,
    "## v2.4.0",
    "### Features",
    "- Export reports as CSV (#412)",
    "### Fixes",
    "- Dates near New Year now use the correct ISO week (#418)",
    FENCE,
    "",
  ),
  rule: lines(
    "---",
    "description: Conventions for Flask route handlers in the API package",
    "globs: app/**/*.py",
    "alwaysApply: false",
    "---",
    "",
    "# Flask routes",
    "",
    "- Return JSON with `jsonify` and an explicit status code.",
    "- Validate the request body at the top of the handler; return 400 with an `error` field on bad input.",
    "- Use parameterised queries; never build SQL with f-strings.",
    "",
    `${FENCE}python`,
    "@bp.post(\"/items\")",
    "def create_item():",
    "    data = request.get_json(silent=True) or {}",
    "    if not data.get(\"name\"):",
    "        return jsonify(error=\"name is required\"), 400",
    "    item = repo.create(name=data[\"name\"])",
    "    return jsonify(item), 201",
    FENCE,
    "",
  ),
};

const FAKE_KEY = ["sk", "DEMO", "not", "a", "real", "key"].join("-");
const WEAK = {
  agents: lines(
    "# Notes for the AI",
    "",
    "Please write clean code and follow best practices.",
    "Make sure everything works properly before you finish.",
    "",
    "Run the tests when needed.",
    "",
    `The staging key is ${FAKE_KEY} if you need to call the API.`,
    "",
  ),
  skill: lines(
    "---",
    "name: PDF Helper",
    "---",
    "",
    "I can help with PDFs. Handle forms correctly and extract text etc.",
    "",
  ),
  rule: lines(
    "# Python",
    "",
    "Write good code and handle errors appropriately. Use best practices for everything, keep it clean and readable, test properly, and try to be consistent with the rest of the codebase as needed.",
    "",
  ),
};

const KINDS = {
  agents: { file: "AGENTS.md", lint: lintAgents, hint: "Repo-wide instructions every coding agent reads first." },
  skill: { file: "SKILL.md", lint: lintSkill, hint: "A packaged workflow the agent loads on demand, matched by its description." },
  rule: { file: "my-rule.mdc", lint: lintRule, hint: "A scoped rule (Cursor .mdc) attached by globs, description or always." },
};

function lintHtml(r) {
  return `
    <div class="mlx-score">
      <div class="mlx-ring ${r.score === 100 ? "full" : r.score >= 60 ? "mid" : "low"}" style="--p:${r.score}"><b>${r.score}</b></div>
      <div><h3>Linter</h3><span class="muted">${r.passed} of ${r.total} checks pass</span></div>
    </div>
    <ul class="clean mlx-checks">${r.checks.map((c) => `<li class="${c.ok ? "ok" : "bad"}"><span class="pill ${c.ok ? "ok" : "bad"}">${c.ok ? "pass" : "fix"}</span><div><b>${esc(c.label)}</b>${c.ok || !c.tip ? "" : `<p>${esc(c.tip)}</p>`}</div></li>`).join("")}</ul>
    ${r.warnings.length ? `<div class="mlx-warn"><b>Notes</b><ul>${r.warnings.map((w) => `<li>${esc(w)}</li>`).join("")}</ul></div>` : ""}`;
}

const PHASE = { plan: ["Plan", "neutral"], tool: ["Tool call", "warn"], obs: ["Observation", "neutral"], reflect: ["Reflect", "ok"], done: ["Done", "ok"] };

export function playground(view) {
  const drafts = { agents: store.get("ml-agent-draft:agents", TEMPLATES.agents), skill: store.get("ml-agent-draft:skill", TEMPLATES.skill), rule: store.get("ml-agent-draft:rule", TEMPLATES.rule) };
  const savedTab = store.get("ml-agent-tab", "agents");
  let kind = ["agents", "skill", "rule", "loop"].includes(savedTab) ? savedTab : "agents";
  const sim = { task: AGENT_TASKS[0].id, useMd: true, cursor: 0, steps: [], timer: null };
  view.innerHTML = `
    ${labHero("AGT", "mint", "Agent Builder", "Write the instruction files coding agents read: <b>AGENTS.md</b> for the repo, <b>SKILL.md</b> for on-demand workflows and scoped <b>rule files</b>. A live linter scores each draft, the preview shows how it renders, and the loop simulator shows how your AGENTS.md changes what an agent actually does.",
      `<div class="tabs" id="agTabs"><button data-k="agents">AGENTS.md</button><button data-k="skill">SKILL.md</button><button data-k="rule">Rule file</button><button data-k="loop">Agent loop</button></div>`)}
    <div class="mlx">
      <section class="mlx-pane" id="agEditor">
        <div class="lab-grid halves">
          <div class="panel clay">
            <div class="mlx-edhead"><b class="mlx-file" id="agFile"></b><span class="muted" id="agHint"></span></div>
            <div class="row mlx-toolbar">
              <button class="btn small" id="agTemplate">Starter template</button>
              <button class="btn small" id="agWeak">Load a weak example</button>
              <button class="btn small primary" id="agCopy">Copy</button>
              <button class="btn small" id="agDownload">Download</button>
            </div>
            <textarea id="agText" class="code code-editor mlx-editor" spellcheck="false" rows="24" aria-label="Instruction file editor"></textarea>
            <div class="muted mlx-note" id="agMeta"></div>
          </div>
          <div class="lab-main">
            <div class="panel clay" id="agLint"></div>
            <div class="panel clay"><h3>Preview</h3><div class="mlx-md" id="agPreview"></div></div>
          </div>
        </div>
      </section>
      <section class="mlx-pane" id="agLoop" hidden>
        <div class="lab-grid side-left">
          <aside class="panel clay mlx-controls">
            <span class="mlx-lbl">Task</span>
            <div class="mlx-tasks">${AGENT_TASKS.map((t) => `<button class="btn small" data-task="${t.id}">${esc(t.label)}</button>`).join("")}</div>
            <span class="mlx-lbl">Instructions</span>
            <div class="tabs" id="agUse"><button data-use="1">My AGENTS.md draft</button><button data-use="0">No AGENTS.md</button></div>
            <div class="row"><button class="btn small primary" id="agPlay">Play</button><button class="btn small" id="agStep">Step</button><button class="btn small" id="agAll">Show all</button><button class="btn small" id="agRestart">Restart</button></div>
            <hr>
            <div id="agRead"></div>
          </aside>
          <div class="lab-main">
            <div class="mlx-stats" id="agCompare"></div>
            <div class="panel clay"><h3 id="agGoal"></h3><ol class="clean mlx-steps" id="agSteps"></ol></div>
          </div>
        </div>
      </section>
    </div>`;
  const ta = $("#agText", view);

  const lintNow = () => {
    const k = KINDS[kind];
    const text = ta.value;
    $("#agLint", view).innerHTML = lintHtml(k.lint(text));
    $("#agPreview", view).innerHTML = renderMarkdown(text) || `<p class="muted">Nothing to preview yet.</p>`;
    $("#agMeta", view).textContent = `${text.split("\n").length} lines, ${text.length} characters. Drafts are saved in this browser.`;
  };
  const save = () => {
    drafts[kind] = ta.value;
    store.set(`ml-agent-draft:${kind}`, ta.value);
  };

  const readHtml = () => {
    const I = extractInstructions(drafts.agents);
    const row = (k, v) => `<li><span class="muted">${esc(k)}</span>${v ? `<code>${esc(v)}</code>` : `<em>not found</em>`}</li>`;
    return `<span class="mlx-lbl">What the agent reads from your AGENTS.md</span><ul class="clean mlx-read">
      ${row("Test command", I.test)}${row("Lint command", I.lint)}${row("Install command", I.setup)}${row("Code style", I.style)}
      <li><span class="muted">Boundaries</span>${I.rules.length ? `<ul>${I.rules.map((r) => `<li>${inlineMd(r)}</li>`).join("")}</ul>` : "<em>none</em>"}</li></ul>
      <p class="muted mlx-note">Edit the AGENTS.md tab (for example, delete the Test section or the dependency rule) and replay to see the agent change course.</p>`;
  };
  const simBuild = () => {
    sim.steps = planAgentRun(sim.task, sim.useMd ? drafts.agents : "");
    sim.cursor = Math.min(sim.cursor, sim.steps.length);
  };
  const simDraw = () => {
    const task = AGENT_TASKS.find((t) => t.id === sim.task);
    $("#agGoal", view).textContent = `Goal: ${task.goal}`;
    $$("[data-task]", view).forEach((b) => b.classList.toggle("active", b.dataset.task === sim.task));
    $$("#agUse button", view).forEach((b) => b.classList.toggle("active", b.dataset.use === (sim.useMd ? "1" : "0")));
    $("#agRead", view).innerHTML = readHtml();
    const withMd = planAgentRun(sim.task, drafts.agents);
    const without = planAgentRun(sim.task, "");
    const calls = (s) => s.filter((x) => x.phase === "tool").length;
    const cites = withMd.filter((x) => x.cite).length;
    $("#agCompare", view).innerHTML = [
      stat("Tool calls with your AGENTS.md", String(calls(withMd)), calls(withMd) <= calls(without) ? "ok" : "warn"),
      stat("Tool calls without instructions", String(calls(without)), "neutral"),
      stat("Decisions taken from AGENTS.md", String(cites), cites ? "ok" : "warn"),
      stat("Step", `${sim.cursor} / ${sim.steps.length}`),
    ].join("");
    $("#agSteps", view).innerHTML = sim.steps.slice(0, sim.cursor).map((s, i) => {
      const [label, tone] = PHASE[s.phase];
      return `<li class="mlx-step ${s.phase}${i === sim.cursor - 1 ? " latest" : ""}"><span class="pill ${tone}">${label}</span><div>
        <p>${esc(s.text)}</p>${s.code ? `<pre class="term-out mlx-term">${s.phase === "tool" ? "$ " : ""}${esc(s.code)}</pre>` : ""}
        ${s.cite ? `<p class="mlx-cite">From AGENTS.md: ${inlineMd(s.cite)}</p>` : ""}</div></li>`;
    }).join("") || `<li class="muted">Press Step or Play to run the agent loop.</li>`;
    $("#agPlay", view).textContent = sim.timer ? "Pause" : "Play";
  };
  const simPause = () => {
    clearTimeout(sim.timer);
    sim.timer = null;
    if ($("#agPlay", view)) $("#agPlay", view).textContent = "Play";
  };
  const simPlay = () => {
    if (sim.timer) return simPause();
    if (sim.cursor >= sim.steps.length) sim.cursor = 0;
    const tick = () => {
      sim.cursor++;
      sim.timer = sim.cursor < sim.steps.length ? setTimeout(tick, reduceMotion() ? 1600 : 900) : null;
      simDraw();
    };
    tick();
  };

  const show = (k) => {
    simPause();
    kind = k;
    store.set("ml-agent-tab", k);
    $$("#agTabs button", view).forEach((b) => b.classList.toggle("active", b.dataset.k === k));
    $("#agEditor", view).hidden = k === "loop";
    $("#agLoop", view).hidden = k !== "loop";
    if (k === "loop") {
      simBuild();
      simDraw();
      return;
    }
    $("#agFile", view).textContent = KINDS[k].file;
    $("#agHint", view).textContent = KINDS[k].hint;
    ta.value = drafts[k];
    lintNow();
  };

  $("#agTabs", view).addEventListener("click", (e) => {
    const k = e.target.closest("[data-k]")?.dataset.k;
    if (k) show(k);
  });
  let deb;
  ta.addEventListener("input", () => {
    clearTimeout(deb);
    deb = setTimeout(() => {
      save();
      lintNow();
    }, 200);
  });
  codeEditor(ta, lintNow, 2);
  $("#agTemplate", view).onclick = () => {
    ta.value = TEMPLATES[kind];
    save();
    lintNow();
  };
  $("#agWeak", view).onclick = () => {
    ta.value = WEAK[kind];
    save();
    lintNow();
  };
  $("#agCopy", view).onclick = () => copy(ta.value);
  $("#agDownload", view).onclick = () => download(KINDS[kind].file, ta.value);
  $("#agLoop", view).addEventListener("click", (e) => {
    const t = e.target.closest("[data-task]")?.dataset.task;
    const u = e.target.closest("[data-use]")?.dataset.use;
    if (t || u !== undefined) {
      simPause();
      if (t) sim.task = t;
      if (u !== undefined) sim.useMd = u === "1";
      sim.cursor = 0;
      simBuild();
      simDraw();
    }
  });
  $("#agPlay", view).onclick = simPlay;
  $("#agStep", view).onclick = () => {
    simPause();
    sim.cursor = Math.min(sim.steps.length, sim.cursor + 1);
    simDraw();
  };
  $("#agAll", view).onclick = () => {
    simPause();
    sim.cursor = sim.steps.length;
    simDraw();
  };
  $("#agRestart", view).onclick = () => {
    simPause();
    sim.cursor = 0;
    simDraw();
  };
  show(kind);
  return () => {
    clearTimeout(deb);
    simPause();
  };
}
