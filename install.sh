#!/usr/bin/env bash
# ==============================================================================
# quiet-ui-skills — 1-Command Installer for Quiet UI v9.2.0 Plugin & 3 Skills
# Bundles:
#   1. Antigravity Native Plugin -> ~/.gemini/config/plugins/quiet-ui-skills
#   2. Cross-Agent Skills        -> ~/.agents/skills/{quiet-ui,quiet-evidence,quiet-bridge}
# License: Apache 2.0 (Core Plugin) + MIT (Customizations, Tokens & Output)
# Upstream: https://github.com/FrankXLT/quiet-ui-skills
# Usage:
#   bash install.sh                  # Default plugin + 3-pillar cross-agent install
#   bash install.sh /custom/skills   # Installs all 3 pillar skills into dir
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UI_SKILL_SRC="${SCRIPT_DIR}/skills/quiet-ui"
EV_ASSETS_SRC="${SCRIPT_DIR}/skills/quiet-evidence/assets"
PILLAR_SKILLS=("quiet-ui" "quiet-evidence" "quiet-bridge")

for sk in "${PILLAR_SKILLS[@]}"; do
  if [[ ! -d "${SCRIPT_DIR}/skills/${sk}" ]]; then
    echo "[ERROR] Missing skill directory: ${SCRIPT_DIR}/skills/${sk}" >&2
    exit 1
  fi
done

if [[ ! -f "${EV_ASSETS_SRC}/quiet-evidence-bundle.css" || ! -f "${UI_SKILL_SRC}/scripts/audit_quiet_html.py" || ! -f "${UI_SKILL_SRC}/scripts/audit_quiet_checks.py" ]]; then
  echo "[ERROR] Missing portable skill assets or auditor modules; run python3 -B scripts/build_all.py first." >&2
  exit 1
fi

copy_clean_tree() {
  local src="$1"
  local dst="$2"
  local src_real dst_real
  src_real="$(cd "${src}" && pwd -P)"
  mkdir -p "${dst}"
  dst_real="$(cd "${dst}" && pwd -P)"
  if [[ "${src_real}" == "${dst_real}" ]]; then
    echo "[ERROR] Refusing self-overwrite on source skill directory: ${dst_real}" >&2
    exit 1
  fi
  rm -rf "${dst}"
  mkdir -p "${dst}"
  cp -R "${src}/." "${dst}/"
  find "${dst}" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
  if [[ -d "${dst}/scripts" ]]; then
    find "${dst}/scripts" -maxdepth 1 -type f -name "*.py" -exec chmod +x {} +
  fi
}

install_plugin_bundle() {
  local plugin_dest="$1"
  rm -rf "${plugin_dest}"
  mkdir -p "${plugin_dest}/assets" "${plugin_dest}/tokens" "${plugin_dest}/skills"
  cp -f "${SCRIPT_DIR}/plugin.json" "${plugin_dest}/plugin.json"
  cp -f "${SCRIPT_DIR}/assets/logo.svg" "${plugin_dest}/assets/logo.svg"
  cp -f "${SCRIPT_DIR}/tokens/quiet-ui-tokens.css" "${plugin_dest}/tokens/quiet-ui-tokens.css"
  for doc in LICENSE NOTICE TRADEMARKS.md THIRD_PARTY_LICENSES.md llms.txt AGENTS.md; do
    [[ -f "${SCRIPT_DIR}/${doc}" ]] && cp -f "${SCRIPT_DIR}/${doc}" "${plugin_dest}/${doc}"
  done
  for sk in "${PILLAR_SKILLS[@]}"; do
    copy_clean_tree "${SCRIPT_DIR}/skills/${sk}" "${plugin_dest}/skills/${sk}"
  done
  echo "[OK] Installed Antigravity Plugin Quiet UI Skills v9.2.0 -> ${plugin_dest}"
}

if [[ $# -ge 1 ]]; then
  TARGET_ROOT="${1%/}"
  if [[ "${TARGET_ROOT}" == */plugins/quiet-ui-skills || "${TARGET_ROOT}" == "plugins/quiet-ui-skills" ]]; then
    install_plugin_bundle "${TARGET_ROOT}"
  else
    mkdir -p "${TARGET_ROOT}"
    for sk in "${PILLAR_SKILLS[@]}"; do
      copy_clean_tree "${SCRIPT_DIR}/skills/${sk}" "${TARGET_ROOT}/${sk}"
    done
    echo "[OK] Installed 3 pillar skills v9.2.0 -> ${TARGET_ROOT}"
  fi
else
  # 1. Purge only repo-owned legacy loose skill directories so they never shadow the plugin
  for legacy in "${PILLAR_SKILLS[@]}"; do
    rm -rf "${HOME}/.gemini/config/skills/${legacy}" "${HOME}/.agents/skills/${legacy}"
  done

  # 2. Install native Antigravity plugin bundle
  install_plugin_bundle "${HOME}/.gemini/config/plugins/quiet-ui-skills"

  # 3. Install cross-agent standalone skills (Claude Code, Cursor, Codex, Windsurf)
  mkdir -p "${HOME}/.agents/skills"
  for sk in "${PILLAR_SKILLS[@]}"; do
    copy_clean_tree "${SCRIPT_DIR}/skills/${sk}" "${HOME}/.agents/skills/${sk}"
  done
  echo "[OK] Installed standalone skills -> ${HOME}/.agents/skills/{quiet-ui,quiet-evidence,quiet-bridge}"
fi
