import { $, $$, esc } from "../util.js";
import { labHero } from "./common.js";

const num = (n) => {
  const a = Math.abs(n);
  if (a >= 1e9) return (n / 1e9).toFixed(a >= 1e10 ? 0 : 1) + "B";
  if (a >= 1e6) return (n / 1e6).toFixed(a >= 1e7 ? 0 : 1) + "M";
  if (a >= 1e3) return (n / 1e3).toFixed(a >= 1e4 ? 0 : 1) + "K";
  return a >= 10 || n === 0 ? Math.round(n).toString() : n.toFixed(1);
};
const bytes = (b) => {
  const u = ["B", "KB", "MB", "GB", "TB", "PB", "EB"];
  let i = 0;
  while (b >= 1000 && i < u.length - 1) { b /= 1000; i++; }
  return `${b >= 100 ? Math.round(b) : b.toFixed(1)} ${u[i]}`;
};

// ===================================================================== architecture simulator
const CAP = { app: 1000, cache: 50000, primary: 2000, replica: 3000, lb: 100000 };
const PRESETS = {
  mvp: { label: "Startup MVP", rps: 200, read: 80, cdn: false, lb: false, servers: 1, cache: false, hit: 80, replicas: 0, queue: false, shards: 1 },
  news: { label: "Read-heavy news site", rps: 40000, read: 97, cdn: false, lb: true, servers: 4, cache: false, hit: 90, replicas: 0, queue: false, shards: 1 },
  iot: { label: "Write-heavy IoT ingest", rps: 20000, read: 10, cdn: false, lb: true, servers: 20, cache: false, hit: 50, replicas: 1, queue: false, shards: 1 },
  sale: { label: "Black Friday", rps: 120000, read: 90, cdn: true, lb: true, servers: 20, cache: true, hit: 90, replicas: 2, queue: false, shards: 2 },
};

function model(c) {
  const reads = c.rps * c.read / 100;
  const writes = c.rps - reads;
  const cdnServed = c.cdn ? reads * 0.4 : 0;
  const appRps = c.rps - cdnServed;
  const liveServers = c.lb ? c.servers : 1;
  const appReads = reads - cdnServed;
  const dbReads = c.cache ? appReads * (1 - c.hit / 100) : appReads;
  const dbWrites = writes * (c.queue ? 0.6 : 1);
  const perShardReads = dbReads / c.shards;
  const util = {
    cdn: c.cdn ? reads / 1e6 : 0,
    lb: c.lb ? appRps / CAP.lb : 0,
    app: appRps / (liveServers * CAP.app),
    cache: c.cache ? appReads / CAP.cache : 0,
    queue: c.queue ? writes / 200000 : 0,
    primary: (dbWrites / c.shards + (c.replicas ? 0 : perShardReads)) / CAP.primary,
    replica: c.replicas ? perShardReads / c.replicas / CAP.replica : 0,
  };
  const q = (ms, u) => (u >= 1 ? ms * 40 : ms / (1 - Math.min(u, 0.97)));
  const readLat = (cdnServed ? (cdnServed / reads) * 18 : 0) + (appReads / Math.max(reads, 1)) * (q(4, util.app) + (c.cache ? (c.hit / 100) * 1 + (1 - c.hit / 100) * q(8, c.replicas ? util.replica : util.primary) : q(8, c.replicas ? util.replica : util.primary)));
  const writeLat = q(4, util.app) + (c.queue ? 2 : q(12, util.primary));
  const latency = reads ? (readLat * reads + writeLat * writes) / c.rps : writeLat;
  const spof = [];
  if (liveServers < 2) spof.push("one app server: a deploy or crash takes the site down");
  if (!c.replicas) spof.push("no database replica: losing the primary means downtime and maybe data loss");
  const cost = c.servers * 1 + (c.lb ? 0.3 : 0) + (c.cache ? 1.5 : 0) + (c.cdn ? 0.6 : 0) + (c.queue ? 0.5 : 0) + c.shards * (2 + c.replicas * 2);
  const traffic = { users: c.rps, cdn: cdnServed, lb: appRps, app: appRps, cache: c.cache ? appReads : 0, queue: c.queue ? writes : 0, primary: dbWrites + (c.replicas ? 0 : dbReads), replica: c.replicas ? dbReads : 0 };
  return { util, latency, spof, cost, traffic, liveServers, dbReads, dbWrites };
}

function advice(c, m) {
  const tips = [];
  const hot = Object.entries(m.util).sort((a, b) => b[1] - a[1])[0];
  if (c.servers > 1 && !c.lb) tips.push("You have several app servers but no load balancer, so only one receives traffic. Turn on the load balancer.");
  if (m.util.app > 0.8) tips.push(`App tier at ${Math.round(m.util.app * 100)}%: add servers (stateless servers scale horizontally) or put a CDN in front for static content.`);
  if (m.util.primary > 0.8 && c.read >= 50 && !c.cache) tips.push("The database is drowning in reads: add a cache (cache-aside) and/or read replicas.");
  if (m.util.primary > 0.8 && c.read >= 50 && c.cache && !c.replicas) tips.push("Reads still hit the primary: add read replicas.");
  if (m.util.primary > 0.8 && c.read < 50) tips.push(c.queue ? "Writes still saturate the primary: shard the database to split writes." : "Write-heavy load: a queue smooths spikes; sharding splits writes across primaries.");
  if (m.util.replica > 0.8) tips.push("Replicas are saturated: add more replicas or raise the cache hit ratio.");
  if (c.cache && c.hit < 80 && m.util.primary + m.util.replica > 0.6) tips.push("Cache hit ratio is low: cache more of the hot set or increase TTLs.");
  m.spof.forEach((s) => tips.push(`Single point of failure: ${s}.`));
  if (!tips.length) tips.push("Everything is green with redundancy. Now look at cost: can you remove a component and stay green?");
  return { hot, tips };
}

const NODES = [
  { id: "users", label: "Users", x: 6, y: 50, always: true },
  { id: "cdn", label: "CDN", x: 21, y: 18 },
  { id: "lb", label: "Load balancer", x: 34, y: 50 },
  { id: "app", label: "App servers", x: 53, y: 50, always: true },
  { id: "cache", label: "Cache", x: 72, y: 16 },
  { id: "queue", label: "Queue + workers", x: 72, y: 84 },
  { id: "primary", label: "DB primary", x: 90, y: 42, always: true },
  { id: "replica", label: "Read replicas", x: 90, y: 74 },
];
const LINKS = [["users", "cdn"], ["users", "lb"], ["lb", "app"], ["users", "app"], ["app", "cache"], ["app", "queue"], ["queue", "primary"], ["app", "primary"], ["app", "replica"], ["primary", "replica"]];

export function lab(view) {
  let c = { ...PRESETS.mvp };
  view.innerHTML = `
    ${labHero("ARC", "lilac", "Architecture Simulator", "Drive traffic at a system and grow it piece by piece. Every box shows its utilisation; links thicken with traffic. Find the bottleneck, fix it, remove single points of failure, then try to do it cheaply.")}
    <div class="filters"><span class="muted">Presets:</span>${Object.entries(PRESETS).map(([k, p]) => `<button class="btn small" data-preset="${k}">${esc(p.label)}</button>`).join("")}</div>
    <div class="lab-grid side-left">
      <aside class="panel clay arch-controls">
        <label>Requests / second <b id="rpsV"></b><input type="range" id="rps" min="0" max="100" step="1"></label>
        <label>Reads <b id="readV"></b><input type="range" id="read" min="0" max="100" step="1"></label>
        <hr>
        <label class="check"><input type="checkbox" data-k="cdn"> CDN for static content</label>
        <label class="check"><input type="checkbox" data-k="lb"> Load balancer</label>
        <label>App servers <b id="serversV"></b><input type="range" id="servers" min="1" max="40"></label>
        <label class="check"><input type="checkbox" data-k="cache"> Cache (Redis)</label>
        <label>Cache hit ratio <b id="hitV"></b><input type="range" id="hit" min="0" max="99"></label>
        <label class="check"><input type="checkbox" data-k="queue"> Queue for writes</label>
        <label>Read replicas per shard <b id="replicasV"></b><input type="range" id="replicas" min="0" max="5"></label>
        <label>Shards <b id="shardsV"></b><input type="range" id="shards" min="1" max="8"></label>
      </aside>
      <div class="lab-main">
        <div class="panel clay arch-stage" id="arch"></div>
        <div class="arch-stats" id="stats"></div>
        <div class="panel clay" id="advice"></div>
      </div>
    </div>`;

  const toLog = (v) => Math.round(10 ** (1 + (v / 100) * 4.5) / 10) * 10;
  const fromLog = (rps) => Math.round(((Math.log10(Math.max(rps, 10)) - 1) / 4.5) * 100);

  const sync = () => {
    $("#rps").value = fromLog(c.rps);
    ["read", "servers", "hit", "replicas", "shards"].forEach((k) => ($(`#${k}`).value = c[k]));
    $$("[data-k]").forEach((i) => (i.checked = c[i.dataset.k]));
  };
  const draw = () => {
    const m = model(c);
    $("#rpsV").textContent = num(c.rps);
    $("#readV").textContent = `${c.read}% (writes ${100 - c.read}%)`;
    $("#serversV").textContent = c.servers;
    $("#hitV").textContent = `${c.hit}%`;
    $("#replicasV").textContent = c.replicas;
    $("#shardsV").textContent = c.shards;
    $("#hit").disabled = !c.cache;
    const on = (id) => ({ users: true, app: true, primary: true, cdn: c.cdn, lb: c.lb, cache: c.cache, queue: c.queue, replica: c.replicas > 0 })[id];
    const linkOn = ([a, b]) => on(a) && on(b) && !(a === "users" && b === "app" && c.lb) && !(a === "app" && b === "replica" && !c.replicas) && !(a === "primary" && b === "replica" && !c.replicas);
    const flowOf = ([a, b]) => (b === "cdn" ? m.traffic.cdn : b === "lb" || (a === "users" && b === "app") ? m.traffic.lb : a === "lb" ? m.traffic.app : b === "cache" ? m.traffic.cache : b === "queue" ? m.traffic.queue : a === "queue" ? m.dbWrites : b === "replica" && a === "app" ? m.traffic.replica : a === "primary" ? m.dbWrites / 10 : c.queue ? m.traffic.primary - m.dbWrites : m.traffic.primary);
    const W = 1000, H = 360;
    const P = (id) => {
      const n = NODES.find((x) => x.id === id);
      return [n.x * W / 100, n.y * H / 100];
    };
    const paths = LINKS.filter(linkOn).map((l) => {
      const [[x1, y1], [x2, y2]] = [P(l[0]), P(l[1])];
      const f = flowOf(l);
      const w = f > 0 ? Math.min(9, 1 + Math.log10(f + 1) * 1.5) : 1;
      const dur = Math.max(0.4, 3 - Math.log10(f + 1) * 0.5);
      return `<path d="M${x1},${y1} C${(x1 + x2) / 2},${y1} ${(x1 + x2) / 2},${y2} ${x2},${y2}" class="arch-link ${f > 0 ? "flow" : "dashed"}" style="stroke-width:${w};animation-duration:${dur}s"/>`;
    }).join("");
    const nodes = NODES.filter((n) => on(n.id)).map((n) => {
      const u = m.util[n.id] ?? 0;
      const lvl = n.id === "users" ? "neutral" : u >= 1 ? "over" : u >= 0.85 ? "hot" : u >= 0.6 ? "warm" : "cool";
      const count = n.id === "app" ? `${m.liveServers}${m.liveServers < c.servers ? `/${c.servers}` : ""} × ` : n.id === "replica" ? `${c.replicas * c.shards} × ` : n.id === "primary" && c.shards > 1 ? `${c.shards} shards × ` : "";
      return `<div class="arch-node ${lvl}" style="left:${n.x}%;top:${n.y}%">
        <b>${count}${esc(n.label)}</b>
        ${n.id === "users" ? `<span>${num(c.rps)} rps</span>` : `<span class="util"><i style="width:${Math.min(100, u * 100)}%"></i></span><span>${u >= 1 ? "OVERLOADED " : ""}${Math.round(u * 100)}%</span>`}
      </div>`;
    }).join("");
    $("#arch").innerHTML = `<svg viewBox="0 0 ${W} ${H}" preserveAspectRatio="none" class="arch-svg">${paths}</svg>${nodes}`;
    const worst = Math.max(...Object.values(m.util));
    const ok = worst < 0.85 && !m.spof.length;
    $("#stats").innerHTML = [
      ["Avg latency", worst >= 1 ? "timeouts" : `${Math.round(m.latency)} ms`, worst >= 1 ? "bad" : m.latency > 100 ? "warn" : "ok"],
      ["Bottleneck", `${NODES.find((n) => n.id === Object.entries(m.util).sort((a, b) => b[1] - a[1])[0][0]).label} ${Math.round(worst * 100)}%`, worst >= 1 ? "bad" : worst >= 0.85 ? "warn" : "ok"],
      ["Single points of failure", m.spof.length || "none", m.spof.length ? "warn" : "ok"],
      ["Relative cost", `${m.cost.toFixed(1)} units/h`, "neutral"],
      ["Verdict", ok ? "Production-ready" : worst >= 1 ? "Falling over" : "Needs work", ok ? "ok" : worst >= 1 ? "bad" : "warn"],
    ].map(([k, v, t]) => `<div class="panel clay stat-card"><span class="muted">${k}</span><b class="pill ${t}">${esc(v)}</b></div>`).join("");
    const a = advice(c, m);
    $("#advice").innerHTML = `<h3>What to do next</h3><ul class="clean tips">${a.tips.map((t) => `<li>${esc(t)}</li>`).join("")}</ul>
      <p class="muted" style="font-size:.78rem;margin-bottom:0">Model: app server ≈ ${num(CAP.app)} rps, cache ≈ ${num(CAP.cache)}, DB primary ≈ ${num(CAP.primary)} qps, replica ≈ ${num(CAP.replica)} reads. CDN serves ~40% of reads (static assets). A queue smooths write peaks to ~60% and makes writes async. Latency uses a queueing curve that explodes near 100%.</p>`;
  };

  view.addEventListener("input", (e) => {
    const id = e.target.id;
    if (id === "rps") c.rps = toLog(+e.target.value);
    else if (["read", "servers", "hit", "replicas", "shards"].includes(id)) c[id] = +e.target.value;
    else if (e.target.dataset.k) c[e.target.dataset.k] = e.target.checked;
    else return;
    draw();
  });
  view.addEventListener("click", (e) => {
    const p = e.target.closest("[data-preset]")?.dataset.preset;
    if (!p) return;
    c = { ...PRESETS[p] };
    sync();
    draw();
  });
  sync();
  draw();
}

// ===================================================================== capacity estimator
const EST_PRESETS = {
  twitter: { label: "Twitter-like feed", dau: 200, writes: 2, ratio: 100, size: 1, media: 10, mediaSize: 500, years: 5, peak: 3, repl: 3, hot: 20, cap: 1000 },
  shortener: { label: "URL shortener", dau: 20, writes: 0.5, ratio: 100, size: 0.5, media: 0, mediaSize: 0, years: 10, peak: 2, repl: 3, hot: 20, cap: 5000 },
  chat: { label: "Chat app", dau: 500, writes: 40, ratio: 1, size: 0.2, media: 2, mediaSize: 300, years: 2, peak: 2, repl: 3, hot: 10, cap: 2000 },
  photos: { label: "Photo sharing", dau: 100, writes: 0.3, ratio: 50, size: 2, media: 100, mediaSize: 2000, years: 5, peak: 3, repl: 3, hot: 20, cap: 800 },
};
const FIELDS = [
  ["dau", "Daily active users (millions)", 0.1, 2000, 0.1],
  ["writes", "Writes per user per day", 0.1, 200, 0.1],
  ["ratio", "Reads per write", 0.1, 1000, 0.1],
  ["size", "Record size (KB)", 0.1, 100, 0.1],
  ["media", "% of writes with media", 0, 100, 1],
  ["mediaSize", "Media size (KB)", 0, 50000, 10],
  ["years", "Retention (years)", 1, 20, 1],
  ["peak", "Peak / average", 1, 10, 0.5],
  ["repl", "Replication factor", 1, 5, 1],
  ["hot", "Hot data to cache (%)", 1, 100, 1],
  ["cap", "QPS one server handles", 100, 50000, 100],
];
const LATENCY = [
  ["L1 cache reference", "0.5 ns"], ["Branch mispredict", "5 ns"], ["Main memory reference", "100 ns"],
  ["Compress 1 KB (fast codec)", "2 µs"], ["Read 1 MB from memory", "3 µs"], ["SSD random read", "16 µs"],
  ["Read 1 MB from SSD", "50 µs"], ["Round trip same datacenter", "0.5 ms"], ["Redis GET over network", "~1 ms"],
  ["Read 1 MB from disk (HDD)", "1 ms"], ["Disk seek", "2 ms"], ["Packet CA ↔ Netherlands ↔ CA", "150 ms"],
];

export function playground(view) {
  let v = { ...EST_PRESETS.twitter };
  view.innerHTML = `
    ${labHero("EST", "peach", "Capacity Estimator", "Back-of-the-envelope maths, the way interviewers want it: state assumptions, derive QPS, storage, bandwidth, cache and servers, and round sensibly. Every number shows its formula.")}
    <div class="filters"><span class="muted">Presets:</span>${Object.entries(EST_PRESETS).map(([k, p]) => `<button class="btn small" data-preset="${k}">${esc(p.label)}</button>`).join("")}</div>
    <div class="lab-grid side-left">
      <aside class="panel clay est-inputs">${FIELDS.map(([k, label, min, max, step]) => `<label>${esc(label)}<input type="number" id="f-${k}" min="${min}" max="${max}" step="${step}"></label>`).join("")}</aside>
      <div class="lab-main"><div class="est-grid" id="est"></div>
        <div class="lab-grid halves">
          <div class="panel clay"><h3>Latency numbers to know</h3><div class="res-table"><table><tbody>${LATENCY.map(([k, t]) => `<tr><td>${esc(k)}</td><td class="num">${esc(t)}</td></tr>`).join("")}</tbody></table></div></div>
          <div class="panel clay"><h3>Handy shortcuts</h3><ul class="clean tips">
            <li><b>1 day ≈ 86,400 s ≈ 10⁵ s</b>, so 1M requests/day ≈ 12 QPS.</li>
            <li><b>2¹⁰ ≈ 10³</b>: KB, MB, GB, TB, PB are each ×1000.</li>
            <li>Peak traffic is commonly 2–3× the daily average.</li>
            <li>80/20 rule: caching ~20% of daily reads serves most traffic.</li>
            <li>One commodity server: ~1K–10K simple QPS; one Postgres primary: a few K writes/s.</li>
            <li>Always round, state assumptions out loud and sanity-check the order of magnitude.</li>
          </ul></div>
        </div>
      </div>
    </div>`;

  const sync = () => FIELDS.forEach(([k]) => ($(`#f-${k}`).value = v[k]));
  const draw = () => {
    const dau = v.dau * 1e6;
    const writesDay = dau * v.writes;
    const wqps = writesDay / 86400;
    const rqps = wqps * v.ratio;
    const peak = (wqps + rqps) * v.peak;
    const textDay = writesDay * v.size * 1e3;
    const mediaDay = writesDay * (v.media / 100) * v.mediaSize * 1e3;
    const perDay = textDay + mediaDay;
    const total = perDay * 365 * v.years * v.repl;
    const avgObj = writesDay ? perDay / writesDay : 0;
    const ingress = wqps * avgObj;
    const egress = rqps * avgObj;
    const cache = rqps * 86400 * v.size * 1e3 * (v.hot / 100);
    const servers = Math.ceil(peak / v.cap);
    const cards = [
      ["Write QPS", num(wqps), `${num(dau)} users × ${v.writes} writes ÷ 86,400 s`],
      ["Read QPS", num(rqps), `write QPS × ${v.ratio} reads per write`],
      ["Peak QPS", num(peak), `(read + write) × ${v.peak} peak factor`],
      ["New data / day", bytes(perDay), `${num(writesDay)} writes × ${v.size} KB + ${v.media}% × ${num(v.mediaSize)} KB media`],
      [`Storage for ${v.years} years`, bytes(total), `per day × 365 × ${v.years} × ${v.repl} replicas`],
      ["Ingress bandwidth", `${bytes(ingress)}/s`, "write QPS × average object size"],
      ["Egress bandwidth", `${bytes(egress)}/s`, "read QPS × average object size (media usually via CDN)"],
      ["Cache memory", bytes(cache), `${v.hot}% of a day's read records (metadata, not media)`],
      ["App servers", `${servers} (+1 spare → ${servers + 1})`, `peak QPS ÷ ${num(v.cap)} per server, then N+1`],
    ];
    $("#est").innerHTML = cards.map(([k, val, f]) => `<div class="panel clay est-card"><span class="muted">${esc(k)}</span><b>${esc(val)}</b><code>${esc(f)}</code></div>`).join("");
  };
  view.addEventListener("input", (e) => {
    const k = e.target.id?.startsWith("f-") && e.target.id.slice(2);
    if (!k) return;
    const x = parseFloat(e.target.value);
    if (!Number.isFinite(x)) return;
    v[k] = x;
    draw();
  });
  view.addEventListener("click", (e) => {
    const p = e.target.closest("[data-preset]")?.dataset.preset;
    if (!p) return;
    v = { ...EST_PRESETS[p] };
    sync();
    draw();
  });
  sync();
  draw();
}
