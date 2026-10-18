import { $, $$, api, enableTabIndent, esc, levelPill, store, toast } from "./util.js";
import { COLORS } from "./scene.js";

const PALETTE = ["sky", "mint", "lilac", "peach", "lemon", "rose", "blue", "green", "orange", "purple", "pink"];
const BAD = /Err|BackOff|Error|OOM|Crash|Failed|Invalid/;
const QUICK = [
  "kubectl get nodes -L topology.kubernetes.io/zone,disktype,gpu",
  "kubectl get pods -o wide",
  "kubectl get deploy,svc,hpa",
  "kubectl top nodes",
  "kubectl get events --sort-by=.lastTimestamp",
  "kubectl describe node k8s-playground-worker3",
];

const SETUP_GUIDES = {
  podman: {
    label: "Podman",
    steps: [
      `Install Podman: <code>brew install podman</code> (or the installer from podman.io), plus <code>brew install kind kubectl</code>`,
      `Create a <b>rootful</b> machine with room for 4 nodes:<br><code>podman machine init --rootful --cpus 4 --memory 8192</code><br>
        Already have one? <code>podman machine stop && podman machine set --rootful --cpus 4 --memory 8192</code>`,
      `Start it: <code>podman machine start</code>. Stuck on "Currently starting"? Run <code>podman machine stop</code>, then start again.`,
      `Verify: <code>podman info --format '{{.Host.Security.Rootless}}'</code> should print <code>false</code>`,
      `Click <b>Create cluster</b> above, or run <code>make cluster</code>. The script exports <code>KIND_EXPERIMENTAL_PROVIDER=podman</code> for you.`,
      `Running kind by hand? Add <code>export KIND_EXPERIMENTAL_PROVIDER=podman</code> to <code>~/.zshrc</code>, otherwise kind looks for Docker and finds no clusters.`,
    ],
  },
  docker: {
    label: "Docker",
    steps: [
      `Install Docker Desktop: <code>brew install --cask docker</code>, then open Docker.app once to finish setup. Also <code>brew install kind kubectl</code>`,
      `Give it room for 4 nodes: Docker Desktop → Settings → Resources → 4 CPUs, 8 GB memory → Apply &amp; restart`,
      `Verify the daemon: <code>docker info</code> should print server details without errors`,
      `Click <b>Create cluster</b> above, or run <code>make cluster</code>. kind uses Docker by default, no extra env needed.`,
      `Prefer no Docker Desktop? <code>brew install colima docker && colima start --cpu 4 --memory 8</code> works the same way.`,
    ],
  },
};

function colorFor(name) {
  let h = 0;
  for (const ch of name || "") h = (h * 31 + ch.charCodeAt(0)) >>> 0;
  return COLORS[PALETTE[h % PALETTE.length]];
}

export function renderPlayground(view, content, params) {
  let status = null;
  let pollTimer = null;
  let jobTimer = null;
  let alive = true;
  let setupTab = SETUP_GUIDES[store.get("setup-tab")] ? store.get("setup-tab") : null;
  let setupOpen = null;
  const history = store.get("console-history", []);
  let histIdx = history.length;

  const examples = content.topics.flatMap((t) => t.examples.map((e) => ({ id: `${t.id}:${e.title}`, label: `${t.title} — ${e.title}`, yaml: e.yaml })));
  const startTab = params.get("lab") ? "labs" : params.get("tab") || "labs";

  view.innerHTML = `
    <section class="topic-hero clay">
      <div class="code tint-mint">KP</div>
      <div>
        <h1>Kind Playground</h1>
        <div class="muted">A real local Kubernetes cluster (<code>${esc(content.cluster.name)}</code>: 1 control-plane + 3 labelled/tainted workers) driven from your browser. Every command is pinned to context <code>${esc(content.cluster.context)}</code>.</div>
      </div>
      <button class="btn" id="refreshBtn">Refresh</button>
    </section>

    <div class="status-bar clay" style="margin-top:1.2rem" id="statusBar"><span class="muted">Checking tools…</span></div>
    <div id="setupHelp"></div>
    <div id="jobPanel"></div>

    <div class="pg-layout">
      <div class="grid">
        <div class="panel clay">
          <div class="tabs" id="pgTabs">
            <button data-t="labs">Guided labs</button>
            <button data-t="yaml">YAML apply</button>
            <button data-t="console">kubectl console</button>
          </div>
          <div id="tab-labs" class="pg-tab" style="margin-top:1rem">
            <select id="labSelect" style="width:100%">${content.labs.map((l) => `<option value="${l.id}">${esc(l.title)} (${l.level})</option>`).join("")}</select>
            <div id="labBody"></div>
          </div>
          <div id="tab-yaml" class="pg-tab" style="margin-top:1rem">
            <select id="exampleSelect" style="width:100%"><option value="">Load an example from any topic…</option>${examples.map((e, i) => `<option value="${i}">${esc(e.label)}</option>`).join("")}</select>
            <textarea class="code" id="yamlInput" spellcheck="false" style="margin-top:.8rem" placeholder="Paste or write Kubernetes YAML here"></textarea>
            <div class="row" style="margin-top:.8rem">
              <button class="btn primary" data-yaml="apply">Apply</button>
              <button class="btn" data-yaml="dry">Server dry-run</button>
              <button class="btn danger" data-yaml="delete">Delete these objects</button>
            </div>
          </div>
          <div id="tab-console" class="pg-tab" style="margin-top:1rem">
            <div class="row"><input type="text" id="cmdInput" style="flex:1; font-family:var(--mono); font-size:.82rem" placeholder="kubectl get pods -o wide"><button class="btn primary" id="cmdRun">Run</button></div>
            <div class="row" style="margin-top:.7rem">${QUICK.map((q) => `<button class="btn small" data-quick="${esc(q)}">${esc(q.replace("kubectl ", ""))}</button>`).join("")}</div>
            <p class="muted" style="font-size:.75rem">Non-interactive verbs only (no exec, port-forward, -w or -f). Use the YAML tab for manifests. ↑/↓ for history.</p>
          </div>
        </div>
        <div class="panel clay">
          <div class="row"><h3 style="margin:0">Output</h3><span class="spacer"></span><button class="btn small" id="clearOut">Clear</button></div>
          <div class="terminal" id="out" style="margin-top:.8rem">Ready.</div>
        </div>
      </div>

      <div class="grid">
        <div class="panel clay">
          <div class="row">
            <h3 style="margin:0">Live cluster map</h3>
            <span class="pill neutral" id="liveBadge">offline</span>
            <span class="spacer"></span>
            <label class="muted" style="font-size:.8rem"><input type="checkbox" id="sysToggle"> system pods</label>
            <label class="muted" style="font-size:.8rem"><input type="checkbox" id="autoToggle" checked> auto-refresh</label>
          </div>
          <div id="live" style="margin-top:1rem"><p class="muted">Create or start the cluster to see nodes and pods here.</p></div>
        </div>
        <div class="grid two" id="liveTables"></div>
      </div>
    </div>`;

  // ---------------------------------------------------------------- output
  const out = $("#out");
  const print = (cmd, res) => {
    if (out.textContent === "Ready.") out.innerHTML = "";
    const body = [res.stdout, res.stderr].filter(Boolean).join("\n").trim() || (res.ok ? "(no output)" : res.error || "failed");
    out.insertAdjacentHTML("beforeend", `<div class="cmd">$ ${esc(cmd)}</div><div class="${res.ok ? "" : "err"}">${esc(body)}</div>\n`);
    out.scrollTop = out.scrollHeight;
  };
  $("#clearOut").onclick = () => (out.textContent = "Ready.");

  const requireCluster = () => {
    if (status?.reachable) return true;
    toast("Cluster not reachable. Create it first (see status bar).", true);
    return false;
  };

  async function runCommand(cmd) {
    if (!cmd.trim() || !requireCluster()) return;
    const res = await api("/api/kubectl/exec", { command: cmd });
    print(cmd, res);
    refreshState();
    return res;
  }

  async function runManifest(kind, manifest, label) {
    if (!requireCluster()) return;
    const path = kind === "delete" ? "/api/kubectl/delete" : "/api/kubectl/apply";
    const res = await api(path, { manifest, dryRun: kind === "dry" });
    print(label || `kubectl ${kind === "delete" ? "delete" : "apply"} -f -${kind === "dry" ? " --dry-run=server" : ""}`, res);
    refreshState();
    return res;
  }

  // ---------------------------------------------------------------- tabs
  const showTab = (t) => {
    $$("#pgTabs button").forEach((b) => b.classList.toggle("active", b.dataset.t === t));
    $$(".pg-tab").forEach((d) => (d.style.display = d.id === `tab-${t}` ? "" : "none"));
  };
  $("#pgTabs").addEventListener("click", (e) => e.target.dataset.t && showTab(e.target.dataset.t));
  showTab(startTab);

  // ---------------------------------------------------------------- labs
  const doneSteps = store.get("lab-steps", {});
  const renderLab = (id) => {
    const lab = content.labs.find((l) => l.id === id) || content.labs[0];
    $("#labSelect").value = lab.id;
    const done = new Set(doneSteps[lab.id] || []);
    $("#labBody").innerHTML = `
      <div class="row" style="margin-top:1rem">${levelPill(lab.level)}<a class="btn small" href="#/k8s/topic/${lab.topic}">Read the concept</a><span class="spacer"></span><button class="btn small" id="labReset">Reset progress</button></div>
      <p><b>Goal:</b> ${esc(lab.goal)}</p>
      ${lab.steps.map((s, i) => `
        <div class="lab-step ${done.has(i) ? "done" : ""}" data-step="${i}">
          <div class="row"><span class="num">${i + 1}</span><b style="flex:1">${esc(s.title)}</b>
            <button class="btn small ${s.kind === "delete" ? "danger" : "primary"}" data-run="${i}">${s.kind === "cmd" ? "Run" : s.kind === "apply" ? "Apply" : "Delete"}</button>
            ${s.kind !== "cmd" ? `<button class="btn small" data-edit="${i}">Edit</button>` : ""}
          </div>
          ${s.text ? `<div class="muted" style="font-size:.82rem; margin-top:.35rem">${esc(s.text)}</div>` : ""}
          <code class="inline">${esc(s.kind === "cmd" ? s.content : s.content.split("\n").filter((l) => /^\s*(kind|name):/.test(l)).slice(0, 4).map((l) => l.trim()).join("  ·  "))}</code>
        </div>`).join("")}`;
    $("#labReset").onclick = () => {
      delete doneSteps[lab.id];
      store.set("lab-steps", doneSteps);
      renderLab(lab.id);
    };
    $("#labBody").onclick = async (e) => {
      const edit = e.target.dataset.edit;
      if (edit !== undefined) {
        $("#yamlInput").value = lab.steps[+edit].content;
        showTab("yaml");
        return;
      }
      const i = e.target.dataset.run;
      if (i === undefined) return;
      const step = lab.steps[+i];
      e.target.disabled = true;
      const res = step.kind === "cmd" ? await runCommand(step.content) : await runManifest(step.kind, step.content, `${step.kind === "apply" ? "kubectl apply" : "kubectl delete"} -f <${step.title}>`);
      e.target.disabled = false;
      if (res?.ok) {
        doneSteps[lab.id] = [...new Set([...(doneSteps[lab.id] || []), +i])];
        store.set("lab-steps", doneSteps);
        e.target.closest(".lab-step").classList.add("done");
      }
    };
  };
  $("#labSelect").onchange = (e) => renderLab(e.target.value);
  renderLab(params.get("lab") || content.labs[0].id);

  // ---------------------------------------------------------------- yaml
  const yamlInput = $("#yamlInput");
  enableTabIndent(yamlInput);
  yamlInput.value = sessionStorage.getItem("pg-yaml") || examples[0]?.yaml || "";
  sessionStorage.removeItem("pg-yaml");
  $("#exampleSelect").onchange = (e) => {
    if (e.target.value !== "") yamlInput.value = examples[+e.target.value].yaml;
  };
  $("#tab-yaml").addEventListener("click", (e) => {
    const k = e.target.dataset.yaml;
    if (k) runManifest(k, yamlInput.value);
  });

  // ---------------------------------------------------------------- console
  const cmdInput = $("#cmdInput");
  const submit = () => {
    const cmd = cmdInput.value.trim();
    if (!cmd) return;
    history.push(cmd);
    store.set("console-history", history.slice(-50));
    histIdx = history.length;
    cmdInput.value = "";
    runCommand(cmd);
  };
  $("#cmdRun").onclick = submit;
  cmdInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") submit();
    else if (e.key === "ArrowUp" && histIdx > 0) cmdInput.value = history[--histIdx];
    else if (e.key === "ArrowDown") cmdInput.value = histIdx < history.length - 1 ? history[++histIdx] : ((histIdx = history.length), "");
  });
  $("#tab-console").addEventListener("click", (e) => {
    const q = e.target.dataset.quick;
    if (q) runCommand(q);
  });

  // ---------------------------------------------------------------- status & setup
  async function refreshStatus() {
    status = await api("/api/cluster/status");
    if (!alive) return;
    const t = status.tools || {};
    const chip = (ok, label) => `<span class="pill ${ok ? "ok" : "bad"}">${ok ? "&#10003;" : "&#10005;"} ${label}</span>`;
    const running = status.job?.status === "running";
    const rt = t.runtime || "podman";
    const engine = rt === "podman" ? "podman machine" : "docker daemon";
    $("#statusBar").innerHTML = `
      ${chip(t.runtime_installed, rt)}${chip(t.runtime_running, `${engine} running`)}
      ${t.rootless === true ? `<span class="pill warn" title="kind is more reliable on a rootful Podman machine">! rootless</span>` : t.rootless === false ? chip(true, "rootful") : ""}
      ${chip(t.kind, "kind")}${chip(t.kubectl, "kubectl")}
      <span class="pill ${status.reachable ? "ok" : status.exists ? "warn" : "neutral"}">cluster: ${status.reachable ? "ready" : status.exists ? "exists, not reachable" : "not created"}</span>
      <span class="spacer"></span>
      <label class="muted" style="font-size:.8rem"><input type="checkbox" id="optIngress"> ingress-nginx</label>
      <label class="muted" style="font-size:.8rem"><input type="checkbox" id="optVpa"> VPA</label>
      <button class="btn small primary" id="createBtn" ${running || !t.runtime_running || !t.kind ? "disabled" : ""}>${status.exists ? "Re-apply setup" : "Create cluster"}</button>
      ${status.exists ? `<button class="btn small" id="recreateBtn" ${running ? "disabled" : ""}>Recreate</button><button class="btn small danger" id="deleteBtn" ${running ? "disabled" : ""}>Delete</button>` : ""}`;
    const opts = () => ({ ingress: $("#optIngress").checked, vpa: $("#optVpa").checked });
    $("#createBtn").onclick = () => startJob("/api/cluster/create", opts());
    if ($("#recreateBtn")) $("#recreateBtn").onclick = () => confirm("Delete and recreate the playground cluster?") && startJob("/api/cluster/create", { ...opts(), recreate: true });
    if ($("#deleteBtn")) $("#deleteBtn").onclick = () => confirm("Delete the kind cluster? All workloads are lost.") && startJob("/api/cluster/delete", {});

    renderSetup(t, rt, engine);

    if (status.job) showJob(status.job);
    $("#liveBadge").textContent = status.reachable ? "live" : "offline";
    $("#liveBadge").className = `pill ${status.reachable ? "ok" : "neutral"}`;
    if (status.reachable) refreshState();
  }

  function renderSetup(t, rt, engine) {
    const ready = t.runtime_running && t.kind && t.rootless !== true;
    if (setupOpen === null) setupOpen = !ready;
    const tab = setupTab || rt;
    const guide = SETUP_GUIDES[tab];
    const detected = (id) => (id === rt && t.runtime_installed ? `<span class="rt-dot" title="detected on this machine"></span>` : "");
    $("#setupHelp").innerHTML = `
      <details class="panel clay" id="setupDetails" style="margin-top:1.2rem" ${setupOpen ? "open" : ""}>
        <summary class="row" style="cursor:pointer; list-style:none"><h3 style="margin:0">${ready ? "Setup guide" : "One-time setup (macOS)"}</h3>
          <span class="pill ${ready ? "ok" : "warn"}">${ready ? "ready" : "action needed"}</span><span class="spacer"></span><span class="muted" style="font-size:.8rem">${setupOpen ? "hide" : "show"}</span></summary>
        <p class="muted">The Learn pages, animations, Scheduler Lab and Interview Prep work without a cluster. The playground runs kind on top of Podman or Docker; pick yours:</p>
        <div class="tabs setup-tabs">${Object.entries(SETUP_GUIDES).map(([id, g]) =>
          `<button type="button" data-setup-tab="${id}" class="${id === tab ? "active" : ""}">${detected(id)}${esc(g.label)}</button>`).join("")}</div>
        <ol class="setup-steps">${guide.steps.map((s) => `<li>${s}</li>`).join("")}</ol>
        <p class="muted setup-note">Detected: ${esc(rt)} ${t.runtime_installed ? "installed" : "missing"}, ${engine} ${t.runtime_running ? "running" : "not running"}${t.rootless === true ? " (rootless: switch to rootful)" : ""}, kind ${t.kind ? "installed" : "missing"}.
          Both installed? Force one with <code>K8S_PLAYGROUND_RUNTIME=${tab} make run</code>.</p>
      </details>`;
    $("#setupDetails").addEventListener("toggle", (e) => {
      setupOpen = e.target.open;
      e.target.querySelector("summary .muted").textContent = setupOpen ? "hide" : "show";
    });
    $$("[data-setup-tab]").forEach((b) => b.addEventListener("click", () => {
      setupTab = b.dataset.setupTab;
      store.set("setup-tab", setupTab);
      renderSetup(t, rt, engine);
    }));
  }

  async function startJob(path, body) {
    const res = await api(path, body);
    if (!res.ok) return toast(res.error || "Failed to start", true);
    showJob(res.job);
    pollJob();
    refreshStatus();
  }

  function showJob(job) {
    $("#jobPanel").innerHTML = `
      <div class="panel clay" style="margin-top:1.2rem">
        <div class="row"><h3 style="margin:0">${esc(job.name)}</h3><span class="pill ${job.status === "succeeded" ? "ok" : job.status === "failed" ? "bad" : "warn"}">${esc(job.status)}</span>
          <span class="spacer"></span><button class="btn small" id="hideJob">Hide</button></div>
        <div class="terminal" id="jobLog" style="margin-top:.8rem">${esc(job.log || "starting…")}</div>
      </div>`;
    const log = $("#jobLog");
    log.scrollTop = log.scrollHeight;
    $("#hideJob").onclick = () => ($("#jobPanel").innerHTML = "");
    if (job.status === "running" && !jobTimer) pollJob();
  }

  function pollJob() {
    clearTimeout(jobTimer);
    jobTimer = setTimeout(async () => {
      jobTimer = null;
      if (!alive) return;
      const { job } = await api("/api/cluster/job");
      if (!job) return;
      showJob(job);
      if (job.status === "running") pollJob();
      else {
        toast(job.status === "succeeded" ? `${job.name} finished` : `${job.name} failed — see log`, job.status !== "succeeded");
        refreshStatus();
      }
    }, 1500);
  }

  // ---------------------------------------------------------------- live state
  async function refreshState() {
    if (!status?.reachable || !alive) return;
    const st = await api(`/api/cluster/state${$("#sysToggle").checked ? "?system=1" : ""}`);
    if (!alive) return;
    if (!st.ok) {
      $("#live").innerHTML = `<div class="event-box">${esc(st.error)}</div>`;
      return;
    }
    const byNode = new Map(st.nodes.map((n) => [n.name, []]));
    const unscheduled = [];
    st.pods.forEach((p) => (p.node && byNode.has(p.node) ? byNode.get(p.node).push(p) : unscheduled.push(p)));
    $("#live").innerHTML = `
      <div class="live-nodes">${st.nodes.map((n) => `
        <div class="live-node clay ${n.unschedulable ? "tint-lemon" : ""}">
          <div class="row"><b style="font-size:.85rem">${esc(n.name.replace(`${content.cluster.name}-`, ""))}</b><span class="spacer"></span>
            <span class="pill ${n.ready ? "ok" : "bad"}">${n.ready ? "Ready" : "NotReady"}</span>${n.unschedulable ? `<span class="pill warn">cordoned</span>` : ""}</div>
          <div style="margin:.35rem 0">${Object.entries(n.labels).map(([k, v]) => `<span class="chip${k === "zone" ? " zone" : ""}">${esc(k)}=${esc(v)}</span>`).join("")}
            ${n.taints.map((t) => `<span class="chip taint">${esc(t)}</span>`).join("")}</div>
          <div class="muted" style="font-size:.7rem">${esc(n.role)} · ${esc(n.cpu)} cpu · ${esc(n.memory)}</div>
          <div class="pods">${byNode.get(n.name).map((p) => `<div class="live-pod ${esc(p.status)} ${BAD.test(p.status) ? "bad" : ""}" style="background:${colorFor(p.app || p.name)}" title="${esc(`${p.namespace}/${p.name}\n${p.status} · ready ${p.ready} · restarts ${p.restarts}${p.requests.cpu ? `\nrequests cpu ${p.requests.cpu}` : ""}`)}"></div>`).join("") || `<span class="muted" style="font-size:.72rem">no pods</span>`}</div>
        </div>`).join("")}</div>
      ${unscheduled.length ? `<h4 style="margin-top:1.2rem">Pending / unscheduled (${unscheduled.length})</h4><ul class="clean pending-list">${unscheduled.map((p) => `<li><b>${esc(p.name)}</b>: ${esc(p.status)}<br><span class="muted">${esc(p.message)}</span></li>`).join("")}</ul>` : ""}`;

    const table = (title, heads, rows) => `<div class="panel clay"><h3>${title}</h3>${rows.length ? `<table class="mini-table"><tr>${heads.map((h) => `<th>${h}</th>`).join("")}</tr>${rows.map((r) => `<tr class="r">${r.map((c) => `<td>${esc(c)}</td>`).join("")}</tr>`).join("")}</table>` : `<p class="muted">none</p>`}</div>`;
    $("#liveTables").innerHTML =
      table("Deployments", ["name", "ready", "image"], st.deployments.map((d) => [d.name, d.ready, d.images.join(", ")])) +
      table("HPA", ["name", "cpu", "replicas"], st.hpa.map((h) => [h.name, `${h.cpuCurrent ?? "?"}% / ${h.cpuTarget ?? "?"}%`, `${h.current ?? "?"} (${h.min}-${h.max})`])) +
      table("Services", ["name", "type", "ports"], st.services.map((s) => [s.name, s.type, s.ports.join(", ")])) +
      table("Recent events", ["reason", "object", "message"], st.events.slice(-8).reverse().map((e) => [e.reason, e.object, e.message]));
  }

  function schedulePoll() {
    clearInterval(pollTimer);
    pollTimer = setInterval(() => {
      if ($("#autoToggle")?.checked && !document.hidden) refreshState();
    }, 3000);
  }

  $("#refreshBtn").onclick = refreshStatus;
  $("#sysToggle").onchange = refreshState;
  refreshStatus();
  schedulePoll();

  return () => {
    alive = false;
    clearInterval(pollTimer);
    clearTimeout(jobTimer);
  };
}
