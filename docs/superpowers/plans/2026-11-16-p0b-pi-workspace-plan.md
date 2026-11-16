# P0B Pi Agent & Workspace — Implementation Plan
> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans. Every task is RED → GREEN → REFACTOR with real verification.

**Goal:** Build a real Pi SDK Agent Run with server-authorized Workspace, durable Pi Session, replayable events and validated artifacts.
**Architecture:** Node Pi Worker executes Pi; FastAPI owns state/ACL/approval/model proxy; per-run sandbox mounts a verified user root; PostgreSQL stores events; browser subscribes SSE.
**Tech Stack:** pinned Pi npm package, pnpm/TypeScript, uv/FastAPI, PostgreSQL/Alembic, sandbox runner, Playwright.
**Spec:** [P0B Design Spec](../specs/2026-11-16-p0b-pi-workspace-spec.md).

## Global Constraints
- P0A Gate must pass first. Proposed file paths are not claims of existing code.
- `/{user-id}/workspace` from AuthContext + Workspace ID, never arbitrary user path.
- Provider secret stays in vault; Pi should use scoped gateway token.
- Native Pi tools and ResourceLoader must not load untrusted project Extensions.
- No Bash/unsafe writes in P0B; no success before Artifact Validator.
- All RED and GREEN commands must have actual outputs; log tests NOT RUN when absent.

## Review Focus
1. Pi SDK tag/API drift and application-level event semantics.
2. Session writer concurrency and crash recovery.
3. Directory traversal/symlink or unintended host mounts.
4. SSE reconnect/abort causing duplicate external effects.
5. Model tool support missing, output incomplete, validator false success.

## Task P0B-T01: Pi SDK version/License/ResourceLoader spike
**Depends:** P0A gate. **Covers:** P0B-AC01.
**Files:** services/pi-worker/package.json; pnpm-lock.yaml; services/pi-worker/src/pi/spike.ts; services/pi-worker/test/pi-sdk.test.ts; docs/adr/ADR-PI-001.md.
**Interface:** pin exact `@earendil-works/pi-coding-agent` release; `createAgentSession`, `SessionManager`, `DefaultResourceLoader` availability; inspect upstream license.

**Test command:** `pnpm --filter @agent-console/pi-worker test -- pi-sdk.test.ts`
**Expected RED:** SDK missing or documented import/signature incompatible.
**Expected GREEN:** actual SDK imports compile with lockfile, readonly in-memory session smoke emits events; ADR records exact version/API.

- [ ] Inspect actual implemented dependencies and read the target Spec.
- [ ] Write focused failing test and required negative fixture in the listed paths.
- [ ] Run `pnpm --filter @agent-console/pi-worker test -- pi-sdk.test.ts`, verify failure matches: SDK missing or documented import/signature incompatible.
- [ ] Implement minimum interface: pin exact `@earendil-works/pi-coding-agent` release; `createAgentSession`, `SessionManager`, `DefaultResourceLoader` availability; inspect upstream license.
- [ ] Rerun `pnpm --filter @agent-console/pi-worker test -- pi-sdk.test.ts` to green, refactor only after green.
- [ ] Run neighboring checks: `pnpm --filter @agent-console/pi-worker typecheck`; record actual results and tool side effects.
- [ ] Commit narrowly, update gotchas/evidence and request spec + code/security reviews.

## Task P0B-T02: Typed RunSpec + Event Schema contracts
**Depends:** T01. **Covers:** P0B-AC02,P0B-AC03.
**Files:** packages/contracts/schemas/run-spec.schema.json; packages/contracts/schemas/run-event.schema.json; packages/contracts/src/index.ts; services/api/tests/test_run_spec_contract.py.
**Interface:** `RunSpec` typed v1: authenticated run/workspace/model/tools/skills/budget; `RunEvent` runId/seq/type/payload; no host path/Key.

**Test command:** `uv run pytest services/api/tests/test_run_spec_contract.py -q`
**Expected RED:** malicious user_id/cwd fields accepted, mismatched schema.
**Expected GREEN:** Python/TS validators reject extraneous privileged inputs and serialize stable known event schema.

- [ ] Inspect actual implemented dependencies and read the target Spec.
- [ ] Write focused failing test and required negative fixture in the listed paths.
- [ ] Run `uv run pytest services/api/tests/test_run_spec_contract.py -q`, verify failure matches: malicious user_id/cwd fields accepted, mismatched schema.
- [ ] Implement minimum interface: `RunSpec` typed v1: authenticated run/workspace/model/tools/skills/budget; `RunEvent` runId/seq/type/payload; no host path/Key.
- [ ] Rerun `uv run pytest services/api/tests/test_run_spec_contract.py -q` to green, refactor only after green.
- [ ] Run neighboring checks: `make test-contract`; record actual results and tool side effects.
- [ ] Commit narrowly, update gotchas/evidence and request spec + code/security reviews.

## Task P0B-T03: Conversation/Run/Step/Event migrations + task queue
**Depends:** T02. **Covers:** P0B-AC02,P0B-AC06,P0B-AC08.
**Files:** services/api/alembic/versions/0002_agent_runtime.py; services/api/app/runs/models.py; services/api/app/runs/queue.py; services/api/tests/test_run_migrations.py.
**Interface:** `agent_conversations/pi_session_refs/agent_runs/run_steps/run_events`; idempotency, per-run sequence, lease and single session writer.

**Test command:** `uv run pytest services/api/tests/test_run_migrations.py -q`
**Expected RED:** duplicate idempotency creates two Runs; conflicting sequence/session lease accepted.
**Expected GREEN:** migrations clean, constraints enforced, queue claim lease works; rollback migration tested.

- [ ] Inspect actual implemented dependencies and read the target Spec.
- [ ] Write focused failing test and required negative fixture in the listed paths.
- [ ] Run `uv run pytest services/api/tests/test_run_migrations.py -q`, verify failure matches: duplicate idempotency creates two Runs; conflicting sequence/session lease accepted.
- [ ] Implement minimum interface: `agent_conversations/pi_session_refs/agent_runs/run_steps/run_events`; idempotency, per-run sequence, lease and single session writer.
- [ ] Rerun `uv run pytest services/api/tests/test_run_migrations.py -q` to green, refactor only after green.
- [ ] Run neighboring checks: `make test-integration`; record actual results and tool side effects.
- [ ] Commit narrowly, update gotchas/evidence and request spec + code/security reviews.

## Task P0B-T04: Worker RunSpec and Pi Event Adapter
**Depends:** T01-T03. **Covers:** P0B-AC01,P0B-AC02.
**Files:** services/pi-worker/src/runner.ts; services/pi-worker/src/pi/session.ts; services/pi-worker/src/pi/events.ts; services/pi-worker/test/runner.test.ts.
**Interface:** `runAuthorized(spec): AsyncIterator<RunEvent>` adapter; `message_update` delta, `message_end` final, `agent_settled` execution-only, error/abort.

**Test command:** `pnpm --filter @agent-console/pi-worker test -- runner.test.ts`
**Expected RED:** prompt ack incorrectly marks SUCCEEDED or event lacks run seq.
**Expected GREEN:** Pi SDK task emits normalized events and never declares success before validator; errors map to failed state.

- [ ] Inspect actual implemented dependencies and read the target Spec.
- [ ] Write focused failing test and required negative fixture in the listed paths.
- [ ] Run `pnpm --filter @agent-console/pi-worker test -- runner.test.ts`, verify failure matches: prompt ack incorrectly marks SUCCEEDED or event lacks run seq.
- [ ] Implement minimum interface: `runAuthorized(spec): AsyncIterator<RunEvent>` adapter; `message_update` delta, `message_end` final, `agent_settled` execution-only, error/abort.
- [ ] Rerun `pnpm --filter @agent-console/pi-worker test -- runner.test.ts` to green, refactor only after green.
- [ ] Run neighboring checks: `pnpm --filter @agent-console/pi-worker typecheck && make test-contract`; record actual results and tool side effects.
- [ ] Commit narrowly, update gotchas/evidence and request spec + code/security reviews.

## Task P0B-T05: Authorized Model Gateway tokens for Pi
**Depends:** P0A-T08,T04. **Covers:** P0B-AC01,P0B-AC09.
**Files:** services/api/app/models/gateway.py; services/api/tests/test_gateway.py; services/pi-worker/src/pi/models.ts; services/pi-worker/test/model-proxy.test.ts.
**Interface:** short-lived run-scoped token resolves model alias via gateway; Pi does not receive provider long-term Key; local Ollama/admin LAN allowed only policy.

**Test command:** `uv run pytest services/api/tests/test_gateway.py -q`
**Expected RED:** worker can retrieve raw Key or call another owner's model.
**Expected GREEN:** least privilege proxy allows authorized inference and denies expired/wrong-run token; real Pi/provider smoke separately.

- [ ] Inspect actual implemented dependencies and read the target Spec.
- [ ] Write focused failing test and required negative fixture in the listed paths.
- [ ] Run `uv run pytest services/api/tests/test_gateway.py -q`, verify failure matches: worker can retrieve raw Key or call another owner's model.
- [ ] Implement minimum interface: short-lived run-scoped token resolves model alias via gateway; Pi does not receive provider long-term Key; local Ollama/admin LAN allowed only policy.
- [ ] Rerun `uv run pytest services/api/tests/test_gateway.py -q` to green, refactor only after green.
- [ ] Run neighboring checks: `pnpm --filter @agent-console/pi-worker test && make test-security`; record actual results and tool side effects.
- [ ] Commit narrowly, update gotchas/evidence and request spec + code/security reviews.

## Task P0B-T06: Workspace Root resolver + read-only sandbox mount
**Depends:** T02,T03. **Covers:** P0B-AC03.
**Files:** services/api/app/workspaces/paths.py; services/api/tests/test_workspace_paths.py; services/runner-manager/sandbox.py; services/runner-manager/tests/test_mounts.py.
**Interface:** `resolve_workspace_root(principal,workspace_id)` returns safe canonical host root and logical `/{uuid}/workspace`; read-only per-run mount.

**Test command:** `uv run pytest services/api/tests/test_workspace_paths.py services/runner-manager/tests/test_mounts.py -q`
**Expected RED:** cross-user, symlink, ../, user ID path injection permitted or host directory mounted.
**Expected GREEN:** only authorized files visible; no Docker socket or other user dirs; failure is 403/404.

- [ ] Inspect actual implemented dependencies and read the target Spec.
- [ ] Write focused failing test and required negative fixture in the listed paths.
- [ ] Run `uv run pytest services/api/tests/test_workspace_paths.py services/runner-manager/tests/test_mounts.py -q`, verify failure matches: cross-user, symlink, ../, user ID path injection permitted or host directory mounted.
- [ ] Implement minimum interface: `resolve_workspace_root(principal,workspace_id)` returns safe canonical host root and logical `/{uuid}/workspace`; read-only per-run mount.
- [ ] Rerun `uv run pytest services/api/tests/test_workspace_paths.py services/runner-manager/tests/test_mounts.py -q` to green, refactor only after green.
- [ ] Run neighboring checks: `make test-security && make test-integration`; record actual results and tool side effects.
- [ ] Commit narrowly, update gotchas/evidence and request spec + code/security reviews.

## Task P0B-T07: File upload, Artifact Store and Validator
**Depends:** T06. **Covers:** P0B-AC04.
**Files:** services/api/app/workspaces/files.py; services/api/app/artifacts/service.py; services/api/tests/test_artifact_validation.py; tests/fixtures/office/sample.csv.
**Interface:** `POST /api/v1/workspaces/{id}/files`, `GET /api/v1/artifacts/{id}/download`; bounded parser/new artifact/sha256 MIME, no overwrite.

**Test command:** `uv run pytest services/api/tests/test_artifact_validation.py -q`
**Expected RED:** file exists but invalid artifact claims success, traversal download bypass.
**Expected GREEN:** valid CSV/Markdown output parsed and downloadable; corrupt/missing artifact fails validation.

- [ ] Inspect actual implemented dependencies and read the target Spec.
- [ ] Write focused failing test and required negative fixture in the listed paths.
- [ ] Run `uv run pytest services/api/tests/test_artifact_validation.py -q`, verify failure matches: file exists but invalid artifact claims success, traversal download bypass.
- [ ] Implement minimum interface: `POST /api/v1/workspaces/{id}/files`, `GET /api/v1/artifacts/{id}/download`; bounded parser/new artifact/sha256 MIME, no overwrite.
- [ ] Rerun `uv run pytest services/api/tests/test_artifact_validation.py -q` to green, refactor only after green.
- [ ] Run neighboring checks: `make test-integration && make test-security`; record actual results and tool side effects.
- [ ] Commit narrowly, update gotchas/evidence and request spec + code/security reviews.

## Task P0B-T08: Run API + replayable SSE + cancel and approvals
**Depends:** T03,T04,T06. **Covers:** P0B-AC02,P0B-AC07,P0B-AC08.
**Files:** services/api/app/runs/routes.py; services/api/app/runs/events.py; services/api/tests/test_run_events.py; apps/web/hooks/useRunEvents.ts.
**Interface:** `POST /agent/runs`, `GET /agent/runs/{id}/events`, `POST /agent/runs/{id}/cancel`; Last-Event-ID, CAS terminal state.

**Test command:** `uv run pytest services/api/tests/test_run_events.py -q`
**Expected RED:** SSE loses events or same tool replays after reconnect; cancel marked success without worker acknowledgement.
**Expected GREEN:** seq stable/replay complete, run idempotent, cancel terminal only after confirmation.

- [ ] Inspect actual implemented dependencies and read the target Spec.
- [ ] Write focused failing test and required negative fixture in the listed paths.
- [ ] Run `uv run pytest services/api/tests/test_run_events.py -q`, verify failure matches: SSE loses events or same tool replays after reconnect; cancel marked success without worker acknowledgement.
- [ ] Implement minimum interface: `POST /agent/runs`, `GET /agent/runs/{id}/events`, `POST /agent/runs/{id}/cancel`; Last-Event-ID, CAS terminal state.
- [ ] Rerun `uv run pytest services/api/tests/test_run_events.py -q` to green, refactor only after green.
- [ ] Run neighboring checks: `make test-contract && make test-integration`; record actual results and tool side effects.
- [ ] Commit narrowly, update gotchas/evidence and request spec + code/security reviews.

## Task P0B-T09: Pi Session Persistence and single writer recovery
**Depends:** T03,T04,T08. **Covers:** P0B-AC06,P0B-AC08.
**Files:** services/pi-worker/src/pi/session-store.ts; services/pi-worker/test/session-resume.test.ts; services/api/tests/test_session_lease.py.
**Interface:** `openSessionRef(conversationId,owner)` with durable Pi SessionManager store ref; one active writer lease, restart/fork detection.

**Test command:** `pnpm --filter @agent-console/pi-worker test -- session-resume.test.ts`
**Expected RED:** two workers append concurrently, restart loses or corrupts context.
**Expected GREEN:** two-turn conversation resumes after cold restart and denies parallel session writer.

- [ ] Inspect actual implemented dependencies and read the target Spec.
- [ ] Write focused failing test and required negative fixture in the listed paths.
- [ ] Run `pnpm --filter @agent-console/pi-worker test -- session-resume.test.ts`, verify failure matches: two workers append concurrently, restart loses or corrupts context.
- [ ] Implement minimum interface: `openSessionRef(conversationId,owner)` with durable Pi SessionManager store ref; one active writer lease, restart/fork detection.
- [ ] Rerun `pnpm --filter @agent-console/pi-worker test -- session-resume.test.ts` to green, refactor only after green.
- [ ] Run neighboring checks: `uv run pytest services/api/tests/test_session_lease.py -q && make test-integration`; record actual results and tool side effects.
- [ ] Commit narrowly, update gotchas/evidence and request spec + code/security reviews.

## Task P0B-T10: Office/Code browser fixture, failure injection and P0B gate
**Depends:** T01-T09. **Covers:** P0B-AC01,P0B-AC02,P0B-AC03,P0B-AC04,P0B-AC05,P0B-AC06,P0B-AC07,P0B-AC08,P0B-AC09.
**Files:** apps/web/app/agent/page.tsx; apps/web/components/RunProgress.tsx; tests/e2e/p0b-office-code.spec.ts; tests/security/p0b-attack.spec.ts.
**Interface:** browser model select/run/upload/artifact/SSE; test suite records actual Pi engine version and status.

**Test command:** `pnpm exec playwright test tests/e2e/p0b-office-code.spec.ts`
**Expected RED:** no real Pi file task, inaccurate status or workspace read outside root.
**Expected GREEN:** Office verifies file, Code fixture unchanged, crash/cancel/timeout negative pass; real LLM smoke separate.

- [ ] Inspect actual implemented dependencies and read the target Spec.
- [ ] Write focused failing test and required negative fixture in the listed paths.
- [ ] Run `pnpm exec playwright test tests/e2e/p0b-office-code.spec.ts`, verify failure matches: no real Pi file task, inaccurate status or workspace read outside root.
- [ ] Implement minimum interface: browser model select/run/upload/artifact/SSE; test suite records actual Pi engine version and status.
- [ ] Rerun `pnpm exec playwright test tests/e2e/p0b-office-code.spec.ts` to green, refactor only after green.
- [ ] Run neighboring checks: `make check && make test-integration && make test-e2e && make test-security`; record actual results and tool side effects.
- [ ] Commit narrowly, update gotchas/evidence and request spec + code/security reviews.

## Coverage & Self-review
- P0B-AC01 ↔ P0B-T01 (Pi SDK version/License/ResourceLoader spike)
- P0B-AC02,P0B-AC03 ↔ P0B-T02 (Typed RunSpec + Event Schema contracts)
- P0B-AC02,P0B-AC06,P0B-AC08 ↔ P0B-T03 (Conversation/Run/Step/Event migrations + task queue)
- P0B-AC01,P0B-AC02 ↔ P0B-T04 (Worker RunSpec and Pi Event Adapter)
- P0B-AC01,P0B-AC09 ↔ P0B-T05 (Authorized Model Gateway tokens for Pi)
- P0B-AC03 ↔ P0B-T06 (Workspace Root resolver + read-only sandbox mount)
- P0B-AC04 ↔ P0B-T07 (File upload, Artifact Store and Validator)
- P0B-AC02,P0B-AC07,P0B-AC08 ↔ P0B-T08 (Run API + replayable SSE + cancel and approvals)
- P0B-AC06,P0B-AC08 ↔ P0B-T09 (Pi Session Persistence and single writer recovery)
- P0B-AC01,P0B-AC02,P0B-AC03,P0B-AC04,P0B-AC05,P0B-AC06,P0B-AC07,P0B-AC08,P0B-AC09 ↔ P0B-T10 (Office/Code browser fixture, failure injection and P0B gate)

- [ ] Real Pi SDK compiled under pinned package and used with real model, not only mocked.
- [ ] Session and Run status are separate; no false success; all SSE replays consistent.
- [ ] All prohibited file/secret paths tested, with OS-level boundary evidence.
- [ ] All tasks and ACs have command outputs bound to commit SHA.
- [ ] Gate G1 signed off before enabling P0C features.

**Handoff:** Read P0B Spec and review this plan; execute task by task in isolated worktree and don't merge without authorization.
