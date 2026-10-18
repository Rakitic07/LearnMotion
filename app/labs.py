"""Guided hands-on labs for the kind playground cluster (node names assume cluster `k8s-playground`)."""

from .kube import CLUSTER_NAME
from .topics import y

W1, W2, W3 = f"{CLUSTER_NAME}-worker", f"{CLUSTER_NAME}-worker2", f"{CLUSTER_NAME}-worker3"


def cmd(title: str, command: str, text: str = "") -> dict:
    return {"title": title, "kind": "cmd", "content": command, "text": text}


def apply(title: str, manifest: str, text: str = "") -> dict:
    return {"title": title, "kind": "apply", "content": manifest, "text": text}


def delete(title: str, manifest: str, text: str = "Remove everything created by this lab.") -> dict:
    return {"title": title, "kind": "delete", "content": manifest, "text": text}


NODESELECTOR_DEPLOY = y("""
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: lab-ssd
    spec:
      replicas: 4
      selector:
        matchLabels: {app: lab-ssd}
      template:
        metadata:
          labels: {app: lab-ssd}
        spec:
          nodeSelector:
            disktype: ssd
          containers:
            - name: app
              image: nginx:1.27-alpine
              resources:
                requests: {cpu: 20m, memory: 16Mi}
""")

AFFINITY_DEPLOY = y("""
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: lab-affinity
    spec:
      replicas: 3
      selector:
        matchLabels: {app: lab-affinity}
      template:
        metadata:
          labels: {app: lab-affinity}
        spec:
          affinity:
            nodeAffinity:
              requiredDuringSchedulingIgnoredDuringExecution:
                nodeSelectorTerms:
                  - matchExpressions:
                      - {key: topology.kubernetes.io/zone, operator: In, values: [zone-a, zone-b]}
              preferredDuringSchedulingIgnoredDuringExecution:
                - weight: 100
                  preference:
                    matchExpressions:
                      - {key: disktype, operator: In, values: [hdd]}
          containers:
            - name: app
              image: nginx:1.27-alpine
              resources:
                requests: {cpu: 20m, memory: 16Mi}
""")

ANTI_AFFINITY_DEPLOY = y("""
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: lab-ha
    spec:
      replicas: 3
      selector:
        matchLabels: {app: lab-ha}
      template:
        metadata:
          labels: {app: lab-ha}
        spec:
          affinity:
            podAntiAffinity:
              requiredDuringSchedulingIgnoredDuringExecution:
                - labelSelector:
                    matchLabels: {app: lab-ha}
                  topologyKey: kubernetes.io/hostname
          containers:
            - name: app
              image: nginx:1.27-alpine
              resources:
                requests: {cpu: 20m, memory: 16Mi}
""")

GPU_DEPLOY = y("""
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: lab-gpu
    spec:
      replicas: 2
      selector:
        matchLabels: {app: lab-gpu}
      template:
        metadata:
          labels: {app: lab-gpu}
        spec:
          nodeSelector:
            gpu: "true"
          tolerations:
            - {key: dedicated, operator: Equal, value: gpu, effect: NoSchedule}
          containers:
            - name: trainer
              image: busybox:1.36
              command: ["sh", "-c", "echo training on $(hostname); sleep 3600"]
              resources:
                requests: {cpu: 20m, memory: 16Mi}
""")

PLAIN_DEPLOY = y("""
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: lab-plain
    spec:
      replicas: 4
      selector:
        matchLabels: {app: lab-plain}
      template:
        metadata:
          labels: {app: lab-plain}
        spec:
          containers:
            - name: app
              image: nginx:1.27-alpine
              resources:
                requests: {cpu: 20m, memory: 16Mi}
""")

HPA_STACK = y("""
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: php-apache
    spec:
      selector:
        matchLabels: {app: php-apache}
      template:
        metadata:
          labels: {app: php-apache}
        spec:
          containers:
            - name: php-apache
              image: registry.k8s.io/hpa-example
              ports:
                - containerPort: 80
              resources:
                requests: {cpu: 200m}
                limits: {cpu: 500m}
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: php-apache
    spec:
      selector: {app: php-apache}
      ports:
        - port: 80
    ---
    apiVersion: autoscaling/v2
    kind: HorizontalPodAutoscaler
    metadata:
      name: php-apache
    spec:
      scaleTargetRef:
        apiVersion: apps/v1
        kind: Deployment
        name: php-apache
      minReplicas: 1
      maxReplicas: 8
      metrics:
        - type: Resource
          resource:
            name: cpu
            target:
              type: Utilization
              averageUtilization: 50
      behavior:
        scaleDown:
          stabilizationWindowSeconds: 60
""")

LOAD_GEN = y("""
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: load-generator
    spec:
      replicas: 2
      selector:
        matchLabels: {app: load-generator}
      template:
        metadata:
          labels: {app: load-generator}
        spec:
          containers:
            - name: load
              image: busybox:1.36
              command: ["sh", "-c", "while true; do wget -q -O- http://php-apache >/dev/null; done"]
""")

CM_V1 = y("""
    apiVersion: v1
    kind: ConfigMap
    metadata:
      name: lab-config
    data:
      LOG_LEVEL: info
""")

CM_V2 = CM_V1.replace("LOG_LEVEL: info", "LOG_LEVEL: debug")

CM_DEPLOY = y("""
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: cm-demo
    spec:
      replicas: 1
      selector:
        matchLabels: {app: cm-demo}
      template:
        metadata:
          labels: {app: cm-demo}
        spec:
          containers:
            - name: app
              image: busybox:1.36
              command: ["sh", "-c", "while true; do echo \\"env=$LOG_LEVEL file=$(cat /etc/config/LOG_LEVEL)\\"; sleep 5; done"]
              env:
                - name: LOG_LEVEL
                  valueFrom:
                    configMapKeyRef: {name: lab-config, key: LOG_LEVEL}
              volumeMounts:
                - {name: config, mountPath: /etc/config}
          volumes:
            - name: config
              configMap: {name: lab-config}
""")

ROLL_V1 = y("""
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: lab-roll
      annotations:
        kubernetes.io/change-cause: "v1 nginx 1.27"
    spec:
      replicas: 4
      strategy:
        rollingUpdate: {maxSurge: 1, maxUnavailable: 0}
      selector:
        matchLabels: {app: lab-roll}
      template:
        metadata:
          labels: {app: lab-roll}
        spec:
          containers:
            - name: web
              image: nginx:1.27-alpine
              readinessProbe:
                httpGet: {path: /, port: 80}
                periodSeconds: 2
              resources:
                requests: {cpu: 20m, memory: 16Mi}
""")
ROLL_V2 = ROLL_V1.replace("nginx:1.27-alpine", "nginx:1.28-alpine").replace("v1 nginx 1.27", "v2 nginx 1.28")
ROLL_BAD = ROLL_V1.replace("nginx:1.27-alpine", "nginx:does-not-exist").replace("v1 nginx 1.27", "v3 broken image")

PROBES = y("""
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: lab-probes
    spec:
      replicas: 2
      selector:
        matchLabels: {app: lab-probes}
      template:
        metadata:
          labels: {app: lab-probes}
        spec:
          containers:
            - name: app
              image: busybox:1.36
              command: ["sh", "-c", "touch /tmp/healthy; sleep 15; touch /tmp/ready; sleep 45; rm /tmp/ready; sleep 30; rm /tmp/healthy; sleep 3600"]
              readinessProbe:
                exec: {command: ["cat", "/tmp/ready"]}
                periodSeconds: 3
              livenessProbe:
                exec: {command: ["cat", "/tmp/healthy"]}
                periodSeconds: 5
                failureThreshold: 2
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: lab-probes
    spec:
      selector: {app: lab-probes}
      ports:
        - port: 80
""")

PDB_STACK = y("""
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: lab-pdb
    spec:
      replicas: 3
      selector:
        matchLabels: {app: lab-pdb}
      template:
        metadata:
          labels: {app: lab-pdb}
        spec:
          containers:
            - name: app
              image: nginx:1.27-alpine
              readinessProbe:
                httpGet: {path: /, port: 80}
              resources:
                requests: {cpu: 20m, memory: 16Mi}
    ---
    apiVersion: policy/v1
    kind: PodDisruptionBudget
    metadata:
      name: lab-pdb
    spec:
      minAvailable: 2
      selector:
        matchLabels: {app: lab-pdb}
""")

VPA_STACK = y("""
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: hamster
    spec:
      replicas: 2
      selector:
        matchLabels: {app: hamster}
      template:
        metadata:
          labels: {app: hamster}
        spec:
          containers:
            - name: hamster
              image: registry.k8s.io/ubuntu-slim:0.14
              command: ["/bin/sh"]
              args: ["-c", "while true; do timeout 0.5s yes >/dev/null; sleep 0.5s; done"]
              resources:
                requests: {cpu: 100m, memory: 50Mi}
    ---
    apiVersion: autoscaling.k8s.io/v1
    kind: VerticalPodAutoscaler
    metadata:
      name: hamster-vpa
    spec:
      targetRef:
        apiVersion: apps/v1
        kind: Deployment
        name: hamster
      updatePolicy:
        updateMode: Recreate
      resourcePolicy:
        containerPolicies:
          - containerName: "*"
            minAllowed: {cpu: 100m, memory: 50Mi}
            maxAllowed: {cpu: "1", memory: 500Mi}
""")


LABS = [
    {
        "id": "lab-nodeselector",
        "topic": "nodeselector",
        "title": "nodeSelector & the hidden taint",
        "level": "basic",
        "goal": "Pin pods to SSD nodes and discover why worker3 (also SSD) receives none.",
        "steps": [
            cmd("Inspect node labels", "kubectl get nodes -L disktype,gpu,topology.kubernetes.io/zone", "worker and worker3 are disktype=ssd."),
            apply("Deploy 4 replicas with nodeSelector disktype=ssd", NODESELECTOR_DEPLOY, "Watch the live map: all pods land on worker."),
            cmd("Where did they go?", "kubectl get pods -l app=lab-ssd -o wide"),
            cmd("Why not worker3?", f"kubectl describe node {W3}", "Look for Taints: dedicated=gpu:NoSchedule."),
            cmd("Make worker2 an SSD node", f"kubectl label node {W2} disktype=ssd --overwrite", "Existing pods don't move (scheduling-time only)..."),
            cmd("...but new pods can use it", "kubectl rollout restart deployment/lab-ssd"),
            cmd("Restore worker2 label", f"kubectl label node {W2} disktype=hdd --overwrite"),
            delete("Cleanup", NODESELECTOR_DEPLOY),
        ],
    },
    {
        "id": "lab-affinity",
        "topic": "node-affinity",
        "title": "Node affinity & pod anti-affinity",
        "level": "intermediate",
        "goal": "See required vs preferred rules, then hit the anti-affinity capacity wall.",
        "steps": [
            apply("Required zones a/b, prefer hdd", AFFINITY_DEPLOY, "Preferred weight 100 for hdd → expect worker2."),
            cmd("Verify placement", "kubectl get pods -l app=lab-affinity -o wide"),
            apply("3 replicas, one per node (hard anti-affinity)", ANTI_AFFINITY_DEPLOY, "Only 2 untainted workers exist → 1 replica stays Pending."),
            cmd("Read the scheduler's verdict", "kubectl get events --field-selector reason=FailedScheduling"),
            delete("Cleanup", AFFINITY_DEPLOY + "---\n" + ANTI_AFFINITY_DEPLOY),
        ],
    },
    {
        "id": "lab-taints",
        "topic": "taints-tolerations",
        "title": "Taints, tolerations & NoExecute eviction",
        "level": "intermediate",
        "goal": "Use the dedicated GPU node, then evict pods from a node with a NoExecute taint.",
        "steps": [
            apply("GPU workload with toleration + nodeSelector", GPU_DEPLOY, "Lands on worker3."),
            apply("Plain deployment (no tolerations)", PLAIN_DEPLOY, "Spreads over worker & worker2 only."),
            cmd("Taint worker2 with NoExecute", f"kubectl taint nodes {W2} maintenance=true:NoExecute", "Watch lab-plain pods on worker2 get evicted and recreated on worker."),
            cmd("Check where pods are now", "kubectl get pods -o wide -l 'app in (lab-plain,lab-gpu)'"),
            cmd("Remove the taint", f"kubectl taint nodes {W2} maintenance-"),
            delete("Cleanup", GPU_DEPLOY + "---\n" + PLAIN_DEPLOY),
        ],
    },
    {
        "id": "lab-hpa",
        "topic": "hpa",
        "title": "HPA under real load",
        "level": "intermediate",
        "goal": "Generate CPU load and watch the HPA scale php-apache up and back down.",
        "steps": [
            cmd("Confirm metrics-server works", "kubectl top nodes", "If this errors, wait a minute after cluster creation."),
            apply("Deploy php-apache + Service + HPA (50% CPU)", HPA_STACK),
            cmd("Baseline", "kubectl get hpa php-apache", "TARGETS may show <unknown> for ~1 min."),
            apply("Start the load generator", LOAD_GEN, "Watch the HPA card in the live map. Replicas climb within ~1-2 min."),
            cmd("Inspect scaling decisions", "kubectl describe hpa php-apache"),
            delete("Stop the load", LOAD_GEN, "Scale-down starts after the 60s stabilization window set in this lab."),
            delete("Cleanup", HPA_STACK),
        ],
    },
    {
        "id": "lab-configmap",
        "topic": "configmaps",
        "title": "ConfigMap: env vs volume updates",
        "level": "basic",
        "goal": "Prove that mounted files update live while env vars need a restart.",
        "steps": [
            apply("Create ConfigMap (LOG_LEVEL=info)", CM_V1),
            apply("Deploy reader (prints env & file every 5s)", CM_DEPLOY),
            cmd("Read logs", "kubectl logs deployment/cm-demo --tail=3"),
            apply("Update ConfigMap to debug", CM_V2, "Wait ~60s for the kubelet to sync the volume."),
            cmd("Logs again: file=debug, env=info", "kubectl logs deployment/cm-demo --tail=3"),
            cmd("Restart to refresh env", "kubectl rollout restart deployment/cm-demo"),
            cmd("Logs: both debug now", "kubectl logs deployment/cm-demo --tail=3"),
            delete("Cleanup", CM_V1 + "---\n" + CM_DEPLOY),
        ],
    },
    {
        "id": "lab-rolling",
        "topic": "deployments",
        "title": "Rolling update, broken release & rollback",
        "level": "basic",
        "goal": "Roll v1 → v2, ship a broken image, observe the safe stall, then roll back.",
        "steps": [
            apply("Deploy v1 (nginx 1.27)", ROLL_V1),
            apply("Roll to v2 (nginx 1.28)", ROLL_V2, "maxSurge 1 / maxUnavailable 0: one new pod at a time."),
            cmd("Watch status", "kubectl rollout status deployment/lab-roll --timeout=60s"),
            apply("Ship a broken image", ROLL_BAD, "New pod hits ImagePullBackOff; old pods keep serving because maxUnavailable=0."),
            cmd("History", "kubectl rollout history deployment/lab-roll"),
            cmd("Roll back", "kubectl rollout undo deployment/lab-roll"),
            delete("Cleanup", ROLL_V1),
        ],
    },
    {
        "id": "lab-probes",
        "topic": "probes",
        "title": "Readiness vs liveness in action",
        "level": "intermediate",
        "goal": "Watch pods become Ready, drop out of endpoints, then get restarted by liveness.",
        "steps": [
            apply("Deploy probe demo", PROBES, "0-15s NotReady → Ready → at ~60s NotReady → at ~90s liveness restarts the container."),
            cmd("Endpoints (only Ready pods)", "kubectl get endpointslices -l kubernetes.io/service-name=lab-probes"),
            cmd("Restarts count", "kubectl get pods -l app=lab-probes"),
            delete("Cleanup", PROBES),
        ],
    },
    {
        "id": "lab-pdb",
        "topic": "pdb",
        "title": "Drain a node safely with a PDB",
        "level": "advanced",
        "goal": "Drain a worker while a PDB keeps at least 2 replicas available.",
        "steps": [
            apply("Deploy 3 replicas + PDB minAvailable 2", PDB_STACK),
            cmd("PDB status", "kubectl get pdb lab-pdb"),
            cmd("Drain worker", f"kubectl drain {W1} --ignore-daemonsets --delete-emptydir-data --timeout=80s", "Evictions respect the budget; pods move to worker2."),
            cmd("Node is cordoned", "kubectl get nodes"),
            cmd("Uncordon", f"kubectl uncordon {W1}"),
            delete("Cleanup", PDB_STACK),
        ],
    },
    {
        "id": "lab-vpa",
        "topic": "vpa",
        "title": "VPA right-sizing (needs VPA add-on)",
        "level": "advanced",
        "goal": "Let VPA observe a CPU-hungry app and recreate pods with bigger requests.",
        "steps": [
            cmd("Is VPA installed?", "kubectl get crd verticalpodautoscalers.autoscaling.k8s.io", "If NotFound: recreate the cluster with the VPA option."),
            apply("Deploy hamster + VPA (Recreate)", VPA_STACK),
            cmd("Recommendation (after ~2-5 min)", "kubectl describe vpa hamster-vpa"),
            cmd("Requests after VPA eviction", "kubectl get pods -l app=hamster -o custom-columns=NAME:.metadata.name,CPU:.spec.containers[0].resources.requests.cpu,MEM:.spec.containers[0].resources.requests.memory"),
            delete("Cleanup", VPA_STACK),
        ],
    },
]
