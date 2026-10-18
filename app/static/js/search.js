// Global topic search: a command palette opened from the topbar, Cmd/Ctrl+K or "/".
// Picking a result routes to that subject's Learn page for the exact topic.
import { $, api, esc, levelPill } from "./util.js";
import { subjectIcon } from "./icons.js";
import { track } from "./account.js";

const MAX_RESULTS = 40;
let index = null;
let loading = null;
let subjects = [];
let staticRoot = "";
let results = [];
let cursor = 0;

const norm = (s) => String(s || "").toLowerCase().normalize("NFKD").replace(/[\u0300-\u036f]/g, "");
const numberWords = new Map(Object.entries({ zero: "0", one: "1", two: "2", three: "3", four: "4", five: "5", six: "6", seven: "7", eight: "8", nine: "9", ten: "10", eleven: "11", twelve: "12", thirteen: "13", fourteen: "14", fifteen: "15", sixteen: "16", seventeen: "17", eighteen: "18", nineteen: "19", twenty: "20" }));
const STOP_WORDS = new Set("a an the and or but if then than of to in on at by for from with about into onto is are was were be been being do does did can could would should i me my we our you your they it its this that these those what whats which who whom why how where when as it s m re t don just please need want looking find show teach explain understand basics through vs more many much very also best way ways get getting have all any example examples topic topics lesson lessons learn learning something things thing too".split(" "));
const SYNONYM_SETS = [
  ["build", "create", "make", "write", "implement", "configure"],
  ["deploy", "deployment", "release", "rollout", "publish", "apply", "run", "execute"],
  ["delete", "remove", "destroy", "cleanup", "teardown", "decommission"],
  ["slow", "sluggish", "laggy", "latency", "performance"],
  ["fast", "faster", "quick", "speed", "improve", "improvement", "enhance", "optimize", "optimization"],
  ["website", "webpage", "webapp", "site", "page"],
  ["url", "address", "link", "uri"],
  ["error", "failure", "fail", "broken", "crash", "troubleshoot", "debug"],
  ["login", "logon", "signin", "authenticate", "authentication", "identity"],
  ["scale", "scaling", "autoscale", "capacity"],
  ["traffic", "requests", "request", "load"],
  ["increase", "grow", "growing", "expand", "expansion"],
  ["sound", "audio", "hear", "listen", "play"],
  ["notes", "note", "pitch", "pitches", "tone", "tones"],
  ["handle", "support", "serve", "process", "manage"],
  ["beginner", "intro", "introductory", "basic", "foundations"],
  ["intermediate", "mid-level"],
  ["advanced", "expert", "production"],
];
const SYNONYMS = new Map();
for (const group of SYNONYM_SETS) for (const word of group) SYNONYMS.set(word, group);
const QUERY_INTENTS = [
  { test: (q) => /\b(browser|website|webpage|url|address bar)\b/.test(q) && /\b(type|enter|paste|open|visit|load|happens|happen)\b/.test(q), ids: ["browser-url-request-lifecycle"] },
  { test: (q) => /\b(users?|customers?|traffic|requests?)\b/.test(q) && /\b(handle|support|serve|grow|growing|increase|increasing|more)\b/.test(q), ids: ["scalability", "load-balancing"] },
];
// Treat punctuation such as hyphens as word boundaries, and make common spelled
// numbers equivalent to their digit form ("Three-tier" and "3-tier").
const searchable = (s) => norm(s)
  .replace(/[\u2010-\u2015-]/g, " ")
  .replace(/[^a-z0-9]+/g, " ")
  .replace(/\b(zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty)\b/g, (word) => numberWords.get(word))
  .trim().replace(/\s+/g, " ");
const tokens = (q) => searchable(q).split(" ").filter((word) => word && !STOP_WORDS.has(word));

function variantsFor(word) {
  const variants = new Set([word, ...(SYNONYMS.get(word) || [])]);
  if (word.length > 4 && word.endsWith("ies")) variants.add(`${word.slice(0, -3)}y`);
  if (word.length > 4 && word.endsWith("s")) variants.add(word.slice(0, -1));
  if (word.length > 5 && word.endsWith("ing")) {
    const base = word.slice(0, -3); variants.add(base); variants.add(`${base}e`);
  }
  if (word.length > 4 && word.endsWith("ed")) variants.add(word.slice(0, -2));
  return [...variants].map(searchable).filter(Boolean);
}

function closeEnough(a, b) {
  if (a === b) return true;
  if (Math.abs(a.length - b.length) > 1 || Math.min(a.length, b.length) < 5) return false;
  if (a.length === b.length) {
    const mismatches = [];
    for (let i = 0; i < a.length; i++) if (a[i] !== b[i]) mismatches.push(i);
    if (mismatches.length === 2) {
      const [left, right] = mismatches;
      if (right === left + 1 && a[left] === b[right] && a[right] === b[left]) return true;
    }
  }
  let i = 0; let j = 0; let edits = 0;
  while (i < a.length && j < b.length) {
    if (a[i] === b[j]) { i++; j++; continue; }
    if (++edits > 1) return false;
    if (a.length > b.length) i++;
    else if (b.length > a.length) j++;
    else { i++; j++; }
  }
  return edits + (i < a.length || j < b.length ? 1 : 0) <= 1;
}

async function loadIndex() {
  if (index) return index;
  loading ??= api("/api/search-index").then((rows) => {
    index = (Array.isArray(rows) ? rows : []).map((r) => ({
      ...r,
      _title: searchable(r.title), _id: searchable(r.id), _tag: searchable(r.tagline),
      _cat: searchable(r.category), _subj: searchable(`${r.subject} ${r.sid}`), _level: searchable(r.level), _terms: searchable(r.terms),
      _lexical: [...new Set(`${searchable(r.title)} ${searchable(r.id)} ${searchable(r.tagline)} ${searchable(r.category)} ${searchable(`${r.subject} ${r.sid}`)}`.split(" ").filter((w) => w.length >= 5))],
    }));
    return index;
  }).finally(() => { loading = null; });
  return loading;
}

function score(r, words, phrase) {
  let total = 0;
  if (r._title === phrase) total += 120;
  else if (r._title.startsWith(phrase)) total += 70;
  else if (r._title.includes(phrase)) total += 45;
  for (const w of words) {
    const variants = variantsFor(w);
    const hasWord = (field, candidate) => (` ${field} `).includes(` ${candidate} `);
    let hit = 0;
    for (const v of variants) {
      if (hasWord(r._title, v)) hit = Math.max(hit, 25);
      else if (r._title.includes(v)) hit = Math.max(hit, 17);
      if (hasWord(r._id, v)) hit = Math.max(hit, 15);
      if (hasWord(r._tag, v)) hit = Math.max(hit, 10);
      if (hasWord(r._cat, v)) hit = Math.max(hit, 7);
      if (hasWord(r._subj, v)) hit = Math.max(hit, 6);
      if (hasWord(r._level, v)) hit = Math.max(hit, 8);
      if (hasWord(r._terms, v)) hit = Math.max(hit, 4);
    }
    if (!hit) {
      const typo = r._lexical.some((indexed) => variants.some((v) => closeEnough(v, indexed)));
      if (typo) hit = 3;
    }
    if (!hit) return null;
    total += hit;
  }
  return total - r._title.length * 0.08;
}

function starterResults() {
  return subjects.map((s) => index.find((r) => r.sid === s.id && r.id === s.start) || index.find((r) => r.sid === s.id)).filter(Boolean);
}

function smartSearch(q) {
  const words = tokens(q);
  if (!words.length) return starterResults();
  const phrase = words.join(" ");
  const intentIds = QUERY_INTENTS.filter((intent) => intent.test(searchable(q))).flatMap((intent) => intent.ids);
  return index.map((r) => {
    const relevance = score(r, words, phrase);
    const intentBoost = intentIds.includes(r.id) ? 110 : 0;
    return [relevance === null && !intentBoost ? null : (relevance || 0) + intentBoost, r];
  })
    .filter(([n]) => n !== null)
    .sort((a, b) => b[0] - a[0] || a[1].title.localeCompare(b[1].title)).slice(0, MAX_RESULTS).map(([, r]) => r);
}

function basicSearch(q) {
  const words = [...new Set(searchable(q).split(" ").filter(Boolean))];
  if (!words.length) return starterResults();
  return index.map((r) => {
    const fields = [r._title, r._id, r._tag, r._cat, r._subj, r._level, r._terms];
    let total = 0;
    for (const word of words) {
      const fieldIndex = fields.findIndex((field) => (` ${field} `).includes(` ${word} `));
      const partialIndex = fieldIndex < 0 ? fields.findIndex((field) => field.includes(word)) : -1;
      const hit = fieldIndex >= 0 ? fieldIndex : partialIndex;
      if (hit < 0) return null;
      total += hit === 0 ? 25 : hit === 1 ? 18 : hit === 2 ? 10 : 4;
    }
    return [total - r._title.length * .08, r];
  }).filter(Boolean).sort((a, b) => b[0] - a[0] || a[1].title.localeCompare(b[1].title))
    .slice(0, MAX_RESULTS).map(([, r]) => r);
}

function search(q) {
  return $("#gsSmart").checked ? smartSearch(q) : basicSearch(q);
}

function mark(text, words) {
  let html = esc(text);
  for (const w of words.filter((x) => x.length > 1).sort((a, b) => b.length - a.length)) {
    html = html.replace(new RegExp(`(${esc(w).replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})(?![^<]*>)`, "gi"), "<mark>$1</mark>");
  }
  return html;
}

function render() {
  const q = $("#gsInput").value;
  const smart = $("#gsSmart").checked;
  const words = smart ? tokens(q) : searchable(q).split(" ").filter(Boolean);
  const list = $("#gsList");
  $("#gsHint").textContent = words.length
    ? `${results.length}${results.length === MAX_RESULTS ? "+" : ""} matching topic${results.length === 1 ? "" : "s"} across ${new Set(results.map((r) => r.sid)).size} subject(s)${smart ? " · plain-English, synonym and typo aware" : ""}`
    : `Start here in any subject, or search ${index.length} topics${smart ? " · smart matching runs locally" : ""}`;
  if (!results.length) {
    list.innerHTML = `<li class="gs-empty">No topic matches "${esc(q)}". Try fewer or shorter words.</li>`;
    return;
  }
  list.innerHTML = results.map((r, i) => {
    const s = subjects.find((x) => x.id === r.sid);
    return `<li role="option" id="gs-opt-${i}" aria-selected="${i === cursor}" class="gs-item${i === cursor ? " on" : ""}" data-i="${i}">
      <span class="gs-icon">${subjectIcon(s, staticRoot)}</span>
      <span class="gs-text"><b>${mark(r.title, words)}</b><small>${mark(r.tagline, words)}</small></span>
      <span class="gs-meta"><span class="gs-subj">${esc(r.subject)}</span>${levelPill(r.level)}</span>
    </li>`;
  }).join("");
  $("#gsInput").setAttribute("aria-activedescendant", `gs-opt-${cursor}`);
  list.querySelector(".gs-item.on")?.scrollIntoView({ block: "nearest" });
}

function setCursor(i, scroll) {
  cursor = i;
  for (const li of $("#gsList").querySelectorAll(".gs-item")) {
    const on = +li.dataset.i === i;
    li.classList.toggle("on", on);
    li.setAttribute("aria-selected", on);
    if (on && scroll) li.scrollIntoView({ block: "nearest" });
  }
  $("#gsInput").setAttribute("aria-activedescendant", `gs-opt-${i}`);
}

function update() {
  results = search($("#gsInput").value);
  cursor = 0;
  render();
}

function go(r) {
  if (!r) return;
  track("search", { sid: r.sid, topic: r.id, detail: $("#gsInput").value.trim().slice(0, 80) || r.title });
  close();
  location.hash = `#/${r.sid}/topic/${r.id}`;
}

export async function open(prefill = "") {
  const dlg = $("#gsDialog");
  if (!dlg.hidden) return;
  dlg.hidden = false;
  document.body.classList.add("gs-locked");
  const input = $("#gsInput");
  input.value = prefill;
  input.focus();
  $("#gsList").innerHTML = `<li class="gs-empty">Loading topics…</li>`;
  await loadIndex();
  if (!dlg.hidden) update();
}

export function close() {
  $("#gsDialog").hidden = true;
  document.body.classList.remove("gs-locked");
  $("#gsOpen")?.focus({ preventScroll: true });
}

export function initSearch(subjectList, root) {
  subjects = subjectList;
  staticRoot = root;
  const isMac = /Mac|iPhone|iPad/.test(navigator.platform);
  $("#gsKbd").textContent = isMac ? "⌘K" : "Ctrl K";
  $("#gsOpen").addEventListener("click", () => open());
  try { $("#gsSmart").checked = localStorage.getItem("learnmotion-smart-search") === "on"; } catch { /* use the default off state */ }
  $("#gsSmart").addEventListener("change", (e) => {
    try { localStorage.setItem("learnmotion-smart-search", e.currentTarget.checked ? "on" : "off"); } catch { /* search still works without storage */ }
    if (index) update();
  });
  $("#gsDialog").addEventListener("click", (e) => { if (e.target.id === "gsDialog") close(); });
  $("#gsClose").addEventListener("click", close);
  $("#gsInput").addEventListener("input", () => index && update());
  $("#gsInput").addEventListener("keydown", (e) => {
    if (e.key === "ArrowDown" || e.key === "ArrowUp") {
      e.preventDefault();
      if (!results.length) return;
      setCursor((cursor + (e.key === "ArrowDown" ? 1 : -1) + results.length) % results.length, true);
    } else if (e.key === "Enter") {
      e.preventDefault();
      go(results[cursor]);
    } else if (e.key === "Escape") {
      close();
    }
  });
  $("#gsList").addEventListener("click", (e) => {
    const item = e.target.closest(".gs-item");
    if (item) go(results[+item.dataset.i]);
  });
  $("#gsList").addEventListener("pointermove", (e) => {
    const item = e.target.closest(".gs-item");
    if (item && +item.dataset.i !== cursor) setCursor(+item.dataset.i, false);
  });
  document.addEventListener("keydown", (e) => {
    const typing = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement?.tagName) || document.activeElement?.isContentEditable;
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
      e.preventDefault();
      $("#gsDialog").hidden ? open() : close();
    } else if (e.key === "/" && !typing && $("#gsDialog").hidden) {
      e.preventDefault();
      open();
    } else if (e.key === "Escape" && !$("#gsDialog").hidden) {
      close();
    }
  });
}
