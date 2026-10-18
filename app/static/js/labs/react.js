import { esc, highlightCode } from "../util.js";
import { scenarioLab } from "./catalog.js";

export function lab(view, content) {
  scenarioLab(view, "RCT", "sky", "React Foundations Lab", "Explore the component, state and effect decisions in a small React interface.", content);
}

export function playground(view) {
  view.innerHTML = `<section class="topic-hero clay"><div class="code tint-sky">RCT</div><div><h1>React Component Builder</h1><div class="muted">Change component inputs and state, then interact with the live preview and inspect the JSX.</div></div></section>
    <div class="grid two" style="margin-top:1rem"><section class="panel clay react-builder-controls">
      <label>Component<select id="reactKind"><option value="counter">Counter</option><option value="toggle">Toggle panel</option><option value="profile">Profile card</option></select></label>
      <label>Component title<input id="reactTitle" value="Welcome" maxlength="50"></label>
      <label>Accent color<input id="reactAccent" type="color" value="#61dafb"></label>
      <label class="check"><input id="reactDisabled" type="checkbox"> Disable the main action</label>
    </section><section class="panel clay"><h3>Live preview</h3><div id="reactPreview" class="react-preview"></div><p class="muted" id="reactState"></p></section></div>
    <section class="panel clay" style="margin-top:1rem"><div class="row"><h3 style="margin:0">JSX sketch</h3><span class="pill neutral">Illustrative React code</span></div><pre class="code react-code" id="reactCode"></pre></section>`;
  const get = (id) => view.querySelector(`#${id}`);
  let count = 0; let open = false;
  const draw = () => {
    const kind = get("reactKind").value; const title = get("reactTitle").value || "Welcome"; const accent = get("reactAccent").value; const disabled = get("reactDisabled").checked;
    const preview = get("reactPreview"); preview.style.setProperty("--react-accent", accent);
    if (kind === "counter") {
      preview.innerHTML = `<h4>${esc(title)}</h4><p class="react-count">${count}</p><button type="button" class="btn primary" ${disabled ? "disabled" : ""}>Increment</button><button type="button" class="btn" data-reset>Reset</button>`;
      preview.querySelector(".primary").addEventListener("click", () => { count++; draw(); });
      preview.querySelector("[data-reset]").addEventListener("click", () => { count = 0; draw(); });
    } else if (kind === "toggle") {
      preview.innerHTML = `<h4>${esc(title)}</h4><button type="button" class="btn primary" ${disabled ? "disabled" : ""}>${open ? "Hide details" : "Show details"}</button>${open ? `<p class="react-detail">This panel is conditionally rendered from component state.</p>` : ""}`;
      preview.querySelector("button").addEventListener("click", () => { open = !open; draw(); });
    } else {
      preview.innerHTML = `<div class="react-profile-mark" aria-hidden="true">${esc(title.slice(0, 1).toUpperCase())}</div><h4>${esc(title)}</h4><p>A component receives its content as props.</p><button type="button" class="btn primary" ${disabled ? "disabled" : ""}>Follow</button>`;
    }
    get("reactState").textContent = kind === "counter" ? `State: count = ${count}` : kind === "toggle" ? `State: open = ${open}` : "Props: title is passed from the parent component";
    const source = kind === "counter" ? `function Counter({ title }) {\n  const [count, setCount] = useState(0);\n  return (\n    <section>\n      <h2>{title}</h2>\n      <button onClick={() => setCount(c => c + 1)}>\n        Count: {count}\n      </button>\n    </section>\n  );\n}` : kind === "toggle" ? `function Details({ title }) {\n  const [open, setOpen] = useState(false);\n  return (\n    <section>\n      <h2>{title}</h2>\n      <button onClick={() => setOpen(value => !value)}>\n        {open ? "Hide details" : "Show details"}\n      </button>\n      {open && <p>Details go here.</p>}\n    </section>\n  );\n}` : `function ProfileCard({ title }) {\n  return (\n    <article className="profile-card">\n      <h2>{title}</h2>\n      <p>Profile details</p>\n      <button>Follow</button>\n    </article>\n  );\n}`;
    get("reactCode").innerHTML = highlightCode(source, "jsx");
  };
  view.querySelectorAll("#reactKind, #reactTitle, #reactAccent, #reactDisabled").forEach((el) => { el.addEventListener("input", draw); el.addEventListener("change", draw); });
  draw();
}
