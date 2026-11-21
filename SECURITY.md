# Security Policy

## Supported Versions

| Version | Supported | Notes |
| :--- | :---: | :--- |
| `9.1.x` | Yes | Active release line (portable skills, unified `tests/`, CI CDP gates) |
| `9.0.x` | Security fixes only | Prior v9 release; upgrade to `9.1.x` recommended |
| `<= 8.x` | No | Legacy architecture retired |

---

## Security Posture & Design Guarantees

Quiet UI Skills is engineered to run safely in air-gapped, regulated, and agentic environments:

- **Zero External CDN Runtime Fetches**: Compiled HTML showcases, Component Library bundles, and standalone `compile_evidence.py` documents make zero requests to third-party CDNs.
- **AST-Only Equation Evaluation**: Analytical plot expressions in `skills/quiet-evidence/scripts/compilers/math_eval.py` are parsed via Python `ast` over a strict mathematical whitelist (`+`, `-`, `*`, `/`, `**`, `sin`, `cos`, `exp`, `log`, `sqrt`), rejecting arbitrary code execution, attribute access, and exponential DoS bounds.
- **HTML/SVG Escaping & Token Allowlisting**: Compiler strings pass through strict HTML escaping (`esc()`) and color/CSS token sanitization (`resolve_token()`).
- **EXIF-Stripped Public-Domain Media**: All backplate JPEGs in `docs/assets/` are verified EXIF-free (`0` camera/GPS metadata).

---

## Reporting a Vulnerability

**Please do not open a public GitHub issue for security vulnerabilities.**

Report security issues privately via GitHub Private Vulnerability Reporting:

- **GitHub Security Advisories**: [https://github.com/FrankXLT/quiet-ui-skills/security/advisories/new](https://github.com/FrankXLT/quiet-ui-skills/security/advisories/new)

Include:
1. Affected file(s), version, or compiler schema input.
2. Minimal reproduction steps or JSON/HTML payload.
3. Expected vs. observed impact (e.g., XSS bypass, AST DoS vector, path traversal).

Maintainers target acknowledgment within **72 hours** and a coordinated remediation plan before public disclosure.
