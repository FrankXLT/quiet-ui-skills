#!/usr/bin/env bash
# ==============================================================================
# quiet-ui-skills — 1-Command Installer for visual-architecture-system (v4.5)
# License: GNU AGPLv3 + Section 7 NOTICE (Unconditional Commercial UI Output
#          Exemption; tokens/quiet-ui-tokens.css dual-licensed MIT)
# Upstream: https://github.com/FrankXLT/quiet-ui-skills
# Usage:
#   bash install.sh                  # Installs to ~/.agents/skills & ~/.gemini/config/skills
#   bash install.sh /custom/target   # Installs to /custom/target
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_SKILL_DIR="${SCRIPT_DIR}/skills/visual-architecture-system"

if [[ ! -d "${SRC_SKILL_DIR}" ]]; then
  echo "[ERROR] Source skill directory not found: ${SRC_SKILL_DIR}" >&2
  exit 1
fi

install_to_target() {
  local dest="$1"
  mkdir -p "${dest}/references" "${dest}/scripts"
  cp -f "${SRC_SKILL_DIR}/SKILL.md" "${dest}/SKILL.md"
  cp -f "${SRC_SKILL_DIR}/references/"*.md "${dest}/references/"
  cp -f "${SRC_SKILL_DIR}/scripts/verify_visual_contract.py" "${dest}/scripts/verify_visual_contract.py"
  chmod +x "${dest}/scripts/verify_visual_contract.py"
  echo "[OK] Installed visual-architecture-system v4.5 -> ${dest}"
}

if [[ $# -ge 1 ]]; then
  install_to_target "$1"
else
  install_to_target "${HOME}/.agents/skills/visual-architecture-system"
  install_to_target "${HOME}/.gemini/config/skills/visual-architecture-system"
fi
