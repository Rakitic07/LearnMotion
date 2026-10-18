import { $, $$, api, copy, esc, highlightCode, highlightYaml, levelPill, prose, store, toast } from "./util.js";
import { renderLanding } from "./landing.js";
import { appLogo, subjectIcon } from "./icons.js";
import { initControls } from "./controls.js";
import { initSearch } from "./search.js";
import { initChat, setChatContext } from "./chat.js";
import { initAccount, track } from "./account.js";

const view = $("#view");
const nav = $("#nav");
const STATIC = new URL($('link[rel="stylesheet"]').href).pathname.replace(/css\/[^/]+$/, "");
let subjects = [];
let S = null;
let content;
let cleanup = () => {};
let routeToken = 0;
const contentCache = new Map();

nav.addEventListener("click", (event) => {
  if (!event.target.closest(".subject-option")) return;
  $$("#nav details[open]").forEach((menu) => { menu.open = false; });
});
document.addEventListener("click", (event) => {
  $$("#nav details[open]").forEach((menu) => {
    if (!menu.contains(event.target)) menu.open = false;
  });
});
document.addEventListener("keydown", (event) => {
  if (event.key !== "Escape") return;
  const openMenus = $$("#nav details[open]");
  openMenus.forEach((menu) => { menu.open = false; });
  openMenus[0]?.querySelector("summary")?.focus();
});

const learnedKey = (sid) => (sid === "k8s" ? "learned" : `learned:${sid}`);
export const learned = {
  all: (sid = S?.id) => new Set(store.get(learnedKey(sid), [])),
  toggle(id) {
    const s = learned.all();
    s.has(id) ? s.delete(id) : s.add(id);
    store.set(learnedKey(S.id), [...s]);
    updateProgress();
    track(s.has(id) ? "learned" : "unlearned", { sid: S.id, topic: id });
    return s.has(id);
  },
};
const learnedCount = (sid) => learned.all(sid).size;

const EXAMPLE_HINT = {
  k8s: "basic → advanced, all runnable on the Kind playground",
  db: "basic → advanced · SQL runs here against a fresh copy of the shop database",
  sysdesign: "basic → advanced · Python snippets run in a sandbox, tweak the numbers",
  git: "basic → advanced · runnable scripts replay in the Git Sandbox",
  python: "basic → advanced · run here or step through in the Code Visualizer",
  aws: "basic → advanced · copy-ready; JSON policies open in the IAM evaluator",
  linux: "basic → advanced · runnable ones replay in the Shell Sandbox",
  java: "basic → advanced · check the minimum Java version of any snippet",
  cicd: "basic → advanced · copy-ready pipeline configs; scripts open in the Pipeline Builder",
  dsa: "basic → advanced · Python solutions run here or step through in the Code Visualizer",
  qa: "basic → advanced · Python tests run here; open them in the Test Runner",
  ds: "basic → advanced · pure-Python analysis runs here; tweak the data and re-run",
  ml: "basic → advanced · tiny models train right here in pure Python",
};

function updateProgress() {
  const chip = $("#progressChip");
  if (S && content) chip.textContent = `${learnedCount(S.id)} / ${content.topics.length} learned`;
  else chip.textContent = `${subjects.reduce((n, s) => n + learnedCount(s.id), 0)} / ${subjects.reduce((n, s) => n + s.topics, 0)} learned`;
}

function setSubject(s) {
  S = s;
  document.documentElement.dataset.subject = s ? s.id : "";
  const brandLogo = $("#brandLogo");
  brandLogo.innerHTML = s ? subjectIcon(s, STATIC) : appLogo(subjects, STATIC);
  brandLogo.classList.toggle("spin", Boolean(s));
  $("#brandName").innerHTML = `<b>Learn</b>Motion`;
  $("#brand").href = "#/";
  document.title = s ? `${s.name} · LearnMotion — learn ${s.name} visually` : "LearnMotion — interactive, animated, interview-ready";
  const groupedSubjects = Object.groupBy ? Object.groupBy(subjects, (x) => x.domain || "Technology & Engineering") : subjects.reduce((groups, x) => {
    (groups[x.domain || "Technology & Engineering"] ||= []).push(x);
    return groups;
  }, {});
  const subjectLinks = Object.entries(groupedSubjects).map(([group, items]) => `<div class="subject-group-title">${esc(group)}</div>${items.map((x) => `<a class="subject-option${x.id === s?.id ? " current" : ""}" href="#/${x.id}"${x.id === s?.id ? ' aria-current="page"' : ""}>${esc(x.name)}</a>`).join("")}`).join("");
  const subjectMenu = `<details class="subject-menu">
    <summary><span class="subject-menu-name">${s ? esc(s.name) : "Subjects"}</span></summary>
    <div class="subject-menu-panel">${subjectLinks}</div>
  </details>`;
  $("#nav").innerHTML = s
    ? `${subjectMenu}
       <a href="#/${s.id}" data-route="learn">Learn</a>
       <a href="#/${s.id}/lab" data-route="lab">${esc(s.tabs.lab)}</a>
       <a href="#/${s.id}/playground" data-route="playground">${esc(s.tabs.playground)}</a>
       <details class="subject-menu more-menu">
         <summary>More</summary>
         <div class="subject-menu-panel">
           <a class="subject-option" href="#/${s.id}/interview" data-route="interview">Interview Prep</a>
           <a class="subject-option" href="#/${s.id}/games" data-route="games">Games</a>
         </div>
       </details>`
    : subjectMenu;
  fitNav();
}

// Tab labels differ per subject, so wrap the nav when it no longer fits beside the controls.
const topbar = $(".topbar");
function fitNav() {
  topbar.classList.remove("nav-wrap");
  if (nav.scrollWidth > nav.clientWidth + 1) topbar.classList.add("nav-wrap");
}
let fitFrame = 0;
const queueFit = () => {
  cancelAnimationFrame(fitFrame);
  fitFrame = requestAnimationFrame(fitNav);
};
new ResizeObserver(queueFit).observe($(".topbar-right"));
window.addEventListener("resize", queueFit);
document.fonts?.ready.then(queueFit);

const catColor = (id) => content.categories.find((c) => c.id === id)?.color || "slate";
const base = () => `#/${S.id}`;

// ------------------------------------------------------------------ subject home
function renderHome(initialLevel = "all") {
  const done = learned.all();
  const totalQs = content.topics.reduce((n, t) => n + t.interview.length, 0) + content.scenarios.length;
  const k8s = S.id === "k8s";
  const blobs = S.blobs || content.topics.slice(0, 4).map((t) => t.title.split(/[\s&,]+/)[0]);
  view.innerHTML = `
    <section class="hero clay" style="--s1:${S.art[0]};--s2:${S.art[1]}">
      <div>
        <span class="pill neutral">Basic → Advanced · Interview-ready</span>
        <h1 style="margin-top:.8rem">${esc(S.headline[0])} <span>${esc(S.headline[1])}</span></h1>
        <p class="muted" style="font-size:1.05rem">${S.blurb}</p>
        <div class="row" style="margin-top:1rem">
          <a class="btn primary" href="${base()}/topic/${S.start}">Start learning</a>
          <a class="btn" href="${base()}/lab">Try the ${esc(S.tabs.lab)}</a>
          <a class="btn" href="${base()}/playground">Open ${esc(S.tabs.playground)}</a>
        </div>
        <div class="stats">
          <div class="stat clay tint-sky"><b>${content.topics.length}</b>concepts</div>
          <div class="stat clay tint-mint"><b>${k8s ? content.labs.length : content.categories.length}</b>${k8s ? "hands-on labs" : "learning tracks"}</div>
          <div class="stat clay tint-peach"><b>${totalQs}</b>interview Qs</div>
          <div class="stat clay tint-lilac"><b>${k8s ? content.presets.length : 5}</b>${k8s ? "scheduler puzzles" : "mini games"}</div>
        </div>
      </div>
      <div class="hero-art" aria-hidden="true">
        ${blobs.map((b, i) => `<div class="blob b${i + 1}">${esc(b)}</div>`).join("")}
      </div>
    </section>
    <div class="filters">
      <input type="text" id="search" placeholder="Search ${esc(S.name)} topics…">
      <div class="tabs" id="levelTabs">
        ${["all", "beginner", "basic", "intermediate", "advanced"].map((l) => `<button data-l="${l}" class="${l === initialLevel ? "active" : ""}">${l}</button>`).join("")}
      </div>
    </div>
    <div id="cats"></div>`;

  const draw = () => {
    const q = $("#search").value.toLowerCase();
    const lvl = $("#levelTabs .active").dataset.l;
    if (lvl === "beginner") {
      const guide = S.beginner;
      const guideText = guide ? `${S.name} ${guide.what} ${guide.why} ${guide.example} ${guide.start}`.toLowerCase() : "";
      const intro = guide && (!q || guideText.includes(q)) ? [
        ["What is this subject?", guide.what],
        ["Why do we need it?", guide.why],
        ["A simple example", guide.example],
        ["Where should I start?", guide.start],
      ].map(([front, back]) => `<details class="beginner-flashcard beginner-intro-card clay"><summary><span class="beginner-card-kicker">${esc(S.name)} · getting started</span><strong>${esc(front)}</strong><span class="beginner-flip-hint">Tap to reveal</span></summary><div class="beginner-flashcard-back"><p>${prose(back)}</p></div></details>`).join("") : "";
      const foundations = content.topics.filter((t) => t.level === "basic" &&
        (!q || `${t.title} ${t.tagline} ${t.id} ${t.what} ${t.analogy}`.toLowerCase().includes(q)));
      const lessonCards = foundations.map((t) => {
        const basicQA = t.interview?.find((item) => item.level === "basic");
        const question = basicQA?.q || `What is ${t.title}?`;
        return `<details class="beginner-flashcard lesson-flashcard clay"><summary><span class="beginner-card-kicker">${esc(t.title)}</span><strong>${esc(question)}</strong><span class="beginner-flip-hint">Tap to reveal</span></summary><div class="beginner-flashcard-back"><p>${basicQA ? prose(basicQA.a) : prose(t.what || t.tagline)}</p>${t.analogy ? `<p><b>Picture it:</b> ${prose(t.analogy)}</p>` : ""}<a class="btn small" href="${base()}/topic/${encodeURIComponent(t.id)}">Open full lesson →</a></div></details>`;
      }).join("");
      const sections = `${intro ? `<section class="beginner-deck-section"><div class="category-head"><span class="category-dot tint-sky"></span><h2 style="margin:0">Start with the idea</h2><span class="muted">What ${esc(S.name)} is and why it matters</span></div><div class="beginner-deck">${intro}</div></section>` : ""}${lessonCards ? `<section class="beginner-deck-section"><div class="category-head"><span class="category-dot tint-mint"></span><h2 style="margin:0">Beginner lesson flashcards</h2><span class="muted">${foundations.length} foundational lessons · tap a card to reveal it</span></div><div class="beginner-deck">${lessonCards}</div></section>` : ""}`;
      $("#cats").innerHTML = sections || `<div class="panel clay muted">No beginner cards match this search.</div>`;
      return;
    }
    $("#cats").innerHTML = content.categories.map((cat) => {
      const topics = content.topics.filter((t) => t.category === cat.id && (lvl === "all" || t.level === lvl) &&
        (!q || `${t.title} ${t.tagline} ${t.id}`.toLowerCase().includes(q)));
      if (!topics.length) return "";
      return `<section class="category">
        <div class="category-head"><span class="category-dot tint-${cat.color}"></span><h2 style="margin:0">${esc(cat.title)}</h2><span class="muted">${esc(cat.blurb)}</span></div>
        <div class="topic-grid">${topics.map((t) => `
          <div class="lift-slot"><a class="topic-card clay spot" href="${base()}/topic/${t.id}">
            ${done.has(t.id) ? `<span class="pill ok done-badge">learned</span>` : ""}
            <div class="code tint-${cat.color}">${esc(t.code)}</div>
            <h4>${esc(t.title)}</h4>
            <p>${esc(t.tagline)}</p>
            <div class="row">${levelPill(t.level)}${t.simulate ? `<span class="pill neutral">simulator</span>` : ""}${k8s && content.labs.some((l) => l.topic === t.id) ? `<span class="pill neutral">lab</span>` : ""}${t.examples?.some((e) => e.runnable && (["sql", "python"].includes(e.lang) || (S.id === "linux" && e.lang === "bash"))) ? `<span class="pill neutral">runnable</span>` : ""}</div>
          </a></div>`).join("")}</div>
      </section>`;
    }).join("") || `<div class="panel clay muted">No topics match.</div>`;
  };
  $("#search").addEventListener("input", draw);
  $("#levelTabs").addEventListener("click", (e) => {
    if (!e.target.dataset.l) return;
    $$("#levelTabs button").forEach((b) => b.classList.toggle("active", b === e.target));
    draw();
  });
  draw();
}

// ------------------------------------------------------------------ topic
function exampleActions(t, ex) {
  const acts = [`<button class="btn small" data-ex="copy">Copy</button>`];
  if (S.id === "k8s") {
    acts.push(`<button class="btn small primary" data-ex="kind">Try in Kind playground</button>`);
    if (t.simulate) acts.push(`<button class="btn small" data-ex="sim">Run in Scheduler Lab</button>`);
    return acts.join("");
  }
  if (ex.runnable && ex.lang === "sql") acts.push(`<button class="btn small primary" data-ex="run">Run here</button>`, `<button class="btn small" data-ex="sqlpg">Open in SQL Playground</button>`);
  if (ex.runnable && ex.lang === "python") acts.push(`<button class="btn small primary" data-ex="run">Run here</button>`, `<button class="btn small" data-ex="pyviz">Visualize step by step</button>`, `<button class="btn small" data-ex="pyrun">Open in Python Runner</button>`);
  if (ex.runnable && S.id === "git" && ex.lang === "bash") acts.push(`<button class="btn small primary" data-ex="git">Replay in Git Sandbox</button>`);
  if (S.id === "aws" && ex.lang === "json" && /"Statement"/.test(ex.code) && !/sts:AssumeRole/.test(ex.code)) acts.push(`<button class="btn small primary" data-ex="iam">Evaluate in IAM lab</button>`);
  if (ex.runnable && S.id === "linux" && ex.lang === "bash") acts.push(`<button class="btn small primary" data-ex="sh">Run in Shell Sandbox</button>`);
  if (ex.lang === "java") acts.push(`<button class="btn small primary" data-ex="javaver">Check minimum Java version</button>`);
  return acts.join("");
}

async function renderTopic(id, token) {
  const t = content.topics.find((x) => x.id === id);
  if (!t) {
    view.innerHTML = `<div class="panel clay">Topic not found. <a href="${base()}">Back</a></div>`;
    return;
  }
  const [sceneModule, scenesModule, widgetsModule, flowModule, runners] = await Promise.all([
    import("./scene.js"), import("./scenes.js"), import("./widgets.js"), import("./flow.js"), import("./runners.js"),
  ]);
  if (token !== routeToken) return;
  const { ScenePlayer } = sceneModule;
  const { SCENES } = scenesModule;
  const { WIDGETS } = widgetsModule;
  const { FlowPlayer } = flowModule;
  const { pyResultHtml, runPython, runSql, sqlResultHtml } = runners;
  store.set("last-visit", { sid: S.id, topic: t.id });
  const k8s = S.id === "k8s";
  const color = catColor(t.category);
  const idx = content.topics.indexOf(t);
  const prev = content.topics[idx - 1];
  const next = content.topics[idx + 1];
  const lab = k8s && content.labs.find((l) => l.topic === t.id);
  const isDone = learned.all().has(t.id);

  view.innerHTML = `
    <section class="topic-hero clay">
      <div class="code tint-${color}">${esc(t.code)}</div>
      <div>
        <div class="row" style="margin-bottom:.4rem">${levelPill(t.level)}<span class="pill neutral">${esc(content.categories.find((c) => c.id === t.category)?.title)}</span><span class="pill neutral">${esc(S.name)}</span></div>
        <h1>${prose(t.title)}</h1>
        <div class="muted">${prose(t.tagline)}</div>
      </div>
      <div class="row">
        <button class="btn ${isDone ? "success" : ""}" id="learnBtn">${isDone ? "Learned" : "Mark as learned"}</button>
      </div>
    </section>
    <div class="analogy clay"><div class="bulb">Aha</div><p><b>Real-life analogy:</b> ${prose(t.analogy)}</p></div>
    <div id="sceneMount"></div>
    <div id="widgetMount"></div>
    <div class="grid three" style="margin-top:1.4rem">
      <div class="panel clay"><h3>What it is</h3><p>${prose(t.what)}</p></div>
      <div class="panel clay"><h3>Real-world usage</h3><ul class="clean ticks">${t.use_cases.map((u) => `<li>${prose(u)}</li>`).join("")}</ul></div>
      <div class="panel clay"><h3>Key points</h3><ul class="clean ticks">${t.key_points.map((u) => `<li>${prose(u)}</li>`).join("")}</ul></div>
    </div>

    <div class="section-title"><h2>Examples</h2><span class="muted">${esc(EXAMPLE_HINT[S.id] || "basic → advanced")}</span></div>
    <div class="panel clay">
      <div class="row">
        <div class="tabs" id="exTabs">${t.examples.map((e, i) => `<button data-i="${i}" class="${i ? "" : "active"}">${esc(e.title)}</button>`).join("")}</div>
      </div>
      <div id="exBody"></div>
    </div>

    <div class="grid two" style="margin-top:1.4rem">
      <div class="panel clay"><h3>${esc(S.cheat)}</h3><ul class="clean cmd-list">${t.commands.map((c) => `<li><code>${esc(c)}</code><button class="btn small" data-copy="${esc(c)}">Copy</button></li>`).join("")}</ul></div>
      <div class="panel clay"><h3>Gotchas</h3><ul class="clean ticks warn">${t.gotchas.map((g) => `<li>${prose(g)}</li>`).join("")}</ul>
        ${lab ? `<div class="lab-step" style="margin-top:1rem"><b>Hands-on lab:</b> ${esc(lab.title)}<p class="muted" style="margin:.3rem 0 .6rem">${esc(lab.goal)}</p><a class="btn small primary" href="#/k8s/playground?lab=${lab.id}">Open lab in playground</a></div>` : ""}
        ${t.simulate ? `<div class="lab-step"><b>Scheduler puzzle</b><p class="muted" style="margin:.3rem 0 .6rem">See filter and score decisions for this concept, node by node.</p><a class="btn small" href="#/k8s/lab?preset=${t.simulate}">Open in Scheduler Lab</a></div>` : ""}
        ${k8s ? "" : `<div class="lab-step" style="margin-top:1rem"><b>Practice it</b><p class="muted" style="margin:.3rem 0 .6rem">Make it stick with the hands-on tools for ${esc(S.name)}.</p><div class="row"><a class="btn small primary" href="${base()}/lab">${esc(S.tabs.lab)}</a><a class="btn small" href="${base()}/playground">${esc(S.tabs.playground)}</a><a class="btn small" href="${base()}/games">Games</a></div></div>`}
      </div>
    </div>

    <div class="section-title"><h2>Interview questions</h2><span class="muted">${t.interview.length} questions</span></div>
    ${t.interview.map((q) => `<details class="qa clay"><summary>${levelPill(q.level)} ${esc(q.q)}</summary><div class="answer">${esc(q.a)}</div></details>`).join("")}

    ${t.related?.length ? `<div class="section-title"><h2>Related</h2></div><div class="row">${t.related.map((r) => {
      const rt = content.topics.find((x) => x.id === r);
      return rt ? `<a class="btn small" href="${base()}/topic/${rt.id}">${esc(rt.title)}</a>` : "";
    }).join("")}</div>` : ""}

    <div class="pager">
      ${prev ? `<a class="btn" href="${base()}/topic/${prev.id}">← ${esc(prev.title)}</a>` : "<span></span>"}
      ${next ? `<a class="btn primary" href="${base()}/topic/${next.id}">${esc(next.title)} →</a>` : "<span></span>"}
    </div>`;

  let player;
  const musicSubject = ["music", "theory", "guitar", "piano", "drums", "violin", "voice"].includes(S.id);
  if (k8s && SCENES[t.scene]) player = new ScenePlayer($("#sceneMount"), { steps: SCENES[t.scene] });
  else if (t.flow && !musicSubject) player = new FlowPlayer($("#sceneMount"), t.flow);
  if (t.widget && WIDGETS[t.widget] && !musicSubject) WIDGETS[t.widget]($("#widgetMount"));
  let musicLessonCleanup;
  if (musicSubject) {
    const musicLessons = await import("./labs/music.js");
    if (token !== routeToken) return;
    musicLessonCleanup = musicLessons.lesson($("#widgetMount"), S.id, t);
  }

  let current;
  const showExample = (i) => {
    current = t.examples[i];
    const ex = current;
    const src = ex.yaml ?? ex.code;
    $("#exBody").innerHTML = `
      <div class="row" style="margin-top:1rem">${levelPill(ex.level)}${ex.lang ? `<span class="pill neutral">${esc(ex.lang)}</span>` : ""}<span class="muted">${esc(ex.description)}</span></div>
      <pre class="yaml">${ex.yaml !== undefined ? highlightYaml(src) : highlightCode(src, ex.lang)}</pre>
      <div class="row" style="margin-top:.9rem">${exampleActions(t, ex)}</div>
      <div id="exOut"></div>`;
  };
  const handoff = (key, value, hash) => {
    sessionStorage.setItem(key, value);
    location.hash = hash;
  };
  $("#exBody").addEventListener("click", async (e) => {
    const act = e.target.closest("[data-ex]")?.dataset.ex;
    if (!act) return;
    const ex = current;
    const src = ex.yaml ?? ex.code;
    if (act === "copy") copy(src);
    else if (act === "kind") handoff("pg-yaml", src, "#/k8s/playground?tab=yaml");
    else if (act === "sim") handoff("sim-pod", src, `#/k8s/lab?preset=${t.simulate}&custom=1`);
    else if (act === "sqlpg") handoff("sql-code", src, "#/db/playground");
    else if (act === "pyviz") handoff("py-code", src, "#/python/lab");
    else if (act === "pyrun") handoff("py-code", src, "#/python/playground");
    else if (act === "git") handoff("git-script", src, "#/git/playground");
    else if (act === "iam") handoff("iam-policy", src, "#/aws/lab");
    else if (act === "sh") handoff("sh-script", src, "#/linux/playground");
    else if (act === "javaver") handoff("java-code", src, "#/java/playground");
    else if (act === "run") {
      const btn = e.target.closest("button");
      btn.disabled = true;
      $("#exOut").innerHTML = `<div class="muted res-meta">Running…</div>`;
      const r = ex.lang === "sql" ? await runSql(src) : await runPython(src);
      btn.disabled = false;
      if (current !== ex) return;
      $("#exOut").innerHTML = ex.lang === "sql" ? sqlResultHtml(r) : pyResultHtml(r);
    }
  });
  $("#exTabs").addEventListener("click", (e) => {
    if (e.target.dataset.i === undefined) return;
    $$("#exTabs button").forEach((b) => b.classList.toggle("active", b === e.target));
    showExample(+e.target.dataset.i);
  });
  showExample(0);

  view.addEventListener("click", onCopyClick);
  $("#learnBtn").onclick = (e) => {
    const on = learned.toggle(t.id);
    e.target.textContent = on ? "Learned" : "Mark as learned";
    e.target.classList.toggle("success", on);
  };
  return () => {
    player?.destroy();
    musicLessonCleanup?.();
    view.removeEventListener("click", onCopyClick);
  };
}

function onCopyClick(e) {
  const c = e.target.closest("[data-copy]");
  if (c) copy(c.dataset.copy);
}

// ------------------------------------------------------------------ data
async function loadContent(sid) {
  if (!contentCache.has(sid)) {
    const p = api(`/api/content?subject=${encodeURIComponent(sid)}`).then((c) => {
      if (!c.topics) contentCache.delete(sid);
      return c;
    });
    contentCache.set(sid, p);
  }
  return contentCache.get(sid);
}

const gameData = (sid) => import(sid === "k8s" ? "./games-data.js" : `./gamedata/${sid}.js`);
const labModule = (sid) => import(`./labs/${sid}.js`);

// ------------------------------------------------------------------ router
function parseHash() {
  const raw = location.hash.replace(/^#/, "") || "/";
  const [path, qs] = raw.split("?");
  return { parts: path.split("/").filter(Boolean), params: new URLSearchParams(qs || ""), qs: qs ? `?${qs}` : "" };
}

const LEGACY = { topic: "topic", simulator: "lab", playground: "playground", interview: "interview", games: "games" };

async function route() {
  const token = ++routeToken;
  cleanup();
  cleanup = () => {};
  const { parts, params, qs } = parseHash();
  if (LEGACY[parts[0]]) {
    location.replace(`#/k8s/${LEGACY[parts[0]]}${parts[1] ? `/${parts[1]}` : ""}${qs}`);
    return;
  }
  const s = subjects.find((x) => x.id === parts[0]);
  if (!s) {
    if (parts.length && parts[0] !== "subjects") toast(`Unknown subject "${parts[0]}"`, true);
    setSubject(null);
    content = null;
    setChatContext(null, null, "");
    $$("#nav a").forEach((a) => a.classList.remove("active"));
    renderLanding(view, subjects, learnedCount, STATIC);
    updateProgress();
    window.scrollTo({ top: 0 });
    track("view_tab", { detail: "home" });
    return;
  }
  const page = parts[1] || "learn";
  setChatContext(s.id, page === "topic" ? parts[2] : null, s.name);
  if (S?.id !== s.id) setSubject(s);
  $$("#nav a").forEach((a) => a.classList.toggle("active", a.dataset.route === (page === "topic" ? "learn" : page)));
  if (!contentCache.has(s.id)) view.innerHTML = `<div class="loading clay">Loading ${esc(s.name)}…</div>`;
  const c = await loadContent(s.id);
  if (token !== routeToken) return;
  if (!c.topics) {
    view.innerHTML = `<div class="panel clay">Failed to load ${esc(s.name)}: ${esc(c.error || "unknown error")}</div>`;
    return;
  }
  content = c;
  const tutorTopic = page === "topic" ? content.topics.find((item) => item.id === parts[2]) : null;
  const tutorContext = {
    subject: content.subject?.name || s.name,
    subject_intro: content.subject?.tagline || s.tagline,
    beginner_guide: content.subject?.beginner || null,
    current_lesson: tutorTopic ? {
      title: tutorTopic.title,
      level: tutorTopic.level,
      summary: tutorTopic.tagline,
      explanation: tutorTopic.what,
      analogy: tutorTopic.analogy,
      key_points: tutorTopic.key_points?.slice(0, 6),
      use_cases: tutorTopic.use_cases?.slice(0, 4),
      commands: tutorTopic.commands?.slice(0, 4),
      examples: tutorTopic.examples?.slice(0, 2).map((example) => ({
        title: example.title,
        description: example.description,
        language: example.lang,
        code: (example.code || example.yaml || "").slice(0, 500),
      })),
      questions: tutorTopic.interview?.slice(0, 3).map(({ q, a }) => ({ question: q, answer: a?.slice(0, 350) })),
    } : null,
    subject_lessons: tutorTopic ? undefined : content.topics.slice(0, 24).map(({ title, tagline }) => ({ title, summary: tagline })),
  };
  setChatContext(s.id, page === "topic" ? parts[2] : null, s.name, tutorContext);
  updateProgress();
  if (page !== "topic") store.set("last-visit", { sid: s.id, topic: store.get("last-visit", {})?.sid === s.id ? store.get("last-visit", {}).topic : null });

  let result;
  try {
    if (page === "topic") {
      result = await renderTopic(parts[2], token);
      if (token !== routeToken) return;
    }
    else if (page === "beginner") result = renderHome("beginner");
    else if (page === "interview") {
      const mod = await import("./interview.js");
      if (token !== routeToken) return;
      result = mod.renderInterview(view, content, params);
    }
    else if (page === "games") {
      const [data, mod] = await Promise.all([gameData(s.id), import("./games.js")]);
      if (token !== routeToken) return;
      result = mod.renderGames(view, content, params, { WORDS: data.WORDS, RUSH: data.RUSH, BUGS: data.BUGS, ...data.META });
    } else if (page === "lab" || page === "playground") {
      if (s.id === "k8s") {
        const mod = await import(page === "lab" ? "./simulator.js" : "./playground.js");
        if (token !== routeToken) return;
        result = page === "lab" ? mod.renderSimulator(view, content, params) : mod.renderPlayground(view, content, params);
      }
      else {
        view.innerHTML = `<div class="loading clay">Loading ${esc(s.tabs[page])}…</div>`;
        const mod = await labModule(s.id);
        if (token !== routeToken) return;
        const root = document.createElement("div");
        root.className = "lab-root";
        view.replaceChildren(root);
        result = mod[page](root, content, params);
      }
    } else result = renderHome();
  } catch (err) {
    console.error(err);
    view.innerHTML = `<div class="panel clay">Something went wrong rendering this page: ${esc(err.message)}</div>`;
  }
  if (typeof result === "function") cleanup = result;
  window.scrollTo({ top: 0 });
  if (page === "topic") track("view_topic", { sid: s.id, topic: parts[2] });
  else track("view_tab", { sid: s.id, detail: page });
}

(async function boot() {
  initControls();
  const list = await api("/api/subjects");
  if (!Array.isArray(list)) {
    view.innerHTML = `<div class="panel clay">Failed to load subjects: ${esc(list.error || "unknown error")}</div>`;
    return;
  }
  subjects = list;
  initSearch(subjects, STATIC);
  initChat();
  window.addEventListener("hashchange", route);
  // Account state can require a round trip to Neon; don't hold the lesson UI
  // behind it. The account button and sync state update when that request ends.
  void initAccount(subjects, { onChange: route }).catch((err) => console.error("Account initialization failed:", err));
  document.addEventListener("pointermove", (e) => {
    const card = e.target.closest?.(".spot");
    if (!card) return;
    const r = card.getBoundingClientRect();
    card.style.setProperty("--mx", `${e.clientX - r.left}px`);
    card.style.setProperty("--my", `${e.clientY - r.top}px`);
  }, { passive: true });
  route();
})();
