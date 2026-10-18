"""More Kubernetes topics. They use a generic flow animation instead of a hand-built scene."""

from textwrap import dedent

from app.subjects._dsl import chain, qa, topic


def y(text: str) -> str:
    return dedent(text).strip() + "\n"


CATEGORIES = [
    {"id": "operations", "title": "Operations", "color": "slate", "blurb": "kubectl, packaging, GitOps and day-2 cluster care."},
    {"id": "extending", "title": "Extending K8s", "color": "peach", "blurb": "CRDs, operators and admission policy."},
    {"id": "observability", "title": "Observability", "color": "rose", "blurb": "Metrics, logs, events and live debugging."},
]

TOPICS = [
    # ------------------------------------------------------------------ fundamentals
    topic(
        id="cluster-architecture",
        title="Cluster Architecture",
        category="fundamentals",
        level="basic",
        code="CA",
        tagline="Control plane decides, nodes execute: API server, etcd, scheduler, controllers, kubelet.",
        analogy="The control plane is an airport control tower with a logbook (etcd); nodes are the runways and kubelets are the ground crews who actually park the planes.",
        what=(
            "A Kubernetes cluster is split into a control plane and worker nodes. The kube-apiserver is the only component that "
            "talks to etcd, the consistent key-value store holding every object. The kube-scheduler watches for unscheduled pods and "
            "binds them to nodes; the kube-controller-manager runs reconcile loops (Deployment, ReplicaSet, Node, Job, EndpointSlice...) "
            "that drive actual state toward desired state. On every node the kubelet watches pods bound to it and asks the container "
            "runtime (containerd, CRI-O) through CRI to start them, while kube-proxy (or an eBPF CNI) programs Service routing. "
            "Everything communicates through the API server using watches, so components are loosely coupled and individually restartable. "
            "Managed offerings (EKS, GKE, AKS) run the control plane for you, but the same components and failure modes still apply."
        ),
        use_cases=[
            "Reasoning about where a failure lives: Pending pod (scheduler), not starting (kubelet/runtime), not updating (controller).",
            "Sizing and hardening a self-managed control plane (3 or 5 etcd members for quorum).",
            "Explaining why the cluster keeps running workloads even if the control plane is briefly down.",
        ],
        key_points=[
            "Only the API server reads and writes etcd; every other component is an API client.",
            "etcd needs an odd number of members (3 or 5) and a majority quorum to accept writes.",
            "Controllers are level-triggered reconcile loops: observe, diff, act, repeat.",
            "kubelet runs static pods from /etc/kubernetes/manifests, which is how kubeadm hosts the control plane.",
            "Running pods keep serving if the control plane dies; you just lose changes, scheduling and self-healing.",
        ],
        examples=[
            {
                "title": "Hardened kubelet configuration",
                "level": "intermediate",
                "description": "Disables anonymous access, uses webhook authz against the API server and requires TLS 1.3.",
                "yaml": y("""
                    apiVersion: kubelet.config.k8s.io/v1beta1
                    kind: KubeletConfiguration
                    authentication:
                      anonymous:
                        enabled: false
                      webhook:
                        enabled: true
                    authorization:
                      mode: Webhook
                    tlsMinVersion: VersionTLS13
                    rotateCertificates: true
                    serverTLSBootstrap: true
                    readOnlyPort: 0
                    protectKernelDefaults: true
                """),
            },
            {
                "title": "Static pod for the scheduler (kubeadm style)",
                "level": "advanced",
                "description": "kubelet starts this directly from /etc/kubernetes/manifests; the API shows a read-only mirror pod.",
                "yaml": y("""
                    apiVersion: v1
                    kind: Pod
                    metadata:
                      name: kube-scheduler
                      namespace: kube-system
                      labels:
                        component: kube-scheduler
                        tier: control-plane
                    spec:
                      hostNetwork: true
                      priorityClassName: system-node-critical
                      containers:
                        - name: kube-scheduler
                          image: registry.k8s.io/kube-scheduler:v1.31.0
                          command:
                            - kube-scheduler
                            - --kubeconfig=/etc/kubernetes/scheduler.conf
                            - --leader-elect=true
                            - --tls-min-version=VersionTLS13
                          volumeMounts:
                            - name: kubeconfig
                              mountPath: /etc/kubernetes/scheduler.conf
                              readOnly: true
                      volumes:
                        - name: kubeconfig
                          hostPath:
                            path: /etc/kubernetes/scheduler.conf
                            type: FileOrCreate
                """),
            },
        ],
        commands=[
            "kubectl get --raw='/readyz?verbose'",
            "kubectl get pods -n kube-system -o wide",
            "kubectl get nodes -o wide",
            "kubectl get lease -n kube-system",
            "kubectl get componentstatuses",
        ],
        gotchas=[
            "Losing etcd quorum makes the API read-only or unavailable; a 2-member etcd is worse than 1 (both must agree).",
            "`componentstatuses` is deprecated; use the /livez and /readyz endpoints instead.",
            "Scheduler and controller-manager use leader election, so only one replica is active at a time.",
        ],
        interview=[
            qa("basic", "What are the control plane components and what does each do?", "kube-apiserver exposes the REST API and is the only etcd client; etcd stores cluster state; kube-scheduler assigns pods to nodes; kube-controller-manager runs reconcile loops; cloud-controller-manager integrates cloud load balancers, routes and nodes. Nodes run kubelet, a container runtime and usually kube-proxy."),
            qa("intermediate", "What happens to running workloads if the whole control plane goes down?", "Existing containers keep running and kube-proxy rules stay in place, so traffic keeps flowing. But nothing new can be scheduled, crashed pods on dead nodes are not replaced, scaling stops and kubectl fails until the API server returns."),
            qa("intermediate", "Why does etcd need an odd number of members?", "Raft requires a majority (quorum) to commit writes. 3 members tolerate 1 failure and 5 tolerate 2; adding a 4th member raises quorum to 3 without increasing fault tolerance, so even counts add cost but no resilience."),
            qa("advanced", "Explain the controller pattern and why it is level-triggered.", "A controller watches resources via informers, compares desired spec with observed status and takes actions to converge, requeueing on errors. Being level-triggered means it acts on the current state rather than individual events, so missed events or restarts are harmless: the next reconcile still sees the full picture."),
        ],
        related=["pods", "deployments", "namespaces"],
        flow=chain(
            ("kubectl", "user intent", "You declare state", "kubectl sends a Deployment manifest to the API server over TLS."),
            ("API server", "authn/authz/admit", "Request validated", "The API server authenticates, authorizes, runs admission and persists the object.", "POST"),
            ("etcd", "source of truth", "State stored", "The object is written to etcd through Raft consensus.", "write"),
            ("Controllers", "reconcile loops", "Pods created", "Deployment and ReplicaSet controllers notice the new object and create Pod objects.", "watch"),
            ("Scheduler", "pick a node", "Pods bound", "The scheduler filters and scores nodes, then writes spec.nodeName.", "bind"),
            ("kubelet", "runs containers", "Containers start", "The node's kubelet sees the bound pod and starts it via the CRI runtime.", "PodSpec"),
        ),
    ),
    topic(
        id="api-request-flow",
        title="API Server Request Flow",
        category="security",
        level="intermediate",
        code="AR",
        tagline="Every request: authenticate, authorize, mutate, validate, persist.",
        analogy="Entering a secure office: show your badge (authentication), the guard checks your access list (authorization), reception adjusts your visitor pass (mutating admission), security inspects your bag (validating admission), then you are logged in the visitor book (etcd).",
        what=(
            "Every call to kube-apiserver passes through a fixed pipeline. Authentication identifies the caller from client certificates, "
            "bearer tokens (ServiceAccount or OIDC JWTs) or an authenticating proxy, producing a username and groups. Authorization then asks "
            "the configured authorizers (Node, RBAC, Webhook) whether that user may perform the verb on the resource; the first allow wins and "
            "the default is deny. Mutating admission controllers and webhooks can change the object (inject sidecars, set defaults), after which "
            "schema validation and validating admission (ValidatingAdmissionPolicy, webhooks, PodSecurity, ResourceQuota) can only accept or reject. "
            "The object is finally versioned with a resourceVersion and stored in etcd, and watchers are notified. Audit logging can record "
            "each stage, which is invaluable for security investigations."
        ),
        use_cases=[
            "Debugging a 401 (authentication) versus a 403 (authorization or admission) error.",
            "Integrating SSO for kubectl via OIDC instead of shared admin certificates.",
            "Enabling audit logs to answer 'who deleted this Deployment?'.",
        ],
        key_points=[
            "401 Unauthorized means identity could not be established; 403 Forbidden means identity known but denied.",
            "Authorization modes are evaluated in order, e.g. --authorization-mode=Node,RBAC.",
            "Mutating admission runs before validating admission so validators see the final object.",
            "Use `kubectl auth whoami` and `kubectl auth can-i` to inspect identity and permissions.",
            "Audit policy levels: None, Metadata, Request, RequestResponse.",
        ],
        examples=[
            {
                "title": "Structured OIDC authentication",
                "level": "intermediate",
                "description": "Lets users log in with an identity provider; groups map to RBAC subjects. No static tokens are stored.",
                "yaml": y("""
                    apiVersion: apiserver.config.k8s.io/v1beta1
                    kind: AuthenticationConfiguration
                    jwt:
                      - issuer:
                          url: https://idp.example.com
                          audiences:
                            - kubernetes
                        claimMappings:
                          username:
                            claim: email
                            prefix: "oidc:"
                          groups:
                            claim: groups
                            prefix: "oidc:"
                """),
            },
            {
                "title": "Audit policy",
                "level": "advanced",
                "description": "Records Secret access only as metadata (never payloads) and full bodies for RBAC changes.",
                "yaml": y("""
                    apiVersion: audit.k8s.io/v1
                    kind: Policy
                    omitStages:
                      - RequestReceived
                    rules:
                      - level: Metadata
                        resources:
                          - group: ""
                            resources: ["secrets", "configmaps"]
                      - level: RequestResponse
                        resources:
                          - group: rbac.authorization.k8s.io
                      - level: None
                        users: ["system:kube-proxy"]
                        verbs: ["watch"]
                      - level: Metadata
                """),
            },
        ],
        commands=[
            "kubectl auth whoami",
            "kubectl auth can-i create deployments -n prod",
            "kubectl get deploy web -v=8",
            "kubectl api-resources --verbs=list -o wide",
            "kubectl get --raw /apis | head",
        ],
        gotchas=[
            "Logging Secrets at Request or RequestResponse level writes their values into audit logs.",
            "A failing admission webhook with failurePolicy: Fail can block every matching request cluster-wide.",
            "Client certificates cannot be revoked by Kubernetes; prefer OIDC or short-lived tokens for humans.",
        ],
        interview=[
            qa("basic", "Walk through what happens when you run kubectl apply.", "kubectl sends an HTTPS request; the API server authenticates the caller, authorizes the verb/resource, runs mutating admission, validates the schema, runs validating admission, then writes the object to etcd. Controllers watching that resource then react to the change."),
            qa("intermediate", "How do you tell an authentication problem from an authorization problem?", "A 401 means the credentials were missing, expired or not trusted. A 403 includes the resolved user in the message, meaning authentication worked but RBAC or an admission controller denied the request; `kubectl auth can-i --as` reproduces the decision."),
            qa("intermediate", "What does the Node authorizer do?", "It restricts kubelets (system:node:<name>) to reading only the Secrets, ConfigMaps and volumes referenced by pods bound to their own node and to updating only their own Node and pod status objects. Combined with the NodeRestriction admission plugin it limits damage from a compromised node."),
            qa("advanced", "Why is the order mutating then validating important?", "Mutators may change any field, so validation must run after all mutations to judge the final object. Webhooks also may be re-invoked (reinvocationPolicy) if later mutators change the object, and only validators can be trusted to enforce policy on what is actually persisted."),
        ],
        related=["rbac", "namespaces", "secrets"],
        flow=chain(
            ("Client", "kubectl / pod", "Request sent", "A client calls the API with a cert or bearer token over TLS."),
            ("AuthN", "who are you?", "Identity resolved", "Authenticators map credentials to a user and groups, or return 401.", "token"),
            ("AuthZ", "may you?", "Permission checked", "Node and RBAC authorizers allow or deny the verb; deny returns 403.", "user"),
            ("Mutating", "admission", "Object adjusted", "Mutating plugins and webhooks set defaults or inject sidecars.", "allowed"),
            ("Validating", "admission", "Policy enforced", "Validators such as PodSecurity and quota accept or reject the final object.", "patched"),
            ("etcd", "persisted", "Stored and watched", "The object is saved with a new resourceVersion and watchers are notified.", "ok"),
        ),
    ),
    topic(
        id="replicasets",
        title="ReplicaSets",
        category="fundamentals",
        level="basic",
        code="RS",
        tagline="Keeps exactly N matching pods running; the engine under every Deployment.",
        analogy="A ReplicaSet is a thermostat for pod count: it reads the current number, compares it with the target, and switches pods on or off until they match.",
        what=(
            "A ReplicaSet ensures a specified number of pods matching its label selector exist at any time. Its controller counts pods that "
            "match the selector and are not terminating, then creates pods from its template or deletes extras. Pods it creates get an "
            "ownerReference pointing at the ReplicaSet, which enables garbage collection when the ReplicaSet is deleted. A ReplicaSet does not "
            "update existing pods when its template changes; only newly created pods use the new template. That is exactly why Deployments exist: "
            "they create a fresh ReplicaSet per template revision and shift replicas between them. You almost never create ReplicaSets "
            "directly, but understanding them explains rollout history, orphaned pods and pod-template-hash labels."
        ),
        use_cases=[
            "Understanding why a Deployment shows several old ReplicaSets with 0 replicas (rollback history).",
            "Adopting or orphaning pods by changing labels during debugging.",
            "Building custom controllers that need a simple fixed-count primitive.",
        ],
        key_points=[
            "Selector must match template labels; selector is immutable in apps/v1.",
            "Deployments add a pod-template-hash label so ReplicaSets never fight over the same pods.",
            "Scale-down prefers deleting pending, unready, and newer pods first, and honours pod-deletion-cost.",
            "`kubectl delete rs x --cascade=orphan` keeps the pods but removes the owner.",
        ],
        examples=[
            {
                "title": "Bare ReplicaSet",
                "level": "basic",
                "description": "Three nginx pods; delete one and the controller creates a replacement immediately.",
                "yaml": y("""
                    apiVersion: apps/v1
                    kind: ReplicaSet
                    metadata:
                      name: web-rs
                    spec:
                      replicas: 3
                      selector:
                        matchLabels:
                          app: web-rs
                      template:
                        metadata:
                          labels:
                            app: web-rs
                        spec:
                          containers:
                            - name: web
                              image: nginx:1.27-alpine
                """),
            },
            {
                "title": "Steering scale-down with pod-deletion-cost",
                "level": "advanced",
                "description": "Pods with lower cost are removed first when the ReplicaSet scales down.",
                "yaml": y("""
                    apiVersion: v1
                    kind: Pod
                    metadata:
                      name: web-rs-cheap
                      labels:
                        app: web-rs
                      annotations:
                        controller.kubernetes.io/pod-deletion-cost: "-100"
                    spec:
                      containers:
                        - name: web
                          image: nginx:1.27-alpine
                """),
            },
        ],
        commands=[
            "kubectl get rs -l app=web -o wide",
            "kubectl describe rs web-rs",
            "kubectl scale rs web-rs --replicas=5",
            "kubectl get pod <pod> -o jsonpath='{.metadata.ownerReferences[0].name}'",
            "kubectl delete rs web-rs --cascade=orphan",
        ],
        gotchas=[
            "A bare pod with labels that match a ReplicaSet selector gets adopted and may be deleted to keep the count.",
            "Editing a ReplicaSet template does not restart existing pods.",
            "Scaling a ReplicaSet owned by a Deployment is reverted by the Deployment controller.",
        ],
        interview=[
            qa("basic", "Why not use ReplicaSets directly?", "They only maintain a count and never roll existing pods to a new template. Deployments manage ReplicaSets to provide rolling updates, rollback history, pause/resume and progress deadlines."),
            qa("intermediate", "What is pod-template-hash?", "A label the Deployment controller adds to each ReplicaSet's selector and pods, derived from a hash of the pod template. It guarantees ReplicaSets of different revisions select disjoint pods."),
            qa("intermediate", "How does garbage collection relate to ReplicaSets?", "Each pod carries an ownerReference to its ReplicaSet. Deleting the ReplicaSet with the default background cascade deletes dependents; foreground waits for them; orphan leaves them running without an owner."),
            qa("advanced", "Which pods does a ReplicaSet delete first when scaling down?", "It ranks pods: unscheduled before scheduled, Pending before Running, not-ready before ready, lower pod-deletion-cost first, pods on nodes with more replicas first, then more recently created pods. This keeps the most established, healthy pods alive."),
        ],
        related=["deployments", "labels", "pods"],
        flow=chain(
            ("Desired", "replicas: 3", "Target declared", "The ReplicaSet spec says three pods matching app=web."),
            ("Observe", "count matches", "Pods counted", "The controller lists pods matching the selector: it finds only two.", "watch"),
            ("Diff", "3 - 2 = 1", "Gap computed", "Desired minus actual equals one missing pod.", "2 found"),
            ("Create", "from template", "Pod created", "A new pod is created from the template with an ownerReference.", "+1"),
        ),
    ),
    topic(
        id="rollout-strategies",
        title="Rolling Updates & Rollbacks",
        category="reliability",
        level="intermediate",
        code="RO",
        tagline="Ship new versions gradually, watch progress, and undo in one command.",
        analogy="Replacing the wheels of a moving bus one at a time: you add a spare first (maxSurge), never let more than a few be off at once (maxUnavailable), and put the old wheel back if the new one wobbles.",
        what=(
            "When a Deployment's pod template changes, the controller creates a new ReplicaSet and scales it up while scaling the old one down. "
            "maxSurge bounds how many extra pods may exist and maxUnavailable bounds how many may be missing, so you choose between speed, extra "
            "capacity and availability. A pod only counts as available once it is Ready for minReadySeconds, which makes readiness probes the real "
            "gate of every rollout. progressDeadlineSeconds marks a stuck rollout as failed (condition Progressing=False) but does not roll back "
            "automatically. The Recreate strategy kills all old pods first, useful when two versions cannot run together. Rollbacks re-apply an "
            "older ReplicaSet template, and `kubectl rollout pause` lets you batch several changes into one revision."
        ),
        use_cases=[
            "Zero-downtime releases of stateless APIs with maxUnavailable: 0.",
            "Recreate for apps holding an exclusive lock or running incompatible schema migrations.",
            "Fast rollback when error rates spike after a release.",
        ],
        key_points=[
            "Only changes to spec.template trigger a new revision.",
            "minReadySeconds protects against pods that pass readiness then crash seconds later.",
            "progressDeadlineSeconds (default 600) sets the Progressing condition to False on stalls.",
            "kubernetes.io/change-cause annotation populates the CHANGE-CAUSE column in rollout history.",
            "StatefulSets and DaemonSets have their own RollingUpdate knobs (partition, maxUnavailable).",
        ],
        examples=[
            {
                "title": "Safe rolling update",
                "level": "intermediate",
                "description": "Surges one pod at a time, never drops capacity and requires 10s of stable readiness.",
                "yaml": y("""
                    apiVersion: apps/v1
                    kind: Deployment
                    metadata:
                      name: api
                      annotations:
                        kubernetes.io/change-cause: "release 2.4.1"
                    spec:
                      replicas: 4
                      minReadySeconds: 10
                      progressDeadlineSeconds: 300
                      revisionHistoryLimit: 5
                      strategy:
                        type: RollingUpdate
                        rollingUpdate:
                          maxSurge: 1
                          maxUnavailable: 0
                      selector:
                        matchLabels:
                          app: api
                      template:
                        metadata:
                          labels:
                            app: api
                        spec:
                          containers:
                            - name: api
                              image: ghcr.io/example/api:2.4.1
                              readinessProbe:
                                httpGet:
                                  path: /healthz
                                  port: 8080
                                periodSeconds: 5
                """),
            },
            {
                "title": "Recreate strategy",
                "level": "basic",
                "description": "All old pods stop before new ones start: brief downtime, but versions never overlap.",
                "yaml": y("""
                    apiVersion: apps/v1
                    kind: Deployment
                    metadata:
                      name: legacy-worker
                    spec:
                      replicas: 1
                      strategy:
                        type: Recreate
                      selector:
                        matchLabels:
                          app: legacy-worker
                      template:
                        metadata:
                          labels:
                            app: legacy-worker
                        spec:
                          containers:
                            - name: worker
                              image: ghcr.io/example/worker:1.9.0
                """),
            },
        ],
        commands=[
            "kubectl set image deploy/api api=ghcr.io/example/api:2.4.2",
            "kubectl rollout status deploy/api --timeout=5m",
            "kubectl rollout history deploy/api --revision=3",
            "kubectl rollout undo deploy/api --to-revision=3",
            "kubectl rollout pause deploy/api && kubectl rollout resume deploy/api",
        ],
        gotchas=[
            "Without a readiness probe, pods count as available as soon as containers start and broken versions roll out fully.",
            "A failed progress deadline only sets a condition; your CI must check `rollout status` exit code and undo.",
            "Rolling back the image does not roll back ConfigMaps or database migrations.",
        ],
        interview=[
            qa("basic", "RollingUpdate vs Recreate?", "RollingUpdate replaces pods gradually so the service stays up but two versions run concurrently. Recreate deletes all old pods first, causing downtime but guaranteeing no version overlap."),
            qa("intermediate", "How do you make a CI pipeline fail on a bad rollout?", "Run `kubectl rollout status deploy/x --timeout=...`, which exits non-zero when progressDeadlineSeconds is exceeded or the timeout hits. On failure run `kubectl rollout undo` and alert."),
            qa("intermediate", "What does minReadySeconds do?", "A new pod must stay Ready without any container crashing for that many seconds before it counts as available. It slows the rollout slightly but catches versions that crash shortly after startup."),
            qa("advanced", "With replicas 10, maxSurge 25% and maxUnavailable 25%, what are the bounds during a rollout?", "maxSurge rounds up to 3, so at most 13 pods exist; maxUnavailable rounds down to 2, so at least 8 must be available. The controller alternates scaling the new ReplicaSet up and the old one down within those limits."),
        ],
        related=["deployments", "probes", "pdb"],
        flow=chain(
            ("New image", "template change", "Rollout triggered", "set image changes spec.template, creating revision N+1."),
            ("New RS", "scale up +1", "Surge pod added", "The new ReplicaSet gets one extra pod within maxSurge.", "rev N+1"),
            ("Readiness", "minReadySeconds", "Pod becomes available", "The pod passes readiness and stays ready for minReadySeconds.", "probe"),
            ("Old RS", "scale down -1", "Old pod removed", "Only then is an old pod terminated, honouring maxUnavailable.", "ready"),
            ("Complete", "or undo", "Rollout finished", "Repeat until the old RS is at 0; `rollout undo` reverses if needed.", "done"),
        ),
    ),
    topic(
        id="blue-green-canary",
        title="Blue-Green & Canary Releases",
        category="reliability",
        level="advanced",
        code="BG",
        tagline="Release to a slice of traffic or a parallel stack before committing.",
        analogy="Blue-green is building a second bridge and switching all traffic at once; canary is letting a few cars over the new bridge first and watching for cracks.",
        what=(
            "Blue-green runs two complete versions side by side and switches traffic atomically, typically by changing a Service selector or "
            "Gateway backend, giving instant rollback at the cost of double capacity. Canary sends a small percentage of real traffic to the new "
            "version, analyses error rate and latency, then increases the weight step by step. Plain Kubernetes can approximate canary by "
            "replica ratio, but precise percentages and header-based routing need Gateway API weights, an ingress controller or a service mesh. "
            "Progressive delivery controllers like Argo Rollouts and Flagger automate the steps and query Prometheus to promote or abort. "
            "Both strategies require the database and APIs to tolerate two versions at once, so plan expand-and-contract migrations."
        ),
        use_cases=[
            "Risky releases where you want real-traffic validation on 5% of users first.",
            "Instant rollback requirement for payment or checkout services (blue-green).",
            "Testing a new version internally via a header such as x-canary: true.",
        ],
        key_points=[
            "Replica-ratio canary is coarse: 1 of 10 pods is roughly 10%, and only if load balancing is even.",
            "Gateway API HTTPRoute backendRefs weights give exact percentages independent of replica counts.",
            "Automated analysis should compare canary vs baseline metrics, not absolute thresholds only.",
            "Keep blue running until green is proven, then scale it down to save cost.",
        ],
        examples=[
            {
                "title": "Weighted canary with Gateway API",
                "level": "advanced",
                "description": "90/10 split between two Services; adjust weights to promote.",
                "yaml": y("""
                    apiVersion: gateway.networking.k8s.io/v1
                    kind: HTTPRoute
                    metadata:
                      name: shop
                    spec:
                      parentRefs:
                        - name: public-gw
                      hostnames: ["shop.example.com"]
                      rules:
                        - matches:
                            - headers:
                                - name: x-canary
                                  value: "true"
                          backendRefs:
                            - name: shop-v2
                              port: 80
                        - backendRefs:
                            - name: shop-v1
                              port: 80
                              weight: 90
                            - name: shop-v2
                              port: 80
                              weight: 10
                """),
            },
            {
                "title": "Blue-green switch via Service selector",
                "level": "intermediate",
                "description": "Both Deployments run; changing version: blue to green flips all traffic at once.",
                "yaml": y("""
                    apiVersion: v1
                    kind: Service
                    metadata:
                      name: checkout
                    spec:
                      selector:
                        app: checkout
                        version: green
                      ports:
                        - port: 80
                          targetPort: 8080
                """),
            },
            {
                "title": "Argo Rollouts canary steps",
                "level": "advanced",
                "description": "Automated progression with pauses; the controller manages ReplicaSets for you.",
                "yaml": y("""
                    apiVersion: argoproj.io/v1alpha1
                    kind: Rollout
                    metadata:
                      name: shop
                    spec:
                      replicas: 10
                      selector:
                        matchLabels:
                          app: shop
                      strategy:
                        canary:
                          steps:
                            - setWeight: 10
                            - pause: {duration: 5m}
                            - setWeight: 50
                            - pause: {duration: 10m}
                      template:
                        metadata:
                          labels:
                            app: shop
                        spec:
                          containers:
                            - name: shop
                              image: ghcr.io/example/shop:3.0.0
                """),
            },
        ],
        commands=[
            "kubectl patch svc checkout -p '{\"spec\":{\"selector\":{\"app\":\"checkout\",\"version\":\"green\"}}}'",
            "kubectl get endpointslices -l kubernetes.io/service-name=checkout",
            "kubectl argo rollouts get rollout shop --watch",
            "kubectl argo rollouts promote shop",
            "kubectl argo rollouts abort shop",
        ],
        gotchas=[
            "Long-lived connections (gRPC, WebSockets) stick to old pods, so weight changes take effect slowly.",
            "Session stickiness can send a user back and forth between versions unless routing is sticky.",
            "Blue-green doubles resource usage during the switch window; make sure quota and nodes allow it.",
        ],
        interview=[
            qa("intermediate", "Blue-green vs canary: when do you pick each?", "Blue-green when you need an atomic switch and instant rollback and can afford double capacity. Canary when you want to limit blast radius and validate with real traffic gradually, accepting more complex routing and observability needs."),
            qa("intermediate", "Why is a replica-based canary imprecise?", "The split depends on pod counts and kube-proxy's per-connection balancing, so 1 of 10 pods is only roughly 10% and long connections skew it. Weighted routing at L7 (Gateway API, mesh) decouples traffic share from replicas."),
            qa("advanced", "How does automated canary analysis work in Argo Rollouts or Flagger?", "At each step an analysis template queries metrics (e.g. Prometheus success rate, p99 latency) for the canary. If results stay within thresholds the weight is increased; failures abort the rollout and shift all traffic back to stable."),
            qa("advanced", "What database concerns arise with both strategies?", "Both run two app versions against the same database, so schema changes must be backward compatible. Use expand-and-contract: add new columns first, deploy code that writes both, migrate, then remove old columns in a later release."),
        ],
        related=["deployments", "services", "ingress"],
        flow=chain(
            ("Stable v1", "100% traffic", "Baseline", "All users hit v1 through the route."),
            ("Deploy v2", "0% traffic", "Canary launched", "v2 pods start and become ready but receive no traffic.", "deploy"),
            ("Shift 10%", "weighted route", "Canary exposed", "The HTTPRoute sends 10% of requests to v2.", "10%"),
            ("Analyse", "errors, latency", "Metrics compared", "Prometheus queries compare v2 against v1.", "metrics"),
            ("Promote", "or abort", "Decision", "Healthy: increase to 100%. Unhealthy: route everything back to v1.", "pass"),
        ),
    ),
    # ------------------------------------------------------------------ workloads
    topic(
        id="cronjobs",
        title="CronJobs",
        category="workloads",
        level="basic",
        code="CJ",
        tagline="Run Jobs on a cron schedule with concurrency and history control.",
        analogy="A CronJob is an alarm clock that, when it rings, hands a task card (a Job) to a worker and keeps the last few completed cards for reference.",
        what=(
            "A CronJob creates a Job object on a cron schedule such as '0 2 * * *'. The cronjob controller checks schedules, creates Jobs named "
            "with a timestamp suffix, and the Job controller then runs pods to completion. concurrencyPolicy decides what happens if a previous "
            "run is still active: Allow, Forbid (skip) or Replace (kill the old one). startingDeadlineSeconds limits how late a missed run may "
            "still start, and timeZone lets you schedule in a named zone instead of the controller's local time. successfulJobsHistoryLimit and "
            "failedJobsHistoryLimit keep a bounded number of finished Jobs for inspection. Your workload must be idempotent, because a schedule "
            "can occasionally fire twice or be missed during control plane outages."
        ),
        use_cases=[
            "Nightly database backups or report generation.",
            "Periodic cache warmup or cleanup of expired records.",
            "Certificate or token rotation tasks that run hourly.",
        ],
        key_points=[
            "Schedule uses standard 5-field cron syntax plus macros like @hourly.",
            "concurrencyPolicy: Forbid is the safe default for jobs that must not overlap.",
            "If more than 100 schedules are missed, the controller stops and logs an error unless startingDeadlineSeconds is set.",
            "spec.suspend: true pauses future runs without deleting history.",
            "Job-level backoffLimit and activeDeadlineSeconds still apply to each run.",
        ],
        examples=[
            {
                "title": "Nightly backup CronJob",
                "level": "basic",
                "description": "Runs at 02:00 Kolkata time, never overlaps, retries twice and keeps short history.",
                "yaml": y("""
                    apiVersion: batch/v1
                    kind: CronJob
                    metadata:
                      name: db-backup
                    spec:
                      schedule: "0 2 * * *"
                      timeZone: Asia/Kolkata
                      concurrencyPolicy: Forbid
                      startingDeadlineSeconds: 600
                      successfulJobsHistoryLimit: 3
                      failedJobsHistoryLimit: 5
                      jobTemplate:
                        spec:
                          backoffLimit: 2
                          activeDeadlineSeconds: 3600
                          template:
                            spec:
                              restartPolicy: OnFailure
                              containers:
                                - name: backup
                                  image: ghcr.io/example/pg-backup:1.2.0
                                  envFrom:
                                    - secretRef:
                                        name: db-backup-credentials
                """),
            },
            {
                "title": "Suspended cleanup job",
                "level": "intermediate",
                "description": "Paused during a maintenance window; unsuspend with kubectl patch.",
                "yaml": y("""
                    apiVersion: batch/v1
                    kind: CronJob
                    metadata:
                      name: cleanup
                    spec:
                      schedule: "*/15 * * * *"
                      suspend: true
                      concurrencyPolicy: Replace
                      jobTemplate:
                        spec:
                          ttlSecondsAfterFinished: 3600
                          template:
                            spec:
                              restartPolicy: Never
                              containers:
                                - name: cleanup
                                  image: busybox:1.36
                                  command: ["sh", "-c", "echo cleaning && sleep 5"]
                """),
            },
        ],
        commands=[
            "kubectl create cronjob hello --image=busybox:1.36 --schedule='*/5 * * * *' -- echo hi",
            "kubectl get cronjobs",
            "kubectl create job manual-run --from=cronjob/db-backup",
            "kubectl patch cronjob cleanup -p '{\"spec\":{\"suspend\":false}}'",
            "kubectl get jobs --sort-by=.metadata.creationTimestamp",
        ],
        gotchas=[
            "Jobs can run twice or be skipped in rare cases; make the work idempotent.",
            "Without timeZone the schedule uses the kube-controller-manager's time zone, usually UTC.",
            "Overlapping runs with concurrencyPolicy: Allow can pile up and exhaust quota.",
        ],
        interview=[
            qa("basic", "How do you trigger a CronJob immediately for testing?", "`kubectl create job <name> --from=cronjob/<cronjob>` creates a one-off Job from the CronJob's jobTemplate without waiting for the schedule."),
            qa("intermediate", "Explain the three concurrencyPolicy values.", "Allow lets runs overlap; Forbid skips the new run while the previous one is active; Replace terminates the running Job and starts the new one. Forbid suits backups, Replace suits jobs where only the latest result matters."),
            qa("intermediate", "What is startingDeadlineSeconds for?", "It defines how late after the scheduled time a run may still start, for example after a controller outage. Runs missing the deadline are counted as missed, and setting it also avoids the 'too many missed start times' stop condition."),
            qa("advanced", "How do you clean up finished Jobs and pods?", "Use successfulJobsHistoryLimit and failedJobsHistoryLimit on the CronJob, and ttlSecondsAfterFinished on the Job template so the TTL controller deletes Jobs and their pods after completion."),
        ],
        related=["jobs", "secrets", "resources-qos"],
        flow=chain(
            ("Schedule", "0 2 * * *", "Time arrives", "The cronjob controller sees that a scheduled time has passed."),
            ("Policy", "concurrency", "Overlap checked", "Forbid skips if the previous Job is still active.", "tick"),
            ("Job", "db-backup-28..", "Job created", "A Job is created from jobTemplate with a timestamp suffix.", "create"),
            ("Pod", "runs to end", "Work executes", "The Job controller runs the pod, retrying up to backoffLimit.", "pod"),
            ("History", "keep last 3", "Cleanup", "Old Jobs beyond history limits are deleted.", "done"),
        ),
    ),
    # ------------------------------------------------------------------ scheduling
    topic(
        id="priority-preemption",
        title="Priority Classes & Preemption",
        category="scheduling",
        level="intermediate",
        code="PP",
        tagline="Important pods jump the queue and can evict less important ones.",
        analogy="A hospital emergency room: a critical patient is seen first, and if every bed is taken, a patient with a minor issue is moved out to make room.",
        what=(
            "A PriorityClass maps a name to an integer value; pods reference it via priorityClassName and receive that priority. The scheduler "
            "orders its queue by priority, so higher-priority pending pods are scheduled first. If no node fits, the scheduler looks for a node "
            "where evicting lower-priority pods would make room and preempts them, respecting PodDisruptionBudgets on a best-effort basis and "
            "their graceful termination period. preemptionPolicy: Never gives a pod queue priority without the right to evict others. The kubelet "
            "also uses priority when evicting pods under node pressure. Built-in classes system-cluster-critical and system-node-critical are "
            "reserved for components like CoreDNS and CNI agents."
        ),
        use_cases=[
            "Guaranteeing production APIs win over batch jobs when the cluster is full.",
            "Overprovisioning: low-priority placeholder pods reserve headroom and are preempted instantly by real workloads.",
            "Protecting cluster add-ons (DNS, CNI, log agents) from eviction.",
        ],
        key_points=[
            "Higher value means higher priority; user classes should stay below 1,000,000,000.",
            "Only one PriorityClass may have globalDefault: true; pods without a class get 0 otherwise.",
            "Preemption can violate PDBs if nothing else fits; PDBs are respected only best-effort.",
            "ResourceQuota can scope quotas per priority class to stop teams abusing high priority.",
        ],
        examples=[
            {
                "title": "Production and batch priority classes",
                "level": "intermediate",
                "description": "Batch jobs are queued behind prod and never evict anything themselves.",
                "yaml": y("""
                    apiVersion: scheduling.k8s.io/v1
                    kind: PriorityClass
                    metadata:
                      name: prod-high
                    value: 100000
                    globalDefault: false
                    description: Customer-facing services.
                    ---
                    apiVersion: scheduling.k8s.io/v1
                    kind: PriorityClass
                    metadata:
                      name: batch-low
                    value: 1000
                    preemptionPolicy: Never
                    description: Batch work; queued but never preempts.
                """),
            },
            {
                "title": "Overprovisioning placeholder pods",
                "level": "advanced",
                "description": "Pause pods with negative priority hold spare capacity; real pods preempt them and the autoscaler adds nodes for the evicted placeholders.",
                "yaml": y("""
                    apiVersion: scheduling.k8s.io/v1
                    kind: PriorityClass
                    metadata:
                      name: overprovisioning
                    value: -10
                    description: Placeholder pods.
                    ---
                    apiVersion: apps/v1
                    kind: Deployment
                    metadata:
                      name: capacity-reservation
                    spec:
                      replicas: 2
                      selector:
                        matchLabels:
                          app: capacity-reservation
                      template:
                        metadata:
                          labels:
                            app: capacity-reservation
                        spec:
                          priorityClassName: overprovisioning
                          terminationGracePeriodSeconds: 0
                          containers:
                            - name: pause
                              image: registry.k8s.io/pause:3.10
                              resources:
                                requests:
                                  cpu: "1"
                                  memory: 2Gi
                """),
            },
        ],
        commands=[
            "kubectl get priorityclasses",
            "kubectl get pods -A -o custom-columns=NAME:.metadata.name,PRIO:.spec.priority",
            "kubectl get events --field-selector reason=Preempted -A",
            "kubectl describe pod <pending-pod> | grep -i nominated",
        ],
        gotchas=[
            "Giving every team a high class makes priority meaningless; restrict usage with quota scopes or admission policy.",
            "Preempted pods get their full grace period, so the high-priority pod may wait a while.",
            "Priority does not affect CPU scheduling inside a node; that is governed by requests and QoS.",
        ],
        interview=[
            qa("basic", "What is a PriorityClass?", "A cluster-scoped object mapping a name to an integer priority. Pods reference it by name and the admission controller resolves it into spec.priority, which the scheduler uses for queue ordering and preemption."),
            qa("intermediate", "How does preemption choose victims?", "The scheduler finds nodes where removing lower-priority pods would let the pending pod fit, prefers nodes with the fewest PDB violations, lowest victim priorities and fewest victims, then evicts them gracefully and sets nominatedNodeName on the pending pod."),
            qa("intermediate", "What does preemptionPolicy: Never do?", "The pod is placed ahead of lower-priority pods in the scheduling queue but will never evict other pods to make room; it waits until capacity frees up naturally."),
            qa("advanced", "How do priority classes enable fast scale-up with the cluster autoscaler?", "Negative-priority placeholder pods reserve capacity. When real pods arrive they preempt placeholders immediately, then the placeholders become Pending, which triggers the autoscaler to add nodes in the background."),
        ],
        related=["resources-qos", "pdb", "taints-tolerations"],
        flow=chain(
            ("Pending pod", "prio 100000", "High-priority arrives", "A prod pod is created and enters the front of the scheduling queue."),
            ("Filter", "no node fits", "No free capacity", "All nodes are full; normal scheduling fails.", "queue"),
            ("Pick victims", "lowest priority", "Preemption plan", "The scheduler finds a node where evicting batch pods would free enough room.", "0 fit"),
            ("Evict", "graceful stop", "Victims terminated", "Lower-priority pods are evicted with their grace period.", "preempt"),
            ("Bind", "nominated node", "Pod scheduled", "The high-priority pod binds to the freed node.", "fits"),
        ),
    ),
    # ------------------------------------------------------------------ scaling
    topic(
        id="cluster-autoscaler",
        title="Cluster Autoscaler & Karpenter",
        category="scaling",
        level="advanced",
        code="CL",
        tagline="Add nodes when pods cannot schedule, remove them when they sit idle.",
        analogy="A car-park attendant who opens a new level the moment cars queue at the gate, and closes empty levels at night to save electricity.",
        what=(
            "HPA adds pods, but pods need nodes. Cluster Autoscaler watches for pods that are Pending due to insufficient resources, simulates "
            "scheduling against configured node groups (cloud auto scaling groups) and increases the group that would fit them. It also scales "
            "down nodes whose pods can all be moved elsewhere and whose utilisation is below a threshold for a period, respecting PDBs and "
            "safe-to-evict annotations. Karpenter takes a different approach: instead of fixed node groups it provisions right-sized instances "
            "directly from NodePool constraints (instance families, zones, spot or on-demand) and actively consolidates underused nodes. Both "
            "decide based on pod resource requests, never actual usage, so accurate requests are essential. Scale-up typically takes one to "
            "several minutes because a VM must boot and join the cluster."
        ),
        use_cases=[
            "Elastic clusters that grow for daytime traffic and shrink overnight.",
            "Mixing spot and on-demand capacity for cost savings with Karpenter.",
            "Batch platforms where large jobs need dozens of nodes for an hour.",
        ],
        key_points=[
            "Triggers on unschedulable pods, not CPU usage; HPA plus autoscaler work together.",
            "Pods with restrictive PDBs, local storage or the safe-to-evict: false annotation block scale-down.",
            "Karpenter NodePools define requirements; consolidation replaces or removes underused nodes.",
            "Set expanders (least-waste, priority) in Cluster Autoscaler to choose among node groups.",
            "Overprovisioning with placeholder pods hides node boot latency.",
        ],
        examples=[
            {
                "title": "Karpenter NodePool with spot and consolidation",
                "level": "advanced",
                "description": "Lets Karpenter pick arm64 or amd64 spot/on-demand instances and consolidate when underutilised.",
                "yaml": y("""
                    apiVersion: karpenter.sh/v1
                    kind: NodePool
                    metadata:
                      name: general
                    spec:
                      template:
                        spec:
                          requirements:
                            - key: karpenter.sh/capacity-type
                              operator: In
                              values: ["spot", "on-demand"]
                            - key: kubernetes.io/arch
                              operator: In
                              values: ["amd64", "arm64"]
                          nodeClassRef:
                            group: karpenter.k8s.aws
                            kind: EC2NodeClass
                            name: default
                      limits:
                        cpu: "200"
                      disruption:
                        consolidationPolicy: WhenEmptyOrUnderutilized
                        consolidateAfter: 5m
                """),
            },
            {
                "title": "Opting a pod out of scale-down",
                "level": "intermediate",
                "description": "Cluster Autoscaler will not remove the node running this pod.",
                "yaml": y("""
                    apiVersion: v1
                    kind: Pod
                    metadata:
                      name: long-training
                      annotations:
                        cluster-autoscaler.kubernetes.io/safe-to-evict: "false"
                        karpenter.sh/do-not-disrupt: "true"
                    spec:
                      containers:
                        - name: train
                          image: ghcr.io/example/trainer:0.4.0
                          resources:
                            requests:
                              cpu: "4"
                              memory: 16Gi
                """),
            },
        ],
        commands=[
            "kubectl get pods -A --field-selector=status.phase=Pending",
            "kubectl -n kube-system logs deploy/cluster-autoscaler | grep -i scale",
            "kubectl get configmap cluster-autoscaler-status -n kube-system -o yaml",
            "kubectl get nodepools,nodeclaims",
            "kubectl describe node <node> | grep -A5 Allocated",
        ],
        gotchas=[
            "Pods without requests look free to the autoscaler, so nodes are packed until they fall over.",
            "A single-replica app with a minAvailable: 1 PDB pins its node forever.",
            "Node groups spanning multiple zones can fail to scale for zonal PVs; use one group per zone or Karpenter.",
        ],
        interview=[
            qa("basic", "How do HPA and Cluster Autoscaler interact?", "HPA increases replicas based on metrics; if new pods cannot fit they go Pending, which triggers the Cluster Autoscaler to add nodes. On scale-down HPA removes pods and the autoscaler later removes empty or underutilised nodes."),
            qa("intermediate", "Why might the Cluster Autoscaler refuse to remove an underutilised node?", "Pods on it cannot be moved: they have local storage, the safe-to-evict false annotation, restrictive PDBs, no controller, node affinity that no other node satisfies, or they are kube-system pods without a PDB."),
            qa("advanced", "How does Karpenter differ from Cluster Autoscaler?", "Cluster Autoscaler scales predefined node groups with fixed instance types. Karpenter reads pending pods' requirements and launches the cheapest fitting instance types directly, binds pods quickly, and continuously consolidates nodes by deleting or replacing them with cheaper ones."),
            qa("advanced", "How would you reduce scale-up latency for spiky workloads?", "Run low-priority overprovisioning pods that hold headroom, use faster-booting images and instance types, keep a warm minimum, and scale on leading indicators (queue length via KEDA) rather than CPU."),
        ],
        related=["hpa", "pdb", "resources-qos", "priority-preemption"],
        flow=chain(
            ("HPA", "more replicas", "Pods requested", "HPA raises replicas from 4 to 10 under load."),
            ("Pending", "insufficient cpu", "Pods unschedulable", "Six new pods cannot fit and are marked Unschedulable.", "+6 pods"),
            ("Autoscaler", "simulate fit", "Node chosen", "The autoscaler simulates node groups or instance types that fit the requests.", "pending"),
            ("Cloud API", "launch VM", "Node provisioned", "A new instance boots and its kubelet registers the Node.", "scale up"),
            ("Scheduled", "pods run", "Pods placed", "The scheduler binds the pending pods to the new node.", "Ready"),
        ),
    ),
    topic(
        id="keda",
        title="KEDA Event-Driven Scaling",
        category="scaling",
        level="advanced",
        code="KE",
        tagline="Scale on queue length, lag or any external metric, including down to zero.",
        analogy="Instead of watching how sweaty the cashiers are (CPU), you count customers in the queue and open more tills before anyone waits.",
        what=(
            "KEDA (Kubernetes Event-Driven Autoscaling) is a CNCF project that extends the HPA with dozens of scalers: Kafka lag, RabbitMQ or SQS "
            "queue depth, Prometheus queries, cron windows, Redis lists and more. You create a ScaledObject targeting a Deployment; KEDA creates "
            "and manages an HPA for it and serves the external metrics through its metrics adapter. KEDA itself handles activation, scaling "
            "from zero to one when events appear and back to zero after a cooldown, which HPA alone cannot do. For run-to-completion work a "
            "ScaledJob spawns Jobs per batch of messages. Credentials for event sources are referenced through TriggerAuthentication objects that "
            "point at Secrets, pod identity or external secret stores, so no credentials live in the ScaledObject."
        ),
        use_cases=[
            "Queue workers that should scale with backlog and sleep at zero overnight.",
            "Kafka consumers scaled on consumer-group lag.",
            "Business-hours scaling with the cron scaler.",
        ],
        key_points=[
            "ScaledObject creates an HPA named keda-hpa-<name>; do not create another HPA for the same target.",
            "minReplicaCount: 0 enables scale-to-zero; activation thresholds decide when to wake up.",
            "Multiple triggers are combined: the highest computed replica count wins.",
            "Use TriggerAuthentication with workload identity instead of static credentials.",
        ],
        examples=[
            {
                "title": "Scale workers on RabbitMQ queue length",
                "level": "advanced",
                "description": "One replica per 20 messages, zero when idle; connection string comes from a Secret.",
                "yaml": y("""
                    apiVersion: keda.sh/v1alpha1
                    kind: TriggerAuthentication
                    metadata:
                      name: rabbitmq-auth
                    spec:
                      secretTargetRef:
                        - parameter: host
                          name: rabbitmq-conn
                          key: amqp-url
                    ---
                    apiVersion: keda.sh/v1alpha1
                    kind: ScaledObject
                    metadata:
                      name: orders-worker
                    spec:
                      scaleTargetRef:
                        name: orders-worker
                      minReplicaCount: 0
                      maxReplicaCount: 50
                      cooldownPeriod: 300
                      triggers:
                        - type: rabbitmq
                          metadata:
                            queueName: orders
                            mode: QueueLength
                            value: "20"
                            activationValue: "1"
                          authenticationRef:
                            name: rabbitmq-auth
                """),
            },
            {
                "title": "Business-hours plus Prometheus scaling",
                "level": "intermediate",
                "description": "At least 5 replicas 09:00-19:00 and more if request rate exceeds 100 rps per pod.",
                "yaml": y("""
                    apiVersion: keda.sh/v1alpha1
                    kind: ScaledObject
                    metadata:
                      name: web
                    spec:
                      scaleTargetRef:
                        name: web
                      minReplicaCount: 1
                      maxReplicaCount: 30
                      triggers:
                        - type: cron
                          metadata:
                            timezone: Asia/Kolkata
                            start: 0 9 * * *
                            end: 0 19 * * *
                            desiredReplicas: "5"
                        - type: prometheus
                          metadata:
                            serverAddress: http://prometheus.monitoring:9090
                            query: sum(rate(http_requests_total{app="web"}[2m]))
                            threshold: "100"
                """),
            },
        ],
        commands=[
            "helm install keda kedacore/keda -n keda --create-namespace",
            "kubectl get scaledobjects,scaledjobs -A",
            "kubectl get hpa keda-hpa-orders-worker -o yaml",
            "kubectl describe scaledobject orders-worker",
            "kubectl get --raw /apis/external.metrics.k8s.io/v1beta1",
        ],
        gotchas=[
            "Scale-from-zero adds cold-start latency; set minReplicaCount 1 for latency-sensitive services.",
            "Only one external metrics adapter can serve external.metrics.k8s.io; KEDA conflicts with prometheus-adapter for that API.",
            "Long-running message handlers can be killed on scale-down; use ScaledJob or a generous grace period.",
        ],
        interview=[
            qa("intermediate", "Why use KEDA instead of a plain HPA?", "HPA scales on CPU, memory or metrics you must expose via an adapter, and cannot scale to zero by default. KEDA ships ready-made scalers for event sources, exposes them as external metrics and handles 0-to-1 activation itself."),
            qa("intermediate", "How does KEDA relate to the HPA?", "KEDA creates and owns an HPA for each ScaledObject and feeds it external metrics; the HPA does 1-to-N scaling, while KEDA's operator handles activation and deactivation between 0 and 1."),
            qa("advanced", "ScaledObject vs ScaledJob?", "ScaledObject scales a long-running Deployment or StatefulSet. ScaledJob creates Kubernetes Jobs in proportion to pending events, so each job processes work to completion and is never interrupted by scale-down."),
            qa("advanced", "How should KEDA authenticate to cloud queues?", "Use TriggerAuthentication or ClusterTriggerAuthentication with pod identity (IRSA, Azure Workload Identity, GCP Workload Identity) or a secret store reference, rather than embedding access keys. This keeps credentials short-lived and out of manifests."),
        ],
        related=["hpa", "deployments", "jobs"],
        flow=chain(
            ("Event source", "queue: 400 msgs", "Backlog grows", "Messages pile up in the orders queue."),
            ("KEDA scaler", "polls source", "Metric read", "The RabbitMQ scaler reads queue length every polling interval.", "length"),
            ("Activate", "0 -> 1", "Wake from zero", "Above activationValue, KEDA scales the Deployment from 0 to 1.", "400"),
            ("HPA", "400 / 20 = 20", "Replicas computed", "The managed HPA computes 20 replicas from the external metric.", "metric"),
            ("Workers", "drain queue", "Backlog cleared", "Workers consume messages; after cooldown KEDA scales back to zero.", "scale"),
        ),
    ),
    # ------------------------------------------------------------------ config
    topic(
        id="quotas-limitranges",
        title="ResourceQuotas & LimitRanges",
        category="config",
        level="intermediate",
        code="RQ",
        tagline="Cap what a namespace can consume and give every container sane defaults.",
        analogy="A ResourceQuota is a department's annual budget; a LimitRange is the per-purchase policy saying what a single expense may cost and what is assumed if nobody fills in the amount.",
        what=(
            "A ResourceQuota limits aggregate consumption in a namespace: total CPU and memory requests and limits, storage, and object counts "
            "such as pods, Services of type LoadBalancer or Secrets. It is enforced at admission time, so a request that would exceed the quota is "
            "rejected with a 403. When a quota covers cpu or memory, every new pod must specify those values, which is where LimitRange helps: it "
            "injects default requests and limits into containers that omit them and enforces min, max and limit-to-request ratios per container, "
            "pod or PVC. Quotas can be scoped, for example by PriorityClass or to BestEffort pods only. Together they are the backbone of fair "
            "multi-tenant clusters and prevent one team from starving the rest."
        ),
        use_cases=[
            "Giving each team namespace a fixed CPU/memory budget.",
            "Ensuring no container is deployed without requests (defaults via LimitRange).",
            "Limiting expensive objects like LoadBalancer Services or large PVCs.",
        ],
        key_points=[
            "Quota is checked at admission; existing objects are not evicted if you lower the quota.",
            "If a quota tracks requests.cpu, pods without cpu requests are rejected unless a LimitRange sets defaults.",
            "LimitRange applies only to objects created after it exists.",
            "`kubectl describe quota` shows Used vs Hard per resource.",
            "Use count/<resource>.<group> syntax for object-count quotas, e.g. count/deployments.apps.",
        ],
        examples=[
            {
                "title": "Team namespace quota",
                "level": "intermediate",
                "description": "Caps compute, storage and object counts for the payments namespace.",
                "yaml": y("""
                    apiVersion: v1
                    kind: ResourceQuota
                    metadata:
                      name: team-budget
                      namespace: payments
                    spec:
                      hard:
                        requests.cpu: "20"
                        requests.memory: 40Gi
                        limits.memory: 60Gi
                        requests.storage: 500Gi
                        persistentvolumeclaims: "20"
                        pods: "100"
                        services.loadbalancers: "2"
                        count/deployments.apps: "30"
                """),
            },
            {
                "title": "Container defaults and bounds",
                "level": "basic",
                "description": "Containers without resources get defaults; anything above 4 CPU or 8Gi is rejected.",
                "yaml": y("""
                    apiVersion: v1
                    kind: LimitRange
                    metadata:
                      name: container-defaults
                      namespace: payments
                    spec:
                      limits:
                        - type: Container
                          defaultRequest:
                            cpu: 100m
                            memory: 128Mi
                          default:
                            memory: 256Mi
                          max:
                            cpu: "4"
                            memory: 8Gi
                          min:
                            cpu: 10m
                            memory: 32Mi
                        - type: PersistentVolumeClaim
                          max:
                            storage: 100Gi
                """),
            },
        ],
        commands=[
            "kubectl create quota team-budget --hard=requests.cpu=20,pods=100 -n payments",
            "kubectl describe quota -n payments",
            "kubectl get limitrange -n payments -o yaml",
            "kubectl describe limitrange container-defaults -n payments",
        ],
        gotchas=[
            "Quota errors surface on the ReplicaSet, not the Deployment: check `kubectl describe rs` events for 'exceeded quota'.",
            "Setting default CPU limits causes throttling; many teams set only CPU requests and memory limits.",
            "Quotas do not account for node overhead or DaemonSets in other namespaces.",
        ],
        interview=[
            qa("basic", "ResourceQuota vs LimitRange?", "ResourceQuota caps the namespace total (sum of requests, limits, object counts). LimitRange works per object: it sets defaults and min/max for each container, pod or PVC."),
            qa("intermediate", "A Deployment shows 0/3 ready and no pods exist. Quota is suspected. How do you confirm?", "Run `kubectl describe rs` for the Deployment's ReplicaSet; FailedCreate events will say 'exceeded quota' or 'must specify requests'. `kubectl describe quota` shows which resource is exhausted."),
            qa("intermediate", "What are quota scopes?", "Scopes restrict which pods a quota counts, e.g. Terminating, NotTerminating, BestEffort, NotBestEffort or a scopeSelector on PriorityClass. This lets you give a separate, smaller budget to high-priority pods."),
            qa("advanced", "How do you design quotas for a multi-tenant platform?", "One namespace per team with a ResourceQuota for compute, storage and object counts, a LimitRange for defaults, priority-class scoped quotas, and NetworkPolicy plus RBAC isolation. Monitor quota usage and provide a self-service process to raise limits."),
        ],
        related=["namespaces", "resources-qos", "priority-preemption"],
        flow=chain(
            ("Pod create", "no resources", "Request arrives", "A developer creates a pod without CPU or memory requests."),
            ("LimitRange", "inject defaults", "Defaults applied", "LimitRange admission sets requests 100m/128Mi and a memory limit.", "spec"),
            ("Bounds", "min / max", "Bounds checked", "Values are validated against min, max and ratio rules.", "defaults"),
            ("Quota", "used + new", "Budget checked", "ResourceQuota admission adds the pod's requests to current usage.", "valid"),
            ("Admit/deny", "403 if over", "Decision", "Within budget the pod is stored; otherwise it is rejected with 'exceeded quota'.", "fits"),
        ),
    ),
    # ------------------------------------------------------------------ security
    topic(
        id="service-accounts",
        title="ServiceAccounts & Tokens",
        category="security",
        level="intermediate",
        code="SA",
        tagline="Workload identity: short-lived, audience-bound tokens for pods.",
        analogy="A ServiceAccount is a staff badge for a robot. Modern badges expire every hour and only open specific doors (audiences), so a stolen badge is quickly useless.",
        what=(
            "Every namespace has a default ServiceAccount, and every pod runs as one. The kubelet requests a token through the TokenRequest API and "
            "mounts it as a projected volume; the token is a JWT bound to the pod, signed by the API server, scoped to an audience and rotated "
            "before expiry (about an hour by default). The API server authenticates it as system:serviceaccount:<ns>:<name>, and RBAC decides what "
            "it may do. Since v1.24 Kubernetes no longer auto-creates long-lived token Secrets, which removed a major credential-leak risk. "
            "Cloud workload identity (IRSA, GKE and Azure Workload Identity) federates these tokens to cloud IAM so pods access cloud APIs without "
            "static keys. Pods that never call the API should disable token automounting entirely."
        ),
        use_cases=[
            "Giving a controller or CI runner precisely scoped API access.",
            "Accessing cloud services (S3, GCS, Key Vault) via workload identity without stored keys.",
            "Projecting a token with a custom audience for Vault or another service to verify.",
        ],
        key_points=[
            "Use one ServiceAccount per workload, never the default SA with extra RBAC.",
            "automountServiceAccountToken: false on SA or pod for workloads that do not call the API.",
            "Projected tokens are bound to the pod: deleting the pod invalidates the token.",
            "`kubectl create token <sa>` issues a short-lived token for testing.",
            "Avoid legacy kubernetes.io/service-account-token Secrets; they never expire.",
        ],
        examples=[
            {
                "title": "Dedicated SA with token automount disabled",
                "level": "basic",
                "description": "The web pod has no API token at all.",
                "yaml": y("""
                    apiVersion: v1
                    kind: ServiceAccount
                    metadata:
                      name: web
                    automountServiceAccountToken: false
                    ---
                    apiVersion: v1
                    kind: Pod
                    metadata:
                      name: web
                    spec:
                      serviceAccountName: web
                      containers:
                        - name: web
                          image: nginx:1.27-alpine
                """),
            },
            {
                "title": "Projected token with custom audience",
                "level": "advanced",
                "description": "A 10-minute token for Vault; the kubelet refreshes it automatically.",
                "yaml": y("""
                    apiVersion: v1
                    kind: Pod
                    metadata:
                      name: vault-client
                    spec:
                      serviceAccountName: payments-api
                      automountServiceAccountToken: false
                      containers:
                        - name: app
                          image: ghcr.io/example/payments:1.0.0
                          volumeMounts:
                            - name: vault-token
                              mountPath: /var/run/secrets/vault
                              readOnly: true
                      volumes:
                        - name: vault-token
                          projected:
                            sources:
                              - serviceAccountToken:
                                  audience: vault
                                  expirationSeconds: 600
                                  path: token
                """),
            },
        ],
        commands=[
            "kubectl create serviceaccount ci-bot -n ci",
            "kubectl create token ci-bot -n ci --duration=10m --audience=kubernetes",
            "kubectl auth can-i --list --as=system:serviceaccount:ci:ci-bot -n ci",
            "kubectl get pod web -o jsonpath='{.spec.serviceAccountName}'",
        ],
        gotchas=[
            "Anyone who can create pods in a namespace can run as any ServiceAccount in it.",
            "Clients that cache the token file forever break after rotation; re-read it periodically (client-go does).",
            "Binding RBAC to the default ServiceAccount silently grants it to every pod in the namespace.",
        ],
        interview=[
            qa("basic", "What is a ServiceAccount?", "A namespaced identity for processes in pods. Pods get a token for it, the API server authenticates the token as system:serviceaccount:<ns>:<name>, and RBAC grants it permissions."),
            qa("intermediate", "What changed with bound service account tokens?", "Tokens are now obtained via the TokenRequest API, are time-limited, audience-scoped and bound to the pod object, and are projected into pods and auto-rotated. Long-lived Secret-based tokens are no longer created automatically."),
            qa("intermediate", "How do pods access cloud APIs without static keys?", "Workload identity federation: the cloud IAM trusts the cluster's OIDC issuer, and a ServiceAccount is mapped to a cloud role. The SDK exchanges the projected SA token for short-lived cloud credentials."),
            qa("advanced", "How would you harden ServiceAccount usage cluster-wide?", "Disable automount by default, one SA per workload with minimal RBAC, forbid binding roles to default SAs via policy, audit with `kubectl auth can-i --list`, delete legacy token Secrets, and restrict who can create pods or impersonate SAs."),
        ],
        related=["rbac", "secrets", "pods"],
        flow=chain(
            ("Pod", "serviceAccount", "Pod scheduled", "The pod references serviceAccountName: payments-api."),
            ("kubelet", "TokenRequest", "Token requested", "kubelet asks the API server for a pod-bound token with an audience.", "request"),
            ("API server", "signs JWT", "Token issued", "A JWT valid for about an hour is signed and returned.", "JWT"),
            ("Projected", "volume mount", "Token mounted", "The token is written to a projected volume and refreshed before expiry.", "token"),
            ("API call", "RBAC check", "Request authorized", "The app sends the token; RBAC decides what the SA may do.", "Bearer"),
        ),
    ),
    topic(
        id="pod-security",
        title="Pod Security Standards & securityContext",
        category="security",
        level="intermediate",
        code="PS",
        tagline="Run containers as non-root, read-only and with no extra privileges.",
        analogy="securityContext is the set of house rules for one guest (no keys to the master bedroom); Pod Security Admission is the building rule that refuses entry to anyone who will not sign them.",
        what=(
            "A container's securityContext controls Linux security features: runAsNonRoot and runAsUser, readOnlyRootFilesystem, "
            "allowPrivilegeEscalation, dropped capabilities, seccomp and AppArmor profiles. Pod Security Standards define three levels: privileged "
            "(unrestricted), baseline (blocks known privilege escalations such as hostPath, hostNetwork and privileged containers) and restricted "
            "(current hardening best practice). The built-in Pod Security Admission controller enforces these levels per namespace through labels, "
            "in enforce, audit or warn mode, and replaced the removed PodSecurityPolicy. For finer-grained or custom rules teams add Kyverno, "
            "Gatekeeper or ValidatingAdmissionPolicy. Hardened pods drastically limit what an attacker gains from an application compromise."
        ),
        use_cases=[
            "Enforcing restricted level on all application namespaces.",
            "Running apps with a read-only root filesystem and writable emptyDir only for /tmp.",
            "Rolling out stricter policy safely using warn and audit modes first.",
        ],
        key_points=[
            "Namespace labels: pod-security.kubernetes.io/enforce, audit and warn, each with a level and version.",
            "Restricted requires runAsNonRoot, allowPrivilegeEscalation false, drop ALL capabilities and a RuntimeDefault or Localhost seccomp profile.",
            "Pod-level securityContext sets defaults; container-level fields override them.",
            "fsGroup changes group ownership of mounted volumes so non-root users can write.",
            "PodSecurityPolicy was removed in v1.25.",
        ],
        examples=[
            {
                "title": "Namespace enforcing restricted",
                "level": "basic",
                "description": "Rejects non-compliant pods; also warns clients and records audit annotations.",
                "yaml": y("""
                    apiVersion: v1
                    kind: Namespace
                    metadata:
                      name: apps
                      labels:
                        pod-security.kubernetes.io/enforce: restricted
                        pod-security.kubernetes.io/enforce-version: latest
                        pod-security.kubernetes.io/warn: restricted
                        pod-security.kubernetes.io/audit: restricted
                """),
            },
            {
                "title": "Restricted-compliant Deployment",
                "level": "intermediate",
                "description": "Non-root, read-only root filesystem, no capabilities, RuntimeDefault seccomp.",
                "yaml": y("""
                    apiVersion: apps/v1
                    kind: Deployment
                    metadata:
                      name: api
                      namespace: apps
                    spec:
                      replicas: 2
                      selector:
                        matchLabels:
                          app: api
                      template:
                        metadata:
                          labels:
                            app: api
                        spec:
                          automountServiceAccountToken: false
                          securityContext:
                            runAsNonRoot: true
                            runAsUser: 10001
                            fsGroup: 10001
                            seccompProfile:
                              type: RuntimeDefault
                          containers:
                            - name: api
                              image: ghcr.io/example/api:2.4.1
                              securityContext:
                                allowPrivilegeEscalation: false
                                readOnlyRootFilesystem: true
                                capabilities:
                                  drop: ["ALL"]
                              volumeMounts:
                                - name: tmp
                                  mountPath: /tmp
                          volumes:
                            - name: tmp
                              emptyDir: {}
                """),
            },
        ],
        commands=[
            "kubectl label ns apps pod-security.kubernetes.io/enforce=restricted --overwrite",
            "kubectl label --dry-run=server --overwrite ns apps pod-security.kubernetes.io/enforce=restricted",
            "kubectl get ns -L pod-security.kubernetes.io/enforce",
            "kubectl exec deploy/api -- id",
        ],
        gotchas=[
            "Pod Security Admission checks pods, but warnings for Deployments appear only in warn mode; enforce failures show up as ReplicaSet events.",
            "Images that write to their own filesystem break with readOnlyRootFilesystem; mount emptyDir where needed.",
            "runAsNonRoot fails at start if the image's user is root and no runAsUser is set.",
        ],
        interview=[
            qa("basic", "What are the three Pod Security Standards levels?", "Privileged has no restrictions, baseline prevents known privilege escalations such as privileged containers, hostPath and host namespaces, and restricted adds hardening like non-root, dropped capabilities and seccomp."),
            qa("intermediate", "How do you roll out restricted enforcement without breaking teams?", "Label namespaces with warn and audit at restricted first and use `kubectl label --dry-run=server` to list violating pods. Fix workloads, then switch enforce to restricted, pinning enforce-version to avoid surprise changes on upgrade."),
            qa("intermediate", "Why is allowPrivilegeEscalation: false important?", "It sets the no_new_privs flag so setuid binaries and file capabilities cannot grant a process more privileges than its parent, blocking a common escalation path inside the container."),
            qa("advanced", "Pod Security Admission vs Kyverno/Gatekeeper?", "PSA is built-in, zero-maintenance and covers only the fixed PSS levels per namespace. Policy engines support custom rules (image registries, labels, resource requirements), mutation, exceptions and reporting, so many clusters use PSA as a baseline plus a policy engine for the rest."),
        ],
        related=["rbac", "namespaces", "pods"],
        flow=chain(
            ("Pod spec", "securityContext", "Pod submitted", "A Deployment's ReplicaSet creates a pod in namespace apps."),
            ("Namespace", "enforce=restrict", "Level looked up", "Pod Security Admission reads the namespace labels.", "create"),
            ("Evaluate", "checks per field", "Fields checked", "runAsNonRoot, capabilities, seccomp, host namespaces and volumes are evaluated.", "restricted"),
            ("Admit/deny", "403 + reasons", "Decision", "Compliant pods are admitted; violations are rejected with a list of reasons.", "result"),
            ("Runtime", "no root, no caps", "Hardened container", "The runtime applies UID, capabilities and seccomp to the process.", "ok"),
        ),
    ),
    # ------------------------------------------------------------------ extending
    topic(
        id="admission-policy",
        title="Admission Webhooks & Policy Engines",
        category="extending",
        level="advanced",
        code="AD",
        tagline="Enforce custom rules on every object: Kyverno, Gatekeeper, ValidatingAdmissionPolicy.",
        analogy="Admission control is a customs checkpoint: one officer can stamp extra details on your form (mutate), another can refuse entry if something is missing (validate).",
        what=(
            "Admission controllers intercept API requests after authorization and before persistence. Besides built-in plugins, Kubernetes calls "
            "external MutatingAdmissionWebhooks and ValidatingAdmissionWebhooks over HTTPS, sending an AdmissionReview and receiving allow, deny "
            "or a JSON patch. Policy engines build on this: OPA Gatekeeper uses Rego-based ConstraintTemplates, while Kyverno writes policies as "
            "Kubernetes YAML and can validate, mutate, generate and verify image signatures. ValidatingAdmissionPolicy (GA in v1.30) runs CEL "
            "expressions inside the API server with no webhook to operate. Typical policies require resource requests, restrict image registries, "
            "forbid latest tags or enforce labels. Webhooks sit in the critical path, so availability, timeouts and failurePolicy matter as much as "
            "the rules themselves."
        ),
        use_cases=[
            "Only allowing images from the company registry.",
            "Requiring team and cost-center labels on every workload.",
            "Auto-injecting sidecars or default securityContext fields (mutation).",
        ],
        key_points=[
            "failurePolicy Fail is secure but can block the cluster if the webhook is down; Ignore is available but fails open.",
            "Exclude kube-system and the webhook's own namespace with namespaceSelector to avoid deadlocks.",
            "ValidatingAdmissionPolicy uses CEL in-process: no network hop, no extra deployment.",
            "Start policies in audit or warn mode, review reports, then enforce.",
            "Webhook TLS: the API server verifies the webhook's certificate against caBundle.",
        ],
        examples=[
            {
                "title": "ValidatingAdmissionPolicy with CEL",
                "level": "advanced",
                "description": "Rejects Deployments whose containers use images outside the approved registry.",
                "yaml": y("""
                    apiVersion: admissionregistration.k8s.io/v1
                    kind: ValidatingAdmissionPolicy
                    metadata:
                      name: approved-registry
                    spec:
                      failurePolicy: Fail
                      matchConstraints:
                        resourceRules:
                          - apiGroups: ["apps"]
                            apiVersions: ["v1"]
                            operations: ["CREATE", "UPDATE"]
                            resources: ["deployments"]
                      validations:
                        - expression: "object.spec.template.spec.containers.all(c, c.image.startsWith('registry.example.com/'))"
                          message: "images must come from registry.example.com"
                    ---
                    apiVersion: admissionregistration.k8s.io/v1
                    kind: ValidatingAdmissionPolicyBinding
                    metadata:
                      name: approved-registry
                    spec:
                      policyName: approved-registry
                      validationActions: ["Deny"]
                      matchResources:
                        namespaceSelector:
                          matchLabels:
                            policy: enforced
                """),
            },
            {
                "title": "Kyverno policy requiring requests and labels",
                "level": "intermediate",
                "description": "Audit mode first; switch validationFailureAction to Enforce after review.",
                "yaml": y("""
                    apiVersion: kyverno.io/v1
                    kind: ClusterPolicy
                    metadata:
                      name: require-requests-and-team
                    spec:
                      validationFailureAction: Audit
                      background: true
                      rules:
                        - name: require-team-label
                          match:
                            any:
                              - resources:
                                  kinds: ["Pod"]
                          validate:
                            message: "label 'team' is required"
                            pattern:
                              metadata:
                                labels:
                                  team: "?*"
                        - name: require-requests
                          match:
                            any:
                              - resources:
                                  kinds: ["Pod"]
                          validate:
                            message: "cpu and memory requests are required"
                            pattern:
                              spec:
                                containers:
                                  - resources:
                                      requests:
                                        cpu: "?*"
                                        memory: "?*"
                """),
            },
        ],
        commands=[
            "kubectl get validatingwebhookconfigurations,mutatingwebhookconfigurations",
            "kubectl get validatingadmissionpolicies,validatingadmissionpolicybindings",
            "kubectl get policyreports -A",
            "kubectl apply --dry-run=server -f deploy.yaml",
        ],
        gotchas=[
            "A webhook matching pods in its own namespace with failurePolicy Fail can never restart itself after an outage.",
            "Webhook latency adds to every matching API call; keep timeoutSeconds low (a few seconds).",
            "Mutating webhooks must be idempotent because they may be invoked more than once.",
        ],
        interview=[
            qa("intermediate", "Mutating vs validating webhooks?", "Mutating webhooks can change the object by returning a JSON patch, for example injecting a sidecar. Validating webhooks only allow or deny and run after all mutations, so they see the final object."),
            qa("intermediate", "What is ValidatingAdmissionPolicy and why use it?", "A built-in resource that evaluates CEL expressions inside the API server. It avoids running and securing a webhook service, has no network latency and cannot take the cluster down through webhook unavailability."),
            qa("advanced", "Trade-offs of failurePolicy Fail vs Ignore?", "Fail guarantees policies are never bypassed but turns webhook downtime into API downtime for matching resources. Ignore keeps the cluster usable but lets non-compliant objects in during outages; mitigate with HA webhooks, PDBs, namespace exclusions and background scans."),
            qa("advanced", "Gatekeeper vs Kyverno?", "Gatekeeper uses OPA and Rego through ConstraintTemplates and Constraints, powerful and portable but with a learning curve. Kyverno policies are Kubernetes-native YAML and also support mutation, resource generation and image signature verification, which many teams find easier."),
        ],
        related=["rbac", "namespaces", "pod-security"],
        flow=chain(
            ("Request", "create pod", "Request authorized", "An authorized request enters the admission phase."),
            ("Mutate", "webhook patch", "Defaults injected", "Mutating webhooks add labels, sidecars or securityContext.", "object"),
            ("Schema", "OpenAPI check", "Object validated", "The patched object is validated against its schema.", "patched"),
            ("Policy", "CEL / Kyverno", "Rules evaluated", "ValidatingAdmissionPolicy and validating webhooks evaluate the final object.", "valid"),
            ("Result", "allow or 403", "Decision", "Allowed objects are persisted; denied ones return the policy message.", "verdict"),
        ),
    ),
    topic(
        id="crds-operators",
        title="CRDs & Operators",
        category="extending",
        level="advanced",
        code="CR",
        tagline="Teach Kubernetes new resource types and automate their care with controllers.",
        analogy="A CRD adds a new form to the government office (say, 'Database Request'); an operator is the clerk trained to process that form: provisioning, backing up and upgrading the database.",
        what=(
            "A CustomResourceDefinition registers a new API type, such as PostgresCluster or Certificate, with an OpenAPI v3 schema, versions and "
            "optional status and scale subresources. After that, the API server stores and serves custom resources exactly like built-in objects, "
            "with RBAC, watches and kubectl support. On its own a CRD is just data; an operator is a controller that watches those resources and "
            "reconciles real infrastructure to match them, encoding operational knowledge such as failover, backups and upgrades. Operators are "
            "usually written with controller-runtime via Kubebuilder or Operator SDK and use finalizers to clean up external resources before "
            "deletion. CEL validation rules (x-kubernetes-validations) and conversion webhooks handle validation and multi-version APIs. Popular "
            "examples include cert-manager, Prometheus Operator, CloudNativePG and Strimzi."
        ),
        use_cases=[
            "Running databases or Kafka with self-healing failover and backups (CloudNativePG, Strimzi).",
            "Building an internal platform API, e.g. kind: Application that expands into Deployment, Service and Ingress.",
            "Managing cloud resources from Kubernetes (Crossplane, ACK).",
        ],
        key_points=[
            "CRD names must be <plural>.<group>; the schema is structural and required in apiextensions.k8s.io/v1.",
            "Enable the status subresource so spec and status are updated separately.",
            "Finalizers block deletion until the controller removes them after cleanup.",
            "Reconcile must be idempotent and level-based; requeue on transient errors.",
            "Deleting a CRD deletes every custom resource of that type.",
        ],
        examples=[
            {
                "title": "CRD with schema, CEL rule and status",
                "level": "advanced",
                "description": "Defines kind Backup with validation and printer columns.",
                "yaml": y("""
                    apiVersion: apiextensions.k8s.io/v1
                    kind: CustomResourceDefinition
                    metadata:
                      name: backups.ops.example.com
                    spec:
                      group: ops.example.com
                      scope: Namespaced
                      names:
                        plural: backups
                        singular: backup
                        kind: Backup
                        shortNames: ["bk"]
                      versions:
                        - name: v1
                          served: true
                          storage: true
                          subresources:
                            status: {}
                          additionalPrinterColumns:
                            - name: Schedule
                              type: string
                              jsonPath: .spec.schedule
                            - name: Phase
                              type: string
                              jsonPath: .status.phase
                          schema:
                            openAPIV3Schema:
                              type: object
                              properties:
                                spec:
                                  type: object
                                  required: ["database", "schedule"]
                                  x-kubernetes-validations:
                                    - rule: "self.retentionDays >= 1 && self.retentionDays <= 90"
                                      message: "retentionDays must be between 1 and 90"
                                  properties:
                                    database:
                                      type: string
                                    schedule:
                                      type: string
                                    retentionDays:
                                      type: integer
                                      default: 7
                                status:
                                  type: object
                                  properties:
                                    phase:
                                      type: string
                """),
            },
            {
                "title": "A custom resource instance",
                "level": "basic",
                "description": "Once the CRD exists, kubectl get backups works like any built-in type.",
                "yaml": y("""
                    apiVersion: ops.example.com/v1
                    kind: Backup
                    metadata:
                      name: orders-db-nightly
                      finalizers:
                        - ops.example.com/cleanup
                    spec:
                      database: orders-db
                      schedule: "0 1 * * *"
                      retentionDays: 14
                """),
            },
        ],
        commands=[
            "kubectl get crds",
            "kubectl explain backup.spec --recursive",
            "kubectl get backups -A",
            "kubebuilder create api --group ops --version v1 --kind Backup",
            "kubectl patch backup orders-db-nightly --type=merge -p '{\"metadata\":{\"finalizers\":null}}'",
        ],
        gotchas=[
            "Removing finalizers by hand skips cleanup and can leak external resources; fix the controller first.",
            "Uninstalling an operator's Helm chart may delete its CRDs and with them all user data objects.",
            "Changing the storage version requires migrating stored objects before dropping the old version.",
        ],
        interview=[
            qa("basic", "What is the difference between a CRD and an operator?", "A CRD extends the API with a new resource type and schema; it stores data but does nothing. An operator is a controller that watches those resources and reconciles real systems to match, embedding operational knowledge."),
            qa("intermediate", "What are finalizers used for?", "A finalizer is a string in metadata.finalizers that blocks deletion. The API server sets deletionTimestamp, the controller performs cleanup such as deleting a cloud resource, then removes the finalizer so the object can be deleted."),
            qa("intermediate", "Why enable the status subresource?", "It splits writes: users update spec through the main endpoint while the controller updates status through /status, so neither overwrites the other, and spec changes bump metadata.generation that controllers can compare with status.observedGeneration."),
            qa("advanced", "How do you design an idempotent reconcile loop?", "Read current state, compute desired children, create or patch them using server-side apply with owner references, update status with conditions and observedGeneration, and return requeue on errors. Never assume what happened last time; derive everything from current cluster and external state."),
        ],
        related=["rbac", "statefulsets", "admission-policy"],
        flow=chain(
            ("CRD", "kind: Backup", "Type registered", "The CRD adds /apis/ops.example.com/v1/backups to the API."),
            ("CR applied", "orders-db", "Desired state", "A user applies a Backup custom resource.", "kubectl"),
            ("Operator", "watch + diff", "Reconcile starts", "The operator's informer receives the event and compares desired with actual.", "event"),
            ("Act", "CronJob, bucket", "Resources created", "It creates a CronJob, storage bucket and credentials.", "create"),
            ("Status", "phase: Ready", "Status reported", "The operator writes conditions and observedGeneration to status.", "update"),
        ),
    ),
    # ------------------------------------------------------------------ operations
    topic(
        id="kubectl-power",
        title="kubectl Power Usage",
        category="operations",
        level="basic",
        code="KC",
        tagline="Contexts, output formats, selectors, dry-runs and diffs: work fast and safely.",
        analogy="kubectl is a universal remote. Most people only use the power button; learning the shortcuts (contexts, jsonpath, dry-run) turns it into a precision instrument.",
        what=(
            "kubectl is a REST client for the API server configured by kubeconfig files containing clusters, users and contexts. Contexts let you "
            "switch clusters and default namespaces safely, which matters when prod and dev live side by side. Output flags such as -o wide, "
            "-o yaml, -o jsonpath, custom-columns and --sort-by turn kubectl into a query tool, while label and field selectors filter results "
            "server-side. Generators with --dry-run=client -o yaml scaffold manifests, `kubectl diff` previews changes and --dry-run=server runs "
            "admission without persisting. Server-side apply tracks field ownership to avoid clobbering changes from other controllers. "
            "`kubectl explain` documents every field offline from the API schema, and plugins via krew extend kubectl further."
        ),
        use_cases=[
            "Quickly generating YAML skeletons instead of writing them from memory.",
            "Previewing a change against production with `kubectl diff` before applying.",
            "Extracting data for scripts with jsonpath or custom-columns.",
        ],
        key_points=[
            "KUBECONFIG can list multiple files separated by colons; kubectl merges them.",
            "`kubectl config set-context --current --namespace=x` changes the default namespace.",
            "--dry-run=client renders locally; --dry-run=server also runs validation and admission.",
            "Server-side apply: `kubectl apply --server-side --field-manager=ci`.",
            "-w (watch) streams changes; --v=6..9 shows HTTP requests for debugging.",
        ],
        examples=[
            {
                "title": "kubeconfig with SSO exec plugin",
                "level": "intermediate",
                "description": "No static token stored: kubectl calls an OIDC helper (kubelogin) to obtain a short-lived credential.",
                "yaml": y("""
                    apiVersion: v1
                    kind: Config
                    clusters:
                      - name: prod
                        cluster:
                          server: https://prod-api.example.com:6443
                          certificate-authority: /etc/kube/prod-ca.crt
                    users:
                      - name: sso-user
                        user:
                          exec:
                            apiVersion: client.authentication.k8s.io/v1
                            command: kubectl
                            args: ["oidc-login", "get-token", "--oidc-issuer-url=https://idp.example.com", "--oidc-client-id=kubernetes"]
                            interactiveMode: IfAvailable
                    contexts:
                      - name: prod-readonly
                        context:
                          cluster: prod
                          user: sso-user
                          namespace: payments
                    current-context: prod-readonly
                """),
            },
            {
                "title": "Scaffolded Deployment from a generator",
                "level": "basic",
                "description": "Output of `kubectl create deploy api --image=nginx:1.27-alpine --replicas=2 --dry-run=client -o yaml`, trimmed.",
                "yaml": y("""
                    apiVersion: apps/v1
                    kind: Deployment
                    metadata:
                      name: api
                      labels:
                        app: api
                    spec:
                      replicas: 2
                      selector:
                        matchLabels:
                          app: api
                      template:
                        metadata:
                          labels:
                            app: api
                        spec:
                          containers:
                            - name: nginx
                              image: nginx:1.27-alpine
                """),
            },
        ],
        commands=[
            "kubectl config get-contexts && kubectl config use-context prod-readonly",
            "kubectl get pods -A -o custom-columns=NS:.metadata.namespace,NAME:.metadata.name,NODE:.spec.nodeName --sort-by=.spec.nodeName",
            "kubectl get pods -l 'app in (web,api),tier!=cache' --field-selector=status.phase!=Running",
            "kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}{\"\\t\"}{.status.allocatable.cpu}{\"\\n\"}{end}'",
            "kubectl diff -f k8s/ && kubectl apply --server-side -f k8s/",
            "kubectl explain deployment.spec.strategy.rollingUpdate",
        ],
        gotchas=[
            "The current context persists across terminals; running a delete in the wrong context is the classic outage. Show the context in your prompt.",
            "`kubectl apply` with client-side apply stores a last-applied annotation that can exceed size limits for huge objects.",
            "`kubectl delete -f dir/` deletes everything in the directory, including namespaces and their contents.",
        ],
        interview=[
            qa("basic", "How do you switch clusters and namespaces with kubectl?", "Use `kubectl config use-context <ctx>` to switch clusters/users and `kubectl config set-context --current --namespace=<ns>` to set the default namespace; tools like kubectx/kubens wrap these."),
            qa("intermediate", "Client vs server dry-run?", "--dry-run=client only renders the object locally. --dry-run=server sends it to the API server, which runs defaulting, validation and admission (including webhooks) without persisting, so it catches quota or policy rejections."),
            qa("intermediate", "What does server-side apply solve?", "The API server tracks which field manager owns each field. Applies from different actors (CI, HPA, controllers) merge without overwriting each other, and conflicts are reported unless forced."),
            qa("advanced", "How do you list all container images running in the cluster?", "`kubectl get pods -A -o jsonpath='{.items[*].spec.containers[*].image}' | tr ' ' '\\n' | sort | uniq -c`, adding initContainers if needed. This is useful for vulnerability and registry audits."),
        ],
        related=["labels", "namespaces", "rbac"],
        flow=chain(
            ("kubeconfig", "context", "Target chosen", "kubectl reads the current context: cluster, user and namespace."),
            ("Credentials", "exec / cert", "Identity obtained", "An exec plugin fetches a short-lived OIDC token.", "context"),
            ("HTTP call", "GET /api/v1/..", "Request sent", "kubectl translates the command into REST calls, visible with -v=8.", "token"),
            ("API server", "filters, admit", "Response built", "Selectors filter results server-side; dry-run skips persistence.", "request"),
            ("Output", "-o jsonpath", "Formatted", "kubectl renders table, YAML, JSON or jsonpath output.", "JSON"),
        ),
    ),
    topic(
        id="helm",
        title="Helm",
        category="operations",
        level="intermediate",
        code="HM",
        tagline="Package, version and install applications as templated charts.",
        analogy="Helm is a package manager like apt for Kubernetes: a chart is the package, values.yaml is the configuration form, and a release is one installed copy you can upgrade or roll back.",
        what=(
            "A Helm chart is a directory of Go-templated Kubernetes manifests plus a values.yaml of defaults and a Chart.yaml with metadata and "
            "dependencies. `helm install` renders the templates with your values and applies the result as a named release; Helm stores each "
            "release revision as a Secret in the target namespace, enabling `helm rollback`. Charts are distributed via HTTP repositories or OCI "
            "registries. Hooks run Jobs at points like pre-upgrade for migrations, and `helm test` runs verification pods. values.schema.json "
            "validates user values. Because templates are code, rendering with `helm template` and diffing before upgrades is a good habit, and "
            "GitOps tools like Argo CD and Flux can render charts declaratively."
        ),
        use_cases=[
            "Installing third-party software (ingress-nginx, Prometheus, cert-manager) with tuned values.",
            "Packaging an internal app once and deploying it to dev, staging and prod with different values files.",
            "Running database migrations as pre-upgrade hooks.",
        ],
        key_points=[
            "Precedence: chart defaults < -f values files (left to right) < --set flags.",
            "`helm upgrade --install --atomic --wait` installs or upgrades and rolls back on failure.",
            "Release history lives in Secrets of type helm.sh/release.v1 in the release namespace.",
            "CRDs in the crds/ directory are installed once and never upgraded or deleted by Helm.",
            "Pin chart versions with --version for reproducible deploys.",
        ],
        examples=[
            {
                "title": "Flux HelmRelease with values",
                "level": "intermediate",
                "description": "Declarative Helm install of ingress-nginx pinned to a chart version, reconciled by Flux.",
                "yaml": y("""
                    apiVersion: helm.toolkit.fluxcd.io/v2
                    kind: HelmRelease
                    metadata:
                      name: ingress-nginx
                      namespace: ingress
                    spec:
                      interval: 10m
                      chart:
                        spec:
                          chart: ingress-nginx
                          version: "4.11.x"
                          sourceRef:
                            kind: HelmRepository
                            name: ingress-nginx
                      install:
                        remediation:
                          retries: 3
                      values:
                        controller:
                          replicaCount: 2
                          config:
                            ssl-protocols: "TLSv1.3"
                          metrics:
                            enabled: true
                """),
            },
            {
                "title": "Rendered template output",
                "level": "basic",
                "description": "What templates/deployment.yaml becomes after `helm template web ./chart --set image.tag=1.4.0`.",
                "yaml": y("""
                    apiVersion: apps/v1
                    kind: Deployment
                    metadata:
                      name: web
                      labels:
                        app.kubernetes.io/name: web
                        app.kubernetes.io/instance: web
                        app.kubernetes.io/managed-by: Helm
                        helm.sh/chart: web-0.3.0
                    spec:
                      replicas: 2
                      selector:
                        matchLabels:
                          app.kubernetes.io/name: web
                          app.kubernetes.io/instance: web
                      template:
                        metadata:
                          labels:
                            app.kubernetes.io/name: web
                            app.kubernetes.io/instance: web
                        spec:
                          containers:
                            - name: web
                              image: ghcr.io/example/web:1.4.0
                """),
            },
            {
                "title": "Pre-upgrade migration hook",
                "level": "advanced",
                "description": "Runs before each upgrade; deleted after success so the next run can recreate it.",
                "yaml": y("""
                    apiVersion: batch/v1
                    kind: Job
                    metadata:
                      name: web-migrate
                      annotations:
                        helm.sh/hook: pre-upgrade,pre-install
                        helm.sh/hook-weight: "0"
                        helm.sh/hook-delete-policy: before-hook-creation,hook-succeeded
                    spec:
                      backoffLimit: 1
                      template:
                        spec:
                          restartPolicy: Never
                          containers:
                            - name: migrate
                              image: ghcr.io/example/web:1.4.0
                              command: ["./migrate", "up"]
                """),
            },
        ],
        commands=[
            "helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx && helm repo update",
            "helm upgrade --install web ./chart -n web --create-namespace -f values-prod.yaml --atomic --wait",
            "helm template web ./chart -f values-prod.yaml | kubectl diff -f -",
            "helm history web -n web && helm rollback web 3 -n web",
            "helm get values web -n web --all",
            "helm install cm oci://registry.example.com/charts/cert-manager --version 1.15.3",
        ],
        gotchas=[
            "Never put real secrets in values.yaml committed to Git; reference existing Secrets or use External Secrets / SOPS.",
            "Manual kubectl edits to Helm-managed objects are overwritten (or conflict) on the next upgrade.",
            "A release stuck in pending-upgrade after an interrupted upgrade blocks further upgrades until rolled back.",
        ],
        interview=[
            qa("basic", "What are chart, release and repository in Helm?", "A chart is the package of templates and default values; a release is a named installed instance of a chart in a namespace with its own revision history; a repository (HTTP or OCI) hosts charts for distribution."),
            qa("intermediate", "How does helm rollback work?", "Helm stores every revision's rendered manifest and values in release Secrets. `helm rollback` re-applies a previous revision's manifest as a new revision, so history is preserved."),
            qa("intermediate", "How do you handle secrets with Helm?", "Do not commit plaintext values. Reference pre-created Secrets by name, use External Secrets Operator with a cloud secret manager, or encrypt values files with SOPS (helm-secrets) using a KMS key."),
            qa("advanced", "Why are CRDs tricky in Helm?", "Charts' crds/ directory is applied only on first install and never upgraded or deleted, to protect custom resources. Teams either manage CRDs separately (kubectl apply or a dedicated chart) or template them deliberately with care around deletion."),
        ],
        related=["deployments", "configmaps", "secrets"],
        flow=chain(
            ("Chart", "templates/", "Package fetched", "Helm pulls a pinned chart version from a repo or OCI registry."),
            ("Values", "-f prod.yaml", "Config merged", "Defaults, values files and --set flags merge by precedence.", "chart"),
            ("Render", "Go templates", "Manifests built", "Templates render into plain Kubernetes YAML.", "values"),
            ("Apply", "API server", "Resources applied", "Helm creates or patches objects and waits for readiness with --wait.", "YAML"),
            ("Release", "revision N", "History saved", "The revision is stored as a Secret for rollback.", "ok"),
        ),
    ),
    topic(
        id="kustomize",
        title="Kustomize",
        category="operations",
        level="intermediate",
        code="KZ",
        tagline="Template-free overlays: patch a shared base per environment.",
        analogy="Kustomize is tracing paper over a master drawing: the base stays untouched and each environment adds its own transparent layer of changes.",
        what=(
            "Kustomize builds manifests from a kustomization.yaml that lists resources and transformations, without any templating language. A "
            "base holds plain YAML; overlays for dev, staging and prod reference the base and apply patches (strategic merge or JSON 6902), "
            "change images, replica counts, namespaces, name prefixes and common labels. ConfigMap and Secret generators append a content hash to "
            "the object name and rewrite references, so changing config automatically triggers a rolling update. Components package optional "
            "features that several overlays can include. Kustomize is built into kubectl (`kubectl apply -k`) and supported natively by Argo CD "
            "and Flux. Because inputs are valid Kubernetes YAML, the output is easy to review and diff."
        ),
        use_cases=[
            "Per-environment differences (replicas, resources, hostnames) without duplicating manifests.",
            "Patching third-party YAML you do not control.",
            "Auto-rolling Deployments when config changes via hashed ConfigMap names.",
        ],
        key_points=[
            "Base plus overlays; overlays never modify base files.",
            "images: transformer changes tags or digests without patches.",
            "configMapGenerator adds a hash suffix; set disableNameSuffixHash only if you must.",
            "`kubectl kustomize dir` renders; `kubectl apply -k dir` renders and applies.",
            "Helm charts can be inflated inside Kustomize via helmCharts (with --enable-helm).",
        ],
        examples=[
            {
                "title": "Production overlay",
                "level": "intermediate",
                "description": "Reuses the base, pins the image, bumps replicas and generates a hashed ConfigMap.",
                "yaml": y("""
                    apiVersion: kustomize.config.k8s.io/v1beta1
                    kind: Kustomization
                    namespace: shop-prod
                    resources:
                      - ../../base
                    labels:
                      - pairs:
                          env: prod
                        includeSelectors: false
                    images:
                      - name: ghcr.io/example/shop
                        newTag: "3.2.0"
                    replicas:
                      - name: shop
                        count: 6
                    configMapGenerator:
                      - name: shop-config
                        literals:
                          - LOG_LEVEL=info
                          - FEATURE_CHECKOUT_V2=true
                    patches:
                      - path: resources-patch.yaml
                        target:
                          kind: Deployment
                          name: shop
                """),
            },
            {
                "title": "Strategic merge patch file",
                "level": "basic",
                "description": "resources-patch.yaml: only the fields to change, matched by kind and name.",
                "yaml": y("""
                    apiVersion: apps/v1
                    kind: Deployment
                    metadata:
                      name: shop
                    spec:
                      template:
                        spec:
                          containers:
                            - name: shop
                              resources:
                                requests:
                                  cpu: 500m
                                  memory: 512Mi
                                limits:
                                  memory: 1Gi
                """),
            },
        ],
        commands=[
            "kubectl kustomize overlays/prod",
            "kubectl diff -k overlays/prod",
            "kubectl apply -k overlays/prod",
            "kustomize edit set image ghcr.io/example/shop:3.2.1",
            "kustomize build --enable-helm overlays/prod",
        ],
        gotchas=[
            "commonLabels also alters selectors, which are immutable on existing Deployments; use labels with includeSelectors: false.",
            "secretGenerator from literal values in Git commits plaintext secrets; use SOPS or External Secrets instead.",
            "kubectl's embedded Kustomize version can lag the standalone binary, so features may differ.",
        ],
        interview=[
            qa("basic", "How does Kustomize differ from Helm?", "Kustomize patches plain YAML with overlays and has no templating, values or release tracking. Helm renders Go templates from values and manages releases with history and rollback. Many teams use Helm for third-party apps and Kustomize for their own."),
            qa("intermediate", "Why do generated ConfigMaps have a hash suffix?", "The suffix changes whenever the content changes and Kustomize rewrites references in pod templates. The template change triggers a rolling update, so pods always pick up new config, and old ConfigMaps remain for rollback."),
            qa("intermediate", "Strategic merge patch vs JSON 6902 patch?", "Strategic merge patches look like partial objects and merge lists by keys such as container name. JSON 6902 patches are explicit operations (add, replace, remove) on JSON paths, useful for precise list edits or CRDs without merge keys."),
            qa("advanced", "How do you structure Kustomize for many environments and clusters?", "A base per app, components for optional features (e.g. monitoring, HPA), overlays per environment, and per-cluster overlays referencing environment overlays. Keep overlays thin, render in CI, and let GitOps tools apply them."),
        ],
        related=["configmaps", "deployments", "namespaces"],
        flow=chain(
            ("Base", "plain YAML", "Shared manifests", "The base defines Deployment, Service and config for every env."),
            ("Overlay", "prod/", "Env selected", "The prod kustomization references the base.", "resources"),
            ("Transform", "images, patches", "Changes applied", "Images, replicas, labels and patches are applied in order.", "overlay"),
            ("Generate", "config-7h2k9", "Hashed configs", "Generators create ConfigMaps with content-hash names and update references.", "patched"),
            ("Output", "kubectl apply -k", "Final YAML", "The fully rendered YAML is applied or committed for GitOps.", "YAML"),
        ),
    ),
    topic(
        id="gitops",
        title="GitOps with Argo CD & Flux",
        category="operations",
        level="advanced",
        code="GO",
        tagline="Git is the source of truth; an in-cluster agent pulls and reconciles continuously.",
        analogy="GitOps is a thermostat for deployments: Git holds the target temperature and the agent keeps adjusting the room until it matches, correcting anyone who fiddles with the radiator.",
        what=(
            "GitOps stores the desired state of clusters declaratively in Git and uses an agent running inside the cluster to pull and apply it. "
            "Argo CD models this as Application objects pointing at a repo path (plain YAML, Kustomize or Helm) and a destination cluster and "
            "namespace; Flux uses GitRepository, Kustomization and HelmRelease resources. Agents continuously compare live state with Git, report "
            "drift as OutOfSync and, with self-heal enabled, revert manual changes. Changes flow through pull requests, giving review, audit "
            "history and simple rollback by git revert. The pull model also means CI never needs cluster-admin credentials. Secrets are handled "
            "with Sealed Secrets, SOPS or External Secrets so no plaintext ever lands in Git."
        ),
        use_cases=[
            "Managing dozens of clusters consistently from one repository (ApplicationSets).",
            "Auditable production changes through pull requests.",
            "Automatic drift correction after manual kubectl edits.",
        ],
        key_points=[
            "Pull-based: the cluster agent fetches from Git; no inbound access from CI to the cluster.",
            "syncPolicy.automated with prune and selfHeal gives full reconciliation.",
            "Sync waves and hooks order resources (CRDs before CRs, migrations before apps).",
            "Separate app source repos from environment config repos; CI updates image tags in config.",
            "Image automation (Argo CD Image Updater, Flux image automation) can bump tags via commits.",
        ],
        examples=[
            {
                "title": "Argo CD Application with self-heal",
                "level": "advanced",
                "description": "Syncs the prod overlay automatically, prunes removed resources and reverts drift.",
                "yaml": y("""
                    apiVersion: argoproj.io/v1alpha1
                    kind: Application
                    metadata:
                      name: shop-prod
                      namespace: argocd
                    spec:
                      project: shop
                      source:
                        repoURL: https://github.com/example/platform-config.git
                        targetRevision: main
                        path: apps/shop/overlays/prod
                      destination:
                        server: https://kubernetes.default.svc
                        namespace: shop-prod
                      syncPolicy:
                        automated:
                          prune: true
                          selfHeal: true
                        syncOptions:
                          - CreateNamespace=true
                          - ServerSideApply=true
                        retry:
                          limit: 5
                          backoff:
                            duration: 10s
                            factor: 2
                """),
            },
            {
                "title": "Flux GitRepository and Kustomization",
                "level": "intermediate",
                "description": "Flux pulls every minute and applies the path with pruning and health checks.",
                "yaml": y("""
                    apiVersion: source.toolkit.fluxcd.io/v1
                    kind: GitRepository
                    metadata:
                      name: platform-config
                      namespace: flux-system
                    spec:
                      interval: 1m
                      url: https://github.com/example/platform-config.git
                      ref:
                        branch: main
                    ---
                    apiVersion: kustomize.toolkit.fluxcd.io/v1
                    kind: Kustomization
                    metadata:
                      name: shop-prod
                      namespace: flux-system
                    spec:
                      interval: 5m
                      path: ./apps/shop/overlays/prod
                      prune: true
                      wait: true
                      sourceRef:
                        kind: GitRepository
                        name: platform-config
                """),
            },
        ],
        commands=[
            "argocd app list",
            "argocd app diff shop-prod",
            "argocd app sync shop-prod && argocd app wait shop-prod --health",
            "flux get kustomizations -A",
            "flux reconcile kustomization shop-prod --with-source",
        ],
        gotchas=[
            "Fields mutated by controllers (HPA replicas, injected sidecars) show as drift; use ignoreDifferences or omit them from Git.",
            "prune: true deletes resources removed from Git, including a namespace if its manifest disappears.",
            "Committing plaintext Secrets to Git compromises them permanently, even after deletion; rotate and use SOPS or External Secrets.",
        ],
        interview=[
            qa("basic", "What are the core principles of GitOps?", "Desired state is declarative, versioned and immutable in Git, pulled automatically by software agents, and continuously reconciled so the live state converges to and stays at what Git declares."),
            qa("intermediate", "Push-based CI deploys vs pull-based GitOps?", "Push CI needs cluster credentials and only applies at pipeline time. Pull GitOps keeps credentials inside the cluster, continuously detects and fixes drift, and makes Git history the deployment audit log."),
            qa("intermediate", "How do you handle secrets in GitOps?", "Encrypt them with SOPS and a KMS key or Sealed Secrets so only the cluster can decrypt, or store references with External Secrets Operator which syncs values from Vault or a cloud secret manager at runtime."),
            qa("advanced", "How do you manage many clusters with Argo CD?", "Register clusters with Argo CD and use ApplicationSets with cluster or Git generators to template one Application per cluster or environment. Use AppProjects to restrict repos, destinations and resource kinds per team."),
        ],
        related=["deployments", "secrets", "namespaces"],
        flow=chain(
            ("Pull request", "bump tag 3.2.0", "Change proposed", "CI opens a PR updating the image tag in the config repo."),
            ("Git main", "merged", "Desired state", "After review the change is merged to main.", "merge"),
            ("Agent", "Argo CD / Flux", "Change detected", "The in-cluster agent polls or receives a webhook and renders manifests.", "fetch"),
            ("Diff", "OutOfSync", "Drift computed", "Live objects are compared with rendered manifests.", "render"),
            ("Sync", "apply + prune", "Cluster updated", "The agent applies changes, prunes removed objects and waits for health.", "apply"),
            ("Healthy", "Synced", "Converged", "Status shows Synced and Healthy; manual drift is reverted by self-heal.", "ok"),
        ),
    ),
    topic(
        id="etcd-backup",
        title="etcd Backup, Restore & Encryption",
        category="operations",
        level="advanced",
        code="ET",
        tagline="Snapshot the cluster's brain regularly, encrypt Secrets at rest, rehearse restores.",
        analogy="etcd is the cluster's only ledger. Backups are photocopies kept in a safe elsewhere, and encryption at rest means a thief who steals the ledger still cannot read the sensitive pages.",
        what=(
            "Every Kubernetes object lives in etcd, so losing etcd without a backup means rebuilding the cluster from scratch. `etcdctl snapshot "
            "save` takes a consistent point-in-time snapshot from one healthy member over mTLS; `etcdutl snapshot restore` rebuilds a data "
            "directory from it, after which the API server and etcd are restarted on the restored data. Snapshots contain every Secret, so they "
            "must be stored encrypted (for example in object storage with KMS-backed AES-256-GCM encryption) with tightly restricted access. "
            "Within etcd, an EncryptionConfiguration makes the API server encrypt Secrets before writing; the KMS v2 provider wraps data keys "
            "with an external KMS and is preferred over locally stored keys. Managed services back up etcd for you, but GitOps repositories "
            "plus tools like Velero still matter for restoring namespaces and persistent volumes."
        ),
        use_cases=[
            "Disaster recovery for self-managed (kubeadm) clusters.",
            "Protecting Secrets if etcd disks or snapshots are stolen.",
            "Pre-upgrade safety snapshot before a control plane upgrade.",
        ],
        key_points=[
            "Back up one member; restore all members from the same snapshot with new cluster tokens.",
            "Verify snapshots with `etcdutl snapshot status` and run regular restore drills.",
            "After enabling encryption, rewrite existing Secrets so they get encrypted.",
            "KMS v2 (GA in v1.29) is the recommended provider; aesgcm with a local key requires frequent key rotation.",
            "Never use the aescbc provider for new setups; prefer KMS v2 or aesgcm.",
        ],
        examples=[
            {
                "title": "Encryption at rest with KMS v2",
                "level": "advanced",
                "description": "Secrets are encrypted with AES-GCM data keys wrapped by an external KMS; identity allows reading old unencrypted data during migration.",
                "yaml": y("""
                    apiVersion: apiserver.config.k8s.io/v1
                    kind: EncryptionConfiguration
                    resources:
                      - resources:
                          - secrets
                          - configmaps
                        providers:
                          - kms:
                              apiVersion: v2
                              name: cloud-kms
                              endpoint: unix:///var/run/kmsplugin/socket.sock
                              timeout: 3s
                          - identity: {}
                """),
            },
            {
                "title": "Scheduled etcd snapshot (kubeadm control plane)",
                "level": "advanced",
                "description": "Runs on a control plane node using the existing etcd client certs from the host (never copy cert material into manifests). The image must bundle a shell and etcdctl.",
                "yaml": y("""
                    apiVersion: batch/v1
                    kind: CronJob
                    metadata:
                      name: etcd-snapshot
                      namespace: kube-system
                    spec:
                      schedule: "0 */6 * * *"
                      concurrencyPolicy: Forbid
                      jobTemplate:
                        spec:
                          template:
                            spec:
                              hostNetwork: true
                              restartPolicy: OnFailure
                              nodeSelector:
                                node-role.kubernetes.io/control-plane: ""
                              tolerations:
                                - key: node-role.kubernetes.io/control-plane
                                  effect: NoSchedule
                              containers:
                                - name: snapshot
                                  image: ghcr.io/example/etcd-backup:3.5.15
                                  command:
                                    - sh
                                    - -c
                                    - >
                                      etcdctl --endpoints=https://127.0.0.1:2379
                                      --cacert=/pki/ca.crt --cert=/pki/healthcheck-client.crt
                                      --key=/pki/healthcheck-client.key
                                      snapshot save /backup/etcd-$(date +%Y%m%d%H%M).db
                                  volumeMounts:
                                    - name: pki
                                      mountPath: /pki
                                      readOnly: true
                                    - name: backup
                                      mountPath: /backup
                              volumes:
                                - name: pki
                                  hostPath:
                                    path: /etc/kubernetes/pki/etcd
                                - name: backup
                                  hostPath:
                                    path: /var/backups/etcd
                """),
            },
        ],
        commands=[
            "ETCDCTL_API=3 etcdctl --endpoints=https://127.0.0.1:2379 --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/server.crt --key=/etc/kubernetes/pki/etcd/server.key snapshot save /var/backups/etcd/snap.db",
            "etcdutl snapshot status /var/backups/etcd/snap.db -w table",
            "etcdutl snapshot restore /var/backups/etcd/snap.db --data-dir /var/lib/etcd-restored",
            "kubectl get secrets -A -o json | kubectl replace -f -",
            "etcdctl endpoint health --cluster -w table",
        ],
        gotchas=[
            "A snapshot copied to an unencrypted bucket leaks every Secret in the cluster; encrypt and restrict access.",
            "Restoring etcd rolls the whole cluster back in time; objects created after the snapshot vanish while their real resources may still exist.",
            "Losing the KMS key or plugin makes encrypted Secrets unreadable; back up and monitor the KMS integration.",
        ],
        interview=[
            qa("intermediate", "How do you back up and restore etcd in a kubeadm cluster?", "Run `etcdctl snapshot save` against a healthy member with the etcd client certificates, verify it, and copy it off-node encrypted. To restore, stop the API server and etcd, run `etcdutl snapshot restore` into a new data dir, point the etcd static pod at it, then restart components."),
            qa("intermediate", "Are Kubernetes Secrets encrypted by default?", "No. They are base64-encoded and stored in plaintext in etcd unless an EncryptionConfiguration is set on the API server. Managed providers often add envelope encryption, but you should enable KMS-based encryption explicitly."),
            qa("advanced", "Why is KMS v2 preferred over the aesgcm provider?", "With aesgcm the key sits in a file on control plane nodes and must be rotated frequently because of nonce limits. KMS v2 uses envelope encryption: data encryption keys are generated per API server and wrapped by an external KMS or HSM, so the root key never touches disk and rotation is centralized."),
            qa("advanced", "Besides etcd snapshots, what else belongs in a DR plan?", "Persistent volume backups (CSI snapshots, Velero), GitOps repositories that can rebuild workloads, external dependencies like DNS and cloud IAM, KMS key backups, and documented, rehearsed restore runbooks with RPO and RTO targets."),
        ],
        related=["secrets", "statefulsets", "storage"],
        flow=chain(
            ("API server", "encrypts Secret", "Encrypt on write", "The API server encrypts Secrets with a KMS-wrapped AES-GCM data key."),
            ("etcd", "ciphertext", "Stored encrypted", "etcd persists only ciphertext for encrypted resources.", "write"),
            ("Snapshot", "etcdctl save", "Backup taken", "A scheduled job snapshots a healthy member over mTLS.", "mTLS"),
            ("Off-site", "KMS-encrypted", "Stored safely", "The snapshot is verified and copied to encrypted, access-restricted storage.", "snap.db"),
            ("Restore", "etcdutl restore", "Disaster recovery", "In a drill or outage, a new data dir is restored and the control plane restarted.", "restore"),
        ),
    ),
    # ------------------------------------------------------------------ networking
    topic(
        id="coredns",
        title="DNS & CoreDNS",
        category="networking",
        level="intermediate",
        code="DN",
        tagline="Service discovery by name: my-svc.my-ns.svc.cluster.local.",
        analogy="CoreDNS is the cluster's phone directory: ask for 'orders in namespace shop' and it gives you the current number, even when the people behind it change daily.",
        what=(
            "CoreDNS runs as a Deployment in kube-system behind the kube-dns Service, and the kubelet writes that Service IP into every pod's "
            "/etc/resolv.conf. A ClusterIP Service gets an A/AAAA record <svc>.<ns>.svc.cluster.local, a headless Service returns the individual "
            "pod IPs, and StatefulSet pods get stable names like db-0.db.ns.svc.cluster.local. SRV records exist for named ports. The resolv.conf "
            "search list plus the default ndots:5 means short names like 'orders' resolve within the namespace, but external names are first tried "
            "against every search domain, multiplying queries. CoreDNS is configured through the Corefile in a ConfigMap, using plugins such as "
            "kubernetes, forward, cache and rewrite. NodeLocal DNSCache can run a caching agent on every node to cut latency and conntrack issues."
        ),
        use_cases=[
            "Calling another service by name across namespaces (orders.shop).",
            "Stable per-pod DNS for databases via headless Services.",
            "Forwarding a corporate domain to on-prem DNS servers.",
        ],
        key_points=[
            "Record format: <service>.<namespace>.svc.<cluster-domain>.",
            "ndots:5 means names with fewer than 5 dots try search domains first; use FQDNs with a trailing dot for external hosts.",
            "dnsPolicy: ClusterFirst (default), Default (node resolver), None (custom dnsConfig).",
            "Scale CoreDNS with replicas or the cluster-proportional-autoscaler for large clusters.",
        ],
        examples=[
            {
                "title": "Corefile with a stub domain",
                "level": "advanced",
                "description": "Forwards corp.example.com to internal resolvers and caches cluster answers for 30s.",
                "yaml": y("""
                    apiVersion: v1
                    kind: ConfigMap
                    metadata:
                      name: coredns
                      namespace: kube-system
                    data:
                      Corefile: |
                        .:53 {
                            errors
                            health
                            ready
                            kubernetes cluster.local in-addr.arpa ip6.arpa {
                                pods insecure
                                fallthrough in-addr.arpa ip6.arpa
                            }
                            prometheus :9153
                            forward . /etc/resolv.conf
                            cache 30
                            loop
                            reload
                        }
                        corp.example.com:53 {
                            forward . 10.0.0.53 10.0.1.53
                            cache 60
                        }
                """),
            },
            {
                "title": "Tuning ndots for an external-heavy app",
                "level": "intermediate",
                "description": "Lowers ndots so api.stripe.com style names are queried directly instead of via search domains.",
                "yaml": y("""
                    apiVersion: v1
                    kind: Pod
                    metadata:
                      name: payments-client
                    spec:
                      dnsConfig:
                        options:
                          - name: ndots
                            value: "2"
                      containers:
                        - name: app
                          image: ghcr.io/example/payments-client:1.0.0
                """),
            },
        ],
        commands=[
            "kubectl run dnsutils --rm -it --image=registry.k8s.io/e2e-test-images/agnhost:2.39 -- nslookup orders.shop",
            "kubectl exec deploy/web -- cat /etc/resolv.conf",
            "kubectl -n kube-system logs -l k8s-app=kube-dns",
            "kubectl -n kube-system get configmap coredns -o yaml",
            "kubectl -n kube-system rollout restart deploy/coredns",
        ],
        gotchas=[
            "NetworkPolicies with default-deny egress must allow UDP and TCP 53 to kube-dns.",
            "Alpine/musl resolvers handle search domains differently, causing intermittent lookup failures.",
            "A forward loop to a node resolver pointing back at CoreDNS crashes it (the loop plugin detects this).",
        ],
        interview=[
            qa("basic", "How does a pod resolve the name 'orders'?", "The resolver appends search domains from /etc/resolv.conf (e.g. <ns>.svc.cluster.local) and queries CoreDNS at the kube-dns Service IP. CoreDNS answers from its Kubernetes plugin with the Service's ClusterIP."),
            qa("intermediate", "What is a headless Service in DNS terms?", "A Service with clusterIP: None. DNS returns A records for each ready pod instead of a single virtual IP, and with StatefulSets each pod gets a stable hostname record."),
            qa("intermediate", "Why can ndots:5 hurt performance?", "Any name with fewer than five dots, such as api.example.com, is first tried with each search domain, generating several NXDOMAIN queries (doubled for A and AAAA) before the real lookup. Use FQDNs with a trailing dot or lower ndots."),
            qa("advanced", "What problem does NodeLocal DNSCache solve?", "It runs a caching DNS agent on each node, so pods query a link-local address instead of crossing the network to CoreDNS. This reduces latency, CoreDNS load and conntrack race issues with UDP DNS that caused 5-second timeouts."),
        ],
        related=["services", "statefulsets", "network-policy"],
        flow=chain(
            ("Pod", "GET http://orders", "Name lookup", "The app resolves 'orders' using /etc/resolv.conf."),
            ("Search list", "ndots:5", "Name expanded", "The resolver tries orders.shop.svc.cluster.local first.", "orders"),
            ("kube-dns svc", "10.96.0.10", "Query routed", "The query goes to the kube-dns ClusterIP and on to a CoreDNS pod.", "UDP 53"),
            ("CoreDNS", "kubernetes plugin", "Record found", "CoreDNS looks up the Service from its API watch cache.", "query"),
            ("Answer", "A 10.96.12.7", "IP returned", "The pod receives the ClusterIP and opens the connection.", "A record"),
        ),
    ),
    topic(
        id="kube-proxy",
        title="kube-proxy & Service Internals",
        category="networking",
        level="advanced",
        code="KP",
        tagline="How a virtual ClusterIP becomes a real pod connection: iptables, IPVS, nftables or eBPF.",
        analogy="A ClusterIP is a company switchboard number that no single desk owns; kube-proxy programs every node's phone system to forward calls on that number to whichever desk is free.",
        what=(
            "A ClusterIP is virtual: no interface owns it. kube-proxy runs on each node, watches Services and EndpointSlices, and programs the "
            "kernel so packets to ClusterIP:port are DNAT-ed to a ready pod IP. In iptables mode it builds chains with random-probability rules, "
            "which is simple but scales linearly with Services; IPVS mode uses kernel hash tables and real load-balancing algorithms; the newer "
            "nftables mode improves performance further. eBPF CNIs such as Cilium can replace kube-proxy entirely. NodePort and LoadBalancer "
            "Services build on the same rules, and externalTrafficPolicy: Local preserves client source IPs by only sending traffic to local pods. "
            "Because selection happens per connection, long-lived connections do not rebalance when pods scale."
        ),
        use_cases=[
            "Debugging why a Service IP does not respond (no endpoints, missing rules).",
            "Preserving client IPs for logging or allowlists with externalTrafficPolicy: Local.",
            "Choosing IPVS, nftables or eBPF for clusters with thousands of Services.",
        ],
        key_points=[
            "Only ready pods are in EndpointSlices; no ready pods means connections are rejected.",
            "Load balancing is per connection, not per request; HTTP/2 and gRPC need L7 balancing.",
            "externalTrafficPolicy: Local keeps source IP but can unbalance traffic and requires health checks.",
            "internalTrafficPolicy: Local keeps in-cluster traffic on the same node (e.g. node agents).",
            "sessionAffinity: ClientIP pins a client to one pod for a timeout period.",
        ],
        examples=[
            {
                "title": "kube-proxy in IPVS mode",
                "level": "advanced",
                "description": "Least-connection balancing with strict ARP, needed for MetalLB in L2 mode.",
                "yaml": y("""
                    apiVersion: kubeproxy.config.k8s.io/v1alpha1
                    kind: KubeProxyConfiguration
                    mode: ipvs
                    ipvs:
                      scheduler: lc
                      strictARP: true
                    conntrack:
                      maxPerCore: 32768
                    metricsBindAddress: 0.0.0.0:10249
                """),
            },
            {
                "title": "LoadBalancer preserving client IP",
                "level": "intermediate",
                "description": "Traffic only goes to nodes with local pods; the cloud LB health-checks healthCheckNodePort.",
                "yaml": y("""
                    apiVersion: v1
                    kind: Service
                    metadata:
                      name: edge
                    spec:
                      type: LoadBalancer
                      externalTrafficPolicy: Local
                      selector:
                        app: edge
                      ports:
                        - name: https
                          port: 443
                          targetPort: 8443
                """),
            },
        ],
        commands=[
            "kubectl get endpointslices -l kubernetes.io/service-name=web -o wide",
            "kubectl -n kube-system get cm kube-proxy -o yaml | grep mode",
            "sudo iptables -t nat -L KUBE-SERVICES -n | grep web",
            "sudo ipvsadm -Ln",
            "kubectl -n kube-system logs ds/kube-proxy",
        ],
        gotchas=[
            "You cannot ping a ClusterIP in iptables mode; test with TCP (curl, nc) instead.",
            "A Service selector typo yields zero endpoints and connection refused, with no error on the Service itself.",
            "gRPC clients hold one connection, so all requests hit one pod; use client-side or mesh load balancing.",
        ],
        interview=[
            qa("intermediate", "How does traffic to a ClusterIP reach a pod?", "kube-proxy on every node watches Services and EndpointSlices and installs iptables, IPVS or nftables rules. A packet to ClusterIP:port is DNAT-ed on the source node to one ready pod IP, then routed by the CNI to that pod."),
            qa("intermediate", "iptables vs IPVS mode?", "iptables evaluates chains sequentially with random-probability rules, so updates and lookups grow with the number of Services. IPVS uses kernel hash tables with O(1) lookup and supports algorithms like round-robin and least-connection, scaling better for large clusters."),
            qa("advanced", "What does externalTrafficPolicy: Local change?", "Nodes only forward external traffic to pods on themselves, avoiding a second hop and SNAT so the client source IP is preserved. Nodes without local pods fail the LB health check, and load can be uneven if pods are unevenly spread."),
            qa("advanced", "Why might a gRPC service be unbalanced behind a ClusterIP?", "kube-proxy balances per TCP connection, and gRPC multiplexes all requests over one long-lived HTTP/2 connection. Use a headless Service with client-side balancing, a service mesh or an L7 proxy to balance per request."),
        ],
        related=["services", "network-policy", "ingress"],
        flow=chain(
            ("Client pod", "-> 10.96.12.7:80", "Packet sent", "A pod connects to the web Service ClusterIP."),
            ("Netfilter", "KUBE-SERVICES", "Rule matched", "On the client's node the packet hits kube-proxy's nat rules.", "SYN"),
            ("Pick backend", "random / lc", "Endpoint chosen", "One ready endpoint is selected from the EndpointSlice.", "match"),
            ("DNAT", "-> 10.244.2.9:8080", "Destination rewritten", "The destination becomes the chosen pod IP and conntrack records it.", "DNAT"),
            ("Pod", "via CNI route", "Delivered", "The CNI routes the packet to the pod; replies are reverse-NAT-ed.", "packet"),
        ),
    ),
    topic(
        id="gateway-api",
        title="Gateway API & TLS",
        category="networking",
        level="intermediate",
        code="GW",
        tagline="The role-oriented successor to Ingress: GatewayClass, Gateway, HTTPRoute.",
        analogy="Ingress is one shared reception desk with sticky notes (annotations). Gateway API gives the building owner the front door (Gateway) and lets each tenant post their own room directory (Routes).",
        what=(
            "Gateway API is a set of CRDs that model traffic entry by role. Infrastructure providers ship a GatewayClass; platform teams create "
            "Gateways that define listeners (ports, protocols, hostnames, TLS certificates); application teams attach HTTPRoute, GRPCRoute or "
            "TLSRoute objects from their own namespaces. Features that required vendor annotations in Ingress, such as header matching, traffic "
            "weights, redirects, header modification and request mirroring, are part of the portable spec. allowedRoutes and ReferenceGrant "
            "control which namespaces may attach routes or reference backends across namespaces. TLS is terminated at the listener using "
            "certificates in Secrets, typically issued and renewed by cert-manager; configure TLS 1.3 (or at minimum 1.2) and ECDSA P-256 or "
            "RSA 2048+ keys. Implementations include Envoy Gateway, Istio, Cilium, NGINX Gateway Fabric and cloud load balancers."
        ),
        use_cases=[
            "Shared company gateway with per-team routes and delegated hostnames.",
            "Weighted canaries and header-based routing without vendor annotations.",
            "Automated TLS for public hosts using cert-manager and Let's Encrypt.",
        ],
        key_points=[
            "Resources: GatewayClass (cluster), Gateway (platform), *Route (app teams).",
            "Routes attach via parentRefs; Gateways restrict attachment with allowedRoutes.",
            "ReferenceGrant is required for cross-namespace backend or Secret references.",
            "Status conditions (Accepted, ResolvedRefs, Programmed) explain why a route does not work.",
            "Ingress is frozen; new features land in Gateway API.",
        ],
        examples=[
            {
                "title": "Gateway with HTTPS listener and cert-manager",
                "level": "intermediate",
                "description": "cert-manager issues an ECDSA P-256 certificate into the referenced Secret; no key material appears in Git.",
                "yaml": y("""
                    apiVersion: gateway.networking.k8s.io/v1
                    kind: Gateway
                    metadata:
                      name: public-gw
                      namespace: infra
                      annotations:
                        cert-manager.io/cluster-issuer: letsencrypt-prod
                    spec:
                      gatewayClassName: envoy
                      listeners:
                        - name: https
                          protocol: HTTPS
                          port: 443
                          hostname: "*.example.com"
                          tls:
                            mode: Terminate
                            certificateRefs:
                              - name: wildcard-example-tls
                          allowedRoutes:
                            namespaces:
                              from: Selector
                              selector:
                                matchLabels:
                                  gateway-access: "true"
                    ---
                    apiVersion: cert-manager.io/v1
                    kind: Certificate
                    metadata:
                      name: wildcard-example
                      namespace: infra
                    spec:
                      secretName: wildcard-example-tls
                      dnsNames: ["*.example.com"]
                      privateKey:
                        algorithm: ECDSA
                        size: 256
                        rotationPolicy: Always
                      issuerRef:
                        kind: ClusterIssuer
                        name: letsencrypt-prod
                """),
            },
            {
                "title": "Team HTTPRoute with redirect and path routing",
                "level": "basic",
                "description": "The shop team attaches its own route to the shared Gateway.",
                "yaml": y("""
                    apiVersion: gateway.networking.k8s.io/v1
                    kind: HTTPRoute
                    metadata:
                      name: shop
                      namespace: shop
                    spec:
                      parentRefs:
                        - name: public-gw
                          namespace: infra
                          sectionName: https
                      hostnames: ["shop.example.com"]
                      rules:
                        - matches:
                            - path:
                                type: PathPrefix
                                value: /api
                          backendRefs:
                            - name: shop-api
                              port: 8080
                        - matches:
                            - path:
                                type: PathPrefix
                                value: /old-cart
                          filters:
                            - type: RequestRedirect
                              requestRedirect:
                                path:
                                  type: ReplacePrefixMatch
                                  replacePrefixMatch: /cart
                                statusCode: 301
                        - backendRefs:
                            - name: shop-web
                              port: 80
                """),
            },
        ],
        commands=[
            "kubectl get gatewayclasses,gateways -A",
            "kubectl get httproutes -A",
            "kubectl describe httproute shop -n shop",
            "kubectl get certificates -A && kubectl describe certificate wildcard-example -n infra",
            "kubectl get gateway public-gw -n infra -o jsonpath='{.status.addresses}'",
        ],
        gotchas=[
            "A route in a namespace not allowed by the listener stays unattached; check the route's parent status.",
            "Gateway API CRDs are not installed by default in most clusters; install the standard channel matching your implementation.",
            "Minimum TLS version and cipher policy are implementation-specific settings; set TLS 1.3 explicitly where supported.",
        ],
        interview=[
            qa("basic", "What problems with Ingress does Gateway API solve?", "Ingress has a minimal spec, so advanced features depend on vendor-specific annotations, and one object mixes infrastructure and app concerns. Gateway API is expressive, portable and role-oriented, separating Gateway ownership from per-team routes."),
            qa("intermediate", "How do teams attach routes to a shared Gateway safely?", "Routes reference the Gateway via parentRefs, while the Gateway's allowedRoutes restricts which namespaces and route kinds may attach. Cross-namespace backend references additionally require a ReferenceGrant in the target namespace."),
            qa("intermediate", "How does cert-manager automate TLS here?", "cert-manager watches Certificate resources or Gateway annotations, completes ACME challenges with the issuer, stores the key pair in a Secret and renews before expiry. The Gateway listener references that Secret in certificateRefs."),
            qa("advanced", "Which TLS settings would you require on a public Gateway?", "TLS 1.3 preferred with TLS 1.2 only for legacy clients, AEAD cipher suites, ECDSA P-256 or RSA 2048+ certificates signed with SHA-256, automatic renewal, HTTP to HTTPS redirects and HSTS. Older protocols and SHA-1 signatures should be disabled."),
        ],
        related=["ingress", "services", "network-policy"],
        flow=chain(
            ("Client", "https://shop", "TLS handshake", "A browser connects to the Gateway's external address."),
            ("Listener", "443 HTTPS", "TLS terminated", "The listener terminates TLS 1.3 with the cert-manager certificate.", "ClientHello"),
            ("HTTPRoute", "host + path", "Route matched", "Hostname shop.example.com and path /api match the shop route.", "request"),
            ("Filters", "redirect, header", "Request processed", "Optional redirects, header changes or weights are applied.", "match"),
            ("Backend", "shop-api:8080", "Forwarded", "Traffic is sent to the backend Service's endpoints.", "proxy"),
        ),
    ),
    # ------------------------------------------------------------------ storage
    topic(
        id="storageclasses-csi",
        title="StorageClasses, CSI & Snapshots",
        category="storage",
        level="intermediate",
        code="SC",
        tagline="Dynamic provisioning: a PVC asks, the CSI driver creates the disk, snapshots protect it.",
        analogy="A StorageClass is a menu item ('fast SSD, encrypted, expandable'); the PVC is your order and the CSI driver is the kitchen that actually prepares the disk.",
        what=(
            "A StorageClass names a provisioner (a CSI driver such as ebs.csi.aws.com or pd.csi.storage.gke.io) with parameters like disk type, "
            "IOPS and encryption. When a PVC references the class, the external-provisioner sidecar calls the driver's CreateVolume and binds a new "
            "PV automatically, so admins no longer pre-create volumes. volumeBindingMode: WaitForFirstConsumer delays provisioning until a pod is "
            "scheduled, so the disk is created in the right zone. allowVolumeExpansion enables online resizing by editing the PVC, and "
            "reclaimPolicy decides whether the disk is deleted or retained when the PVC goes away. With the snapshot CRDs and controller you can "
            "create VolumeSnapshots and restore new PVCs from them via dataSource. CSI also covers node-side operations such as staging and "
            "mounting volumes."
        ),
        use_cases=[
            "Self-service storage for StatefulSets without tickets to the storage team.",
            "Encrypted, zone-aware block storage with expandable size.",
            "Point-in-time snapshots before risky database migrations, and cloning test databases.",
        ],
        key_points=[
            "Mark one class as default with the is-default-class annotation.",
            "WaitForFirstConsumer avoids zone mismatches between pod and volume.",
            "reclaimPolicy Retain keeps the disk after PVC deletion for safety.",
            "Snapshots need the external-snapshotter CRDs, controller and a VolumeSnapshotClass.",
            "Access modes: ReadWriteOnce, ReadWriteOncePod, ReadOnlyMany, ReadWriteMany depend on the driver.",
        ],
        examples=[
            {
                "title": "Encrypted, expandable, zone-aware StorageClass",
                "level": "intermediate",
                "description": "AWS EBS gp3 volumes encrypted with a KMS key, created where the pod lands.",
                "yaml": y("""
                    apiVersion: storage.k8s.io/v1
                    kind: StorageClass
                    metadata:
                      name: fast-encrypted
                      annotations:
                        storageclass.kubernetes.io/is-default-class: "true"
                    provisioner: ebs.csi.aws.com
                    parameters:
                      type: gp3
                      iops: "6000"
                      encrypted: "true"
                    reclaimPolicy: Retain
                    allowVolumeExpansion: true
                    volumeBindingMode: WaitForFirstConsumer
                    ---
                    apiVersion: v1
                    kind: PersistentVolumeClaim
                    metadata:
                      name: orders-db-data
                    spec:
                      accessModes: ["ReadWriteOnce"]
                      storageClassName: fast-encrypted
                      resources:
                        requests:
                          storage: 50Gi
                """),
            },
            {
                "title": "Snapshot and restore",
                "level": "advanced",
                "description": "Take a snapshot of a PVC, then create a new PVC pre-populated from it.",
                "yaml": y("""
                    apiVersion: snapshot.storage.k8s.io/v1
                    kind: VolumeSnapshotClass
                    metadata:
                      name: ebs-snapshots
                    driver: ebs.csi.aws.com
                    deletionPolicy: Retain
                    ---
                    apiVersion: snapshot.storage.k8s.io/v1
                    kind: VolumeSnapshot
                    metadata:
                      name: orders-db-pre-migration
                    spec:
                      volumeSnapshotClassName: ebs-snapshots
                      source:
                        persistentVolumeClaimName: orders-db-data
                    ---
                    apiVersion: v1
                    kind: PersistentVolumeClaim
                    metadata:
                      name: orders-db-restore
                    spec:
                      accessModes: ["ReadWriteOnce"]
                      storageClassName: fast-encrypted
                      dataSource:
                        apiGroup: snapshot.storage.k8s.io
                        kind: VolumeSnapshot
                        name: orders-db-pre-migration
                      resources:
                        requests:
                          storage: 50Gi
                """),
            },
        ],
        commands=[
            "kubectl get storageclass",
            "kubectl get pvc,pv -o wide",
            "kubectl patch pvc orders-db-data -p '{\"spec\":{\"resources\":{\"requests\":{\"storage\":\"100Gi\"}}}}'",
            "kubectl get volumesnapshots,volumesnapshotcontents",
            "kubectl get csidrivers,csinodes",
        ],
        gotchas=[
            "Immediate binding can create a disk in a zone where the pod cannot run, leaving it Pending forever.",
            "PVC size can only grow, never shrink.",
            "Crash-consistent snapshots of a running database may need app-level quiescing or WAL replay for consistency.",
        ],
        interview=[
            qa("basic", "What is dynamic provisioning?", "When a PVC references a StorageClass, the class's provisioner (a CSI driver) automatically creates a backing volume and PV that binds to the claim, instead of admins pre-creating PVs."),
            qa("intermediate", "Why use volumeBindingMode: WaitForFirstConsumer?", "It delays volume creation until a pod using the PVC is scheduled, so the scheduler's choice (zone, node constraints) determines where the disk is created. Immediate mode can create zonal disks the pod can never reach."),
            qa("intermediate", "What does reclaimPolicy control?", "What happens to the PV and backing disk when the PVC is deleted: Delete removes the disk, Retain keeps it and leaves the PV Released for manual recovery. Production data classes often use Retain."),
            qa("advanced", "How does CSI split responsibilities?", "The controller plugin with sidecars (external-provisioner, attacher, resizer, snapshotter) handles cluster-level operations like CreateVolume and ControllerPublish. The node plugin, a DaemonSet registered with kubelet, stages and mounts volumes on the node."),
        ],
        related=["storage", "statefulsets", "etcd-backup"],
        flow=chain(
            ("PVC", "50Gi, fast", "Claim created", "A StatefulSet creates a PVC referencing StorageClass fast-encrypted."),
            ("Scheduler", "WaitForConsumer", "Zone decided", "Binding waits until the pod is scheduled to a node in zone a.", "pending"),
            ("Provisioner", "CreateVolume", "Disk created", "The CSI external-provisioner asks the driver for an encrypted gp3 disk.", "zone a"),
            ("PV bound", "pvc <-> pv", "Claim bound", "A PV is created and bound to the claim.", "volume"),
            ("Node plugin", "stage + mount", "Volume mounted", "The node plugin attaches and mounts the disk into the pod.", "attach"),
        ),
    ),
    # ------------------------------------------------------------------ observability
    topic(
        id="observability",
        title="Metrics, Logs & Monitoring",
        category="observability",
        level="intermediate",
        code="OB",
        tagline="metrics-server for autoscaling, Prometheus for monitoring, a log pipeline for everything else.",
        analogy="metrics-server is the car's speedometer (live, no history); Prometheus is the flight recorder (history and alarms); logs are the pilot's spoken notes.",
        what=(
            "metrics-server scrapes CPU and memory from each kubelet's resource endpoint and serves the metrics.k8s.io API used by `kubectl top`, "
            "HPA and VPA; it keeps no history. For real monitoring, Prometheus scrapes application /metrics endpoints, kube-state-metrics (object "
            "state such as desired vs available replicas) and node-exporter, stores time series and evaluates alerting rules sent to "
            "Alertmanager. The Prometheus Operator adds ServiceMonitor, PodMonitor and PrometheusRule CRDs so teams declare scraping and alerts "
            "next to their apps. Containers should log to stdout and stderr; the runtime writes files on the node and a DaemonSet agent "
            "(Fluent Bit, Vector, OpenTelemetry Collector) ships them to Loki, Elasticsearch or a cloud service. Traces via OpenTelemetry "
            "complete the picture, and events provide short-lived cluster-level signals."
        ),
        use_cases=[
            "Alerting on error rate, latency and saturation for each service.",
            "Capacity planning with historical CPU and memory against requests.",
            "Centralised log search after pods have been deleted.",
        ],
        key_points=[
            "metrics-server is required for `kubectl top` and resource-based HPA, but is not a monitoring system.",
            "kube-state-metrics exposes object state; node-exporter exposes host metrics.",
            "Use the RED (rate, errors, duration) and USE (utilisation, saturation, errors) methods for dashboards.",
            "Logs written inside containers to files are lost on restart and invisible to `kubectl logs`.",
            "Watch label cardinality: per-user or per-request labels explode Prometheus memory.",
        ],
        examples=[
            {
                "title": "ServiceMonitor for an app",
                "level": "intermediate",
                "description": "Prometheus Operator discovers Services labelled app=shop and scrapes /metrics every 30s.",
                "yaml": y("""
                    apiVersion: monitoring.coreos.com/v1
                    kind: ServiceMonitor
                    metadata:
                      name: shop
                      namespace: shop
                      labels:
                        release: kube-prometheus-stack
                    spec:
                      selector:
                        matchLabels:
                          app: shop
                      endpoints:
                        - port: metrics
                          path: /metrics
                          interval: 30s
                """),
            },
            {
                "title": "Alerting rules",
                "level": "advanced",
                "description": "Pages on high 5xx ratio and warns on pods restarting repeatedly.",
                "yaml": y("""
                    apiVersion: monitoring.coreos.com/v1
                    kind: PrometheusRule
                    metadata:
                      name: shop-alerts
                      namespace: shop
                    spec:
                      groups:
                        - name: shop.rules
                          rules:
                            - alert: ShopHighErrorRate
                              expr: |
                                sum(rate(http_requests_total{app="shop",code=~"5.."}[5m]))
                                  / sum(rate(http_requests_total{app="shop"}[5m])) > 0.05
                              for: 10m
                              labels:
                                severity: page
                              annotations:
                                summary: More than 5% of shop requests fail
                            - alert: PodRestartingOften
                              expr: increase(kube_pod_container_status_restarts_total{namespace="shop"}[1h]) > 5
                              labels:
                                severity: warning
                """),
            },
        ],
        commands=[
            "kubectl top nodes && kubectl top pods -A --sort-by=memory",
            "kubectl get --raw /apis/metrics.k8s.io/v1beta1/nodes",
            "helm install monitoring prometheus-community/kube-prometheus-stack -n monitoring --create-namespace",
            "kubectl get servicemonitors,prometheusrules -A",
            "kubectl logs -l app=shop --since=15m --prefix --max-log-requests=10",
        ],
        gotchas=[
            "`kubectl top` failing with 'Metrics API not available' means metrics-server is missing or unhealthy, which also breaks HPA.",
            "ServiceMonitors must carry the labels your Prometheus instance selects (e.g. release: kube-prometheus-stack).",
            "Never log secrets or tokens; log pipelines are widely accessible and long-retained.",
        ],
        interview=[
            qa("basic", "metrics-server vs Prometheus?", "metrics-server provides current CPU and memory via the metrics API for kubectl top, HPA and VPA, without history. Prometheus is a full time-series database scraping arbitrary metrics with querying, retention and alerting."),
            qa("intermediate", "What does kube-state-metrics provide?", "Metrics derived from Kubernetes object state, such as Deployment desired vs available replicas, pod phases, container restarts and resource requests. It complements resource usage metrics from cAdvisor and node-exporter."),
            qa("intermediate", "How do logs flow in Kubernetes?", "Containers write to stdout and stderr; the container runtime writes them to files under /var/log/pods on the node, rotated by kubelet. A DaemonSet agent tails those files, enriches them with pod metadata and ships them to a backend like Loki or Elasticsearch."),
            qa("advanced", "What causes high cardinality and how do you prevent it?", "Labels with unbounded values like user IDs, request IDs or full URLs create a new series per value, exhausting Prometheus memory. Keep labels bounded, aggregate with recording rules, drop labels via relabeling and review top series counts."),
        ],
        related=["hpa", "vpa", "probes"],
        flow=chain(
            ("App", "/metrics, stdout", "Signals emitted", "The app exposes Prometheus metrics and writes logs to stdout."),
            ("Collectors", "scrape + tail", "Data collected", "Prometheus scrapes targets; Fluent Bit tails node log files.", "metrics"),
            ("Storage", "TSDB, Loki", "Data stored", "Time series and logs are stored with labels for querying.", "samples"),
            ("Rules", "PromQL alerts", "Rules evaluated", "Alert rules evaluate PromQL expressions continuously.", "query"),
            ("Alertmanager", "route, dedupe", "Humans notified", "Firing alerts are grouped and routed to Slack or a pager.", "alert"),
        ),
    ),
    topic(
        id="debugging-pods",
        title="Debugging Pods & Ephemeral Containers",
        category="observability",
        level="basic",
        code="DB",
        tagline="describe, events, logs, exec and kubectl debug: a repeatable triage path.",
        analogy="Debugging a pod is like a doctor's visit: read the chart (describe), ask what happened (events, logs), examine the patient (exec), and if needed bring in a specialist with tools (ephemeral debug container).",
        what=(
            "Most pod problems surface in a few places. `kubectl get pods` shows status such as Pending, ImagePullBackOff, CrashLoopBackOff or "
            "OOMKilled, and `kubectl describe pod` adds conditions, exit codes, probe failures and events from the scheduler and kubelet. "
            "`kubectl logs --previous` shows output from the last crashed container instance. Minimal or distroless images often lack a shell, so "
            "`kubectl debug` injects an ephemeral container with tools into the running pod, optionally sharing the target container's process "
            "namespace. It can also copy a pod with a modified command, or start a privileged pod on a node to inspect the host. Events are kept "
            "for only about an hour by default, so capture them early or ship them to your log system."
        ),
        use_cases=[
            "Triaging Pending, CrashLoopBackOff and ImagePullBackOff pods quickly.",
            "Inspecting network or files inside distroless containers without rebuilding images.",
            "Investigating node-level problems (disk pressure, kubelet logs) from kubectl.",
        ],
        key_points=[
            "Pending: scheduling issue (resources, taints, affinity, PVC); check describe events.",
            "CrashLoopBackOff: the app exits; check logs --previous and exit codes (137 = SIGKILL/OOM, 1 = app error).",
            "Ephemeral containers cannot be removed or restarted and have no ports or probes.",
            "`kubectl debug --copy-to` creates a modified copy, leaving the original pod untouched.",
            "`kubectl events --for pod/x` gives a sorted event view.",
        ],
        examples=[
            {
                "title": "Pod with process namespace sharing",
                "level": "intermediate",
                "description": "Lets a debug sidecar or ephemeral container see and signal the app's processes.",
                "yaml": y("""
                    apiVersion: v1
                    kind: Pod
                    metadata:
                      name: api-debuggable
                    spec:
                      shareProcessNamespace: true
                      containers:
                        - name: api
                          image: gcr.io/distroless/static:nonroot
                          command: ["/app/api"]
                """),
            },
            {
                "title": "Throwaway network debug pod",
                "level": "basic",
                "description": "A toolbox pod for DNS, curl and tcpdump tests from inside the cluster; delete it afterwards.",
                "yaml": y("""
                    apiVersion: v1
                    kind: Pod
                    metadata:
                      name: netdebug
                      labels:
                        purpose: debug
                    spec:
                      restartPolicy: Never
                      activeDeadlineSeconds: 3600
                      containers:
                        - name: tools
                          image: nicolaka/netshoot:v0.13
                          command: ["sleep", "3600"]
                          securityContext:
                            allowPrivilegeEscalation: false
                """),
            },
        ],
        commands=[
            "kubectl describe pod api-7d9f -n shop",
            "kubectl logs api-7d9f -c api --previous",
            "kubectl events --for pod/api-7d9f -n shop",
            "kubectl debug -it api-7d9f --image=busybox:1.36 --target=api",
            "kubectl debug api-7d9f -it --copy-to=api-copy --container=api -- sh",
            "kubectl debug node/worker-1 -it --image=busybox:1.36",
        ],
        gotchas=[
            "Events expire (default 1h), so a pod that failed overnight may show nothing; rely on shipped events or logs.",
            "Node debug pods mount the host filesystem at /host and run privileged; restrict who can use them via RBAC.",
            "`kubectl exec` into production to hot-fix files is lost on restart and bypasses review; fix the image or config instead.",
        ],
        interview=[
            qa("basic", "A pod is stuck in Pending. How do you debug it?", "Run `kubectl describe pod` and read the scheduler event, e.g. insufficient cpu, untolerated taint, node affinity mismatch or unbound PVC. Then fix requests, tolerations, labels or storage, or add capacity."),
            qa("basic", "How do you see why a container keeps crashing?", "Check `kubectl logs <pod> --previous` for the last crashed instance and `kubectl describe pod` for Last State, exit code and reason such as OOMKilled or probe failure."),
            qa("intermediate", "What are ephemeral containers?", "Temporary containers added to a running pod via the ephemeralcontainers subresource, usually with `kubectl debug`. They share the pod's namespaces (and optionally a target container's process namespace) so you can debug distroless images without restarting the pod."),
            qa("advanced", "How do you debug a node-level problem without SSH?", "`kubectl debug node/<name> -it --image=...` starts a pod in the host's namespaces with the root filesystem at /host; you can chroot /host to inspect kubelet logs, disk usage or containerd. Remove the pod afterwards and restrict this capability with RBAC and policy."),
        ],
        related=["pods", "probes", "resources-qos"],
        flow=chain(
            ("get pods", "STATUS column", "Spot symptom", "Status shows CrashLoopBackOff, Pending or ImagePullBackOff."),
            ("describe", "events, exit code", "Read the chart", "Conditions, last state, exit code and events narrow the cause.", "pod name"),
            ("logs", "--previous", "Read output", "Logs from the crashed instance reveal the application error.", "reason"),
            ("debug", "ephemeral tools", "Inspect live", "An ephemeral container with tools attaches to the running pod.", "hypothesis"),
            ("Fix", "image / config", "Resolve", "Fix the manifest, config or image and roll out; never hot-patch in place.", "root cause"),
        ),
    ),
]

from app.subjects._catalog import build_lessons

TOPICS += build_lessons([
    ("openshift-architecture", "Red Hat OpenShift: Routes, Operators & Builds", "operations", "intermediate", "OpenShift extends Kubernetes with an integrated developer platform, Routes, Operators, image/build workflows and security defaults. Core Kubernetes objects still apply, while platform-specific APIs and policies shape deployment and cluster operations.", "oc get routes,deployments,pods -n app-prod", "Learn the Kubernetes primitive behind each OpenShift feature so platform-specific tooling does not hide the underlying workload, service, ingress or RBAC behavior.", "How does an OpenShift Route relate to Kubernetes networking?", "A Route exposes a service through the OpenShift ingress/router layer. The application still uses Kubernetes Services and endpoints behind it; DNS, TLS termination, router health and service selectors all matter.", ["cluster-architecture", "ingress", "helm"]),
], "K8S", "A platform packages Kubernetes primitives with safer defaults and managed workflows.")

SCENARIOS = [
    {"level": "advanced", "topic": "admission-policy", "q": "After a node pool replacement, nobody can create pods in any namespace and errors mention a webhook timeout.", "a": "A validating or mutating webhook with failurePolicy: Fail has no running backend, possibly because its own pods also need admission. Check `kubectl get validatingwebhookconfigurations` and the webhook Service endpoints, scale the webhook back up or temporarily set failurePolicy Ignore, and exclude kube-system and the webhook namespace via namespaceSelector so it can always restart."},
    {"level": "intermediate", "topic": "quotas-limitranges", "q": "A new Deployment shows READY 0/3 and `kubectl get pods` returns nothing.", "a": "Pods are being rejected at admission. `kubectl describe rs <deploy-hash>` shows FailedCreate events such as 'exceeded quota' or 'must specify limits.memory'. Add requests and limits, add a LimitRange with defaults, or raise the ResourceQuota."},
    {"level": "advanced", "topic": "cluster-autoscaler", "q": "Pods stay Pending for 20 minutes even though the Cluster Autoscaler is installed.", "a": "Check autoscaler logs and its status ConfigMap: node groups may be at max size, no group satisfies the pod's affinity, taints or zonal PVC, the instance type is out of capacity, or requests exceed any node size. Fix constraints, raise max size, or add a suitable node group or Karpenter NodePool."},
    {"level": "intermediate", "topic": "coredns", "q": "An app calling an external API sees intermittent 5-second latency spikes on DNS lookups.", "a": "Typical causes are ndots:5 search expansion plus conntrack races for parallel A/AAAA UDP queries. Use FQDNs with a trailing dot or lower ndots, enable NodeLocal DNSCache, scale CoreDNS, and check the CoreDNS metrics for errors."},
    {"level": "advanced", "topic": "gitops", "q": "Argo CD shows an app permanently OutOfSync on spec.replicas even right after a sync.", "a": "An HPA owns replicas and changes it, so the live value differs from Git. Remove replicas from the manifest or configure ignoreDifferences for /spec/replicas, ideally with server-side apply so field ownership is respected."},
    {"level": "advanced", "topic": "etcd-backup", "q": "Security asks whether a stolen etcd snapshot would expose your database passwords. What do you answer and change?", "a": "Without encryption at rest, Secrets in the snapshot are only base64-encoded, so yes. Enable EncryptionConfiguration with the KMS v2 provider, rewrite all existing Secrets, store snapshots in encrypted, access-restricted storage, and rotate credentials that may already have leaked."},
]


# Extra interview questions for the original hand-built topics, so every topic has at least four.
EXTRA_INTERVIEW = {
    "labels": [
        qa("intermediate", "What selector types does Kubernetes support?", "Equality-based selectors (app=web, tier!=db) and set-based selectors (env in (prod,staging), !canary). Services and ReplicationControllers only support equality-based maps, while Deployments, Jobs and NetworkPolicies support matchLabels plus matchExpressions."),
        qa("advanced", "Why can you not change a Deployment's spec.selector after creation?", "The selector is immutable in apps/v1 because changing it would orphan the existing ReplicaSets and Pods it owns. To change it you create a new Deployment (or delete with --cascade=orphan and recreate), then clean up the old ReplicaSets."),
    ],
    "namespaces": [
        qa("intermediate", "Which resources are not namespaced?", "Cluster-scoped resources such as Nodes, PersistentVolumes, StorageClasses, ClusterRoles, ClusterRoleBindings, CRDs and Namespaces themselves. kubectl api-resources --namespaced=false lists them."),
        qa("advanced", "Are namespaces a security boundary?", "Only partly. They scope names, RBAC, ResourceQuotas and NetworkPolicies, but pods in different namespaces share nodes and the kernel and can talk freely unless a NetworkPolicy blocks it. Strong isolation needs RBAC, NetworkPolicies, Pod Security and sometimes separate node pools or clusters."),
    ],
    "configmaps": [
        qa("advanced", "Do pods see ConfigMap changes automatically?", "Volume-mounted keys are refreshed by the kubelet after a sync delay (unless mounted with subPath), but environment variables are read only at container start. A common pattern is to put a hash of the config in a pod template annotation so a change triggers a rollout."),
    ],
    "secrets": [
        qa("advanced", "How do you keep Secrets safe at rest and in Git?", "Enable etcd encryption at rest with a KMS v2 provider (AES-GCM), restrict get/list on secrets with RBAC, and never commit plain Secret manifests. Use External Secrets, Sealed Secrets or SOPS so Git only holds encrypted or referenced values."),
    ],
    "nodeselector": [
        qa("intermediate", "nodeSelector vs node affinity?", "nodeSelector is a simple exact match on labels, all of which must match. Node affinity adds operators (In, NotIn, Exists, Gt, Lt), OR-ed terms, and a soft preferredDuringScheduling mode with weights."),
    ],
    "node-affinity": [
        qa("advanced", "What does IgnoredDuringExecution mean?", "The rule is only checked at scheduling time. If a node's labels change later, already running pods are not evicted; only new pods are affected."),
    ],
    "pod-affinity": [
        qa("advanced", "Why can required pod anti-affinity hurt large clusters?", "Inter-pod affinity is expensive for the scheduler, roughly proportional to pods times nodes, and a hard anti-affinity with topologyKey hostname caps replicas at the node count, leaving extra pods Pending. topologySpreadConstraints or preferred anti-affinity are often better."),
    ],
    "taints-tolerations": [
        qa("intermediate", "Difference between NoSchedule, PreferNoSchedule and NoExecute?", "NoSchedule blocks new pods without a toleration, PreferNoSchedule is a soft version, and NoExecute also evicts running pods that do not tolerate it (optionally after tolerationSeconds)."),
    ],
    "topology-spread": [
        qa("intermediate", "What do maxSkew and whenUnsatisfiable control?", "maxSkew is the largest allowed difference in matching pods between any two topology domains. whenUnsatisfiable: DoNotSchedule makes it a hard rule, ScheduleAnyway makes the scheduler prefer, but not require, the spread."),
        qa("advanced", "Why might pods still end up unevenly spread?", "Spread is only enforced at scheduling time, so scale-downs, evictions and node failures can leave skew; the descheduler can rebalance. Domains with no eligible nodes, or labelSelectors that do not match the pods, also produce surprising results."),
    ],
    "vpa": [
        qa("advanced", "Can VPA and HPA be used together?", "Not on the same CPU or memory metric, because they fight: VPA raises requests while HPA computes utilisation from those requests. Use HPA on custom or external metrics with VPA on resources, or VPA in recommendation-only mode."),
    ],
    "probes": [
        qa("advanced", "Why should a liveness probe not check downstream dependencies?", "If the database is down, every pod's liveness fails and Kubernetes restarts them all, turning a dependency outage into a cascading restart storm. Liveness should only detect a stuck process; dependency health belongs in readiness."),
    ],
    "pdb": [
        qa("intermediate", "Which disruptions does a PDB protect against?", "Only voluntary disruptions that use the eviction API, such as kubectl drain, cluster autoscaler scale-down and node upgrades. Node crashes, OOM kills and direct pod deletes are not blocked."),
        qa("advanced", "How can a PDB block a node drain forever?", "If minAvailable equals the replica count (or maxUnavailable is 0), no pod can ever be evicted, so drain hangs. Keep at least one allowed disruption and make sure the pods are actually healthy, because unhealthy pods also count against the budget."),
    ],
    "statefulsets": [
        qa("advanced", "What happens to PVCs when you scale a StatefulSet down?", "By default the PVCs are kept so the data survives and is reattached on scale-up. Since Kubernetes 1.27 persistentVolumeClaimRetentionPolicy can delete them on scale-down or on StatefulSet deletion."),
    ],
    "daemonsets": [
        qa("intermediate", "How do DaemonSets run on control-plane or tainted nodes?", "DaemonSet pods only land on tainted nodes if they tolerate the taints, for example node-role.kubernetes.io/control-plane:NoSchedule. Some tolerations such as not-ready and unreachable are added automatically."),
        qa("advanced", "How are DaemonSets updated?", "updateStrategy RollingUpdate replaces pods node by node, limited by maxUnavailable (and maxSurge since 1.25); OnDelete only replaces a pod when you delete it. Monitor with kubectl rollout status ds/<name>."),
    ],
    "jobs": [
        qa("intermediate", "What do completions, parallelism and backoffLimit do?", "completions is how many successful pods are needed, parallelism how many run at once, and backoffLimit how many retries before the Job is marked Failed. activeDeadlineSeconds caps total runtime."),
        qa("advanced", "How do you clean up finished Jobs automatically?", "Set ttlSecondsAfterFinished so the TTL controller deletes the Job and its pods after completion. For CronJobs, successfulJobsHistoryLimit and failedJobsHistoryLimit keep only the last few."),
    ],
    "init-sidecar": [
        qa("intermediate", "How do init containers differ from regular containers?", "They run one at a time to completion before app containers start, and a failure restarts the pod per restartPolicy. They do not support readiness probes and are ideal for migrations, waiting for dependencies or fetching config."),
        qa("advanced", "What are native sidecar containers?", "Since Kubernetes 1.28 an init container with restartPolicy: Always starts before the app containers, keeps running alongside them and is stopped after them. This fixes old sidecar problems such as Jobs never completing because a proxy kept running."),
    ],
    "storage": [
        qa("advanced", "What do the access modes RWO, ROX, RWX and RWOP mean?", "ReadWriteOnce is read-write by one node, ReadOnlyMany is read-only by many nodes, ReadWriteMany is read-write by many nodes, and ReadWriteOncePod is read-write by a single pod. Block storage like EBS is usually RWO; RWX needs a shared filesystem such as EFS or NFS."),
    ],
    "ingress": [
        qa("advanced", "How is TLS configured on an Ingress?", "Reference a kubernetes.io/tls Secret under spec.tls for the host; the controller terminates TLS with it. cert-manager can issue and renew the certificate automatically, and the controller should be configured for TLS 1.3 with modern ciphers."),
    ],
    "network-policy": [
        qa("advanced", "Why does a NetworkPolicy sometimes have no effect?", "NetworkPolicies are enforced by the CNI plugin, so on a CNI without policy support (for example plain flannel) they are silently ignored. Also, policies are additive allow-lists: once a pod is selected, only what some policy allows is permitted."),
    ],
    "rbac": [
        qa("advanced", "How do you check what a ServiceAccount is allowed to do?", "Use kubectl auth can-i --list --as=system:serviceaccount:<ns>:<name>, or check one verb with kubectl auth can-i get secrets --as=... . Review RoleBindings and ClusterRoleBindings that reference it and avoid wildcard verbs or resources."),
    ],
}
