import { esc } from "./util.js";
import { animSpeed, bindSpeed } from "./settings.js";

const POD_W = 56;
const POD_H = 64;
const BALL = 42;

export const COLORS = {
  sky: "#8cc3ff", mint: "#6ee8bd", lilac: "#bba8ff", peach: "#ffab85", lemon: "#ffd76a",
  rose: "#ff8fb1", slate: "#aab0d6", blue: "#6aa8ff", green: "#46e0aa", orange: "#ff9a5c",
  purple: "#a98bff", pink: "#ff7ab6", gray: "#8d93b8",
};

const KIND_TINT = {
  Deployment: "sky", ReplicaSet: "sky", StatefulSet: "sky", DaemonSet: "sky", Pod: "sky",
  Service: "mint", EndpointSlice: "mint", HPA: "mint", ServiceAccount: "mint",
  ConfigMap: "lemon", StorageClass: "lemon", CronJob: "lemon", RoleBinding: "lemon", LimitRange: "lemon",
  Secret: "rose", NetworkPolicy: "rose", Event: "rose", ResourceQuota: "rose",
  VPA: "lilac", PV: "lilac", Role: "lilac", ClusterRole: "lilac", Scheduler: "lilac", Rule: "lilac",
  PDB: "peach", Ingress: "peach", Job: "peach", Controller: "peach",
  PVC: "sky",
};

// Re-inserting an element restarts its CSS entry animation, so only move what is out of place.
function syncOrder(parent, els) {
  els.forEach((node, i) => {
    const live = [...parent.children].filter((c) => !c.classList.contains("leaving"));
    if (live[i] !== node) parent.insertBefore(node, live[i] || null);
  });
}

/**
 * Plays a list of declarative cluster states with smooth transitions.
 * State: { title, text, nodes[], pods[], cards[], links[], meter?, queue?, highlight[] }
 */
export class ScenePlayer {
  constructor(container, scene) {
    this.scene = scene;
    this.steps = scene.steps;
    this.i = 0;
    this.speed = animSpeed();
    this.playing = true;
    this.podEls = new Map();
    this.cardEls = new Map();
    this.nodeEls = new Map();
    this.podTargets = new Map();

    container.innerHTML = `
      <div class="scene clay">
        <div class="scene-head">
          <h3 style="margin:0">Animated walkthrough</h3>
          <span class="pill neutral">${this.steps.length} steps</span>
          <span class="spacer"></span>
          <span class="muted" style="font-size:.8rem">Pods glide between nodes as the cluster changes</span>
        </div>
        <div class="stage">
          <svg class="links"></svg>
          <div class="cards-row" data-row="1"></div>
          <div class="cluster-row">
            <div class="queue"><div class="title"><span>Scheduling queue</span></div><div class="body"></div></div>
            <div class="nodes"></div>
          </div>
          <div class="cards-row" data-row="2" style="margin-top:1rem"></div>
          <div class="pods-layer"></div>
          <div class="meter clay" hidden></div>
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
    this.stage = q(".stage");
    this.svg = q("svg.links");
    this.rows = { 1: q('.cards-row[data-row="1"]'), 2: q('.cards-row[data-row="2"]') };
    this.clusterRow = q(".cluster-row");
    this.queueEl = q(".queue");
    this.nodesEl = q(".nodes");
    this.podsLayer = q(".pods-layer");
    this.meterEl = q(".meter");
    this.captionNo = q(".caption .stepno");
    this.captionTitle = q(".caption h4");
    this.captionText = q(".caption p");
    this.playBtn = q('[data-act="play"]');
    this.dots = q(".dots");

    this.dots.innerHTML = this.steps.map((_, i) => `<button title="Step ${i + 1}" data-i="${i}"></button>`).join("");
    this.dots.addEventListener("click", (e) => {
      const i = e.target.dataset.i;
      if (i !== undefined) this.pause(), this.go(+i);
    });
    q('[data-act="prev"]').onclick = () => (this.pause(), this.go(this.i - 1));
    q('[data-act="next"]').onclick = () => (this.pause(), this.go(this.i + 1));
    this.playBtn.onclick = () => (this.playing ? this.pause() : this.play());
    q('[data-act="speed"]').onchange = (e) => {
      this.speed = +e.target.value;
      if (this.playing) this.schedule();
    };
    this.unbindSpeed = bindSpeed(this, q('[data-act="speed"]'), () => this.playing && this.schedule());

    this.ro = new ResizeObserver(() => this.layout(false));
    this.ro.observe(this.stage);
    this.go(0);
  }

  destroy() {
    this.unbindSpeed();
    clearTimeout(this.timer);
    clearTimeout(this.relayoutTimer);
    this.ro.disconnect();
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
    const dur = (this.state.duration || 4200) / this.speed;
    this.timer = setTimeout(() => {
      if (this.i < this.steps.length - 1) this.go(this.i + 1);
      else this.pause();
    }, dur);
  }

  go(i) {
    this.i = Math.max(0, Math.min(this.steps.length - 1, i));
    this.state = this.steps[this.i];
    this.renderCards();
    this.renderNodes();
    this.renderMeter();
    this.captionNo.textContent = this.i + 1;
    this.captionTitle.textContent = this.state.title || "";
    this.captionText.innerHTML = this.state.text || "";
    [...this.dots.children].forEach((d, k) => d.classList.toggle("active", k === this.i));
    requestAnimationFrame(() => this.layout(true));
    clearTimeout(this.relayoutTimer);
    this.relayoutTimer = setTimeout(() => this.layout(false), 520);
    if (this.playing) this.schedule();
    else this.playBtn.textContent = this.i >= this.steps.length - 1 ? "Replay" : "Play";
  }

  // ------------------------------------------------------------------ cards
  renderCards() {
    const cards = this.state.cards || [];
    const hl = new Set(this.state.highlight || []);
    const keep = new Set(cards.map((c) => c.id));
    for (const [id, node] of this.cardEls) {
      if (!keep.has(id)) {
        node.classList.add("leaving");
        this.cardEls.delete(id);
        setTimeout(() => node.remove(), 420);
      }
    }
    for (const row of [1, 2]) {
      const rowCards = cards.filter((c) => (c.row || 1) === row);
      rowCards.forEach((c) => {
        let node = this.cardEls.get(c.id);
        if (!node) {
          node = document.createElement("div");
          node.dataset.id = c.id;
          this.cardEls.set(c.id, node);
        }
        const tint = c.tint || KIND_TINT[c.kind] || "slate";
        node.className = `kcard tint-${tint}${hl.has(c.id) ? " highlight" : ""}`;
        node.innerHTML = `<div class="kind">${esc(c.kind)}</div><div class="name">${esc(c.name)}</div>${(c.lines || []).map((l) => `<div class="line" title="${esc(l)}">${esc(l)}</div>`).join("")}`;
      });
      syncOrder(this.rows[row], rowCards.map((c) => this.cardEls.get(c.id)));
    }
  }

  // ------------------------------------------------------------------ nodes
  renderNodes() {
    const nodes = this.state.nodes || [];
    const pods = this.state.pods || [];
    const hl = new Set(this.state.highlight || []);
    const showQueue = this.state.queue === true || pods.some((p) => p.node === "queue");
    this.queueEl.style.display = showQueue ? "" : "none";
    this.clusterRow.style.display = nodes.length || showQueue ? "" : "none";
    this.stage.classList.toggle("no-cluster", !nodes.length && !showQueue);

    const keep = new Set(nodes.map((n) => n.id));
    for (const [id, node] of this.nodeEls) {
      if (!keep.has(id)) {
        node.remove();
        this.nodeEls.delete(id);
      }
    }
    nodes.forEach((n) => {
      let node = this.nodeEls.get(n.id);
      if (!node) {
        node = document.createElement("div");
        node.dataset.id = n.id;
        node.innerHTML = `<div class="title"></div><div class="chips"></div><div class="body"></div>`;
        this.nodeEls.set(n.id, node);
      }
      const status = n.status || "ready";
      node.className = `knode ${status}${n.mark === "no" ? " marked-no" : ""}${hl.has(n.id) ? " highlight" : ""}`;
      node.querySelector(".title").innerHTML =
        `<span>${esc(n.name)}</span><span class="state-pill ${status}">${status === "ready" || status === "new" ? "Ready" : status === "cordoned" ? "Cordoned" : "NotReady"}</span>`;
      node.querySelector(".chips").innerHTML =
        (n.labels || []).map((l) => `<span class="chip${l.startsWith("zone") ? " zone" : ""}">${esc(l)}</span>`).join("") +
        (n.taints || []).map((t) => `<span class="chip taint">taint ${esc(t)}</span>`).join("");
      node.querySelectorAll(".mark, .score").forEach((x) => x.remove());
      if (n.mark) node.insertAdjacentHTML("beforeend", `<div class="mark ${n.mark}">${n.mark === "ok" ? "&#10003;" : "&#10005;"}</div>`);
      if (n.score !== undefined) node.insertAdjacentHTML("beforeend", `<div class="score">${esc(n.score)}</div>`);
    });
    syncOrder(this.nodesEl, nodes.map((n) => this.nodeEls.get(n.id)));
  }

  renderMeter() {
    const m = this.state.meter;
    if (!m) {
      this.meterEl.hidden = true;
      return;
    }
    this.meterEl.hidden = false;
    const v = Math.min(100, m.value);
    this.meterEl.innerHTML = `
      <div class="lbl"><span>${esc(m.label)}</span><span>${esc(m.display ?? m.value + "%")}</span></div>
      <div class="bar"><div class="fill" style="width:${v}%"></div>${m.target !== undefined ? `<div class="target" style="left:calc(${Math.min(100, m.target)}% - 1px)" title="target"></div>` : ""}</div>
      ${m.target !== undefined ? `<div class="lbl muted" style="margin-top:.35rem"><span>target</span><span>${esc(m.target)}%</span></div>` : ""}`;
  }

  // ------------------------------------------------------------------ pods + links
  relRect(node) {
    const s = this.stage.getBoundingClientRect();
    const r = node.getBoundingClientRect();
    return { x: r.left - s.left, y: r.top - s.top, w: r.width, h: r.height };
  }

  layout(animate) {
    if (!this.state) return;
    const pods = this.state.pods || [];
    const hl = new Set(this.state.highlight || []);
    const groups = new Map();
    pods.forEach((p) => {
      if (!groups.has(p.node)) groups.set(p.node, []);
      groups.get(p.node).push(p);
    });

    // grow node bodies to fit their pods before measuring
    const bodyFor = (id) => (id === "queue" ? this.queueEl.querySelector(".body") : this.nodeEls.get(id)?.querySelector(".body"));
    for (const [id, list] of groups) {
      const body = bodyFor(id);
      if (!body) continue;
      const cols = Math.max(1, Math.floor((body.clientWidth - 8) / POD_W));
      body.style.minHeight = `${Math.max(140, Math.ceil(list.length / cols) * POD_H + 14)}px`;
    }

    this.podTargets.clear();
    for (const [id, list] of groups) {
      const body = bodyFor(id);
      if (!body) continue;
      const r = this.relRect(body);
      const cols = Math.max(1, Math.floor((r.w - 8) / POD_W));
      const used = Math.min(cols, list.length);
      const offset = (r.w - used * POD_W) / 2;
      list.forEach((p, k) => {
        const col = k % cols;
        const row = Math.floor(k / cols);
        this.podTargets.set(p.id, { x: r.x + offset + col * POD_W, y: r.y + 8 + row * POD_H });
      });
    }

    const keep = new Set(pods.map((p) => p.id));
    for (const [id, node] of this.podEls) {
      if (!keep.has(id) || !this.podTargets.has(id)) {
        node.classList.add("leaving");
        this.podEls.delete(id);
        setTimeout(() => node.remove(), 500);
      }
    }

    pods.forEach((p) => {
      const t = this.podTargets.get(p.id);
      if (!t) return;
      let node = this.podEls.get(p.id);
      const fresh = !node;
      if (fresh) {
        node = document.createElement("div");
        node.innerHTML = `<div class="ball"><span></span></div><div class="pname"></div>`;
        node.style.transition = "none";
        node.style.transform = `translate(${t.x}px, ${t.y}px)`;
        node.classList.add("entering");
        this.podsLayer.appendChild(node);
        this.podEls.set(p.id, node);
        node.getBoundingClientRect();
        node.style.transition = "";
        requestAnimationFrame(() => node.classList.remove("entering"));
      }
      node.className = `pod ${p.status || "running"}${hl.has(p.id) ? " highlight" : ""}${fresh ? " entering" : ""}`;
      if (fresh) requestAnimationFrame(() => node.classList.remove("entering"));
      if (!animate) node.style.transition = "none";
      node.style.transform = `translate(${t.x}px, ${t.y}px)`;
      if (!animate) {
        node.getBoundingClientRect();
        node.style.transition = "";
      }
      const ball = node.querySelector(".ball");
      const size = Math.round(BALL * (p.size || 1));
      ball.style.width = ball.style.height = `${size}px`;
      ball.style.background = COLORS[p.color] || p.color || COLORS.sky;
      ball.querySelector("span").textContent = p.tag || "";
      node.querySelector(".pname").textContent = p.name || p.id;
      node.title = `${p.name || p.id} — ${p.status || "running"}`;
    });

    this.drawLinks();
  }

  anchor(id) {
    const t = this.podTargets.get(id);
    if (t) return { x: t.x + POD_W / 2 - BALL / 2, y: t.y, w: BALL, h: BALL, kind: "pod", cx: t.x + POD_W / 2 };
    const node = this.cardEls.get(id) || this.nodeEls.get(id);
    if (!node || !node.isConnected) return null;
    const r = this.relRect(node);
    return { ...r, cx: r.x + r.w / 2 };
  }

  drawLinks() {
    const links = this.state.links || [];
    const parts = [];
    let sideways = 0;
    links.forEach((l) => {
      const a = this.anchor(l.from);
      const b = this.anchor(l.to);
      if (!a || !b) return;
      let x1, y1, x2, y2, d;
      let lift = 0;
      const ay = a.y + a.h / 2;
      const by = b.y + b.h / 2;
      if (Math.abs(ay - by) < 30) {
        const leftToRight = a.cx < b.cx;
        x1 = leftToRight ? a.x + a.w : a.x;
        x2 = leftToRight ? b.x : b.x + b.w;
        y1 = ay;
        y2 = by;
        // Fan out parallel sideways links so they don't overlap.
        lift = 34 + (sideways++ % 4) * 26;
        d = `M${x1},${y1} C${x1 + (x2 - x1) / 4},${y1 - lift} ${x2 - (x2 - x1) / 4},${y2 - lift} ${x2},${y2}`;
      } else {
        const down = by > ay;
        x1 = a.cx;
        y1 = down ? a.y + a.h : a.y;
        x2 = b.cx;
        y2 = down ? b.y : b.y + b.h;
        const dy = (y2 - y1) / 2;
        d = `M${x1},${y1} C${x1},${y1 + dy} ${x2},${y2 - dy} ${x2},${y2}`;
      }
      const mx = (x1 + x2) / 2;
      const my = (y1 + y2) / 2 - lift * 0.75;
      parts.push(`<path class="${esc(l.style || "flow")}" d="${d}"/>`);
      if (l.style === "blocked") parts.push(`<text class="x" x="${mx - 5}" y="${my + 5}">&#10005;</text>`);
      if (l.label) parts.push(`<text x="${mx + 8}" y="${my - 6}">${esc(l.label)}</text>`);
    });
    this.svg.innerHTML = parts.join("");
  }
}
