import yaml
import pytest

from app import create_app, kube
from app.labs import LABS
from app.topics import TOPICS

HEADERS = {"X-K8s-Playground": "1"}


@pytest.fixture()
def client():
    return create_app().test_client()


def test_index_and_content(client):
    assert client.get("/").status_code == 200
    data = client.get("/api/content").get_json()
    assert len(data["topics"]) == len(TOPICS) >= 20
    assert {t["id"] for t in data["topics"]} >= {"nodeselector", "node-affinity", "hpa", "vpa", "configmaps"}


def test_games_tab_and_assets(client):
    assert b'id="nav"' in client.get("/").data
    for name in ("games.js", "games-data.js"):
        res = client.get(f"/static/js/{name}")
        assert res.status_code == 200
        res.close()


def test_topic_404(client):
    assert client.get("/api/topics/nope").status_code == 404
    assert client.get("/api/topics/hpa").get_json()["id"] == "hpa"


def test_every_topic_is_complete():
    for t in TOPICS:
        for key in ("what", "analogy", "use_cases", "key_points", "examples", "commands", "interview"):
            assert t[key], f"{t['id']} missing {key}"
        assert t.get("scene") or t.get("flow"), f"{t['id']} needs a scene or a flow"
        for ex in t["examples"]:
            docs = [d for d in yaml.safe_load_all(ex["yaml"]) if d]
            assert all("apiVersion" in d and "kind" in d for d in docs), f"{t['id']}: {ex['title']}"


def test_lab_manifests_parse():
    for lab in LABS:
        for step in lab["steps"]:
            if step["kind"] == "cmd":
                kube.parse_command(step["content"])
            else:
                kube._validate_manifest(step["content"])


def test_post_requires_header_and_json(client):
    assert client.post("/api/simulate", json={}).status_code == 403
    assert client.post("/api/simulate", data="x", headers=HEADERS).status_code == 403


def test_foreign_host_rejected(client):
    assert client.get("/api/content", headers={"Host": "evil.example.com"}).status_code == 403


def test_simulate_endpoint(client):
    from app.simulator import PRESETS

    res = client.post("/api/simulate", json={"nodes": PRESETS[0]["nodes"], "pod": PRESETS[0]["pod"]}, headers=HEADERS)
    assert res.status_code == 200 and res.get_json()["ok"]
    bad = client.post("/api/simulate", json={"nodes": "nodes: []", "pod": ""}, headers=HEADERS)
    assert bad.status_code == 400


@pytest.mark.parametrize("command", [
    "kubectl exec -it pod -- sh",
    "kubectl get pods --context other",
    "kubectl get pods --kubeconfig=/tmp/x",
    "kubectl apply -f evil.yaml",
    "kubectl get pods -w",
    "kubectl port-forward svc/x 80",
    "rm -rf /",
])
def test_console_rejects_dangerous_commands(command):
    with pytest.raises(kube.KubeError):
        kube.parse_command(command)


def test_console_accepts_common_commands():
    assert kube.parse_command("kubectl get pods -o wide") == ["get", "pods", "-o", "wide"]
    assert kube.parse_command("k describe node x")[0] == "describe"
    assert kube.parse_command("kubectl auth can-i list pods --as=system:serviceaccount:default:ci-bot")[0] == "auth"


def test_manifest_validation():
    with pytest.raises(kube.KubeError):
        kube._validate_manifest("")
    with pytest.raises(kube.KubeError):
        kube._validate_manifest("foo: bar")
    with pytest.raises(kube.KubeError):
        kube._validate_manifest("a" * (kube.MAX_MANIFEST_BYTES + 1))


def test_kubectl_is_context_pinned(monkeypatch):
    captured = {}

    def fake_run(args, **kwargs):
        captured["args"] = args
        return {"ok": True, "code": 0, "stdout": "", "stderr": "", "ms": 0}

    monkeypatch.setattr(kube, "_run", fake_run)
    kube.run_command("kubectl get pods")
    assert captured["args"][:3] == ["kubectl", "--context", kube.CONTEXT]


def fake_host(monkeypatch, installed, running, rootless="false"):
    calls = []

    def fake_run(args, **kwargs):
        calls.append((args, kwargs.get("env")))
        if args[1:] == ["info"]:
            ok = args[0] in running
            return {"ok": ok, "code": 0 if ok else 1, "stdout": "", "stderr": "", "ms": 0}
        if args[:2] == ["podman", "info"]:
            return {"ok": True, "code": 0, "stdout": rootless + "\n", "stderr": "", "ms": 0}
        return {"ok": True, "code": 0, "stdout": "k8s-playground\n", "stderr": "", "ms": 0}

    monkeypatch.setattr(kube.shutil, "which", lambda name: f"/bin/{name}" if name in installed else None)
    monkeypatch.setattr(kube, "_run", fake_run)
    monkeypatch.delenv("K8S_PLAYGROUND_RUNTIME", raising=False)
    return calls


def test_runtime_prefers_running_podman(monkeypatch):
    fake_host(monkeypatch, {"podman", "docker", "kind", "kubectl"}, {"podman"}, rootless="true")
    t = kube.tool_status()
    assert (t["runtime"], t["runtime_running"], t["rootless"]) == ("podman", True, True)


def test_runtime_falls_back_to_running_docker(monkeypatch):
    fake_host(monkeypatch, {"podman", "docker", "kind"}, {"docker"})
    t = kube.tool_status()
    assert (t["runtime"], t["runtime_running"], t["rootless"]) == ("docker", True, None)


def test_runtime_override_and_stopped_machine(monkeypatch):
    fake_host(monkeypatch, {"podman", "docker"}, {"docker"})
    monkeypatch.setenv("K8S_PLAYGROUND_RUNTIME", "podman")
    t = kube.tool_status()
    assert (t["runtime"], t["runtime_installed"], t["runtime_running"]) == ("podman", True, False)


def test_kind_uses_podman_provider(monkeypatch):
    calls = fake_host(monkeypatch, {"podman", "kind", "kubectl"}, {"podman"})
    assert kube.cluster_status()["exists"] is True
    kind_env = next(env for args, env in calls if args[0] == "kind")
    assert kind_env["KIND_EXPERIMENTAL_PROVIDER"] == "podman"
