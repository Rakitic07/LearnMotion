"""Guarded wrapper around kind/kubectl, pinned to the local playground cluster."""

from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import yaml

CLUSTER_NAME = os.environ.get("K8S_PLAYGROUND_CLUSTER", "k8s-playground")
CONTEXT = f"kind-{CLUSTER_NAME}"
ROOT = Path(__file__).resolve().parent.parent
SETUP_SCRIPT = ROOT / "scripts" / "setup_cluster.sh"
TEARDOWN_SCRIPT = ROOT / "scripts" / "teardown.sh"

SYSTEM_NAMESPACES = {
    "kube-system",
    "kube-public",
    "kube-node-lease",
    "local-path-storage",
    "ingress-nginx",
}
MAX_MANIFEST_BYTES = 200_000
DEFAULT_TIMEOUT = 45

ALLOWED_VERBS = {
    "get", "describe", "logs", "top", "explain", "api-resources", "api-versions",
    "version", "cluster-info", "rollout", "scale", "label", "annotate", "taint",
    "cordon", "uncordon", "drain", "delete", "create", "run", "expose", "set",
    "autoscale", "auth", "events", "wait", "patch",
}
# Flags that would escape the playground context, block forever, or need a TTY.
FORBIDDEN_FLAGS = {
    "--context", "--kubeconfig", "--server", "-s", "--token", "--user", "--cluster",
    "--certificate-authority", "--client-key", "--client-certificate",
    "--insecure-skip-tls-verify", "-f", "--filename", "-k", "--kustomize",
    "-w", "--watch", "--watch-only", "--follow", "--raw", "-i", "-t", "-it", "-ti",
    "--stdin", "--tty", "--attach", "--rm", "--edit",
}


class KubeError(ValueError):
    """Raised for rejected input (bad command, oversized manifest...)."""


def _run(args: list[str], input_text: str | None = None, timeout: int = DEFAULT_TIMEOUT, env: dict | None = None) -> dict:
    started = time.time()
    try:
        proc = subprocess.run(args, input=input_text, capture_output=True, text=True, timeout=timeout, env=env)
    except FileNotFoundError:
        return {"ok": False, "code": 127, "stdout": "", "stderr": f"{args[0]}: command not found", "ms": 0}
    except subprocess.TimeoutExpired as exc:
        out = exc.stdout.decode() if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        return {"ok": False, "code": 124, "stdout": out, "stderr": f"timed out after {timeout}s", "ms": timeout * 1000}
    return {
        "ok": proc.returncode == 0,
        "code": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "ms": int((time.time() - started) * 1000),
    }


def kubectl(args: list[str], input_text: str | None = None, timeout: int = DEFAULT_TIMEOUT) -> dict:
    return _run(["kubectl", "--context", CONTEXT, *args], input_text=input_text, timeout=timeout)


# --------------------------------------------------------------------------- status

RUNTIMES = ("podman", "docker")


def tool_status() -> dict:
    """Mirrors scripts/runtime.sh: forced runtime, else a running Podman, else a running Docker."""
    installed = {name: shutil.which(name) is not None for name in (*RUNTIMES, "kind", "kubectl")}
    running = {name: installed[name] and _run([name, "info"], timeout=8)["ok"] for name in RUNTIMES}
    forced = os.environ.get("K8S_PLAYGROUND_RUNTIME")
    if forced in RUNTIMES:
        runtime = forced
    else:
        runtime = next((r for r in RUNTIMES if running[r]), None) or next((r for r in RUNTIMES if installed[r]), None)
    rootless = None
    if runtime == "podman" and running["podman"]:
        res = _run(["podman", "info", "--format", "{{.Host.Security.Rootless}}"], timeout=8)
        rootless = res["stdout"].strip() == "true" if res["ok"] else None
    return {
        **installed,
        "runtime": runtime,
        "runtime_installed": bool(runtime and installed[runtime]),
        "runtime_running": bool(runtime and running[runtime]),
        "rootless": rootless,
    }


def _kind_env(runtime: str | None) -> dict:
    env = {**os.environ, "K8S_PLAYGROUND_CLUSTER": CLUSTER_NAME}
    if runtime == "podman":
        env["KIND_EXPERIMENTAL_PROVIDER"] = "podman"
    return env


def cluster_status() -> dict:
    tools = tool_status()
    exists = False
    reachable = False
    if tools["kind"] and tools["runtime_running"]:
        res = _run(["kind", "get", "clusters"], timeout=15, env=_kind_env(tools["runtime"]))
        exists = CLUSTER_NAME in res["stdout"].split()
    if exists and tools["kubectl"]:
        reachable = kubectl(["get", "--raw", "/readyz"], timeout=8)["ok"]
    return {
        "tools": tools,
        "cluster": CLUSTER_NAME,
        "context": CONTEXT,
        "exists": exists,
        "reachable": reachable,
        "job": JOBS.current(),
    }


def _json(res: dict) -> dict:
    if not res["ok"]:
        return {"items": []}
    try:
        return json.loads(res["stdout"] or "{}")
    except json.JSONDecodeError:
        return {"items": []}


def _short_labels(labels: dict) -> dict:
    out = {}
    for key, value in (labels or {}).items():
        if key == "topology.kubernetes.io/zone":
            out["zone"] = value
        elif key.startswith(("kubernetes.io/", "beta.kubernetes.io/", "node-role.kubernetes.io/", "node.kubernetes.io/")):
            continue
        elif key in ("ingress-ready",):
            continue
        else:
            out[key] = value
    return out


def _pod_status(pod: dict) -> tuple[str, str]:
    meta, status = pod.get("metadata", {}), pod.get("status", {})
    if meta.get("deletionTimestamp"):
        return "Terminating", ""
    for cs in (status.get("initContainerStatuses") or []):
        waiting = (cs.get("state") or {}).get("waiting")
        if waiting and waiting.get("reason") not in (None, "PodInitializing"):
            return f"Init:{waiting['reason']}", waiting.get("message", "")
        if (cs.get("state") or {}).get("running"):
            return "Init:Running", ""
    for cs in (status.get("containerStatuses") or []):
        state = cs.get("state") or {}
        if state.get("waiting") and state["waiting"].get("reason"):
            return state["waiting"]["reason"], state["waiting"].get("message", "")
        if state.get("terminated") and status.get("phase") not in ("Succeeded",):
            return state["terminated"].get("reason", "Terminated"), ""
    if status.get("phase") == "Pending":
        for cond in status.get("conditions") or []:
            if cond.get("type") == "PodScheduled" and cond.get("status") == "False":
                return cond.get("reason", "Pending"), cond.get("message", "")
    if status.get("phase") == "Running":
        ready = all(cs.get("ready") for cs in status.get("containerStatuses") or [])
        return ("Running" if ready else "NotReady"), ""
    return status.get("phase", "Unknown"), ""


def _summarize_node(node: dict) -> dict:
    meta, spec, status = node["metadata"], node.get("spec", {}), node.get("status", {})
    labels = meta.get("labels", {})
    ready = any(c.get("type") == "Ready" and c.get("status") == "True" for c in status.get("conditions", []))
    return {
        "name": meta["name"],
        "role": "control-plane" if "node-role.kubernetes.io/control-plane" in labels else "worker",
        "ready": ready,
        "unschedulable": bool(spec.get("unschedulable")),
        "labels": _short_labels(labels),
        "taints": [
            f"{t['key']}{'=' + t['value'] if t.get('value') else ''}:{t['effect']}" for t in spec.get("taints", []) or []
        ],
        "cpu": status.get("allocatable", {}).get("cpu"),
        "memory": status.get("allocatable", {}).get("memory"),
    }


def _summarize_pod(pod: dict) -> dict:
    meta, spec, status = pod["metadata"], pod.get("spec", {}), pod.get("status", {})
    reason, message = _pod_status(pod)
    cstat = status.get("containerStatuses") or []
    owner = (meta.get("ownerReferences") or [{}])[0]
    requests = [((c.get("resources") or {}).get("requests") or {}) for c in spec.get("containers", [])]
    return {
        "namespace": meta["namespace"],
        "name": meta["name"],
        "node": spec.get("nodeName"),
        "status": reason,
        "message": message,
        "ready": f"{sum(1 for c in cstat if c.get('ready'))}/{len(spec.get('containers', []))}",
        "restarts": sum(c.get("restartCount", 0) for c in cstat),
        "app": (meta.get("labels") or {}).get("app") or (meta.get("labels") or {}).get("app.kubernetes.io/name"),
        "owner": owner.get("kind"),
        "requests": {
            "cpu": ",".join(r["cpu"] for r in requests if r.get("cpu")),
            "memory": ",".join(r["memory"] for r in requests if r.get("memory")),
        },
    }


def _summarize_hpa(hpa: dict) -> dict:
    spec, status = hpa.get("spec", {}), hpa.get("status", {})
    target = current = None
    for metric in spec.get("metrics", []) or []:
        if metric.get("type") == "Resource":
            target = (metric["resource"].get("target") or {}).get("averageUtilization")
            break
    for metric in status.get("currentMetrics", []) or []:
        if metric.get("type") == "Resource":
            current = (metric["resource"].get("current") or {}).get("averageUtilization")
            break
    return {
        "namespace": hpa["metadata"]["namespace"],
        "name": hpa["metadata"]["name"],
        "target": f"{spec.get('scaleTargetRef', {}).get('kind')}/{spec.get('scaleTargetRef', {}).get('name')}",
        "min": spec.get("minReplicas", 1),
        "max": spec.get("maxReplicas"),
        "current": status.get("currentReplicas"),
        "desired": status.get("desiredReplicas"),
        "cpuCurrent": current,
        "cpuTarget": target,
    }


def cluster_state(include_system: bool = False) -> dict:
    queries = {
        "nodes": ["get", "nodes", "-o", "json"],
        "pods": ["get", "pods", "-A", "-o", "json"],
        "deployments": ["get", "deployments", "-A", "-o", "json"],
        "services": ["get", "services", "-A", "-o", "json"],
        "hpa": ["get", "hpa", "-A", "-o", "json"],
        "events": ["get", "events", "-A", "-o", "json"],
    }
    with ThreadPoolExecutor(max_workers=len(queries)) as pool:
        futures = {key: pool.submit(kubectl, args, None, 20) for key, args in queries.items()}
        raw = {key: fut.result() for key, fut in futures.items()}

    if not raw["nodes"]["ok"]:
        return {"ok": False, "error": raw["nodes"]["stderr"].strip() or "cluster unreachable"}

    def visible(item: dict) -> bool:
        return include_system or item["metadata"].get("namespace") not in SYSTEM_NAMESPACES

    events = [e for e in _json(raw["events"]).get("items", []) if visible(e)]
    events.sort(key=lambda e: e.get("lastTimestamp") or e.get("eventTime") or e["metadata"].get("creationTimestamp") or "")
    return {
        "ok": True,
        "nodes": [_summarize_node(n) for n in _json(raw["nodes"]).get("items", [])],
        "pods": [_summarize_pod(p) for p in _json(raw["pods"]).get("items", []) if visible(p)],
        "deployments": [
            {
                "namespace": d["metadata"]["namespace"],
                "name": d["metadata"]["name"],
                "ready": f"{d.get('status', {}).get('readyReplicas', 0)}/{d.get('spec', {}).get('replicas', 0)}",
                "images": [c.get("image") for c in d["spec"]["template"]["spec"].get("containers", [])],
            }
            for d in _json(raw["deployments"]).get("items", [])
            if visible(d)
        ],
        "services": [
            {
                "namespace": s["metadata"]["namespace"],
                "name": s["metadata"]["name"],
                "type": s.get("spec", {}).get("type"),
                "clusterIP": s.get("spec", {}).get("clusterIP"),
                "ports": [f"{p.get('port')}{'/' + str(p['nodePort']) if p.get('nodePort') else ''}" for p in s.get("spec", {}).get("ports", []) or []],
            }
            for s in _json(raw["services"]).get("items", [])
            if visible(s)
        ],
        "hpa": [_summarize_hpa(h) for h in _json(raw["hpa"]).get("items", []) if visible(h)],
        "events": [
            {
                "type": e.get("type"),
                "reason": e.get("reason"),
                "object": f"{e.get('involvedObject', {}).get('kind')}/{e.get('involvedObject', {}).get('name')}",
                "message": e.get("message"),
                "count": e.get("count", 1),
            }
            for e in events[-25:]
        ],
    }


# --------------------------------------------------------------------------- mutations

def _validate_manifest(text: str) -> list[dict]:
    if not text or not text.strip():
        raise KubeError("Manifest is empty.")
    if len(text.encode()) > MAX_MANIFEST_BYTES:
        raise KubeError("Manifest is too large (200 KB max).")
    try:
        docs = [d for d in yaml.safe_load_all(text) if d is not None]
    except yaml.YAMLError as exc:
        raise KubeError(f"Invalid YAML: {exc}") from exc
    if not docs:
        raise KubeError("Manifest has no documents.")
    for doc in docs:
        if not isinstance(doc, dict) or "kind" not in doc or "apiVersion" not in doc:
            raise KubeError("Every YAML document needs apiVersion and kind.")
    return docs


def apply_manifest(text: str, dry_run: bool = False) -> dict:
    _validate_manifest(text)
    args = ["apply", "-f", "-"]
    if dry_run:
        args.append("--dry-run=server")
    return kubectl(args, input_text=text)


def delete_manifest(text: str) -> dict:
    _validate_manifest(text)
    return kubectl(["delete", "-f", "-", "--ignore-not-found", "--wait=false"], input_text=text)


def parse_command(command: str) -> list[str]:
    try:
        tokens = shlex.split(command.strip())
    except ValueError as exc:
        raise KubeError(f"Could not parse command: {exc}") from exc
    if tokens and tokens[0] in ("kubectl", "k"):
        tokens = tokens[1:]
    if not tokens:
        raise KubeError("Type a kubectl command, e.g. `kubectl get pods -o wide`.")
    verb = tokens[0]
    if verb not in ALLOWED_VERBS:
        raise KubeError(
            f"`{verb}` is not allowed in the web console. Allowed: {', '.join(sorted(ALLOWED_VERBS))}. "
            "Use the YAML tab to apply manifests."
        )
    for token in tokens[1:]:
        flag = token.split("=", 1)[0]
        if flag in FORBIDDEN_FLAGS:
            raise KubeError(f"Flag `{flag}` is disabled in the web console (context-pinned / non-interactive).")
    return tokens


def run_command(command: str) -> dict:
    tokens = parse_command(command)
    return {**kubectl(tokens, timeout=90 if tokens[0] in ("drain", "wait") else DEFAULT_TIMEOUT), "argv": ["kubectl", *tokens]}


# --------------------------------------------------------------------------- background jobs

class Job:
    def __init__(self, name: str, argv: list[str]):
        self.id = uuid.uuid4().hex[:8]
        self.name = name
        self.argv = argv
        self.lines: list[str] = []
        self.status = "running"
        self.started = time.time()
        self.ended: float | None = None

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "started": self.started,
            "ended": self.ended,
            "log": "\n".join(self.lines[-400:]),
        }


class JobManager:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._job: Job | None = None

    def current(self) -> dict | None:
        with self._lock:
            return self._job.as_dict() if self._job else None

    def start(self, name: str, argv: list[str]) -> dict:
        with self._lock:
            if self._job and self._job.status == "running":
                raise KubeError(f"A job is already running: {self._job.name}")
            job = Job(name, argv)
            self._job = job
        threading.Thread(target=self._run, args=(job,), daemon=True).start()
        return job.as_dict()

    @staticmethod
    def _run(job: Job) -> None:
        env = {**os.environ, "K8S_PLAYGROUND_CLUSTER": CLUSTER_NAME}
        try:
            proc = subprocess.Popen(
                job.argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env, cwd=ROOT
            )
            assert proc.stdout is not None
            for line in proc.stdout:
                job.lines.append(line.rstrip())
            job.status = "succeeded" if proc.wait() == 0 else "failed"
        except OSError as exc:
            job.lines.append(f"Failed to start: {exc}")
            job.status = "failed"
        job.ended = time.time()


JOBS = JobManager()


def create_cluster(ingress: bool = False, vpa: bool = False, recreate: bool = False) -> dict:
    argv = ["bash", str(SETUP_SCRIPT)]
    if ingress:
        argv.append("--with-ingress")
    if vpa:
        argv.append("--with-vpa")
    if recreate:
        argv.append("--recreate")
    return JOBS.start("create-cluster", argv)


def delete_cluster() -> dict:
    return JOBS.start("delete-cluster", ["bash", str(TEARDOWN_SCRIPT)])
