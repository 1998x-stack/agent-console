# P0B Design Spec — Pi SDK Runner, Run Events, Safe Workspace & Verified Artifacts

> DRAFT / NOT IMPLEMENTED. Prerequisite: P0A Gate passed. Parent: [Master Spec](2026-11-16-master-product-architecture.md). Plan: [P0B](../plans/2026-11-16-p0b-pi-workspace-plan.md).

## Goal

A browser user selects a configured model, sends an Office or Code task; the actual pinned Pi SDK Worker reads only the server-authorized `/{user-id}/workspace`, streams structured events and persists Conversation/Session; a verified Artifact can be previewed and downloaded. Cancels, crashes, SSE disconnects, unsupported tools and malformed paths do not produce false success.

## User Journey

1. Open Workspace, upload test fixture, select Office/Code mode and model.
2. API checks current principal, workspace ownership, model access and allowed tools; creates immutable signed/authenticated RunSpec with run ID, model alias, tool policy, selected skills and run budget.
3. Node Pi Worker creates AgentSession with verified cwd, isolated resource loader and limited tools (P0 read-only by default).
4. API persists ordered RunEvents; Web displays Pi text deltas, tool start/progress/end, cancellation and final Artifact validation.
5. Browser can disconnect/reconnect via Last-Event-ID; Docker restart resumes Conversation/Pi Session or explicitly marks unavailable, without corrupting user files.
6. For Code mode, at least analyze a known local failing-test fixture without changing its original worktree. Advanced edit/test-in-sandbox deferred to P1.

## Non-goals

P0B does not grant generic Bash, remote Git push, private unknown Pi Extensions, emailing, cross-user workspaces, arbitrary script upload or background autonomy. Artifact generation may use a trusted file writer that only writes new files in task staging directory; overwriting existing files requires P1 review semantics.

## Boundary Architecture

```text
Browser → API Auth/Run Controller → Postgres Queue/Events
                                 → Pi Worker (Node, pinned SDK)
                                     ↘ configured Model Gateway
                                     ↘ isolated read-only workspace mount
                                     ↘ guarded File/Office Tools
                            → Validator → Artifact metadata & download API
```

Pi is not the policy enforcement point. Runner OS restrictions and backend per-resource authorization remain necessary even if Pi tools list is read-only. Worker must not inherit arbitrary project `.pi/extensions`. No Docker socket mount in Web/API or third-party Skill environment.

## Contracts

| Contract | Required properties | Validated at |
|---|---|---|
| `RunSpec` | schema/version, runId, principal/workspace, model alias, tool grants, resource limits | API and worker |
| `Conversation` | workspace ownership, parent Pi Session Ref, active writer lock | API/DB |
| `PiSessionRef` | stable ID/version, no user-selected storage path | API/Session manager |
| `RunEvent` | runId, seq, timestamp, schema, type, sanitized payload | Event service |
| `WorkspacePath` | internal user UUID, workspaceId, resolved logical cwd | File resolver |
| `Artifact` | runId, content hash, MIME, validation result, authorized download | Validator |
| `Cancel` | persisted requested time, final response confirmed | API/Runner |
| `Approval` | bound action hash/target/expiry; no “approve all tools” | API Policy |

Use existing [Pi Integration](../../PI_AGENT_INTEGRATION.md) for SDK/RPC assumptions and [Data Model](../../DATA_MODEL.md) for schema draft; synchronize final interface types in implementation, don't silently invent conflicts.

## State & Event Invariants

Current DB state machine remains authoritative: CREATED → PLANNING → RUNNING/WAITING_TOOL/WAITING_APPROVAL → VALIDATING → SUCCEEDED/FAILED/CANCELED (extend only via formal migration/ADR). Pi `agent_settled` merely means its automatic loop settled; Validator determines business success.

Every event has a monotonically increasing per-Run `seq`; reconnect replays events from DB and then subscribes without holes. At most one active writer for a Pi Session. Event data and logs must never store provider Key or raw sensitive file content unnecessarily.

## Failure & Concurrency

- Two POST with same idempotency key: one Run/one execution.
- Two Runs on one Pi Session: serialize/reject; never concurrently append to the same JSONL.
- User cancels while tool runs: abort Pi, stop child process, report already-completed effects; don't claim rollback.
- Worker crash during uncertain tool effect: reconcile, fail safely rather than blindly rerun non-idempotent action.
- SSE lost: background Run continues; UI reattaches and sees real terminal event.
- Disk full: reject new artifact, retain original upload, mark failure.
- Path traversal, symlink or URL-selected user directory: deny, no data leakage.
- Model lacks function calling: downgrade to chat-only with explicit UI; no fabricated file output.

## Security Boundary

Workspace physical host path `[DATA_DIR]/users/[uuid]/workspace` maps to authorized run filesystem `/{uuid}/workspace`. Path resolution uses safe descriptor/openat-style logic or strong equivalent; host root and other users not mounted. Limit CPU/RAM/seconds/output, network egress and secrets. P0 may run read-only trusted tools only under a constrained worker; if suitable isolation is absent do not claim user file isolation.

## Acceptance

| AC | Oracle |
|---|---|
| P0B-AC01 | Pinned Pi SDK compiles, real provider produces actual AgentSession/tool event |
| P0B-AC02 | Browser sends Run, sees correct ordered events, SSE reconnect has no gaps/replayed tool |
| P0B-AC03 | Authorized cwd is correct; other UUID/path traversal/symlink read denied |
| P0B-AC04 | Uploaded Office fixture yields real verified artifact and download |
| P0B-AC05 | Code fixture analyzed with no change to original repository |
| P0B-AC06 | Session persists after restart or cleanly handles incompatible/corrupt session |
| P0B-AC07 | cancel/timeout/crash/no tool-call model distinctly diagnosed, no false SUCCEEDED |
| P0B-AC08 | Run idempotency, one Pi session writer, no duplicated external effects |
| P0B-AC09 | App/Worker/Tool logs and session contain no Key sentinel |

## Gate & Open Experiments

Choose SDK integration and container sandbox based on actual Pi version, model proxy PoC and filesystem boundary experiment. Required: Pi SDK package locked, actual code compiled, tests + security negative executed. If a safe sandbox is unavailable, restrict P0B to single-user trusted read-only fixtures; do not expand arbitrary execution.
