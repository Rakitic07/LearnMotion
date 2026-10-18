import { $, esc, highlightCode } from "../util.js";
import { labHero } from "./common.js";

export function scenarioLab(view, badge, color, name, intro, content) {
  const scenarios = content.scenarios || [];
  view.innerHTML = `${labHero(badge, color, name, intro)}<div class="grid" style="margin-top:1rem">${scenarios.map((s, i) => `<article class="panel clay"><span class="pill neutral">${esc(s.level)}</span><h3>${esc(s.q)}</h3><details><summary>Reveal diagnosis and response</summary><p>${esc(s.a)}</p></details></article>`).join("")}</div>`;
}

export function topicBench(view, heading, subtitle, content, makeSnippet) {
  const topics = content.topics;
  view.innerHTML = `<section class="topic-hero clay"><div class="code tint-lilac">LAB</div><div><h1>${esc(heading)}</h1><div class="muted">${esc(subtitle)}</div></div></section><section class="panel clay" style="margin-top:1rem"><label>Concept<select id="benchTopic" style="width:100%;margin-top:.4rem">${topics.map((t, i) => `<option value="${i}">${esc(t.title)}</option>`).join("")}</select></label><p id="benchWhy" class="muted"></p><textarea class="code" id="benchCode" spellcheck="false" style="width:100%;min-height:260px"></textarea><pre class="code bench-highlight" aria-label="Syntax highlighted code"><code id="benchCodeHighlight"></code></pre><div class="row" style="margin-top:.7rem"><button class="btn" id="benchReset">Reload example</button><button class="btn" id="benchCopy">Copy snippet</button></div></section>`;
  const select = $("#benchTopic", view), code = $("#benchCode", view);
  function draw() {
    const t = topics[+select.value];
    $("#benchWhy", view).textContent = t.what;
    code.value = makeSnippet(t);
    $("#benchCodeHighlight", view).innerHTML = highlightCode(code.value, t.lang || "text");
  }
  code.addEventListener("input", () => { const t = topics[+select.value]; $("#benchCodeHighlight", view).innerHTML = highlightCode(code.value, t.lang || "text"); });
  select.addEventListener("change", draw);
  $("#benchReset", view).addEventListener("click", draw);
  $("#benchCopy", view).addEventListener("click", async () => {
    await navigator.clipboard?.writeText(code.value);
    $("#benchCopy", view).textContent = "Copied";
    setTimeout(() => { if ($("#benchCopy", view)) $("#benchCopy", view).textContent = "Copy snippet"; }, 1400);
  });
  draw();
}
