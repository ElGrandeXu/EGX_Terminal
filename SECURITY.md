# Security Policy

## Supported versions

At the 2026-07-22 pretransition checkpoint
`23cd5c596159fda6866e0fdc6ef0ba7bcf0d2515`, the canonical repository had no
published release or Git tag. The guarded transition does not authorize either.
Historical `v1.0.0` was withdrawn during privacy remediation and is not a
downloadable supported release. No long-term-support window or backport promise
is made. Archived experiments are research evidence, not supported products or
independently supported versions.

## Reporting a vulnerability

Do not open a public issue or publish a proof containing a secret. During
`PUBLICATION_TRANSITION`, effective visibility and reporting availability must
be verified directly on GitHub; this document does not infer them.

The executable transition sequence starts with a private-repository preflight,
changes the repository to public, immediately activates Private Vulnerability
Reporting, and then mechanically verifies its accessibility. Before successful
activation and verification, the project claims no active confidential
reporting channel and is not considered shareable. If activation or verification
fails, the transition stops with that non-shareable status. No personal address
is published as a fallback.

Once PVR is verified active, GitHub's
[private vulnerability report](https://github.com/ElGrandeXu/EGX_Terminal/security/advisories/new)
is the recommended reporting channel for `ElGrandeXu/EGX_Terminal`. Reports
should state the impact, a minimal reproduction, and the affected commit, with
personal data and logs redacted.

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
