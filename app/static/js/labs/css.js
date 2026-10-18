import { esc, highlightCode } from "../util.js";
import { scenarioLab } from "./catalog.js";

export function lab(view, content) {
  scenarioLab(view, "CSS", "lilac", "CSS Foundations Lab", "Choose a style, inspect its CSS and evaluate readability in the live preview.", content);
  const exercises = [
    { name: "Flexbox navigation", css: ".demo-nav {\n  display: flex;\n  align-items: center;\n  justify-content: space-between;\n  gap: 1rem;\n}\n.demo-links { display: flex; gap: .75rem; }", html: `<nav class="demo-nav"><b>Studio</b><div class="demo-links"><a href="#">Work</a><a href="#">About</a><a href="#">Contact</a></div><button type="button">Sign in</button></nav>`, label: "Align a navigation bar with Flexbox." },
    { name: "Responsive card grid", css: ".demo-grid {\n  display: grid;\n  grid-template-columns: repeat(auto-fit, minmax(10rem, 1fr));\n  gap: 1rem;\n}\n.demo-tile { padding: 1rem; border-radius: 1rem; }", html: `<div class="demo-grid"><article class="demo-tile">Design</article><article class="demo-tile">Build</article><article class="demo-tile">Ship</article></div>`, label: "Use Grid to fit cards to the available width." },
    { name: "Box model", css: ".demo-box {\n  box-sizing: border-box;\n  width: 100%;\n  padding: 1.5rem;\n  border: 4px solid #7058e8;\n  border-radius: 1rem;\n}", html: `<article class="demo-box"><b>Box model</b><p>Change padding, border and width to see how the box responds.</p></article>`, label: "Explore how content, padding, border and width combine." },
    { name: "Focus and hover states", css: ".demo-action {\n  border: 2px solid transparent;\n  border-radius: .75rem;\n  padding: .8rem 1rem;\n  background: #7058e8; color: white;\n  transition: transform 160ms ease;\n}\n.demo-action:hover { transform: translateY(-2px); }\n.demo-action:focus-visible { outline: 3px solid #182033; outline-offset: 3px; }", html: `<div class="demo-actions"><button class="demo-action" type="button">Hover or tab to me</button><span>Use Tab to see keyboard focus.</span></div>`, label: "Add visible hover and keyboard-focus feedback." },
    { name: "Design tokens and themes", css: ".demo-token-card {\n  --surface: #f2efff;\n  --accent: #7058e8;\n  padding: 1.25rem;\n  color: #182033;\n  background: var(--surface);\n  border-inline-start: 5px solid var(--accent);\n}\n.demo-token-card strong { color: var(--accent); }", html: `<article class="demo-token-card"><strong>Reusable tokens</strong><p>Change the variables to update the whole component.</p></article>`, label: "Use custom properties to theme a component consistently." },
  ];
  view.insertAdjacentHTML("beforeend", `<section class="panel clay css-foundations-sandbox"><div class="section-title"><div><h2>Try CSS and see it render</h2><p class="muted">Choose a small example, edit the CSS, and watch the preview update.</p></div></div><label class="css-exercise-picker" for="cssExercise">Example<select id="cssExercise">${exercises.map((item, i) => `<option value="${i}">${esc(item.name)}</option>`).join("")}</select></label><p id="cssExerciseHint" class="muted"></p><div class="grid two css-exercise-grid"><div><label for="cssExerciseEditor">Editable CSS</label><textarea id="cssExerciseEditor" class="code code-editor" rows="13" spellcheck="false"></textarea><pre class="code css-code" aria-label="Color-coded CSS"><code id="cssExerciseHighlight"></code></pre><div class="row"><button class="btn primary" id="cssExerciseApply" type="button">Apply CSS</button><button class="btn" id="cssExerciseReset" type="button">Reset example</button></div></div><section class="css-exercise-preview"><h3>Browser preview</h3><div id="cssExerciseDemo" class="css-lab-demo"></div><span id="cssExerciseStatus" class="muted" aria-live="polite">Preview ready</span></section></div></section>`);
  const $ = (selector) => view.querySelector(selector);
  const editor = $("#cssExerciseEditor"), demo = $("#cssExerciseDemo");
  const drawExercise = (apply = true) => {
    const sample = exercises[Number($("#cssExercise").value)];
    editor.value = sample.css; $("#cssExerciseHint").textContent = sample.label;
    demo.innerHTML = sample.html;
    const style = document.createElement("style"); style.textContent = editor.value; demo.prepend(style);
    $("#cssExerciseHighlight").innerHTML = highlightCode(editor.value, "css");
    if (apply) $("#cssExerciseStatus").textContent = "CSS applied to the preview";
  };
  $("#cssExercise").addEventListener("change", () => drawExercise());
  $("#cssExerciseApply").addEventListener("click", () => { const style = demo.querySelector("style"); if (style) style.textContent = editor.value; $("#cssExerciseStatus").textContent = "CSS applied to the preview"; });
  $("#cssExerciseReset").addEventListener("click", () => drawExercise());
  editor.addEventListener("input", () => {
    $("#cssExerciseHighlight").innerHTML = highlightCode(editor.value, "css");
    const style = demo.querySelector("style"); if (style) style.textContent = editor.value;
    $("#cssExerciseStatus").textContent = "Preview updated";
  });
  drawExercise(false);
}

export function playground(view) {
  const presets = [["clay", "Claymorphism"], ["neo", "Neumorphism"], ["glass", "Glassmorphism"], ["flat", "Flat design"], ["material", "Material"], ["brutal", "Brutalist"], ["gradient", "Gradient"], ["skeuo", "Skeuomorphic"], ["outline", "Outline"]];
  view.innerHTML = `<section class="topic-hero clay"><div class="code tint-lilac">CSS</div><div><h1>Live Style Studio</h1><div class="muted">Explore nine interface styles, then tune the surface and preview your own rendered component.</div></div></section>
    <div class="css-style-tabs" role="tablist" aria-label="Choose a visual style">${presets.map(([id, label], i) => `<button class="btn ${i === 0 ? "primary" : ""}" type="button" role="tab" aria-selected="${i === 0}" data-css-style="${id}">${label}</button>`).join("")}</div>
    <div class="grid two css-studio-layout"><section class="panel clay css-controls">
      <label>Surface color<input id="cssSurface" type="color" value="#e9edf5"></label>
      <label>Accent color<input id="cssAccent" type="color" value="#7058e8"></label>
      <label>Corner radius <b id="cssRadiusValue">24 px</b><input id="cssRadius" type="range" min="8" max="48" value="24"></label>
      <label>Depth / blur <b id="cssDepthValue">16</b><input id="cssDepth" type="range" min="0" max="32" value="16"></label>
      <label>Text contrast<select id="cssContrast"><option value="dark">Dark text</option><option value="light">Light text</option></select></label>
    </section><section class="panel clay css-preview-panel"><h3>Rendered preview</h3><div id="cssPreviewStage"><article id="cssPreviewCard"><span class="css-preview-icon">✦</span><p class="css-preview-kicker">LIVE COMPONENT</p><h2>Soft surfaces</h2><p>Readable text and clear controls matter more than the visual effect.</p><button type="button" id="cssPreviewButton">Explore styles</button></article></div><p id="cssAccessibility" class="muted"></p></section></div>
    <section class="panel clay css-code-panel"><div class="row"><div><h3 style="margin:0">Generated CSS</h3><span class="muted">Updates as you adjust the controls</span></div><button class="btn small" type="button" id="cssCopy">Copy CSS</button></div><pre class="code css-code" id="cssCode"></pre></section>`;
  const $ = (q) => view.querySelector(q); let selected = "clay";
  const contrast = (hex) => { const values = hex.slice(1).match(/.{2}/g).map((v) => parseInt(v, 16) / 255).map((v) => v <= .04045 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4); return .2126 * values[0] + .7152 * values[1] + .0722 * values[2]; };
  const draw = () => {
    const surface = $("#cssSurface").value, accent = $("#cssAccent").value, radius = +$("#cssRadius").value, depth = +$("#cssDepth").value, text = $("#cssContrast").value === "light" ? "#f8fafc" : "#182033";
    $("#cssRadiusValue").textContent = `${radius} px`; $("#cssDepthValue").textContent = depth;
    const stage = $("#cssPreviewStage"); const card = $("#cssPreviewCard");
    const previewStyles = {
      clay: { background: surface, border: "1px solid rgb(255 255 255 / .68)", shadow: `10px 10px ${depth}px color-mix(in srgb, ${surface} 72%, #182033), -8px -8px ${depth}px color-mix(in srgb, ${surface} 72%, white), inset 0 1px 0 rgb(255 255 255 / .55)`, radius },
      neo: { background: surface, border: "0", shadow: `${depth}px ${depth}px ${depth * 1.5}px color-mix(in srgb, ${surface} 72%, #142033), -${depth}px -${depth}px ${depth * 1.5}px color-mix(in srgb, ${surface} 78%, white)`, radius },
      glass: { background: `color-mix(in srgb, ${surface} 66%, transparent)`, border: "1px solid rgb(255 255 255 / .55)", shadow: "0 18px 42px rgb(24 32 51 / .22)", radius, backdrop: `blur(${depth}px) saturate(1.35)`, stage: `linear-gradient(135deg, ${accent}88, #f6c97499), linear-gradient(45deg, #d9e5ff, #b7eddc)` },
      flat: { background: surface, border: "0", shadow: "none", radius: Math.min(radius, 10) },
      material: { background: surface, border: "0", shadow: "0 3px 6px rgb(0 0 0 / .12), 0 8px 22px rgb(0 0 0 / .18)", radius: Math.min(radius, 16) },
      brutal: { background: surface, border: `3px solid ${text}`, shadow: `8px 8px 0 ${accent}`, radius: 0 },
      gradient: { background: `linear-gradient(135deg, ${accent}, ${surface} 85%)`, border: "1px solid rgb(255 255 255 / .42)", shadow: `0 18px ${depth}px color-mix(in srgb, ${accent} 40%, transparent)`, radius },
      skeuo: { background: `linear-gradient(180deg, color-mix(in srgb, ${surface} 72%, white), ${surface} 55%, color-mix(in srgb, ${surface} 78%, #526078))`, border: "1px solid color-mix(in srgb, #111827 28%, transparent)", shadow: "inset 0 2px 2px rgb(255 255 255 / .78), inset 0 -3px 4px rgb(15 23 42 / .22), 0 5px 10px rgb(15 23 42 / .2)", radius },
      outline: { background: "transparent", border: `2px solid ${accent}`, shadow: "none", radius },
    }[selected];
    stage.style.setProperty("--css-stage", previewStyles.stage || surface);
    card.style.setProperty("--css-surface", surface); card.style.setProperty("--css-accent", accent); card.style.setProperty("--css-text", text);
    card.style.setProperty("--css-radius", `${previewStyles.radius}px`); card.style.setProperty("--css-depth", `${depth}px`);
    card.style.setProperty("--css-card-bg", previewStyles.background); card.style.setProperty("--css-card-border", previewStyles.border); card.style.setProperty("--css-card-shadow", previewStyles.shadow); card.style.setProperty("--css-backdrop", previewStyles.backdrop || "none");
    card.dataset.style = selected;
    $("#cssPreviewButton").style.background = accent;
    const declarations = [`color: ${text}`, `border-radius: ${previewStyles.radius}px`, `background: ${previewStyles.background}`, `border: ${previewStyles.border}`, `box-shadow: ${previewStyles.shadow}`, ...(previewStyles.backdrop ? [`backdrop-filter: ${previewStyles.backdrop}`] : [])];
    const source = `.surface-card {\n${declarations.map((line) => `  ${line};`).join("\n")}\n}\n\n.surface-card button {\n  background: ${accent};\n  color: #fff;\n}`;
    $("#cssCode").innerHTML = highlightCode(source, "css");
    const ratio = contrast(surface), foreground = contrast(text); const lighter = Math.max(ratio, foreground), darker = Math.min(ratio, foreground); const score = (lighter + .05) / (darker + .05);
    $("#cssAccessibility").textContent = `Text contrast against the selected surface: ${score.toFixed(2)}:1 ${score >= 4.5 ? "· passes the WCAG AA normal-text ratio" : "· below the WCAG AA normal-text ratio; try a different text color"}.`;
  };
  view.querySelectorAll("[data-css-style]").forEach((button) => button.addEventListener("click", () => {
    selected = button.dataset.cssStyle;
    view.querySelectorAll("[data-css-style]").forEach((tab) => { const active = tab === button; tab.classList.toggle("primary", active); tab.setAttribute("aria-selected", String(active)); });
    draw();
  }));
  view.querySelectorAll("#cssSurface, #cssAccent, #cssRadius, #cssDepth, #cssContrast").forEach((el) => { el.addEventListener("input", draw); el.addEventListener("change", draw); });
  $("#cssCopy").addEventListener("click", async () => { await navigator.clipboard?.writeText($("#cssCode").textContent); $("#cssCopy").textContent = "Copied"; setTimeout(() => { if ($("#cssCopy")) $("#cssCopy").textContent = "Copy CSS"; }, 1200); });
  draw();
}
