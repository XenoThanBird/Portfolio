# Security Policy

## Scope

This repository is a personal AI/ML portfolio published for demonstration and
review purposes. It is not a supported product and carries no service-level
commitments. All datasets, catalogs, and fixtures in this repository are
synthetic; the code is not connected to any production system.

## Reporting a Vulnerability

If you find a security issue in this repository — a leaked credential, a
dependency vulnerability, or a flaw in one of the security-focused modules
(sections 09–10) — please report it privately:

- **Email**: [bird.matthan@gmail.com](mailto:bird.matthan@gmail.com)

Please do not open a public issue for suspected credential leaks. Reports are
typically acknowledged within a few days.

## Secret Hygiene

- No real credentials, API keys, or tokens are committed to this repository.
  Configuration secrets are supplied via gitignored `.env` files; each module
  documents its required variables in a `.env.template`.
- Continuous integration runs a [gitleaks](https://github.com/gitleaks/gitleaks)
  scan on every push and pull request.
- A local pre-commit hook configuration is provided in
  `.pre-commit-config.yaml` (`pip install pre-commit && pre-commit install`).
