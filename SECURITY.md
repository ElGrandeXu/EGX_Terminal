# Security Policy

## Supported versions

There is currently no published release or Git tag. The private canonical
`main` branch is examined on a best-effort basis. Historical `v1.0.0` was
withdrawn during privacy remediation and is not a downloadable supported
release. No long-term-support window or backport promise is made. Archived
experiments are research evidence, not supported products or independently
supported versions.

## Reporting a vulnerability

Do not open a public issue or publish a proof containing a secret. Use GitHub's
[private vulnerability report](https://github.com/ElGrandeXu/EGX_Terminal/security/advisories/new)
for `ElGrandeXu/EGX_Terminal` only after that feature is enabled. Reports should
state the impact, a minimal reproduction, and the affected commit, with personal
data and logs redacted.

Private Vulnerability Reporting is currently unavailable while the repository
is private. The project does not invent or publish a personal security address
as a substitute. Enabling and verifying Private Vulnerability Reporting is a
required gate before any public publication; until then, this policy does not
claim that a confidential GitHub reporting channel is active.

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
