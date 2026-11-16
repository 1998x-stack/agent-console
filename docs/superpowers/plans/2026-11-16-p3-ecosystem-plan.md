# P3 Ecosystem Extensions & Operations — Implementation Plan
> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans. Phase families are optional; implement only those with evidence and approved scope.

**Goal:** Expand CLI/SDK, scoped MCP, evidence-driven search and operational capacity without regressing local-first privacy or prior gates.
**Architecture:** Stable public API/SDK and Tool Gateway, optional connectors, benchmarked search, migratable durable storage and resource admission.
**Tech Stack:** TypeScript/pnpm, FastAPI/pytest, MCP adapters, Pi Worker, PostgreSQL, Docker/load harness.
**Spec:** [P3 Design Spec](../specs/2026-11-16-p3-ecosystem-spec.md).

## Global Constraints
- Do not build every P3 item merely to call roadmap complete; Task T01 decides which families have evidence.
- CLI & connectors must use existing auth, version, approval and audit boundaries.
- MCP/remote tool results are untrusted, tokens stay secret.
- Search ACL and compatibility are hard filters; measured quality vs baseline only.
- Upgrades/restore cannot corrupt existing Pi Session or workspace.

## Review Focus
1. Developer CLI bypasses Web permission or duplicates publish.
2. MCP tool exfiltrates credentials through model context.
3. Embedding/ranking surfaces unauthorized Skill.
4. Pi upgrade breaks old JSONL, backup misses encryption key.
5. Queue overload or partial migration loses in-flight Run.

## Task P3-T01: Usage evidence gate and extension family ADR
**Depends:** P2 Gate or explicitly scoped P0 local-only pilot. **Spec:** P3-AC01-AC06.
**Files:** docs/adr/ADR-P3-PRIORITIES.md; tests/metrics/test_usage_evidence.py; docs/product/p3-adoption-decision.md.
**Interface:** supported feature family and measurable acceptance formally chosen.
**Test:** `uv run pytest tests/metrics/test_usage_evidence.py -q`.
**Expected RED:** feature accepted without user signal/metric or security gate.
**Expected GREEN:** supported feature family and measurable acceptance formally chosen.

- [ ] Check adoption/ADR evidence; record explicit inclusion of this task.
- [ ] Write failing fixture/unit/contract test, including security negative.
- [ ] Run `uv run pytest tests/metrics/test_usage_evidence.py -q`, confirm RED from actual missing behavior.
- [ ] Implement only Usage evidence gate and extension family ADR, preserving existing API and security contracts.
- [ ] Rerun `uv run pytest tests/metrics/test_usage_evidence.py -q` to GREEN, refactor and verify compatibility.
- [ ] Run relevant integration/E2E/security/restore tests and capture real evidence.
- [ ] Commit scoped change, update gotchas, request spec and code/security reviews.

## Task P3-T02: Authenticated developer CLI: validate/install/publish
**Depends:** T01. **Spec:** P3-AC01/AC06.
**Files:** apps/cli/src/index.ts; apps/cli/src/commands/skills.ts; apps/cli/test/skills.test.ts; packages/contracts/openapi.yaml.
**Interface:** CLI uses same HTTP API/auth/version pin/idempotency as Web.
**Test:** `pnpm --filter @agent-console/cli test`.
**Expected RED:** CLI bypasses server ACL or duplicate publish after retry.
**Expected GREEN:** CLI uses same HTTP API/auth/version pin/idempotency as Web.

- [ ] Check adoption/ADR evidence; record explicit inclusion of this task.
- [ ] Write failing fixture/unit/contract test, including security negative.
- [ ] Run `pnpm --filter @agent-console/cli test`, confirm RED from actual missing behavior.
- [ ] Implement only Authenticated developer CLI: validate/install/publish, preserving existing API and security contracts.
- [ ] Rerun `pnpm --filter @agent-console/cli test` to GREEN, refactor and verify compatibility.
- [ ] Run relevant integration/E2E/security/restore tests and capture real evidence.
- [ ] Commit scoped change, update gotchas, request spec and code/security reviews.

## Task P3-T03: Scoped MCP server registry and Tool Gateway
**Depends:** T01. **Spec:** P3-AC02.
**Files:** services/api/app/connectors/mcp_registry.py; services/api/tests/test_mcp_policy.py; services/pi-worker/src/pi/mcp-tools.ts.
**Interface:** MCP declared scopes, short credential, action hash approvals and audit.
**Test:** `uv run pytest services/api/tests/test_mcp_policy.py -q`.
**Expected RED:** MCP tool can read plaintext OAuth token or run unapproved external write.
**Expected GREEN:** MCP declared scopes, short credential, action hash approvals and audit.

- [ ] Check adoption/ADR evidence; record explicit inclusion of this task.
- [ ] Write failing fixture/unit/contract test, including security negative.
- [ ] Run `uv run pytest services/api/tests/test_mcp_policy.py -q`, confirm RED from actual missing behavior.
- [ ] Implement only Scoped MCP server registry and Tool Gateway, preserving existing API and security contracts.
- [ ] Rerun `uv run pytest services/api/tests/test_mcp_policy.py -q` to GREEN, refactor and verify compatibility.
- [ ] Run relevant integration/E2E/security/restore tests and capture real evidence.
- [ ] Commit scoped change, update gotchas, request spec and code/security reviews.

## Task P3-T04: Skill search benchmark and safer ranking
**Depends:** T01. **Spec:** P3-AC03.
**Files:** services/api/app/skills/search.py; tests/evals/skill_search_queries.jsonl; tests/evals/test_skill_retrieval.py.
**Interface:** ACL/compatibility hard filter, measured relevance improvement over baseline.
**Test:** `uv run pytest tests/evals/test_skill_retrieval.py -q`.
**Expected RED:** unauthorized or incompatible Skill ranks into results; no baseline quality measure.
**Expected GREEN:** ACL/compatibility hard filter, measured relevance improvement over baseline.

- [ ] Check adoption/ADR evidence; record explicit inclusion of this task.
- [ ] Write failing fixture/unit/contract test, including security negative.
- [ ] Run `uv run pytest tests/evals/test_skill_retrieval.py -q`, confirm RED from actual missing behavior.
- [ ] Implement only Skill search benchmark and safer ranking, preserving existing API and security contracts.
- [ ] Rerun `uv run pytest tests/evals/test_skill_retrieval.py -q` to GREEN, refactor and verify compatibility.
- [ ] Run relevant integration/E2E/security/restore tests and capture real evidence.
- [ ] Commit scoped change, update gotchas, request spec and code/security reviews.

## Task P3-T05: Versioned backup/restore and Pi session upgrade drill
**Depends:** T01. **Spec:** P3-AC04.
**Files:** scripts/backup.sh; scripts/restore.sh; tests/ops/test_upgrade_restore.sh; docs/deployment/upgrade.md.
**Interface:** consistent backup and cold restore + upgrade/downgrade compatibility diagnostics.
**Test:** `bash tests/ops/test_upgrade_restore.sh`.
**Expected RED:** DB-only restore loses Workspace/Skill/Pi Session or master key mismatch silently destroys data.
**Expected GREEN:** consistent backup and cold restore + upgrade/downgrade compatibility diagnostics.

- [ ] Check adoption/ADR evidence; record explicit inclusion of this task.
- [ ] Write failing fixture/unit/contract test, including security negative.
- [ ] Run `bash tests/ops/test_upgrade_restore.sh`, confirm RED from actual missing behavior.
- [ ] Implement only Versioned backup/restore and Pi session upgrade drill, preserving existing API and security contracts.
- [ ] Rerun `bash tests/ops/test_upgrade_restore.sh` to GREEN, refactor and verify compatibility.
- [ ] Run relevant integration/E2E/security/restore tests and capture real evidence.
- [ ] Commit scoped change, update gotchas, request spec and code/security reviews.

## Task P3-T06: Capacity and resilience suite with workload evidence
**Depends:** T01-T05. **Spec:** P3-AC05.
**Files:** tests/load/scenarios.js; services/api/app/metrics.py; docs/operations/capacity.md; tests/ops/test_backpressure.py.
**Interface:** bounded admission/backpressure and measured latency/memory on supported host.
**Test:** `uv run pytest tests/ops/test_backpressure.py -q`.
**Expected RED:** queue overload loses Runs, API accepts tasks beyond quota without status.
**Expected GREEN:** bounded admission/backpressure and measured latency/memory on supported host.

- [ ] Check adoption/ADR evidence; record explicit inclusion of this task.
- [ ] Write failing fixture/unit/contract test, including security negative.
- [ ] Run `uv run pytest tests/ops/test_backpressure.py -q`, confirm RED from actual missing behavior.
- [ ] Implement only Capacity and resilience suite with workload evidence, preserving existing API and security contracts.
- [ ] Rerun `uv run pytest tests/ops/test_backpressure.py -q` to GREEN, refactor and verify compatibility.
- [ ] Run relevant integration/E2E/security/restore tests and capture real evidence.
- [ ] Commit scoped change, update gotchas, request spec and code/security reviews.

## Gate G5 / Scope Report
- [ ] For each implemented family AC01–AC06 evidence linked and real tests run.
- [ ] Each deferred feature explicitly marked DEFERRED, not falsely PASSED.
- [ ] Compatibility, secrets and local-first tests do not regress.
- [ ] Rollback, queue pressure and incident paths validated for deployed features.
- [ ] Report partial stage scope honestly and do not merge automatically.
