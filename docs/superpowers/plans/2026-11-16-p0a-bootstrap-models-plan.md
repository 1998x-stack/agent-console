# P0A Bootstrap & BYOK — Implementation Plan
> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Deliver a clean Docker Web bootstrap, one-time authenticated setup and encrypted model configuration with independently tested inference.
**Architecture:** Next.js Web and FastAPI control plane, PostgreSQL transaction-migrated state, encrypted Vault and bounded provider connector. Pi file execution is not P0A.
**Tech Stack:** pnpm/Next.js/Playwright, uv/FastAPI/pytest, PostgreSQL/Alembic, Docker Compose.
**Spec:** [P0A Design Spec](../specs/2026-11-16-p0a-bootstrap-models-spec.md).

## Global Constraints
- This is a proposed plan; all paths and commands are target implementation, not pre-existing evidence.
- Single-user local-first, no model Key needed for Docker boot; no default admin password.
- Keys encrypted and never echoed to browser/DB logs; Base URL must pass SSRF and admin LAN policy.
- Fail closed on auth/config inconsistency; no Pi SDK runtime or public Registry claims yet.
- Strict RED→GREEN→REFACTOR, negative tests, no false-green status, PR review before moving Gate.

## Review Focus
1. Two tabs initialize first admin concurrently.
2. Container localhost versus host Ollama URL and DNS rebinding.
3. Model /models succeeds but generation/tool calls fail.
4. Key injected into error stack, trace, DB dump or API response.
5. DB/migration or encryption key missing during restart.

## Task P0A-T01: 建立可失败的 Monorepo/CI 基线
**Depends:** none. **Requirement:** P0A-AC01.

**Files:** Makefile; pnpm-workspace.yaml; package.json; pyproject.toml; apps/web/package.json; services/api/pyproject.toml; services/pi-worker/package.json; tests/unit/test_repo_layout.py; .github/workflows/ci.yml; docs/gotchas.md.

**Interfaces:** `make check/docs-check/test-unit` targets; layout detector must assert directory and lockfile presence; CI fails on a deliberate broken test.

**Test command:** `python3 -m unittest discover -s tests/unit -p 'test_repo_layout.py' -v`
**Expected RED:** missing directories, lockfiles and targets cause a test failure.
**Expected GREEN:** repo skeleton, pinned lockfiles and CI structure exist; deliberate breaking of detector makes CI red.

- [ ] Confirm prerequisite Task commits and clean worktree; read exact Spec section.
- [ ] Write a failing test in listed test file for: missing directories, lockfiles and targets cause a test failure.
- [ ] Run `python3 -m unittest discover -s tests/unit -p 'test_repo_layout.py' -v` and record failing assertion + exit code (not missing test tooling).
- [ ] Implement only this interface: `make check/docs-check/test-unit` targets; layout detector must assert directory and lockfile presence; CI fails on a deliberate broken test.
- [ ] Rerun `python3 -m unittest discover -s tests/unit -p 'test_repo_layout.py' -v` until it passes; inspect output, then refactor.
- [ ] Run `make check && make docs-check`; note real failures and security edge cases.
- [ ] Commit task-only change, update `docs/gotchas.md`, request spec-compliance and code-quality reviews.

## Task P0A-T02: Compose、可达 Web/API 与健康检查
**Depends:** T01. **Requirement:** P0A-AC01.

**Files:** compose.yaml; apps/web/app/page.tsx; services/api/app/main.py; services/api/app/health.py; services/api/tests/test_health.py; tests/e2e/bootstrap.spec.ts.

**Interfaces:** `GET /api/v1/health/live`, `GET /api/v1/health/ready`. Compose web :3000 loopback, api, postgres, pi-worker stub (not fake full Agent).

**Test command:** `uv run pytest services/api/tests/test_health.py -q`
**Expected RED:** health route unavailable, readiness does not distinguish DB down.
**Expected GREEN:** liveness and readiness distinguish process vs DB; Compose config valid.

- [ ] Confirm prerequisite Task commits and clean worktree; read exact Spec section.
- [ ] Write a failing test in listed test file for: health route unavailable, readiness does not distinguish DB down.
- [ ] Run `uv run pytest services/api/tests/test_health.py -q` and record failing assertion + exit code (not missing test tooling).
- [ ] Implement only this interface: `GET /api/v1/health/live`, `GET /api/v1/health/ready`. Compose web :3000 loopback, api, postgres, pi-worker stub (not fake full Agent).
- [ ] Rerun `uv run pytest services/api/tests/test_health.py -q` until it passes; inspect output, then refactor.
- [ ] Run `docker compose config -q && docker compose up -d --build && docker compose ps`; note real failures and security edge cases.
- [ ] Commit task-only change, update `docs/gotchas.md`, request spec-compliance and code-quality reviews.

## Task P0A-T03: Users / Workspace / Model schema migration
**Depends:** T02. **Requirement:** P0A-AC06.

**Files:** services/api/alembic/versions/0001_identity_models.py; services/api/app/db/models.py; services/api/tests/test_migrations.py.

**Interfaces:** `users`, `workspaces`, `model_connections`, `model_aliases` with UUID FK/unique constraints; migration upgrade/downgrade policy.

**Test command:** `uv run pytest services/api/tests/test_migrations.py -q`
**Expected RED:** fresh DB lacks tables/constraints or downgrade fails.
**Expected GREEN:** clean database upgrade creates schema; duplicate identity and bad scope rejected.

- [ ] Confirm prerequisite Task commits and clean worktree; read exact Spec section.
- [ ] Write a failing test in listed test file for: fresh DB lacks tables/constraints or downgrade fails.
- [ ] Run `uv run pytest services/api/tests/test_migrations.py -q` and record failing assertion + exit code (not missing test tooling).
- [ ] Implement only this interface: `users`, `workspaces`, `model_connections`, `model_aliases` with UUID FK/unique constraints; migration upgrade/downgrade policy.
- [ ] Rerun `uv run pytest services/api/tests/test_migrations.py -q` until it passes; inspect output, then refactor.
- [ ] Run `make test-integration`; note real failures and security edge cases.
- [ ] Commit task-only change, update `docs/gotchas.md`, request spec-compliance and code-quality reviews.

## Task P0A-T04: 一次性 Admin Bootstrap 与并发防护
**Depends:** T03. **Requirement:** P0A-AC02.

**Files:** services/api/app/setup/service.py; services/api/app/setup/routes.py; services/api/tests/test_bootstrap.py.

**Interfaces:** `GET /api/v1/setup/status`; `POST /api/v1/setup/initialize-admin` accepts local one-time capability, one admin max.

**Test command:** `uv run pytest services/api/tests/test_bootstrap.py -q`
**Expected RED:** two concurrent bootstrap attempts both succeed or token not checked.
**Expected GREEN:** one 201 and one 409; empty instance first-run works; no default weak password.

- [ ] Confirm prerequisite Task commits and clean worktree; read exact Spec section.
- [ ] Write a failing test in listed test file for: two concurrent bootstrap attempts both succeed or token not checked.
- [ ] Run `uv run pytest services/api/tests/test_bootstrap.py -q` and record failing assertion + exit code (not missing test tooling).
- [ ] Implement only this interface: `GET /api/v1/setup/status`; `POST /api/v1/setup/initialize-admin` accepts local one-time capability, one admin max.
- [ ] Rerun `uv run pytest services/api/tests/test_bootstrap.py -q` until it passes; inspect output, then refactor.
- [ ] Run `make test-integration`; note real failures and security edge cases.
- [ ] Commit task-only change, update `docs/gotchas.md`, request spec-compliance and code-quality reviews.

## Task P0A-T05: 登录会话和 Same-origin Web Auth
**Depends:** T04. **Requirement:** P0A-AC02,P0A-AC03.

**Files:** services/api/app/auth/routes.py; services/api/app/auth/session.py; services/api/tests/test_auth.py; apps/web/app/login/page.tsx.

**Interfaces:** `POST /api/v1/auth/session`, `DELETE /api/v1/auth/session`, `GET /api/v1/auth/me`; HttpOnly Secure/SameSite and CSRF validation.

**Test command:** `uv run pytest services/api/tests/test_auth.py -q`
**Expected RED:** unauthorized API accepted, CSRF bypass or session not invalidated.
**Expected GREEN:** cookie session expires/logouts, unauthorized model routes rejected, no secrets returned.

- [ ] Confirm prerequisite Task commits and clean worktree; read exact Spec section.
- [ ] Write a failing test in listed test file for: unauthorized API accepted, CSRF bypass or session not invalidated.
- [ ] Run `uv run pytest services/api/tests/test_auth.py -q` and record failing assertion + exit code (not missing test tooling).
- [ ] Implement only this interface: `POST /api/v1/auth/session`, `DELETE /api/v1/auth/session`, `GET /api/v1/auth/me`; HttpOnly Secure/SameSite and CSRF validation.
- [ ] Rerun `uv run pytest services/api/tests/test_auth.py -q` until it passes; inspect output, then refactor.
- [ ] Run `make test-unit && make test-integration`; note real failures and security edge cases.
- [ ] Commit task-only change, update `docs/gotchas.md`, request spec-compliance and code-quality reviews.

## Task P0A-T06: 加密 Vault 与 Key 不可回显
**Depends:** T03,T05. **Requirement:** P0A-AC03,P0A-AC08.

**Files:** services/api/app/secrets/vault.py; services/api/tests/test_vault.py; services/api/app/logging/redaction.py.

**Interfaces:** `encrypt_secret(secret)->secret_ref` and `resolve_secret(secret_ref,principal)->bytes`; persistent APP_ENCRYPTION_KEY, no plaintext API read.

**Test command:** `uv run pytest services/api/tests/test_vault.py -q`
**Expected RED:** plaintext DB/log exposure, key rotation or missing-key behavior unsafe.
**Expected GREEN:** encrypt/decrypt authorized, key not returned/logged, missing master key fails closed.

- [ ] Confirm prerequisite Task commits and clean worktree; read exact Spec section.
- [ ] Write a failing test in listed test file for: plaintext DB/log exposure, key rotation or missing-key behavior unsafe.
- [ ] Run `uv run pytest services/api/tests/test_vault.py -q` and record failing assertion + exit code (not missing test tooling).
- [ ] Implement only this interface: `encrypt_secret(secret)->secret_ref` and `resolve_secret(secret_ref,principal)->bytes`; persistent APP_ENCRYPTION_KEY, no plaintext API read.
- [ ] Rerun `uv run pytest services/api/tests/test_vault.py -q` until it passes; inspect output, then refactor.
- [ ] Run `make test-security`; note real failures and security edge cases.
- [ ] Commit task-only change, update `docs/gotchas.md`, request spec-compliance and code-quality reviews.

## Task P0A-T07: ModelConnection CRUD/URL Policy
**Depends:** T06. **Requirement:** P0A-AC03,P0A-AC07.

**Files:** services/api/app/models/schemas.py; services/api/app/models/routes.py; services/api/app/models/network_policy.py; services/api/tests/test_model_connections.py.

**Interfaces:** `POST/GET/PATCH/DELETE /api/v1/model-connections` and associated alias endpoints; URL/SSRF policy with admin-approved LAN exception.

**Test command:** `uv run pytest services/api/tests/test_model_connections.py -q`
**Expected RED:** wrong user sees connection, unsupported URL accepted or forbidden redirect allowed.
**Expected GREEN:** ownership guards, masked Key, DNS/scheme/redirect policy enforce allowed targets.

- [ ] Confirm prerequisite Task commits and clean worktree; read exact Spec section.
- [ ] Write a failing test in listed test file for: wrong user sees connection, unsupported URL accepted or forbidden redirect allowed.
- [ ] Run `uv run pytest services/api/tests/test_model_connections.py -q` and record failing assertion + exit code (not missing test tooling).
- [ ] Implement only this interface: `POST/GET/PATCH/DELETE /api/v1/model-connections` and associated alias endpoints; URL/SSRF policy with admin-approved LAN exception.
- [ ] Rerun `uv run pytest services/api/tests/test_model_connections.py -q` until it passes; inspect output, then refactor.
- [ ] Run `make test-security && make test-contract`; note real failures and security edge cases.
- [ ] Commit task-only change, update `docs/gotchas.md`, request spec-compliance and code-quality reviews.

## Task P0A-T08: Provider 探测：鉴权、推理和工具能力分离
**Depends:** T07. **Requirement:** P0A-AC04,P0A-AC05.

**Files:** services/api/app/models/probes.py; services/api/app/models/providers/openai_compatible.py; services/api/tests/test_model_probe.py; tests/fixtures/mock_llm.py.

**Interfaces:** `POST /api/v1/model-connections/{id}/test` returns reachability/auth/inference/tool_call/observed_at with error_code.

**Test command:** `uv run pytest services/api/tests/test_model_probe.py -q`
**Expected RED:** /models-only probe falsely reports tool capable, wrong Key returns generic success.
**Expected GREEN:** each stage distinct, mock scenarios classify 401/404/429/timeout; real-provider smoke opt-in.

- [ ] Confirm prerequisite Task commits and clean worktree; read exact Spec section.
- [ ] Write a failing test in listed test file for: /models-only probe falsely reports tool capable, wrong Key returns generic success.
- [ ] Run `uv run pytest services/api/tests/test_model_probe.py -q` and record failing assertion + exit code (not missing test tooling).
- [ ] Implement only this interface: `POST /api/v1/model-connections/{id}/test` returns reachability/auth/inference/tool_call/observed_at with error_code.
- [ ] Rerun `uv run pytest services/api/tests/test_model_probe.py -q` until it passes; inspect output, then refactor.
- [ ] Run `make test-integration && make test-security`; note real failures and security edge cases.
- [ ] Commit task-only change, update `docs/gotchas.md`, request spec-compliance and code-quality reviews.

## Task P0A-T09: Web Setup+Models 流程和重启/密钥 E2E
**Depends:** T04-T08. **Requirement:** P0A-AC01,P0A-AC03,P0A-AC04,P0A-AC05,P0A-AC06,P0A-AC08.

**Files:** apps/web/app/setup/page.tsx; apps/web/app/settings/models/page.tsx; apps/web/components/ModelConnectionForm.tsx; tests/e2e/p0a-onboarding.spec.ts; docs/deployment/local.md.

**Interfaces:** setup status UI, Save vs Test distinct, model default selection; local Ollama URL guidance.

**Test command:** `pnpm exec playwright test tests/e2e/p0a-onboarding.spec.ts`
**Expected RED:** user cannot configure model/start from browser, restart loses alias or secret exposed.
**Expected GREEN:** clean browser setup passes with mock endpoint; run separately against approved real provider, DB persist.

- [ ] Confirm prerequisite Task commits and clean worktree; read exact Spec section.
- [ ] Write a failing test in listed test file for: user cannot configure model/start from browser, restart loses alias or secret exposed.
- [ ] Run `pnpm exec playwright test tests/e2e/p0a-onboarding.spec.ts` and record failing assertion + exit code (not missing test tooling).
- [ ] Implement only this interface: setup status UI, Save vs Test distinct, model default selection; local Ollama URL guidance.
- [ ] Rerun `pnpm exec playwright test tests/e2e/p0a-onboarding.spec.ts` until it passes; inspect output, then refactor.
- [ ] Run `make check && make test-integration && make test-e2e && make test-security`; note real failures and security edge cases.
- [ ] Commit task-only change, update `docs/gotchas.md`, request spec-compliance and code-quality reviews.

## Spec → Task Coverage
- P0A-AC01: P0A-T01 — 建立可失败的 Monorepo/CI 基线
- P0A-AC01: P0A-T02 — Compose、可达 Web/API 与健康检查
- P0A-AC06: P0A-T03 — Users / Workspace / Model schema migration
- P0A-AC02: P0A-T04 — 一次性 Admin Bootstrap 与并发防护
- P0A-AC02,P0A-AC03: P0A-T05 — 登录会话和 Same-origin Web Auth
- P0A-AC03,P0A-AC08: P0A-T06 — 加密 Vault 与 Key 不可回显
- P0A-AC03,P0A-AC07: P0A-T07 — ModelConnection CRUD/URL Policy
- P0A-AC04,P0A-AC05: P0A-T08 — Provider 探测：鉴权、推理和工具能力分离
- P0A-AC01,P0A-AC03,P0A-AC04,P0A-AC05,P0A-AC06,P0A-AC08: P0A-T09 — Web Setup+Models 流程和重启/密钥 E2E

## Phase Self-review / Handoff
- [ ] All AC01–AC08 have positive and negative tests with real provider compatibility recorded separately from mock.
- [ ] Commands, targets and interfaces match repo actual paths; update plan via ADR if changed.
- [ ] No user secret in CI or public artifacts; no skipped tests.
- [ ] Gate G0 evidence manifest and explicit PASS/FAIL/BLOCKED/NOT RUN decision.
**Execution handoff:** Review spec and this plan, then execute one task per reviewable commit. Prefer fresh subagent implementation + spec/quality reviewers when available; otherwise inline with explicit review limitation. Do not merge automatically.

## Explicit AC Coverage (implementation ownership)

- P0A-AC01 → P0A-T02, P0A-T09.
- P0A-AC02 → P0A-T04, P0A-T05.
- P0A-AC03 → P0A-T05, P0A-T06, P0A-T07, P0A-T09.
- P0A-AC04 → P0A-T08, P0A-T09.
- P0A-AC05 → P0A-T08, P0A-T09.
- P0A-AC06 → P0A-T03, P0A-T09.
- P0A-AC07 → P0A-T07.
- P0A-AC08 → P0A-T06, P0A-T09.

**Current test state:** ALL NOT RUN until a developer executes these exact tasks and records evidence.
