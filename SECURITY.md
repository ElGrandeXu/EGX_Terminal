# Security Policy

## Supported versions

EGX_Terminal is pre-release. Only the latest published commit on `main` will be
examined. Archived experiments are evidence, not supported versions. After the
first release, this policy may evolve to cover the latest release and `main`;
no long-term support is promised.

## Reporting a vulnerability

Do not open a public issue or publish a proof containing a secret. Before the
repository becomes public, GitHub Private Vulnerability Reporting / Security
Advisories will be enabled for `ElGrandeXu/EGX_Terminal`. Reports should state
the impact, a minimal reproduction, and the affected version or commit, with
personal data and logs redacted.

Private Vulnerability Reporting is not yet available because the remote
repository has not been created. Until it is enabled, do not disclose the issue
publicly. The project does not invent or publish a personal security address as
a substitute; enabling the private channel is a gate before public visibility.

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
