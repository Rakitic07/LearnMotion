import pytest
import yaml

from app import simulator as sim

NODES = """
nodes:
  - name: a
    labels: {zone: z1, disktype: ssd}
    allocatable: {cpu: "1", memory: 1Gi}
  - name: b
    labels: {zone: z2, disktype: hdd}
    allocatable: {cpu: "1", memory: 1Gi}
  - name: gpu
    labels: {zone: z3, gpu: "true"}
    taints: ["dedicated=gpu:NoSchedule"]
"""

ANTI = {"podAntiAffinity": {"requiredDuringSchedulingIgnoredDuringExecution": [
    {"labelSelector": {"matchLabels": {"app": "web"}}, "topologyKey": "kubernetes.io/hostname"}]}}
GPU_TOLERATION = [{"key": "dedicated", "operator": "Equal", "value": "gpu", "effect": "NoSchedule"}]


def workload(kind="Pod", replicas=1, cpu=None, **spec):
    container = {"name": "c", "image": "x"}
    if cpu:
        container["resources"] = {"requests": {"cpu": cpu}}
    pod_spec = {"containers": [container], **spec}
    if kind == "Pod":
        doc = {"apiVersion": "v1", "kind": "Pod", "metadata": {"name": "p", "labels": {"app": "web"}}, "spec": pod_spec}
    else:
        doc = {"apiVersion": "apps/v1", "kind": kind, "metadata": {"name": "web"},
               "spec": {"replicas": replicas, "template": {"metadata": {"labels": {"app": "web"}}, "spec": pod_spec}}}
    return yaml.safe_dump(doc)


def placed(result):
    return [p["node"] for p in result["placements"]]


def test_quantities():
    assert sim.parse_cpu("250m") == 250
    assert sim.parse_cpu("1.5") == 1500
    assert sim.parse_cpu(2) == 2000
    assert sim.parse_mem("1Gi") == 1024
    assert sim.parse_mem("512Mi") == 512
    with pytest.raises(sim.SimulationError):
        sim.parse_mem("lots")


def test_node_selector_filters():
    assert placed(sim.simulate(NODES, workload(nodeSelector={"disktype": "hdd"}))) == ["b"]


def test_taint_blocks_and_toleration_allows():
    blocked = sim.simulate(NODES, workload(nodeSelector={"gpu": "true"}))
    assert placed(blocked) == [None]
    assert "untolerated taint {dedicated=gpu:NoSchedule}" in blocked["placements"][0]["message"]
    allowed = sim.simulate(NODES, workload(nodeSelector={"gpu": "true"}, tolerations=GPU_TOLERATION))
    assert placed(allowed) == ["gpu"]


def test_exists_toleration_without_key_tolerates_everything():
    assert sim.tolerates({"key": "x", "value": "y", "effect": "NoExecute"}, [{"operator": "Exists"}])


def test_required_and_preferred_node_affinity():
    affinity = {"nodeAffinity": {
        "requiredDuringSchedulingIgnoredDuringExecution": {"nodeSelectorTerms": [
            {"matchExpressions": [{"key": "zone", "operator": "In", "values": ["z1", "z2"]}]}]},
        "preferredDuringSchedulingIgnoredDuringExecution": [
            {"weight": 100, "preference": {"matchExpressions": [{"key": "disktype", "operator": "In", "values": ["hdd"]}]}}],
    }}
    r = sim.simulate(NODES, workload(affinity=affinity))
    assert placed(r) == ["b"]
    gpu = next(n for n in r["placements"][0]["nodes"] if n["name"] == "gpu")
    assert not gpu["feasible"]


def test_not_in_matches_missing_label():
    assert sim.match_expression({}, {"key": "disktype", "operator": "NotIn", "values": ["ssd"]})


def test_hard_anti_affinity_leaves_extra_replicas_pending():
    r = sim.simulate(NODES, workload("Deployment", replicas=3, affinity=ANTI))
    assert sorted(n for n in placed(r) if n) == ["a", "b"]
    assert placed(r).count(None) == 1
    assert "anti-affinity" in r["placements"][2]["message"]


def test_insufficient_cpu():
    r = sim.simulate(NODES, workload("Deployment", replicas=3, cpu="800m"))
    assert placed(r).count(None) == 1
    assert "Insufficient cpu" in r["placements"][2]["message"]


def test_pod_affinity_first_pod_rule():
    affinity = {"podAffinity": {"requiredDuringSchedulingIgnoredDuringExecution": [
        {"labelSelector": {"matchLabels": {"app": "web"}}, "topologyKey": "zone"}]}}
    first, second = placed(sim.simulate(NODES, workload("Deployment", replicas=2, affinity=affinity)))
    assert first is not None and first == second


def test_topology_spread_taint_policy():
    constraint = {"maxSkew": 1, "topologyKey": "zone", "whenUnsatisfiable": "DoNotSchedule",
                  "labelSelector": {"matchLabels": {"app": "web"}}}
    ignore = sim.simulate(NODES, workload("Deployment", replicas=4, topologySpreadConstraints=[constraint]))
    assert placed(ignore).count(None) == 2
    honor = sim.simulate(NODES, workload("Deployment", replicas=4, topologySpreadConstraints=[{**constraint, "nodeTaintsPolicy": "Honor"}]))
    assert placed(honor).count(None) == 0


def test_cordoned_node_rejected():
    nodes = NODES.replace("  - name: b\n", "  - name: b\n    unschedulable: true\n")
    r = sim.simulate(nodes, workload(nodeSelector={"disktype": "hdd"}))
    assert placed(r) == [None]
    assert "were unschedulable" in r["placements"][0]["message"]


def test_daemonset_targets_every_feasible_node():
    r = sim.simulate(NODES, workload("DaemonSet"))
    assert sorted(n for n in placed(r) if n) == ["a", "b"]


def test_all_presets_run():
    for preset in sim.PRESETS:
        assert sim.simulate(preset["nodes"], preset["pod"])["placements"], preset["id"]


def test_invalid_input():
    with pytest.raises(sim.SimulationError):
        sim.simulate("nodes: []", workload())
    with pytest.raises(sim.SimulationError):
        sim.simulate(NODES, "kind: Service\napiVersion: v1\nmetadata: {name: s}")
