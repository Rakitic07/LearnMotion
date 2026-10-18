import { enableTabIndent, esc } from "../util.js";

export const labHero = (code, tint, title, desc, extra = "") => `
  <section class="topic-hero clay">
    <div class="code tint-${tint}">${esc(code)}</div>
    <div><h1>${esc(title)}</h1><div class="muted">${desc}</div></div>
    <div class="row">${extra}</div>
  </section>`;

/** Tab indentation plus Ctrl/Cmd+Enter to run. */
export function codeEditor(textarea, onRun, indent = 2) {
  enableTabIndent(textarea, indent);
  textarea.addEventListener("keydown", (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      e.preventDefault();
      onRun();
    }
  });
}

export const takeHandoff = (key) => {
  const v = sessionStorage.getItem(key);
  sessionStorage.removeItem(key);
  return v;
};

export const sampleOptions = (content, langs) =>
  content.topics.flatMap((t) => t.examples.filter((e) => e.runnable && langs.includes(e.lang)).map((e) => ({ label: `${t.title} · ${e.title}`, code: e.code })));
