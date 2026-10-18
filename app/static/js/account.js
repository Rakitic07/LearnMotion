import { $, copy, esc, send, store, toast } from "./util.js";
import { SPEED_MAX, SPEED_MIN, SPEED_PRESETS, animSpeed, clampSpeed, clearLocalSettings, formatSpeed, setLocalSettings } from "./settings.js";

const SYNC_RE = /^(learned|known-qs|game-best)(:[a-z0-9]{1,20})?$|^last-visit$/;
const LOWER_IS_BETTER = new Set(["crossword", "memory"]);
const FEEDBACK_KINDS = [
  ["missing_topic", "A topic is missing"],
  ["content_error", "Something in a lesson is wrong"],
  ["bug", "Something is broken"],
  ["idea", "Idea or request"],
  ["other", "Something else"],
];
const STATUS_LABEL = { open: "Open", in_progress: "In progress", resolved: "Resolved", wontfix: "Won't fix" };
const STATUS_PILL = { open: "neutral", in_progress: "warn", resolved: "ok", wontfix: "bad" };

let user = null;
let subjects = [];
let onChange = () => {};
let applying = false;
const dirty = new Set();
let pushTimer = null;
const queue = [];
let flushTimer = null;

export const currentUser = () => user;

function routeContext() {
  const [, sid = "", page = "", topic = ""] = location.hash.split("/");
  const known = subjects.some((s) => s.id === sid);
  return { sid: known ? sid : null, page: page || (known ? "learn" : "home"), topic: page === "topic" ? topic : null };
}

let nudged = false;

export function track(type, extra = {}) {
  if (!user) {
    if (type === "learned" && !nudged) {
      nudged = true;
      toast("Log in to save your learning progress");
    }
    return;
  }
  const ctx = routeContext();
  queue.push({ type, sid: extra.sid ?? ctx.sid, topic: extra.topic ?? ctx.topic, detail: extra.detail ?? null });
  if (queue.length >= 20) flush();
  else if (!flushTimer) flushTimer = setTimeout(flush, 8000);
}

function flush(keepalive = false) {
  clearTimeout(flushTimer);
  flushTimer = null;
  if (!user || !queue.length) return;
  const events = queue.splice(0, 40);
  fetch("/api/events", {
    method: "POST", keepalive,
    headers: { "Content-Type": "application/json", "X-K8s-Playground": "1" },
    body: JSON.stringify({ events }),
  }).catch(() => {});
}

function localSynced() {
  const out = {};
  for (const key of store.keys()) if (SYNC_RE.test(key)) out[key] = store.get(key);
  return out;
}

function mergeValue(key, local, remote) {
  if (local === undefined || local === null) return remote;
  if (remote === undefined || remote === null) return local;
  if (Array.isArray(local) || Array.isArray(remote)) return [...new Set([...(remote || []), ...(local || [])])];
  if (key.startsWith("game-best")) {
    const out = { ...remote };
    for (const [game, value] of Object.entries(local)) {
      const prev = out[game];
      out[game] = typeof prev !== "number" ? value : LOWER_IS_BETTER.has(game) ? Math.min(prev, value) : Math.max(prev, value);
    }
    return out;
  }
  return local;
}

async function syncDown() {
  const res = await send("GET", "/api/me/progress");
  if (!res.ok) return;
  const remote = res.data || {};
  const local = localSynced();
  const merged = {};
  for (const key of new Set([...Object.keys(remote), ...Object.keys(local)])) merged[key] = mergeValue(key, local[key], remote[key]);
  applying = true;
  for (const [key, value] of Object.entries(merged)) store.set(key, value);
  applying = false;
  if (Object.keys(merged).length) await send("POST", "/api/me/progress", { data: merged });
}

function schedulePush() {
  clearTimeout(pushTimer);
  pushTimer = setTimeout(async () => {
    if (!user || !dirty.size) return;
    const data = {};
    for (const key of dirty) data[key] = store.get(key, null);
    dirty.clear();
    const res = await send("POST", "/api/me/progress", { data });
    if (!res.ok && res.status === 401) setUser(null);
  }, 1200);
}

window.addEventListener("lm:store", (event) => {
  const key = event.detail?.key;
  if (applying || !user || !SYNC_RE.test(key)) return;
  dirty.add(key);
  schedulePush();
});
document.addEventListener("visibilitychange", () => { if (document.visibilityState === "hidden") flush(true); });

function setUser(next) {
  user = next;
  renderTopbar();
  document.dispatchEvent(new CustomEvent("lm:auth-state", { detail: { authenticated: Boolean(next) } }));
}

function initials(name) {
  return name.split(/\s+/).filter(Boolean).slice(0, 2).map((w) => w[0].toUpperCase()).join("");
}

function renderTopbar() {
  const slot = $("#acct");
  if (!slot) return;
  const chat = $("#chatOpen");
  if (chat) chat.hidden = !user;
  if (!user) {
    slot.innerHTML = `<button type="button" class="btn small primary acct-login" id="acctLogin" title="Log in to save your learning progress">Log in</button>`;
    $("#acctLogin").onclick = () => openAuth("login");
    return;
  }
  slot.innerHTML = `
    <button type="button" class="acct-feedback clay" id="acctFeedback" title="Send feedback">
      <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/><path d="M8 9h8M8 13h5"/></svg>
      <span class="acct-label">Feedback</span>
    </button>
    <div class="acct-wrap">
      <button type="button" class="acct-chip clay" id="acctChip" aria-haspopup="true" aria-expanded="false" title="${esc(user.name)}">
        <span class="acct-avatar">${esc(initials(user.name))}</span><span class="acct-name">${esc(user.name)}</span>
      </button>
      <div class="acct-menu clay" id="acctMenu" hidden>
        <div class="acct-menu-head"><b>${esc(user.name)}</b><small class="muted">Progress syncs to your account</small></div>
        <button type="button" data-act="feedback">Send feedback</button>
        <button type="button" data-act="mine">My feedback</button>
        <button type="button" data-act="settings">Settings</button>
        <button type="button" data-act="logout">Log out</button>
      </div>
    </div>`;
  $("#acctFeedback").onclick = () => openFeedback();
  const chip = $("#acctChip");
  const menu = $("#acctMenu");
  chip.onclick = () => {
    menu.hidden = !menu.hidden;
    chip.setAttribute("aria-expanded", String(!menu.hidden));
  };
  menu.onclick = (event) => {
    const act = event.target.closest("button")?.dataset.act;
    menu.hidden = true;
    if (act === "feedback") openFeedback();
    if (act === "mine") openFeedback("mine");
    if (act === "settings") openSettings();
    if (act === "logout") logout();
  };
}
document.addEventListener("click", (event) => {
  const menu = $("#acctMenu");
  if (!menu || menu.hidden || event.composedPath().some((n) => n.classList?.contains("acct-wrap"))) return;
  menu.hidden = true;
  $("#acctChip")?.setAttribute("aria-expanded", "false");
});

async function logout() {
  flush();
  await send("POST", "/api/auth/logout", {});
  setUser(null);
  for (const key of store.keys()) if (SYNC_RE.test(key)) store.remove(key);
  clearLocalSettings();
  toast("Logged out. Progress on this device was cleared; it is safe in your account.");
  onChange();
}

// ------------------------------------------------------------------ dialog shell
function dialog() {
  let root = $("#acctDialog");
  if (!root) {
    root = document.createElement("div");
    root.id = "acctDialog";
    root.className = "acct-backdrop";
    root.hidden = true;
    root.innerHTML = `<div class="acct-panel clay" role="dialog" aria-modal="true" aria-labelledby="acctTitle"><button type="button" class="acct-x" aria-label="Close">×</button><div class="acct-body"></div></div>`;
    document.body.append(root);
    root.addEventListener("mousedown", (event) => { if (event.target === root) closeDialog(); });
    root.querySelector(".acct-x").onclick = closeDialog;
    document.addEventListener("keydown", (event) => { if (event.key === "Escape" && !root.hidden) closeDialog(); });
  }
  return root;
}

function show(html, focusSel = "input, textarea, select, button.primary") {
  const root = dialog();
  root.querySelector(".acct-body").innerHTML = html;
  root.hidden = false;
  document.body.classList.add("gs-locked");
  requestAnimationFrame(() => root.querySelector(`.acct-body ${focusSel}`)?.focus());
  return root.querySelector(".acct-body");
}

function closeDialog() {
  const root = $("#acctDialog");
  if (!root) return;
  root.hidden = true;
  document.body.classList.remove("gs-locked");
}

function field(label, input, hint = "") {
  return `<label class="acct-field"><span>${label}</span>${input}${hint ? `<small class="muted">${hint}</small>` : ""}</label>`;
}

const nameInput = (value = "") => `<input type="text" name="name" autocomplete="username" maxlength="40" required placeholder="e.g. Raktim" value="${esc(value)}">`;
const passInput = (name = "passphrase", auto = "current-password") => `<input type="password" name="${name}" autocomplete="${auto}" minlength="6" maxlength="64" required placeholder="At least 6 characters">`;

function busy(form, on) {
  form.querySelectorAll("button, input, textarea, select").forEach((el) => { el.disabled = on; });
}

function formError(form, msg) {
  const box = form.querySelector(".acct-error");
  box.textContent = msg || "";
  box.hidden = !msg;
}

function bindForm(body, handler) {
  const form = body.querySelector("form");
  form.onsubmit = async (event) => {
    event.preventDefault();
    formError(form, "");
    const data = Object.fromEntries(new FormData(form));
    busy(form, true);
    try {
      await handler(data, form);
    } finally {
      if (form.isConnected) busy(form, false);
    }
  };
  return form;
}

// ------------------------------------------------------------------ auth views
export function openAuth(mode = "login", name = "") {
  const isLogin = mode === "login";
  const body = show(`
    <h2 id="acctTitle">${isLogin ? "Welcome back" : "Create your account"}</h2>
    <p class="muted acct-sub">${isLogin ? "Log in to save your learning progress and pick it up on any device." : "Sign up to save your learning progress. Just a name and a passphrase, no email needed."}</p>
    <div class="acct-tabs" role="tablist">
      <button type="button" role="tab" class="${isLogin ? "on" : ""}" data-mode="login" aria-selected="${isLogin}">Log in</button>
      <button type="button" role="tab" class="${isLogin ? "" : "on"}" data-mode="register" aria-selected="${!isLogin}">Sign up</button>
    </div>
    <form class="acct-form" novalidate>
      ${field("Your name", nameInput(name))}
      ${field("Passphrase", passInput("passphrase", isLogin ? "current-password" : "new-password"), isLogin ? "" : "At least 6 characters. Pick something you will remember.")}
      <p class="acct-error" role="alert" hidden></p>
      <button type="submit" class="btn primary acct-submit">${isLogin ? "Log in" : "Create account"}</button>
      ${isLogin ? `<button type="button" class="acct-link" data-go="forgot">Forgot your passphrase?</button>` : ""}
    </form>`);
  body.querySelectorAll("[data-mode]").forEach((b) => { b.onclick = () => openAuth(b.dataset.mode, body.querySelector("[name=name]").value); });
  body.querySelector("[data-go=forgot]")?.addEventListener("click", () => openForgot(body.querySelector("[name=name]").value));
  bindForm(body, async (data, form) => {
    const res = await send("POST", isLogin ? "/api/auth/login" : "/api/auth/register", data);
    if (!res.ok) return formError(form, res.error || "Something went wrong.");
    await signedIn(res.user);
    if (res.recoveryCode) showRecoveryCode(res.recoveryCode, "Save your recovery code", "This is the only time it is shown. If you forget your passphrase, this code lets you reset it yourself.");
    else {
      closeDialog();
      toast(`Welcome back, ${res.user.name}`);
    }
  });
}

async function loadSettings() {
  const res = await send("GET", "/api/me/settings");
  if (res.ok) setLocalSettings(res.settings);
}

async function signedIn(next) {
  setUser(next);
  await Promise.all([syncDown(), loadSettings()]);
  track("view_tab", { detail: routeContext().page });
  onChange();
}

function showRecoveryCode(code, title, text) {
  const body = show(`
    <h2 id="acctTitle">${title}</h2>
    <p class="muted acct-sub">${text}</p>
    <div class="acct-code"><code>${esc(code)}</code><button type="button" class="btn small" data-copy>Copy</button></div>
    <label class="acct-check"><input type="checkbox" data-ack> <span>I saved this code somewhere safe</span></label>
    <button type="button" class="btn primary acct-submit" data-done disabled>Continue</button>`, "[data-copy]");
  body.querySelector("[data-copy]").onclick = () => copy(code);
  body.querySelector("[data-ack]").onchange = (event) => { body.querySelector("[data-done]").disabled = !event.target.checked; };
  body.querySelector("[data-done]").onclick = closeDialog;
}

function openForgot(name = "") {
  const body = show(`
    <h2 id="acctTitle">Reset your passphrase</h2>
    <p class="muted acct-sub">Pick the option that fits.</p>
    <div class="acct-options">
      <button type="button" class="acct-option clay" data-go="code"><b>I have my recovery code</b><span class="muted">Reset instantly with the code shown when you signed up.</span></button>
      <button type="button" class="acct-option clay" data-go="admin"><b>Ask the admin to reset it</b><span class="muted">Lost the code too? Send a request; the admin verifies and approves it.</span></button>
      <button type="button" class="acct-option clay" data-go="status"><b>Check a request I sent</b><span class="muted">Use the ticket you got after sending a request.</span></button>
    </div>
    <button type="button" class="acct-link" data-go="back">Back to log in</button>`, ".acct-option");
  const go = { code: () => openRecoverCode(name), admin: () => openAdminRequest(name), status: () => openStatus(name), back: () => openAuth("login", name) };
  body.querySelectorAll("[data-go]").forEach((b) => { b.onclick = go[b.dataset.go]; });
}

function openRecoverCode(name) {
  const body = show(`
    <h2 id="acctTitle">Use your recovery code</h2>
    <form class="acct-form" novalidate>
      ${field("Your name", nameInput(name))}
      ${field("Recovery code", `<input type="text" name="recoveryCode" autocomplete="one-time-code" maxlength="40" required placeholder="XXXX-XXXX-XXXX-XXXX" class="acct-mono">`)}
      ${field("New passphrase", passInput("passphrase", "new-password"), "At least 6 characters.")}
      <p class="acct-error" role="alert" hidden></p>
      <button type="submit" class="btn primary acct-submit">Reset and log in</button>
      <button type="button" class="acct-link" data-go="back">Other options</button>
    </form>`);
  body.querySelector("[data-go=back]").onclick = () => openForgot(body.querySelector("[name=name]").value);
  bindForm(body, async (data, form) => {
    const res = await send("POST", "/api/auth/recover", data);
    if (!res.ok) return formError(form, res.error || "Could not reset.");
    await signedIn(res.user);
    showRecoveryCode(res.recoveryCode, "You're back in", "Your old recovery code no longer works. Here is your new one; save it.");
  });
}

function openAdminRequest(name) {
  const body = show(`
    <h2 id="acctTitle">Ask the admin to reset it</h2>
    <p class="muted acct-sub">Your new passphrase only takes effect after the admin approves. Answer what you can so they can tell it is really you.</p>
    <form class="acct-form" novalidate>
      ${field("Your name", nameInput(name))}
      ${field("New passphrase", passInput("passphrase", "new-password"), "Applied only after approval.")}
      ${field("Subjects you study", `<input type="text" name="subjects" maxlength="300" placeholder="e.g. Kubernetes, Databases">`)}
      ${field("Topics you learned or opened recently", `<input type="text" name="topics" maxlength="300" placeholder="e.g. HPA, SQL joins">`)}
      ${field("Roughly when you signed up", `<input type="text" name="joined" maxlength="300" placeholder="e.g. October 2026">`)}
      ${field("Anything else (optional)", `<textarea name="note" rows="2" maxlength="300" placeholder="Extra context that helps the admin verify you"></textarea>`)}
      <p class="acct-error" role="alert" hidden></p>
      <button type="submit" class="btn primary acct-submit">Send request</button>
      <button type="button" class="acct-link" data-go="back">Other options</button>
    </form>`);
  body.querySelector("[data-go=back]").onclick = () => openForgot(body.querySelector("[name=name]").value);
  bindForm(body, async (data, form) => {
    const { name: n, passphrase, ...questionnaire } = data;
    const res = await send("POST", "/api/auth/reset-request", { name: n, passphrase, questionnaire });
    if (!res.ok) return formError(form, res.error || "Could not send the request.");
    const done = show(`
      <h2 id="acctTitle">Request sent</h2>
      <p class="muted acct-sub">Keep this ticket. Use it under "Check a request I sent" to see when the admin approves; then log in with your new passphrase.</p>
      <div class="acct-code"><code>${esc(res.ticket)}</code><button type="button" class="btn small" data-copy>Copy</button></div>
      <button type="button" class="btn primary acct-submit" data-done>Done</button>`, "[data-copy]");
    done.querySelector("[data-copy]").onclick = () => copy(res.ticket);
    done.querySelector("[data-done]").onclick = () => openAuth("login", n);
  });
}

function openStatus(name) {
  const body = show(`
    <h2 id="acctTitle">Check your request</h2>
    <form class="acct-form" novalidate>
      ${field("Your name", nameInput(name))}
      ${field("Ticket", `<input type="text" name="ticket" maxlength="40" required placeholder="XXXX-XXXX-XXXX" class="acct-mono">`)}
      <p class="acct-error" role="alert" hidden></p>
      <div class="acct-status" hidden></div>
      <button type="submit" class="btn primary acct-submit">Check status</button>
      <button type="button" class="acct-link" data-go="back">Other options</button>
    </form>`);
  body.querySelector("[data-go=back]").onclick = () => openForgot(body.querySelector("[name=name]").value);
  bindForm(body, async (data, form) => {
    const res = await send("POST", "/api/auth/reset-status", data);
    const box = form.querySelector(".acct-status");
    if (!res.ok) {
      box.hidden = true;
      return formError(form, res.error || "Not found.");
    }
    const msg = {
      pending: "Still waiting for the admin. Check back later.",
      approved: "Approved. Log in with the new passphrase you chose.",
      rejected: "The admin could not verify this request. Send a new one with more details.",
    }[res.status];
    box.innerHTML = `<span class="pill ${res.status === "approved" ? "ok" : res.status === "rejected" ? "bad" : "warn"}">${esc(res.status)}</span> ${esc(msg)}`;
    box.hidden = false;
    if (res.status === "approved") {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "btn small primary";
      btn.textContent = "Log in now";
      btn.onclick = () => openAuth("login", data.name);
      box.append(" ", btn);
    }
  });
}

// ------------------------------------------------------------------ feedback
export function openFeedback(view = "new") {
  if (!user) return openAuth("login");
  const ctx = routeContext();
  const tabs = `<div class="acct-tabs" role="tablist">
      <button type="button" role="tab" class="${view === "new" ? "on" : ""}" data-view="new" aria-selected="${view === "new"}">Send feedback</button>
      <button type="button" role="tab" class="${view === "mine" ? "on" : ""}" data-view="mine" aria-selected="${view === "mine"}">My feedback</button>
    </div>`;
  if (view === "mine") return openMyFeedback(tabs);
  const subjectOptions = [`<option value="">Whole app</option>`, ...subjects.map((s) => `<option value="${esc(s.id)}" ${s.id === ctx.sid ? "selected" : ""}>${esc(s.name)}</option>`)].join("");
  const body = show(`
    <h2 id="acctTitle">Tell us what to improve</h2>
    <p class="muted acct-sub">Missing a topic, spotted a mistake or something broke? The admin reads every message.</p>
    ${tabs}
    <form class="acct-form" novalidate>
      ${field("What is it about?", `<select name="kind">${FEEDBACK_KINDS.map(([v, l]) => `<option value="${v}">${esc(l)}</option>`).join("")}</select>`)}
      ${field("Subject", `<select name="sid">${subjectOptions}</select>`)}
      ${ctx.topic ? `<label class="acct-check"><input type="checkbox" name="withTopic" checked> <span>About this topic: <b>${esc(ctx.topic)}</b></span></label>` : ""}
      ${field("Message", `<textarea name="message" rows="5" maxlength="2000" required placeholder="e.g. Please add a topic on Kafka consumer groups"></textarea>`)}
      <p class="acct-error" role="alert" hidden></p>
      <button type="submit" class="btn primary acct-submit">Send feedback</button>
    </form>`, "select");
  body.querySelectorAll("[data-view]").forEach((b) => { b.onclick = () => openFeedback(b.dataset.view); });
  bindForm(body, async (data, form) => {
    const payload = { kind: data.kind, sid: data.sid || null, topic: data.withTopic ? ctx.topic : null, message: data.message, page: location.hash || "#/" };
    const res = await send("POST", "/api/feedback", payload);
    if (!res.ok) return formError(form, res.error || "Could not send.");
    toast("Thanks! Your feedback reached the admin.");
    openFeedback("mine");
  });
}

async function openMyFeedback(tabs) {
  const body = show(`<h2 id="acctTitle">My feedback</h2>${tabs}<div class="acct-list"><p class="muted">Loading…</p></div>`, "[data-view=new]");
  body.querySelectorAll("[data-view]").forEach((b) => { b.onclick = () => openFeedback(b.dataset.view); });
  const res = await send("GET", "/api/me/feedback");
  const list = body.querySelector(".acct-list");
  if (!res.ok) {
    list.innerHTML = `<p class="acct-error">${esc(res.error || "Could not load.")}</p>`;
    return;
  }
  const kind = Object.fromEntries(FEEDBACK_KINDS);
  const subjectName = (sid) => subjects.find((s) => s.id === sid)?.name || "Whole app";
  list.innerHTML = res.feedback.length ? res.feedback.map((f) => `
    <article class="acct-fb clay">
      <div class="row"><span class="pill ${STATUS_PILL[f.status]}">${esc(STATUS_LABEL[f.status] || f.status)}</span><small class="muted">${esc(kind[f.kind] || f.kind)} · ${esc(subjectName(f.sid))}${f.topic ? ` · ${esc(f.topic)}` : ""} · ${esc(new Date(f.createdAt).toLocaleDateString())}</small></div>
      <p>${esc(f.message)}</p>
      ${f.adminNote ? `<p class="acct-reply"><b>Admin:</b> ${esc(f.adminNote)}</p>` : ""}
    </article>`).join("") : `<p class="muted">You have not sent any feedback yet.</p>`;
}

// ------------------------------------------------------------------ settings
export function openSettings() {
  if (!user) return openAuth("login");
  const current = animSpeed();
  const body = show(`
    <h2 id="acctTitle">Settings</h2>
    <p class="muted acct-sub">Saved to your account, so they follow you to every device.</p>
    <form class="acct-form" novalidate>
      <div class="acct-field">
        <span>Animation speed</span>
        <div class="acct-speed">
          <input type="range" name="range" min="${SPEED_MIN}" max="${SPEED_MAX}" step="0.05" value="${current}" aria-label="Animation speed slider">
          <label class="acct-speed-num"><input type="number" name="speed" min="${SPEED_MIN}" max="${SPEED_MAX}" step="0.05" value="${current}" aria-label="Animation speed"><span>×</span></label>
        </div>
        <div class="acct-presets">${SPEED_PRESETS.map((p) => `<button type="button" data-speed="${p}" class="${p === current ? "on" : ""}">${formatSpeed(p)}</button>`).join("")}</div>
        <small class="muted">Applies to every animated walkthrough. Pick any value from ${formatSpeed(SPEED_MIN)} (slowest) to ${formatSpeed(SPEED_MAX)} (fastest).</small>
      </div>
      <p class="acct-error" role="alert" hidden></p>
      <button type="submit" class="btn primary acct-submit">Save settings</button>
    </form>`, "[name=range]");
  const range = body.querySelector("[name=range]");
  const num = body.querySelector("[name=speed]");
  const mark = (v) => {
    body.querySelectorAll("[data-speed]").forEach((b) => b.classList.toggle("on", +b.dataset.speed === v));
  };
  const paint = () => range.dispatchEvent(new Event("input", { bubbles: true }));
  range.addEventListener("input", () => { num.value = range.value; mark(+range.value); });
  num.addEventListener("input", () => {
    if (num.value !== "" && +num.value >= SPEED_MIN && +num.value <= SPEED_MAX) {
      range.value = num.value;
      range.style.setProperty("--fill", `${((+num.value - SPEED_MIN) / (SPEED_MAX - SPEED_MIN)) * 100}%`);
    }
    mark(+num.value);
  });
  body.querySelector(".acct-presets").onclick = (event) => {
    const b = event.target.closest("[data-speed]");
    if (!b) return;
    range.value = b.dataset.speed;
    paint();
  };
  paint();
  bindForm(body, async (data, form) => {
    const speed = Number(data.speed);
    if (data.speed === "" || !Number.isFinite(speed) || speed < SPEED_MIN || speed > SPEED_MAX) {
      return formError(form, `Animation speed must be between ${formatSpeed(SPEED_MIN)} and ${formatSpeed(SPEED_MAX)}.`);
    }
    const res = await send("POST", "/api/me/settings", { settings: { animSpeed: clampSpeed(speed) } });
    if (!res.ok) return formError(form, res.error || "Could not save settings.");
    setLocalSettings(res.settings);
    closeDialog();
    toast(`Animation speed set to ${formatSpeed(res.settings.animSpeed)}`);
  });
}

// ------------------------------------------------------------------ boot
export async function initAccount(subjectList, { onChange: changed } = {}) {
  subjects = subjectList;
  onChange = changed || onChange;
  renderTopbar();
  const res = await send("GET", "/api/auth/me");
  if (res.authenticated && res.user) {
    setUser(res.user);
    await Promise.all([syncDown(), loadSettings()]);
  } else if (res.status === 200) {
    clearLocalSettings();
  }
}
