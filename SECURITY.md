# Security Policy

## Supported versions

EGX_Terminal has no release yet. Only the latest published commit on `main` will be
examined. Archived experiments are evidence, not supported versions. After the
first release, this policy may evolve to cover the latest release and `main`;
no long-term support is promised.

## Reporting a vulnerability

Do not open a public issue or publish a proof containing a secret. Use GitHub's
[private vulnerability report](https://github.com/ElGrandeXu/EGX_Terminal/security/advisories/new)
for `ElGrandeXu/EGX_Terminal`. Reports should state the impact, a minimal
reproduction, and the affected commit, with personal data and logs redacted.

Private Vulnerability Reporting is active. The project does not publish a
personal security address as a substitute for that private channel.

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
