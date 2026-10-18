import { $, $$, api, esc } from "../util.js";
import { runSql, sqlResultHtml } from "../runners.js";
import { codeEditor, labHero, sampleOptions, takeHandoff } from "./common.js";

// ===================================================================== SQL playground
const DEFAULT_SQL = `-- Each run starts from a fresh copy of the shop database.
SELECT c.name, COUNT(o.id) AS orders
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id
GROUP BY c.id
ORDER BY orders DESC
LIMIT 5;`;

export function playground(view, content) {
  const samples = sampleOptions(content, ["sql"]);
  view.innerHTML = `
    ${labHero("SQL", "mint", "SQL Playground", "Real SQLite running on the server against a seeded shop: customers, products, orders, order_items, employees, accounts and 20,000 events. Every run gets a fresh copy, so experiment freely: inserts, indexes, transactions, EXPLAIN.")}
    <div class="lab-grid side-left" style="margin-top:1.2rem">
      <aside class="panel clay schema-panel"><h3>Schema</h3><div id="schema" class="muted">Loading…</div></aside>
      <div class="lab-main">
        <div class="panel clay">
          <div class="row">
            <select id="sample" style="max-width:100%;flex:1 1 260px"><option value="">Load a sample from the lessons…</option>${samples.map((s, i) => `<option value="${i}">${esc(s.label)}</option>`).join("")}</select>
            <label class="muted check"><input type="checkbox" id="explain"> Show query plans</label>
            <button class="btn primary" id="run">Run <kbd>⌘/Ctrl ↵</kbd></button>
          </div>
          <textarea id="sql" class="code-editor" spellcheck="false" rows="12"></textarea>
        </div>
        <div class="panel clay" id="out"><span class="muted">Results appear here.</span></div>
      </div>
    </div>`;
  const ta = $("#sql");
  ta.value = takeHandoff("sql-code") || DEFAULT_SQL;
  const run = async () => {
    $("#run").disabled = true;
    $("#out").innerHTML = `<span class="muted">Running…</span>`;
    const r = await runSql(ta.value, $("#explain").checked);
    $("#run").disabled = false;
    $("#out").innerHTML = sqlResultHtml(r);
  };
  codeEditor(ta, run);
  $("#run").onclick = run;
  $("#sample").onchange = (e) => {
    if (e.target.value !== "") ta.value = samples[+e.target.value].code;
  };
  api("/api/sql/schema").then((tables) => {
    if (!Array.isArray(tables)) return ($("#schema").textContent = "Schema unavailable.");
    $("#schema").innerHTML = tables.map((t) => `
      <details class="schema-table" ${["customers", "orders"].includes(t.name) ? "open" : ""}>
        <summary><b>${esc(t.name)}</b><span class="pill neutral">${t.rows.toLocaleString()}</span></summary>
        <ul class="clean">${t.columns.map((c) => `<li><code>${esc(c.name)}</code><span class="muted">${esc(c.type)}${c.pk ? " · PK" : ""}</span></li>`).join("")}</ul>
        <button class="btn small" data-peek="${esc(t.name)}">SELECT * …</button>
      </details>`).join("");
  });
  $("#schema").addEventListener("click", (e) => {
    const t = e.target.closest("[data-peek]")?.dataset.peek;
    if (!t) return;
    ta.value = `SELECT * FROM ${t} LIMIT 20;`;
    run();
  });
}

// ===================================================================== isolation lab (mini MVCC engine)
const LEVELS = [
  { id: "ru", name: "Read Uncommitted" },
  { id: "rc", name: "Read Committed" },
  { id: "rr", name: "Repeatable Read" },
  { id: "ser", name: "Serializable" },
];

class Mvcc {
  constructor(init, level) {
    this.level = level;
    this.clock = 1;
    this.versions = Object.fromEntries(Object.entries(init).map(([k, v]) => [k, [{ v, by: "init", committed: true, ts: 0 }]]));
    this.tx = {};
  }
  begin(t) {
    this.tx[t] = { snap: this.clock++, reads: new Set(), wrote: false, status: "active", seen: {} };
    return { text: `snapshot @${this.tx[t].snap}` };
  }
  visible(t, k) {
    const vs = (this.versions[k] || []).filter((v) => !v.aborted);
    const own = [...vs].reverse().find((v) => v.by === t);
    if (own) return own;
    const tx = this.tx[t];
    const pool = this.level === "ru" ? vs : vs.filter((v) => v.committed && (this.level === "rc" || v.ts < tx.snap));
    return pool[pool.length - 1];
  }
  read(t, k) {
    this.tx[t].reads.add(k);
    const v = this.visible(t, k);
    this.tx[t].seen[k] = v?.v;
    return { value: v?.v, text: v ? `sees ${v.v}${v.committed ? "" : " (uncommitted!)"}` : "no row" };
  }
  count(t, prefix, match) {
    const keys = Object.keys(this.versions).filter((k) => k.startsWith(prefix));
    keys.forEach((k) => this.tx[t].reads.add(k));
    this.tx[t].reads.add(`${prefix}*`);
    const n = keys.filter((k) => this.visible(t, k)?.v === match).length;
    return { value: n, text: `count = ${n}` };
  }
  write(t, k, value) {
    const tx = this.tx[t];
    if (["rr", "ser"].includes(this.level) && (this.versions[k] || []).some((v) => v.committed && v.by !== t && v.ts > tx.snap)) {
      return this.abort(t, "could not serialize access due to concurrent update");
    }
    const v = typeof value === "function" ? value(tx.seen) : value;
    (this.versions[k] ||= []).push({ v, by: t, committed: false });
    tx.wrote = true;
    return { text: `writes ${v}` };
  }
  commit(t) {
    const tx = this.tx[t];
    if (tx.status !== "active") return { text: "already finished" };
    if (this.level === "ser" && tx.wrote) {
      const conflict = [...tx.reads].some((k) => {
        const prefix = k.endsWith("*") ? k.slice(0, -1) : null;
        return Object.entries(this.versions).some(([key, vs]) => (prefix ? key.startsWith(prefix) : key === k) &&
          vs.some((v) => v.committed && v.by !== t && v.ts > tx.snap));
      });
      if (conflict) return this.abort(t, "serialization failure: a concurrent commit changed data you read");
    }
    const ts = this.clock++;
    Object.values(this.versions).forEach((vs) => vs.forEach((v) => { if (v.by === t && !v.committed && !v.aborted) Object.assign(v, { committed: true, ts }); }));
    tx.status = "committed";
    return { text: "COMMIT ok" };
  }
  rollback(t) {
    Object.values(this.versions).forEach((vs) => vs.forEach((v) => { if (v.by === t && !v.committed) v.aborted = true; }));
    this.tx[t].status = "rolled back";
    return { text: "ROLLBACK" };
  }
  abort(t, reason) {
    this.rollback(t);
    this.tx[t].status = "aborted";
    return { text: `ERROR: ${reason}`, abort: true };
  }
  committedValue(k) {
    const vs = (this.versions[k] || []).filter((v) => v.committed);
    return vs[vs.length - 1]?.v;
  }
}

const SCENARIOS = [
  {
    id: "dirty", title: "Dirty read", desc: "T2 reads a value T1 has not committed, and T1 then rolls back.",
    init: { "alice.balance": 100 },
    ops: [
      ["T1", "begin", "BEGIN;"], ["T2", "begin", "BEGIN;"],
      ["T1", "write", "UPDATE accounts SET balance = 999 WHERE owner = 'alice';", "alice.balance", 999],
      ["T2", "read", "SELECT balance FROM accounts WHERE owner = 'alice';", "alice.balance"],
      ["T1", "rollback", "ROLLBACK;"],
      ["T2", "commit", "COMMIT;"],
    ],
    judge: (log) => log[3].value === 999 ? [true, "T2 acted on 999, a balance that never officially existed."] : [false, "T2 only saw committed data (100)."],
  },
  {
    id: "nonrepeat", title: "Non-repeatable read", desc: "T1 reads the same row twice while T2 updates and commits it in between.",
    init: { "alice.balance": 100 },
    ops: [
      ["T1", "begin", "BEGIN;"], ["T2", "begin", "BEGIN;"],
      ["T1", "read", "SELECT balance FROM accounts WHERE owner = 'alice';", "alice.balance"],
      ["T2", "write", "UPDATE accounts SET balance = 200 WHERE owner = 'alice';", "alice.balance", 200],
      ["T2", "commit", "COMMIT;"],
      ["T1", "read", "SELECT balance FROM accounts WHERE owner = 'alice';", "alice.balance"],
      ["T1", "commit", "COMMIT;"],
    ],
    judge: (log) => log[2].value !== log[5].value ? [true, `T1 read ${log[2].value} then ${log[5].value} inside one transaction.`] : [false, `T1 saw ${log[2].value} both times: a stable snapshot.`],
  },
  {
    id: "phantom", title: "Phantom read", desc: "T1 counts pending orders twice; T2 inserts a new pending order in between.",
    init: { "order.1": "pending", "order.2": "pending", "order.3": "paid" },
    ops: [
      ["T1", "begin", "BEGIN;"], ["T2", "begin", "BEGIN;"],
      ["T1", "count", "SELECT COUNT(*) FROM orders WHERE status = 'pending';", "order.", "pending"],
      ["T2", "write", "INSERT INTO orders (id, status) VALUES (4, 'pending');", "order.4", "pending"],
      ["T2", "commit", "COMMIT;"],
      ["T1", "count", "SELECT COUNT(*) FROM orders WHERE status = 'pending';", "order.", "pending"],
      ["T1", "commit", "COMMIT;"],
    ],
    judge: (log) => log[2].value !== log[5].value ? [true, `A phantom row appeared: ${log[2].value} → ${log[5].value}.`] : [false, `Both counts were ${log[2].value}.`],
  },
  {
    id: "lost", title: "Lost update", desc: "Both transactions read the balance, compute in the app and write back. T1 adds 50, T2 subtracts 30.",
    init: { "alice.balance": 100 },
    ops: [
      ["T1", "begin", "BEGIN;"], ["T2", "begin", "BEGIN;"],
      ["T1", "read", "SELECT balance … -- app remembers it", "alice.balance"],
      ["T2", "read", "SELECT balance … -- app remembers it", "alice.balance"],
      ["T1", "write", "UPDATE accounts SET balance = :seen + 50 …;", "alice.balance", (seen) => seen["alice.balance"] + 50],
      ["T1", "commit", "COMMIT;"],
      ["T2", "write", "UPDATE accounts SET balance = :seen - 30 …;", "alice.balance", (seen) => seen["alice.balance"] - 30],
      ["T2", "commit", "COMMIT;"],
    ],
    judge: (log, db) => {
      const final = db.committedValue("alice.balance");
      if (db.tx.T2.status === "aborted") return [false, `T2 was aborted and must retry; balance stays ${final}. (Or use UPDATE … SET balance = balance - 30.)`];
      return final === 120 ? [false, "Final balance 120: both changes kept."] : [true, `Final balance ${final}, but it should be 120: T1's +50 was overwritten.`];
    },
  },
  {
    id: "skew", title: "Write skew", desc: "Rule: at least one doctor must be on call. Both doctors check the rule and go off call at the same time.",
    init: { "oncall.alice": "yes", "oncall.bob": "yes" },
    ops: [
      ["T1", "begin", "BEGIN;"], ["T2", "begin", "BEGIN;"],
      ["T1", "count", "SELECT COUNT(*) FROM doctors WHERE on_call; -- 2, ok to leave", "oncall.", "yes"],
      ["T2", "count", "SELECT COUNT(*) FROM doctors WHERE on_call; -- 2, ok to leave", "oncall.", "yes"],
      ["T1", "write", "UPDATE doctors SET on_call = false WHERE name = 'alice';", "oncall.alice", "no"],
      ["T2", "write", "UPDATE doctors SET on_call = false WHERE name = 'bob';", "oncall.bob", "no"],
      ["T1", "commit", "COMMIT;"],
      ["T2", "commit", "COMMIT;"],
    ],
    judge: (log, db) => {
      const n = ["oncall.alice", "oncall.bob"].filter((k) => db.committedValue(k) === "yes").length;
      return n === 0 ? [true, "Nobody is on call: each transaction's check was valid alone, but not together."] : [false, `${n} doctor still on call; the second transaction was aborted and must retry.`];
    },
  },
];

function simulate(sc, level, upto = sc.ops.length) {
  const db = new Mvcc(sc.init, level);
  const log = [];
  for (let k = 0; k < upto; k++) {
    const [t, op, , key, val] = sc.ops[k];
    const tx = db.tx[t];
    if (tx && tx.status !== "active" && op !== "begin") {
      log.push({ text: `skipped (${tx.status})`, skipped: true });
      continue;
    }
    log.push(op === "begin" ? db.begin(t) : op === "read" ? db.read(t, key) : op === "count" ? db.count(t, key, val) : op === "write" ? db.write(t, key, val) : op === "commit" ? db.commit(t) : db.rollback(t));
  }
  return { db, log };
}

export function lab(view) {
  let sc = SCENARIOS[0];
  let level = "rc";
  let step = 0;
  let timer;

  view.innerHTML = `
    ${labHero("ISO", "lilac", "Isolation Lab", "Two transactions race on the same rows. Pick an anomaly and an isolation level, then step through to see what each transaction sees, which row versions exist (MVCC) and whether the database prevents the anomaly.")}
    <div class="filters"><div class="tabs" id="scTabs">${SCENARIOS.map((s) => `<button data-s="${s.id}">${esc(s.title)}</button>`).join("")}</div></div>
    <div class="filters"><div class="tabs" id="lvTabs">${LEVELS.map((l) => `<button data-l="${l.id}">${esc(l.name)}</button>`).join("")}</div>
      <span class="spacer"></span>
      <button class="btn small" id="isoReset">Reset</button><button class="btn small" id="isoStep">Step</button><button class="btn small primary" id="isoPlay">Play</button>
    </div>
    <div class="panel clay"><p class="muted" id="scDesc" style="margin:0"></p></div>
    <div class="lab-grid side-right" style="margin-top:1.2rem">
      <div class="panel clay"><div class="tx-grid" id="txGrid"></div><div id="verdict"></div></div>
      <aside class="panel clay"><h3>Row versions</h3><div id="versions"></div><p class="muted" style="font-size:.78rem;margin-bottom:0">Uncommitted versions are dashed; rolled back versions are struck through. Under MVCC writers add versions instead of overwriting.</p></aside>
    </div>
    <div class="section-title"><h2>All levels at a glance</h2><span class="muted">computed by the same engine; models PostgreSQL, where Repeatable Read is a snapshot and so already blocks phantoms (the SQL standard would allow them)</span></div>
    <div class="panel clay res-table iso-matrix" id="matrix"></div>`;

  const draw = () => {
    $$("#scTabs button").forEach((b) => b.classList.toggle("active", b.dataset.s === sc.id));
    $$("#lvTabs button").forEach((b) => b.classList.toggle("active", b.dataset.l === level));
    $("#scDesc").textContent = sc.desc;
    const { db, log } = simulate(sc, level, step);
    $("#txGrid").innerHTML = `<div class="tx-h">T1</div><div class="tx-h">T2</div>` + sc.ops.map(([t, , sql], k) => {
      const res = log[k];
      const cls = k === step - 1 ? "cur" : k < step ? "done" : "todo";
      const cell = `<div class="tx-op ${cls}${res?.abort ? " bad" : ""}"><code>${esc(sql)}</code>${res ? `<span class="tx-res">${esc(res.text)}</span>` : ""}</div>`;
      return t === "T1" ? `${cell}<div class="tx-gap"></div>` : `<div class="tx-gap"></div>${cell}`;
    }).join("");
    $("#versions").innerHTML = Object.entries(db.versions).map(([k, vs]) => `
      <div class="ver-row"><code>${esc(k)}</code><div class="ver-list">${vs.map((v) => `<span class="ver ${v.aborted ? "aborted" : v.committed ? "committed" : "pending"}" title="${esc(v.by)}">${esc(v.v)}<small>${esc(v.by)}</small></span>`).join("")}</div></div>`).join("");
    if (step >= sc.ops.length) {
      const [bad, text] = sc.judge(log, db);
      $("#verdict").innerHTML = `<div class="bug-why ${bad ? "bad" : "good"}" style="margin-top:1rem"><b>${bad ? "Anomaly happened" : "Prevented"} under ${esc(LEVELS.find((l) => l.id === level).name)}.</b> ${esc(text)}</div>`;
    } else $("#verdict").innerHTML = "";
  };

  const matrix = () => {
    $("#matrix").innerHTML = `<table><thead><tr><th>Anomaly</th>${LEVELS.map((l) => `<th>${esc(l.name)}</th>`).join("")}</tr></thead><tbody>${SCENARIOS.map((s) => `<tr><td><b>${esc(s.title)}</b></td>${LEVELS.map((l) => {
      const { db, log } = simulate(s, l.id);
      const [bad] = s.judge(log, db);
      return `<td><span class="pill ${bad ? "bad" : "ok"}">${bad ? "possible" : "prevented"}</span></td>`;
    }).join("")}</tr>`).join("")}</tbody></table>`;
  };

  const stop = () => {
    clearInterval(timer);
    timer = null;
    $("#isoPlay").textContent = "Play";
  };
  $("#scTabs").onclick = (e) => {
    const s = SCENARIOS.find((x) => x.id === e.target.dataset.s);
    if (s) { sc = s; step = 0; stop(); draw(); }
  };
  $("#lvTabs").onclick = (e) => {
    if (e.target.dataset.l) { level = e.target.dataset.l; step = Math.min(step, sc.ops.length); draw(); }
  };
  $("#isoStep").onclick = () => { stop(); step = step >= sc.ops.length ? 0 : step + 1; draw(); };
  $("#isoReset").onclick = () => { stop(); step = 0; draw(); };
  $("#isoPlay").onclick = () => {
    if (timer) return stop();
    if (step >= sc.ops.length) step = 0;
    $("#isoPlay").textContent = "Pause";
    timer = setInterval(() => {
      step++;
      draw();
      if (step >= sc.ops.length) stop();
    }, 1100);
  };
  draw();
  matrix();
  return () => clearInterval(timer);
}
