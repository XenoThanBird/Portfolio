# Portfolio Remediation — Task Tracker

Local working file — not committed. Phase discipline per remediation brief.

## Phase 0 — Reproduce the audit (2026-08-13)
- [x] Compile check (4 broken files confirmed)
- [x] CI absence confirmed
- [x] Secret scan clean (brief patterns + gh/slack tokens + private keys)
- [x] Correction: toolkit_starter_notebook.py breaks on U+2028 chars + embedded SQL/YAML/prose, not fences
- [x] Restored 28 accidentally deleted Vue files (owner-approved)
- [x] Owner removed stray personal file from repo root

## Phase 1 — Hotfix (branch: fix/repo-hygiene)
- [x] Fix 3 fence-broken files in 04_nlp_tools (module docstrings)
- [x] Fix toolkit_starter_notebook.py (strip U+2028, comment non-Python content, docstring)
- [x] CLAUDE.md → 12 sections, real tree, sections 11/12 summaries
- [x] README bio (from owner CV, PMC title) + removed unsourced $3.53B claim
- [x] requirements.txt installability (postal → manual, mcp → py3.10+ marker)
- [x] CI workflow (3.9/3.11 matrix, compileall, ruff --exit-zero, gitleaks)
- [x] SECURITY.md + .pre-commit-config.yaml (gitleaks hook)
- [x] Commit + report to owner (PR #2, 5 commits)
- [x] CI green on PR #2 — all 6 checks pass (Build 3.9: 3m19s, 3.11: 2m27s, gitleaks, CodeQL ×3)
- [ ] Owner merges PR #2 → CI green on main

## Phase 1 review
- 11 files changed across 5 conventional commits; no logic refactors.
- Extra root cause found beyond audit: python-nmap>=1.6.0 was unsatisfiable
  (latest PyPI release is 0.7.1) — master requirements were never installable.

## Phase 2 — Restructure (NOT STARTED — dry-run plan requires owner approval)
## Phase 3 — Agent Governance Kit (NOT STARTED — ask owner re: existing private impl)
## Phase 4 — Value Model + Registry (NOT STARTED)
## Phase 5 — Hub README (NOT STARTED)

## Lessons learned
- Audit briefs can misdiagnose root causes (fences vs U+2028) — always reproduce before fixing.
- `pip install postal` can never succeed without system libpostal — check native deps before wiring installs into CI.
