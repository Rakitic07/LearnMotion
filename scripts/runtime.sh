# Sourced by setup_cluster.sh / teardown.sh: picks the container runtime kind should use.
#
# Order: $K8S_PLAYGROUND_RUNTIME (podman|docker), then a running Podman, then a running Docker,
# then whichever CLI is installed. Exports KIND_EXPERIMENTAL_PROVIDER=podman when Podman is chosen.

runtime_running() { "$1" info >/dev/null 2>&1; }

detect_runtime() {
  local want="${K8S_PLAYGROUND_RUNTIME:-}"
  if [ -n "$want" ]; then RUNTIME="$want"
  elif command -v podman >/dev/null 2>&1 && runtime_running podman; then RUNTIME=podman
  elif command -v docker >/dev/null 2>&1 && runtime_running docker; then RUNTIME=docker
  elif command -v podman >/dev/null 2>&1; then RUNTIME=podman
  elif command -v docker >/dev/null 2>&1; then RUNTIME=docker
  else RUNTIME=""
  fi
  if [ "$RUNTIME" = podman ]; then export KIND_EXPERIMENTAL_PROVIDER=podman; fi
}
