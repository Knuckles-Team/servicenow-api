#!/usr/bin/env bash
# One-command contributor setup from a fresh clone. Idempotent and
# non-interactive; safe for people, CI and any AI agent.
#
#   scripts/bootstrap.sh
#
# Installs a current uv, the pinned Python (.python-version, else 3.14), the
# locked environment (`uv sync --locked`, or `uv sync` when the repository
# has no uv.lock yet), and the pre-commit and pre-push git hooks. Then it
# prints the gate command. Set BOOTSTRAP_SKIP_HOOKS=1 to skip hook install.
set -euo pipefail

cd "$(dirname "$0")/.."

log() { printf 'bootstrap: %s\n' "$*"; }
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

case "${1:-}" in
  -h | --help)
    sed -n '2,10p' "$0"
    exit 0
    ;;
  "") ;;
  *)
    echo "unknown argument: $1" >&2
    exit 2
    ;;
esac

# 1. uv + Python ------------------------------------------------------------
# uv older than 0.9 cannot download current CPython patch releases.
uv_minor() { uv --version 2>/dev/null | awk '{split($2, v, "."); print v[1] * 1000 + v[2]}'; }
if ! command -v uv >/dev/null 2>&1 || [[ "$(uv_minor)" -lt 9 ]]; then
  log "installing a current uv"
  python3 -m pip install --quiet --user --upgrade "uv>=0.9" \
    || curl -LsSf https://astral.sh/uv/install.sh | sh
fi
python_version="3.14"
if [ -f .python-version ]; then
  python_version="$(tr -d '[:space:]' < .python-version)"
fi
log "Python ${python_version} (uv $(uv --version | awk '{print $2}'))"
uv python install "$python_version"

# 2. Environment ------------------------------------------------------------
if [ -f uv.lock ]; then
  log "uv sync --locked"
  uv sync --locked --python "$python_version"
else
  log "no uv.lock: uv sync (generate and commit one)"
  uv sync --python "$python_version"
fi

# 3. Git hooks --------------------------------------------------------------
if [ "${BOOTSTRAP_SKIP_HOOKS:-0}" != 1 ] && [ -f .pre-commit-config.yaml ]; then
  log "installing pre-commit and pre-push hooks"
  uvx pre-commit install --hook-type pre-commit --hook-type pre-push >/dev/null
fi

log "done. Gate command: uvx pre-commit run --all-files"
