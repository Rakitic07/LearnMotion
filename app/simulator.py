"""A teaching-grade model of kube-scheduler's filter & score phases.

It understands real Pod/Deployment YAML: nodeSelector, nodeAffinity, pod (anti-)affinity,
tolerations, resource requests, topologySpreadConstraints, nodeName and cordoned nodes.
"""

from __future__ import annotations

import re
from collections import Counter
from copy import deepcopy

import yaml

MAX_REPLICAS = 20
HOSTNAME_KEY = "kubernetes.io/hostname"


class SimulationError(ValueError):
    pass


# --------------------------------------------------------------------------- quantities

def parse_cpu(value) -> int:
    """Return millicores."""
    if value in (None, ""):
        return 0
    if isinstance(value, (int, float)):
        return int(round(float(value) * 1000))
    text = str(value).strip()
    try:
        if text.endswith("m"):
            return int(float(text[:-1]))
        return int(round(float(text) * 1000))
    except ValueError as exc:
        raise SimulationError(f"Invalid cpu quantity: {value!r}") from exc


_MEM_UNITS = {
    "Ki": 1 / 1024, "Mi": 1, "Gi": 1024, "Ti": 1024 * 1024,
    "K": 1000 / 1024 ** 2, "M": 1000 ** 2 / 1024 ** 2, "G": 1000 ** 3 / 1024 ** 2, "T": 1000 ** 4 / 1024 ** 2,
}


def parse_mem(value) -> float:
    """Return MiB."""
    if value in (None, ""):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value) / 1024 ** 2
    match = re.fullmatch(r"\s*([0-9.]+)\s*([KMGT]i?)?\s*", str(value))
    if not match:
        raise SimulationError(f"Invalid memory quantity: {value!r}")
    number, unit = float(match.group(1)), match.group(2)
    return number * _MEM_UNITS[unit] if unit else number / 1024 ** 2


# --------------------------------------------------------------------------- matching

def match_expression(labels: dict, expr: dict) -> bool:
    key, op = expr.get("key"), expr.get("operator", "In")
    values = [str(v) for v in expr.get("values", []) or []]
    present = key in labels
    value = str(labels.get(key, ""))
    if op == "In":
        return present and value in values
    if op == "NotIn":
        return not present or value not in values
    if op == "Exists":
        return present
    if op == "DoesNotExist":
        return not present
    if op in ("Gt", "Lt"):
        if not present or not values:
            return False
        try:
            return int(value) > int(values[0]) if op == "Gt" else int(value) < int(values[0])
        except ValueError:
            return False
    raise SimulationError(f"Unknown operator {op!r}")


def match_node_term(node: dict, term: dict) -> bool:
    exprs = term.get("matchExpressions", []) or []
    fields = term.get("matchFields", []) or []
    if not exprs and not fields:
        return False
    return all(match_expression(node["labels"], e) for e in exprs) and all(
        match_expression({"metadata.name": node["name"]}, f) for f in fields
    )


def match_selector(labels: dict, selector: dict | None) -> bool:
    if not selector:
        return False
    for key, value in (selector.get("matchLabels") or {}).items():
        if str(labels.get(key)) != str(value):
            return False
    return all(match_expression(labels, e) for e in selector.get("matchExpressions", []) or [])


def tolerates(taint: dict, tolerations: list[dict]) -> bool:
    for tol in tolerations:
        if tol.get("effect") and tol["effect"] != taint["effect"]:
            continue
        if tol.get("operator", "Equal") == "Exists":
            if not tol.get("key") or tol["key"] == taint["key"]:
                return True
        elif tol.get("key") == taint["key"] and str(tol.get("value", "")) == str(taint.get("value", "")):
            return True
    return False


def taint_str(taint: dict) -> str:
    value = f"={taint['value']}" if taint.get("value") not in (None, "") else ""
    return f"{taint['key']}{value}:{taint['effect']}"


# --------------------------------------------------------------------------- parsing

def _parse_taint(raw) -> dict:
    if isinstance(raw, str):
        match = re.fullmatch(r"([^=:]+)(?:=([^:]*))?:(NoSchedule|PreferNoSchedule|NoExecute)", raw.strip())
        if not match:
            raise SimulationError(f"Invalid taint {raw!r}; use key=value:Effect")
        return {"key": match.group(1), "value": match.group(2) or "", "effect": match.group(3)}
    if not isinstance(raw, dict) or "key" not in raw or raw.get("effect") not in ("NoSchedule", "PreferNoSchedule", "NoExecute"):
        raise SimulationError(f"Invalid taint {raw!r}")
    return {"key": raw["key"], "value": str(raw.get("value", "") or ""), "effect": raw["effect"]}


def parse_nodes(text: str) -> list[dict]:
    try:
        data = yaml.safe_load(text) or {}
    except yaml.YAMLError as exc:
        raise SimulationError(f"Nodes YAML is invalid: {exc}") from exc
    raw_nodes = data.get("nodes") if isinstance(data, dict) else data
    if not isinstance(raw_nodes, list) or not raw_nodes:
        raise SimulationError("Nodes YAML must contain a non-empty `nodes:` list.")
    nodes = []
    for i, raw in enumerate(raw_nodes):
        if not isinstance(raw, dict) or not raw.get("name"):
            raise SimulationError(f"Node #{i + 1} needs a name.")
        labels = {str(k): str(v) for k, v in (raw.get("labels") or {}).items()}
        labels.setdefault(HOSTNAME_KEY, str(raw["name"]))
        alloc = raw.get("allocatable") or {}
        pods = []
        for p in raw.get("pods") or []:
            pods.append({
                "name": str(p.get("name", "pod")),
                "labels": {str(k): str(v) for k, v in (p.get("labels") or {}).items()},
                "cpu": parse_cpu(p.get("cpu")),
                "memory": parse_mem(p.get("memory")),
                "existing": True,
            })
        nodes.append({
            "name": str(raw["name"]),
            "labels": labels,
            "taints": [_parse_taint(t) for t in raw.get("taints") or []],
            "cpu": parse_cpu(alloc.get("cpu", "4")),
            "memory": parse_mem(alloc.get("memory", "8Gi")),
            "unschedulable": bool(raw.get("unschedulable")),
            "pods": pods,
        })
    return nodes


def _pod_template(doc: dict) -> tuple[dict, dict, int, str]:
    kind = doc.get("kind", "Pod")
    spec = doc.get("spec") or {}
    if kind == "Pod":
        return doc.get("metadata") or {}, spec, 1, kind
    if kind in ("Deployment", "ReplicaSet", "StatefulSet"):
        tmpl = spec.get("template") or {}
        return tmpl.get("metadata") or {}, tmpl.get("spec") or {}, int(spec.get("replicas", 1)), kind
    if kind == "DaemonSet":
        tmpl = spec.get("template") or {}
        return tmpl.get("metadata") or {}, tmpl.get("spec") or {}, 0, kind
    if kind == "Job":
        tmpl = spec.get("template") or {}
        return tmpl.get("metadata") or {}, tmpl.get("spec") or {}, int(spec.get("parallelism", 1)), kind
    if kind == "CronJob":
        tmpl = ((spec.get("jobTemplate") or {}).get("spec") or {}).get("template") or {}
        return tmpl.get("metadata") or {}, tmpl.get("spec") or {}, 1, kind
    raise SimulationError(f"Unsupported kind {kind!r}. Use Pod, Deployment, ReplicaSet, StatefulSet, DaemonSet, Job or CronJob.")


def parse_workload(text: str) -> dict:
    try:
        docs = [d for d in yaml.safe_load_all(text) if d]
    except yaml.YAMLError as exc:
        raise SimulationError(f"Pod YAML is invalid: {exc}") from exc
    if not docs or not isinstance(docs[0], dict):
        raise SimulationError("Provide a Pod or Deployment manifest.")
    doc = docs[0]
    meta, spec, replicas, kind = _pod_template(doc)
    containers = spec.get("containers") or []
    cpu = mem = 0.0
    for c in containers:
        req = ((c or {}).get("resources") or {}).get("requests") or {}
        cpu += parse_cpu(req.get("cpu"))
        mem += parse_mem(req.get("memory"))
    affinity = spec.get("affinity") or {}
    return {
        "kind": kind,
        "name": (doc.get("metadata") or {}).get("name") or meta.get("name") or "pod",
        "labels": {str(k): str(v) for k, v in (meta.get("labels") or {}).items()},
        "replicas": max(0, min(replicas, MAX_REPLICAS)),
        "nodeName": spec.get("nodeName"),
        "nodeSelector": {str(k): str(v) for k, v in (spec.get("nodeSelector") or {}).items()},
        "nodeAffinity": affinity.get("nodeAffinity") or {},
        "podAffinity": affinity.get("podAffinity") or {},
        "podAntiAffinity": affinity.get("podAntiAffinity") or {},
        "tolerations": spec.get("tolerations") or [],
        "spread": spec.get("topologySpreadConstraints") or [],
        "cpu": int(cpu),
        "memory": mem,
    }


# --------------------------------------------------------------------------- filters

def _domain_pods(nodes: list[dict], node: dict, topology_key: str) -> list[dict]:
    if topology_key not in node["labels"]:
        return []
    value = node["labels"][topology_key]
    return [p for n in nodes if n["labels"].get(topology_key) == value for p in n["pods"]]


def _all_pods(nodes: list[dict]) -> list[dict]:
    return [p for n in nodes for p in n["pods"]]


def _passes_node_affinity(pod: dict, node: dict) -> bool:
    if any(node["labels"].get(k) != v for k, v in pod["nodeSelector"].items()):
        return False
    required = pod["nodeAffinity"].get("requiredDuringSchedulingIgnoredDuringExecution") or {}
    terms = required.get("nodeSelectorTerms") or []
    return not terms or any(match_node_term(node, t) for t in terms)


def _filter(pod: dict, node: dict, nodes: list[dict]) -> tuple[list[tuple[str, str]], list[str]]:
    """Return (failures, passed) where failures are (plugin, message)."""
    failures: list[tuple[str, str]] = []
    passed: list[str] = []

    # Same order as kube-scheduler's default filter plugins; the first failure is what events report.
    if node["unschedulable"] and not tolerates(
        {"key": "node.kubernetes.io/unschedulable", "value": "", "effect": "NoSchedule"}, pod["tolerations"]
    ):
        failures.append(("NodeUnschedulable", "node(s) were unschedulable"))
    else:
        passed.append("NodeUnschedulable: node is schedulable")

    if pod["nodeName"]:
        if pod["nodeName"] != node["name"]:
            failures.append(("NodeName", "node(s) didn't match the requested node name"))
        else:
            passed.append("NodeName: pinned via spec.nodeName")

    bad_taints = [t for t in node["taints"] if t["effect"] in ("NoSchedule", "NoExecute") and not tolerates(t, pod["tolerations"])]
    if bad_taints:
        failures.append(("TaintToleration", f"node(s) had untolerated taint {{{taint_str(bad_taints[0])}}}"))
    elif node["taints"]:
        passed.append("TaintToleration: all hard taints tolerated")

    if _passes_node_affinity(pod, node):
        if pod["nodeSelector"] or pod["nodeAffinity"].get("requiredDuringSchedulingIgnoredDuringExecution"):
            passed.append("NodeAffinity: nodeSelector / required affinity matched")
    else:
        failures.append(("NodeAffinity", "node(s) didn't match Pod's node affinity/selector"))

    used_cpu = sum(p["cpu"] for p in node["pods"])
    used_mem = sum(p["memory"] for p in node["pods"])
    if pod["cpu"] and used_cpu + pod["cpu"] > node["cpu"]:
        failures.append(("NodeResourcesFit", "Insufficient cpu"))
    if pod["memory"] and used_mem + pod["memory"] > node["memory"]:
        failures.append(("NodeResourcesFit", "Insufficient memory"))
    if not any(f[0] == "NodeResourcesFit" for f in failures):
        passed.append(f"NodeResourcesFit: {node['cpu'] - used_cpu}m cpu / {int(node['memory'] - used_mem)}Mi free")

    for c in pod["spread"]:
        if c.get("whenUnsatisfiable", "DoNotSchedule") != "DoNotSchedule":
            continue
        key = c.get("topologyKey")
        if key not in node["labels"]:
            failures.append(("PodTopologySpread", "node(s) didn't match pod topology spread constraints (missing required label)"))
            break
        skew = _spread_skew(pod, node, nodes, c)
        if skew > int(c.get("maxSkew", 1)):
            failures.append(("PodTopologySpread", "node(s) didn't match pod topology spread constraints"))
            break

    all_pods = _all_pods(nodes)
    for term in pod["podAffinity"].get("requiredDuringSchedulingIgnoredDuringExecution") or []:
        key = term.get("topologyKey", HOSTNAME_KEY)
        selector = term.get("labelSelector")
        in_domain = any(match_selector(p["labels"], selector) for p in _domain_pods(nodes, node, key))
        first_pod = not any(match_selector(p["labels"], selector) for p in all_pods) and match_selector(pod["labels"], selector)
        if not (in_domain or (first_pod and key in node["labels"])):
            failures.append(("InterPodAffinity", "node(s) didn't match pod affinity rules"))
            break
    for term in pod["podAntiAffinity"].get("requiredDuringSchedulingIgnoredDuringExecution") or []:
        key = term.get("topologyKey", HOSTNAME_KEY)
        if any(match_selector(p["labels"], term.get("labelSelector")) for p in _domain_pods(nodes, node, key)):
            failures.append(("InterPodAffinity", "node(s) didn't match pod anti-affinity rules"))
            break

    return failures, passed


def _spread_counts(pod: dict, nodes: list[dict], constraint: dict) -> Counter:
    key = constraint.get("topologyKey")
    selector = constraint.get("labelSelector") or {"matchLabels": pod["labels"]}
    counts: Counter = Counter()
    honor_taints = constraint.get("nodeTaintsPolicy", "Ignore") == "Honor"
    honor_affinity = constraint.get("nodeAffinityPolicy", "Honor") == "Honor"
    for n in nodes:
        if key not in n["labels"]:
            continue
        if honor_affinity and not _passes_node_affinity(pod, n):
            continue
        if honor_taints and any(
            t["effect"] in ("NoSchedule", "NoExecute") and not tolerates(t, pod["tolerations"]) for t in n["taints"]
        ):
            continue
        counts[n["labels"][key]] += sum(1 for p in n["pods"] if match_selector(p["labels"], selector))
    return counts


def _spread_skew(pod: dict, node: dict, nodes: list[dict], constraint: dict) -> int:
    counts = _spread_counts(pod, nodes, constraint)
    domain = node["labels"][constraint["topologyKey"]]
    counts.setdefault(domain, 0)
    after = counts[domain] + 1
    return after - min(counts.values())


# --------------------------------------------------------------------------- scores

def _normalize(raw: dict[str, float], reverse: bool = False) -> dict[str, int]:
    if not raw:
        return {}
    lo, hi = min(raw.values()), max(raw.values())
    if hi == lo:
        return {k: (0 if hi == 0 and not reverse else 100) for k in raw}
    out = {}
    for k, v in raw.items():
        frac = (v - lo) / (hi - lo)
        out[k] = int(round(100 * (1 - frac if reverse else frac)))
    return out


def _score(pod: dict, feasible: list[dict], nodes: list[dict]) -> dict[str, dict[str, int]]:
    breakdown: dict[str, dict[str, int]] = {n["name"]: {} for n in feasible}

    prefs = pod["nodeAffinity"].get("preferredDuringSchedulingIgnoredDuringExecution") or []
    if prefs:
        raw = {
            n["name"]: sum(int(p.get("weight", 1)) for p in prefs if match_node_term(n, p.get("preference") or {}))
            for n in feasible
        }
        for name, val in _normalize(raw).items():
            breakdown[name]["NodeAffinity"] = val

    if any(t["effect"] == "PreferNoSchedule" for n in feasible for t in n["taints"]):
        raw = {
            n["name"]: sum(1 for t in n["taints"] if t["effect"] == "PreferNoSchedule" and not tolerates(t, pod["tolerations"]))
            for n in feasible
        }
        for name, val in _normalize(raw, reverse=True).items():
            breakdown[name]["TaintToleration"] = val

    for n in feasible:
        free_cpu = (n["cpu"] - sum(p["cpu"] for p in n["pods"]) - pod["cpu"]) / max(n["cpu"], 1)
        free_mem = (n["memory"] - sum(p["memory"] for p in n["pods"]) - pod["memory"]) / max(n["memory"], 1)
        breakdown[n["name"]]["LeastAllocated"] = int(round(max(0.0, (free_cpu + free_mem) / 2) * 100))

    aff_pref = pod["podAffinity"].get("preferredDuringSchedulingIgnoredDuringExecution") or []
    anti_pref = pod["podAntiAffinity"].get("preferredDuringSchedulingIgnoredDuringExecution") or []
    if aff_pref or anti_pref:
        raw = {}
        for n in feasible:
            total = 0
            for sign, terms in ((1, aff_pref), (-1, anti_pref)):
                for t in terms:
                    term = t.get("podAffinityTerm") or {}
                    pods = _domain_pods(nodes, n, term.get("topologyKey", HOSTNAME_KEY))
                    if any(match_selector(p["labels"], term.get("labelSelector")) for p in pods):
                        total += sign * int(t.get("weight", 1))
            raw[n["name"]] = total
        for name, val in _normalize(raw).items():
            breakdown[name]["InterPodAffinity"] = val

    soft = [c for c in pod["spread"] if c.get("whenUnsatisfiable") == "ScheduleAnyway"]
    if soft:
        raw = {
            n["name"]: sum(_spread_skew(pod, n, nodes, c) for c in soft if c.get("topologyKey") in n["labels"])
            for n in feasible
        }
        for name, val in _normalize(raw, reverse=True).items():
            breakdown[name]["PodTopologySpread"] = val

    return breakdown


# --------------------------------------------------------------------------- driver

def _schedule_one(pod: dict, nodes: list[dict]) -> dict:
    results = []
    feasible = []
    for node in nodes:
        failures, passed = _filter(pod, node, nodes)
        results.append({"name": node["name"], "feasible": not failures, "failures": [f[1] for f in failures],
                        "plugins": sorted({f[0] for f in failures}), "passed": passed})
        if not failures:
            feasible.append(node)

    breakdown = _score(pod, feasible, nodes) if feasible else {}
    for r in results:
        if r["feasible"]:
            r["breakdown"] = breakdown[r["name"]]
            r["score"] = sum(breakdown[r["name"]].values())

    chosen = None
    if feasible:
        best = max(results, key=lambda r: (r.get("score", -1), -nodes.index(next(n for n in nodes if n["name"] == r["name"]))))
        chosen = best["name"]

    message = None
    if not chosen:
        counts = Counter(r["failures"][0] for r in results if r["failures"])
        parts = ", ".join(f"{c} {m}" for m, c in sorted(counts.items()))
        message = f"0/{len(nodes)} nodes are available: {parts}. preemption: 0/{len(nodes)} nodes are available."
    return {"node": chosen, "nodes": results, "message": message}


def simulate(nodes_yaml: str, pod_yaml: str) -> dict:
    nodes = parse_nodes(nodes_yaml)
    pod = parse_workload(pod_yaml)
    placements = []
    working = deepcopy(nodes)

    if pod["kind"] == "DaemonSet":
        for node in working:
            res = _schedule_one({**pod, "nodeName": node["name"]}, [node])
            placements.append({"replica": f"{pod['name']}-{node['name']}", **res, "nodes": res["nodes"]})
    else:
        for i in range(pod["replicas"]):
            res = _schedule_one(pod, working)
            replica_name = f"{pod['name']}-{i}" if pod["kind"] == "StatefulSet" else f"{pod['name']}-{i + 1}"
            placements.append({"replica": replica_name, **res})
            if res["node"]:
                target = next(n for n in working if n["name"] == res["node"])
                target["pods"].append({"name": replica_name, "labels": pod["labels"], "cpu": pod["cpu"], "memory": pod["memory"], "existing": False})

    scheduled = sum(1 for p in placements if p["node"])
    return {
        "workload": {k: pod[k] for k in ("kind", "name", "labels", "replicas", "cpu")} | {"memory": round(pod["memory"])},
        "nodes": [
            {"name": n["name"], "labels": {k: v for k, v in n["labels"].items() if k != HOSTNAME_KEY},
             "taints": [taint_str(t) for t in n["taints"]], "cpu": n["cpu"], "memory": round(n["memory"]),
             "unschedulable": n["unschedulable"],
             "pods": [{"name": p["name"], "labels": p["labels"]} for p in n["pods"]]}
            for n in nodes
        ],
        "placements": placements,
        "summary": f"{scheduled}/{len(placements)} replica(s) scheduled" + (
            "" if scheduled == len(placements) else f", {len(placements) - scheduled} Pending"
        ),
    }


# --------------------------------------------------------------------------- presets

BASE_NODES = """\
nodes:
  - name: worker-1
    labels: {topology.kubernetes.io/zone: zone-a, disktype: ssd, tier: frontend}
    allocatable: {cpu: "2", memory: 4Gi}
    pods:
      - {name: cache-1, labels: {app: cache}, cpu: 250m, memory: 256Mi}
  - name: worker-2
    labels: {topology.kubernetes.io/zone: zone-b, disktype: hdd, tier: backend}
    allocatable: {cpu: "2", memory: 4Gi}
  - name: worker-3
    labels: {topology.kubernetes.io/zone: zone-c, disktype: ssd, gpu: "true"}
    taints: ["dedicated=gpu:NoSchedule"]
    allocatable: {cpu: "4", memory: 8Gi}
"""

PRESETS = [
    {
        "id": "nodeselector",
        "title": "nodeSelector: SSD only",
        "hint": "worker-3 also has disktype=ssd, but it is tainted. Which node wins and why?",
        "nodes": BASE_NODES,
        "pod": """\
apiVersion: apps/v1
kind: Deployment
metadata: {name: web}
spec:
  replicas: 2
  selector: {matchLabels: {app: web}}
  template:
    metadata: {labels: {app: web}}
    spec:
      nodeSelector:
        disktype: ssd
      containers:
        - name: web
          image: nginx:1.27-alpine
          resources: {requests: {cpu: 200m, memory: 128Mi}}
""",
    },
    {
        "id": "node-affinity",
        "title": "Node affinity: required zones + preferred disk",
        "hint": "Required = hard filter, preferred = score. Try changing the weight or operator to NotIn.",
        "nodes": BASE_NODES,
        "pod": """\
apiVersion: v1
kind: Pod
metadata: {name: api, labels: {app: api}}
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
          - matchExpressions:
              - {key: topology.kubernetes.io/zone, operator: In, values: [zone-a, zone-b]}
      preferredDuringSchedulingIgnoredDuringExecution:
        - weight: 80
          preference:
            matchExpressions:
              - {key: disktype, operator: In, values: [hdd]}
  containers:
    - name: api
      image: nginx:1.27-alpine
""",
    },
    {
        "id": "taints",
        "title": "Taints: GPU node needs a toleration",
        "hint": "Remove the toleration and watch FailedScheduling. Toleration alone doesn't attract — the nodeSelector does.",
        "nodes": BASE_NODES,
        "pod": """\
apiVersion: v1
kind: Pod
metadata: {name: trainer, labels: {app: trainer}}
spec:
  nodeSelector: {gpu: "true"}
  tolerations:
    - key: dedicated
      operator: Equal
      value: gpu
      effect: NoSchedule
  containers:
    - name: trainer
      image: busybox:1.36
      resources: {requests: {cpu: "1", memory: 1Gi}}
""",
    },
    {
        "id": "anti-affinity",
        "title": "Pod anti-affinity: 1 replica per node",
        "hint": "4 replicas, but only 2 untainted workers → 2 stay Pending. Switch to preferred... to make it soft.",
        "nodes": BASE_NODES,
        "pod": """\
apiVersion: apps/v1
kind: Deployment
metadata: {name: web}
spec:
  replicas: 4
  selector: {matchLabels: {app: web}}
  template:
    metadata: {labels: {app: web}}
    spec:
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            - labelSelector: {matchLabels: {app: web}}
              topologyKey: kubernetes.io/hostname
      containers:
        - name: web
          image: nginx:1.27-alpine
""",
    },
    {
        "id": "pod-affinity",
        "title": "Pod affinity: co-locate with cache",
        "hint": "The pod must land where an app=cache pod already runs (same hostname).",
        "nodes": BASE_NODES,
        "pod": """\
apiVersion: v1
kind: Pod
metadata: {name: web, labels: {app: web}}
spec:
  affinity:
    podAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        - labelSelector: {matchLabels: {app: cache}}
          topologyKey: kubernetes.io/hostname
  containers:
    - name: web
      image: nginx:1.27-alpine
""",
    },
    {
        "id": "resources",
        "title": "Insufficient CPU",
        "hint": "Requests (not actual usage) drive scheduling. Lower the request to make it fit.",
        "nodes": BASE_NODES,
        "pod": """\
apiVersion: apps/v1
kind: Deployment
metadata: {name: heavy}
spec:
  replicas: 3
  selector: {matchLabels: {app: heavy}}
  template:
    metadata: {labels: {app: heavy}}
    spec:
      containers:
        - name: heavy
          image: busybox:1.36
          resources: {requests: {cpu: 1500m, memory: 1Gi}}
""",
    },
    {
        "id": "spread",
        "title": "Topology spread across zones",
        "hint": "Gotcha: zone-c still counts as a domain (nodeTaintsPolicy defaults to Ignore) so replicas 3-4 go Pending. Add `nodeTaintsPolicy: Honor` to the constraint and re-run.",
        "nodes": BASE_NODES,
        "pod": """\
apiVersion: apps/v1
kind: Deployment
metadata: {name: shop}
spec:
  replicas: 4
  selector: {matchLabels: {app: shop}}
  template:
    metadata: {labels: {app: shop}}
    spec:
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: DoNotSchedule
          labelSelector: {matchLabels: {app: shop}}
      containers:
        - name: shop
          image: nginx:1.27-alpine
          resources: {requests: {cpu: 100m, memory: 64Mi}}
""",
    },
    {
        "id": "cordon",
        "title": "Cordoned node (kubectl cordon)",
        "hint": "unschedulable: true blocks NEW pods only; existing pods keep running until drained.",
        "nodes": BASE_NODES.replace("  - name: worker-2\n", "  - name: worker-2\n    unschedulable: true\n"),
        "pod": """\
apiVersion: v1
kind: Pod
metadata: {name: batch, labels: {app: batch}}
spec:
  nodeSelector: {tier: backend}
  containers:
    - name: batch
      image: busybox:1.36
""",
    },
]
