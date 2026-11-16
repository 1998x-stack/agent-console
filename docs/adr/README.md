# Architecture Decision Records

> No final implementation-specific ADR has been accepted yet. The numbered ADRs described in specs are **proposed decisions** pending PoC and actual test evidence.

## How to write an ADR

Create one file per decision: `YYYY-MM-DD-<topic>.md` containing:
1. Status — Proposed / Accepted / Superseded / Rejected.
2. Context and user problem.
3. Options with measurable trade-offs.
4. Decision and reason.
5. Security/privacy effects.
6. Contracts/migrations/compatibility implications.
7. Experiments and actual evidence.
8. Rollback conditions and date/approver.

A draft cannot be labeled Accepted solely because the plan references it. An architecture disagreement must be documented before competing implementation choices drift.

## Proposed early ADRs

- Pi SDK pinned release and extension/ResourceLoader behavior.
- Web auth + one-time bootstrap + CSRF.
- Provider Base URL/SSRF and local LAN exceptions.
- User Workspace physical mapping and container isolation.
- Pi Model proxy secret delivery.
- Sandboxing mechanism, untrusted scripts and executable extensions.
- PostgreSQL / local file storage backup compatibility.
- Registry immutable digest, installation and Listing lifecycle.

Reference [Phased Plans](../superpowers/README.md), [Risk Register](../functional-decomposition/12_DECISIONS_AND_RISKS.md), [Pi Integration](../PI_AGENT_INTEGRATION.md).
