#!/usr/bin/env bash
# ==============================================================================
# quiet-ui-skills — Dual-Remote 3-2-1 Mirror Synchronizer (GitHub + GitLab)
# License: GNU AGPLv3 + Section 7 NOTICE
# Upstream: https://github.com/FrankXLT/quiet-ui-skills
# Usage:
#   bash scripts/sync_mirrors.sh [--force]
# ==============================================================================
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_DIR}"

FORCE_FLAG=""
if [[ "${1:-}" == "--force" || "${1:-}" == "-f" ]]; then
  FORCE_FLAG="--force"
fi

# Load GITHUB_TOKEN from environment or standard local secret store if present
if [[ -z "${GITHUB_TOKEN:-}" ]]; then
  for env_file in "${HOME}/.config/ag-bridge-mcp/secrets.env" "${HOME}/.config/github/secrets.env"; do
    if [[ -f "${env_file}" ]]; then
      tok="$(grep -E '^(GITHUB_TOKEN|GH_TOKEN)=' "${env_file}" | head -n1 | cut -d= -f2- | tr -d "'\"[:space:]" || true)"
      if [[ -n "${tok}" ]]; then
        export GITHUB_TOKEN="${tok}"
        break
      fi
    fi
  done
fi

BRANCH="$(git rev-parse --abbrev-ref HEAD)"

# 1. Push to primary remote (origin -> GitHub)
if git remote get-url origin >/dev/null 2>&1; then
  ORIGIN_URL="$(git remote get-url origin)"
  if [[ "${ORIGIN_URL}" == *"github.com"* && -n "${GITHUB_TOKEN:-}" ]]; then
    BASIC_AUTH="$(printf 'x-access-token:%s' "${GITHUB_TOKEN}" | base64 -w0)"
    git -c "http.https://github.com/.extraheader=AUTHORIZATION: basic ${BASIC_AUTH}" \
      push ${FORCE_FLAG} origin "${BRANCH}:main"
  else
    git push ${FORCE_FLAG} origin "${BRANCH}:main"
  fi
  echo "[OK] Pushed ${BRANCH} -> origin (${ORIGIN_URL})"
fi

# 2. Push to secondary 3-2-1 mirror remote (gitlab) if configured
if git remote get-url gitlab >/dev/null 2>&1; then
  GITLAB_URL="$(git remote get-url gitlab)"
  git push ${FORCE_FLAG} gitlab "${BRANCH}:main"
  echo "[OK] Pushed ${BRANCH} -> gitlab mirror"
fi
