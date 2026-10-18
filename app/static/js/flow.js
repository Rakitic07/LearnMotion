import { esc } from "./util.js";
import { COLORS } from "./scene.js";
import { animSpeed, bindSpeed } from "./settings.js";

const reduceMotion = () => matchMedia("(prefers-reduced-motion: reduce)").matches;

/**
 * Plays a declarative flow: nodes placed at x/y percentages, links between them, and steps that
 * highlight nodes, patch node properties (cumulatively) and fly labelled packets along links.
 */
export class FlowPlayer {
  constructor(container, flow, { title = "Animated walkthrough", hint = "Packets show what moves where at each step" } = {}) {
    this.flow = flow;
    this.steps = flow.steps;
    this.i = 0;
    this.speed = animSpeed();
    this.playing = true;
    this.anims = [];
    container.innerHTML = `
      <div class="scene clay flow">
        <div class="scene-head">
          <h3 style="margin:0">${esc(title)}</h3>
          <span class="pill neutral">${this.steps.length} steps</span>
          <span class="spacer"></span>
          <span class="muted" style="font-size:.8rem">${esc(hint)}</span>
        </div>
        <div class="stage flow-stage">
          <svg class="links flow-links"></svg>
          <div class="flow-nodes"></div>
          <div class="flow-packets"></div>
        </div>
        <div class="caption clay">
          <div class="stepno">1</div>
          <div><h4></h4><p></p></div>
        </div>
        <div class="controls">
          <button class="btn small" data-act="prev">Prev</button>
          <button class="btn small primary" data-act="play">Pause</button>
          <button class="btn small" data-act="next">Next</button>
          <div class="dots"></div>
          <span class="spacer"></span>
          <label class="muted" style="font-size:.8rem">Speed
            <select data-act="speed"><option value="0.6">0.6×</option><option value="1" selected>1×</option><option value="1.6">1.6×</option></select>
          </label>
        </div>
      </div>`;
    const q = (s) => container.querySelector(s);
    this.stage = q(".flow-stage");
    this.svg = q(".flow-links");
    this.nodesEl = q(".flow-nodes");
    this.packetsEl = q(".flow-packets");
    this.captionNo = q(".caption .stepno");
    this.captionTitle = q(".caption h4");
    this.captionText = q(".caption p");
    this.playBtn = q('[data-act="play"]');
    this.dots = q(".dots");
    this.nodeEls = new Map();

    this.dots.innerHTML = this.steps.map((_, i) => `<button title="Step ${i + 1}" data-i="${i}"></button>`).join("");
    this.dots.addEventListener("click", (e) => {
      const i = e.target.dataset.i;
      if (i !== undefined) this.pause(), this.go(+i);
    });
    q('[data-act="prev"]').onclick = () => (this.pause(), this.go(this.i - 1));
    q('[data-act="next"]').onclick = () => (this.pause(), this.go(this.i + 1));
    this.playBtn.onclick = () => (this.playing ? this.pause() : this.play());
    const respeed = () => {
      this.renderPackets();
      if (this.playing) this.schedule();
    };
    q('[data-act="speed"]').onchange = (e) => {
      this.speed = +e.target.value;
      respeed();
    };
    this.unbindSpeed = bindSpeed(this, q('[data-act="speed"]'), respeed);

    this.ro = new ResizeObserver(() => this.layout());
    this.ro.observe(this.stage);
    this.go(0);
  }

  destroy() {
    this.unbindSpeed();
    clearTimeout(this.timer);
    this.ro.disconnect();
    this.anims.forEach((a) => a.cancel());
  }

  play() {
    if (this.i >= this.steps.length - 1) this.go(0);
    this.playing = true;
    this.playBtn.textContent = "Pause";
    this.schedule();
  }

  pause() {
    this.playing = false;
    this.playBtn.textContent = this.i >= this.steps.length - 1 ? "Replay" : "Play";
    clearTimeout(this.timer);
  }

  schedule() {
    clearTimeout(this.timer);
    const s = this.steps[this.i];
    const dur = Math.max(3800, (s.text || "").length * 42) / this.speed;
    this.timer = setTimeout(() => {
      if (this.i < this.steps.length - 1) this.go(this.i + 1);
      else this.pause();
    }, dur);
  }

  /** Node properties after applying every step's `set` up to and including step i. */
  stateAt(i) {
    const nodes = new Map(this.flow.nodes.map((n) => [n.id, { ...n }]));
    for (let k = 0; k <= i; k++) {
      for (const [id, patch] of Object.entries(this.steps[k].set || {})) {
        if (nodes.has(id)) Object.assign(nodes.get(id), patch);
      }
    }
    return nodes;
  }

  go(i) {
    this.i = Math.max(0, Math.min(this.steps.length - 1, i));
    const s = this.steps[this.i];
    this.nodes = this.stateAt(this.i);
    this.active = new Set(s.active);
    this.captionNo.textContent = this.i + 1;
    this.captionTitle.textContent = s.title || "";
    this.captionText.innerHTML = s.text || "";
    [...this.dots.children].forEach((d, k) => d.classList.toggle("active", k === this.i));
    this.renderNodes();
    this.layout();
    if (this.playing) this.schedule();
    else this.playBtn.textContent = this.i >= this.steps.length - 1 ? "Replay" : "Play";
  }

  renderNodes() {
    const anyActive = this.active.size > 0;
    for (const n of this.nodes.values()) {
      let el = this.nodeEls.get(n.id);
      if (!el) {
        el = document.createElement("div");
        el.innerHTML = `<b></b><small></small>`;
        this.nodesEl.appendChild(el);
        this.nodeEls.set(n.id, el);
      }
      el.className = `fnode shape-${n.shape || "box"} tint-${n.tint || "sky"}${this.active.has(n.id) ? " on" : anyActive ? " dim" : ""}${n.hidden ? " gone" : ""}`;
      el.style.left = `${n.x}%`;
      el.style.top = `${n.y}%`;
      el.querySelector("b").textContent = n.label;
      const sub = el.querySelector("small");
      sub.textContent = n.sub || "";
      sub.hidden = !n.sub;
    }
  }

  center(id) {
    const n = this.nodes.get(id);
    if (!n) return null;
    return { x: (n.x / 100) * this.w, y: (n.y / 100) * this.h };
  }

  layout() {
    if (!this.nodes) return;
    this.w = this.stage.clientWidth;
    this.h = this.stage.clientHeight;
    const parts = [];
    const visible = (id) => this.nodes.get(id) && !this.nodes.get(id).hidden;
    for (const [a, b, label] of this.flow.links) {
      if (!visible(a) || !visible(b)) continue;
      const p = this.center(a);
      const q = this.center(b);
      const hot = this.active.has(a) && this.active.has(b);
      const curve = Math.abs(p.y - q.y) < 8 ? 0 : (q.x - p.x) * 0.15;
      parts.push(`<path class="${hot ? "flow" : "dashed"}" d="M${p.x},${p.y} C${p.x + curve},${(p.y + q.y) / 2} ${q.x - curve},${(p.y + q.y) / 2} ${q.x},${q.y}"/>`);
      if (label) parts.push(`<text x="${(p.x + q.x) / 2 + 6}" y="${(p.y + q.y) / 2 - 6}">${esc(label)}</text>`);
    }
    this.svg.innerHTML = parts.join("");
    this.renderPackets();
  }

  renderPackets() {
    this.anims.forEach((a) => a.cancel());
    this.anims = [];
    this.packetsEl.innerHTML = "";
    const packets = (this.steps[this.i]?.packets || []).filter((p) => this.nodes.get(p.from) && this.nodes.get(p.to));
    packets.forEach((p, k) => {
      const a = this.center(p.from);
      const b = this.center(p.to);
      const el = document.createElement("div");
      el.className = `packet${p.label ? "" : " dot"}`;
      el.textContent = p.label || "";
      el.style.setProperty("--pc", COLORS[p.tint] || "var(--accent)");
      this.packetsEl.appendChild(el);
      const from = `translate(${a.x}px, ${a.y}px) translate(-50%, -50%)`;
      const to = `translate(${b.x}px, ${b.y}px) translate(-50%, -50%)`;
      if (reduceMotion()) {
        el.style.transform = `translate(${(a.x + b.x) / 2}px, ${(a.y + b.y) / 2}px) translate(-50%, -50%)`;
        return;
      }
      const dur = 2300 / this.speed;
      this.anims.push(el.animate([
        { transform: from, opacity: 0, offset: 0 },
        { transform: from, opacity: 1, offset: 0.08 },
        { transform: to, opacity: 1, offset: 0.62 },
        { transform: to, opacity: 0, offset: 0.78 },
        { transform: to, opacity: 0, offset: 1 },
      ], { duration: dur, delay: (k * 380) / this.speed, iterations: Infinity, easing: "cubic-bezier(.45,0,.2,1)", fill: "both" }));
    });
  }
}
