// Declarative storyboards: each step clones the previous state and applies a mutation.

const N = (id, name, o = {}) => ({ id, name, labels: o.labels || [], taints: o.taints || [], status: o.status || "ready" });
const podName = (id, tag) => (/^[a-z]+$/i.test(tag || "") ? `${tag}-${id.replace(/^\D+/, "") || id}` : id);
const P = (id, node, o = {}) => ({ id, node, name: o.name || podName(id, o.tag), tag: o.tag || "", color: o.color || "sky", status: o.status || "running", size: o.size || 1 });
const C = (id, kind, name, lines = [], o = {}) => ({ id, kind, name, lines, row: o.row || 1, tint: o.tint });
const L = (from, to, style = "flow", label = "") => ({ from, to, style, label });

const pod = (s, id) => s.pods.find((p) => p.id === id);
const node = (s, id) => s.nodes.find((n) => n.id === id);
const set = (s, id, props) => Object.assign(pod(s, id), props);
const add = (s, ...pods) => s.pods.push(...pods);
const drop = (s, ...ids) => (s.pods = s.pods.filter((p) => !ids.includes(p.id)));
const card = (s, c) => {
  const i = s.cards.findIndex((x) => x.id === c.id);
  if (i >= 0) s.cards[i] = c;
  else s.cards.push(c);
};
const uncard = (s, ...ids) => (s.cards = s.cards.filter((c) => !ids.includes(c.id)));
const lines = (s, id, l) => (s.cards.find((c) => c.id === id).lines = l);
const mark = (s, marks) => Object.entries(marks).forEach(([id, m]) => (node(s, id).mark = m));

function story(base, ...steps) {
  let cur = { nodes: [], pods: [], cards: [], links: [], ...structuredClone(base) };
  return steps.map(([title, text, fn]) => {
    cur = structuredClone(cur);
    cur.title = title;
    cur.text = text;
    cur.highlight = [];
    cur.nodes.forEach((n) => {
      delete n.mark;
      delete n.score;
    });
    if (fn) fn(cur);
    return cur;
  });
}

const W = () => [
  N("w1", "worker-1", { labels: ["zone=a", "disk=ssd"] }),
  N("w2", "worker-2", { labels: ["zone=b", "disk=hdd"] }),
  N("w3", "worker-3", { labels: ["zone=c", "gpu=true"] }),
];

export const SCENES = {
  pods: story(
    { nodes: W(), queue: true, cards: [C("api", "Controller", "kube-apiserver", ["validates & stores in etcd"])] },
    ["You submit a Pod", "<code>kubectl apply -f pod.yaml</code> sends the spec to the API server. It's stored in etcd with no node assigned yet, so its phase is <b>Pending</b>.", (s) => add(s, P("p1", "queue", { name: "hello", status: "pending", tag: "web" }))],
    ["The scheduler binds it", "kube-scheduler filters and scores nodes, then writes <code>spec.nodeName=worker-1</code>.", (s) => { mark(s, { w1: "ok" }); set(s, "p1", { node: "w1", status: "creating" }); s.links = [L("api", "p1", "dashed", "bind")]; }],
    ["kubelet starts the containers", "kubelet on worker-1 pulls images, the CNI assigns a pod IP and the containers start, so the pod is <b>Running</b>. All containers in the pod share that IP and its volumes.", (s) => { set(s, "p1", { status: "running" }); card(s, C("spec", "Pod", "hello", ["IP 10.244.1.7", "containers: web + log-sidecar", "shares network + volumes"])); s.links = [L("spec", "p1", "dashed")]; }],
    ["A container crashes", "The process exits. kubelet restarts it in place with exponential backoff (10s, 20s, 40s … up to 5m). If it keeps failing, the status shows <b>CrashLoopBackOff</b>. Debug with <code>kubectl logs --previous</code>.", (s) => { set(s, "p1", { status: "failed", tag: "!" }); lines(s, "spec", ["restarts: 3", "Last state: Error (exit 1)", "CrashLoopBackOff"]); }],
    ["Fixed and running again", "The pod keeps the same IP, because the pause container holds the network namespace across container restarts.", (s) => { set(s, "p1", { status: "running", tag: "web" }); lines(s, "spec", ["IP 10.244.1.7", "restarts: 3", "Ready 2/2"]); }],
    ["The node dies", "worker-1 goes <b>NotReady</b>. After the default 300s toleration, the pod is evicted.", (s) => { node(s, "w1").status = "notready"; set(s, "p1", { status: "terminating" }); }],
    ["Bare pods are not resurrected", "Nothing owns this pod, so nothing recreates it. That's why you use <b>Deployments</b>, <b>StatefulSets</b> or <b>Jobs</b>, which provide self-healing.", (s) => { drop(s, "p1"); s.links = []; uncard(s, "spec"); }],
  ),

  deployments: story(
    {
      nodes: W(),
      cards: [C("dep", "Deployment", "web", ["replicas: 3", "image: nginx:v1", "maxSurge 1 / maxUnavailable 0"]), C("rs1", "ReplicaSet", "web-7d4f", ["v1 · 3/3"])],
      pods: [P("a1", "w1", { name: "web-v1", tag: "v1" }), P("a2", "w2", { name: "web-v1", tag: "v1" }), P("a3", "w3", { name: "web-v1", tag: "v1" })],
      links: [L("dep", "rs1", "dashed", "owns"), L("rs1", "a1", "dashed"), L("rs1", "a2", "dashed"), L("rs1", "a3", "dashed")],
    },
    ["Desired state: 3 replicas", "The Deployment owns a ReplicaSet, and the ReplicaSet owns the pods. Controllers run reconciliation loops that drive the <i>actual</i> state toward the <i>desired</i> state."],
    ["A pod dies", "worker-2's pod crashed or was deleted. The ReplicaSet sees 2/3 pods.", (s) => { set(s, "a2", { status: "terminating" }); lines(s, "rs1", ["v1 · 2/3"]); }],
    ["Self-healing", "The ReplicaSet immediately creates a replacement with a new name, a new IP and the same template.", (s) => { drop(s, "a2"); add(s, P("a4", "w2", { name: "web-v1", tag: "v1", status: "creating" })); s.links = s.links.filter((l) => l.to !== "a2").concat(L("rs1", "a4", "dashed")); }],
    ["kubectl set image web=nginx:v2", "Changing the <b>pod template</b> creates a new ReplicaSet (a new revision). The old one is kept for rollback.", (s) => { set(s, "a4", { status: "running" }); lines(s, "dep", ["replicas: 3", "image: nginx:v2", "revision 2"]); card(s, C("rs2", "ReplicaSet", "web-9c1a", ["v2 · 0/3"])); lines(s, "rs1", ["v1 · 3/3"]); s.links.push(L("dep", "rs2", "dashed", "owns")); }],
    ["Surge: one v2 pod", "maxSurge 1 allows 4 pods temporarily. A v2 pod starts, and readiness gates the rollout.", (s) => { add(s, P("b1", "w1", { name: "web-v2", tag: "v2", color: "mint", status: "creating" })); lines(s, "rs2", ["v2 · 1/3"]); s.links.push(L("rs2", "b1", "dashed")); }],
    ["v2 ready, retire one v1", "maxUnavailable 0 means an old pod is removed only after a new one is Ready.", (s) => { set(s, "b1", { status: "running" }); set(s, "a1", { status: "terminating" }); lines(s, "rs1", ["v1 · 2/3"]); }],
    ["Repeat until done", "The new ReplicaSet scales up and the old one scales down, one pod at a time, with zero downtime.", (s) => { drop(s, "a1", "a3", "a4"); add(s, P("b2", "w2", { name: "web-v2", tag: "v2", color: "mint" }), P("b3", "w3", { name: "web-v2", tag: "v2", color: "mint" })); lines(s, "rs1", ["v1 · 0/0 (kept)"]); lines(s, "rs2", ["v2 · 3/3"]); s.links = [L("dep", "rs1", "dashed", "owns"), L("dep", "rs2", "dashed", "owns"), L("rs2", "b1", "dashed"), L("rs2", "b2", "dashed"), L("rs2", "b3", "dashed")]; }],
    ["kubectl rollout undo", "A bad release? Undo scales the old ReplicaSet back up using the same rolling strategy.", (s) => { s.highlight = ["rs1"]; lines(s, "rs1", ["v1 · scaling up"]); add(s, P("c1", "w3", { name: "web-v1", tag: "v1", status: "creating" })); set(s, "b3", { status: "terminating" }); s.links.push(L("rs1", "c1", "dashed")); }],
  ),

  services: story(
    {
      nodes: W(),
      cards: [C("svc", "Service", "web", ["ClusterIP 10.96.12.4", "selector app=web", "port 80 → targetPort 8080"])],
      pods: [P("web1", "w1", { tag: "web", name: "web-1" }), P("web2", "w2", { tag: "web", name: "web-2" }), P("db", "w2", { tag: "db", color: "peach", name: "db-0" }), P("web3", "w3", { tag: "web", name: "web-3" })],
    },
    ["Pods come and go; a Service is stable", "A Service has a fixed virtual IP and DNS name (<code>web.default.svc.cluster.local</code>). It selects pods by <b>labels</b>, not by IP.", (s) => (s.highlight = ["web1", "web2", "web3"])],
    ["Selector, then endpoints", "The EndpointSlice controller records the IPs of Ready pods matching <code>app=web</code>. The db pod isn't selected.", (s) => { s.links = ["web1", "web2", "web3"].map((p) => L("svc", p, "flow")); card(s, C("eps", "EndpointSlice", "web-abc12", ["10.244.1.5", "10.244.2.8", "10.244.3.4"])); }],
    ["Traffic is load-balanced", "kube-proxy (iptables/IPVS/nftables) on every node DNATs the ClusterIP to one of the endpoints.", (s) => { card(s, C("client", "Pod", "frontend", ["curl http://web"])); s.links.unshift(L("client", "svc", "flow", "GET /")); }],
    ["Pod not Ready means no traffic", "web-2's readiness probe fails, so it's removed from the endpoints. It is NOT restarted; it just stops receiving requests.", (s) => { set(s, "web2", { status: "notready" }); s.links = s.links.filter((l) => l.to !== "web2"); lines(s, "eps", ["10.244.1.5", "10.244.3.4"]); }],
    ["NodePort: open a port on every node", "type: NodePort adds port 30080 on each node's IP. External clients hit any node, and it is forwarded to a ready pod.", (s) => { set(s, "web2", { status: "running" }); s.links.push(L("svc", "web2", "flow")); lines(s, "svc", ["type NodePort", "nodePort 30080", "selector app=web"]); card(s, C("client", "Pod", "external user", ["http://<nodeIP>:30080"], { tint: "slate" })); lines(s, "eps", ["10.244.1.5", "10.244.2.8", "10.244.3.4"]); }],
    ["LoadBalancer: a cloud LB in front", "type: LoadBalancer asks the cloud controller for an external LB that targets the NodePorts. Each Service gets its own LB, which is why we have Ingress.", (s) => { card(s, C("lb", "Controller", "Cloud LB 34.120.x.x", ["→ nodes:30080"], { tint: "peach" })); s.links = s.links.filter((l) => l.from !== "client"); s.links.unshift(L("client", "lb", "flow", "https"), L("lb", "svc", "flow")); lines(s, "svc", ["type LoadBalancer", "nodePort 30080", "selector app=web"]); }],
  ),

  labels: story(
    {
      nodes: [N("w1", "worker-1"), N("w2", "worker-2")],
      pods: [
        P("p1", "w1", { tag: "web", name: "web·prod" }), P("p2", "w1", { tag: "web", name: "web·dev", color: "lemon" }),
        P("p3", "w2", { tag: "api", name: "api·prod", color: "lilac" }), P("p4", "w2", { tag: "db", name: "db·prod", color: "peach" }),
        P("p5", "w2", { tag: "web", name: "web·prod" }),
      ],
      cards: [C("sel", "Rule", "selector", ["(none)"])],
    },
    ["Everything carries labels", "Labels are key/value tags (app=web, env=prod, tier=db). Selectors query them. This is how Services, ReplicaSets, NetworkPolicies and nodeSelector find things."],
    ["Equality selector: app=web", "<code>kubectl get pods -l app=web</code> matches 3 pods across nodes.", (s) => { lines(s, "sel", ["app=web"]); s.links = ["p1", "p2", "p5"].map((p) => L("sel", p, "ok")); }],
    ["AND: app=web,env=prod", "Comma means AND. The dev pod drops out.", (s) => { lines(s, "sel", ["app=web,env=prod"]); s.links = ["p1", "p5"].map((p) => L("sel", p, "ok")); }],
    ["Set-based: env in (prod), app notin (db)", "matchExpressions support In, NotIn, Exists and DoesNotExist.", (s) => { lines(s, "sel", ["env in (prod)", "app notin (db)"]); s.links = ["p1", "p3", "p5"].map((p) => L("sel", p, "ok")); }],
    ["Debug trick: remove a label", "<code>kubectl label pod web-5 app-</code> removes the label. The ReplicaSet no longer owns the pod, so it creates a replacement. The isolated pod stays alive for debugging.", (s) => { lines(s, "sel", ["app=web (ReplicaSet)"]); set(s, "p5", { name: "debug-me", color: "slate", tag: "?" }); add(s, P("p6", "w1", { tag: "web", name: "web·prod", status: "creating" })); s.links = ["p1", "p2", "p6"].map((p) => L("sel", p, "ok")); }],
  ),

  namespaces: story(
    {
      nodes: [N("dev", "ns: dev", { labels: ["quota cpu 4", "pods ≤ 5"] }), N("prod", "ns: prod", { labels: ["quota cpu 16"] }), N("team", "ns: team-a", { labels: ["LimitRange"] })],
      pods: [P("d1", "dev", { tag: "1c", color: "lemon" }), P("d2", "dev", { tag: "2c", color: "lemon" }), P("pr1", "prod", { tag: "api", color: "mint" }), P("pr2", "prod", { tag: "web", color: "mint" }), P("t1", "team", { tag: "job", color: "lilac" })],
      queue: true,
    },
    ["Namespaces are virtual clusters", "Names, RBAC, quotas and policies are scoped per namespace. Here the boxes are namespaces, not nodes, and they all share the same physical nodes."],
    ["ResourceQuota caps the total", "dev may request at most 4 CPU, and 3 are used. A new pod requesting 2 CPU is <b>rejected at admission</b>, so it is never even created.", (s) => { card(s, C("rq", "ResourceQuota", "dev-quota", ["requests.cpu: 3 / 4", "pods: 2 / 5"])); add(s, P("d3", "queue", { tag: "2c", color: "lemon", status: "rejected", name: "new-pod" })); s.links = [L("rq", "d3", "blocked", "403 exceeded quota")]; }],
    ["LimitRange injects defaults", "In team-a, a pod without resources gets defaultRequest 100m/128Mi and default limits automatically.", (s) => { drop(s, "d3"); s.links = []; card(s, C("lr", "LimitRange", "defaults", ["defaultRequest 100m / 128Mi", "default limit 500m / 256Mi"])); add(s, P("t2", "team", { tag: "def", color: "lilac", status: "creating" })); s.links = [L("lr", "t2", "flow", "mutates")]; }],
    ["Not a network boundary!", "Pods in dev can still call prod pods by default. Add NetworkPolicies (and maybe separate clusters) for real isolation.", (s) => { set(s, "t2", { status: "running" }); s.links = [L("d1", "pr1", "flow", "still reachable")]; s.highlight = ["d1", "pr1"]; }],
  ),

  configmaps: story(
    {
      nodes: [N("w1", "worker-1"), N("w2", "worker-2")],
      cards: [C("cm", "ConfigMap", "app-config", ["LOG_LEVEL=info", "FEATURE_X=true", "app.properties (file)"])],
      pods: [P("a1", "w1", { tag: "env", name: "api-env" }), P("a2", "w2", { tag: "vol", name: "api-vol", color: "mint" })],
    },
    ["Config outside the image", "The same image runs in dev/stage/prod, and each environment supplies its own ConfigMap."],
    ["Consume as env vars", "<code>envFrom.configMapRef</code> or <code>valueFrom.configMapKeyRef</code>. Values are read <b>once at container start</b>.", (s) => (s.links = [L("cm", "a1", "flow", "env")])],
    ["Consume as files", "Mounted as a volume at /etc/config, each key becomes a file.", (s) => s.links.push(L("cm", "a2", "flow", "volume"))],
    ["Edit the ConfigMap", "<code>kubectl edit cm app-config</code> sets LOG_LEVEL=debug.", (s) => { lines(s, "cm", ["LOG_LEVEL=debug", "FEATURE_X=true", "app.properties (file)"]); s.highlight = ["cm"]; }],
    ["Volume files update live", "kubelet syncs mounted ConfigMaps in roughly a minute (but never with subPath). The env-var pod still sees <b>info</b>.", (s) => { s.highlight = ["a2"]; set(s, "a2", { tag: "dbg" }); }],
    ["Env needs a restart", "<code>kubectl rollout restart deploy/api</code>, or better, a checksum annotation that triggers rollouts automatically.", (s) => { set(s, "a1", { status: "terminating" }); add(s, P("a3", "w1", { tag: "dbg", name: "api-env-2", status: "creating" })); }],
    ["Both consistent", "Tip: <code>immutable: true</code> plus versioned names (app-config-v2) make changes explicit and safe.", (s) => { drop(s, "a1"); set(s, "a3", { status: "running" }); s.links = [L("cm", "a3", "flow", "env"), L("cm", "a2", "flow", "volume")]; }],
  ),

  secrets: story(
    {
      nodes: [N("w1", "worker-1"), N("w2", "worker-2")],
      cards: [C("sec", "Secret", "db-creds", ["DB_USER: YXBw", "DB_PASSWORD: ••••••••"])],
      pods: [P("api", "w1", { tag: "api", color: "mint" })],
    },
    ["Secrets reach pods like ConfigMaps", "Mounted secret files are stored in tmpfs (RAM) on the node, and env vars are also possible.", (s) => (s.links = [L("sec", "api", "flow", "file / env")])],
    ["base64 is NOT encryption", "Anyone with <code>get secrets</code> or <code>create pods</code> in the namespace can read them. By default etcd stores them unencrypted.", (s) => { card(s, C("etcd", "Controller", "etcd", ["/registry/secrets/db-creds", "base64 → decodes instantly"], { tint: "rose" })); s.links.push(L("sec", "etcd", "dashed", "stored")); s.highlight = ["etcd"]; }],
    ["Harden it", "Enable encryption at rest with a <b>KMS v2</b> provider (envelope encryption), restrict RBAC on secrets, and audit access.", (s) => { lines(s, "etcd", ["KMS v2 envelope encryption", "RBAC: get secrets restricted"]); card(s, C("rbac", "Role", "least privilege", ["no list/watch secrets for devs"])); }],
    ["Source of truth outside the cluster", "External Secrets Operator (or the CSI Secrets Store) syncs from Vault or AWS/GCP/Azure secret managers. Git holds only <i>references</i>.", (s) => { uncard(s, "rbac"); card(s, C("vault", "Controller", "Vault / Secret Manager", ["prod/payments/db"], { tint: "lilac" })); card(s, C("eso", "Controller", "External Secrets", ["refreshInterval 1h"])); s.links = [L("vault", "eso", "flow", "sync"), L("eso", "sec", "flow", "writes"), L("sec", "api", "flow", "file")]; }],
  ),

  "resources-qos": story(
    {
      nodes: [N("w1", "worker-1", { labels: ["alloc 2 CPU / 4Gi"] }), N("w2", "worker-2", { labels: ["alloc 2 CPU / 4Gi"] })],
      pods: [P("g", "w1", { tag: "G", color: "mint", name: "guaranteed" }), P("b", "w1", { tag: "Bu", color: "lemon", name: "burstable" }), P("be", "w1", { tag: "BE", color: "rose", name: "besteffort" })],
      cards: [C("qos", "Rule", "QoS classes", ["G: requests = limits (cpu+mem)", "Bu: some requests/limits", "BE: nothing set"])],
    },
    ["Requests reserve, limits cap", "The scheduler only looks at <b>requests</b> when placing pods. Limits are enforced at runtime by cgroups."],
    ["CPU over limit is throttled", "CPU is compressible: the burstable pod hits its CPU limit and is slowed down (CFS throttling), not killed.", (s) => { s.highlight = ["b"]; set(s, "b", { tag: "slow" }); }],
    ["Memory over limit is OOMKilled", "Memory is not compressible: exceeding the limit means the kernel kills the container (exit 137), then it restarts.", (s) => set(s, "b", { status: "failed", tag: "137", name: "OOMKilled" })],
    ["Node under memory pressure", "kubelet must reclaim memory. It evicts <b>BestEffort</b> first, then Burstable pods above their requests, and Guaranteed last.", (s) => { set(s, "b", { status: "running", tag: "Bu", name: "burstable" }); node(s, "w1").taints = ["memory-pressure"]; set(s, "be", { status: "terminating" }); }],
    ["Evicted pod rescheduled", "Its controller recreates it elsewhere. Lesson: set requests on everything important.", (s) => { drop(s, "be"); add(s, P("be2", "w2", { tag: "BE", color: "rose", name: "besteffort", status: "creating" })); }],
  ),

  probes: story(
    {
      nodes: [N("w1", "worker-1"), N("w2", "worker-2")],
      cards: [C("svc", "Service", "web", ["routes to Ready pods only"]), C("pr", "Rule", "probes", ["startup: /healthz 30×5s", "readiness: /ready every 5s", "liveness: /healthz every 10s"])],
      pods: [P("p1", "w1", { status: "creating", name: "web-1" }), P("p2", "w2", { status: "creating", name: "web-2" })],
    },
    ["Startup probe protects slow boots", "Until the startup probe succeeds, liveness and readiness are disabled, so a slow JVM isn't killed mid-boot."],
    ["Readiness passes, traffic flows", "Pods join the Service endpoints only once ready.", (s) => { set(s, "p1", { status: "running" }); set(s, "p2", { status: "running" }); s.links = [L("svc", "p1"), L("svc", "p2")]; }],
    ["Readiness fails, so the pod is pulled out", "web-2 is overloaded or warming a cache. It is removed from endpoints but <b>not restarted</b>.", (s) => { set(s, "p2", { status: "notready" }); s.links = [L("svc", "p1")]; }],
    ["Liveness fails, so the container restarts", "web-1 deadlocked. After failureThreshold misses, kubelet restarts the container.", (s) => { set(s, "p1", { status: "failed", name: "restart #1" }); s.links = []; set(s, "p2", { status: "running" }); s.links = [L("svc", "p2")]; }],
    ["Both healthy", "Rule of thumb: liveness checks the <i>process</i>, never downstream dependencies.", (s) => { set(s, "p1", { status: "running", name: "web-1" }); s.links = [L("svc", "p1"), L("svc", "p2")]; }],
  ),

  nodeselector: story(
    {
      nodes: [N("w1", "worker-1", { labels: ["disktype=ssd"] }), N("w2", "worker-2", { labels: ["disktype=hdd"] }), N("w3", "worker-3", { labels: ["disktype=ssd"] })],
      queue: true,
      cards: [C("spec", "Pod", "db-cache", ["nodeSelector:", "  disktype: ssd"])],
      pods: [P("a", "queue", { status: "pending", name: "db-1", tag: "db", color: "peach" }), P("b", "queue", { status: "pending", name: "db-2", tag: "db", color: "peach" })],
    },
    ["Pods wait in the scheduling queue", "Each pod asks for nodes labelled <code>disktype=ssd</code>. Label nodes with <code>kubectl label node worker-1 disktype=ssd</code>."],
    ["Filter phase", "nodeSelector is a hard filter: an exact match on <i>all</i> keys. worker-2 (hdd) is eliminated.", (s) => mark(s, { w1: "ok", w2: "no", w3: "ok" })],
    ["Score & bind", "Among the feasible nodes, scoring (resources, spreading…) picks a winner for each pod.", (s) => { mark(s, { w1: "ok", w2: "no", w3: "ok" }); set(s, "a", { node: "w1", status: "creating" }); set(s, "b", { node: "w3", status: "creating" }); }],
    ["Running on SSD nodes", "Note: changing node labels later does NOT move running pods.", (s) => { set(s, "a", { status: "running" }); set(s, "b", { status: "running" }); }],
    ["No match means Pending forever", "Request <code>disktype: nvme</code> and no node matches. Events show the scheduler's verdict.", (s) => { lines(s, "spec", ["nodeSelector:", "  disktype: nvme"]); add(s, P("c", "queue", { status: "pending", name: "db-3", tag: "db", color: "peach" })); mark(s, { w1: "no", w2: "no", w3: "no" }); card(s, C("ev", "Event", "FailedScheduling", ["0/3 nodes are available:", "3 node(s) didn't match Pod's node affinity/selector"])); }],
  ),

  "node-affinity": story(
    {
      nodes: [N("w1", "worker-1", { labels: ["zone=a", "disk=ssd"] }), N("w2", "worker-2", { labels: ["zone=b", "disk=hdd"] }), N("w3", "worker-3", { labels: ["zone=c", "disk=ssd"] })],
      queue: true,
      cards: [C("req", "Rule", "required (filter)", ["zone In [a, b]"]), C("pref", "Rule", "preferred (score)", ["disk In [hdd] · weight 80"])],
      pods: [P("p", "queue", { status: "pending", name: "api", tag: "api", color: "lilac" })],
    },
    ["Hard + soft rules", "<b>required</b>DuringScheduling is a filter. <b>preferred</b>DuringScheduling adds weighted points to matching nodes."],
    ["Required filters nodes", "zone-c is out. Terms are ORed; expressions inside a term are ANDed.", (s) => { mark(s, { w1: "ok", w2: "ok", w3: "no" }); s.highlight = ["req"]; }],
    ["Preferred scores the rest", "worker-2 matches disk=hdd and gets +80. worker-1 gets +0 from this rule.", (s) => { mark(s, { w1: "ok", w2: "ok", w3: "no" }); node(s, "w1").score = "+0"; node(s, "w2").score = "+80"; s.highlight = ["pref"]; }],
    ["Bound to worker-2", "Preferences are only part of the total score, so resource balancing can still change the outcome.", (s) => set(s, "p", { node: "w2", status: "running" })],
    ["…IgnoredDuringExecution", "Relabel worker-2 to zone=c and the pod keeps running. Rules apply only at scheduling time (the descheduler can fix drift).", (s) => { node(s, "w2").labels = ["zone=c", "disk=hdd"]; s.highlight = ["w2", "p"]; }],
  ),

  "pod-affinity": story(
    {
      nodes: W(),
      queue: true,
      pods: [P("cache", "w1", { tag: "redis", color: "peach", name: "cache" })],
      cards: [C("rule", "Rule", "podAffinity", ["labelSelector app=cache", "topologyKey: kubernetes.io/hostname"])],
    },
    ["Affinity: sit next to the cache", "The web pod requires a node that already runs a pod labelled app=cache in the same <i>topology domain</i> (here: the same hostname).", (s) => add(s, P("web", "queue", { status: "pending", tag: "web", name: "web" }))],
    ["Co-located", "Only worker-1 qualifies. Network hops to Redis are now local.", (s) => { mark(s, { w1: "ok", w2: "no", w3: "no" }); set(s, "web", { node: "w1", status: "running" }); s.links = [L("web", "cache", "ok", "same node")]; }],
    ["Anti-affinity: replicas avoid each other", "For high availability, each api replica refuses nodes that already run an api pod.", (s) => { s.links = []; card(s, C("rule", "Rule", "podAntiAffinity (required)", ["labelSelector app=api", "topologyKey: hostname"])); add(s, P("a1", "w1", { tag: "api", color: "lilac", status: "creating" }), P("a2", "w2", { tag: "api", color: "lilac", status: "creating" }), P("a3", "w3", { tag: "api", color: "lilac", status: "creating" })); }],
    ["Replica #4 has nowhere to go", "3 nodes means at most 3 replicas. The 4th stays <b>Pending</b>, and hard anti-affinity can also stall rolling updates.", (s) => { ["a1", "a2", "a3"].forEach((id) => set(s, id, { status: "running" })); add(s, P("a4", "queue", { tag: "api", color: "lilac", status: "pending" })); mark(s, { w1: "no", w2: "no", w3: "no" }); }],
    ["Relax it", "Use <b>preferred</b> anti-affinity or topologySpreadConstraints (maxSkew) to spread without blocking.", (s) => { card(s, C("rule", "Rule", "podAntiAffinity (preferred)", ["weight 100", "topologyKey: hostname"])); set(s, "a4", { node: "w2", status: "running" }); }],
  ),

  "taints-tolerations": story(
    {
      nodes: [N("w1", "worker-1"), N("w2", "worker-2"), N("w3", "worker-3", { labels: ["gpu=true"], taints: ["dedicated=gpu:NoSchedule"] })],
      queue: true,
      pods: [P("b1", "w2", { tag: "web", name: "web-1" })],
    },
    ["worker-3 is tainted", "A taint is a 'keep out' sign: <code>kubectl taint node worker-3 dedicated=gpu:NoSchedule</code>.", (s) => (s.highlight = ["w3"])],
    ["A pod without a toleration bounces", "The scheduler won't place a pod on a node whose NoSchedule taint it doesn't tolerate.", (s) => add(s, P("a", "w3", { tag: "web", status: "rejected", name: "web-2" }))],
    ["…and lands elsewhere", "", (s) => { set(s, "a", { node: "w1", status: "running" }); mark(s, { w3: "no" }); }],
    ["A toleration lets the GPU pod in", "Toleration <code>dedicated=gpu:NoSchedule</code> plus <code>nodeSelector gpu=true</code>. The toleration permits; the selector attracts.", (s) => { card(s, C("tol", "Rule", "tolerations", ["key: dedicated", "value: gpu", "effect: NoSchedule"])); add(s, P("g1", "w3", { tag: "gpu", color: "lilac", status: "creating", name: "trainer" })); s.links = [L("tol", "g1", "ok")]; }],
    ["NoExecute evicts running pods", "<code>kubectl taint node worker-2 maintenance=true:NoExecute</code>. Pods that don't tolerate it are evicted now (or after tolerationSeconds).", (s) => { set(s, "g1", { status: "running" }); s.links = []; node(s, "w2").taints = ["maintenance:NoExecute"]; set(s, "b1", { status: "terminating" }); }],
    ["Rescheduled by its controller", "Kubernetes itself uses NoExecute taints (not-ready, unreachable) to evict pods from failed nodes after 300s.", (s) => { drop(s, "b1"); add(s, P("b2", "w1", { tag: "web", name: "web-1", status: "creating" })); }],
  ),

  "topology-spread": story(
    {
      nodes: W(),
      pods: [1, 2, 3, 4, 5, 6].map((i) => P(`s${i}`, "w1", { tag: "shop", name: `shop-${i}`, color: "mint" })),
      cards: [C("ts", "Rule", "no constraint", ["scheduler may bin-pack"])],
    },
    ["Without constraints", "All 6 replicas could land in zone-a. One AZ outage would take the whole service down.", (s) => s.highlight.push("w1")],
    ["maxSkew: 1 across zones", "topologySpreadConstraints keep the per-zone counts within 1 of each other.", (s) => { card(s, C("ts", "Rule", "topologySpreadConstraints", ["maxSkew: 1", "topologyKey: zone", "whenUnsatisfiable: DoNotSchedule"])); set(s, "s3", { node: "w2" }); set(s, "s4", { node: "w2" }); set(s, "s5", { node: "w3" }); set(s, "s6", { node: "w3" }); }],
    ["How skew is computed", "skew(D) = count(D) + 1 − min(count). Placing #7 anywhere gives 3−2 = 1 ≤ maxSkew, so it's OK.", (s) => { ["w1", "w2", "w3"].forEach((n) => (node(s, n).score = "count 2")); add(s, P("s7", "w1", { tag: "shop", name: "shop-7", color: "mint", status: "creating" })); }],
    ["#8 can't go to zone-a", "zone-a would have 4 vs min 2, giving skew 2 > 1. It's filtered, so #8 goes to zone-b.", (s) => { set(s, "s7", { status: "running" }); node(s, "w1").score = "count 3"; node(s, "w2").score = "count 2"; node(s, "w3").score = "count 2"; mark(s, { w1: "no", w2: "ok", w3: "ok" }); add(s, P("s8", "w2", { tag: "shop", name: "shop-8", color: "mint", status: "creating" })); }],
    ["Gotcha: tainted domains still count", "nodeTaintsPolicy defaults to <b>Ignore</b>, so a tainted zone counts with 0 pods and blocks placements. Set <code>nodeTaintsPolicy: Honor</code>. Try it in the Scheduler Lab!", (s) => { set(s, "s8", { status: "running" }); node(s, "w3").taints = ["dedicated:NoSchedule"]; s.highlight = ["w3"]; }],
  ),

  hpa: story(
    {
      nodes: W(),
      cards: [C("dep", "Deployment", "web", ["replicas: 2", "requests cpu 200m"]), C("hpa", "HPA", "web-hpa", ["target CPU 50%", "min 2 · max 10"]), C("ms", "Controller", "metrics-server", ["kubelet → cAdvisor stats"])],
      pods: [P("p1", "w1", { tag: "web" }), P("p2", "w2", { tag: "web" })],
      links: [L("ms", "hpa", "dashed", "metrics"), L("hpa", "dep", "dashed", "scale")],
      meter: { label: "avg CPU / request", value: 30, target: 50 },
    },
    ["HPA watches utilization vs requests", "Every 15s the HPA reads pod metrics. Utilization is a percentage of the pods' <b>requests</b>, so requests are mandatory."],
    ["Traffic spike", "A marketing email went out and CPU jumps to 90%.", (s) => { card(s, C("load", "Pod", "users ×4", ["requests/sec ↑"], { tint: "peach" })); s.links.push(L("load", "p1", "flow"), L("load", "p2", "flow")); s.meter = { label: "avg CPU / request", value: 90, target: 50 }; }],
    ["desired = ceil(2 × 90 / 50) = 4", "The HPA patches replicas to 4. Scale-up has no stabilization window by default, so it reacts fast.", (s) => { lines(s, "dep", ["replicas: 4", "requests cpu 200m"]); add(s, P("p3", "w3", { tag: "web", status: "creating" }), P("p4", "w1", { tag: "web", status: "creating" })); s.highlight = ["hpa"]; }],
    ["Load spreads out", "4 pods share the load, which drops to about 45%, within the 10% tolerance, so no further change.", (s) => { set(s, "p3", { status: "running" }); set(s, "p4", { status: "running" }); s.links = s.links.filter((l) => l.from !== "load").concat(["p1", "p2", "p3", "p4"].map((p) => L("load", p))); s.meter = { label: "avg CPU / request", value: 45, target: 50 }; }],
    ["Traffic drops", "CPU falls to 20%. The HPA waits for the 300s <b>scale-down stabilization window</b> to avoid flapping.", (s) => { uncard(s, "load"); s.links = s.links.filter((l) => l.from !== "load"); s.meter = { label: "avg CPU / request", value: 20, target: 50 }; }],
    ["ceil(4 × 20 / 50) = 2", "It scales back down to 2 (and never below minReplicas).", (s) => { lines(s, "dep", ["replicas: 2", "requests cpu 200m"]); set(s, "p3", { status: "terminating" }); set(s, "p4", { status: "terminating" }); }],
    ["Steady state", "Pair the HPA with Cluster Autoscaler or Karpenter so Pending pods get new nodes.", (s) => { drop(s, "p3", "p4"); s.meter = { label: "avg CPU / request", value: 40, target: 50 }; }],
  ),

  vpa: story(
    {
      nodes: [N("w1", "worker-1"), N("w2", "worker-2")],
      cards: [C("vpa", "VPA", "hamster-vpa", ["updateMode: Recreate"]), C("rec", "Controller", "recommender", ["collecting usage…"])],
      pods: [P("h1", "w1", { tag: "100m", name: "hamster-1", size: 0.85, color: "peach" }), P("h2", "w2", { tag: "100m", name: "hamster-2", size: 0.85, color: "peach" })],
      meter: { label: "usage vs request", value: 100, display: "350m / 100m" },
    },
    ["Under-provisioned pods", "The pods request 100m but use about 350m, so they're throttled, and the scheduler packs too many of them per node."],
    ["Recommender computes a target", "From usage history (decaying histogram) it produces target, lowerBound and upperBound.", (s) => { lines(s, "rec", ["target 350m / 300Mi", "lower 250m · upper 600m"]); s.links = [L("rec", "vpa", "flow", "recommendation")]; }],
    ["Updater evicts an outlier", "Requests are outside the bounds, so the pod is evicted (respecting PDBs).", (s) => { card(s, C("upd", "Controller", "updater", ["evicting hamster-1"])); set(s, "h1", { status: "terminating" }); }],
    ["Admission webhook rewrites requests", "The replacement pod is mutated at creation time with the recommended requests.", (s) => { drop(s, "h1"); card(s, C("adm", "Controller", "admission-controller", ["requests → 350m / 300Mi"])); add(s, P("h1b", "w1", { tag: "350m", name: "hamster-1", size: 1.25, color: "mint", status: "creating" })); s.links = [L("rec", "vpa", "flow"), L("adm", "h1b", "flow", "mutate")]; }],
    ["Rolled one by one", "", (s) => { set(s, "h1b", { status: "running" }); set(s, "h2", { status: "terminating" }); lines(s, "upd", ["evicting hamster-2"]); }],
    ["Right-sized", "Usage now matches requests. In-place resize (newer VPA modes) can avoid restarts entirely.", (s) => { drop(s, "h2"); add(s, P("h2b", "w2", { tag: "350m", name: "hamster-2", size: 1.25, color: "mint" })); s.meter = { label: "usage vs request", value: 85, display: "300m / 350m" }; s.links = []; }],
    ["Don't fight the HPA", "VPA and HPA on the same CPU or memory metric create a feedback loop. Use VPA for memory or Off mode, and HPA on CPU or RPS.", (s) => card(s, C("warn", "Rule", "rule of thumb", ["HPA: replicas on CPU/RPS", "VPA: right-size requests"]))],
  ),

  pdb: story(
    {
      nodes: W(),
      cards: [C("pdb", "PDB", "api-pdb", ["minAvailable: 2", "allowed disruptions: 1"])],
      pods: [P("a1", "w1", { tag: "api" }), P("a2", "w2", { tag: "api" }), P("a3", "w3", { tag: "api" })],
    },
    ["3 replicas, budget of 1", "A PodDisruptionBudget limits <b>voluntary</b> disruptions: drains, upgrades, autoscaler scale-down."],
    ["kubectl drain worker-1", "First it <b>cordons</b> the node (unschedulable), then it evicts pods through the Eviction API.", (s) => (node(s, "w1").status = "cordoned")],
    ["Eviction allowed", "Allowed disruptions drops to 0 until the replacement is Ready.", (s) => { set(s, "a1", { status: "terminating" }); add(s, P("a4", "w3", { tag: "api", status: "creating" })); lines(s, "pdb", ["minAvailable: 2", "allowed disruptions: 0"]); }],
    ["Concurrent drain is blocked", "Draining worker-2 at the same time gets <b>429 Too Many Requests</b>, and drain retries.", (s) => { node(s, "w2").status = "cordoned"; set(s, "a2", { status: "blocked" }); card(s, C("ev", "Event", "eviction api-a2", ["429: would violate PDB"])); s.links = [L("pdb", "a2", "blocked", "denied")]; }],
    ["Budget frees up", "The replacement is Ready, so the next eviction proceeds.", (s) => { drop(s, "a1"); set(s, "a4", { status: "running" }); set(s, "a2", { status: "terminating" }); add(s, P("a5", "w3", { tag: "api", status: "creating" })); uncard(s, "ev"); s.links = []; lines(s, "pdb", ["minAvailable: 2", "allowed disruptions: 0"]); }],
    ["Nodes drained safely", "Availability never dropped below 2. Now upgrade the nodes and <code>kubectl uncordon</code> them.", (s) => { drop(s, "a2"); set(s, "a5", { status: "running" }); lines(s, "pdb", ["minAvailable: 2", "allowed disruptions: 1"]); }],
  ),

  statefulsets: story(
    { nodes: W(), cards: [C("svc", "Service", "web (headless)", ["clusterIP: None"])] },
    ["Ordinal pods, created in order", "web-0 starts first and gets its own PVC from volumeClaimTemplates.", (s) => { add(s, P("s0", "w1", { name: "web-0", tag: "0", status: "creating", color: "lilac" })); card(s, C("pvc0", "PVC", "data-web-0", ["100Mi RWO"], { row: 2 })); s.links = [L("s0", "pvc0", "dashed")]; }],
    ["web-1 waits for web-0 Ready", "podManagementPolicy: OrderedReady (default). Use Parallel for faster starts if the app allows it.", (s) => { set(s, "s0", { status: "running" }); add(s, P("s1", "w2", { name: "web-1", tag: "1", status: "creating", color: "lilac" })); card(s, C("pvc1", "PVC", "data-web-1", ["100Mi RWO"], { row: 2 })); s.links.push(L("s1", "pvc1", "dashed")); }],
    ["web-2", "", (s) => { set(s, "s1", { status: "running" }); add(s, P("s2", "w3", { name: "web-2", tag: "2", status: "creating", color: "lilac" })); card(s, C("pvc2", "PVC", "data-web-2", ["100Mi RWO"], { row: 2 })); s.links.push(L("s2", "pvc2", "dashed")); }],
    ["Stable DNS per pod", "<code>web-0.web.default.svc.cluster.local</code>: clients (or replicas) can address a specific member, e.g. the primary.", (s) => { set(s, "s2", { status: "running" }); s.links.push(L("svc", "s0", "flow", "web-0.web"), L("svc", "s1", "flow"), L("svc", "s2", "flow")); }],
    ["web-1 dies…", "", (s) => set(s, "s1", { status: "terminating" })],
    ["…and returns as web-1 with the same data", "Same name, same identity, same PVC. Unlike a Deployment, its identity is stable.", (s) => { drop(s, "s1"); add(s, P("s1b", "w2", { name: "web-1", tag: "1", status: "running", color: "lilac" })); s.links = s.links.filter((l) => l.from !== "s1" && l.to !== "s1").concat(L("s1b", "pvc1", "dashed"), L("svc", "s1b", "flow")); s.highlight = ["pvc1", "s1b"]; }],
  ),

  daemonsets: story(
    {
      nodes: [N("cp", "control-plane", { taints: ["control-plane:NoSchedule"] }), ...W()],
      cards: [C("ds", "DaemonSet", "log-agent", ["1 pod per eligible node"])],
    },
    ["One agent per node", "The DaemonSet controller creates a pod for every node that matches its selector and tolerations.", (s) => add(s, ...["w1", "w2", "w3"].map((n) => P(`d-${n}`, n, { tag: "log", color: "lemon", status: "creating", name: `agent-${n}` })))],
    ["Control-plane skipped", "The control-plane is tainted. Add a toleration if your agent must run there too.", (s) => s.pods.forEach((p) => (p.status = "running"))],
    ["A new node joins", "Autoscaler added worker-4, and an agent pod is created automatically.", (s) => { s.nodes.push(N("w4", "worker-4", { status: "new" })); add(s, P("d-w4", "w4", { tag: "log", color: "lemon", status: "creating", name: "agent-w4" })); }],
    ["Tolerate the control-plane", "<code>tolerations: [{key: node-role.kubernetes.io/control-plane, operator: Exists}]</code>", (s) => { set(s, "d-w4", { status: "running" }); add(s, P("d-cp", "cp", { tag: "log", color: "lemon", status: "creating", name: "agent-cp" })); }],
    ["Node removed, pod garbage-collected", "Typical DaemonSets: Fluent Bit, node-exporter, kube-proxy, CNI and CSI node plugins.", (s) => { set(s, "d-cp", { status: "running" }); node(s, "w2").status = "notready"; set(s, "d-w2", { status: "terminating" }); }],
  ),

  jobs: story(
    {
      nodes: [N("w1", "worker-1"), N("w2", "worker-2")],
      cards: [C("job", "Job", "crunch", ["completions 5 · parallelism 2", "succeeded 0/5"])],
      pods: [P("j1", "w1", { tag: "1", color: "peach" }), P("j2", "w2", { tag: "2", color: "peach" })],
    },
    ["Run to completion", "A Job runs pods until <b>completions</b> succeed, with up to <b>parallelism</b> pods at a time."],
    ["Two done, next two start", "", (s) => { set(s, "j1", { status: "completed" }); set(s, "j2", { status: "completed" }); add(s, P("j3", "w1", { tag: "3", color: "peach" }), P("j4", "w2", { tag: "4", color: "peach" })); lines(s, "job", ["completions 5 · parallelism 2", "succeeded 2/5"]); }],
    ["A pod fails", "It's retried with exponential backoff, up to backoffLimit (default 6). podFailurePolicy can fail fast on fatal exit codes.", (s) => { set(s, "j3", { status: "failed" }); lines(s, "job", ["succeeded 2/5", "failed 1 / backoffLimit 3"]); }],
    ["Retry succeeds", "", (s) => { drop(s, "j3"); add(s, P("j3b", "w1", { tag: "3", color: "peach" })); set(s, "j4", { status: "completed" }); lines(s, "job", ["succeeded 3/5", "failed 1 / backoffLimit 3"]); }],
    ["Job Complete", "<code>ttlSecondsAfterFinished</code> cleans up finished Jobs automatically.", (s) => { set(s, "j3b", { status: "completed" }); add(s, P("j5", "w2", { tag: "5", color: "peach", status: "completed" })); lines(s, "job", ["succeeded 5/5", "Complete"]); }],
    ["CronJob = Jobs on a schedule", "A CronJob creates a new Job every tick. concurrencyPolicy (Allow/Forbid/Replace) controls overlap.", (s) => { s.pods = []; card(s, C("cron", "CronJob", "report", ['schedule "*/2 * * * *"', "concurrencyPolicy: Forbid"])); s.cards = [s.cards.find((c) => c.id === "cron"), { ...s.cards.find((c) => c.id === "job"), name: "report-29012345", lines: ["created by CronJob"] }]; s.links = [L("cron", "job", "flow", "every 2 min")]; add(s, P("r1", "w1", { tag: "rep", color: "lemon", status: "creating" })); }],
  ),

  "init-sidecar": story(
    {
      nodes: [N("w1", "worker-1")],
      cards: [
        C("i1", "Controller", "init: wait-for-db", ["running…"], { tint: "lilac" }),
        C("i2", "Controller", "init: migrate", ["waiting"], { tint: "slate" }),
        C("sc", "Controller", "sidecar: log-shipper", ["restartPolicy: Always", "waiting"], { tint: "slate" }),
        C("app", "Controller", "app: web", ["waiting"], { tint: "slate" }),
      ],
      pods: [P("p", "w1", { status: "init", tag: "0/3", name: "init-demo" })],
    },
    ["Init containers run first, in order", "Status shows <code>Init:0/3</code>. Each must exit 0 before the next starts.", (s) => (s.links = [L("i1", "p", "flow")])],
    ["Second init: migrations", "", (s) => { s.cards[0] = C("i1", "Controller", "init: wait-for-db", ["✓ completed"], { tint: "mint" }); s.cards[1] = C("i2", "Controller", "init: migrate", ["running…"], { tint: "lilac" }); set(s, "p", { tag: "1/3" }); s.links = [L("i2", "p", "flow")]; }],
    ["Native sidecar starts and keeps running", "A sidecar is an init container with <code>restartPolicy: Always</code> (GA in v1.33). It starts before the app and keeps running.", (s) => { s.cards[1] = C("i2", "Controller", "init: migrate", ["✓ completed"], { tint: "mint" }); s.cards[2] = C("sc", "Controller", "sidecar: log-shipper", ["restartPolicy: Always", "running"], { tint: "lemon" }); set(s, "p", { tag: "2/3" }); s.links = [L("sc", "p", "flow")]; }],
    ["App runs alongside the sidecar", "", (s) => { s.cards[3] = C("app", "Controller", "app: web", ["running"], { tint: "sky" }); set(s, "p", { status: "running", tag: "2/2" }); s.links = [L("sc", "p", "flow"), L("app", "p", "flow")]; }],
    ["Shutdown order", "App containers stop first, then sidecars in reverse order. This finally fixes Jobs that never ended because a sidecar kept running.", (s) => { set(s, "p", { status: "terminating" }); s.cards[3] = C("app", "Controller", "app: web", ["stopped (1st)"], { tint: "slate" }); s.cards[2] = C("sc", "Controller", "sidecar: log-shipper", ["stopped (2nd)"], { tint: "slate" }); s.links = []; }],
  ),

  storage: story(
    {
      nodes: [N("w1", "worker-1"), N("w2", "worker-2")],
      cards: [C("sc", "StorageClass", "standard", ["provisioner: local-path", "WaitForFirstConsumer"]), C("pvc", "PVC", "notes", ["100Mi RWO", "Pending"])],
      links: [L("pvc", "sc", "dashed", "class")],
    },
    ["Claim created, Pending", "With WaitForFirstConsumer, nothing is provisioned until a pod using the claim is scheduled (so the disk lands in the right zone)."],
    ["Pod scheduled, PV provisioned", "The CSI/local-path provisioner creates a PV and binds it to the PVC.", (s) => { add(s, P("p", "w1", { status: "creating", tag: "app", name: "notes-writer" })); card(s, C("pv", "PV", "pvc-3f2a…", ["100Mi", "node: worker-1"])); lines(s, "pvc", ["100Mi RWO", "Bound"]); s.links = [L("pvc", "sc", "dashed"), L("pvc", "pv", "ok", "bound"), L("pvc", "p", "flow", "mount")]; }],
    ["Data written", "", (s) => set(s, "p", { status: "running" })],
    ["Pod deleted", "The PVC and PV stay. Storage lifecycle is independent of pods.", (s) => set(s, "p", { status: "terminating" })],
    ["New pod, same data", "A new pod mounting the same claim sees the old notes.txt.", (s) => { drop(s, "p"); add(s, P("p2", "w1", { tag: "app", name: "notes-writer" })); s.links = [L("pvc", "sc", "dashed"), L("pvc", "pv", "ok", "bound"), L("pvc", "p2", "flow", "mount")]; s.highlight = ["pv"]; }],
    ["reclaimPolicy decides the end", "Deleting the PVC means <b>Delete</b> removes the disk (the dynamic default), while <b>Retain</b> keeps it for manual recovery.", (s) => { drop(s, "p2"); uncard(s, "pvc"); lines(s, "pv", ["reclaimPolicy: Delete", "→ disk removed"]); s.links = []; }],
  ),

  ingress: story(
    {
      nodes: [N("w1", "worker-1"), N("w2", "worker-2")],
      cards: [
        C("client", "Pod", "browser", ["shop.example.com"], { tint: "slate" }),
        C("ic", "Controller", "ingress-nginx", [":80 / :443"], { tint: "peach" }),
        C("ing", "Ingress", "shop", ["/api → api:80", "/ → frontend:80"]),
        C("sfe", "Service", "frontend", [], { row: 2 }),
        C("sapi", "Service", "api", [], { row: 2 }),
      ],
      pods: [P("fe1", "w1", { tag: "fe" }), P("fe2", "w2", { tag: "fe" }), P("api1", "w2", { tag: "api", color: "peach" })],
      links: [L("client", "ic", "flow"), L("ing", "ic", "dashed", "config")],
    },
    ["One entry point for many services", "The Ingress resource is just rules. The <b>controller</b> (nginx, Traefik, cloud LB) does the routing."],
    ["GET / goes to frontend", "Path / matches the Prefix rule, so it goes to Service frontend and then its endpoints.", (s) => s.links.push(L("ic", "sfe", "flow", "/"), L("sfe", "fe1", "flow"), L("sfe", "fe2", "flow"))],
    ["GET /api goes to api", "The longest matching prefix wins.", (s) => { s.links = [L("client", "ic", "flow"), L("ing", "ic", "dashed", "config"), L("ic", "sapi", "flow", "/api"), L("sapi", "api1", "flow")]; }],
    ["TLS termination", "<code>spec.tls</code> references a Secret that cert-manager issues and renews. Never paste certificates and keys into manifests by hand.", (s) => { lines(s, "ic", [":443 TLS (shop-tls secret)", "cert-manager renews"]); s.highlight = ["ic"]; }],
    ["Next: Gateway API", "Gateway + HTTPRoute: role-oriented, typed features like weights, headers and gRPC. It's the long-term successor to Ingress.", (s) => card(s, C("gw", "Rule", "Gateway API", ["Gateway (infra team)", "HTTPRoute (app team)"]))],
  ),

  "network-policy": story(
    {
      nodes: [N("w1", "worker-1"), N("w2", "worker-2"), N("w3", "worker-3")],
      pods: [P("fe", "w1", { tag: "fe", name: "frontend" }), P("x", "w1", { tag: "?", color: "slate", name: "rogue" }), P("be", "w2", { tag: "be", color: "peach", name: "backend" }), P("db", "w3", { tag: "db", color: "lilac", name: "postgres" })],
    },
    ["Default: everyone can talk to everyone", "The Kubernetes network is flat. A compromised pod can reach your database.", (s) => (s.links = [L("fe", "be", "ok"), L("be", "db", "ok"), L("x", "db", "ok", "uh-oh"), L("fe", "db", "ok")])],
    ["Apply default-deny ingress", "<code>podSelector: {}</code> with policyTypes [Ingress] and no rules isolates every pod in the namespace.", (s) => { card(s, C("np1", "NetworkPolicy", "default-deny", ["podSelector: {}", "policyTypes: [Ingress]"])); s.links = s.links.map((l) => ({ ...l, style: "blocked", label: "" })); }],
    ["Allow frontend → backend:8080", "Policies are additive allow-lists.", (s) => { card(s, C("np2", "NetworkPolicy", "backend-allow-fe", ["to: app=backend", "from: app=frontend :8080"])); s.links = [L("fe", "be", "ok", ":8080"), L("be", "db", "blocked"), L("x", "db", "blocked"), L("fe", "db", "blocked")]; }],
    ["Allow backend → db:5432", "Least privilege achieved. With egress policies, remember to allow DNS (port 53)!", (s) => { card(s, C("np3", "NetworkPolicy", "db-allow-be", ["to: app=postgres", "from: app=backend :5432"])); s.links = [L("fe", "be", "ok", ":8080"), L("be", "db", "ok", ":5432"), L("x", "db", "blocked"), L("fe", "db", "blocked")]; }],
  ),

  rbac: story(
    {
      cards: [
        C("sa", "ServiceAccount", "ci-bot", ["namespace: default"]),
        C("rb", "RoleBinding", "ci-bot-reads-pods", ["subject: ci-bot"]),
        C("role", "Role", "pod-reader", ["pods: get, list, watch"]),
        C("api", "Controller", "kube-apiserver", ["AuthN → AuthZ (RBAC) → Admission"], { row: 2, tint: "sky" }),
      ],
    },
    ["Who are you? (AuthN)", "Pods authenticate as a <b>ServiceAccount</b> using a short-lived projected token. Humans use OIDC or certificates.", (s) => (s.highlight = ["sa"])],
    ["What may you do? (AuthZ)", "A Role lists verbs on resources. A RoleBinding grants it to subjects within one namespace.", (s) => (s.links = [L("rb", "sa", "dashed", "subject"), L("rb", "role", "dashed", "roleRef")])],
    ["GET /api/v1/pods: allowed", "<code>kubectl auth can-i list pods --as=system:serviceaccount:default:ci-bot</code> returns yes.", (s) => { s.links.push(L("sa", "api", "ok", "list pods")); card(s, C("res", "Event", "200 OK", ["pods listed"], { row: 2, tint: "mint" })); s.links.push(L("api", "res", "ok")); }],
    ["DELETE pod: forbidden", "RBAC is deny-by-default and additive, and there's no explicit deny rule.", (s) => { s.links = [L("rb", "sa", "dashed"), L("rb", "role", "dashed"), L("sa", "api", "blocked", "delete pod")]; card(s, C("res", "Event", "403 Forbidden", ["cannot delete pods"], { row: 2 })); s.links.push(L("api", "res", "blocked")); }],
    ["Role vs ClusterRole", "A ClusterRole is cluster-scoped (nodes, PVs) or reusable. Bind it with a RoleBinding to grant it in one namespace only.", (s) => { card(s, C("cr", "ClusterRole", "view", ["built-in read-only role"], { row: 2 })); s.highlight = ["cr"]; s.links = [L("rb", "sa", "dashed"), L("rb", "role", "dashed")]; }],
  ),
};
