#!/usr/bin/env bash
set -euo pipefail
CLUSTER_NAME="${K8S_PLAYGROUND_CLUSTER:-k8s-playground}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=runtime.sh
source "$ROOT_DIR/scripts/runtime.sh"
detect_runtime

if ! command -v kind >/dev/null 2>&1; then echo "kind not installed; nothing to delete."; exit 0; fi
if kind get clusters 2>/dev/null | grep -qx "$CLUSTER_NAME"; then
  echo "==> Deleting kind cluster $CLUSTER_NAME (${RUNTIME:-unknown runtime})"
  kind delete cluster --name "$CLUSTER_NAME"
else
  echo "Cluster $CLUSTER_NAME does not exist."
fi
