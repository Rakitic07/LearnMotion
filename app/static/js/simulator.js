import { $, $$, api, enableTabIndent, esc } from "./util.js";

export function renderSimulator(view, content, params) {
  const presets = content.presets;
  let preset = presets.find((p) => p.id === params.get("preset")) || presets[0];
  const customPod = params.get("custom") ? sessionStorage.getItem("sim-pod") : null;

  view.innerHTML = `
    <section class="topic-hero clay">
      <div class="code tint-lilac">KS</div>
      <div>
        <h1>Scheduler Lab</h1>
        <div class="muted">A teaching model of kube-scheduler's <b>filter → score → bind</b>. Edit real Pod/Deployment YAML and see, node by node, why each replica lands where it does. No cluster needed.</div>
      </div>
      <a class="btn" href="#/k8s/playground">Try for real on Kind →</a>
    </section>
    <div class="sim-layout" style="margin-top:1.4rem">
      <div class="grid">
        <div class="panel clay">
          <h3>Puzzles</h3>
          <div class="preset-list" id="presetList">
            ${presets.map((p) => `<button class="btn small ${p.id === preset.id ? "active" : ""}" data-id="${p.id}">${esc(p.title)}</button>`).join("")}
          </div>
          <div class="lab-step" id="hint" style="margin-top:1rem"></div>
        </div>
        <div class="panel clay">
          <div class="row">
            <div class="tabs" id="edTabs"><button data-t="pod" class="active">Workload YAML</button><button data-t="nodes">Nodes YAML</button></div>
            <span class="spacer"></span>
            <button class="btn primary" id="runBtn">Schedule</button>
          </div>
          <textarea class="code" id="podYaml" spellcheck="false" style="margin-top:.9rem"></textarea>
          <textarea class="code" id="nodesYaml" spellcheck="false" style="margin-top:.9rem; display:none"></textarea>
          <p class="muted" style="font-size:.78rem">Supports nodeSelector, nodeAffinity, pod (anti-)affinity, tolerations, requests, topologySpreadConstraints (incl. nodeTaintsPolicy), nodeName and cordoned nodes. Ctrl/Cmd+Enter to run.</p>
        </div>
      </div>
      <div id="results"><div class="panel clay muted">Press <b>Schedule</b> to run the simulation.</div></div>
    </div>`;

  const podTa = $("#podYaml");
  const nodesTa = $("#nodesYaml");
  [podTa, nodesTa].forEach((ta) => {
    enableTabIndent(ta);
    ta.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) run();
    });
  });

  const load = (p, podOverride) => {
    preset = p;
    podTa.value = podOverride || p.pod;
    nodesTa.value = p.nodes;
    $("#hint").innerHTML = `<b>Challenge:</b> ${esc(p.hint)}`;
    $$("#presetList button").forEach((b) => b.classList.toggle("active", b.dataset.id === p.id));
    run();
  };

  $("#presetList").addEventListener("click", (e) => {
    const id = e.target.dataset.id;
    if (id) load(presets.find((p) => p.id === id));
  });
  $("#edTabs").addEventListener("click", (e) => {
    const t = e.target.dataset.t;
    if (!t) return;
    $$("#edTabs button").forEach((b) => b.classList.toggle("active", b === e.target));
    podTa.style.display = t === "pod" ? "" : "none";
    nodesTa.style.display = t === "nodes" ? "" : "none";
  });
  $("#runBtn").onclick = () => run();

  async function run() {
    const res = await api("/api/simulate", { nodes: nodesTa.value, pod: podTa.value });
    if (!res.ok) {
      $("#results").innerHTML = `<div class="panel clay"><h3>Couldn't simulate</h3><div class="event-box">${esc(res.error)}</div></div>`;
      return;
    }
    renderResult(res);
  }

  function renderResult(res) {
    const pending = res.placements.findIndex((p) => !p.node);
    let selected = pending >= 0 ? pending : res.placements.length - 1;
    const all = res.placements.length === res.placements.filter((p) => p.node).length;

    $("#results").innerHTML = `
      <div class="panel clay">
        <div class="row">
          <h3 style="margin:0">${esc(res.workload.kind)} / ${esc(res.workload.name)}</h3>
          <span class="pill ${all ? "ok" : "bad"}">${esc(res.summary)}</span>
          <span class="pill neutral">requests ${res.workload.cpu}m cpu · ${res.workload.memory}Mi</span>
        </div>
        <p class="muted" style="margin:.6rem 0">Pick a replica to see the scheduler's reasoning at that moment. Earlier replicas already occupy their nodes, which matters for anti-affinity and spreading.</p>
        <div class="row" id="replicas">${res.placements.map((p, i) => `<button class="btn small ${p.node ? "" : "danger"}" data-i="${i}">${esc(p.replica)} → ${esc(p.node || "Pending")}</button>`).join("")}</div>
        <div id="detail"></div>
      </div>`;

    const showReplica = (i) => {
      selected = i;
      $$("#replicas button").forEach((b) => b.classList.toggle("active", +b.dataset.i === i));
      const pl = res.placements[i];
      const before = res.placements.slice(0, i);
      $("#detail").innerHTML = `
        ${pl.message ? `<div class="event-box"><b>Warning FailedScheduling</b><br>${esc(pl.message)}</div>` : `<div class="lab-step done" style="margin-top:.8rem"><b>Bound to ${esc(pl.node)}</b>: highest total score among feasible nodes.</div>`}
        <div class="sim-nodes">${res.nodes.map((n) => {
          const verdict = pl.nodes.find((v) => v.name === n.name);
          const placedBefore = before.filter((b) => b.node === n.name);
          const bd = verdict.breakdown || {};
          return `<div class="sim-node clay spot ${pl.node === n.name ? "chosen" : ""} ${verdict.feasible ? "" : "infeasible"}">
            <div class="row"><b>${esc(n.name)}</b><span class="spacer"></span>${verdict.feasible ? `<span class="pill ok">feasible${verdict.score !== undefined ? ` · ${verdict.score}` : ""}</span>` : `<span class="pill bad">filtered</span>`}</div>
            <div style="margin:.4rem 0">${Object.entries(n.labels).map(([k, v]) => `<span class="chip${k.includes("zone") ? " zone" : ""}" title="${esc(k)}=${esc(v)}">${esc(k.replace("topology.kubernetes.io/", ""))}=${esc(v)}</span>`).join("")}
              ${n.taints.map((t) => `<span class="chip taint">${esc(t)}</span>`).join("")}
              ${n.unschedulable ? `<span class="chip taint">cordoned</span>` : ""}</div>
            <div class="muted" style="font-size:.72rem">${n.cpu}m cpu · ${n.memory}Mi allocatable</div>
            <div class="pods">
              ${n.pods.map((p) => `<span class="sim-pod" title="${esc(JSON.stringify(p.labels))}">${esc(p.name)}</span>`).join("")}
              ${placedBefore.map((p) => `<span class="sim-pod">${esc(p.replica)}</span>`).join("")}
              ${pl.node === n.name ? `<span class="sim-pod new">${esc(pl.replica)}</span>` : ""}
            </div>
            <ul class="clean reasons" style="margin-top:.6rem">
              ${verdict.failures.map((f) => `<li class="fail">${esc(f)}</li>`).join("")}
              ${verdict.passed.map((f) => `<li>${esc(f)}</li>`).join("")}
            </ul>
            ${Object.keys(bd).length ? `<div class="score-bars">${Object.entries(bd).map(([k, v]) => `<div><span>${esc(k)}</span><i style="width:${Math.max(4, v)}%"></i><b>${v}</b></div>`).join("")}</div>` : ""}
          </div>`;
        }).join("")}</div>`;
    };
    $("#replicas").addEventListener("click", (e) => {
      if (e.target.dataset.i !== undefined) showReplica(+e.target.dataset.i);
    });
    showReplica(selected);
  }

  load(preset, customPod);
}
