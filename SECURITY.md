# Security Policy

## Supported versions

The canonical repository is public. No Git tag or GitHub release is active;
historical `v1.0.0` was withdrawn during privacy remediation and is not a
supported release. No long-term-support window or backport promise is made.
Current support concerns the canonical `main` branch. Archived experiments are
research evidence, not supported products.

## Reporting a vulnerability

Private Vulnerability Reporting (PVR) is active. Use GitHub's
[private vulnerability report](https://github.com/ElGrandeXu/EGX_Terminal/security/advisories/new)
as the recommended confidential reporting channel for
`ElGrandeXu/EGX_Terminal`.

Do not open a public issue containing a secret or publish a proof that exposes
one. Reports should include:

- the impact;
- a minimal reproduction;
- the affected commit; and
- sanitized data and logs.

Historically, confidential reporting was activated and verified as part of the
controlled public-transition sequence. The dated transition and rollback record
is preserved in the [publication documents](docs/publication/).

## Scope

Security reports include secret exposure, defects in repository scanners,
neutral-root bypasses, unexpected execution, undetected provenance or license
changes, GitHub Actions workflow vulnerabilities, and accidentally tracked
private artifacts.

Out of scope are generic vulnerabilities in OpenCode, Ollama, Qwen, or another
third-party project unless EGX_Terminal integrates it incorrectly; weak
experimental results; feature requests; and purely editorial problems without
security impact.

## Response expectations

Reports are acknowledged and handled on a best-effort basis, without a response
or remediation SLA. Coordinated disclosure will be used when appropriate. A
reporter is credited only with their consent.
