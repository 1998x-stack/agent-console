# P3 Design Spec — Open SDK/CLI, MCP Connectors, Search Quality & Operations

> DRAFT / CONDITIONAL ROADMAP. Do not build all features simply to complete a checklist. Requires user/usage evidence and P2 security gate where a feature affects multiple users. Plan: [P3](../plans/2026-11-16-p3-ecosystem-plan.md).

## Product Goal

Expose stable, permission-preserving ways for developers to publish and use Skills from CLI/SDK, for Office users to connect external systems through controlled MCP Tools, and for operators to observe, back up, upgrade, and scale the platform without breaking local-first guarantees.

## Scope: Four Optional Capability Families

| Family | Why users need it | Contract to preserve | Priority trigger |
|---|---|---|---|
| CLI / SDK | developer automates installs/releases/tests | same Auth, release digest, idempotency, audit as Web | enough repeated developer workflows |
| MCP / Integrations | Office and Code need external data/tools | scoped OAuth/short credentials, action approval, audit | real connector usage feedback |
| Discovery / Quality | larger market makes exact keyword search weak | compatible/safe filtering first, evaluation signals evidence-based | documented search false negatives |
| Operating Maturity | multi-user instance resources exceed local mode | backup, upgrade, observability, controlled queues | measured load and uptime needs |

## Developer CLI

Commands (proposed; API contracts must be frozen before coding):
- `agent-console login` (device/local login or scoped token, not copy provider API Key);
- `agent-console skills validate [path]`;
- `agent-console skills test [path] --fixture [id]`;
- `agent-console skills publish [path] --scope private|team|public`;
- `agent-console skills install [name] --workspace [id] --version [semver]`;
- `agent-console skills unlist [listing-id]`.

All CLI writes go through API authorization, not direct DB or shared filesystem. CLI must not allow arbitrary on-disk path escape or bypass server version/scan. Offline private validation may run local parser but publishing needs controlled service.

## MCP & External Tool Access

- Tool registration includes server provenance, allowed scopes, network URL policy, auth handler, declared risk level, version.
- Every tool call is linked to current Run/Workspace; L3 actions (email send, GitHub write, ticket mutation) require concrete action approval. Client may revoke connector grants.
- OAuth tokens remain vault-managed; Pi Tool sees only response/short token, not broad operator keys. Prompt injection from external documents must not expand capabilities.
- MCP Server or extension cannot run arbitrary untrusted code in the API/Pi Worker host namespace.
- Offline mode with no connector must still support local Agent/Skill capabilities.

## Discovery

Search improvement is evaluated against a fixed query relevance dataset; baseline BM25/metadata filters before embedding/semantic re-rank. Rank by task fit, actual test success, compatibility and provenance; don't invent downloads, ratings or completion statistics. Safety and ACL are hard filters, not scoring factors that can be traded away.

## Operations & Upgrade

Define capacity budgets, task admission, per-instance worker/memory/disk limits, startup readiness, backup/restore including Pi JSONL, encrypted keys and release blobs, downgrade compatibility checks, and GitHub Actions release evidence. Database, Registry and Pi SDK upgrades need version-pinned compatibility snapshots.

## Failure Stories

- MCP endpoint fails mid-run: explicit WAITING_TOOL/FAILED with safe retries, no secret leak.
- CLI publish retries after lost response: same idempotency key, no duplicate Release.
- Provider or Tool API changes: compatibility contract break detected in CI.
- Search index unavailable: fall back to basic catalog by authorized metadata.
- Pi SDK upgrade makes older Session unreadable: preserve read-only history, explicit migration/rollback plan.
- Work queue overload: reject/backpressure with useful UI, never silently lose jobs.
- Backup restored with missing encryption key: cannot impersonate decrypted model connections; fail safely.

## Acceptance

| AC | Objective evidence |
|---|---|
| P3-AC01 | CLI matches Web access and release semantics, retry is idempotent |
| P3-AC02 | MCP scoped tool calls enforce approvals and do not leak long-lived credentials |
| P3-AC03 | search benchmark demonstrates measured improvement without ACL bypass |
| P3-AC04 | restore and upgrade/downgrade drills include DB+files+sessions+keys+registry |
| P3-AC05 | controlled load test has clear concurrency/latency/resource envelope |
| P3-AC06 | documentation and CLI onboarding allow clean device installation without manual DB changes |

## Gate

Each P3 family can independently be deferred. Stage PASS for implemented, approved families, but never claim “entire ecosystem built” if other families were explicitly excluded. Security and data durability cannot regress from earlier phases.
