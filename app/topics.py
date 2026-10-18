"""Learning content: every topic has analogy, use-cases, YAML (basic→advanced), commands and interview Q&A."""

from textwrap import dedent


def y(text: str) -> str:
    return dedent(text).strip() + "\n"


CATEGORIES = [
    {"id": "fundamentals", "title": "Fundamentals", "color": "sky", "blurb": "Pods, Deployments, Services & the label glue."},
    {"id": "config", "title": "Configuration", "color": "lemon", "blurb": "Decouple config & secrets from images."},
    {"id": "scheduling", "title": "Scheduling", "color": "lilac", "blurb": "Decide WHERE pods run."},
    {"id": "scaling", "title": "Autoscaling", "color": "mint", "blurb": "Scale out (HPA) and scale up (VPA)."},
    {"id": "reliability", "title": "Reliability", "color": "peach", "blurb": "Probes, budgets and resource guarantees."},
    {"id": "workloads", "title": "Workload Types", "color": "rose", "blurb": "StatefulSet, DaemonSet, Jobs & init/sidecars."},
    {"id": "storage", "title": "Storage", "color": "sky", "blurb": "Data that outlives pods."},
    {"id": "networking", "title": "Networking", "color": "mint", "blurb": "North-south (Ingress) & east-west (NetworkPolicy)."},
    {"id": "security", "title": "Security", "color": "lilac", "blurb": "Who can do what: RBAC & ServiceAccounts."},
]


TOPICS = [
    # ------------------------------------------------------------------ fundamentals
    {
        "id": "pods",
        "title": "Pods",
        "category": "fundamentals",
        "level": "basic",
        "code": "Po",
        "tagline": "The smallest deployable unit: one or more containers sharing network & storage.",
        "analogy": "A pod is a shared flat. Containers are flatmates: one address (pod IP), a shared kitchen (volumes), and they move in and out together.",
        "what": "A Pod wraps one or more containers that are always co-scheduled on the same node. They share a network namespace (talk over localhost), can share volumes, and have one IP. Pods are ephemeral: if the node dies, a bare pod is gone forever — controllers (Deployment, StatefulSet...) recreate them.",
        "use_cases": [
            "Run a single web container (the 95% case).",
            "App + sidecar: log shipper, service-mesh proxy (Envoy), config reloader.",
            "Debug pod: `kubectl run tmp --image=busybox` to test DNS from inside the cluster.",
        ],
        "key_points": [
            "Lifecycle phases: Pending → Running → Succeeded/Failed (Unknown if node lost).",
            "restartPolicy: Always (default), OnFailure, Never — applies to all containers in the pod.",
            "Each pod gets its own IP from the CNI; containers share it.",
            "You rarely create pods directly — use a controller for self-healing.",
        ],
        "examples": [
            {
                "title": "Minimal pod",
                "level": "basic",
                "description": "One nginx container listening on port 80.",
                "yaml": y("""
                    apiVersion: v1
                    kind: Pod
                    metadata:
                      name: hello
                      labels:
                        app: hello
                    spec:
                      containers:
                        - name: web
                          image: nginx:1.27-alpine
                          ports:
                            - containerPort: 80
                """),
            },
            {
                "title": "Multi-container pod sharing a volume",
                "level": "intermediate",
                "description": "A writer container produces a file that nginx serves — both see the same emptyDir.",
                "yaml": y("""
                    apiVersion: v1
                    kind: Pod
                    metadata:
                      name: shared-volume
                    spec:
                      volumes:
                        - name: html
                          emptyDir: {}
                      containers:
                        - name: web
                          image: nginx:1.27-alpine
                          volumeMounts:
                            - name: html
                              mountPath: /usr/share/nginx/html
                        - name: writer
                          image: busybox:1.36
                          command: ["sh", "-c", "while true; do date > /data/index.html; sleep 5; done"]
                          volumeMounts:
                            - name: html
                              mountPath: /data
                """),
            },
        ],
        "commands": [
            "kubectl run tmp --image=busybox:1.36 --restart=Never -- sleep 3600",
            "kubectl get pods -o wide",
            "kubectl describe pod hello",
            "kubectl logs hello -c web --previous",
            "kubectl get pod hello -o yaml",
        ],
        "gotchas": [
            "A pod deleted or on a dead node is NOT rescheduled unless a controller owns it.",
            "`kubectl logs --previous` shows logs of the crashed container instance — vital for CrashLoopBackOff.",
            "Changing most pod spec fields requires recreation; that's why we template pods in Deployments.",
        ],
        "interview": [
            {"level": "basic", "q": "Why does Kubernetes schedule pods, not containers?", "a": "A pod is the atomic unit for co-scheduling tightly-coupled containers that must share network/IPC/volumes (e.g. app + sidecar). Grouping them guarantees they land on the same node and live/die together."},
            {"level": "basic", "q": "What does CrashLoopBackOff mean and how do you debug it?", "a": "The container keeps exiting and kubelet restarts it with exponential backoff (10s, 20s ... max 5m). Debug with `kubectl logs <pod> --previous`, `kubectl describe pod` (exit code, OOMKilled, probe failures), check command/args, config and missing env/secrets."},
            {"level": "intermediate", "q": "What is the pause container?", "a": "The infra container started first in every pod. It holds the network (and optionally IPC/PID) namespace so app containers can restart without losing the pod IP."},
            {"level": "advanced", "q": "Explain the pod termination sequence.", "a": "Pod marked Terminating → removed from Service endpoints → preStop hook runs → SIGTERM to containers → wait terminationGracePeriodSeconds (default 30s) → SIGKILL. Apps should handle SIGTERM and drain in-flight requests; a short preStop sleep helps avoid traffic hitting a dying pod while endpoints propagate."},
        ],
        "related": ["deployments", "probes", "init-sidecar"],
        "scene": "pods",
    },
    {
        "id": "deployments",
        "title": "Deployments & ReplicaSets",
        "category": "fundamentals",
        "level": "basic",
        "code": "De",
        "tagline": "Declare the desired state; the controller does rolling updates and rollbacks.",
        "analogy": "A Deployment is a restaurant manager: 'I always want 3 chefs.' If one leaves, hire another. When the recipe changes, swap chefs one-by-one so the kitchen never closes.",
        "what": "A Deployment manages ReplicaSets, which keep N identical pods running. Changing the pod template creates a new ReplicaSet and gradually shifts replicas (RollingUpdate) according to maxSurge/maxUnavailable. Old ReplicaSets are kept (revisionHistoryLimit) for rollbacks.",
        "use_cases": [
            "Stateless web/API services.",
            "Zero-downtime releases with rolling updates.",
            "Fast rollback after a bad release (`kubectl rollout undo`).",
        ],
        "key_points": [
            "Deployment → ReplicaSet → Pods (ownerReferences chain).",
            "Strategy: RollingUpdate (default; maxSurge 25%, maxUnavailable 25%) or Recreate.",
            "Selector is immutable and must match template labels.",
            "Only changes to `.spec.template` trigger a new rollout (not replicas).",
        ],
        "examples": [
            {
                "title": "Deployment with rolling update strategy",
                "level": "basic",
                "description": "3 replicas; during updates at most 1 extra pod and 0 unavailable.",
                "yaml": y("""
                    apiVersion: apps/v1
                    kind: Deployment
                    metadata:
                      name: web
                    spec:
                      replicas: 3
                      revisionHistoryLimit: 5
                      selector:
                        matchLabels:
                          app: web
                      strategy:
                        type: RollingUpdate
                        rollingUpdate:
                          maxSurge: 1
                          maxUnavailable: 0
                      template:
                        metadata:
                          labels:
                            app: web
                        spec:
                          containers:
                            - name: web
                              image: nginx:1.27-alpine
                              ports:
                                - containerPort: 80
                              readinessProbe:
                                httpGet:
                                  path: /
                                  port: 80
                """),
            },
            {
                "title": "Canary with two Deployments behind one Service",
                "level": "advanced",
                "description": "Both deployments share app=shop so the Service splits traffic ≈ by replica count (9:1).",
                "yaml": y("""
                    apiVersion: apps/v1
                    kind: Deployment
                    metadata:
                      name: shop-stable
                    spec:
                      replicas: 9
                      selector:
                        matchLabels: {app: shop, track: stable}
                      template:
                        metadata:
                          labels: {app: shop, track: stable}
                        spec:
                          containers:
                            - name: shop
                              image: nginx:1.27-alpine
                    ---
                    apiVersion: apps/v1
                    kind: Deployment
                    metadata:
                      name: shop-canary
                    spec:
                      replicas: 1
                      selector:
                        matchLabels: {app: shop, track: canary}
                      template:
                        metadata:
                          labels: {app: shop, track: canary}
                        spec:
                          containers:
                            - name: shop
                              image: nginx:1.28-alpine
                    ---
                    apiVersion: v1
                    kind: Service
                    metadata:
                      name: shop
                    spec:
                      selector:
                        app: shop
                      ports:
                        - port: 80
                """),
            },
        ],
        "commands": [
            "kubectl create deployment web --image=nginx:1.27-alpine --replicas=3",
            "kubectl set image deployment/web web=nginx:1.28-alpine",
            "kubectl rollout status deployment/web",
            "kubectl rollout history deployment/web",
            "kubectl rollout undo deployment/web --to-revision=1",
            "kubectl rollout restart deployment/web",
            "kubectl scale deployment web --replicas=5",
        ],
        "gotchas": [
            "Without a readinessProbe, a rolling update may send traffic to pods that aren't ready yet.",
            "`maxSurge: 0` + `maxUnavailable: 0` is invalid — the rollout could never progress.",
            "If an HPA manages replicas, remove `replicas:` from the manifest or every apply fights the HPA.",
        ],
        "interview": [
            {"level": "basic", "q": "Difference between ReplicaSet and Deployment?", "a": "A ReplicaSet only keeps N pods alive. A Deployment manages ReplicaSets over time, adding versioned rollouts, rollback, pause/resume and update strategies."},
            {"level": "intermediate", "q": "How do maxSurge and maxUnavailable affect a rollout?", "a": "maxSurge = how many pods above desired may exist during update (speed/extra capacity). maxUnavailable = how many below desired may be unavailable (availability). maxSurge=1,maxUnavailable=0 is the safest zero-downtime config."},
            {"level": "intermediate", "q": "How does `kubectl rollout undo` work?", "a": "It re-applies the pod template of a previous ReplicaSet revision (kept per revisionHistoryLimit), creating a new revision number and rolling back to it."},
            {"level": "advanced", "q": "How would you do blue/green or canary in plain Kubernetes?", "a": "Blue/green: two Deployments (blue, green) and switch the Service selector. Canary: two Deployments sharing a label the Service selects, ratio by replicas. For precise % or header-based routing use Ingress annotations, Gateway API weights, a service mesh, or Argo Rollouts/Flagger."},
        ],
        "related": ["pods", "services", "probes", "hpa"],
        "scene": "deployments",
    },
    {
        "id": "services",
        "title": "Services",
        "category": "fundamentals",
        "level": "basic",
        "code": "Sv",
        "tagline": "A stable virtual IP + DNS name in front of a changing set of pods.",
        "analogy": "A Service is a company's reception phone number. Employees (pods) come and go, but callers always dial the same number and get routed to someone available.",
        "what": "A Service selects pods by labels and load-balances to their Ready endpoints (tracked in EndpointSlices). kube-proxy (iptables/IPVS/nftables) or an eBPF CNI programs the routing. DNS: <svc>.<ns>.svc.cluster.local.",
        "use_cases": [
            "ClusterIP: internal microservice-to-microservice calls.",
            "NodePort: quick external access on every node's port 30000–32767.",
            "LoadBalancer: cloud LB in front of NodePorts (EKS/GKE/AKS).",
            "Headless (clusterIP: None): direct pod DNS records for StatefulSets/databases.",
        ],
        "key_points": [
            "Only Ready pods receive traffic (readiness probes matter!).",
            "port = service port, targetPort = container port, nodePort = node port.",
            "ExternalName maps a Service to an external DNS CNAME.",
            "sessionAffinity: ClientIP for sticky sessions.",
        ],
        "examples": [
            {
                "title": "ClusterIP service",
                "level": "basic",
                "description": "Routes port 80 to pods labelled app=web on containerPort 80.",
                "yaml": y("""
                    apiVersion: v1
                    kind: Service
                    metadata:
                      name: web
                    spec:
                      type: ClusterIP
                      selector:
                        app: web
                      ports:
                        - name: http
                          port: 80
                          targetPort: 80
                """),
            },
            {
                "title": "NodePort + headless service",
                "level": "intermediate",
                "description": "NodePort exposes 30080 on every node; the headless service gives each pod a DNS record.",
                "yaml": y("""
                    apiVersion: v1
                    kind: Service
                    metadata:
                      name: web-nodeport
                    spec:
                      type: NodePort
                      selector:
                        app: web
                      ports:
                        - port: 80
                          targetPort: 80
                          nodePort: 30080
                    ---
                    apiVersion: v1
                    kind: Service
                    metadata:
                      name: web-headless
                    spec:
                      clusterIP: None
                      selector:
                        app: web
                      ports:
                        - port: 80
                """),
            },
        ],
        "commands": [
            "kubectl expose deployment web --port=80 --target-port=80",
            "kubectl get svc,endpointslices -o wide",
            "kubectl describe svc web",
            "kubectl run curl --image=curlimages/curl --restart=Never -- curl -s web",
        ],
        "gotchas": [
            "Service has no endpoints? Selector labels don't match pod labels, or pods aren't Ready.",
            "externalTrafficPolicy: Local preserves client IP but only routes to nodes with local pods.",
            "A Service IP isn't pingable — it's a virtual IP implemented by NAT rules.",
        ],
        "interview": [
            {"level": "basic", "q": "Explain ClusterIP vs NodePort vs LoadBalancer.", "a": "ClusterIP: internal VIP only. NodePort: ClusterIP + a port on every node. LoadBalancer: NodePort + an external cloud load balancer. Each builds on the previous one."},
            {"level": "intermediate", "q": "How does a Service know which pods to send traffic to?", "a": "The EndpointSlice controller watches pods matching the selector and records Ready pod IPs. kube-proxy watches EndpointSlices and programs iptables/IPVS rules on every node."},
            {"level": "intermediate", "q": "What is a headless service and when do you use it?", "a": "clusterIP: None — no VIP; DNS returns pod IPs directly (and per-pod records for StatefulSets like db-0.db). Used for stateful apps needing stable identities or client-side load balancing."},
            {"level": "advanced", "q": "Your service returns connection refused intermittently. How do you debug?", "a": "Check endpoints (`kubectl get endpointslices`), readiness probes, targetPort vs containerPort, pod restarts, NetworkPolicies, and whether terminating pods still get traffic (add preStop sleep, ensure graceful shutdown). Test from a debug pod with curl and DNS lookups."},
        ],
        "related": ["labels", "ingress", "network-policy", "probes"],
        "scene": "services",
    },
    {
        "id": "labels",
        "title": "Labels, Selectors & Annotations",
        "category": "fundamentals",
        "level": "basic",
        "code": "Lb",
        "tagline": "Key/value tags that glue Kubernetes objects together.",
        "analogy": "Labels are hashtags on photos. #prod #frontend — a selector is a search: 'show me everything tagged #prod AND #frontend'.",
        "what": "Labels are identifying key/value pairs used by selectors (Services, Deployments, nodeSelector, NetworkPolicy...). Annotations are non-identifying metadata (build info, tool config) and can't be selected on.",
        "use_cases": [
            "Service → pods routing, Deployment → pods ownership.",
            "Environment/tier filtering: `kubectl get pods -l env=prod,tier!=db`.",
            "Node labels for scheduling (disktype=ssd, zone).",
            "Annotations for ingress controller config, Prometheus scraping, change-cause.",
        ],
        "key_points": [
            "Equality selectors: =, ==, != ; set-based: in, notin, exists.",
            "Recommended labels: app.kubernetes.io/name, /instance, /version, /component, /part-of.",
            "Label values ≤ 63 chars; annotations can be large.",
        ],
        "examples": [
            {
                "title": "Recommended labels + annotations",
                "level": "basic",
                "description": "Common labels make tooling (Helm, dashboards) and selectors consistent.",
                "yaml": y("""
                    apiVersion: v1
                    kind: Pod
                    metadata:
                      name: checkout
                      labels:
                        app.kubernetes.io/name: checkout
                        app.kubernetes.io/part-of: shop
                        env: prod
                        tier: backend
                      annotations:
                        kubernetes.io/change-cause: "release 2.3.1 - faster cart"
                        prometheus.io/scrape: "true"
                    spec:
                      containers:
                        - name: app
                          image: nginx:1.27-alpine
                """),
            },
            {
                "title": "Set-based selector in a Deployment",
                "level": "intermediate",
                "description": "matchExpressions allow In/NotIn/Exists/DoesNotExist.",
                "yaml": y("""
                    apiVersion: apps/v1
                    kind: Deployment
                    metadata:
                      name: api
                    spec:
                      replicas: 2
                      selector:
                        matchLabels:
                          app: api
                        matchExpressions:
                          - {key: env, operator: In, values: [prod, staging]}
                      template:
                        metadata:
                          labels: {app: api, env: prod}
                        spec:
                          containers:
                            - name: api
                              image: nginx:1.27-alpine
                """),
            },
        ],
        "commands": [
            "kubectl get pods --show-labels",
            "kubectl get pods -l 'env in (prod,staging),tier!=db'",
            "kubectl label pod checkout version=v2 --overwrite",
            "kubectl label pod checkout version-",
            "kubectl annotate deployment api kubernetes.io/change-cause='bump image'",
        ],
        "gotchas": [
            "Removing a label from a pod 'orphans' it: the ReplicaSet creates a replacement (handy for debugging!).",
            "Two Deployments with overlapping selectors fight over pods.",
        ],
        "interview": [
            {"level": "basic", "q": "Labels vs annotations?", "a": "Labels identify and are selectable (used for grouping/routing). Annotations hold arbitrary non-identifying metadata for tools/humans and cannot be used in selectors."},
            {"level": "intermediate", "q": "How can you debug a misbehaving pod without it being killed by its ReplicaSet?", "a": "Remove/change the selector label (`kubectl label pod x app-`). The ReplicaSet no longer owns it, starts a replacement, and the Service stops routing to it — you can inspect the isolated pod freely."},
        ],
        "related": ["services", "nodeselector", "deployments"],
        "scene": "labels",
    },
    {
        "id": "namespaces",
        "title": "Namespaces, Quotas & LimitRanges",
        "category": "fundamentals",
        "level": "intermediate",
        "code": "Ns",
        "tagline": "Virtual clusters inside a cluster, with budgets and defaults.",
        "analogy": "Namespaces are floors in an office building: each team gets a floor, a budget (ResourceQuota) and house rules (LimitRange) — but the building (nodes) is shared.",
        "what": "Namespaces scope names, RBAC, quotas and policies. ResourceQuota caps aggregate usage (CPU, memory, object counts) per namespace. LimitRange sets default/min/max requests & limits per container.",
        "use_cases": [
            "Multi-team clusters: team-a, team-b with separate quotas.",
            "Environment split: dev / staging (prod often a separate cluster).",
            "Inject sane defaults so pods without resources still get requests.",
        ],
        "key_points": [
            "Nodes, PVs, StorageClasses, ClusterRoles are cluster-scoped (not namespaced).",
            "With a CPU/memory quota, every pod MUST specify requests/limits (or get them from a LimitRange).",
            "Cross-namespace DNS: svc.other-ns.svc.cluster.local.",
        ],
        "examples": [
            {
                "title": "Namespace + ResourceQuota + LimitRange",
                "level": "intermediate",
                "description": "Team namespace capped at 4 CPU / 8Gi with per-container defaults.",
                "yaml": y("""
                    apiVersion: v1
                    kind: Namespace
                    metadata:
                      name: team-a
                    ---
                    apiVersion: v1
                    kind: ResourceQuota
                    metadata:
                      name: team-a-quota
                      namespace: team-a
                    spec:
                      hard:
                        requests.cpu: "4"
                        requests.memory: 8Gi
                        limits.cpu: "8"
                        limits.memory: 16Gi
                        pods: "20"
                    ---
                    apiVersion: v1
                    kind: LimitRange
                    metadata:
                      name: defaults
                      namespace: team-a
                    spec:
                      limits:
                        - type: Container
                          defaultRequest: {cpu: 100m, memory: 128Mi}
                          default: {cpu: 500m, memory: 256Mi}
                          max: {cpu: "2", memory: 2Gi}
                """),
            },
        ],
        "commands": [
            "kubectl create namespace team-a",
            "kubectl get resourcequota -n team-a",
            "kubectl describe quota team-a-quota -n team-a",
            "kubectl get pods -A",
        ],
        "gotchas": [
            "Deleting a namespace deletes EVERYTHING in it.",
            "Namespaces are not a network boundary — add NetworkPolicies for isolation.",
        ],
        "interview": [
            {"level": "basic", "q": "Which resources are not namespaced?", "a": "Nodes, PersistentVolumes, StorageClasses, Namespaces, ClusterRoles/ClusterRoleBindings, CRDs, IngressClasses, PriorityClasses. `kubectl api-resources --namespaced=false` lists them."},
            {"level": "intermediate", "q": "ResourceQuota vs LimitRange?", "a": "ResourceQuota limits the namespace total (sum of all pods/objects). LimitRange applies per container/pod: defaults, min and max. They're often used together."},
        ],
        "related": ["resources-qos", "rbac", "network-policy"],
        "scene": "namespaces",
    },
    # ------------------------------------------------------------------ config
    {
        "id": "configmaps",
        "title": "ConfigMaps",
        "category": "config",
        "level": "basic",
        "code": "Cm",
        "tagline": "Externalize non-secret configuration from your container image.",
        "analogy": "A ConfigMap is the settings sheet taped next to a machine. Same machine (image) everywhere; each site (environment) tapes its own sheet.",
        "what": "ConfigMaps hold key/value pairs or whole files (≤1 MiB). Pods consume them as env vars (envFrom / valueFrom), command args, or mounted files. Mounted files auto-update (kubelet sync ≈ up to a minute); env vars do NOT — they need a pod restart.",
        "use_cases": [
            "12-factor apps: LOG_LEVEL, FEATURE_FLAGS, API endpoints per environment.",
            "Ship nginx.conf / application.yaml as a mounted file.",
            "Hot-reloadable config with a sidecar/reloader watching the mounted file.",
        ],
        "key_points": [
            "env/envFrom = snapshot at container start.",
            "Volume mount = live updates (except when using subPath!).",
            "immutable: true protects from accidental change and reduces API load.",
            "Rollout on change: hash the config into a pod annotation (Helm/Kustomize configMapGenerator).",
        ],
        "examples": [
            {
                "title": "ConfigMap as env + file",
                "level": "basic",
                "description": "LOG_LEVEL as env var and app.properties mounted at /etc/config.",
                "yaml": y("""
                    apiVersion: v1
                    kind: ConfigMap
                    metadata:
                      name: app-config
                    data:
                      LOG_LEVEL: info
                      FEATURE_CHECKOUT_V2: "true"
                      app.properties: |
                        cache.ttl=300
                        payments.url=http://payments.default.svc
                    ---
                    apiVersion: v1
                    kind: Pod
                    metadata:
                      name: config-demo
                    spec:
                      containers:
                        - name: app
                          image: busybox:1.36
                          command: ["sh", "-c", "while true; do echo LOG_LEVEL=$LOG_LEVEL; cat /etc/config/app.properties; sleep 10; done"]
                          env:
                            - name: LOG_LEVEL
                              valueFrom:
                                configMapKeyRef:
                                  name: app-config
                                  key: LOG_LEVEL
                          volumeMounts:
                            - name: config
                              mountPath: /etc/config
                      volumes:
                        - name: config
                          configMap:
                            name: app-config
                            items:
                              - key: app.properties
                                path: app.properties
                """),
            },
            {
                "title": "Auto-rollout on config change (checksum pattern)",
                "level": "advanced",
                "description": "Changing the annotation value (hash of config) changes the template → new rollout. Helm: `{{ include (print $.Template.BasePath \"/cm.yaml\") . | sha256sum }}`.",
                "yaml": y("""
                    apiVersion: apps/v1
                    kind: Deployment
                    metadata:
                      name: api
                    spec:
                      replicas: 2
                      selector:
                        matchLabels: {app: api}
                      template:
                        metadata:
                          labels: {app: api}
                          annotations:
                            checksum/config: "replace-with-sha256-of-configmap"
                        spec:
                          containers:
                            - name: api
                              image: nginx:1.27-alpine
                              envFrom:
                                - configMapRef:
                                    name: app-config
                """),
            },
        ],
        "commands": [
            "kubectl create configmap app-config --from-literal=LOG_LEVEL=info --from-file=app.properties",
            "kubectl get configmap app-config -o yaml",
            "kubectl rollout restart deployment/api",
        ],
        "gotchas": [
            "subPath mounts never receive ConfigMap updates.",
            "Pod fails with CreateContainerConfigError if a referenced ConfigMap/key is missing (unless optional: true).",
            "Never put passwords in ConfigMaps — use Secrets (and ideally an external secret store).",
        ],
        "interview": [
            {"level": "basic", "q": "How can a pod consume a ConfigMap?", "a": "As individual env vars (valueFrom.configMapKeyRef), all keys as env (envFrom), command-line args via $(VAR), or as files in a volume."},
            {"level": "intermediate", "q": "You updated a ConfigMap but the app still sees old values. Why?", "a": "Env vars are injected only at container start → restart pods. For volume mounts, kubelet sync takes up to ~1 min, subPath mounts never update, and the app itself must re-read the file."},
            {"level": "advanced", "q": "How do you trigger a rolling restart automatically when config changes?", "a": "Put a hash of the ConfigMap in a pod-template annotation (Helm sha256sum), use Kustomize configMapGenerator (name suffix hash), or run a controller like Stakater Reloader."},
        ],
        "related": ["secrets", "deployments"],
        "scene": "configmaps",
    },
    {
        "id": "secrets",
        "title": "Secrets",
        "category": "config",
        "level": "basic",
        "code": "Se",
        "tagline": "Sensitive data (passwords, tokens, certs) delivered to pods — base64 ≠ encryption.",
        "analogy": "A Secret is a sealed envelope handed to the right employee. But the envelope is only sealed with tape (base64): you still need a locked safe (etcd encryption + RBAC).",
        "what": "Secrets are like ConfigMaps for sensitive values. Data is base64-encoded (not encrypted!). Protect them with encryption-at-rest (EncryptionConfiguration/KMS), tight RBAC, and preferably source them from Vault / cloud secret managers via External Secrets Operator or CSI Secrets Store.",
        "use_cases": [
            "DB credentials injected as env vars or files.",
            "imagePullSecrets for private registries.",
            "TLS certs for Ingress (type kubernetes.io/tls), typically issued by cert-manager.",
        ],
        "key_points": [
            "Types: Opaque, kubernetes.io/tls, kubernetes.io/dockerconfigjson, service-account-token.",
            "stringData lets you write plain text; the API stores it base64-encoded.",
            "Mounted secrets are stored in tmpfs (RAM) on the node.",
            "Never commit real secret values to Git — use Sealed Secrets / SOPS / External Secrets.",
        ],
        "examples": [
            {
                "title": "Secret consumed as env (placeholder values)",
                "level": "basic",
                "description": "Create the real secret from the CLI so values never land in Git: `kubectl create secret generic db-creds --from-literal=DB_USER=app --from-literal=DB_PASSWORD=\"$DB_PASSWORD\"`.",
                "yaml": y("""
                    apiVersion: v1
                    kind: Secret
                    metadata:
                      name: db-creds
                    type: Opaque
                    stringData:
                      DB_USER: app
                      DB_PASSWORD: "<set-at-deploy-time>"
                    ---
                    apiVersion: v1
                    kind: Pod
                    metadata:
                      name: secret-demo
                    spec:
                      containers:
                        - name: app
                          image: busybox:1.36
                          command: ["sh", "-c", "echo user=$DB_USER; sleep 3600"]
                          envFrom:
                            - secretRef:
                                name: db-creds
                """),
            },
            {
                "title": "External Secrets Operator (production pattern)",
                "level": "advanced",
                "description": "The operator syncs from Vault/AWS Secrets Manager into a k8s Secret. Requires ESO installed.",
                "yaml": y("""
                    apiVersion: external-secrets.io/v1
                    kind: ExternalSecret
                    metadata:
                      name: db-creds
                    spec:
                      refreshInterval: 1h
                      secretStoreRef:
                        name: vault-backend
                        kind: ClusterSecretStore
                      target:
                        name: db-creds
                      data:
                        - secretKey: DB_PASSWORD
                          remoteRef:
                            key: prod/payments/db
                            property: password
                """),
            },
        ],
        "commands": [
            "kubectl create secret generic db-creds --from-literal=DB_USER=app --from-literal=DB_PASSWORD=\"$DB_PASSWORD\"",
            "kubectl get secret db-creds -o jsonpath='{.data.DB_USER}'",
            "kubectl auth can-i get secrets --as=system:serviceaccount:default:default",
        ],
        "gotchas": [
            "Anyone who can create pods in a namespace can read its secrets (mount them).",
            "`kubectl get secret -o yaml` + base64 -d reveals values — restrict `get/list` on secrets.",
            "Env vars can leak through crash dumps/logs; file mounts are generally safer.",
        ],
        "interview": [
            {"level": "basic", "q": "Are Kubernetes Secrets encrypted?", "a": "Not by default — they're base64-encoded in etcd. Enable encryption at rest (ideally with a KMS provider), restrict RBAC, and use external secret managers for production."},
            {"level": "intermediate", "q": "How do you keep secrets out of Git in a GitOps setup?", "a": "Sealed Secrets (encrypted with controller public key), SOPS with KMS/age, or External Secrets Operator referencing Vault/cloud secret managers — Git holds only references or ciphertext."},
            {"level": "advanced", "q": "How do pods authenticate to cloud secret managers without static keys?", "a": "Workload identity: IRSA/EKS Pod Identity (AWS), GKE Workload Identity, Azure Workload Identity — a projected ServiceAccount token is exchanged for short-lived cloud credentials."},
        ],
        "related": ["configmaps", "rbac"],
        "scene": "secrets",
    },
    # ------------------------------------------------------------------ scheduling
    {
        "id": "nodeselector",
        "title": "nodeSelector",
        "category": "scheduling",
        "level": "basic",
        "code": "NS",
        "tagline": "The simplest way to pin pods to nodes with matching labels.",
        "analogy": "nodeSelector is a 'Window seat only' ticket. The usher (scheduler) only considers seats labelled window; if none is free, you wait in the queue (Pending).",
        "what": "spec.nodeSelector is a map of labels a node MUST have (AND logic, exact match). It's a hard filter in the scheduler's filter phase. For OR/NotIn/soft preferences use node affinity.",
        "use_cases": [
            "Run databases only on SSD nodes (disktype=ssd).",
            "Run ML workloads on GPU node pools (combined with tolerations).",
            "Keep workloads in a specific node pool/arch: kubernetes.io/arch=arm64.",
        ],
        "key_points": [
            "Exact key=value matches only; all entries must match.",
            "No match → Pod stays Pending with FailedScheduling event.",
            "Label nodes with `kubectl label node <n> disktype=ssd`.",
            "Doesn't bypass taints: a matching tainted node still needs a toleration.",
        ],
        "examples": [
            {
                "title": "Schedule on SSD nodes",
                "level": "basic",
                "description": "On the playground cluster only k8s-playground-worker matches (worker3 is ssd but tainted).",
                "yaml": y("""
                    apiVersion: apps/v1
                    kind: Deployment
                    metadata:
                      name: ssd-app
                    spec:
                      replicas: 3
                      selector:
                        matchLabels: {app: ssd-app}
                      template:
                        metadata:
                          labels: {app: ssd-app}
                        spec:
                          nodeSelector:
                            disktype: ssd
                          containers:
                            - name: app
                              image: nginx:1.27-alpine
                              resources:
                                requests: {cpu: 50m, memory: 32Mi}
                """),
            },
            {
                "title": "Well-known labels: architecture & OS",
                "level": "intermediate",
                "description": "Built-in labels set by kubelet are perfect selectors.",
                "yaml": y("""
                    apiVersion: v1
                    kind: Pod
                    metadata:
                      name: arm-only
                    spec:
                      nodeSelector:
                        kubernetes.io/os: linux
                        kubernetes.io/arch: arm64
                      containers:
                        - name: app
                          image: nginx:1.27-alpine
                """),
            },
        ],
        "commands": [
            "kubectl get nodes --show-labels",
            "kubectl get nodes -L disktype,topology.kubernetes.io/zone",
            "kubectl label node k8s-playground-worker2 disktype=ssd --overwrite",
            "kubectl get pods -o wide -l app=ssd-app",
            "kubectl describe pod -l app=ssd-app",
        ],
        "gotchas": [
            "Changing node labels later doesn't evict running pods (scheduling-time only).",
            "Typos in labels silently cause Pending pods — check events.",
        ],
        "interview": [
            {"level": "basic", "q": "What happens if no node matches the nodeSelector?", "a": "The pod stays Pending. Events show `0/N nodes are available: N node(s) didn't match Pod's node affinity/selector`. If cluster-autoscaler is installed it may add a node from a matching node group."},
            {"level": "intermediate", "q": "nodeSelector vs node affinity?", "a": "nodeSelector: simple AND of exact matches, hard only. Node affinity: richer operators (In, NotIn, Exists, DoesNotExist, Gt, Lt), OR across terms, and soft preferences with weights."},
            {"level": "intermediate", "q": "A pod has nodeSelector gpu=true and the GPU node exists, but the pod is Pending. Why?", "a": "Most likely the GPU node is tainted (e.g. nvidia.com/gpu:NoSchedule) and the pod lacks a toleration; or insufficient resources (requests nvidia.com/gpu), or the node is cordoned."},
        ],
        "related": ["node-affinity", "taints-tolerations", "labels"],
        "scene": "nodeselector",
        "simulate": "nodeselector",
    },
    {
        "id": "node-affinity",
        "title": "Node Affinity",
        "category": "scheduling",
        "level": "intermediate",
        "code": "NA",
        "tagline": "Expressive hard and soft rules for which nodes a pod can/should run on.",
        "analogy": "Booking a hotel: 'MUST be in Mumbai or Pune' (required) and 'I'd PREFER sea-view, weight 80' (preferred). Any hotel failing the must is out; the rest are ranked by preferences.",
        "what": "requiredDuringSchedulingIgnoredDuringExecution is a filter: nodeSelectorTerms are ORed, matchExpressions inside a term are ANDed. preferredDuringSchedulingIgnoredDuringExecution adds weights (1-100) to the score of matching nodes. 'IgnoredDuringExecution' means running pods are not evicted if node labels change.",
        "use_cases": [
            "Keep latency-sensitive services in specific zones.",
            "Prefer spot/cheap nodes but allow on-demand fallback.",
            "Avoid nodes with a label (NotIn / DoesNotExist), e.g. nodes marked for maintenance.",
        ],
        "key_points": [
            "Terms OR, expressions AND.",
            "Operators: In, NotIn, Exists, DoesNotExist, Gt, Lt.",
            "Preferred weights are summed and normalized into the score.",
            "If both nodeSelector and affinity are set, BOTH must be satisfied.",
        ],
        "examples": [
            {
                "title": "Required zones + preferred disk type",
                "level": "intermediate",
                "description": "Must be in zone-a or zone-b; prefer hdd → lands on k8s-playground-worker2.",
                "yaml": y("""
                    apiVersion: apps/v1
                    kind: Deployment
                    metadata:
                      name: affinity-demo
                    spec:
                      replicas: 3
                      selector:
                        matchLabels: {app: affinity-demo}
                      template:
                        metadata:
                          labels: {app: affinity-demo}
                        spec:
                          affinity:
                            nodeAffinity:
                              requiredDuringSchedulingIgnoredDuringExecution:
                                nodeSelectorTerms:
                                  - matchExpressions:
                                      - key: topology.kubernetes.io/zone
                                        operator: In
                                        values: [zone-a, zone-b]
                              preferredDuringSchedulingIgnoredDuringExecution:
                                - weight: 80
                                  preference:
                                    matchExpressions:
                                      - {key: disktype, operator: In, values: [hdd]}
                          containers:
                            - name: app
                              image: nginx:1.27-alpine
                              resources:
                                requests: {cpu: 50m, memory: 32Mi}
                """),
            },
            {
                "title": "Prefer spot, fall back to on-demand",
                "level": "advanced",
                "description": "Common cost-optimization pattern on EKS/GKE node pools (label names vary by provider).",
                "yaml": y("""
                    apiVersion: v1
                    kind: Pod
                    metadata:
                      name: batch-worker
                    spec:
                      affinity:
                        nodeAffinity:
                          requiredDuringSchedulingIgnoredDuringExecution:
                            nodeSelectorTerms:
                              - matchExpressions:
                                  - {key: node.kubernetes.io/maintenance, operator: DoesNotExist}
                          preferredDuringSchedulingIgnoredDuringExecution:
                            - weight: 100
                              preference:
                                matchExpressions:
                                  - {key: capacity-type, operator: In, values: [spot]}
                            - weight: 10
                              preference:
                                matchExpressions:
                                  - {key: capacity-type, operator: In, values: [on-demand]}
                      containers:
                        - name: worker
                          image: busybox:1.36
                          command: ["sleep", "3600"]
                """),
            },
        ],
        "commands": [
            "kubectl get nodes -L topology.kubernetes.io/zone,disktype",
            "kubectl get pods -l app=affinity-demo -o wide",
            "kubectl explain pod.spec.affinity.nodeAffinity",
        ],
        "gotchas": [
            "An empty nodeSelectorTerms list or a term with no expressions matches nothing.",
            "Preferred rules are only a score — resource balancing can still win.",
            "Label changes don't move running pods (IgnoredDuringExecution); use descheduler for that.",
        ],
        "interview": [
            {"level": "intermediate", "q": "What does IgnoredDuringExecution mean?", "a": "Rules are evaluated only at scheduling time. If node labels later change so the pod no longer matches, the running pod is not evicted. (RequiredDuringExecution was proposed but isn't implemented.)"},
            {"level": "intermediate", "q": "How are multiple nodeSelectorTerms and matchExpressions combined?", "a": "Terms are ORed; matchExpressions within one term are ANDed. So [term1(A AND B), term2(C)] means (A and B) or C."},
            {"level": "advanced", "q": "How do you dedicate nodes to a team so ONLY their pods run there and their pods ONLY run there?", "a": "Combine a taint on the nodes (keeps others off) with a toleration + required node affinity on the team's pods (keeps them on). Taints repel, affinity attracts — you need both."},
        ],
        "related": ["nodeselector", "taints-tolerations", "pod-affinity"],
        "scene": "node-affinity",
        "simulate": "node-affinity",
    },
    {
        "id": "pod-affinity",
        "title": "Pod Affinity & Anti-Affinity",
        "category": "scheduling",
        "level": "advanced",
        "code": "PA",
        "tagline": "Schedule relative to OTHER pods: together (affinity) or apart (anti-affinity).",
        "analogy": "Seating at a wedding: put the web team next to the cache (affinity — less latency), but never seat two replicas of the same family at one table (anti-affinity — if the table collapses, not everyone falls).",
        "what": "Rules use a labelSelector over existing pods and a topologyKey that defines the 'same place' (hostname = same node, zone = same zone). Required = filter, preferred = weighted score. Anti-affinity on hostname is the classic HA pattern.",
        "use_cases": [
            "Spread replicas one-per-node/zone for high availability.",
            "Co-locate web with its cache to cut network hops.",
            "Keep noisy neighbours apart (batch vs latency-sensitive).",
        ],
        "key_points": [
            "topologyKey is mandatory: kubernetes.io/hostname, topology.kubernetes.io/zone...",
            "Required anti-affinity + more replicas than domains → Pending pods.",
            "Inter-pod affinity is expensive in large clusters; prefer topologySpreadConstraints for spreading.",
            "First-pod rule: required affinity to itself is allowed for the very first replica.",
        ],
        "examples": [
            {
                "title": "One replica per node (hard anti-affinity)",
                "level": "intermediate",
                "description": "4 replicas but only 2 schedulable workers in the playground → 2 Pending (control-plane and worker3 are tainted).",
                "yaml": y("""
                    apiVersion: apps/v1
                    kind: Deployment
                    metadata:
                      name: ha-web
                    spec:
                      replicas: 4
                      selector:
                        matchLabels: {app: ha-web}
                      template:
                        metadata:
                          labels: {app: ha-web}
                        spec:
                          affinity:
                            podAntiAffinity:
                              requiredDuringSchedulingIgnoredDuringExecution:
                                - labelSelector:
                                    matchLabels: {app: ha-web}
                                  topologyKey: kubernetes.io/hostname
                          containers:
                            - name: web
                              image: nginx:1.27-alpine
                              resources:
                                requests: {cpu: 50m, memory: 32Mi}
                """),
            },
            {
                "title": "Co-locate with cache, softly spread across zones",
                "level": "advanced",
                "description": "Hard affinity to cache on the same node + soft anti-affinity across zones.",
                "yaml": y("""
                    apiVersion: apps/v1
                    kind: Deployment
                    metadata:
                      name: redis-cache
                    spec:
                      replicas: 1
                      selector:
                        matchLabels: {app: cache}
                      template:
                        metadata:
                          labels: {app: cache}
                        spec:
                          containers:
                            - name: redis
                              image: redis:7-alpine
                    ---
                    apiVersion: apps/v1
                    kind: Deployment
                    metadata:
                      name: web-near-cache
                    spec:
                      replicas: 2
                      selector:
                        matchLabels: {app: web-near-cache}
                      template:
                        metadata:
                          labels: {app: web-near-cache}
                        spec:
                          affinity:
                            podAffinity:
                              requiredDuringSchedulingIgnoredDuringExecution:
                                - labelSelector:
                                    matchLabels: {app: cache}
                                  topologyKey: kubernetes.io/hostname
                            podAntiAffinity:
                              preferredDuringSchedulingIgnoredDuringExecution:
                                - weight: 50
                                  podAffinityTerm:
                                    labelSelector:
                                      matchLabels: {app: web-near-cache}
                                    topologyKey: topology.kubernetes.io/zone
                          containers:
                            - name: web
                              image: nginx:1.27-alpine
                """),
            },
        ],
        "commands": [
            "kubectl get pods -l app=ha-web -o wide",
            "kubectl describe pod -l app=ha-web | grep -A3 Events",
        ],
        "gotchas": [
            "Required anti-affinity blocks rolling updates with maxSurge if there's no spare node!",
            "Pod affinity matches pods in the same namespace by default (use namespaces/namespaceSelector to widen).",
        ],
        "interview": [
            {"level": "intermediate", "q": "What is topologyKey?", "a": "A node label key defining a topology domain. Pods on nodes sharing the same value of that label are in the same domain (hostname → node, zone → availability zone)."},
            {"level": "advanced", "q": "Your Deployment with hard pod anti-affinity is stuck mid-rollout. Why?", "a": "With N replicas on N nodes, the surge pod can't be placed anywhere (each node already has a replica). Fix: maxSurge 0 + maxUnavailable 1, use preferred anti-affinity, or add nodes."},
            {"level": "advanced", "q": "Pod anti-affinity vs topologySpreadConstraints?", "a": "Anti-affinity is binary (0 or 1 per domain for required). Spread constraints allow controlled skew (maxSkew), handle more replicas than domains gracefully, and scale better. Prefer spread constraints for HA spreading."},
        ],
        "related": ["topology-spread", "node-affinity", "pdb"],
        "scene": "pod-affinity",
        "simulate": "anti-affinity",
    },
    {
        "id": "taints-tolerations",
        "title": "Taints & Tolerations",
        "category": "scheduling",
        "level": "intermediate",
        "code": "TT",
        "tagline": "Nodes repel pods unless the pod explicitly tolerates the taint.",
        "analogy": "A taint is a 'Staff only' sign on a door. Visitors bounce off; staff with the badge (toleration) may enter — but the badge doesn't force them to go in.",
        "what": "Taints (key=value:Effect) on nodes repel pods. Effects: NoSchedule (hard for new pods), PreferNoSchedule (soft), NoExecute (also evicts running pods lacking the toleration, optionally after tolerationSeconds). Kubernetes itself uses taints: node.kubernetes.io/not-ready, unreachable, disk-pressure, unschedulable, and control-plane nodes.",
        "use_cases": [
            "Dedicated GPU/high-memory node pools.",
            "Keep workloads off control-plane nodes.",
            "Node maintenance: NoExecute evicts pods.",
            "Taint-based eviction when a node becomes unreachable (default 300s toleration).",
        ],
        "key_points": [
            "Toleration operators: Equal (key+value) or Exists (any value; empty key = tolerate everything).",
            "Toleration does NOT attract — pair with nodeSelector/affinity for dedication.",
            "DaemonSets get automatic tolerations for some node-condition taints.",
        ],
        "examples": [
            {
                "title": "Pod for the dedicated GPU node",
                "level": "intermediate",
                "description": "The playground taints worker3 with dedicated=gpu:NoSchedule. Toleration + nodeSelector = lands on worker3.",
                "yaml": y("""
                    apiVersion: apps/v1
                    kind: Deployment
                    metadata:
                      name: gpu-job
                    spec:
                      replicas: 2
                      selector:
                        matchLabels: {app: gpu-job}
                      template:
                        metadata:
                          labels: {app: gpu-job}
                        spec:
                          nodeSelector:
                            gpu: "true"
                          tolerations:
                            - key: dedicated
                              operator: Equal
                              value: gpu
                              effect: NoSchedule
                          containers:
                            - name: trainer
                              image: busybox:1.36
                              command: ["sh", "-c", "echo training...; sleep 3600"]
                              resources:
                                requests: {cpu: 50m, memory: 32Mi}
                """),
            },
            {
                "title": "Survive node outage longer (tolerationSeconds)",
                "level": "advanced",
                "description": "Default is 300s for not-ready/unreachable. Stateful apps may want longer, latency-critical apps shorter.",
                "yaml": y("""
                    apiVersion: v1
                    kind: Pod
                    metadata:
                      name: patient-pod
                    spec:
                      tolerations:
                        - key: node.kubernetes.io/unreachable
                          operator: Exists
                          effect: NoExecute
                          tolerationSeconds: 900
                        - key: node.kubernetes.io/not-ready
                          operator: Exists
                          effect: NoExecute
                          tolerationSeconds: 900
                      containers:
                        - name: app
                          image: nginx:1.27-alpine
                """),
            },
        ],
        "commands": [
            "kubectl describe node k8s-playground-worker3 | grep -i taint",
            "kubectl taint nodes k8s-playground-worker2 maintenance=true:NoExecute",
            "kubectl taint nodes k8s-playground-worker2 maintenance-",
            "kubectl get nodes -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints",
        ],
        "gotchas": [
            "operator: Exists with no key tolerates ALL taints — powerful and dangerous.",
            "NoExecute evicts immediately unless tolerationSeconds is set.",
        ],
        "interview": [
            {"level": "basic", "q": "Taints vs node affinity?", "a": "Taints are on nodes and repel pods (node's choice). Affinity is on pods and attracts them to nodes (pod's choice). Dedicated nodes need both."},
            {"level": "intermediate", "q": "Explain the three taint effects.", "a": "NoSchedule: new pods without toleration are not scheduled. PreferNoSchedule: scheduler tries to avoid. NoExecute: not scheduled AND running pods without toleration are evicted (after tolerationSeconds if set)."},
            {"level": "advanced", "q": "How does Kubernetes evict pods from a failed node?", "a": "The node lifecycle controller adds node.kubernetes.io/unreachable or not-ready NoExecute taints. Pods get default tolerations of 300s (DefaultTolerationSeconds admission plugin), after which they're evicted and controllers recreate them elsewhere."},
        ],
        "related": ["node-affinity", "nodeselector", "daemonsets", "pdb"],
        "scene": "taints-tolerations",
        "simulate": "taints",
    },
    {
        "id": "topology-spread",
        "title": "Topology Spread Constraints",
        "category": "scheduling",
        "level": "advanced",
        "code": "TS",
        "tagline": "Spread replicas evenly across zones/nodes with a controllable skew.",
        "analogy": "Distributing eggs across baskets: 'no basket may have more than 1 egg more than the emptiest basket' (maxSkew: 1).",
        "what": "topologySpreadConstraints compute, per domain (topologyKey value), how many matching pods exist. Skew = count(domain) − min(count). whenUnsatisfiable: DoNotSchedule (filter) or ScheduleAnyway (score). Newer fields: minDomains, nodeAffinityPolicy, nodeTaintsPolicy, matchLabelKeys (e.g. pod-template-hash to spread per revision).",
        "use_cases": [
            "Zone-level HA: survive an AZ outage with ≥ 2/3 capacity.",
            "Even spread across nodes to reduce blast radius.",
            "Cluster-wide defaults via scheduler configuration.",
        ],
        "key_points": [
            "Multiple constraints are ANDed (e.g. zone + hostname).",
            "Nodes missing the topologyKey label are ignored for counting and can't host the pod (DoNotSchedule).",
            "nodeTaintsPolicy defaults to Ignore → tainted nodes still count as domains (common gotcha).",
        ],
        "examples": [
            {
                "title": "Spread across zones and nodes",
                "level": "advanced",
                "description": "Hard zone spread + soft node spread. Try it in the simulator and toggle nodeTaintsPolicy.",
                "yaml": y("""
                    apiVersion: apps/v1
                    kind: Deployment
                    metadata:
                      name: spread-demo
                    spec:
                      replicas: 4
                      selector:
                        matchLabels: {app: spread-demo}
                      template:
                        metadata:
                          labels: {app: spread-demo}
                        spec:
                          topologySpreadConstraints:
                            - maxSkew: 1
                              topologyKey: topology.kubernetes.io/zone
                              whenUnsatisfiable: DoNotSchedule
                              nodeTaintsPolicy: Honor
                              labelSelector:
                                matchLabels: {app: spread-demo}
                            - maxSkew: 1
                              topologyKey: kubernetes.io/hostname
                              whenUnsatisfiable: ScheduleAnyway
                              labelSelector:
                                matchLabels: {app: spread-demo}
                          containers:
                            - name: app
                              image: nginx:1.27-alpine
                              resources:
                                requests: {cpu: 50m, memory: 32Mi}
                """),
            },
        ],
        "commands": [
            "kubectl get pods -l app=spread-demo -o wide",
            "kubectl get nodes -L topology.kubernetes.io/zone",
        ],
        "gotchas": [
            "Scale-down doesn't rebalance; skew can grow after scale-in (descheduler helps).",
            "Rolling updates count old + new pods unless matchLabelKeys: [pod-template-hash] is used.",
        ],
        "interview": [
            {"level": "advanced", "q": "How is skew calculated?", "a": "For each eligible domain, count pods matching labelSelector. Skew for placing on domain D = (count(D) + 1) − min over all domains. With DoNotSchedule, nodes where skew > maxSkew are filtered."},
            {"level": "advanced", "q": "Why might pods be Pending with zone spread even though there's capacity?", "a": "A domain counts as eligible but can't take pods (tainted nodes with nodeTaintsPolicy Ignore, or nodes full) so min stays 0 and skew grows. Use nodeTaintsPolicy: Honor, minDomains appropriately, or ScheduleAnyway."},
        ],
        "related": ["pod-affinity", "node-affinity"],
        "scene": "topology-spread",
        "simulate": "spread",
    },
    # ------------------------------------------------------------------ scaling
    {
        "id": "hpa",
        "title": "Horizontal Pod Autoscaler",
        "category": "scaling",
        "level": "intermediate",
        "code": "HP",
        "tagline": "Add or remove replicas based on CPU, memory or custom metrics.",
        "analogy": "Supermarket checkouts: when queues grow, open more counters (scale out); when quiet for a while, close some (scale in) — but not instantly, to avoid flapping.",
        "what": "The HPA controller (every 15s) reads metrics (metrics-server for CPU/memory, custom/external metrics APIs for others) and computes desiredReplicas = ceil(currentReplicas × currentMetric / targetMetric), within min/max and behavior policies. Utilization is relative to the pod's REQUESTS, so requests are mandatory.",
        "use_cases": [
            "Web/API services with variable traffic.",
            "Queue workers scaling on queue length (external metric / KEDA).",
            "Scale on RPS via Prometheus Adapter.",
        ],
        "key_points": [
            "Needs metrics-server (installed by the playground setup).",
            "Target averageUtilization is % of requests.",
            "Default scale-down stabilization window: 300s; scale-up: 0s.",
            "10% tolerance: no scaling if ratio is within 0.9–1.1.",
            "Don't combine with VPA on the same CPU/memory metric.",
        ],
        "examples": [
            {
                "title": "CPU-based HPA with behavior",
                "level": "intermediate",
                "description": "Scale web 2→10 at 60% CPU of requests; scale down cautiously.",
                "yaml": y("""
                    apiVersion: autoscaling/v2
                    kind: HorizontalPodAutoscaler
                    metadata:
                      name: web-hpa
                    spec:
                      scaleTargetRef:
                        apiVersion: apps/v1
                        kind: Deployment
                        name: web
                      minReplicas: 2
                      maxReplicas: 10
                      metrics:
                        - type: Resource
                          resource:
                            name: cpu
                            target:
                              type: Utilization
                              averageUtilization: 60
                      behavior:
                        scaleUp:
                          policies:
                            - type: Pods
                              value: 4
                              periodSeconds: 15
                        scaleDown:
                          stabilizationWindowSeconds: 300
                          policies:
                            - type: Percent
                              value: 50
                              periodSeconds: 60
                """),
            },
            {
                "title": "Custom metric: requests per second",
                "level": "advanced",
                "description": "Requires Prometheus Adapter exposing http_requests_per_second via custom.metrics.k8s.io.",
                "yaml": y("""
                    apiVersion: autoscaling/v2
                    kind: HorizontalPodAutoscaler
                    metadata:
                      name: api-rps
                    spec:
                      scaleTargetRef:
                        apiVersion: apps/v1
                        kind: Deployment
                        name: api
                      minReplicas: 3
                      maxReplicas: 50
                      metrics:
                        - type: Pods
                          pods:
                            metric:
                              name: http_requests_per_second
                            target:
                              type: AverageValue
                              averageValue: "100"
                        - type: Resource
                          resource:
                            name: memory
                            target:
                              type: Utilization
                              averageUtilization: 75
                """),
            },
        ],
        "commands": [
            "kubectl autoscale deployment web --cpu-percent=60 --min=2 --max=10",
            "kubectl get hpa",
            "kubectl describe hpa web-hpa",
            "kubectl top pods",
        ],
        "gotchas": [
            "TARGETS shows <unknown>: metrics-server missing or pods have no CPU requests.",
            "With multiple metrics the HPA picks the HIGHEST desired replica count.",
            "Keep `replicas:` out of the Deployment manifest in GitOps when HPA owns it.",
        ],
        "interview": [
            {"level": "intermediate", "q": "What's the HPA formula?", "a": "desiredReplicas = ceil(currentReplicas × currentMetricValue / desiredMetricValue). E.g. 4 pods at 90% vs target 60% → ceil(4×1.5) = 6."},
            {"level": "intermediate", "q": "Why does my HPA show <unknown> targets?", "a": "metrics-server isn't installed/healthy, the pods lack resource requests for that metric, or pods aren't ready yet. Check `kubectl describe hpa` conditions and `kubectl top pods`."},
            {"level": "advanced", "q": "How do you avoid flapping?", "a": "Use behavior.scaleDown.stabilizationWindowSeconds (default 300s), rate-limit policies (Pods/Percent per period), sensible targets, and readiness/startup probes so new pods' CPU spikes at startup don't skew metrics."},
            {"level": "advanced", "q": "HPA vs KEDA vs Cluster Autoscaler?", "a": "HPA scales pods on metrics. KEDA extends HPA with event sources (Kafka lag, SQS, cron) and scale-to-zero. Cluster Autoscaler/Karpenter add nodes when pods are Pending due to capacity. They complement each other."},
        ],
        "related": ["vpa", "resources-qos", "deployments"],
        "scene": "hpa",
        "widget": "hpa-calc",
    },
    {
        "id": "vpa",
        "title": "Vertical Pod Autoscaler",
        "category": "scaling",
        "level": "advanced",
        "code": "VP",
        "tagline": "Right-size CPU/memory requests from observed usage.",
        "analogy": "A tailor who watches how you grow and adjusts your clothes. Classic tailoring needs you to take the clothes off (pod restart); newer in-place resize can adjust while you wear them.",
        "what": "VPA (add-on, autoscaling.k8s.io) has three parts: Recommender (computes target/lower/upper bounds from usage history), Updater (evicts pods that are far off), Admission Controller (rewrites requests on pod creation). updateMode: Off (recommend only), Initial (set at creation), Recreate (evict & recreate), InPlaceOrRecreate (newer VPA releases, uses in-place pod resize when available).",
        "use_cases": [
            "Right-sizing: start with `Off` to collect recommendations, then bake them into manifests.",
            "Stateful/singleton workloads that can't scale horizontally.",
            "Reducing waste from over-provisioned requests (cost).",
        ],
        "key_points": [
            "Don't use VPA and HPA on the same CPU/memory metric (they fight).",
            "Keeps limit/request ratio by default (controlledValues: RequestsAndLimits).",
            "Use minAllowed/maxAllowed to bound recommendations.",
            "Pair with a PDB because Recreate mode evicts pods.",
        ],
        "examples": [
            {
                "title": "Recommendation-only VPA",
                "level": "intermediate",
                "description": "Safest first step: read `kubectl describe vpa` and apply numbers yourself.",
                "yaml": y("""
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
                        updateMode: "Off"
                """),
            },
            {
                "title": "Auto mode with bounds",
                "level": "advanced",
                "description": "Recreate pods with bounded recommendations, only controlling requests.",
                "yaml": y("""
                    apiVersion: autoscaling.k8s.io/v1
                    kind: VerticalPodAutoscaler
                    metadata:
                      name: api-vpa
                    spec:
                      targetRef:
                        apiVersion: apps/v1
                        kind: Deployment
                        name: api
                      updatePolicy:
                        updateMode: Recreate
                        minReplicas: 2
                      resourcePolicy:
                        containerPolicies:
                          - containerName: "*"
                            controlledResources: ["cpu", "memory"]
                            controlledValues: RequestsOnly
                            minAllowed: {cpu: 50m, memory: 64Mi}
                            maxAllowed: {cpu: "2", memory: 2Gi}
                """),
            },
        ],
        "commands": [
            "kubectl get vpa",
            "kubectl describe vpa hamster-vpa",
            "kubectl get pods -l app=hamster -o custom-columns=NAME:.metadata.name,CPU:.spec.containers[0].resources.requests.cpu,MEM:.spec.containers[0].resources.requests.memory",
        ],
        "gotchas": [
            "VPA is NOT built-in: install it (playground: Create cluster with the VPA option).",
            "Recommendations need some minutes of metrics history.",
            "Single-replica deployments are not evicted by default (minReplicas 2).",
        ],
        "interview": [
            {"level": "intermediate", "q": "HPA vs VPA?", "a": "HPA changes replica count (scale out) — good for stateless traffic-driven apps. VPA changes per-pod requests/limits (scale up) — good for right-sizing and non-horizontally-scalable apps."},
            {"level": "advanced", "q": "Can you use HPA and VPA together?", "a": "Not on the same resource metric. Common pattern: VPA in Off/Initial mode for right-sizing memory + HPA on CPU or custom metrics like RPS."},
            {"level": "advanced", "q": "What are VPA's components?", "a": "Recommender (usage history → target/lowerBound/upperBound), Updater (evicts pods whose requests are outside bounds), Admission controller (mutating webhook that injects recommended requests into new pods)."},
        ],
        "related": ["hpa", "resources-qos", "pdb"],
        "scene": "vpa",
    },
    # ------------------------------------------------------------------ reliability
    {
        "id": "resources-qos",
        "title": "Requests, Limits & QoS",
        "category": "reliability",
        "level": "intermediate",
        "code": "Rq",
        "tagline": "Requests reserve, limits cap. Together they decide QoS and eviction order.",
        "analogy": "Requests = a reserved table at a restaurant (guaranteed). Limits = the maximum you're allowed to order. Overeat memory and you're thrown out (OOMKilled); over-order CPU and you're simply served slower (throttled).",
        "what": "The scheduler places pods by REQUESTS. At runtime, CPU over limit is throttled (CFS quota); memory over limit gets the container OOMKilled. QoS classes: Guaranteed (requests = limits for every container, cpu & memory), Burstable (some requests/limits), BestEffort (none). Under node pressure kubelet evicts BestEffort first, then Burstable exceeding requests.",
        "use_cases": [
            "Capacity planning and bin-packing.",
            "Protect critical pods (Guaranteed QoS).",
            "Required for HPA utilization and ResourceQuotas.",
        ],
        "key_points": [
            "CPU is compressible (throttle); memory is not (kill).",
            "Many teams set memory limit = request and omit CPU limits to avoid throttling.",
            "Ephemeral storage can be requested/limited too.",
            "kubectl top shows actual usage (metrics-server).",
        ],
        "examples": [
            {
                "title": "Three QoS classes side by side",
                "level": "intermediate",
                "description": "Check `kubectl get pod <name> -o jsonpath='{.status.qosClass}'` for each.",
                "yaml": y("""
                    apiVersion: v1
                    kind: Pod
                    metadata:
                      name: qos-guaranteed
                    spec:
                      containers:
                        - name: app
                          image: nginx:1.27-alpine
                          resources:
                            requests: {cpu: 100m, memory: 64Mi}
                            limits: {cpu: 100m, memory: 64Mi}
                    ---
                    apiVersion: v1
                    kind: Pod
                    metadata:
                      name: qos-burstable
                    spec:
                      containers:
                        - name: app
                          image: nginx:1.27-alpine
                          resources:
                            requests: {cpu: 50m, memory: 32Mi}
                            limits: {memory: 128Mi}
                    ---
                    apiVersion: v1
                    kind: Pod
                    metadata:
                      name: qos-besteffort
                    spec:
                      containers:
                        - name: app
                          image: nginx:1.27-alpine
                """),
            },
            {
                "title": "Trigger an OOMKill",
                "level": "advanced",
                "description": "Allocates ~150Mi with a 64Mi limit → OOMKilled, then CrashLoopBackOff.",
                "yaml": y("""
                    apiVersion: v1
                    kind: Pod
                    metadata:
                      name: oom-demo
                    spec:
                      containers:
                        - name: hog
                          image: busybox:1.36
                          command: ["sh", "-c", "dd if=/dev/zero of=/dev/shm/fill bs=1M count=150; sleep 3600"]
                          resources:
                            requests: {memory: 32Mi}
                            limits: {memory: 64Mi}
                """),
            },
        ],
        "commands": [
            "kubectl top nodes",
            "kubectl top pods",
            "kubectl describe node k8s-playground-worker | grep -A8 'Allocated resources'",
            "kubectl get pod qos-burstable -o jsonpath='{.status.qosClass}'",
        ],
        "gotchas": [
            "A pod requesting more than any node's allocatable stays Pending forever.",
            "JVM/Node apps must be configured to respect container memory limits.",
        ],
        "interview": [
            {"level": "basic", "q": "Requests vs limits?", "a": "Requests: what the scheduler reserves and guarantees. Limits: the hard cap enforced at runtime by the kernel (cgroups)."},
            {"level": "intermediate", "q": "What happens when a container exceeds CPU vs memory limits?", "a": "CPU: throttled (slower, not killed). Memory: OOMKilled by the kernel (exit code 137), restarted per restartPolicy."},
            {"level": "intermediate", "q": "Explain QoS classes and eviction order.", "a": "Guaranteed (req=lim for all), Burstable (partial), BestEffort (none). Under node memory pressure kubelet evicts BestEffort first, then Burstable pods using more than requests, Guaranteed last."},
            {"level": "advanced", "q": "Should you set CPU limits?", "a": "Debated. CPU limits cause CFS throttling even when the node is idle, hurting latency. Many orgs set CPU requests only (+ memory limit=request); others keep limits for multi-tenant fairness. Know the trade-off."},
        ],
        "related": ["hpa", "vpa", "namespaces"],
        "scene": "resources-qos",
        "widget": "qos-calc",
    },
    {
        "id": "probes",
        "title": "Liveness, Readiness & Startup Probes",
        "category": "reliability",
        "level": "intermediate",
        "code": "Pr",
        "tagline": "Tell Kubernetes when to restart a container and when to send it traffic.",
        "analogy": "Readiness = 'Is the shop open?' (closed shops get no customers). Liveness = 'Is the shopkeeper conscious?' (if not, call an ambulance — restart). Startup = 'Give the new shopkeeper time to set up before checking.'",
        "what": "Probes run httpGet, tcpSocket, exec or grpc checks. Readiness failure removes the pod from Service endpoints (no restart). Liveness failure restarts the container. Startup probe disables the other two until it succeeds — ideal for slow-starting apps.",
        "use_cases": [
            "Don't route traffic until caches are warm (readiness).",
            "Recover from deadlocks (liveness).",
            "Legacy Java app needing 2 min to boot (startup).",
        ],
        "key_points": [
            "Fields: initialDelaySeconds, periodSeconds, timeoutSeconds, failureThreshold, successThreshold.",
            "Liveness should check the process itself, NOT downstream dependencies.",
            "Readiness can check dependencies if you want to shed load.",
        ],
        "examples": [
            {
                "title": "All three probes",
                "level": "intermediate",
                "description": "Startup allows 30×5s = 150s to boot, then liveness/readiness take over.",
                "yaml": y("""
                    apiVersion: apps/v1
                    kind: Deployment
                    metadata:
                      name: probed-web
                    spec:
                      replicas: 2
                      selector:
                        matchLabels: {app: probed-web}
                      template:
                        metadata:
                          labels: {app: probed-web}
                        spec:
                          containers:
                            - name: web
                              image: nginx:1.27-alpine
                              ports:
                                - containerPort: 80
                              startupProbe:
                                httpGet: {path: /, port: 80}
                                failureThreshold: 30
                                periodSeconds: 5
                              readinessProbe:
                                httpGet: {path: /, port: 80}
                                periodSeconds: 5
                                failureThreshold: 2
                              livenessProbe:
                                tcpSocket: {port: 80}
                                periodSeconds: 10
                                failureThreshold: 3
                """),
            },
            {
                "title": "Watch readiness flip (exec probe)",
                "level": "advanced",
                "description": "Ready after 20s, unready after 80s → leaves endpoints but is NOT restarted.",
                "yaml": y("""
                    apiVersion: v1
                    kind: Pod
                    metadata:
                      name: readiness-flip
                      labels: {app: readiness-flip}
                    spec:
                      containers:
                        - name: app
                          image: busybox:1.36
                          command: ["sh", "-c", "sleep 20; touch /tmp/ready; sleep 60; rm /tmp/ready; sleep 3600"]
                          readinessProbe:
                            exec:
                              command: ["cat", "/tmp/ready"]
                            periodSeconds: 5
                """),
            },
        ],
        "commands": [
            "kubectl get pods -w",
            "kubectl describe pod readiness-flip | grep -A5 Readiness",
            "kubectl get endpointslices -l kubernetes.io/service-name=web",
        ],
        "gotchas": [
            "Liveness probe hitting a DB → DB outage restarts ALL pods (cascading failure).",
            "Too aggressive liveness on a slow start = CrashLoopBackOff; use a startup probe.",
        ],
        "interview": [
            {"level": "basic", "q": "Difference between liveness and readiness probes?", "a": "Liveness failure → container restart. Readiness failure → pod removed from Service endpoints but keeps running. A pod can be alive but not ready."},
            {"level": "intermediate", "q": "Why use a startup probe instead of a long initialDelaySeconds?", "a": "Startup probe checks repeatedly and hands over as soon as the app is up (fast when fast, patient when slow). A fixed delay is either too long (slow detection) or too short (restart loops)."},
            {"level": "advanced", "q": "Should liveness probes check dependencies?", "a": "No. A dependency outage would restart every pod, making things worse. Liveness should only detect a broken process (deadlock). Use readiness or circuit breakers for dependency health."},
        ],
        "related": ["services", "deployments", "pods"],
        "scene": "probes",
    },
    {
        "id": "pdb",
        "title": "PodDisruptionBudgets & Drain",
        "category": "reliability",
        "level": "advanced",
        "code": "PD",
        "tagline": "Limit how many pods voluntary disruptions (drain, upgrades) can take down at once.",
        "analogy": "A hospital rota: 'at least 2 nurses on duty at all times'. Nurses can take leave (eviction) only if the minimum stays covered.",
        "what": "A PDB (minAvailable or maxUnavailable) protects against VOLUNTARY disruptions using the Eviction API: kubectl drain, cluster upgrades, autoscaler scale-down. It doesn't protect against node crashes (involuntary). Evictions that would violate the budget are rejected (HTTP 429) and drain retries.",
        "use_cases": [
            "Safe node upgrades in managed clusters (EKS/GKE/AKS).",
            "Quorum-based systems (etcd, Kafka, Zookeeper): keep a majority.",
            "Cluster autoscaler respects PDBs when removing nodes.",
        ],
        "key_points": [
            "kubectl cordon = mark unschedulable; drain = cordon + evict pods.",
            "minAvailable: 100% or maxUnavailable: 0 can block drains forever.",
            "unhealthyPodEvictionPolicy: AlwaysAllow lets you evict crashlooping pods.",
        ],
        "examples": [
            {
                "title": "Deployment + PDB",
                "level": "intermediate",
                "description": "Drain a node and watch evictions wait for replacements to be Ready.",
                "yaml": y("""
                    apiVersion: apps/v1
                    kind: Deployment
                    metadata:
                      name: critical-api
                    spec:
                      replicas: 3
                      selector:
                        matchLabels: {app: critical-api}
                      template:
                        metadata:
                          labels: {app: critical-api}
                        spec:
                          containers:
                            - name: api
                              image: nginx:1.27-alpine
                              resources:
                                requests: {cpu: 50m, memory: 32Mi}
                    ---
                    apiVersion: policy/v1
                    kind: PodDisruptionBudget
                    metadata:
                      name: critical-api-pdb
                    spec:
                      minAvailable: 2
                      unhealthyPodEvictionPolicy: AlwaysAllow
                      selector:
                        matchLabels: {app: critical-api}
                """),
            },
        ],
        "commands": [
            "kubectl get pdb",
            "kubectl cordon k8s-playground-worker",
            "kubectl drain k8s-playground-worker --ignore-daemonsets --delete-emptydir-data --timeout=60s",
            "kubectl uncordon k8s-playground-worker",
        ],
        "gotchas": [
            "Single-replica deployment + minAvailable: 1 = node can never be drained.",
            "Deleting pods directly (kubectl delete pod) bypasses PDBs — only the Eviction API respects them.",
        ],
        "interview": [
            {"level": "intermediate", "q": "Voluntary vs involuntary disruptions?", "a": "Voluntary: initiated by admins/automation (drain, upgrade, autoscaler) — PDBs apply. Involuntary: hardware failure, kernel panic, node OOM — PDBs can't prevent them."},
            {"level": "advanced", "q": "A node drain hangs forever. What do you check?", "a": "PDBs whose budget is 0 (`kubectl get pdb` → ALLOWED DISRUPTIONS 0), single-replica apps, pods that can't reschedule (affinity/taints/capacity), pods with local storage needing --delete-emptydir-data, and bare pods needing --force."},
        ],
        "related": ["taints-tolerations", "pod-affinity", "vpa"],
        "scene": "pdb",
    },
    # ------------------------------------------------------------------ workloads
    {
        "id": "statefulsets",
        "title": "StatefulSets",
        "category": "workloads",
        "level": "intermediate",
        "code": "SS",
        "tagline": "Stable names, stable storage and ordered rollout for stateful apps.",
        "analogy": "Numbered lockers at a gym: member #0 always gets locker #0 with their stuff still inside, even after leaving and coming back.",
        "what": "StatefulSet pods get ordinal names (db-0, db-1...), stable DNS via a headless Service (db-0.db.ns.svc), and a PVC per pod from volumeClaimTemplates that survives pod rescheduling. Pods are created/terminated in order by default (OrderedReady) or in parallel (podManagementPolicy: Parallel).",
        "use_cases": [
            "Databases (PostgreSQL, MySQL), Kafka, Zookeeper, Elasticsearch, etcd.",
            "Anything needing stable network identity or per-replica storage.",
        ],
        "key_points": [
            "Requires a headless Service (serviceName).",
            "PVCs are NOT deleted on scale-down by default (persistentVolumeClaimRetentionPolicy).",
            "updateStrategy RollingUpdate with partition enables staged/canary rollouts.",
            "Operators (CloudNativePG, Strimzi) handle failover logic StatefulSets don't.",
        ],
        "examples": [
            {
                "title": "StatefulSet with per-pod storage",
                "level": "intermediate",
                "description": "Uses kind's default 'standard' StorageClass (local-path provisioner).",
                "yaml": y("""
                    apiVersion: v1
                    kind: Service
                    metadata:
                      name: web
                    spec:
                      clusterIP: None
                      selector:
                        app: web-sts
                      ports:
                        - port: 80
                    ---
                    apiVersion: apps/v1
                    kind: StatefulSet
                    metadata:
                      name: web-sts
                    spec:
                      serviceName: web
                      replicas: 3
                      selector:
                        matchLabels: {app: web-sts}
                      template:
                        metadata:
                          labels: {app: web-sts}
                        spec:
                          containers:
                            - name: web
                              image: nginx:1.27-alpine
                              volumeMounts:
                                - name: data
                                  mountPath: /usr/share/nginx/html
                      volumeClaimTemplates:
                        - metadata:
                            name: data
                          spec:
                            accessModes: ["ReadWriteOnce"]
                            storageClassName: standard
                            resources:
                              requests:
                                storage: 100Mi
                """),
            },
        ],
        "commands": [
            "kubectl get sts,pods,pvc -l app=web-sts",
            "kubectl delete pod web-sts-1   # comes back with the same name & PVC",
            "kubectl scale sts web-sts --replicas=1",
            "kubectl run dns --image=busybox:1.36 --restart=Never -- nslookup web-sts-0.web",
        ],
        "gotchas": [
            "A StatefulSet does not make your app replicate data — the app must.",
            "Stuck rollout if a pod never becomes Ready under OrderedReady.",
        ],
        "interview": [
            {"level": "basic", "q": "Deployment vs StatefulSet?", "a": "Deployment pods are interchangeable (random names, shared or no storage). StatefulSet pods have stable ordinal identity, stable DNS, per-pod persistent volumes and ordered operations."},
            {"level": "intermediate", "q": "What happens to PVCs when you scale a StatefulSet down?", "a": "By default they're retained, so scaling back up reattaches the same data. persistentVolumeClaimRetentionPolicy (whenScaled/whenDeleted: Delete) can change that."},
            {"level": "advanced", "q": "How do you do a canary rollout of a StatefulSet?", "a": "updateStrategy.rollingUpdate.partition: N — only pods with ordinal ≥ N are updated. Lower the partition step by step."},
        ],
        "related": ["storage", "services"],
        "scene": "statefulsets",
    },
    {
        "id": "daemonsets",
        "title": "DaemonSets",
        "category": "workloads",
        "level": "basic",
        "code": "DS",
        "tagline": "Exactly one pod per (matching) node — for node-level agents.",
        "analogy": "A security guard for every building floor: add a new floor and a guard is automatically assigned to it.",
        "what": "DaemonSets ensure a pod runs on all (or selected) nodes. When nodes join, pods are added; when nodes leave, pods are garbage-collected. Uses nodeSelector/affinity to target subsets and tolerations to run on tainted nodes (e.g. control-plane).",
        "use_cases": [
            "Log collectors (Fluent Bit), node metrics (node-exporter).",
            "CNI plugins (Calico, Cilium), kube-proxy, CSI node drivers.",
            "Security agents (Falco).",
        ],
        "key_points": [
            "Scheduled by the default scheduler (via node affinity per node).",
            "updateStrategy: RollingUpdate (maxUnavailable) or OnDelete.",
            "Add control-plane toleration to also run there.",
        ],
        "examples": [
            {
                "title": "Log agent on every node incl. control-plane",
                "level": "basic",
                "description": "Tolerates the control-plane taint and worker3's GPU taint.",
                "yaml": y("""
                    apiVersion: apps/v1
                    kind: DaemonSet
                    metadata:
                      name: log-agent
                    spec:
                      selector:
                        matchLabels: {app: log-agent}
                      template:
                        metadata:
                          labels: {app: log-agent}
                        spec:
                          tolerations:
                            - key: node-role.kubernetes.io/control-plane
                              operator: Exists
                              effect: NoSchedule
                            - key: dedicated
                              operator: Exists
                              effect: NoSchedule
                          containers:
                            - name: agent
                              image: busybox:1.36
                              command: ["sh", "-c", "while true; do echo shipping logs from $NODE_NAME; sleep 30; done"]
                              env:
                                - name: NODE_NAME
                                  valueFrom:
                                    fieldRef:
                                      fieldPath: spec.nodeName
                              resources:
                                requests: {cpu: 10m, memory: 16Mi}
                """),
            },
        ],
        "commands": [
            "kubectl get ds -A",
            "kubectl get pods -l app=log-agent -o wide",
            "kubectl rollout status ds/log-agent",
        ],
        "gotchas": [
            "DaemonSet pods ignore cordon (unschedulable) — they tolerate it by default.",
            "Resource requests on DaemonSets reduce allocatable on EVERY node.",
        ],
        "interview": [
            {"level": "basic", "q": "When would you use a DaemonSet?", "a": "For per-node agents: logging, monitoring, networking (CNI), storage drivers, security scanners."},
            {"level": "intermediate", "q": "How do you run a DaemonSet only on some nodes?", "a": "Add nodeSelector or node affinity to the pod template; add tolerations to include tainted nodes."},
        ],
        "related": ["taints-tolerations", "nodeselector"],
        "scene": "daemonsets",
    },
    {
        "id": "jobs",
        "title": "Jobs & CronJobs",
        "category": "workloads",
        "level": "basic",
        "code": "Jb",
        "tagline": "Run-to-completion work, once or on a schedule.",
        "analogy": "A Job is a to-do list item that's done when ticked. A CronJob is a recurring calendar reminder that creates a new to-do item every time.",
        "what": "A Job runs pods until `completions` succeed, with `parallelism` at a time and retries up to backoffLimit. CronJob creates Jobs on a cron schedule with concurrencyPolicy (Allow/Forbid/Replace), history limits and optional timeZone.",
        "use_cases": [
            "DB migrations, batch processing, report generation.",
            "Nightly backups, cleanup tasks (CronJob).",
            "Indexed Jobs for parallel sharded work (completionMode: Indexed).",
        ],
        "key_points": [
            "restartPolicy must be OnFailure or Never.",
            "activeDeadlineSeconds caps total runtime; ttlSecondsAfterFinished auto-cleans.",
            "podFailurePolicy can fail fast on non-retriable exit codes.",
        ],
        "examples": [
            {
                "title": "Parallel Job",
                "level": "basic",
                "description": "5 completions, 2 at a time, auto-deleted 5 minutes after finishing.",
                "yaml": y("""
                    apiVersion: batch/v1
                    kind: Job
                    metadata:
                      name: crunch
                    spec:
                      completions: 5
                      parallelism: 2
                      backoffLimit: 3
                      ttlSecondsAfterFinished: 300
                      template:
                        spec:
                          restartPolicy: Never
                          containers:
                            - name: worker
                              image: busybox:1.36
                              command: ["sh", "-c", "echo crunching; sleep 8; echo done"]
                """),
            },
            {
                "title": "CronJob every 2 minutes",
                "level": "intermediate",
                "description": "Forbid overlapping runs; keep 3 successful histories.",
                "yaml": y("""
                    apiVersion: batch/v1
                    kind: CronJob
                    metadata:
                      name: report
                    spec:
                      schedule: "*/2 * * * *"
                      timeZone: "Asia/Kolkata"
                      concurrencyPolicy: Forbid
                      successfulJobsHistoryLimit: 3
                      failedJobsHistoryLimit: 1
                      jobTemplate:
                        spec:
                          template:
                            spec:
                              restartPolicy: OnFailure
                              containers:
                                - name: report
                                  image: busybox:1.36
                                  command: ["sh", "-c", "date; echo generating report"]
                """),
            },
        ],
        "commands": [
            "kubectl get jobs,cronjobs",
            "kubectl create job manual-run --from=cronjob/report",
            "kubectl logs job/crunch",
        ],
        "gotchas": [
            "Jobs are retried with exponential backoff; a flaky job may take a long time to fail.",
            "CronJobs can miss runs if the controller is down > startingDeadlineSeconds.",
        ],
        "interview": [
            {"level": "basic", "q": "Job vs Deployment?", "a": "Deployment keeps pods running forever (restart Always). Job runs pods to successful completion and then stops."},
            {"level": "intermediate", "q": "Explain CronJob concurrencyPolicy.", "a": "Allow (default): overlapping runs ok. Forbid: skip the new run if the previous is still running. Replace: cancel the running job and start the new one."},
        ],
        "related": ["pods"],
        "scene": "jobs",
    },
    {
        "id": "init-sidecar",
        "title": "Init Containers & Sidecars",
        "category": "workloads",
        "level": "intermediate",
        "code": "In",
        "tagline": "Run setup steps before the app, and helpers alongside it.",
        "analogy": "Init containers are the stage crew who set up before the show; sidecars are the sound engineer who stays for the whole performance.",
        "what": "Init containers run sequentially to completion before app containers start (wait for DB, run migrations, fetch config). Native sidecars (GA in v1.33) are init containers with restartPolicy: Always: they start before the app, keep running, and stop after it — fixing Job/sidecar shutdown issues.",
        "use_cases": [
            "Wait for a dependency: `until nslookup db; do sleep 2; done`.",
            "Schema migrations before the app starts.",
            "Sidecars: log shipping, service-mesh proxies, secret refreshers.",
        ],
        "key_points": [
            "Init containers can use different images/tools than the app.",
            "If an init container fails, the pod restarts it (per restartPolicy).",
            "Pod status shows Init:0/2 while they run.",
        ],
        "examples": [
            {
                "title": "Init container + native sidecar",
                "level": "intermediate",
                "description": "Init writes a page; a native sidecar tails logs for the pod's lifetime.",
                "yaml": y("""
                    apiVersion: v1
                    kind: Pod
                    metadata:
                      name: init-demo
                    spec:
                      volumes:
                        - name: shared
                          emptyDir: {}
                      initContainers:
                        - name: prepare
                          image: busybox:1.36
                          command: ["sh", "-c", "echo '<h1>prepared by init</h1>' > /work/index.html; sleep 5"]
                          volumeMounts:
                            - {name: shared, mountPath: /work}
                        - name: log-shipper
                          image: busybox:1.36
                          restartPolicy: Always
                          command: ["sh", "-c", "touch /work/access.log; tail -F /work/access.log"]
                          volumeMounts:
                            - {name: shared, mountPath: /work}
                      containers:
                        - name: web
                          image: nginx:1.27-alpine
                          volumeMounts:
                            - {name: shared, mountPath: /usr/share/nginx/html}
                """),
            },
        ],
        "commands": [
            "kubectl get pod init-demo -w",
            "kubectl logs init-demo -c prepare",
            "kubectl describe pod init-demo",
        ],
        "gotchas": [
            "Classic sidecars in Jobs kept the pod alive forever — native sidecars fix this.",
            "Init container resource requests count toward scheduling (max of init vs sum of apps).",
        ],
        "interview": [
            {"level": "intermediate", "q": "Init container vs sidecar?", "a": "Init: runs to completion before app containers, sequentially. Sidecar: runs alongside the app for its lifetime (native sidecars = init containers with restartPolicy: Always, start before and stop after the main containers)."},
            {"level": "advanced", "q": "How are pod resource requests computed with init containers?", "a": "Effective request = max(largest init container request, sum of app containers + sidecars). The scheduler uses this effective value."},
        ],
        "related": ["pods", "jobs"],
        "scene": "init-sidecar",
    },
    # ------------------------------------------------------------------ storage
    {
        "id": "storage",
        "title": "PV, PVC & StorageClass",
        "category": "storage",
        "level": "intermediate",
        "code": "PV",
        "tagline": "Request storage abstractly; let the provisioner create the actual disk.",
        "analogy": "PVC = a rental request ('I need a 10 GB room'). StorageClass = the rental agency type (premium, standard). PV = the actual room handed over.",
        "what": "A PersistentVolumeClaim requests size + access mode + StorageClass. The CSI provisioner dynamically creates a PersistentVolume and binds it. Pods mount the PVC. reclaimPolicy (Delete/Retain) decides what happens to the disk when the PVC is deleted. volumeBindingMode: WaitForFirstConsumer delays provisioning until the pod is scheduled (zone-aware).",
        "use_cases": [
            "Databases and stateful apps.",
            "Shared file storage (RWX via NFS/EFS/Azure Files).",
            "Volume snapshots for backup/restore.",
        ],
        "key_points": [
            "Access modes: ReadWriteOnce, ReadOnlyMany, ReadWriteMany, ReadWriteOncePod.",
            "kind ships 'standard' StorageClass (rancher local-path).",
            "allowVolumeExpansion: true lets you grow PVCs.",
        ],
        "examples": [
            {
                "title": "PVC + pod",
                "level": "intermediate",
                "description": "Write data, delete the pod, recreate it — data is still there.",
                "yaml": y("""
                    apiVersion: v1
                    kind: PersistentVolumeClaim
                    metadata:
                      name: notes
                    spec:
                      accessModes: ["ReadWriteOnce"]
                      storageClassName: standard
                      resources:
                        requests:
                          storage: 100Mi
                    ---
                    apiVersion: v1
                    kind: Pod
                    metadata:
                      name: notes-writer
                    spec:
                      containers:
                        - name: app
                          image: busybox:1.36
                          command: ["sh", "-c", "date >> /data/notes.txt; cat /data/notes.txt; sleep 3600"]
                          volumeMounts:
                            - name: data
                              mountPath: /data
                      volumes:
                        - name: data
                          persistentVolumeClaim:
                            claimName: notes
                """),
            },
            {
                "title": "Custom StorageClass (cloud example)",
                "level": "advanced",
                "description": "AWS EBS gp3 with expansion and zone-aware binding (won't work on kind).",
                "yaml": y("""
                    apiVersion: storage.k8s.io/v1
                    kind: StorageClass
                    metadata:
                      name: fast-gp3
                    provisioner: ebs.csi.aws.com
                    parameters:
                      type: gp3
                      encrypted: "true"
                    reclaimPolicy: Retain
                    allowVolumeExpansion: true
                    volumeBindingMode: WaitForFirstConsumer
                """),
            },
        ],
        "commands": [
            "kubectl get sc,pv,pvc",
            "kubectl describe pvc notes",
            "kubectl delete pod notes-writer && kubectl logs notes-writer",
        ],
        "gotchas": [
            "PVC Pending with WaitForFirstConsumer is normal until a pod uses it.",
            "RWO volumes can attach to only one NODE — two pods on different nodes fail.",
        ],
        "interview": [
            {"level": "basic", "q": "PV vs PVC?", "a": "PV is the actual storage resource (cluster-scoped). PVC is a namespaced request for storage that binds to a PV. Pods reference PVCs, not PVs."},
            {"level": "intermediate", "q": "What is WaitForFirstConsumer?", "a": "Volume binding/provisioning is delayed until a pod using the PVC is scheduled, so the disk is created in the same zone as the pod — avoids zone mismatch."},
            {"level": "advanced", "q": "Reclaim policies?", "a": "Delete: underlying disk is deleted with the PVC (default for dynamic). Retain: PV and data are kept for manual recovery. (Recycle is deprecated.)"},
        ],
        "related": ["statefulsets"],
        "scene": "storage",
    },
    # ------------------------------------------------------------------ networking
    {
        "id": "ingress",
        "title": "Ingress",
        "category": "networking",
        "level": "intermediate",
        "code": "Ig",
        "tagline": "HTTP(S) routing from outside the cluster to Services by host and path.",
        "analogy": "Ingress is a hotel receptionist: guests arrive at one front door and get directed by name/purpose ('/api → conference hall, / → lobby').",
        "what": "An Ingress resource defines host/path rules; an Ingress controller (ingress-nginx, Traefik, cloud LBs) implements them. TLS is terminated with a Secret (usually issued by cert-manager). Gateway API (Gateway, HTTPRoute) is the more expressive successor.",
        "use_cases": [
            "One LB for many services (cost).",
            "Path routing (/api, /static) and virtual hosts.",
            "TLS termination, redirects, rate limits via controller annotations.",
        ],
        "key_points": [
            "Ingress does nothing without a controller (playground: Create cluster with ingress option).",
            "pathType: Prefix, Exact, ImplementationSpecific.",
            "ingressClassName selects the controller.",
        ],
        "examples": [
            {
                "title": "Path-based routing",
                "level": "intermediate",
                "description": "With the ingress add-on: curl http://localhost:8081/ and /api.",
                "yaml": y("""
                    apiVersion: apps/v1
                    kind: Deployment
                    metadata: {name: frontend}
                    spec:
                      replicas: 1
                      selector: {matchLabels: {app: frontend}}
                      template:
                        metadata: {labels: {app: frontend}}
                        spec:
                          containers:
                            - name: web
                              image: hashicorp/http-echo:1.0
                              args: ["-text=hello from frontend", "-listen=:5678"]
                    ---
                    apiVersion: v1
                    kind: Service
                    metadata: {name: frontend}
                    spec:
                      selector: {app: frontend}
                      ports: [{port: 80, targetPort: 5678}]
                    ---
                    apiVersion: apps/v1
                    kind: Deployment
                    metadata: {name: api}
                    spec:
                      replicas: 1
                      selector: {matchLabels: {app: api}}
                      template:
                        metadata: {labels: {app: api}}
                        spec:
                          containers:
                            - name: api
                              image: hashicorp/http-echo:1.0
                              args: ["-text=hello from api", "-listen=:5678"]
                    ---
                    apiVersion: v1
                    kind: Service
                    metadata: {name: api}
                    spec:
                      selector: {app: api}
                      ports: [{port: 80, targetPort: 5678}]
                    ---
                    apiVersion: networking.k8s.io/v1
                    kind: Ingress
                    metadata:
                      name: shop
                    spec:
                      ingressClassName: nginx
                      rules:
                        - http:
                            paths:
                              - path: /api
                                pathType: Prefix
                                backend:
                                  service: {name: api, port: {number: 80}}
                              - path: /
                                pathType: Prefix
                                backend:
                                  service: {name: frontend, port: {number: 80}}
                """),
            },
            {
                "title": "TLS with cert-manager (production pattern)",
                "level": "advanced",
                "description": "cert-manager issues and rotates the certificate into the Secret — never hand-paste certs/keys into manifests.",
                "yaml": y("""
                    apiVersion: networking.k8s.io/v1
                    kind: Ingress
                    metadata:
                      name: shop-tls
                      annotations:
                        cert-manager.io/cluster-issuer: letsencrypt-prod
                    spec:
                      ingressClassName: nginx
                      tls:
                        - hosts: [shop.example.com]
                          secretName: shop-example-com-tls
                      rules:
                        - host: shop.example.com
                          http:
                            paths:
                              - path: /
                                pathType: Prefix
                                backend:
                                  service: {name: frontend, port: {number: 80}}
                """),
            },
        ],
        "commands": [
            "kubectl get ingress",
            "kubectl describe ingress shop",
            "kubectl -n ingress-nginx get pods",
        ],
        "gotchas": [
            "Annotations are controller-specific (nginx.ingress.kubernetes.io/... won't work on Traefik).",
            "Ingress-nginx is in maintenance mode upstream; evaluate Gateway API for new platforms.",
        ],
        "interview": [
            {"level": "basic", "q": "Ingress vs Service type LoadBalancer?", "a": "LoadBalancer gives one external LB per Service (L4). Ingress shares one entry point and routes L7 HTTP by host/path to many services, with TLS termination."},
            {"level": "intermediate", "q": "What is an Ingress controller?", "a": "The component (e.g. ingress-nginx pods) that watches Ingress objects and configures a reverse proxy/LB accordingly. Without it, Ingress objects have no effect."},
            {"level": "advanced", "q": "Why Gateway API?", "a": "Role-oriented (infra team owns Gateway, app teams own HTTPRoutes), portable typed features (header matching, weights for canary, TCP/gRPC routes) instead of vendor annotations."},
        ],
        "related": ["services", "network-policy"],
        "scene": "ingress",
    },
    {
        "id": "network-policy",
        "title": "NetworkPolicy",
        "category": "networking",
        "level": "advanced",
        "code": "NP",
        "tagline": "Pod-level firewall rules: who may talk to whom.",
        "analogy": "Office access cards: by default every door is open. A NetworkPolicy reprograms doors so only finance staff can enter the vault.",
        "what": "By default all pods can talk to all pods. Once a pod is selected by a policy for Ingress/Egress, only explicitly allowed traffic passes (allow-list, additive). Rules match podSelector, namespaceSelector and ipBlock plus ports. Enforcement requires a CNI that supports it (Calico, Cilium; recent kindnet versions also enforce policies).",
        "use_cases": [
            "Default-deny per namespace, then allow known flows.",
            "Only frontend → backend → database.",
            "Restrict egress to known external IP ranges (and DNS!).",
        ],
        "key_points": [
            "Policies are additive; there is no 'deny' rule (except via default-deny).",
            "Egress default-deny breaks DNS unless you allow UDP/TCP 53 to kube-dns.",
            "namespaceSelector + podSelector in ONE item = AND; separate items = OR.",
        ],
        "examples": [
            {
                "title": "Default deny + allow frontend → backend",
                "level": "advanced",
                "description": "Apply both, then only pods labelled app=frontend reach app=backend on 8080.",
                "yaml": y("""
                    apiVersion: networking.k8s.io/v1
                    kind: NetworkPolicy
                    metadata:
                      name: default-deny-ingress
                    spec:
                      podSelector: {}
                      policyTypes: [Ingress]
                    ---
                    apiVersion: networking.k8s.io/v1
                    kind: NetworkPolicy
                    metadata:
                      name: backend-allow-frontend
                    spec:
                      podSelector:
                        matchLabels: {app: backend}
                      policyTypes: [Ingress]
                      ingress:
                        - from:
                            - podSelector:
                                matchLabels: {app: frontend}
                          ports:
                            - protocol: TCP
                              port: 8080
                """),
            },
        ],
        "commands": [
            "kubectl get networkpolicy",
            "kubectl describe networkpolicy backend-allow-frontend",
            "kubectl run probe --image=busybox:1.36 --restart=Never -l app=frontend -- wget -qO- -T2 backend:8080",
        ],
        "gotchas": [
            "Using a CNI without policy support = policies silently ignored.",
            "Pod-to-node / hostNetwork traffic semantics vary by CNI.",
        ],
        "interview": [
            {"level": "intermediate", "q": "What's the default network behavior in Kubernetes?", "a": "Flat network: every pod can reach every other pod across namespaces. NetworkPolicies are needed to restrict it."},
            {"level": "advanced", "q": "You applied egress default-deny and the app broke entirely. Why?", "a": "DNS lookups to kube-dns (UDP/TCP 53 in kube-system) are blocked. Add an egress rule allowing DNS, then the specific destinations."},
            {"level": "advanced", "q": "Explain the AND vs OR gotcha in `from`.", "a": "One list item with both namespaceSelector and podSelector = pods matching podSelector IN namespaces matching namespaceSelector (AND). Two separate items = any pod in those namespaces OR matching pods in the policy's namespace."},
        ],
        "related": ["ingress", "services", "namespaces"],
        "scene": "network-policy",
    },
    # ------------------------------------------------------------------ security
    {
        "id": "rbac",
        "title": "RBAC & ServiceAccounts",
        "category": "security",
        "level": "advanced",
        "code": "RB",
        "tagline": "Least-privilege access for humans and workloads to the Kubernetes API.",
        "analogy": "A Role is a job description ('can read the inventory'), a RoleBinding is the employment contract assigning it to a person or a robot (ServiceAccount).",
        "what": "RBAC rules list apiGroups, resources and verbs. Role/RoleBinding are namespaced; ClusterRole/ClusterRoleBinding are cluster-wide (a RoleBinding can reference a ClusterRole to reuse it in one namespace). Pods authenticate as ServiceAccounts via projected, short-lived tokens. RBAC is purely additive (no deny).",
        "use_cases": [
            "CI bot may deploy only to its namespace.",
            "Operators/controllers watching specific resources.",
            "Read-only access for developers in prod.",
        ],
        "key_points": [
            "Verbs: get, list, watch, create, update, patch, delete, deletecollection.",
            "`kubectl auth can-i` to verify permissions (with --as for impersonation).",
            "automountServiceAccountToken: false for pods that don't need the API.",
            "Avoid wildcard (*) rules and cluster-admin bindings.",
        ],
        "examples": [
            {
                "title": "Read-only pod access for a CI ServiceAccount",
                "level": "advanced",
                "description": "Then test: kubectl auth can-i list pods --as=system:serviceaccount:default:ci-bot",
                "yaml": y("""
                    apiVersion: v1
                    kind: ServiceAccount
                    metadata:
                      name: ci-bot
                    ---
                    apiVersion: rbac.authorization.k8s.io/v1
                    kind: Role
                    metadata:
                      name: pod-reader
                    rules:
                      - apiGroups: [""]
                        resources: ["pods", "pods/log"]
                        verbs: ["get", "list", "watch"]
                    ---
                    apiVersion: rbac.authorization.k8s.io/v1
                    kind: RoleBinding
                    metadata:
                      name: ci-bot-reads-pods
                    subjects:
                      - kind: ServiceAccount
                        name: ci-bot
                        namespace: default
                    roleRef:
                      kind: Role
                      name: pod-reader
                      apiGroup: rbac.authorization.k8s.io
                """),
            },
        ],
        "commands": [
            "kubectl auth can-i list pods --as=system:serviceaccount:default:ci-bot",
            "kubectl auth can-i delete pods --as=system:serviceaccount:default:ci-bot",
            "kubectl get roles,rolebindings",
            "kubectl describe clusterrole view",
        ],
        "gotchas": [
            "`create pods` permission implies access to any Secret/SA in that namespace (mount it).",
            "Escalate/bind/impersonate verbs are privilege-escalation vectors.",
        ],
        "interview": [
            {"level": "intermediate", "q": "Role vs ClusterRole?", "a": "Role grants permissions within one namespace. ClusterRole is cluster-scoped: for cluster resources (nodes, PVs), non-resource URLs, or reusable roles bound per namespace via RoleBinding."},
            {"level": "advanced", "q": "How do pods authenticate to the API server?", "a": "Via a ServiceAccount token projected into the pod (bound, audience-scoped, auto-rotated, ~1h). The API server validates it and RBAC authorizes the SA's requests."},
            {"level": "advanced", "q": "How would you audit who can delete deployments in prod?", "a": "`kubectl auth can-i --list --as=...` per subject, or tools like rbac-lookup/kubectl-who-can; review ClusterRoleBindings to cluster-admin; enable API audit logs."},
        ],
        "related": ["secrets", "namespaces"],
        "scene": "rbac",
    },
]


SCENARIOS = [
    {"level": "intermediate", "topic": "nodeselector", "q": "A pod is Pending: `0/4 nodes are available: 1 node(s) had untolerated taint {node-role.kubernetes.io/control-plane: }, 3 node(s) didn't match Pod's node affinity/selector`. Walk through your fix.", "a": "Check the pod's nodeSelector/affinity vs node labels (`kubectl get nodes --show-labels`). Either fix the typo/label in the manifest, label an appropriate node, or relax required → preferred affinity. The control-plane taint is expected and not the issue."},
    {"level": "intermediate", "topic": "hpa", "q": "Traffic doubled but the HPA did not scale. What do you check?", "a": "`kubectl describe hpa`: metrics available? (metrics-server, requests set). Current vs target, maxReplicas already reached? ScalingLimited conditions? Behavior policies? Pods Pending due to capacity (then cluster autoscaler)?"},
    {"level": "advanced", "topic": "pdb", "q": "Cluster upgrade is stuck draining one node for 30 minutes.", "a": "List PDBs with ALLOWED DISRUPTIONS 0, single-replica apps with minAvailable 1, pods unable to reschedule (anti-affinity, taints, no capacity), local-storage pods. Scale up the app, temporarily adjust the PDB, or fix scheduling constraints."},
    {"level": "advanced", "topic": "resources-qos", "q": "Pods restart every few hours with exit code 137.", "a": "137 = SIGKILL, usually OOMKilled. `kubectl describe pod` shows Last State: OOMKilled. Check memory limit vs real usage (kubectl top, metrics), memory leaks, JVM heap flags; raise limits or fix the leak. If no OOMKilled reason, check liveness probe kills or node pressure eviction."},
    {"level": "intermediate", "topic": "configmaps", "q": "You changed a ConfigMap; half the pods use new config, half old.", "a": "Pods mounting the ConfigMap as a volume got updates (eventually), pods using env vars didn't. Or some pods restarted. Use a checksum annotation or `kubectl rollout restart` to roll consistently; consider immutable versioned ConfigMaps."},
    {"level": "advanced", "topic": "services", "q": "During deployments users see 502 errors for a few seconds.", "a": "Pods receive traffic before ready (no readiness probe) or are killed while still in endpoints. Add readiness probes, a preStop `sleep 5-10`, handle SIGTERM gracefully, maxUnavailable 0, and ensure the ingress controller respects endpoint updates."},
    {"level": "advanced", "topic": "pod-affinity", "q": "Rolling update of a 3-replica Deployment on a 3-node cluster never finishes.", "a": "Hard pod anti-affinity on hostname: the surge pod has nowhere to go. Use maxSurge 0/maxUnavailable 1, preferred anti-affinity, or topologySpreadConstraints with maxSkew."},
    {"level": "intermediate", "topic": "probes", "q": "After adding a liveness probe, the app is in CrashLoopBackOff on startup only.", "a": "Liveness probe fires before the app is up (slow boot) and kills it. Add a startupProbe with enough failureThreshold×periodSeconds, or relax liveness timing."},
    {"level": "advanced", "topic": "network-policy", "q": "After applying a namespace default-deny egress policy, every app returns DNS errors.", "a": "DNS to kube-dns is blocked. Add an egress rule to namespace kube-system pods k8s-app=kube-dns on UDP/TCP 53, then allow specific app destinations."},
    {"level": "basic", "topic": "pods", "q": "`ImagePullBackOff` — what are common causes?", "a": "Wrong image name/tag, private registry without imagePullSecrets, registry rate limits (Docker Hub), network/proxy issues, or wrong architecture manifest. `kubectl describe pod` shows the exact pull error."},
]


from app.topics_more import CATEGORIES as _MORE_CATEGORIES, EXTRA_INTERVIEW as _EXTRA_INTERVIEW, SCENARIOS as _MORE_SCENARIOS, TOPICS as _MORE_TOPICS

for _t in TOPICS:
    _t["interview"] += _EXTRA_INTERVIEW.get(_t["id"], [])

CATEGORIES += _MORE_CATEGORIES
TOPICS += _MORE_TOPICS
SCENARIOS += _MORE_SCENARIOS


def topic_index() -> list[dict]:
    return [
        {k: t[k] for k in ("id", "title", "category", "level", "code", "tagline")} for t in TOPICS
    ]


def get_topic(topic_id: str) -> dict | None:
    return next((t for t in TOPICS if t["id"] == topic_id), None)
