import { $, esc, store, toast, copy, highlightCode } from "../util.js";
import { labHero } from "./common.js";

// ===================================================================== shared helpers
export const fmt = (s) => {
  s = Math.max(0, Math.round(s));
  return s < 60 ? `${s}s` : `${Math.floor(s / 60)}m ${String(s % 60).padStart(2, "0")}s`;
};
const clockTxt = (s) => `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(Math.floor(s % 60)).padStart(2, "0")}`;
const round1 = (x) => Math.round(x * 10) / 10;

/** Deterministic PRNG (mulberry32): the same seed always gives the same run. */
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

/** Kahn topological sort over [{id, needs}]. Returns order, ids stuck in cycles, dangling needs and depth per id. */
export function computeDag(nodes) {
  const ids = new Set(nodes.map((n) => n.id));
  const indeg = new Map(nodes.map((n) => [n.id, 0]));
  const out = new Map(nodes.map((n) => [n.id, []]));
  const missing = [];
  for (const n of nodes) {
    for (const d of n.needs) {
      if (!ids.has(d)) { missing.push([n.id, d]); continue; }
      indeg.set(n.id, indeg.get(n.id) + 1);
      out.get(d).push(n.id);
    }
  }
  const queue = nodes.filter((n) => indeg.get(n.id) === 0).map((n) => n.id);
  const order = [];
  while (queue.length) {
    const id = queue.shift();
    order.push(id);
    for (const c of out.get(id)) {
      indeg.set(c, indeg.get(c) - 1);
      if (indeg.get(c) === 0) queue.push(c);
    }
  }
  const done = new Set(order);
  const cyclic = nodes.map((n) => n.id).filter((id) => !done.has(id));
  const byId = new Map(nodes.map((n) => [n.id, n]));
  const level = new Map();
  for (const id of order) level.set(id, Math.max(0, ...byId.get(id).needs.filter((d) => level.has(d)).map((d) => level.get(d) + 1)));
  return { order, cyclic, missing, level };
}

/** Earliest start/finish per node, the longest (critical) path and wall time vs. running everything serially. */
export function criticalPath(nodes) {
  const dag = computeDag(nodes);
  const byId = new Map(nodes.map((n) => [n.id, n]));
  const es = new Map(), ef = new Map(), prev = new Map();
  for (const id of dag.order) {
    const n = byId.get(id);
    let s = 0, p = null;
    for (const d of n.needs) if (ef.has(d) && (p === null || ef.get(d) > s)) { s = ef.get(d); p = d; }
    es.set(id, s);
    ef.set(id, s + n.dur);
    prev.set(id, p);
  }
  let end = null, wall = 0;
  for (const id of dag.order) if (end === null || ef.get(id) > wall) { wall = ef.get(id); end = id; }
  const path = [];
  for (let c = end; c; c = prev.get(c)) path.unshift(c);
  const serial = nodes.filter((n) => es.has(n.id)).reduce((a, n) => a + n.dur, 0);
  return { ...dag, es, ef, path, wall, serial };
}

/** Ancestors (transitive needs) of a node. */
export function ancestors(nodes, id) {
  const byId = new Map(nodes.map((n) => [n.id, n]));
  const seen = new Set();
  const stack = [...(byId.get(id)?.needs || [])];
  while (stack.length) {
    const d = stack.pop();
    if (seen.has(d) || !byId.has(d)) continue;
    seen.add(d);
    stack.push(...byId.get(d).needs);
  }
  return seen;
}

// ===================================================================== pipeline simulator
export const SIM_STAGES = [
  { id: "checkout", label: "Checkout", needs: [] },
  { id: "install", label: "Install deps", needs: ["checkout"] },
  { id: "lint", label: "Lint", needs: ["install"] },
  { id: "unit", label: "Unit tests", needs: ["install"] },
  { id: "build", label: "Build image", needs: ["lint", "unit"] },
  { id: "scan", label: "Scan image", needs: ["build"] },
  { id: "integration", label: "Integration", needs: ["build"] },
  { id: "staging", label: "Deploy staging", needs: ["scan", "integration"] },
  { id: "approval", label: "Approval", needs: ["staging"] },
  { id: "prod", label: "Deploy prod", needs: ["approval"] },
];
export const SIM_DEFAULTS = { seed: 42, cache: true, shards: 2, flaky: 5, breakAt: "none", strategy: "canary", errorRate: 0, threshold: 5, platform: "github-actions" };
export const BASE_ERR = 0.4;
const STRATEGY_LABEL = { rolling: "Rolling update", bluegreen: "Blue-green", canary: "Canary" };

/** Production rollout model. Canary judges the canary pods alone; rolling judges the blended fleet; blue-green judges after a full switch. */
export function deployPlan(strategy, errorRate, threshold) {
  const steps = [];
  let t = 0, rolledBack = false, exposure = 0;
  const live = round1(errorRate + BASE_ERR);
  if (strategy === "canary") {
    for (const share of [5, 25, 50, 100]) {
      t += 15;
      steps.push({ t, share, metric: null, text: `Shift ${share}% of traffic to the canary` });
      t += 60;
      exposure = share;
      if (live > threshold) {
        steps.push({ t, share, metric: live, bad: true, text: `Canary error rate ${live}% > ${threshold}% threshold: abort and roll back` });
        t += 10;
        steps.push({ t, share: 0, metric: BASE_ERR, text: "All traffic back on the stable version" });
        rolledBack = true;
        break;
      }
      steps.push({ t, share, metric: live, text: `Analysis passed at ${share}%: canary ${live}% vs ${threshold}% threshold` });
    }
  } else if (strategy === "bluegreen") {
    t += 50;
    steps.push({ t, share: 0, metric: null, text: "Green environment deployed next to blue (0% traffic)" });
    t += 20;
    if (errorRate >= 20) {
      steps.push({ t, share: 0, metric: live, bad: true, text: "Smoke tests on green failed: switch cancelled, blue keeps serving" });
      rolledBack = true;
    } else {
      steps.push({ t, share: 0, metric: null, text: "Smoke tests on green passed (only a handful of requests)" });
      t += 5;
      steps.push({ t, share: 100, metric: null, text: "Router switched 100% of traffic to green" });
      exposure = 100;
      t += 60;
      if (live > threshold) {
        steps.push({ t, share: 100, metric: live, bad: true, text: `Error rate ${live}% > ${threshold}% threshold: switch back to blue` });
        t += 5;
        steps.push({ t, share: 0, metric: BASE_ERR, text: "Blue is live again in seconds; green kept for debugging" });
        rolledBack = true;
      } else steps.push({ t, share: 100, metric: live, text: `Healthy at ${live}%; blue kept warm for instant rollback` });
    }
  } else {
    for (const share of [25, 50, 75, 100]) {
      t += 45;
      const m = round1((share / 100) * errorRate + BASE_ERR);
      exposure = share;
      if (m > threshold) {
        steps.push({ t, share, metric: m, bad: true, text: `Batch ${share / 25}/4: fleet error rate ${m}% > ${threshold}% threshold: roll back` });
        t += 30 * (share / 25);
        steps.push({ t, share: 0, metric: BASE_ERR, text: "Old pods recreated batch by batch (rollback is another rollout)" });
        rolledBack = true;
        break;
      }
      steps.push({ t, share, metric: m, text: `Batch ${share / 25}/4 replaced: ${share}% new pods, fleet error rate ${m}%` });
    }
  }
  return { strategy, steps, dur: t, rolledBack, exposure };
}

/** Runs the whole pipeline model for one configuration. Pure and deterministic for a given seed. */
export function simulatePipeline(input = {}) {
  const c = { ...SIM_DEFAULTS, ...input };
  const res = new Map();
  const logs = [];
  const notes = [];
  let deploy = null;
  SIM_STAGES.forEach((st, i) => {
    const r = rng((c.seed >>> 0) * 1009 + i * 7919 + 1);
    const deps = st.needs.map((d) => res.get(d));
    const start = Math.max(0, ...deps.map((d) => d.end));
    const blocked = deps.filter((d) => d.status !== "passed");
    if (blocked.length) {
      res.set(st.id, { ...st, start, end: start, dur: 0, status: "skipped", note: `skipped because ${blocked.map((d) => d.label).join(", ")} did not pass` });
      return;
    }
    const log = (off, text, lvl = "") => logs.push({ t: start + off, text: `[${st.label}] ${text}`, lvl });
    let dur = 0, status = "passed", note = "";
    if (st.id === "checkout") {
      dur = 5 + Math.round(r() * 4);
      log(1, c.platform === "jenkins" ? "Jenkins SCM checkout: checkout scm" : "actions/checkout@v4 · fetch-depth: 1");
      log(dur, "HEAD is now at a1b2c3d", "ok");
    } else if (st.id === "install") {
      const jitter = Math.round(r() * 12);
      const full = 110 + jitter, hitDur = 20 + Math.round(jitter / 3);
      const hit = c.cache && r() > 0.12;
      if (hit) {
        dur = hitDur;
        note = `cache hit saved ${full - hitDur} s`;
        log(2, c.platform === "jenkins" ? "Jenkins dependency cache: lockfile key restored" : "actions/cache: key npm-linux-<lockfile hash> restored");
        log(dur, `node_modules restored in ${dur} s`, "ok");
        notes.push(`Dependency cache hit: install took ${fmt(dur)} instead of ${fmt(full)}, saving ${full - hitDur} s.`);
      } else {
        dur = full;
        if (c.cache) {
          note = "cache miss";
          log(2, c.platform === "jenkins" ? "Jenkins dependency cache: no entry for lockfile key" : "actions/cache: no entry for lockfile hash", "warn");
          notes.push(`Cache miss: the lockfile hash changed (seed ${c.seed}), so this run paid the full ${fmt(full)} install and saved a fresh cache for the next run.`);
        } else {
          note = "no cache";
          notes.push(`No dependency cache: every run downloads all packages (${fmt(full)}). A cache keyed on the lockfile hash would cut this to about ${fmt(hitDur)}.`);
        }
        log(3, "npm ci: downloading 1,284 packages");
        log(dur, `added 1284 packages in ${dur}s`, "ok");
      }
    } else if (st.id === "lint") {
      dur = 16 + Math.round(r() * 6);
      if (c.breakAt === "lint") {
        dur = Math.round(dur * 0.7);
        status = "failed";
        note = "1 lint error";
        log(dur, "src/cart.js:12:7  error  'total' is assigned a value but never used  no-unused-vars", "bad");
        notes.push("The lint step failed fast, so nothing was built or deployed. Cheap checks first give the quickest feedback.");
      } else log(dur, "eslint: 0 problems", "ok");
    } else if (st.id === "unit") {
      const work = 240, setup = 14;
      const per = Math.round(work / c.shards);
      let longest = 0, failed = false;
      for (let k = 1; k <= c.shards; k++) {
        let d = setup + per + Math.round(r() * 8);
        if (c.breakAt === "test" && k === 1) {
          d = setup + Math.round(per * 0.6);
          failed = true;
          log(d, `shard 1/${c.shards}: FAIL cart.test.js > applies discount: expected 90, received 100`, "bad");
        } else if (r() < c.flaky / 100) {
          log(d, `shard ${k}/${c.shards}: flaky test checkout.test.js timed out, retrying`, "warn");
          d += per;
          if (r() < c.flaky / 100) {
            failed = true;
            log(d, `shard ${k}/${c.shards}: retry failed again`, "bad");
            notes.push(`Shard ${k} failed twice on a flaky test. Flaky tests erode trust: quarantine and fix them instead of re-running until green.`);
          } else {
            log(d, `shard ${k}/${c.shards}: retry passed`, "ok");
            notes.push(`Shard ${k} hit a flaky test; the automatic retry passed but cost +${per} s.`);
          }
        } else log(d, `shard ${k}/${c.shards}: ${Math.round(412 / c.shards)} tests passed`, "ok");
        longest = Math.max(longest, d);
      }
      dur = longest;
      status = failed ? "failed" : "passed";
      note = `${c.shards} shard${c.shards > 1 ? "s" : ""}`;
      if (c.breakAt === "test") notes.push("A real test failure stopped the pipeline before an image was built: the bug never reached staging.");
      if (c.shards > 1) notes.push(`${c.shards} test shards ran in parallel: about ${fmt(setup + per)} each instead of ${fmt(setup + work)} on one runner.`);
      else notes.push(`One runner ran all ${work} s of tests. Splitting into 4 shards would bring it near ${fmt(setup + work / 4)}.`);
    } else if (st.id === "build") {
      const full = 92 + Math.round(r() * 8);
      dur = c.cache ? 36 + Math.round(r() * 4) : full;
      note = c.cache ? `layer cache saved ${full - dur} s` : "cold build";
      log(4, c.cache ? "docker buildx: CACHED [deps 3/6] RUN npm ci --omit=dev" : "docker buildx: [deps 3/6] RUN npm ci --omit=dev");
      log(dur, "pushed ghcr.io/acme/shop:a1b2c3d (digest sha256:9f3e...)", "ok");
      if (c.cache) notes.push(`Docker layer cache reused the dependency layers: image built in ${fmt(dur)} instead of ${fmt(full)}.`);
    } else if (st.id === "scan") {
      dur = 24 + Math.round(r() * 6);
      if (c.breakAt === "vuln") {
        status = "failed";
        note = "critical CVE";
        log(dur, "CRITICAL lodash 4.17.15: prototype pollution (CVE-2020-8203), fixed in 4.17.19", "bad");
        notes.push("The image scan blocked a known-vulnerable dependency. Upgrading the package (and keeping the lockfile updated by a bot) fixes it; ignoring the gate ships the CVE.");
      } else log(dur, "0 critical, 0 high vulnerabilities", "ok");
    } else if (st.id === "integration") {
      const base = 120 + Math.round(r() * 20);
      dur = base;
      if (r() < c.flaky / 100) {
        log(base, "flaky: payment-sandbox timed out, retrying suite", "warn");
        dur += base;
        if (r() < c.flaky / 100) {
          status = "failed";
          log(dur, "retry failed: payment-sandbox timeout", "bad");
          notes.push("Integration tests failed twice on a flaky dependency. Stub or containerise external services so the suite is deterministic.");
        } else {
          log(dur, "retry passed", "ok");
          notes.push(`The integration suite was retried after a flaky timeout, adding ${fmt(base)}.`);
        }
      } else log(dur, "38 integration tests passed against docker compose services", "ok");
      note = status === "failed" ? "flaky failure" : dur > base ? "retried" : "";
    } else if (st.id === "staging") {
      dur = 38 + Math.round(r() * 10);
      log(dur - 8, "kubectl rollout status deploy/shop -n staging: success");
      log(dur, "smoke test GET /healthz 200", "ok");
    } else if (st.id === "approval") {
      dur = 40 + Math.round(r() * 50);
      log(1, c.platform === "jenkins" ? "input step: waiting for release-manager approval" : "waiting for reviewer (GitHub production environment protection)");
      log(dur, "approved by release-manager", "ok");
    } else if (st.id === "prod") {
      deploy = deployPlan(c.strategy, c.errorRate, c.threshold);
      dur = deploy.dur;
      deploy.steps.forEach((s) => log(s.t, s.text, s.bad ? "bad" : s.share === 100 && s.metric !== null ? "ok" : ""));
      status = deploy.rolledBack ? "failed" : "passed";
      note = deploy.rolledBack ? "rolled back" : STRATEGY_LABEL[c.strategy];
    }
    res.set(st.id, { ...st, start, dur, end: start + dur, status, note });
  });
  const stages = SIM_STAGES.map((s) => res.get(s.id));
  const total = Math.max(...stages.map((s) => s.end));
  const failed = stages.find((s) => s.status === "failed") || null;
  const cp = criticalPath(stages.filter((s) => s.status !== "skipped").map((s) => ({ id: s.id, needs: s.needs.filter((d) => res.get(d).status !== "skipped"), dur: s.dur })));
  const serial = stages.reduce((a, s) => a + s.dur, 0);
  if (serial > total) notes.push(`Parallel jobs (lint beside unit tests, scan beside integration) saved ${fmt(serial - total)} versus running every stage one after another.`);
  if (deploy) notes.push(...deployNotes(c, deploy));
  logs.sort((a, b) => a.t - b.t);
  return { config: c, stages, total, failed, logs, notes, deploy, criticalPath: cp.path };
}

function deployNotes(c, d) {
  const out = [];
  const others = Object.keys(STRATEGY_LABEL).filter((s) => s !== c.strategy).map((s) => [s, deployPlan(s, c.errorRate, c.threshold)]);
  if (d.rolledBack) {
    const exp = d.exposure ? `${d.exposure}% of users` : "no users";
    out.push(`${STRATEGY_LABEL[c.strategy]} detected the ${c.errorRate}% error rate and rolled back automatically; ${exp} saw the bad version before the decision.`);
    const cmp = others.map(([s, p]) => `${STRATEGY_LABEL[s]}: ${p.rolledBack ? `${p.exposure}% exposed before rollback` : "would not have rolled back"}`).join("; ");
    out.push(`For comparison, ${cmp}.`);
    if (c.strategy === "rolling") out.push("Rolling judges the whole fleet, so a bad version is diluted by healthy pods and is caught late. Canary analysis compares the new pods on their own.");
  } else if (c.errorRate > 0) {
    out.push(`The new version shipped with ${c.errorRate}% extra errors because they stayed under the ${c.threshold}% rollback threshold. Tune the threshold to your SLO, or compare canary against baseline rather than a fixed number.`);
  } else out.push(`${STRATEGY_LABEL[c.strategy]} finished cleanly in ${fmt(d.dur)}.`);
  return out;
}

const SIM_PRESETS = {
  happy: { label: "Happy path", cache: true, shards: 4, flaky: 0, breakAt: "none", strategy: "canary", errorRate: 0 },
  cold: { label: "Cold and serial", cache: false, shards: 1, flaky: 0, breakAt: "none", strategy: "rolling", errorRate: 0 },
  flaky: { label: "Flaky suite", cache: true, shards: 2, flaky: 25, breakAt: "none", strategy: "canary", errorRate: 0, seed: 7 },
  badCanary: { label: "Bad release, canary", cache: true, shards: 4, flaky: 0, breakAt: "none", strategy: "canary", errorRate: 12 },
  badRolling: { label: "Bad release, rolling", cache: true, shards: 4, flaky: 0, breakAt: "none", strategy: "rolling", errorRate: 12 },
  vuln: { label: "Vulnerable dependency", cache: true, shards: 2, flaky: 0, breakAt: "vuln", strategy: "bluegreen", errorRate: 0 },
};

const SIM_PLATFORM_SOURCE = {
  "github-actions": {
    title: ".github/workflows/ci.yml · GitHub Actions",
    note: "Workflow → jobs → steps. GitHub-hosted runners execute each job; needs controls job dependencies.",
    lang: "yaml",
    code: `name: ci
on: [push, pull_request]
permissions:
  contents: read
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm run lint
      - run: npm test
  build:
    needs: verify
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker buildx build .
  deploy:
    needs: build
    environment: production
    runs-on: ubuntu-latest
    steps:
      - run: ./scripts/deploy.sh production`,
  },
  jenkins: {
    title: "Jenkinsfile · Declarative Pipeline",
    note: "Jenkinsfile → stages → steps. Agents provide the workspace; parallel branches shorten independent test work.",
    lang: "generic",
    code: `pipeline {
  agent any
  options { timestamps(); disableConcurrentBuilds() }
  stages {
    stage('Checkout') { steps { checkout scm } }
    stage('Verify') {
      parallel {
        stage('Lint') { steps { sh 'npm ci && npm run lint' } }
        stage('Unit tests') { steps { sh 'npm ci && npm test' } }
      }
    }
    stage('Build image') {
      steps { sh 'docker buildx build --push .' }
    }
    stage('Production') {
      input { message 'Approve production?' }
      steps { sh './scripts/deploy.sh production' }
    }
  }
}`,
  },
};

const stageState = (s, now) => {
  if (now < s.start) return "queued";
  if (s.status === "skipped") return "skipped";
  if (now < s.end) return "running";
  return s.status;
};
const STATUS_PILL = { queued: "neutral", running: "warn", passed: "ok", failed: "bad", skipped: "neutral" };

export function lab(view) {
  let c = { ...SIM_DEFAULTS, ...store.get("cicd-sim", {}) };
  if (!["github-actions", "jenkins"].includes(c.platform)) c.platform = "github-actions";
  let timer = null;
  let result = null;
  const reduce = typeof matchMedia === "function" && matchMedia("(prefers-reduced-motion: reduce)").matches;
  const seg = (name, opts) => `<div class="tabs cd-seg" role="group" aria-label="${esc(name)}">${opts.map(([v, l]) => `<button type="button" data-${name}="${esc(v)}">${esc(l)}</button>`).join("")}</div>`;
  view.innerHTML = `
    ${labHero("CI", "sky", "Pipeline Simulator", "Compare GitHub Actions workflows with Jenkins pipelines while running the same CI/CD scenario. Toggle caching, shard tests, inject failures and watch a release get caught (or not). Runs use a seed, so the same settings always replay the same way.")}
    <div class="filters"><b>Platform:</b>${seg("platform", [["github-actions", "GitHub Actions"], ["jenkins", "Jenkins"]])}<span class="muted" id="cdPlatformHint"></span></div>
    <div class="filters"><span class="muted">Scenarios:</span>${Object.entries(SIM_PRESETS).map(([k, p]) => `<button class="btn small" data-preset="${k}">${esc(p.label)}</button>`).join("")}</div>
    <div class="lab-grid side-left">
      <aside class="panel clay cd-controls">
        <h3>Build</h3>
        <label class="check"><input type="checkbox" id="cdCache"> Dependency and layer cache</label>
        <div class="cd-field"><span>Parallel test shards</span>${seg("shards", [["1", "1"], ["2", "2"], ["4", "4"]])}</div>
        <label class="cd-field">Flaky test rate <b id="cdFlakyV"></b><input type="range" id="cdFlaky" min="0" max="40" step="1"></label>
        <label class="cd-field">Break the build
          <select id="cdBreak"><option value="none">Nothing, ship it</option><option value="lint">Lint error</option><option value="test">Failing unit test</option><option value="vuln">Vulnerable dependency</option></select></label>
        <h3>Release</h3>
        <div class="cd-field"><span>Deployment strategy</span>${seg("strategy", [["rolling", "Rolling"], ["bluegreen", "Blue-green"], ["canary", "Canary"]])}</div>
        <label class="cd-field">Error rate of new version <b id="cdErrV"></b><input type="range" id="cdErr" min="0" max="30" step="1"></label>
        <label class="cd-field">Rollback threshold <b id="cdThrV"></b><input type="range" id="cdThr" min="1" max="10" step="1"></label>
        <label class="cd-field">Seed <input type="number" id="cdSeed" min="1" max="99999" step="1"></label>
        <div class="row"><button class="btn primary" id="cdRun">Run pipeline</button><button class="btn small" id="cdSkip">Skip to end</button><button class="btn small" id="cdReseed">New seed</button></div>
      </aside>
      <div class="lab-main cd-main">
        <div class="panel clay">
          <div class="cd-head"><h3>Pipeline <small class="muted" id="cdPlatformLabel"></small></h3><div class="row"><span class="pill neutral" id="cdClock">00:00</span><span class="pill neutral" id="cdVerdict">Ready</span></div></div>
          <div class="cd-pipe" id="cdPipe"></div>
        </div>
        <div class="lab-grid halves">
          <div class="panel clay"><h3>Production rollout</h3><div id="cdDeploy" class="cd-deploy"></div></div>
          <div class="panel clay"><h3>Log</h3><pre class="term-out cd-log" id="cdLog" aria-live="polite"></pre></div>
        </div>
        <div class="panel clay" id="cdExplain"><h3>What happened and why</h3><p class="muted">Press <b>Run pipeline</b> to see timings and explanations.</p></div>
        <div class="panel clay"><div class="cd-head"><h3 id="cdSourceTitle"></h3><span class="pill neutral" id="cdSourceKind"></span></div><p class="muted" id="cdSourceNote"></p><pre class="yaml cd-yaml" id="cdSource"></pre></div>
      </div>
    </div>`;

  const levels = computeDag(SIM_STAGES).level;
  const cols = [];
  SIM_STAGES.forEach((s) => (cols[levels.get(s.id)] ||= []).push(s));

  const sync = () => {
    $("#cdCache", view).checked = c.cache;
    $("#cdFlaky", view).value = c.flaky;
    $("#cdBreak", view).value = c.breakAt;
    $("#cdErr", view).value = c.errorRate;
    $("#cdThr", view).value = c.threshold;
    $("#cdSeed", view).value = c.seed;
    $("#cdFlakyV", view).textContent = `${c.flaky}%`;
    $("#cdErrV", view).textContent = `${c.errorRate}%`;
    $("#cdThrV", view).textContent = `${c.threshold}%`;
    view.querySelectorAll("[data-platform]").forEach((b) => {
      const on = b.dataset.platform === c.platform;
      b.classList.toggle("active", on);
      b.setAttribute("aria-pressed", on);
    });
    const source = SIM_PLATFORM_SOURCE[c.platform];
    $("#cdPlatformLabel", view).textContent = c.platform === "jenkins" ? "· Jenkins stages on agents" : "· GitHub Actions jobs on runners";
    $("#cdPlatformHint", view).textContent = c.platform === "jenkins" ? "Jenkinsfile · agent · stage · input approval" : "workflow YAML · hosted runner · job · environment approval";
    $("#cdSourceTitle", view).textContent = source.title;
    $("#cdSourceKind", view).textContent = c.platform === "jenkins" ? "Declarative Pipeline" : "Workflow YAML";
    $("#cdSourceNote", view).textContent = source.note;
    $("#cdSource", view).innerHTML = highlightCode(source.code, source.lang);
    view.querySelectorAll("[data-shards]").forEach((b) => { const on = +b.dataset.shards === c.shards; b.classList.toggle("active", on); b.setAttribute("aria-pressed", on); });
    view.querySelectorAll("[data-strategy]").forEach((b) => { const on = b.dataset.strategy === c.strategy; b.classList.toggle("active", on); b.setAttribute("aria-pressed", on); });
  };
  const save = () => store.set("cicd-sim", c);

  const paintPipe = (now) => {
    $("#cdPipe", view).innerHTML = cols.map((col, i) => `
      <div class="cd-col">${col.map((s) => {
        const r = result?.stages.find((x) => x.id === s.id);
        const st = r ? stageState(r, now) : "queued";
        const pct = r && st === "running" ? Math.min(100, ((now - r.start) / Math.max(r.dur, 1)) * 100) : st === "passed" || st === "failed" ? 100 : 0;
        const crit = r && result.criticalPath.includes(s.id) && (st === "passed" || st === "failed");
        const label = st === "failed" && s.id === "prod" ? "rolled back" : st;
        return `<div class="cd-stage is-${st}${crit ? " is-crit" : ""}">
          <div class="cd-stage-top"><b>${esc(s.label)}</b><span class="pill ${STATUS_PILL[st]}">${esc(label)}</span></div>
          <div class="cd-bar"><i style="width:${pct}%"></i></div>
          <div class="cd-stage-meta muted">${r && (st === "passed" || st === "failed") ? `${fmt(r.dur)}${r.note ? ` · ${esc(r.note)}` : ""}` : st === "running" ? `${fmt(now - r.start)}…` : st === "skipped" ? "skipped" : "waiting"}</div>
        </div>`;
      }).join("")}</div>${i < cols.length - 1 ? `<div class="cd-arrow" aria-hidden="true"></div>` : ""}`).join("");
  };

  const paintDeploy = (now) => {
    const prod = result?.stages.find((s) => s.id === "prod");
    const d = result?.deploy;
    if (!d || !prod || now < prod.start) {
      $("#cdDeploy", view).innerHTML = `<p class="muted">${result && prod?.status === "skipped" && now >= prod.start ? "Production deploy skipped: an earlier stage did not pass." : `Waiting for the pipeline to reach production. Strategy: <b>${esc(STRATEGY_LABEL[c.strategy])}</b>, threshold ${c.threshold}%.`}</p>`;
      return;
    }
    const rel = now - prod.start;
    const seen = d.steps.filter((s) => s.t <= rel);
    const last = seen.at(-1);
    const share = last ? last.share : 0;
    const metrics = seen.filter((s) => s.metric !== null);
    const lastM = metrics.at(-1)?.metric ?? BASE_ERR;
    const maxM = Math.max(c.threshold * 1.6, ...d.steps.map((s) => s.metric ?? 0), 1);
    $("#cdDeploy", view).innerHTML = `
      <div class="cd-traffic" role="img" aria-label="${share}% of traffic on the new version">
        <div class="cd-old" style="flex:${100 - share}"><span>stable ${100 - share}%</span></div>
        <div class="cd-new${last?.bad ? " bad" : ""}" style="flex:${share}"><span>${share ? `new ${share}%` : ""}</span></div>
      </div>
      <div class="cd-meter"><span class="muted">${d.strategy === "rolling" ? "Fleet" : "New version"} error rate</span>
        <div class="cd-gauge"><i class="${lastM > c.threshold ? "over" : ""}" style="width:${Math.min(100, (lastM / maxM) * 100)}%"></i><em style="left:${(c.threshold / maxM) * 100}%" title="threshold"></em></div>
        <b class="pill ${lastM > c.threshold ? "bad" : "ok"}">${lastM}% / ${c.threshold}%</b></div>
      <ol class="clean cd-steps">${seen.map((s) => `<li class="${s.bad ? "bad" : ""}"><span class="muted">+${fmt(s.t)}</span> ${esc(s.text)}</li>`).join("")}</ol>`;
  };

  let logCount = -1;
  const paintLog = (now) => {
    const lines = result ? result.logs.filter((l) => l.t <= now) : [];
    if (lines.length === logCount) return;
    logCount = lines.length;
    const el = $("#cdLog", view);
    const platformPrefix = c.platform === "jenkins" ? "Jenkins agent" : "GitHub Actions runner";
    el.innerHTML = lines.length ? lines.map((l) => `<span class="cd-l ${l.lvl}">[${clockTxt(l.t)}] ${esc(l.text)}</span>`).join("\n") : `$ ${platformPrefix}: waiting for a run`;
    el.scrollTop = el.scrollHeight;
  };

  const paintExplain = () => {
    const r = result;
    const ok = !r.failed;
    const total = `<span class="pill ${ok ? "ok" : "bad"}">${ok ? "Deployed" : r.failed.id === "prod" ? "Rolled back" : `Failed at ${esc(r.failed.label)}`}</span>`;
    $("#cdExplain", view).innerHTML = `<h3>What happened and why</h3>
      <div class="row cd-sum">${total}<span class="pill neutral">Wall time ${fmt(r.total)}</span><span class="pill neutral">Seed ${r.config.seed}</span></div>
      <p class="muted cd-crit">Critical path: ${r.criticalPath.map((id) => esc(SIM_STAGES.find((s) => s.id === id).label)).join(" &rarr; ")}. Speeding up anything off this path does not shorten the run.</p>
      <ul class="clean tips">${r.notes.map((n) => `<li>${esc(n)}</li>`).join("")}</ul>`;
  };

  const paint = (now, done) => {
    $("#cdClock", view).textContent = clockTxt(now);
    paintPipe(now);
    paintDeploy(now);
    paintLog(now);
    const v = $("#cdVerdict", view);
    if (!result) { v.textContent = "Ready"; v.className = "pill neutral"; return; }
    if (done) {
      v.textContent = result.failed ? (result.failed.id === "prod" ? "Rolled back" : "Failed") : "Deployed";
      v.className = `pill ${result.failed ? "bad" : "ok"}`;
      paintExplain();
    } else { v.textContent = "Running"; v.className = "pill warn"; }
  };

  const stop = () => { if (timer) clearInterval(timer); timer = null; };
  const run = () => {
    stop();
    result = simulatePipeline(c);
    logCount = -1;
    $("#cdExplain", view).innerHTML = `<h3>What happened and why</h3><p class="muted">Running…</p>`;
    const total = Math.max(result.total, 1);
    const ms = reduce ? 0 : Math.min(9000, Math.max(4500, total * 8));
    if (!ms) return paint(total, true);
    const t0 = Date.now();
    timer = setInterval(() => {
      const k = Math.min(1, (Date.now() - t0) / ms);
      paint(k * total, k >= 1);
      if (k >= 1) stop();
    }, 60);
  };
  const reset = () => { stop(); result = null; logCount = -1; paint(0, false); $("#cdExplain", view).innerHTML = `<h3>What happened and why</h3><p class="muted">Settings changed. Press <b>Run pipeline</b> to replay with seed ${c.seed}.</p>`; };

  view.addEventListener("input", (e) => {
    const id = e.target.id;
    const v = +e.target.value;
    if (id === "cdFlaky") c.flaky = v;
    else if (id === "cdErr") c.errorRate = v;
    else if (id === "cdThr") c.threshold = v;
    else if (id === "cdSeed") { if (!Number.isInteger(v) || v < 1) return; c.seed = Math.min(99999, v); }
    else return;
    sync(); save(); reset();
  });
  view.addEventListener("change", (e) => {
    if (e.target.id === "cdCache") c.cache = e.target.checked;
    else if (e.target.id === "cdBreak") c.breakAt = ["none", "lint", "test", "vuln"].includes(e.target.value) ? e.target.value : "none";
    else return;
    save(); reset();
  });
  view.addEventListener("click", (e) => {
    const b = e.target.closest("button");
    if (!b || !view.contains(b)) return;
    if (["github-actions", "jenkins"].includes(b.dataset.platform)) { c.platform = b.dataset.platform; sync(); save(); reset(); }
    else if (b.dataset.shards) { c.shards = +b.dataset.shards; sync(); save(); reset(); }
    else if (b.dataset.strategy) { c.strategy = b.dataset.strategy; sync(); save(); reset(); }
    else if (b.dataset.preset) { const { label, ...p } = SIM_PRESETS[b.dataset.preset]; c = { ...SIM_DEFAULTS, platform: c.platform, threshold: c.threshold, ...p }; sync(); save(); run(); }
    else if (b.id === "cdRun") run();
    else if (b.id === "cdSkip") { if (!result) result = simulatePipeline(c); stop(); logCount = -1; paint(result.total, true); }
    else if (b.id === "cdReseed") { c.seed = 1 + Math.floor(Math.random() * 99998); sync(); save(); run(); }
  });
  sync();
  paint(0, false);
  return stop;
}

// ===================================================================== pipeline builder
export const JOB_KINDS = Object.freeze({
  lint: { label: "Lint", dur: 40, deps: true, run: "npm run lint" },
  typecheck: { label: "Type check", dur: 60, deps: true, run: "npm run typecheck" },
  unit: { label: "Unit tests", dur: 300, deps: true, matrix: true, test: true, run: "npm test" },
  integration: { label: "Integration tests", dur: 240, deps: true, matrix: true, test: true, run: "npm run test:integration" },
  build: { label: "Build image", dur: 180, image: true },
  scan: { label: "Security scan", dur: 60, deps: true, run: "npm audit --audit-level=high" },
  "deploy-staging": { label: "Deploy staging", dur: 90, deploy: "staging" },
  "deploy-prod": { label: "Deploy production", dur: 90, deploy: "production" },
});
const kindOf = (k) => (Object.hasOwn(JOB_KINDS, k) ? JOB_KINDS[k] : null);
export const SETUP_S = 10, INSTALL_S = 110, INSTALL_CACHED_S = 20, IMAGE_CACHED_S = 70;
const MATRIX_SIZES = [1, 2, 4, 8];
export const isCacheable = (kind) => !!(kindOf(kind)?.deps || kindOf(kind)?.image);

/** Wall time of one job (one matrix leg) and runner time billed across all legs. */
export function jobDuration(job) {
  const k = kindOf(job.kind);
  if (!k) return { dur: 0, billed: 0 };
  const m = k.matrix ? job.matrix : 1;
  let d = SETUP_S;
  if (k.deps) d += job.cache ? INSTALL_CACHED_S : INSTALL_S;
  d += k.image ? (job.cache ? IMAGE_CACHED_S : k.dur) : Math.round(k.dur / m);
  return { dur: d, billed: d * m };
}

export const jobNodes = (p) => p.jobs.map((j) => ({ id: j.id, needs: j.needs, kind: j.kind, ...jobDuration(j) }));

export function analyzePipeline(p) {
  const nodes = jobNodes(p);
  const cp = criticalPath(nodes);
  return { nodes, ...cp, billed: nodes.reduce((a, n) => a + n.billed, 0) };
}

/** Problems a reviewer would flag. Each: {level: error|warn|info, msg, fix, job?}. */
export function lintPipeline(p, platform = p.platform || "github-actions") {
  const out = [];
  const add = (level, msg, fix, job) => out.push({ level, msg, fix, job });
  const nodes = jobNodes(p);
  if (!nodes.length) { add("info", "The pipeline is empty.", "Add jobs from the palette, starting with lint and tests."); return out; }
  const dag = computeDag(nodes);
  dag.cyclic.forEach((id) => add("error", `Job "${id}" is part of a dependency cycle, so it can never start.`, "Remove one of the needs that points back up the chain.", id));
  dag.missing.forEach(([id, d]) => add("error", `Job "${id}" needs "${d}", which does not exist.`, "Remove the dangling dependency.", id));
  const deploys = p.jobs.filter((j) => kindOf(j.kind)?.deploy);
  for (const j of deploys) {
    const anc = ancestors(nodes, j.id);
    const kinds = new Set(p.jobs.filter((x) => anc.has(x.id)).map((x) => x.kind));
    if (![...kinds].some((k) => kindOf(k)?.test)) add("error", `"${j.id}" can deploy before any tests have passed.`, `Add a test job to ${j.id}'s needs (directly or through build).`, j.id);
    if (!kinds.has("build")) add("warn", `"${j.id}" does not wait for an image build, so it may deploy an old or missing artifact.`, "Make the deploy need the build job and deploy the image by commit SHA.", j.id);
    if (j.kind === "deploy-prod" && !kinds.has("deploy-staging")) add("warn", "Production deploys without going through staging first.", "Make deploy-prod need deploy-staging so every release is verified in staging.", j.id);
  }
  if (deploys.length && !p.jobs.some((j) => j.kind === "scan")) add("info", "Nothing scans dependencies or the image before deploying.", "Add a security scan job and make deploys need it.");
  if (platform === "github-actions" && !p.perms) add("error", "No permissions block: GITHUB_TOKEN may inherit broad repository permissions.", "Set workflow permissions to contents: read and grant extra scopes per job.");
  if (deploys.length && !p.concurrency) add("warn", platform === "jenkins" ? "Concurrent Jenkins builds can race while deploying the same environment." : "No concurrency group: two pushes can deploy at the same time and race.", platform === "jenkins" ? "Use disableConcurrentBuilds() or serialize deployments by environment." : "Add concurrency with a group per branch.");
  if (deploys.length && !p.oidc) add("warn", platform === "jenkins" ? "Jenkins deploys need cloud credentials; stored long-lived keys increase leak risk." : "Cloud access uses long-lived access keys stored as secrets.", platform === "jenkins" ? "Prefer an OIDC/workload-identity credential provider on the Jenkins agent; otherwise scope and rotate credentials stored in Jenkins Credentials." : "Use OIDC (id-token: write) to assume a cloud role and get short-lived credentials.");
  if (p.printSecret) add("error", "A step echoes a secret. Masking only hides exact matches; encoded or partial values leak into logs.", "Never print secrets. Pass them through env to the tool that needs them.");
  p.jobs.filter((j) => isCacheable(j.kind) && !j.cache).forEach((j) => add("warn", `"${j.id}" has no cache, so every run pays ${kindOf(j.kind).image ? fmt(kindOf(j.kind).dur - IMAGE_CACHED_S) : fmt(INSTALL_S - INSTALL_CACHED_S)} of extra work.`, kindOf(j.kind).image ? (platform === "jenkins" ? "Configure a registry-backed BuildKit cache on the Jenkins agent." : "Use the BuildKit GitHub Actions cache (cache-from/cache-to type=gha).") : (platform === "jenkins" ? "Enable a lockfile-keyed dependency cache on the Jenkins agent." : "Enable the package manager cache keyed on the lockfile."), j.id));
  if (platform === "github-actions" && p.refs === "main") add("error", "Actions are referenced by branch (@main): any upstream push changes the code you run.", "Pin actions to a full commit SHA (keep the tag in a comment).");
  else if (platform === "github-actions" && p.refs === "tag") add("info", "Actions are pinned to tags, which their owners can move.", "Pin third-party actions to a full commit SHA for supply-chain safety.");
  return out;
}

const GH = (expr) => "${{ " + expr + " }}";
const ACTIONS = { checkout: ["actions/checkout", "v4"], node: ["actions/setup-node", "v4"], buildx: ["docker/setup-buildx-action", "v3"], login: ["docker/login-action", "v3"], push: ["docker/build-push-action", "v6"], aws: ["aws-actions/configure-aws-credentials", "v4"] };
const uses = (key, refs) => {
  const [name, tag] = ACTIONS[key];
  return refs === "main" ? `${name}@main` : refs === "sha" ? `${name}@<full-commit-sha> # ${tag}` : `${name}@${tag}`;
};

const BUILDER_PLUGINS = {
  "github-actions": [
    { id: "upload-artifact", label: "Upload build artifact", action: "actions/upload-artifact@v4", with: { name: "build-output", path: "dist/" } },
    { id: "trivy", label: "Scan image with Trivy", action: "aquasecurity/trivy-action@0.28.0", with: { "image-ref": "ghcr.io/acme/shop:${{ github.sha }}", "exit-code": "1", format: "table" } },
    { id: "slack", label: "Send Slack notification", action: "8398a7/action-slack@v3", with: { status: "${{ job.status }}", fields: "repo,message,commit,author,action,eventName,ref,workflow,job,took" }, env: { SLACK_WEBHOOK_URL: "${{ secrets.SLACK_WEBHOOK_URL }}" } },
  ],
  jenkins: [
    { id: "archive-artifacts", label: "Archive build artifacts", dsl: "archiveArtifacts artifacts: 'dist/**', fingerprint: true" },
    { id: "docker-pipeline", label: "Build with Docker Pipeline", dsl: "script { docker.build(\"ghcr.io/acme/shop:${env.GIT_COMMIT}\") }" },
    { id: "slack", label: "Send Slack notification", dsl: "slackSend channel: '#deployments', message: \"Build ${env.BUILD_NUMBER} completed\"" },
  ],
};
const pluginLabel = (plugin, provider) => plugin.custom ? plugin.name : BUILDER_PLUGINS[provider].find((x) => x.id === plugin.catalogId)?.label || plugin.catalogId;
const pluginLines = (plugin, provider, pad) => {
  const spaces = " ".repeat(pad);
  if (provider === "github-actions") {
    const catalog = BUILDER_PLUGINS[provider].find((x) => x.id === plugin.catalogId);
    const action = plugin.custom ? plugin.action : catalog?.action;
    if (!action) return [];
    const lines = [`${spaces}- name: ${yamlScalar(plugin.custom ? plugin.name : pluginLabel(plugin, provider))}`, `${spaces}  uses: ${action}`];
    const config = plugin.custom ? plugin.config : Object.entries(catalog.with || {}).map(([key, value]) => `${key}: ${value}`).join("\n");
    if (config.trim()) lines.push(`${spaces}  with:`, ...config.split("\n").map((line) => `${spaces}    ${line}`));
    if (!plugin.custom && Object.keys(catalog.env || {}).length) {
      lines.push(`${spaces}  env:`, ...Object.entries(catalog.env).map(([key, value]) => `${spaces}    ${key}: ${value}`));
    }
    return lines;
  }
  const catalog = BUILDER_PLUGINS[provider].find((x) => x.id === plugin.catalogId);
  const dsl = plugin.custom ? plugin.dsl : catalog?.dsl;
  return dsl ? dsl.split("\n").map((line) => `${spaces}${line}`) : [];
};
const yamlScalar = (value) => `'${String(value).replace(/'/g, "''")}'`;

/** GitHub Actions workflow for the pipeline. Secrets only ever appear as secrets.NAME expressions. */
export function toYaml(p) {
  const L = [];
  const push = (...lines) => L.push(...lines);
  push("name: ci", "", "on:", "  push:", "    branches: [main]", "  pull_request:", "");
  if (p.perms) push("permissions:", "  contents: read", "");
  if (p.concurrency) push("concurrency:", `  group: ci-${GH("github.ref")}`, `  cancel-in-progress: ${GH("github.event_name == 'pull_request'")}`, "");
  push("jobs:");
  if (!p.jobs.length) push("  {}");
  const deploys = p.jobs.filter((j) => kindOf(j.kind)?.deploy);
  const leakIn = deploys[0]?.id || p.jobs.at(-1)?.id;
  for (const j of p.jobs) {
    const k = kindOf(j.kind);
    if (!k) continue;
    const m = k.matrix && j.matrix > 1 ? j.matrix : 1;
    push(`  ${j.id}:`, `    name: ${k.label}`);
    if (j.needs.length) push(`    needs: [${j.needs.join(", ")}]`);
    if (k.deploy) push("    if: github.ref == 'refs/heads/main'");
    push("    runs-on: ubuntu-latest", `    timeout-minutes: ${k.deploy ? 15 : 20}`);
    if (k.deploy) push(`    environment: ${k.deploy}`);
    if (p.perms && (k.image || (k.deploy && p.oidc))) {
      push("    permissions:", "      contents: read");
      if (k.image) push("      packages: write");
      if (k.deploy && p.oidc) push("      id-token: write");
    }
    if (m > 1) push("    strategy:", "      fail-fast: false", "      matrix:", `        shard: [${Array.from({ length: m }, (_, i) => i + 1).join(", ")}]`);
    push("    steps:", `      - uses: ${uses("checkout", p.refs)}`);
    if (k.deps) {
      push(`      - uses: ${uses("node", p.refs)}`, "        with:", "          node-version: 20");
      if (j.cache) push("          cache: npm");
      push("      - run: npm ci", `      - run: ${k.run}${m > 1 ? ` -- --shard=${GH("matrix.shard")}/${m}` : ""}`);
    } else if (k.image) {
      push(`      - uses: ${uses("buildx", p.refs)}`, `      - uses: ${uses("login", p.refs)}`, "        with:", "          registry: ghcr.io", `          username: ${GH("github.actor")}`, `          password: ${GH("secrets.GITHUB_TOKEN")}`);
      push(`      - uses: ${uses("push", p.refs)}`, "        with:", `          push: ${GH("github.event_name == 'push'")}`, `          tags: ghcr.io/${GH("github.repository")}:${GH("github.sha")}`);
      if (j.cache) push("          cache-from: type=gha", "          cache-to: type=gha,mode=max");
    } else if (k.deploy) {
      if (p.oidc) push(`      - uses: ${uses("aws", p.refs)}`, "        with:", `          role-to-assume: ${GH("vars.AWS_DEPLOY_ROLE_ARN")}`, "          aws-region: eu-west-1");
      push(`      - run: ./scripts/deploy.sh ${k.deploy} ${GH("github.sha")}`);
      if (!p.oidc) push("        env:", `          AWS_ACCESS_KEY_ID: ${GH("secrets.AWS_ACCESS_KEY_ID")}`, `          AWS_SECRET_ACCESS_KEY: ${GH("secrets.AWS_SECRET_ACCESS_KEY")}`);
    }
    (p.plugins || []).filter((plugin) => plugin.provider === "github-actions" && plugin.jobId === j.id).forEach((plugin) => push(...pluginLines(plugin, "github-actions", 6)));
    if (p.printSecret && j.id === leakIn) push(`      - run: echo "Deploy token is ${GH("secrets.DEPLOY_TOKEN")}"  # leaks into logs`);
  }
  return L.join("\n") + "\n";
}

const groovyQuote = (s) => String(s).replace(/\\/g, "\\\\").replace(/'/g, "\\'");
/** Declarative Jenkinsfile preview. DAG levels become sequential stages with parallel branches at each level. */
export function toJenkinsfile(p) {
  const L = ["pipeline {", `  agent ${p.jenkinsAgent && p.jenkinsAgent !== "any" ? `{ label '${groovyQuote(p.jenkinsAgent)}' }` : "any"}`, "  options {", "    timestamps()", "    timeout(time: 30, unit: 'MINUTES')"];
  if (p.concurrency) L.push("    disableConcurrentBuilds()");
  L.push("  }", "  stages {", "    stage('Checkout') {", "      steps { checkout scm }", "    }");
  const dag = computeDag(jobNodes(p));
  const levelById = dag.level;
  const maxLevel = Math.max(0, ...levelById.values());
  const groups = new Map();
  p.jobs.forEach((j) => {
    const level = levelById.get(j.id) ?? maxLevel + 1;
    if (!groups.has(level)) groups.set(level, []);
    groups.get(level).push(j);
  });
  const deployIds = new Set(p.jobs.filter((j) => kindOf(j.kind)?.deploy).map((j) => j.id));
  const leakId = p.jobs.find((j) => j.kind === "deploy-prod")?.id || p.jobs.find((j) => j.kind.startsWith("deploy-"))?.id;
  const emitJob = (j, indent) => {
    const k = kindOf(j.kind);
    const pad = " ".repeat(indent);
    L.push(`${pad}stage('${groovyQuote(k.label)} · ${groovyQuote(j.id)}') {`);
    if (j.kind === "deploy-prod") L.push(`${pad}  input { message 'Approve production deploy?'; submitter 'release-managers' }`);
    if (k.deploy) L.push(`${pad}  when { branch 'main' }`);
    if (p.jenkinsAgent && p.jenkinsAgent !== "any") L.push(`${pad}  agent { label '${groovyQuote(p.jenkinsAgent)}' }`);
    L.push(`${pad}  steps {`);
    if (k.deps) {
      L.push(`${pad}    sh 'npm ci'`);
      if (k.test && j.matrix > 1) {
        const branches = Array.from({ length: j.matrix }, (_, i) => `'shard-${i + 1}': { sh 'npm test -- --shard=${i + 1}/${j.matrix}' }`).join(",\n");
        L.push(`${pad}    script {`, `${pad}      parallel(`, ...branches.split("\n").map((line) => `${pad}        ${line}`), `${pad}      )`, `${pad}    }`);
      } else L.push(`${pad}    sh '${groovyQuote(k.run)}'`);
    } else if (k.image) {
      L.push(`${pad}    // Configure registry credentials on this agent before pushing images.`);
      L.push(`${pad}    sh "docker buildx build --push --tag ghcr.io/acme/shop:\${env.GIT_COMMIT} ."`);
    } else if (j.kind === "scan") L.push(`${pad}    sh '${groovyQuote(k.run)}'`);
    else if (k.deploy) {
      if (p.oidc) L.push(`${pad}    // Use the Jenkins OIDC/workload-identity provider configured for this agent.`);
      else L.push(`${pad}    withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-deploy']]) {`);
      L.push(`${pad}    ${p.oidc ? "" : "  "}sh './scripts/deploy.sh ${k.deploy}'`);
      if (!p.oidc) L.push(`${pad}    }`);
    }
    (p.plugins || []).filter((plugin) => plugin.provider === "jenkins" && plugin.jobId === j.id).forEach((plugin) => L.push(...pluginLines(plugin, "jenkins", indent + 4)));
    if (p.printSecret && j.id === leakId) {
      L.push(`${pad}    withCredentials([string(credentialsId: 'deploy-token', variable: 'DEPLOY_TOKEN')]) {`, `${pad}      sh 'echo "Deploy token is $DEPLOY_TOKEN"' // unsafe: leaks secret`, `${pad}    }`);
    }
    L.push(`${pad}  }`, `${pad}}`);
  };
  if (!p.jobs.length) L.push("    // Add jobs from the palette to generate pipeline stages.");
  for (const [level, jobs] of [...groups.entries()].sort(([a], [b]) => a - b)) {
    if (jobs.length === 1) emitJob(jobs[0], 6);
    else {
      L.push(`    stage('Parallel jobs · ${level + 1}') {`, "      parallel {");
      jobs.forEach((j) => emitJob(j, 8));
      L.push("      }", "    }");
    }
  }
  L.push("  }", "  post {", "    always {", "      junit allowEmptyResults: true, testResults: '**/reports/*.xml'", "    }", "  }", "}");
  if (dag.cyclic.length) L.push(`// Fix dependency cycle before running these stages: ${dag.cyclic.join(", ")}`);
  if (deployIds.size && !p.oidc) L.push("// Configure and rotate credentialsId 'aws-deploy' in Jenkins Credentials.");
  return L.join("\n") + "\n";
}

const job = (kind, id, needs = [], extra = {}) => ({ id, kind, needs, cache: true, matrix: 1, ...extra });
export const BUILDER_PRESETS = {
  starter: {
    label: "Starter (has problems)",
    p: { perms: false, concurrency: false, oidc: false, printSecret: true, refs: "main", jobs: [job("lint", "lint", [], { cache: false }), job("unit", "unit", [], { cache: false }), job("build", "build", ["lint"], { cache: false }), job("deploy-prod", "deploy-prod", ["build"])] },
  },
  safe: {
    label: "Fast and safe",
    p: {
      perms: true, concurrency: true, oidc: true, printSecret: false, refs: "sha",
      jobs: [job("lint", "lint"), job("unit", "unit", [], { matrix: 4 }), job("build", "build", ["lint", "unit"]), job("scan", "scan", ["build"]), job("integration", "integration", ["build"], { matrix: 2 }),
        job("deploy-staging", "deploy-staging", ["scan", "integration"]), job("deploy-prod", "deploy-prod", ["deploy-staging"])],
    },
  },
  empty: { label: "Empty", p: { perms: true, concurrency: true, oidc: true, printSecret: false, refs: "tag", jobs: [] } },
};

const ID_RE = /^[a-z][a-z0-9-]{0,30}$/;
/** Validates anything read from storage into a clean pipeline object. */
export function sanitizePipeline(raw) {
  const base = structuredClone(BUILDER_PRESETS.starter.p);
  if (!raw || typeof raw !== "object" || !Array.isArray(raw.jobs)) return base;
  const jobs = [];
  for (const j of raw.jobs.slice(0, 30)) {
    if (!j || !kindOf(j.kind) || typeof j.id !== "string" || !ID_RE.test(j.id) || jobs.some((x) => x.id === j.id)) continue;
    jobs.push({ id: j.id, kind: j.kind, needs: Array.isArray(j.needs) ? j.needs.filter((d) => typeof d === "string" && ID_RE.test(d)) : [], cache: j.cache !== false, matrix: MATRIX_SIZES.includes(j.matrix) ? j.matrix : 1 });
  }
  const ids = new Set(jobs.map((j) => j.id));
  jobs.forEach((j) => (j.needs = [...new Set(j.needs)].filter((d) => ids.has(d) && d !== j.id)));
  const plugins = [];
  if (Array.isArray(raw.plugins)) for (const plugin of raw.plugins.slice(0, 30)) {
    if (!plugin || !ids.has(plugin.jobId) || !["github-actions", "jenkins"].includes(plugin.provider)) continue;
    if (plugin.custom && typeof plugin.name === "string") {
      const name = plugin.name.trim().slice(0, 80);
      if (!name) continue;
      if (plugin.provider === "github-actions") {
        const action = typeof plugin.action === "string" ? plugin.action.trim().slice(0, 200) : "";
        if (!/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+@[A-Za-z0-9_.\/-]+$/.test(action)) continue;
        plugins.push({ id: uniquePluginId(plugins), custom: true, provider: plugin.provider, name, action, config: String(plugin.config || "").slice(0, 2000), jobId: plugin.jobId });
      } else {
        const dsl = String(plugin.dsl || "").trim().slice(0, 2000);
        if (!dsl) continue;
        plugins.push({ id: uniquePluginId(plugins), custom: true, provider: plugin.provider, name, dsl, jobId: plugin.jobId });
      }
      continue;
    }
    if (BUILDER_PLUGINS[plugin.provider].some((item) => item.id === plugin.catalogId)) {
      plugins.push({ id: uniquePluginId(plugins), provider: plugin.provider, catalogId: plugin.catalogId, jobId: plugin.jobId });
    }
  }
  return {
    platform: ["github-actions", "jenkins"].includes(raw.platform) ? raw.platform : "github-actions",
    jenkinsAgent: ["any", "linux", "docker"].includes(raw.jenkinsAgent) ? raw.jenkinsAgent : "any",
    perms: !!raw.perms, concurrency: !!raw.concurrency, oidc: !!raw.oidc, printSecret: !!raw.printSecret, plugins,
    refs: ["main", "tag", "sha"].includes(raw.refs) ? raw.refs : "tag", jobs,
  };
}

function uniquePluginId(plugins) {
  let id = 1;
  while (plugins.some((plugin) => plugin.id === id)) id++;
  return id;
}
function addBuilderPlugin(p, provider, catalogId, jobId) {
  if (!p.jobs.some((job) => job.id === jobId) || !BUILDER_PLUGINS[provider]?.some((plugin) => plugin.id === catalogId)) return p;
  const plugins = p.plugins || [];
  return { ...p, plugins: [...plugins, { id: uniquePluginId(plugins), provider, catalogId, jobId }] };
}
function addCustomBuilderPlugin(p, plugin) {
  if (!p.jobs.some((job) => job.id === plugin.jobId)) return p;
  const plugins = p.plugins || [];
  return { ...p, plugins: [...plugins, { ...plugin, id: uniquePluginId(plugins), custom: true }] };
}

export function addJob(p, kind) {
  if (!kindOf(kind)) return p;
  let id = kind, n = 2;
  while (p.jobs.some((j) => j.id === id)) id = `${kind}-${n++}`;
  const last = p.jobs.at(-1);
  return { ...p, jobs: [...p.jobs, job(kind, id, last ? [last.id] : [])] };
}
export function removeJob(p, id) {
  return { ...p, jobs: p.jobs.filter((j) => j.id !== id).map((j) => ({ ...j, needs: j.needs.filter((d) => d !== id) })) };
}
export function moveJob(p, id, dir) {
  const i = p.jobs.findIndex((j) => j.id === id);
  const k = i + dir;
  if (i < 0 || k < 0 || k >= p.jobs.length) return p;
  const jobs = [...p.jobs];
  [jobs[i], jobs[k]] = [jobs[k], jobs[i]];
  return { ...p, jobs };
}
export function toggleNeed(p, id, dep) {
  return { ...p, jobs: p.jobs.map((j) => (j.id !== id || dep === id ? j : { ...j, needs: j.needs.includes(dep) ? j.needs.filter((d) => d !== dep) : [...j.needs, dep] })) };
}

const LEVEL_PILL = { error: "bad", warn: "warn", info: "neutral" };

export function playground(view) {
  let p = sanitizePipeline(store.get("cicd-builder", null) ?? BUILDER_PRESETS.starter.p);
  view.innerHTML = `
    ${labHero("CI", "mint", "Pipeline Builder", "Build one pipeline model, then switch between GitHub Actions workflow YAML and a Jenkins Declarative Pipeline. Wire job dependencies, compare runner time and review platform-specific security guidance.")}
    <div class="filters"><span class="muted">Start from:</span>${Object.entries(BUILDER_PRESETS).map(([k, x]) => `<button class="btn small" data-bpreset="${k}">${esc(x.label)}</button>`).join("")}</div>
    <div class="filters"><b>Generate for:</b><div class="tabs cd-seg" role="group" aria-label="Pipeline platform"><button type="button" data-platform="github-actions">GitHub Actions</button><button type="button" data-platform="jenkins">Jenkins</button></div><span class="muted" id="cdBuilderPlatformHint"></span></div>
    <div class="lab-grid side-left">
      <aside class="panel clay cd-controls">
        <h3>Add a job</h3>
        <div class="cd-palette">${Object.entries(JOB_KINDS).map(([k, x]) => `<button class="btn small" data-add="${k}" aria-label="Add ${esc(x.label)} job">+ ${esc(x.label)}</button>`).join("")}</div>
        <h3>Plugins & integrations</h3>
        <p class="muted">Add a GitHub Action or Jenkins Pipeline step to a job. The code preview updates with the selected platform.</p>
        <label class="cd-field">Attach plugin to
          <select id="cdPluginJob" aria-label="Job for plugin step"></select>
        </label>
        <div class="cd-palette" id="cdPluginPalette"></div>
        <details class="cd-custom-plugin">
          <summary>Add a custom plugin step</summary>
          <label class="cd-field">Step name<input id="cdCustomPluginName" type="text" maxlength="80" placeholder="For example: Publish coverage"></label>
          <label class="cd-field" id="cdCustomActionField">GitHub Action reference<input id="cdCustomPluginAction" type="text" placeholder="owner/action@v1"></label>
          <label class="cd-field" id="cdCustomConfigField">Action inputs <span class="muted">one key: value per line</span><textarea id="cdCustomPluginConfig" class="code short" rows="3" placeholder="path: coverage/\nname: coverage-report"></textarea></label>
          <label class="cd-field" id="cdCustomDslField" hidden>Jenkins Pipeline DSL<textarea id="cdCustomPluginDsl" class="code short" rows="3" placeholder="publishHTML(target: [reportDir: 'coverage'])"></textarea></label>
          <button class="btn small" type="button" data-add-custom-plugin>Add custom step</button>
        </details>
        <div id="cdPlugins" class="cd-plugins"></div>
        <h3 id="cdBuilderSettingsTitle">GitHub Actions settings</h3>
        <div id="ghBuilderSettings">
          <label class="check"><input type="checkbox" data-set="perms"> Least-privilege <code>GITHUB_TOKEN</code></label>
          <label class="cd-field">Action references
            <select id="cdRefs"><option value="main">Branch (@main)</option><option value="tag">Tag (@v4)</option><option value="sha">Commit SHA</option></select></label>
        </div>
        <div id="jenkinsBuilderSettings" hidden>
          <label class="cd-field">Agent label
            <select id="jenkinsAgent"><option value="any">any available agent</option><option value="linux">linux</option><option value="docker">docker</option></select></label>
          <p class="muted">Jenkins reads a <code>Jenkinsfile</code> from source control. Configure labels, credentials and OIDC/workload-identity plugins on your agents.</p>
        </div>
        <label class="check"><input type="checkbox" data-set="concurrency"> Prevent overlapping deployments</label>
        <label class="check"><input type="checkbox" data-set="oidc"> Use OIDC / workload identity for cloud auth</label>
        <label class="check"><input type="checkbox" data-set="printSecret"> Echo a secret for debugging</label>
      </aside>
      <div class="lab-main cd-main">
        <div class="cd-stats" id="cdStats"></div>
        <div class="panel clay"><h3>Jobs</h3><div id="cdJobs" class="cd-jobs"></div></div>
        <div class="panel clay"><h3>Timeline</h3><div id="cdGantt" class="cd-gantt"></div></div>
        <div class="panel clay"><h3>Review</h3><ul class="clean cd-problems" id="cdProblems"></ul></div>
        <div class="panel clay"><div class="cd-head"><h3 id="cdOutputTitle">.github/workflows/ci.yml</h3><button class="btn small" id="cdCopy">Copy</button></div><pre class="yaml cd-yaml" id="cdYaml"></pre></div>
      </div>
    </div>`;

  const save = () => store.set("cicd-builder", p);
  const outputCode = () => p.platform === "jenkins" ? toJenkinsfile(p) : toYaml(p);
  const draw = () => {
    const selectedPlatform = p.platform === "jenkins" ? "jenkins" : "github-actions";
    view.querySelectorAll("[data-set]").forEach((i) => (i.checked = !!p[i.dataset.set]));
    $("#cdRefs", view).value = p.refs;
    $("#jenkinsAgent", view).value = p.jenkinsAgent;
    $("#ghBuilderSettings", view).hidden = selectedPlatform !== "github-actions";
    $("#jenkinsBuilderSettings", view).hidden = selectedPlatform !== "jenkins";
    $("#cdBuilderSettingsTitle", view).textContent = `${selectedPlatform === "jenkins" ? "Jenkins" : "GitHub Actions"} settings`;
    $("#cdBuilderPlatformHint", view).textContent = selectedPlatform === "jenkins" ? "Jenkinsfile · agents · stages · credentials binding" : "workflow YAML · hosted runners · jobs · GITHUB_TOKEN";
    $("#cdOutputTitle", view).textContent = selectedPlatform === "jenkins" ? "Jenkinsfile" : ".github/workflows/ci.yml";
    $("#cdPluginJob", view).innerHTML = p.jobs.length ? p.jobs.map((job) => `<option value="${esc(job.id)}">${esc(job.id)}</option>`).join("") : `<option value="">Add a job first</option>`;
    $("#cdPluginJob", view).disabled = !p.jobs.length;
    $("#cdPluginPalette", view).innerHTML = BUILDER_PLUGINS[selectedPlatform].map((plugin) => `<button type="button" class="btn small" data-add-plugin="${esc(plugin.id)}" ${p.jobs.length ? "" : "disabled"}>+ ${esc(plugin.label)}</button>`).join("");
    $("#cdCustomActionField", view).hidden = selectedPlatform !== "github-actions";
    $("#cdCustomConfigField", view).hidden = selectedPlatform !== "github-actions";
    $("#cdCustomDslField", view).hidden = selectedPlatform !== "jenkins";
    $("#cdPlugins", view).innerHTML = (p.plugins || []).filter((plugin) => plugin.provider === selectedPlatform).map((plugin) => `
      <div class="cd-plugin"><span><b>${esc(pluginLabel(plugin, selectedPlatform))}</b><small class="muted">in ${esc(p.jobs.find((job) => job.id === plugin.jobId)?.id || "missing job")}</small></span>
      <button type="button" class="btn small" data-remove-plugin="${plugin.id}" aria-label="Remove ${esc(pluginLabel(plugin, selectedPlatform))}">Remove</button></div>`).join("") || `<p class="muted">No ${selectedPlatform === "jenkins" ? "Jenkins steps" : "Actions"} added yet.</p>`;
    view.querySelectorAll("[data-platform]").forEach((b) => {
      const on = b.dataset.platform === p.platform;
      b.classList.toggle("active", on);
      b.setAttribute("aria-pressed", on);
    });
    const a = analyzePipeline(p);
    const problems = lintPipeline(p, p.platform);
    const errs = problems.filter((x) => x.level === "error").length;
    const crit = new Set(a.path);
    $("#cdStats", view).innerHTML = [
      ["Wall time", a.cyclic.length ? "blocked" : fmt(a.wall), a.cyclic.length ? "bad" : "neutral"],
      ["If run serially", fmt(a.serial), "neutral"],
      ["Runner time billed", fmt(a.billed), "neutral"],
      ["Review", errs ? `${errs} error${errs > 1 ? "s" : ""}` : problems.some((x) => x.level === "warn") ? "warnings" : "clean", errs ? "bad" : problems.some((x) => x.level === "warn") ? "warn" : "ok"],
    ].map(([k, v, t]) => `<div class="panel clay stat-card"><span class="muted">${esc(k)}</span><b class="pill ${t}">${esc(v)}</b></div>`).join("");

    $("#cdJobs", view).innerHTML = p.jobs.length ? p.jobs.map((j, i) => {
      const k = kindOf(j.kind);
      const n = a.nodes.find((x) => x.id === j.id);
      const others = p.jobs.filter((x) => x.id !== j.id);
      return `<div class="cd-job${crit.has(j.id) ? " is-crit" : ""}${a.cyclic.includes(j.id) ? " is-bad" : ""}">
        <div class="cd-job-head">
          <div><b>${esc(k.label)}</b> <code>${esc(j.id)}</code> <span class="pill neutral">${fmt(n.dur)}</span>${crit.has(j.id) ? ` <span class="pill warn">critical</span>` : ""}</div>
          <div class="row">
            <button class="btn small" data-move="-1" data-id="${esc(j.id)}" aria-label="Move ${esc(j.id)} up" ${i === 0 ? "disabled" : ""}>Up</button>
            <button class="btn small" data-move="1" data-id="${esc(j.id)}" aria-label="Move ${esc(j.id)} down" ${i === p.jobs.length - 1 ? "disabled" : ""}>Down</button>
            <button class="btn small" data-remove="${esc(j.id)}" aria-label="Remove ${esc(j.id)}">Remove</button>
          </div>
        </div>
        <div class="cd-needs"><span class="muted">needs:</span>${others.length ? others.map((o) => `<button type="button" class="cd-chip${j.needs.includes(o.id) ? " on" : ""}" data-need="${esc(o.id)}" data-id="${esc(j.id)}" aria-pressed="${j.needs.includes(o.id)}">${esc(o.id)}</button>`).join("") : `<span class="muted">no other jobs</span>`}</div>
        ${isCacheable(j.kind) || k.matrix ? `<div class="row cd-job-opts">
          ${isCacheable(j.kind) ? `<label class="check"><input type="checkbox" data-cache="${esc(j.id)}" ${j.cache ? "checked" : ""}> cache</label>` : ""}
          ${k.matrix ? `<label class="inline cd-inline">matrix shards <select data-matrix="${esc(j.id)}" aria-label="Matrix size for ${esc(j.id)}">${MATRIX_SIZES.map((s) => `<option value="${s}" ${s === j.matrix ? "selected" : ""}>${s}</option>`).join("")}</select></label>` : ""}
          ${k.matrix && j.matrix > 1 ? `<span class="muted">${j.matrix} runners × ${fmt(n.dur)}</span>` : ""}
        </div>` : ""}
      </div>`;
    }).join("") : `<p class="muted">No jobs yet. Add some from the palette.</p>`;

    const rows = a.order.map((id) => a.nodes.find((x) => x.id === id));
    $("#cdGantt", view).innerHTML = rows.length ? `${rows.map((n) => {
      const left = a.wall ? (a.es.get(n.id) / a.wall) * 100 : 0;
      const w = a.wall ? Math.max(1.5, (n.dur / a.wall) * 100) : 0;
      return `<div class="cd-grow"><span class="cd-gname">${esc(n.id)}</span><div class="cd-gtrack"><i class="${crit.has(n.id) ? "crit" : ""}" style="left:${left}%;width:${w}%" title="${esc(n.id)}: starts ${fmt(a.es.get(n.id))}, takes ${fmt(n.dur)}"></i></div><span class="cd-gtime muted">${fmt(a.ef.get(n.id))}</span></div>`;
    }).join("")}<p class="muted cd-crit">Critical path: ${a.path.map(esc).join(" &rarr; ") || "none"} (${fmt(a.wall)}). Parallelism saves ${fmt(Math.max(0, a.serial - a.wall))} versus a serial run.</p>${a.cyclic.length ? `<p class="pill bad">Not scheduled (cycle): ${a.cyclic.map(esc).join(", ")}</p>` : ""}` : `<p class="muted">Nothing to schedule.</p>`;

    $("#cdProblems", view).innerHTML = problems.length ? problems.map((x) => `<li><span class="pill ${LEVEL_PILL[x.level]}">${esc(x.level)}</span> ${esc(x.msg)}<div class="muted">Fix: ${esc(x.fix)}</div></li>`).join("") : `<li><span class="pill ok">ok</span> No problems found. Tests gate deploys, tokens are least-privilege and credentials are short-lived.</li>`;
    const code = selectedPlatform === "jenkins" ? toJenkinsfile(p) : toYaml(p);
    const preview = $("#cdYaml", view);
    preview.dataset.codePlatform = selectedPlatform;
    preview.innerHTML = highlightCode(code, selectedPlatform === "jenkins" ? "generic" : "yaml");
  };
  const update = (next) => { p = next; save(); draw(); };

  view.addEventListener("click", (e) => {
    const b = e.target.closest("button");
    if (!b || !view.contains(b)) return;
    const d = b.dataset;
    if (["github-actions", "jenkins"].includes(d.platform)) update({ ...p, platform: d.platform });
    else if (d.addPlugin) update(addBuilderPlugin(p, p.platform, d.addPlugin, $("#cdPluginJob", view).value));
    else if (d.removePlugin) update({ ...p, plugins: (p.plugins || []).filter((plugin) => plugin.id !== +d.removePlugin) });
    else if (b.hasAttribute("data-add-custom-plugin")) {
      const provider = p.platform;
      const jobId = $("#cdPluginJob", view).value;
      const name = $("#cdCustomPluginName", view).value.trim();
      if (!jobId || !name) { toast("Choose a job and enter a step name.", true); return; }
      if (provider === "github-actions") {
        const action = $("#cdCustomPluginAction", view).value.trim();
        if (!/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+@[A-Za-z0-9_.\/-]+$/.test(action)) { toast("Enter an Action reference like owner/action@v1.", true); return; }
        update(addCustomBuilderPlugin(p, { provider, jobId, name, action, config: $("#cdCustomPluginConfig", view).value }));
      } else {
        const dsl = $("#cdCustomPluginDsl", view).value.trim();
        if (!dsl) { toast("Enter the Jenkins Pipeline DSL step.", true); return; }
        update(addCustomBuilderPlugin(p, { provider, jobId, name, dsl }));
      }
    }
    else if (d.add) update(addJob(p, d.add));
    else if (d.remove) update(removeJob(p, d.remove));
    else if (d.move) update(moveJob(p, d.id, +d.move));
    else if (d.need) update(toggleNeed(p, d.id, d.need));
    else if (d.bpreset && BUILDER_PRESETS[d.bpreset]) { update({ ...structuredClone(BUILDER_PRESETS[d.bpreset].p), platform: p.platform, jenkinsAgent: p.jenkinsAgent }); toast(`Loaded "${BUILDER_PRESETS[d.bpreset].label}"`); }
    else if (b.id === "cdCopy") copy(outputCode());
  });
  view.addEventListener("change", (e) => {
    const t = e.target;
    if (t.dataset.set && ["perms", "concurrency", "oidc", "printSecret"].includes(t.dataset.set)) update({ ...p, [t.dataset.set]: t.checked });
    else if (t.id === "cdRefs") update({ ...p, refs: ["main", "tag", "sha"].includes(t.value) ? t.value : "tag" });
    else if (t.id === "jenkinsAgent") update({ ...p, jenkinsAgent: ["any", "linux", "docker"].includes(t.value) ? t.value : "any" });
    else if (t.dataset.cache) update({ ...p, jobs: p.jobs.map((j) => (j.id === t.dataset.cache ? { ...j, cache: t.checked } : j)) });
    else if (t.dataset.matrix) { const m = +t.value; if (MATRIX_SIZES.includes(m)) update({ ...p, jobs: p.jobs.map((j) => (j.id === t.dataset.matrix ? { ...j, matrix: m } : j)) }); }
  });
  draw();
}
