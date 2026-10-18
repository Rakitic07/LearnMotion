#!/usr/bin/env bash
# Creates the local "k8s-playground" kind cluster used by the web app.
#
# Usage: scripts/setup_cluster.sh [--with-ingress] [--with-vpa] [--recreate]
set -euo pipefail

CLUSTER_NAME="${K8S_PLAYGROUND_CLUSTER:-k8s-playground}"
CONTEXT="kind-${CLUSTER_NAME}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WITH_INGRESS=false
WITH_VPA=false
RECREATE=false

for arg in "$@"; do
  case "$arg" in
    --with-ingress) WITH_INGRESS=true ;;
    --with-vpa) WITH_VPA=true ;;
    --recreate) RECREATE=true ;;
    *) echo "Unknown flag: $arg" >&2; exit 2 ;;
  esac
done

step() { printf '\n==> %s\n' "$*"; }
k() { kubectl --context "$CONTEXT" "$@"; }

# shellcheck source=runtime.sh
source "$ROOT_DIR/scripts/runtime.sh"

step "Checking prerequisites"
detect_runtime
if [ -z "$RUNTIME" ]; then
  cat >&2 <<'EOF'
No container runtime found. Install Podman (recommended) or Docker, then re-run:
  - Podman:  brew install podman   (or the installer from podman.io)
             podman machine init --rootful --cpus 4 --memory 8192 && podman machine start
  - Docker:  brew install --cask docker   (then open Docker.app)
EOF
  exit 1
fi
if ! runtime_running "$RUNTIME"; then
  if [ "$RUNTIME" = podman ]; then
    cat >&2 <<'EOF'
Podman is installed but its VM is not running (or is stuck "starting"). Try:
  podman machine stop; podman machine start
No machine yet?  podman machine init --rootful --cpus 4 --memory 8192 && podman machine start
EOF
  else
    echo "Docker is installed but the daemon is not running. Start Docker Desktop." >&2
  fi
  exit 1
fi
if [ "$RUNTIME" = podman ] && [ "$(podman info --format '{{.Host.Security.Rootless}}' 2>/dev/null)" = "true" ]; then
  cat >&2 <<'EOF'
WARNING: the Podman machine is rootless. kind is far more reliable on a rootful machine:
  podman machine stop && podman machine set --rootful && podman machine start
Continuing anyway...
EOF
fi
if ! command -v kubectl >/dev/null 2>&1; then
  if command -v brew >/dev/null 2>&1; then brew install kubectl; else echo "Install kubectl: https://kubernetes.io/docs/tasks/tools/" >&2; exit 1; fi
fi
if ! command -v kind >/dev/null 2>&1; then
  if command -v brew >/dev/null 2>&1; then
    step "Installing kind via Homebrew"
    brew install kind
  else
    echo "Install kind: https://kind.sigs.k8s.io/docs/user/quick-start/#installation" >&2
    exit 1
  fi
fi
echo "$RUNTIME: $("$RUNTIME" version --format '{{.Server.Version}}' 2>/dev/null || "$RUNTIME" --version)  kind: $(kind version)  kubectl: $(kubectl version --client -o yaml | awk '/gitVersion/{print $2; exit}')"

if kind get clusters 2>/dev/null | grep -qx "$CLUSTER_NAME"; then
  if [ "$RECREATE" = true ]; then
    step "Deleting existing cluster $CLUSTER_NAME"
    kind delete cluster --name "$CLUSTER_NAME"
  else
    echo "Cluster $CLUSTER_NAME already exists (use --recreate to rebuild). Re-applying labels/add-ons."
  fi
fi

if ! kind get clusters 2>/dev/null | grep -qx "$CLUSTER_NAME"; then
  step "Creating kind cluster $CLUSTER_NAME (1 control-plane + 3 workers)"
  kind create cluster --name "$CLUSTER_NAME" --config "$ROOT_DIR/kind/kind-config.yaml" --wait 180s
fi

step "Labelling and tainting worker nodes for scheduling labs"
W1="${CLUSTER_NAME}-worker"
W2="${CLUSTER_NAME}-worker2"
W3="${CLUSTER_NAME}-worker3"
k label node "$W1" topology.kubernetes.io/zone=zone-a disktype=ssd tier=frontend --overwrite
k label node "$W2" topology.kubernetes.io/zone=zone-b disktype=hdd tier=backend --overwrite
k label node "$W3" topology.kubernetes.io/zone=zone-c disktype=ssd gpu=true --overwrite
k taint node "$W3" dedicated=gpu:NoSchedule --overwrite
k get nodes -L topology.kubernetes.io/zone,disktype,gpu,tier

step "Installing metrics-server (required for HPA / kubectl top)"
k apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
# kind kubelets use self-signed serving certs; skipping kubelet TLS verification is acceptable ONLY for this local cluster.
if ! k -n kube-system get deploy metrics-server -o jsonpath='{.spec.template.spec.containers[0].args}' | grep -q -- '--kubelet-insecure-tls'; then
  k -n kube-system patch deployment metrics-server --type=json \
    -p '[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'
fi
k -n kube-system rollout status deployment/metrics-server --timeout=180s

if [ "$WITH_INGRESS" = true ]; then
  step "Installing ingress-nginx (kind provider)"
  k apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
  k -n ingress-nginx wait --for=condition=Ready pod -l app.kubernetes.io/component=controller --timeout=240s
  echo "Ingress reachable at http://localhost:8081"
fi

if [ "$WITH_VPA" = true ]; then
  step "Installing Vertical Pod Autoscaler (upstream hack/vpa-up.sh)"
  command -v git >/dev/null 2>&1 || { echo "git is required for VPA install" >&2; exit 1; }
  TMP_DIR="$(mktemp -d)"
  trap 'rm -rf "$TMP_DIR"' EXIT
  git clone --depth 1 https://github.com/kubernetes/autoscaler.git "$TMP_DIR/autoscaler"
  kubectl config use-context "$CONTEXT"
  (cd "$TMP_DIR/autoscaler/vertical-pod-autoscaler" && ./hack/vpa-up.sh)
  k -n kube-system get pods -l 'app in (vpa-recommender,vpa-updater,vpa-admission-controller)'
fi

step "Done! Context: $CONTEXT"
k get nodes -o wide
