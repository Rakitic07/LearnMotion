// Clay replacements for native form controls. The native <select> stays in the DOM (hidden),
// so existing code that reads/writes .value or listens for "change" keeps working.

const valueDesc = Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, "value");
const indexDesc = Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, "selectedIndex");
let openSelect = null;

function closeOpen() {
  if (openSelect) openSelect.close();
}

function enhanceSelect(sel) {
  sel.dataset.clay = "1";
  const wrap = document.createElement("div");
  wrap.className = "cselect";
  // Layout classes such as "jx-mobile" must apply to the visible wrapper, not only the hidden <select>.
  wrap.classList.add(...sel.classList);
  if (sel.style.width) wrap.style.width = sel.style.width;
  sel.style.width = "";
  sel.parentNode.insertBefore(wrap, sel);
  wrap.appendChild(sel);

  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "cselect-btn";
  btn.setAttribute("aria-haspopup", "listbox");
  btn.setAttribute("aria-expanded", "false");
  if (sel.id) btn.setAttribute("aria-label", sel.getAttribute("aria-label") || sel.id);
  const label = document.createElement("span");
  label.className = "cselect-label";
  const chev = document.createElement("span");
  chev.className = "cselect-chev";
  btn.append(label, chev);

  const list = document.createElement("ul");
  list.className = "cselect-list clay";
  list.setAttribute("role", "listbox");
  list.hidden = true;
  wrap.append(btn, list);

  let active = -1;

  function sync() {
    const opt = sel.options[sel.selectedIndex];
    label.textContent = opt ? opt.textContent : "";
  }

  function build() {
    list.replaceChildren(...[...sel.options].map((o, i) => {
      const li = document.createElement("li");
      li.setAttribute("role", "option");
      li.dataset.i = i;
      li.textContent = o.textContent;
      li.setAttribute("aria-selected", String(i === sel.selectedIndex));
      if (o.disabled) li.setAttribute("aria-disabled", "true");
      return li;
    }));
  }

  function highlight(i) {
    const items = list.children;
    if (!items.length) return;
    active = (i + items.length) % items.length;
    [...items].forEach((li, n) => li.classList.toggle("active", n === active));
    items[active].scrollIntoView({ block: "nearest" });
  }

  function choose(i) {
    if (sel.options[i]?.disabled) return;
    const changed = i !== sel.selectedIndex;
    indexDesc.set.call(sel, i);
    sync();
    api.close();
    btn.focus();
    if (changed) sel.dispatchEvent(new Event("change", { bubbles: true }));
  }

  const api = {
    wrap,
    open() {
      closeOpen();
      build();
      list.hidden = false;
      const below = window.innerHeight - btn.getBoundingClientRect().bottom;
      wrap.classList.toggle("up", below < Math.min(list.scrollHeight, 300) + 16);
      btn.setAttribute("aria-expanded", "true");
      wrap.classList.add("open");
      highlight(Math.max(0, sel.selectedIndex));
      openSelect = api;
    },
    close() {
      list.hidden = true;
      wrap.classList.remove("open");
      btn.setAttribute("aria-expanded", "false");
      if (openSelect === api) openSelect = null;
    },
  };

  btn.addEventListener("click", () => {
    if (list.hidden) api.open(); else api.close();
  });
  list.addEventListener("click", (e) => {
    const li = e.target.closest("li[data-i]");
    if (li) choose(+li.dataset.i);
  });
  list.addEventListener("mousemove", (e) => {
    const li = e.target.closest("li[data-i]");
    if (li && +li.dataset.i !== active) highlight(+li.dataset.i);
  });
  btn.addEventListener("keydown", (e) => {
    const isOpen = !list.hidden;
    if (e.key === "ArrowDown" || e.key === "ArrowUp") {
      e.preventDefault();
      if (!isOpen) api.open(); else highlight(active + (e.key === "ArrowDown" ? 1 : -1));
    } else if ((e.key === "Enter" || e.key === " ") && isOpen) {
      e.preventDefault();
      choose(active);
    } else if (e.key === "Escape" && isOpen) {
      e.preventDefault();
      api.close();
    } else if (e.key === "Tab" && isOpen) {
      api.close();
    } else if (e.key.length === 1 && /\S/.test(e.key)) {
      const start = isOpen ? active + 1 : sel.selectedIndex + 1;
      const opts = [...sel.options];
      const hit = [...opts.slice(start), ...opts.slice(0, start)].find((o) => o.textContent.trim().toLowerCase().startsWith(e.key.toLowerCase()));
      if (hit) isOpen ? highlight(hit.index) : choose(hit.index);
    }
  });

  Object.defineProperty(sel, "value", {
    configurable: true,
    get() { return valueDesc.get.call(this); },
    set(v) { valueDesc.set.call(this, v); sync(); },
  });
  Object.defineProperty(sel, "selectedIndex", {
    configurable: true,
    get() { return indexDesc.get.call(this); },
    set(v) { indexDesc.set.call(this, v); sync(); },
  });
  sel.addEventListener("change", sync);
  sync();
}

function paintRange(input) {
  const min = +input.min || 0;
  const max = input.max === "" ? 100 : +input.max;
  input.style.setProperty("--fill", `${((+input.value - min) / (max - min || 1)) * 100}%`);
}

function enhance(root) {
  root.querySelectorAll?.("select:not([data-clay]):not([multiple])").forEach(enhanceSelect);
  root.querySelectorAll?.('input[type="range"]').forEach(paintRange);
}

export function initControls() {
  enhance(document);
  new MutationObserver((records) => {
    for (const r of records) for (const n of r.addedNodes) if (n.nodeType === 1) {
      if (n.matches?.("select:not([data-clay])")) enhanceSelect(n);
      else enhance(n);
    }
  }).observe(document.body, { childList: true, subtree: true });
  document.addEventListener("input", (e) => { if (e.target.matches?.('input[type="range"]')) paintRange(e.target); });
  document.addEventListener("click", (e) => {
    if (openSelect && !e.composedPath().includes(openSelect.wrap)) closeOpen();
  });
  window.addEventListener("hashchange", closeOpen);
}
