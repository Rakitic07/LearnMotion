// Loaded as a classic script in <head> so the saved theme applies before first paint.
(function () {
  const KEY = "k8s-everything:theme";
  const THEMES = {
    midnight: { label: "Midnight", style: "clay", base: "dark", preview: ["#0b0d17", "#8f7dff", "#46e0c4", "#ff6fae"] },
    daylight: { label: "Daylight", style: "clay", base: "light", preview: ["#e9ecf8", "#6c5cf0", "#0fa892", "#e64d8a"] },
    sunset: { label: "Sunset", style: "glass", base: "dark", preview: ["#140d12", "#ff7a59", "#ffc857", "#ff4f8b"] },
    neumorph: { label: "Dark", style: "neumorph", base: "dark", preview: ["#2a2c30", "#ff5a1f", "#ffb21e", "#8b8f97"] },
    custom: { label: "Custom", style: null, base: null, preview: null },
  };
  const STYLES = { clay: "Claymorph", glass: "Glassmorph", neumorph: "Neumorph" };
  const DEFAULT_CUSTOM = { bg: "#0f1a1f", primary: "#3fa9f5", accent: "#a3e635", style: "clay" };
  const HEX = /^#[0-9a-f]{6}$/i;
  const COLOR_KEYS = [["bg", "Background"], ["primary", "Primary"], ["accent", "Accent"]];
  const PRESETS = ["#0b0d17", "#f4f1ea", "#8f7dff", "#3fa9f5", "#46e0c4", "#a3e635", "#ffc857", "#ff7a59", "#ff4f8b", "#2a2c30"];

  function load() {
    try {
      const saved = JSON.parse(localStorage.getItem(KEY) || "{}");
      const custom = { ...DEFAULT_CUSTOM, ...(saved.custom || {}) };
      for (const k of ["bg", "primary", "accent"]) if (!HEX.test(custom[k])) custom[k] = DEFAULT_CUSTOM[k];
      if (!STYLES[custom.style]) custom.style = DEFAULT_CUSTOM.style;
      return { name: THEMES[saved.name] ? saved.name : "custom", custom };
    } catch {
      return { name: "custom", custom: { ...DEFAULT_CUSTOM } };
    }
  }

  function luminance(hex) {
    const [r, g, b] = [1, 3, 5].map((i) => {
      const c = parseInt(hex.slice(i, i + 2), 16) / 255;
      return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
    });
    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  }

  const contrast = (a, b) => {
    const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x);
    return (hi + 0.05) / (lo + 0.05);
  };
  const mix = (a, b, t) => "#" + [1, 3, 5].map((i) => {
    const v = Math.round(parseInt(a.slice(i, i + 2), 16) * (1 - t) + parseInt(b.slice(i, i + 2), 16) * t);
    return v.toString(16).padStart(2, "0");
  }).join("");
  // Nudges a colour toward the text pole until it reaches the target contrast on bg.
  const readable = (color, bg, pole, target) => {
    for (let t = 0; t <= 1; t += 0.05) {
      const c = mix(color, pole, t);
      if (contrast(c, bg) >= target) return c;
    }
    return pole;
  };
  const DERIVED = ["--bg", "--primary", "--accent", "--on-primary", "--ink", "--ink-strong", "--ink-soft", "--ink-dim", "--accent-ink", "--primary-ink"];

  function apply(state) {
    const root = document.documentElement;
    root.dataset.theme = state.name;
    for (const v of DERIVED) root.style.removeProperty(v);
    const preset = THEMES[state.name];
    root.dataset.style = preset.style || state.custom.style;
    if (state.name === "custom") {
      const { bg, primary, accent } = state.custom;
      const dark = contrast(bg, "#ffffff") >= contrast(bg, "#10121f");
      const pole = dark ? "#ffffff" : "#10121f";
      root.dataset.base = dark ? "dark" : "light";
      const vars = {
        "--bg": bg,
        "--primary": primary,
        "--accent": accent,
        "--on-primary": contrast(primary, "#ffffff") >= contrast(primary, "#10121f") ? "#ffffff" : "#10121f",
        "--ink-strong": readable(mix(bg, pole, 0.95), bg, pole, 12),
        "--ink": readable(mix(bg, pole, 0.82), bg, pole, 8),
        "--ink-soft": readable(mix(bg, pole, 0.6), bg, pole, 5),
        "--ink-dim": readable(mix(bg, pole, 0.45), bg, pole, 3.2),
        "--accent-ink": readable(accent, bg, pole, 4.5),
        "--primary-ink": readable(primary, bg, pole, 4.5),
      };
      for (const [k, v] of Object.entries(vars)) root.style.setProperty(k, v);
    } else {
      root.dataset.base = preset.base;
    }
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.content = getComputedStyle(root).getPropertyValue("--bg").trim() || "#0b0d17";
  }

  function save(state) {
    try { localStorage.setItem(KEY, JSON.stringify(state)); } catch { /* storage disabled */ }
  }

  let state = load();
  apply(state);

  function previewFor(name) {
    const colors = name === "custom" ? [state.custom.bg, state.custom.primary, state.custom.accent, state.custom.primary] : THEMES[name].preview;
    return `<span class="preview" style="background:${colors[0]}">${colors.slice(1).map((c) => `<i style="background:${c}"></i>`).join("")}</span>`;
  }

  function hexToHsv(hex) {
    const [r, g, b] = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255);
    const max = Math.max(r, g, b), d = max - Math.min(r, g, b);
    let h = 0;
    if (d) {
      h = 60 * (max === r ? ((g - b) / d) % 6 : max === g ? (b - r) / d + 2 : (r - g) / d + 4);
      if (h < 0) h += 360;
    }
    return { h, s: max ? d / max : 0, v: max };
  }

  function hsvToHex(h, s, v) {
    const f = (n) => { const k = (n + h / 60) % 6; return v - v * s * Math.max(0, Math.min(k, 4 - k, 1)); };
    return "#" + [f(5), f(3), f(1)].map((x) => Math.round(x * 255).toString(16).padStart(2, "0")).join("");
  }

  function render(pop) {
    picker = null;
    pop.innerHTML = `
      <h4>Theme</h4>
      <div class="theme-grid">${Object.entries(THEMES).map(([id, t]) =>
        `<button type="button" class="theme-opt${state.name === id ? " active" : ""}" data-theme-id="${id}">${previewFor(id)}<span class="opt-name"><b>${t.label}</b><small>${STYLES[t.style || state.custom.style]}</small></span></button>`).join("")}
      </div>
      <div class="custom-box">
        <h4>Custom style</h4>
        <div class="tabs style-seg" role="radiogroup">${Object.entries(STYLES).map(([id, label]) =>
          `<button type="button" role="radio" aria-checked="${state.custom.style === id}" class="${state.custom.style === id ? "active" : ""}" data-custom-style="${id}">${id === "neumorph" ? "Neumorph" : label.replace("morph", "")}</button>`).join("")}
        </div>
        <h4>Custom colours</h4>
        ${COLOR_KEYS.map(([key, label]) => `<div class="custom-row"><span>${label}</span><button type="button" class="swatch-btn" data-pick="${key}" aria-label="Pick ${label.toLowerCase()} colour" aria-expanded="false" style="background:${state.custom[key]}"></button></div>`).join("")}
        <div class="row" style="margin-top:.8rem"><span class="muted" style="font-size:.72rem">Light or dark text is picked from the background.</span><span class="spacer"></span><button type="button" class="btn small" data-reset>Reset</button></div>
      </div>`;
  }

  let picker = null;
  let suppressClick = false;

  function setCustom(pop, key, hex) {
    state = { name: "custom", custom: { ...state.custom, [key]: hex } };
    apply(state); save(state);
    pop.querySelectorAll(".theme-opt").forEach((o) => o.classList.toggle("active", o.dataset.themeId === "custom"));
    const preview = pop.querySelector('[data-theme-id="custom"] .preview');
    if (preview) preview.outerHTML = previewFor("custom");
    const swatch = pop.querySelector(`[data-pick="${key}"]`);
    if (swatch) swatch.style.background = hex;
  }

  function paintPicker() {
    const { el, h, s, v } = picker;
    const hex = hsvToHex(h, s, v);
    el.style.setProperty("--h", h);
    Object.assign(el.querySelector(".cp-sv .cp-knob").style, { left: `${s * 100}%`, top: `${(1 - v) * 100}%`, background: hex });
    Object.assign(el.querySelector(".cp-hue .cp-knob").style, { left: `${(h / 360) * 100}%`, background: `hsl(${h} 100% 50%)` });
    const input = el.querySelector(".cp-hex");
    if (document.activeElement !== input) input.value = hex;
  }

  function dragArea(area, onMove) {
    area.addEventListener("pointerdown", (e) => {
      area.setPointerCapture(e.pointerId);
      const move = (ev) => {
        const r = area.getBoundingClientRect();
        onMove(Math.min(1, Math.max(0, (ev.clientX - r.left) / r.width)), Math.min(1, Math.max(0, (ev.clientY - r.top) / r.height)));
      };
      const up = () => {
        area.removeEventListener("pointermove", move);
        suppressClick = true;
        setTimeout(() => { suppressClick = false; });
      };
      move(e);
      area.addEventListener("pointermove", move);
      area.addEventListener("pointerup", up, { once: true });
      area.addEventListener("pointercancel", up, { once: true });
    });
  }

  function closePicker() {
    if (!picker) return;
    picker.btn.setAttribute("aria-expanded", "false");
    picker.el.remove();
    picker = null;
  }

  function openPicker(pop, btn) {
    closePicker();
    const key = btn.dataset.pick;
    const el = document.createElement("div");
    el.className = "cpick";
    el.innerHTML = `
      <div class="cp-sv"><i class="cp-knob"></i></div>
      <div class="cp-hue"><i class="cp-knob"></i></div>
      <div class="cp-foot">
        <input class="cp-hex" maxlength="7" spellcheck="false" autocomplete="off" aria-label="Hex colour">
        <div class="cp-presets">${PRESETS.map((c) => `<button type="button" data-hex="${c}" aria-label="${c}" style="background:${c}"></button>`).join("")}</div>
      </div>`;
    btn.closest(".custom-row").after(el);
    btn.setAttribute("aria-expanded", "true");
    picker = { key, el, btn, ...hexToHsv(state.custom[key]) };
    const commit = () => { setCustom(pop, key, hsvToHex(picker.h, picker.s, picker.v)); paintPicker(); };
    dragArea(el.querySelector(".cp-sv"), (x, y) => { picker.s = x; picker.v = 1 - y; commit(); });
    dragArea(el.querySelector(".cp-hue"), (x) => { picker.h = Math.min(x * 360, 359.9); commit(); });
    const useHex = (hex) => { Object.assign(picker, hexToHsv(hex)); setCustom(pop, key, hex.toLowerCase()); paintPicker(); };
    el.querySelector(".cp-hex").addEventListener("input", (e) => {
      const v = e.target.value.trim();
      const hex = v.startsWith("#") ? v : `#${v}`;
      if (HEX.test(hex)) useHex(hex);
    });
    el.querySelector(".cp-hex").addEventListener("blur", paintPicker);
    el.querySelectorAll("[data-hex]").forEach((b) => b.addEventListener("click", () => useHex(b.dataset.hex)));
    paintPicker();
  }

  function wire() {
    const btn = document.getElementById("themeBtn");
    const pop = document.getElementById("themePop");
    if (!btn || !pop) return;
    const close = () => { closePicker(); pop.hidden = true; btn.setAttribute("aria-expanded", "false"); };
    btn.addEventListener("click", () => {
      if (pop.hidden) { render(pop); pop.hidden = false; fit(); btn.setAttribute("aria-expanded", "true"); } else close();
    });
    // The topbar wraps on phones, so the popup's height budget depends on where the button sits.
    const fit = () => {
      if (pop.hidden) return;
      const top = btn.getBoundingClientRect().bottom + 11;
      pop.style.maxHeight = `${Math.max(220, window.innerHeight - top - 12)}px`;
    };
    window.addEventListener("resize", fit);
    document.addEventListener("click", (e) => {
      if (suppressClick || pop.hidden) return;
      // composedPath is fixed at dispatch, so it still includes pop after render() detached the clicked node.
      const path = e.composedPath();
      if (!path.includes(pop) && !path.includes(btn)) close();
      else if (picker && !path.includes(picker.el) && !e.target.closest("[data-pick]")) closePicker();
    });
    document.addEventListener("keydown", (e) => {
      if (e.key !== "Escape" || pop.hidden) return;
      if (picker) { const swatch = picker.btn; closePicker(); swatch.focus(); } else close();
    });
    pop.addEventListener("click", (e) => {
      const swatch = e.target.closest("[data-pick]");
      if (swatch) {
        if (picker && picker.key === swatch.dataset.pick) closePicker();
        else openPicker(pop, swatch);
        return;
      }
      const opt = e.target.closest("[data-theme-id]");
      if (opt) {
        state = { ...state, name: opt.dataset.themeId };
        apply(state); save(state); render(pop);
      }
      const seg = e.target.closest("[data-custom-style]");
      if (seg && STYLES[seg.dataset.customStyle]) {
        state = { name: "custom", custom: { ...state.custom, style: seg.dataset.customStyle } };
        apply(state); save(state); render(pop);
      }
      if (e.target.closest("[data-reset]")) {
        state = { ...state, name: "custom", custom: { ...DEFAULT_CUSTOM } };
        apply(state); save(state); render(pop);
      }
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", wire);
  else wire();
})();
