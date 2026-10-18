import { $, $$, copy, esc, levelPill, store } from "./util.js";

function shuffle(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

export function renderInterview(view, content) {
  const sid = content.subject.id;
  const knownKey = sid === "k8s" ? "known-qs" : `known-qs:${sid}`;
  const topicTitle = (id) => content.topics.find((t) => t.id === id)?.title || id;
  const allQs = [
    ...content.topics.flatMap((t) => t.interview.map((q, i) => ({ ...q, topic: t.id, category: t.category, id: `${t.id}#${i}`, type: "concept" }))),
    ...content.scenarios.map((q, i) => ({ ...q, category: content.topics.find((t) => t.id === q.topic)?.category, id: `scenario#${i}`, type: "scenario" })),
  ];
  const known = new Set(store.get(knownKey, []));
  const saveKnown = () => store.set(knownKey, [...known]);

  view.innerHTML = `
    <section class="topic-hero clay">
      <div class="code tint-peach">IQ</div>
      <div>
        <h1>${esc(content.subject.name)} Interview Prep</h1>
        <div class="muted">${allQs.length} questions from basic to advanced, plus real troubleshooting scenarios. Your progress is saved in this browser.</div>
      </div>
      <div style="min-width:180px"><div class="muted" style="font-size:.8rem">Mastered</div><div class="big-number" id="knownCount" style="font-size:2rem"></div></div>
    </section>
    <div class="filters">
      <div class="tabs" id="modeTabs">
        <button data-m="flash" class="active">Flashcards</button>
        <button data-m="list">All questions</button>
        <button data-m="scenarios">Troubleshooting</button>
        <button data-m="cheat">${esc(content.subject.cheat)}</button>
      </div>
      <span class="spacer"></span>
      <select id="lvlFilter"><option value="">All levels</option><option>basic</option><option>intermediate</option><option>advanced</option></select>
      <select id="catFilter"><option value="">All categories</option>${content.categories.map((c) => `<option value="${c.id}">${esc(c.title)}</option>`).join("")}</select>
      <label class="muted" style="font-size:.85rem"><input type="checkbox" id="hideKnown"> hide mastered</label>
    </div>
    <div id="mode"></div>`;

  const updateCount = () => ($("#knownCount").textContent = `${[...known].filter((k) => allQs.some((q) => q.id === k)).length} / ${allQs.length}`);
  updateCount();

  const filtered = (onlyType) => allQs.filter((q) =>
    (!onlyType || q.type === onlyType) &&
    (!$("#lvlFilter").value || q.level === $("#lvlFilter").value) &&
    (!$("#catFilter").value || q.category === $("#catFilter").value) &&
    (!$("#hideKnown").checked || !known.has(q.id)));

  let mode = "flash";

  function renderFlash() {
    let deck = shuffle(filtered());
    let i = 0;
    const draw = () => {
      if (!deck.length) {
        $("#mode").innerHTML = `<div class="panel clay" style="text-align:center"><h3>Deck empty</h3><p class="muted">Change filters or untick "hide mastered".</p></div>`;
        return;
      }
      const q = deck[i];
      $("#mode").innerHTML = `
        <div class="flash-wrap">
          <div class="row" style="justify-content:center; margin-bottom:.8rem"><span class="pill neutral">${i + 1} / ${deck.length}</span>${levelPill(q.level)}<span class="pill neutral">${esc(q.type === "scenario" ? "scenario" : topicTitle(q.topic))}</span>${known.has(q.id) ? `<span class="pill ok">mastered</span>` : ""}</div>
          <div class="flashcard" id="card">
            <div class="face front clay"><span class="muted">Question. Click to flip.</span><h2>${esc(q.q)}</h2><span class="muted" style="margin-top:auto">Say your answer out loud first, like in the real interview.</span></div>
            <div class="face back clay tint-mint"><span class="muted">Answer</span><p>${esc(q.a)}</p><a href="#/${sid}/topic/${q.topic}" style="margin-top:auto">Review: ${esc(topicTitle(q.topic))} →</a></div>
          </div>
        </div>
        <div class="flash-actions">
          <button class="btn" id="prevQ">Prev</button>
          <button class="btn danger" id="againQ">Review again</button>
          <button class="btn success" id="knowQ">I knew it</button>
          <button class="btn" id="nextQ">Next</button>
          <button class="btn" id="shuffleQ">Shuffle</button>
        </div>`;
      $("#card").onclick = (e) => {
        if (e.target.tagName !== "A") $("#card").classList.toggle("flipped");
      };
      const step = (d) => ((i = (i + d + deck.length) % deck.length), draw());
      $("#prevQ").onclick = () => step(-1);
      $("#nextQ").onclick = () => step(1);
      $("#knowQ").onclick = () => { known.add(q.id); saveKnown(); updateCount(); step(1); };
      $("#againQ").onclick = () => { known.delete(q.id); saveKnown(); updateCount(); step(1); };
      $("#shuffleQ").onclick = () => { deck = shuffle(deck); i = 0; draw(); };
    };
    draw();
  }

  function renderList(type) {
    const qs = filtered(type);
    const groups = type === "scenario" ? [["Troubleshooting scenarios", qs]] : content.topics.map((t) => [t.title, qs.filter((q) => q.topic === t.id && q.type === "concept")]).filter(([, g]) => g.length);
    $("#mode").innerHTML = groups.map(([title, g]) => `
      <div class="section-title"><h2>${esc(title)}</h2><span class="muted">${g.length}</span></div>
      ${g.map((q) => `<details class="qa clay"><summary>${levelPill(q.level)} ${esc(q.q)} ${known.has(q.id) ? `<span class="pill ok">mastered</span>` : ""}</summary>
        <div class="answer">${esc(q.a)}<div class="row" style="margin-top:.7rem"><a class="btn small" href="#/${sid}/topic/${q.topic}">Open topic</a>
        <button class="btn small ${known.has(q.id) ? "" : "success"}" data-know="${esc(q.id)}">${known.has(q.id) ? "Unmark" : "Mark mastered"}</button></div></div></details>`).join("")}`).join("") ||
      `<div class="panel clay muted">No questions match the filters.</div>`;
  }

  function renderCheat() {
    $("#mode").innerHTML = `<div class="grid two">${content.categories.map((c) => {
      const cmds = content.topics.filter((t) => t.category === c.id).flatMap((t) => t.commands);
      return cmds.length ? `<div class="panel clay"><h3><span class="category-dot tint-${c.color}"></span>${esc(c.title)}</h3><ul class="clean cmd-list">${[...new Set(cmds)].map((cmd) => `<li><code>${esc(cmd)}</code><button class="btn small" data-copy="${esc(cmd)}">Copy</button></li>`).join("")}</ul></div>` : "";
    }).join("")}</div>`;
  }

  const draw = () => {
    if (mode === "flash") renderFlash();
    else if (mode === "list") renderList("concept");
    else if (mode === "scenarios") renderList("scenario");
    else renderCheat();
  };

  $("#modeTabs").addEventListener("click", (e) => {
    if (!e.target.dataset.m) return;
    mode = e.target.dataset.m;
    $$("#modeTabs button").forEach((b) => b.classList.toggle("active", b === e.target));
    draw();
  });
  ["#lvlFilter", "#catFilter", "#hideKnown"].forEach((s) => ($(s).onchange = draw));
  $("#mode").addEventListener("click", (e) => {
    const k = e.target.dataset.know;
    if (k) {
      known.has(k) ? known.delete(k) : known.add(k);
      saveKnown();
      updateCount();
      draw();
    }
    const c = e.target.closest("[data-copy]");
    if (c) copy(c.dataset.copy);
  });
  draw();
}
