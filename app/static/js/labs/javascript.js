import { $, esc, highlightCode } from "../util.js";
import { codeEditor, labHero } from "./common.js";

const samples = {
  counter: `const app = document.querySelector('#app');\nlet count = 0;\n\nconst button = document.createElement('button');\nbutton.textContent = 'Clicked 0 times';\nbutton.addEventListener('click', () => {\n  count += 1;\n  button.textContent = \`Clicked \${count} times\`;\n});\napp.append(button);`,
  filter: `const items = ['JavaScript', 'NGINX', 'React', 'CSS'];\nconst query = 'script';\nconst matches = items.filter(item =>\n  item.toLowerCase().includes(query.toLowerCase())\n);\n\nconst list = document.createElement('ul');\nfor (const item of matches) {\n  const row = document.createElement('li');\n  row.textContent = item;\n  list.append(row);\n}\ndocument.querySelector('#app').append(list);`,
  async: `const app = document.querySelector('#app');\nconst status = document.createElement('p');\nstatus.textContent = 'Loading…';\napp.append(status);\n\nasync function loadMessage() {\n  await new Promise(resolve => setTimeout(resolve, 500));\n  status.textContent = 'Promise fulfilled: async work finished.';\n}\n\nloadMessage().catch(error => {\n  status.textContent = error.message;\n});`,
  events: `const app = document.querySelector('#app');\napp.innerHTML = '<button data-action="add">Add item</button><ul></ul>';\nconst list = app.querySelector('ul');\nlet nextId = 1;\n\napp.addEventListener('click', event => {\n  if (!event.target.matches('[data-action="add"]')) return;\n  const item = document.createElement('li');\n  item.textContent = \`Item \${nextId++}\`;\n  list.append(item);\n});`,
};

function makeFrame(code) {
  const encoded = btoa(unescape(encodeURIComponent(code)));
  return `<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline' 'unsafe-eval'; style-src 'unsafe-inline'; connect-src 'none'; img-src data:"><style>body{font:16px system-ui;margin:1rem;color:#1d2433}button{padding:.55rem .8rem;border:0;border-radius:.6rem;background:#315ddd;color:white;font:inherit;cursor:pointer}li{margin:.35rem 0}</style><main id="app"></main><pre id="log" aria-live="polite"></pre><script>
    const source = new TextDecoder().decode(Uint8Array.from(atob('${encoded}'), c => c.charCodeAt(0)));
    const log = document.querySelector('#log');
    const safeConsole = { log: (...items) => { log.textContent += items.map(String).join(' ') + '\\n'; }, error: (...items) => { log.textContent += items.map(String).join(' ') + '\\n'; } };
    try { new Function('console', source)(safeConsole); } catch (error) { log.textContent = error.name + ': ' + error.message; }
  <\/script>`;
}

export function lab(view, content) {
  const lessonSamples = content.topics.flatMap((topic) => topic.examples.map((example) => ({ label: `${topic.title} · ${example.title}`, code: example.code })));
  const options = lessonSamples.slice(0, 40).map((item, index) => `<option value="lesson-${index}">${esc(item.label)}</option>`).join("");
  view.innerHTML = `${labHero("JS", "lemon", "JavaScript Foundations Lab", "Explore browser events and asynchronous work with small examples. The preview runs in a sandboxed frame; it does not share this app's DOM or storage.")}
    <section class="panel clay" style="margin-top:1rem"><div class="row"><label>Starter example<select id="jsSample"><option value="counter">Event handlers & state</option><option value="filter">Arrays & rendering</option><option value="async">Promises & async/await</option><option value="events">Event delegation</option>${options}</select></label><button class="btn primary" id="jsRun">Run example <kbd>⌘/Ctrl ↵</kbd></button></div>
    <label for="jsEditor">JavaScript code</label><textarea id="jsEditor" class="code code-editor" spellcheck="false" rows="13"></textarea><details class="js-highlight"><summary>Highlighted JavaScript</summary><pre class="code" id="jsHighlighted"></pre></details></section>
    <section class="panel clay" style="margin-top:1rem"><h3>Sandboxed preview</h3><iframe id="jsPreview" title="JavaScript example preview" sandbox="allow-scripts" style="width:100%;min-height:220px;border:0;border-radius:14px;background:#fff"></iframe></section>`;
  const editor = $("#jsEditor", view);
  const highlighted = $("#jsHighlighted", view);
  const select = $("#jsSample", view);
  const run = () => { $("#jsPreview", view).srcdoc = makeFrame(editor.value); };
  const updateHighlight = () => { highlighted.innerHTML = highlightCode(editor.value, "javascript"); };
  codeEditor(editor, run, 2);
  editor.addEventListener("input", updateHighlight);
  select.addEventListener("change", () => {
    const selected = select.value;
    if (selected.startsWith("lesson-")) editor.value = lessonSamples[Number(selected.slice(7))]?.code || "";
    else editor.value = samples[selected] || samples.counter;
    updateHighlight();
    run();
  });
  $("#jsRun", view).addEventListener("click", run);
  editor.value = samples.counter;
  updateHighlight();
  run();
}

export function playground(view, content) {
  lab(view, content);
}
