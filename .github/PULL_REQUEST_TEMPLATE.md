## Summary

<!-- Briefly describe what this pull request changes and why. -->

## Related Issue

<!-- Fixes #(issue) -->

## Scope & Standards Checklist

- [ ] Every modified or added `.py`, `.js`, `.css`, `.md`, and `.json` source/doc file is `<= 450` lines (`SKILL.md <= 140` lines).
- [ ] Zero `!important` declarations and zero runtime `pip` dependencies introduced.
- [ ] Skills remain 100% portable when copied outside this repository (no repo-root assumptions in `skills/`).
- [ ] Public diff contains no private hostnames, personal identifiers, or proprietary assets.
- [ ] Regenerated derived bundles and verified `0` byte drift:
  - `python3 -B scripts/build_all.py`
  - `python3 -B scripts/build_all.py --check`

## Verification Run Locally

- [ ] `QUIET_SKIP_CDP=1 python3 -B -m unittest discover -s tests -v`
- [ ] `QUIET_REQUIRE_CDP=1 python3 -B -m unittest discover -s tests -v` (or Chrome CDP visual check if UI/CSS changed)
- [ ] `python3 -B skills/quiet-ui/scripts/audit_quiet_html.py quiet-ui-showcase.html`

## Screenshots / Notes

<!-- Attach Retina screenshots if visual presentation, layout, or chart rendering changed. -->
