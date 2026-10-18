import { $, $$, esc, send, toast } from "./util.js";
import { initControls } from "./controls.js";

const SECRET_KEY = "learnmotion-admin-secret";
const view = $("#adView");
let subjects = [];
let tab = "overview";
let selectedUser = null;

const KIND = { missing_topic: "Missing topic", content_error: "Content error", bug: "Bug", idea: "Idea", other: "Other" };
const STATUS = { open: "Open", in_progress: "In progress", resolved: "Resolved", wontfix: "Won't fix" };
const STATUS_PILL = { open: "neutral", in_progress: "warn", resolved: "ok", wontfix: "bad" };
const TAB_LABEL = { home: "Home page", learn: "Learn", lab: "Lab", playground: "Playground", interview: "Interview Prep", games: "Games" };
const EVENT_TYPES = { view_topic: "Opened topic", view_tab: "Opened tab", learned: "Marked learned", unlearned: "Unmarked", run_code: "Ran code", game_done: "Finished game", search: "Searched" };

const secret = () => sessionStorage.getItem(SECRET_KEY);
const call = (method, path, body) => send(method, path, body, { "X-Admin-Secret": secret() || "" });

function ago(iso) {
  if (!iso) return "never";
  const s = Math.max(0, (Date.now() - new Date(iso).getTime()) / 1000);
  if (s < 60) return "just now";
  if (s < 3600) return `${Math.floor(s / 60)}m ago`;
  if (s < 86400) return `${Math.floor(s / 3600)}h ago`;
  if (s < 86400 * 30) return `${Math.floor(s / 86400)}d ago`;
  return new Date(iso).toLocaleDateString();
}
const when = (iso) => (iso ? new Date(iso).toLocaleString() : "");
const subjectName = (sid) => subjects.find((s) => s.id === sid)?.name || sid || "";
const topicLink = (sid, topic, title) => (sid && topic ? `<a href="/#/${esc(sid)}/topic/${esc(topic)}" target="_blank" rel="noopener">${esc(title || topic)}</a>` : esc(title || topic || ""));

function describe(e) {
  const subj = e.subject ? ` <span class="muted">in ${esc(e.subject)}</span>` : "";
  switch (e.type) {
    case "view_topic": return `opened ${topicLink(e.sid, e.topic, e.topicTitle)}${subj}`;
    case "view_tab": return `opened <b>${esc(TAB_LABEL[e.detail] || e.detail || "a page")}</b>${subj}`;
    case "learned": return `marked ${topicLink(e.sid, e.topic, e.topicTitle)} as learned${subj}`;
    case "unlearned": return `unmarked ${topicLink(e.sid, e.topic, e.topicTitle)}${subj}`;
    case "run_code": return `ran <b>${esc(e.detail || "code")}</b>${e.topic ? ` on ${topicLink(e.sid, e.topic, e.topicTitle)}` : ""}${subj}`;
    case "game_done": return `finished game <b>${esc(e.detail || "")}</b>${subj}`;
    case "search": return `searched <b>"${esc(e.detail || "")}"</b>${e.topic ? ` and opened ${topicLink(e.sid, e.topic, e.topicTitle)}` : ""}`;
    default: return esc(e.type);
  }
}

function feedItem(e, showUser = true) {
  return `<li class="ad-feed-item"><span class="ad-dot t-${esc(e.type)}"></span><div>${showUser && e.user ? `<b class="ad-user-link" data-user="${esc(e.user.id)}">${esc(e.user.name)}</b> ` : ""}${describe(e)}<small class="muted">${esc(ago(e.createdAt))}</small></div></li>`;
}

function bars(series, key = "count", label = "") {
  const max = Math.max(1, ...series.map((p) => p[key]));
  const w = 100 / series.length;
  return `<svg class="ad-bars" viewBox="0 0 100 44" preserveAspectRatio="none" role="img" aria-label="${esc(label)}">
    ${series.map((p, i) => {
      const h = (p[key] / max) * 38;
      return `<rect x="${i * w + w * 0.15}" y="${42 - h}" width="${w * 0.7}" height="${Math.max(h, 0.6)}" rx="1.2"><title>${esc(p.date)}: ${p[key]}</title></rect>`;
    }).join("")}
  </svg>
  <div class="ad-bars-axis"><span>${esc(series[0]?.date.slice(5) || "")}</span><span>${esc(series.at(-1)?.date.slice(5) || "")}</span></div>`;
}

function stat(label, value, hint = "", tone = "") {
  return `<div class="ad-stat clay ${tone}"><small>${esc(label)}</small><b>${esc(value)}</b>${hint ? `<span class="muted">${esc(hint)}</span>` : ""}</div>`;
}

function table(head, rows, empty = "Nothing yet.") {
  if (!rows.length) return `<p class="muted ad-empty">${esc(empty)}</p>`;
  return `<div class="ad-table-wrap"><table class="ad-table"><thead><tr>${head.map((h) => `<th>${esc(h)}</th>`).join("")}</tr></thead><tbody>${rows.join("")}</tbody></table></div>`;
}

// ------------------------------------------------------------------ gate
function renderGate(error = "") {
  $("#adTabs").hidden = true;
  $("#adRefresh").hidden = true;
  $("#adLogout").hidden = true;
  view.innerHTML = `
    <form class="ad-gate clay" id="adGate">
      <h1>Admin panel</h1>
      <p class="muted">Enter the admin secret set in the server's <code>ADMIN_SECRET</code> environment variable. It stays in this browser tab only and is forgotten when you close it.</p>
      <label class="acct-field"><span>Admin secret</span><input type="password" name="secret" autocomplete="current-password" required></label>
      <p class="acct-error" role="alert" ${error ? "" : "hidden"}>${esc(error)}</p>
      <button type="submit" class="btn primary acct-submit">Unlock</button>
    </form>`;
  $("#adGate [name=secret]").focus();
  $("#adGate").onsubmit = async (event) => {
    event.preventDefault();
    sessionStorage.setItem(SECRET_KEY, event.target.secret.value);
    const res = await call("GET", "/api/admin/metrics");
    if (!res.ok) {
      sessionStorage.removeItem(SECRET_KEY);
      return renderGate(res.error || "Could not unlock.");
    }
    unlocked();
  };
}

function unlocked() {
  $("#adTabs").hidden = false;
  $("#adRefresh").hidden = false;
  $("#adLogout").hidden = false;
  show(tab);
}

async function guarded(path) {
  const res = await call("GET", path);
  if (res.status === 401 || res.status === 429) {
    sessionStorage.removeItem(SECRET_KEY);
    renderGate(res.error);
    return null;
  }
  if (!res.ok) {
    view.innerHTML = `<div class="panel clay">Could not load: ${esc(res.error || "unknown error")}</div>`;
    return null;
  }
  return res;
}

function show(next) {
  tab = next;
  $$("#adTabs button").forEach((b) => b.classList.toggle("on", b.dataset.tab === tab));
  ({ overview, users, activity, feedback, recovery })[tab]();
}

// ------------------------------------------------------------------ overview
async function overview() {
  const m = await guarded("/api/admin/metrics");
  if (!m) return;
  const t = m.totals;
  $("#adFbCount").textContent = t.feedbackOpen || "";
  $("#adRrCount").textContent = t.resetPending || "";
  view.innerHTML = `
    <div class="ad-stats">
      ${stat("Users", t.users, `${t.newUsers7} new this week`)}
      ${stat("Active today", t.activeToday)}
      ${stat("Active 7 days", t.active7)}
      ${stat("Topics learned", t.topicsLearned, "across all users")}
      ${stat("Actions 7 days", t.events7)}
      ${stat("Open feedback", t.feedbackOpen, `${t.feedbackTotal} total`, t.feedbackOpen ? "warn" : "")}
      ${stat("Reset requests", t.resetPending, "waiting for you", t.resetPending ? "bad" : "")}
    </div>
    <div class="ad-grid">
      <section class="panel clay"><h3>Sign-ups, last 14 days</h3>${bars(m.signups, "count", "Sign-ups per day")}</section>
      <section class="panel clay"><h3>Active learners per day</h3>${bars(m.activity, "activeUsers", "Active users per day")}</section>
      <section class="panel clay ad-wide"><h3>Subjects</h3>
        ${table(["Subject", "Learners", "Topics learned", "Visits (30d)"], m.subjects.map((s) => `<tr><td><b>${esc(s.name)}</b></td><td>${s.learners}</td><td>${s.learned}</td><td>${s.views30}</td></tr>`))}
      </section>
      <section class="panel clay"><h3>Most opened topics (30d)</h3>
        ${table(["Topic", "Subject", "Opens", "Users"], m.topViewed.map((r) => `<tr><td>${topicLink(r.sid, r.topic, r.title)}</td><td>${esc(r.subject)}</td><td>${r.views}</td><td>${r.users}</td></tr>`), "No topic views yet.")}
      </section>
      <section class="panel clay"><h3>Most learned topics</h3>
        ${table(["Topic", "Subject", "Learners"], m.topLearned.map((r) => `<tr><td>${topicLink(r.sid, r.topic, r.title)}</td><td>${esc(r.subject)}</td><td>${r.learners}</td></tr>`), "Nobody has marked a topic yet.")}
      </section>
      <section class="panel clay"><h3>Tabs people use (30d)</h3>
        ${table(["Tab", "Opens"], m.tabs.map((r) => `<tr><td>${esc(TAB_LABEL[r.tab] || r.tab)}</td><td>${r.views}</td></tr>`))}
      </section>
      <section class="panel clay"><h3>What people search for (30d)</h3>
        ${table(["Search", "Count"], m.searches.map((r) => `<tr><td>${esc(r.query)}</td><td>${r.count}</td></tr>`), "No searches yet.")}
      </section>
      <section class="panel clay ad-wide"><h3>Latest activity</h3>
        ${m.recent.length ? `<ul class="ad-feed clean">${m.recent.map((e) => feedItem(e)).join("")}</ul>` : `<p class="muted ad-empty">No activity yet.</p>`}
      </section>
    </div>
    <p class="muted ad-foot">Updated ${esc(when(m.generatedAt))}</p>`;
}

// ------------------------------------------------------------------ users
async function users(q = "") {
  const res = await guarded(`/api/admin/users?q=${encodeURIComponent(q)}`);
  if (!res) return;
  view.innerHTML = `
    <div class="ad-split">
      <section class="panel clay ad-users">
        <div class="ad-toolbar"><input type="text" id="adUserQ" placeholder="Search by name" value="${esc(q)}"><span class="muted">${res.users.length} shown</span></div>
        ${res.users.length ? `<ul class="clean ad-user-list">${res.users.map((u) => `
          <li><button type="button" class="ad-user ${u.id === selectedUser ? "on" : ""}" data-user="${esc(u.id)}">
            <span class="acct-avatar">${esc(u.name.split(/\s+/).filter(Boolean).slice(0, 2).map((w) => w[0].toUpperCase()).join(""))}</span>
            <span class="ad-user-main"><b>${esc(u.name)}</b><small class="muted">joined ${esc(ago(u.createdAt))} · seen ${esc(ago(u.lastSeenAt))}</small>
              <span class="ad-chips">${u.subjects.slice(0, 4).map((s) => `<span class="pill neutral">${esc(s.name)} ${s.learned}</span>`).join("")}</span></span>
            <span class="ad-user-num"><b>${u.learned}</b><small class="muted">learned</small></span>
          </button></li>`).join("")}</ul>` : `<p class="muted ad-empty">No users match.</p>`}
      </section>
      <section class="panel clay ad-detail" id="adDetail"><p class="muted ad-empty">Pick a user to see their progress, activity and feedback.</p></section>
    </div>`;
  let timer;
  $("#adUserQ").oninput = (event) => {
    clearTimeout(timer);
    timer = setTimeout(async () => {
      await users(event.target.value);
      const input = $("#adUserQ");
      input.focus();
      input.setSelectionRange(input.value.length, input.value.length);
    }, 300);
  };
  $$(".ad-user").forEach((b) => { b.onclick = () => openUser(b.dataset.user); });
  if (selectedUser && res.users.some((u) => u.id === selectedUser)) openUser(selectedUser);
}

async function openUser(id) {
  selectedUser = id;
  $$(".ad-user").forEach((b) => b.classList.toggle("on", b.dataset.user === id));
  const box = $("#adDetail");
  box.innerHTML = `<p class="muted">Loading…</p>`;
  const res = await guarded(`/api/admin/users/${encodeURIComponent(id)}`);
  if (!res) return;
  const u = res.user;
  box.innerHTML = `
    <div class="ad-detail-head">
      <div><h2>${esc(u.name)}</h2><p class="muted">Joined ${esc(when(u.createdAt))} · last seen ${esc(ago(u.lastSeenAt))}${res.lastVisit?.sid ? ` · last at ${topicLink(res.lastVisit.sid, res.lastVisit.topic, `${subjectName(res.lastVisit.sid)}${res.lastVisit.topic ? ` / ${res.lastVisit.topic}` : ""}`)}` : ""} · animation speed ${esc(res.settings?.animSpeed ?? 1)}×</p></div>
      <button type="button" class="btn small danger" id="adDelete">Delete user</button>
    </div>
    <h3>Progress</h3>
    ${res.progress.length ? res.progress.map((p) => `
      <details class="ad-prog">
        <summary><b>${esc(p.name)}</b><span class="ad-meter"><i style="width:${p.total ? Math.round((p.learned.length / p.total) * 100) : 0}%"></i></span><span class="muted">${p.learned.length} / ${p.total} learned · ${p.known} questions mastered</span></summary>
        <div class="ad-chips">${p.learned.map((t) => `<span class="pill ok">${topicLink(p.sid, t.id, t.title)}</span>`).join("") || `<span class="muted">No topics marked yet.</span>`}</div>
      </details>`).join("") : `<p class="muted">No progress synced yet.</p>`}
    <h3>Feedback (${res.feedback.length})</h3>
    ${res.feedback.length ? res.feedback.map((f) => `<div class="ad-mini clay"><span class="pill ${STATUS_PILL[f.status]}">${esc(STATUS[f.status])}</span> <b>${esc(KIND[f.kind] || f.kind)}</b> <small class="muted">${esc(ago(f.createdAt))}</small><p>${esc(f.message)}</p></div>`).join("") : `<p class="muted">No feedback from this user.</p>`}
    <h3>Recent activity</h3>
    ${res.events.length ? `<ul class="ad-feed clean">${res.events.map((e) => feedItem(e, false)).join("")}</ul>` : `<p class="muted">No activity yet.</p>`}`;
  $("#adDelete").onclick = async () => {
    if (!confirm(`Delete ${u.name} and all their progress, activity and feedback? This cannot be undone.`)) return;
    const del = await call("DELETE", `/api/admin/users/${encodeURIComponent(id)}`);
    if (!del.ok) return toast(del.error || "Delete failed", true);
    toast(`${u.name} deleted`);
    selectedUser = null;
    users($("#adUserQ")?.value || "");
  };
}

// ------------------------------------------------------------------ activity
async function activity(filters = {}) {
  const qs = new URLSearchParams({ limit: "300", ...Object.fromEntries(Object.entries(filters).filter(([, v]) => v)) });
  const res = await guarded(`/api/admin/events?${qs}`);
  if (!res) return;
  view.innerHTML = `
    <section class="panel clay">
      <div class="ad-toolbar">
        <select id="adType"><option value="">All actions</option>${Object.entries(EVENT_TYPES).map(([k, l]) => `<option value="${k}" ${filters.type === k ? "selected" : ""}>${esc(l)}</option>`).join("")}</select>
        <select id="adSid"><option value="">All subjects</option>${subjects.map((s) => `<option value="${esc(s.id)}" ${filters.sid === s.id ? "selected" : ""}>${esc(s.name)}</option>`).join("")}</select>
        <span class="muted">${res.events.length} most recent</span>
      </div>
      ${res.events.length ? `<ul class="ad-feed clean">${res.events.map((e) => feedItem(e)).join("")}</ul>` : `<p class="muted ad-empty">No activity matches.</p>`}
    </section>`;
  const refilter = () => activity({ type: $("#adType").value, sid: $("#adSid").value });
  $("#adType").onchange = refilter;
  $("#adSid").onchange = refilter;
}

// ------------------------------------------------------------------ feedback
async function feedback(status = "") {
  const res = await guarded(`/api/admin/feedback${status ? `?status=${status}` : ""}`);
  if (!res) return;
  const open = res.feedback.filter((f) => f.status === "open" || f.status === "in_progress").length;
  if (!status) $("#adFbCount").textContent = open || "";
  view.innerHTML = `
    <section class="panel clay">
      <div class="ad-toolbar">
        <select id="adFbStatus"><option value="">All feedback</option>${Object.entries(STATUS).map(([k, l]) => `<option value="${k}" ${status === k ? "selected" : ""}>${esc(l)}</option>`).join("")}</select>
        <span class="muted">${res.feedback.length} shown</span>
      </div>
      ${res.feedback.length ? `<div class="ad-fb-list">${res.feedback.map((f) => `
        <article class="ad-fb clay" data-id="${f.id}">
          <header class="row">
            <span class="pill ${STATUS_PILL[f.status]}">${esc(STATUS[f.status])}</span>
            <b>${esc(KIND[f.kind] || f.kind)}</b>
            <span class="muted">${esc(f.subject || "Whole app")}${f.topic ? ` · ${topicLink(f.sid, f.topic, f.topicTitle)}` : ""}</span>
            <span class="muted ad-fb-meta">from <b class="ad-user-link" data-user="${esc(f.user.id)}">${esc(f.user.name)}</b> · ${esc(ago(f.createdAt))}</span>
          </header>
          <p class="ad-fb-msg">${esc(f.message)}</p>
          ${f.page ? `<small class="muted">Sent from <a href="/${esc(f.page)}" target="_blank" rel="noopener">${esc(f.page)}</a></small>` : ""}
          <div class="ad-fb-actions">
            <select data-status>${Object.entries(STATUS).map(([k, l]) => `<option value="${k}" ${f.status === k ? "selected" : ""}>${esc(l)}</option>`).join("")}</select>
            <input type="text" data-note maxlength="1000" placeholder="Reply the user will see (optional)" value="${esc(f.adminNote || "")}">
            <button type="button" class="btn small primary" data-save>Save</button>
          </div>
        </article>`).join("")}</div>` : `<p class="muted ad-empty">No feedback here.</p>`}
    </section>`;
  $("#adFbStatus").onchange = (event) => feedback(event.target.value);
  $$(".ad-fb").forEach((card) => {
    card.querySelector("[data-save]").onclick = async () => {
      const res2 = await call("PATCH", `/api/admin/feedback/${card.dataset.id}`, {
        status: card.querySelector("[data-status]").value, note: card.querySelector("[data-note]").value,
      });
      if (!res2.ok) return toast(res2.error || "Save failed", true);
      toast("Feedback updated");
      feedback($("#adFbStatus").value);
    };
  });
}

// ------------------------------------------------------------------ recovery
async function recovery() {
  const res = await guarded("/api/admin/reset-requests");
  if (!res) return;
  const pending = res.requests.filter((r) => r.status === "pending").length;
  $("#adRrCount").textContent = pending || "";
  const answer = (label, value) => `<div><small class="muted">${esc(label)}</small><p>${value ? esc(value) : `<span class="muted">not answered</span>`}</p></div>`;
  view.innerHTML = `
    <section class="panel clay">
      <h3>Passphrase reset requests</h3>
      <p class="muted">Compare what the person wrote with what the account actually did. Approve only when it clearly matches; approving applies the passphrase they chose and signs out their other sessions.</p>
      ${res.requests.length ? `<div class="ad-fb-list">${res.requests.map((r) => `
        <article class="ad-rr clay" data-id="${r.id}">
          <header class="row"><span class="pill ${r.status === "pending" ? "warn" : r.status === "approved" ? "ok" : "bad"}">${esc(r.status)}</span><b class="ad-user-link" data-user="${esc(r.user.id)}">${esc(r.user.name)}</b><span class="muted">requested ${esc(ago(r.createdAt))} · joined ${esc(when(r.user.joined))} · seen ${esc(ago(r.user.lastSeenAt))}</span></header>
          <div class="ad-rr-cols">
            <div class="ad-rr-col"><h4>They say</h4>
              ${answer("Subjects", r.answers.subjects)}${answer("Topics", r.answers.topics)}${answer("Joined", r.answers.joined)}${answer("Note", r.answers.note)}
            </div>
            <div class="ad-rr-col"><h4>The account shows</h4>
              ${answer("Subjects with progress", r.truth.subjects.join(", "))}
              ${answer("Recently opened topics", r.truth.recentTopics.join(", "))}
              ${answer("Joined", when(r.user.joined))}
            </div>
          </div>
          ${r.status === "pending" ? `<div class="row"><button type="button" class="btn small success" data-act="approve">Approve</button><button type="button" class="btn small danger" data-act="reject">Reject</button></div>` : `<small class="muted">Resolved ${esc(ago(r.resolvedAt))}</small>`}
        </article>`).join("")}</div>` : `<p class="muted ad-empty">No reset requests.</p>`}
    </section>`;
  $$(".ad-rr [data-act]").forEach((b) => {
    b.onclick = async () => {
      const card = b.closest(".ad-rr");
      const action = b.dataset.act;
      if (action === "approve" && !confirm("Approve this reset? Their passphrase changes to the one they requested.")) return;
      const res2 = await call("POST", `/api/admin/reset-requests/${card.dataset.id}`, { action });
      if (!res2.ok) return toast(res2.error || "Failed", true);
      toast(`Request ${res2.status}`);
      recovery();
    };
  });
}

// ------------------------------------------------------------------ boot
view.addEventListener("click", (event) => {
  const link = event.target.closest(".ad-user-link");
  if (!link) return;
  selectedUser = link.dataset.user;
  show("users");
});
$("#adTabs").addEventListener("click", (event) => {
  const b = event.target.closest("button[data-tab]");
  if (b) show(b.dataset.tab);
});
$("#adRefresh").onclick = () => show(tab);
$("#adLogout").onclick = () => {
  sessionStorage.removeItem(SECRET_KEY);
  renderGate();
};

(async function boot() {
  initControls();
  const list = await send("GET", "/api/subjects");
  subjects = Array.isArray(list) ? list : Object.values(list).filter((v) => v && v.id);
  if (!secret()) return renderGate();
  const res = await call("GET", "/api/admin/metrics");
  if (!res.ok) {
    sessionStorage.removeItem(SECRET_KEY);
    return renderGate(res.status === 401 ? "" : res.error);
  }
  unlocked();
})();
