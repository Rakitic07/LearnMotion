// Content for the mini games. Answers are A-Z only so they fit crossword cells.
export const WORDS = [
  { answer: "POD", term: "Pod", clue: "Smallest deployable unit: one or more containers sharing network and storage" },
  { answer: "NODE", term: "Node", clue: "Worker machine where the kubelet runs pods" },
  { answer: "KUBELET", term: "kubelet", clue: "Node agent that makes sure the containers in a PodSpec are running" },
  { answer: "ETCD", term: "etcd", clue: "Consistent key-value store that holds all cluster state" },
  { answer: "TAINT", term: "Taint", clue: "Applied to a node to repel pods that don't tolerate it" },
  { answer: "TOLERATION", term: "Toleration", clue: "Pod-side permission to land on a tainted node" },
  { answer: "AFFINITY", term: "Affinity", clue: "Rules that attract pods to certain nodes or to other pods" },
  { answer: "CONFIGMAP", term: "ConfigMap", clue: "Non-secret key/value config injected as env vars or files" },
  { answer: "SECRET", term: "Secret", clue: "Object for sensitive data; only base64-encoded unless encryption at rest is on" },
  { answer: "INGRESS", term: "Ingress", clue: "L7 HTTP routing by host and path into Services" },
  { answer: "SERVICE", term: "Service", clue: "Stable virtual IP and DNS name in front of a changing set of pods" },
  { answer: "DEPLOYMENT", term: "Deployment", clue: "Controller for stateless apps with rolling updates and rollbacks" },
  { answer: "REPLICASET", term: "ReplicaSet", clue: "Keeps N identical pods running; owned by a Deployment" },
  { answer: "STATEFULSET", term: "StatefulSet", clue: "Controller giving pods stable names and per-pod volumes" },
  { answer: "DAEMONSET", term: "DaemonSet", clue: "Runs one copy of a pod on every matching node" },
  { answer: "NAMESPACE", term: "Namespace", clue: "Virtual cluster scope for names, quotas and RBAC" },
  { answer: "HPA", term: "HPA", clue: "Autoscaler that changes the replica count from metrics (abbr.)" },
  { answer: "VPA", term: "VPA", clue: "Autoscaler that right-sizes CPU and memory requests (abbr.)" },
  { answer: "PDB", term: "PDB", clue: "Limits voluntary disruptions such as node drains (abbr.)" },
  { answer: "CRONJOB", term: "CronJob", clue: "Creates Jobs on a repeating schedule" },
  { answer: "LIVENESS", term: "Liveness probe", clue: "Probe whose failure makes the kubelet restart the container" },
  { answer: "READINESS", term: "Readiness probe", clue: "Probe that decides whether a pod receives Service traffic" },
  { answer: "SIDECAR", term: "Sidecar", clue: "Helper container running alongside the main app in the same pod" },
  { answer: "KUBECTL", term: "kubectl", clue: "The Kubernetes command-line client" },
  { answer: "HELM", term: "Helm", clue: "Package manager that installs charts" },
  { answer: "KIND", term: "kind", clue: "Runs Kubernetes nodes as containers on your laptop" },
  { answer: "SCHEDULER", term: "Scheduler", clue: "Control-plane component that binds pending pods to nodes" },
  { answer: "CORDON", term: "Cordon", clue: "Mark a node unschedulable without evicting its pods" },
  { answer: "DRAIN", term: "Drain", clue: "Cordon plus evict pods, for example before maintenance" },
  { answer: "SELECTOR", term: "Selector", clue: "Label query used by Services and controllers to find pods" },
  { answer: "ANNOTATION", term: "Annotation", clue: "Non-identifying metadata attached to objects" },
  { answer: "RBAC", term: "RBAC", clue: "Role-based access control (abbr.)" },
  { answer: "QUOTA", term: "ResourceQuota", clue: "Resource____: namespace-wide cap on aggregate usage" },
  { answer: "PVC", term: "PVC", clue: "A pod's claim on persistent storage (abbr.)" },
  { answer: "OPERATOR", term: "Operator", clue: "Custom controller plus CRD that encodes operational knowledge" },
  { answer: "CRD", term: "CRD", clue: "Extends the API with your own resource types (abbr.)" },
  { answer: "EVICTION", term: "Eviction", clue: "Removing a pod from a node, e.g. under memory pressure" },
  { answer: "OOMKILLED", term: "OOMKilled", clue: "Reason shown when a container exceeds its memory limit" },
  { answer: "NODEPORT", term: "NodePort", clue: "Service type that opens the same port on every node" },
  { answer: "CLUSTERIP", term: "ClusterIP", clue: "Default Service type, reachable only inside the cluster" },
  { answer: "COREDNS", term: "CoreDNS", clue: "The cluster DNS server" },
  { answer: "ROLLOUT", term: "Rollout", clue: "kubectl ____ undo deploy/web" },
  { answer: "LIMITS", term: "Limits", clue: "Hard ceiling on CPU or memory for a container" },
  { answer: "REQUESTS", term: "Requests", clue: "Resources the scheduler reserves for a container" },
  { answer: "INITCONTAINER", term: "Init container", clue: "Runs to completion before the app containers start" },
  { answer: "APISERVER", term: "API server", clue: "Front door of the control plane; every request goes through it" },
  { answer: "CONTROLLER", term: "Controller", clue: "Reconcile loop that drives actual state toward desired state" },
];

export const RUSH = [
  { task: "Scale deployment web to 5 replicas", answer: "kubectl scale deploy/web --replicas=5", wrong: ["kubectl set replicas web 5", "kubectl autoscale deploy/web --replicas=5", "kubectl edit replicas web=5"] },
  { task: "Roll back the last rollout of web", answer: "kubectl rollout undo deploy/web", wrong: ["kubectl rollback deploy/web", "kubectl rollout revert deploy/web", "kubectl undo deployment web"] },
  { task: "Watch a rollout until it finishes", answer: "kubectl rollout status deploy/web", wrong: ["kubectl get rollout web -w", "kubectl describe rollout web", "kubectl logs deploy/web --rollout"] },
  { task: "Logs from the previous (crashed) container", answer: "kubectl logs web-0 --previous", wrong: ["kubectl logs web-0 --last", "kubectl describe pod web-0 --logs", "kubectl logs web-0 --crashed"] },
  { task: "Mark node worker2 unschedulable", answer: "kubectl cordon worker2", wrong: ["kubectl drain worker2 --soft", "kubectl taint worker2 off", "kubectl label node worker2 schedulable=false"] },
  { task: "Evict pods from worker2 for maintenance", answer: "kubectl drain worker2 --ignore-daemonsets", wrong: ["kubectl cordon worker2 --evict", "kubectl delete node worker2", "kubectl evict worker2 --all"] },
  { task: "Add label disk=ssd to node worker1", answer: "kubectl label node worker1 disk=ssd", wrong: ["kubectl annotate node worker1 disk=ssd", "kubectl set label worker1 disk=ssd", "kubectl tag node worker1 disk=ssd"] },
  { task: "Taint worker3 so only GPU-tolerating pods land there", answer: "kubectl taint node worker3 gpu=true:NoSchedule", wrong: ["kubectl label node worker3 gpu:NoSchedule", "kubectl cordon worker3 --taint gpu", "kubectl taint node worker3 gpu=true:NoSchedule-"] },
  { task: "Remove that GPU taint from worker3", answer: "kubectl taint node worker3 gpu=true:NoSchedule-", wrong: ["kubectl untaint node worker3 gpu", "kubectl taint node worker3 --remove gpu", "kubectl delete taint worker3 gpu"] },
  { task: "Open a shell inside pod api", answer: "kubectl exec -it api -- sh", wrong: ["kubectl attach api sh", "kubectl run -it api sh", "kubectl ssh api"] },
  { task: "Forward local port 8080 to service web port 80", answer: "kubectl port-forward svc/web 8080:80", wrong: ["kubectl expose svc/web 8080:80", "kubectl proxy svc/web 8080", "kubectl forward svc/web 80:8080"] },
  { task: "Autoscale web between 2 and 10 replicas at 50% CPU", answer: "kubectl autoscale deploy/web --min=2 --max=10 --cpu-percent=50", wrong: ["kubectl scale deploy/web --min=2 --max=10", "kubectl hpa create web 2 10 50", "kubectl set autoscale web --cpu=50"] },
  { task: "Show live CPU and memory usage of pods", answer: "kubectl top pods", wrong: ["kubectl get pods --usage", "kubectl describe pods --metrics", "kubectl stats pods"] },
  { task: "Read the docs for pod.spec.affinity in the terminal", answer: "kubectl explain pod.spec.affinity", wrong: ["kubectl describe pod.spec.affinity", "kubectl help pod.spec.affinity", "kubectl docs affinity"] },
  { task: "Create ConfigMap app with LOG_LEVEL=debug", answer: "kubectl create configmap app --from-literal=LOG_LEVEL=debug", wrong: ["kubectl create secret app --from-literal=LOG_LEVEL=debug", "kubectl set env cm/app LOG_LEVEL=debug", "kubectl apply configmap app LOG_LEVEL=debug"] },
  { task: "Restart every pod of deployment web without changing the spec", answer: "kubectl rollout restart deploy/web", wrong: ["kubectl restart deploy/web", "kubectl delete deploy/web --restart", "kubectl rollout redo deploy/web"] },
  { task: "Check whether you may delete pods in namespace dev", answer: "kubectl auth can-i delete pods -n dev", wrong: ["kubectl rbac check delete pods -n dev", "kubectl get roles --can delete", "kubectl whoami delete pods"] },
  { task: "List recent events, oldest to newest", answer: "kubectl get events --sort-by=.lastTimestamp", wrong: ["kubectl logs events --sort", "kubectl describe events --latest", "kubectl get events --order=time"] },
  { task: "Print Deployment YAML without creating anything", answer: "kubectl create deploy web --image=nginx --dry-run=client -o yaml", wrong: ["kubectl get deploy web -o yaml --new", "kubectl apply deploy web --image=nginx --preview", "kubectl run web --image=nginx --yaml-only"] },
  { task: "Make dev the default namespace of the current context", answer: "kubectl config set-context --current --namespace=dev", wrong: ["kubectl namespace use dev", "kubectl config use-namespace dev", "kubectl set ns dev"] },
  { task: "List pods together with their node and IP", answer: "kubectl get pods -o wide", wrong: ["kubectl get pods --nodes", "kubectl describe pods --ip", "kubectl get pods -o nodes"] },
  { task: "Preview what applying app.yaml would change", answer: "kubectl diff -f app.yaml", wrong: ["kubectl apply -f app.yaml --compare", "kubectl get -f app.yaml --diff", "kubectl check -f app.yaml"] },
  { task: "Show only pods labelled app=web", answer: "kubectl get pods -l app=web", wrong: ["kubectl get pods --label app=web", "kubectl get pods app=web", "kubectl find pods -l app=web"] },
  { task: "See why a pod is Pending", answer: "kubectl describe pod web-0", wrong: ["kubectl logs web-0 --pending", "kubectl get pod web-0 --why", "kubectl explain pod web-0"] },
];

// `bug` lists the 0-based line(s) that cause the symptom.
export const BUGS = [
  {
    symptom: "Traffic never reaches the pods. The Deployment's pods are labelled app: web.",
    yaml: `apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  selector:
    app: frontend
  ports:
    - port: 80
      targetPort: 8080`,
    bug: [6],
    why: "The Service selector must match pod labels. app: frontend selects nothing, so the Service has no endpoints (check with kubectl get endpoints web).",
  },
  {
    symptom: "The node is tainted dedicated=gpu:NoSchedule, yet this pod stays Pending.",
    yaml: `spec:
  tolerations:
    - key: dedicated
      operator: Equal
      value: gpu
      effect: NoExecute
  containers:
    - name: train
      image: trainer:1.0`,
    bug: [5],
    why: "A toleration matches a taint only if the effect matches too. The taint is NoSchedule, so the toleration needs effect: NoSchedule (or omit effect to match all effects).",
  },
  {
    symptom: "The pod is Running but never becomes Ready. The app listens on 8080.",
    yaml: `containers:
  - name: api
    image: api:2.1
    ports:
      - containerPort: 8080
    readinessProbe:
      httpGet:
        path: /healthz
        port: 80`,
    bug: [8],
    why: "The readiness probe hits port 80 where nothing listens, so it keeps failing and the pod is never added to Service endpoints. Use port: 8080 (or a named port).",
  },
  {
    symptom: "Nodes are labelled disktype=ssd, but the pod stays Pending.",
    yaml: `spec:
  nodeSelector:
    disk-type: ssd
  containers:
    - name: db
      image: postgres:16`,
    bug: [2],
    why: "nodeSelector keys must match exactly. disk-type ≠ disktype, so no node matches. kubectl describe pod shows: 0/3 nodes are available: didn't match node selector.",
  },
  {
    symptom: "kubectl apply fails: selector does not match template labels.",
    yaml: `apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web-app
    spec:
      containers:
        - name: web
          image: nginx:1.27`,
    bug: [12, 8],
    why: "spec.selector.matchLabels must be a subset of the pod template labels. app: web vs app: web-app do not match, and the selector is immutable after creation.",
  },
  {
    symptom: "The container is OOMKilled under normal load. It needs about 300Mi.",
    yaml: `resources:
  requests:
    cpu: 100m
    memory: 64Mi
  limits:
    cpu: 500m
    memory: 128Mi`,
    bug: [6],
    why: "The memory limit is the hard ceiling. Exceeding 128Mi gets the container killed (exit code 137). Raise the limit, and set requests close to real usage so scheduling is honest.",
  },
  {
    symptom: "The pod fails with CreateContainerConfigError: couldn't find key LOG_LEVEL in ConfigMap app-config.",
    yaml: `apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  log_level: debug
---
env:
  - name: LOG_LEVEL
    valueFrom:
      configMapKeyRef:
        name: app-config
        key: LOG_LEVEL`,
    bug: [12, 5],
    why: "ConfigMap keys are case-sensitive. The data key is log_level but the pod asks for LOG_LEVEL. Make them match, or mark the ref optional: true.",
  },
  {
    symptom: "kubectl drain hangs forever. The Deployment has 2 replicas.",
    yaml: `apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: web-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: web`,
    bug: [5],
    why: "With 2 replicas and minAvailable: 2, zero voluntary evictions are allowed, so drain retries forever. Use minAvailable: 1 or maxUnavailable: 1 (or run more replicas).",
  },
  {
    symptom: "Pods go Pending when zone-a is full. They should only prefer zone-a.",
    yaml: `affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
        - matchExpressions:
            - key: topology.kubernetes.io/zone
              operator: In
              values: [zone-a]`,
    bug: [2],
    why: "required… is a hard filter. A soft preference needs preferredDuringSchedulingIgnoredDuringExecution with a weight and a preference block.",
  },
  {
    symptom: "Clients get connection refused through the Service. The container listens on 3000.",
    yaml: `apiVersion: v1
kind: Service
metadata:
  name: api
spec:
  selector:
    app: api
  ports:
    - port: 80
      targetPort: 8080`,
    bug: [9],
    why: "targetPort is the container port the Service forwards to. It should be 3000. port: 80 is just what clients dial.",
  },
];

export const META = { rushLabel: "kubectl Rush", rushIntro: "Pick the command that does the job.", rushMono: true, bugLabel: "YAML Bug Hunt", bugNoun: "symptom" };
