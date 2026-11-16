# P0C Local Skill Store & E2E — Implementation Plan
> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans. Execute each checklist task RED/GREEN/REFACTOR.

**Goal:** Offline bundled Skill Store, pinned installations loaded by real Pi, full Docker browser E2E.
**Architecture:** Trusted bundled catalog + immutable Registry + Workspace installation API + Pi ResourceLoader + Web Store.
**Tech Stack:** FastAPI/pytest/Alembic/Postgres, Next.js/Playwright, TypeScript Pi SDK, durable file storage.
**Spec:** [P0C Design Spec](../specs/2026-11-16-p0c-local-store-e2e-spec.md).

## Global Constraints
- Requires P0A/P0B Gates. No public Registry or untrusted shell in P0C.
- Release immutable and digest-pinned. Install != permission; Uninstall != Unlist.
- Current active Run preserves previous skill snapshot; disabled Skill excluded next Run.
- Mock/real model tests kept distinct; no test claims without actual command output.

## Review Focus
1. Hash mismatch/cache poisoning. 2. Cross-workspace install.
3. Malicious ZIP and unknown Pi Extension. 4. Active run update race.
5. Restart with missing registry blob or encrypted settings.

## Task P0C-T01: Bundled catalog + validated skills
**Depends:** P0B Gate. **Spec:** P0C-AC01/AC05.
**Files:** packages/skill-catalog/manifest.schema.json, packages/skill-catalog/bundled/{summarize-project,csv-insights}/SKILL.md, tests/unit/test_bundled_catalog.py.
**Interface:** two bundled skills validate deterministically.
**Test:** `uv run pytest tests/unit/test_bundled_catalog.py -q`.
**Expected RED:** invalid/missing manifest or digest not caught. **Expected GREEN:** two bundled skills validate deterministically.
- [ ] Inspect spec and actual dependencies.
- [ ] Write failing test in tests/unit/test_bundled_catalog.py.
- [ ] Run `uv run pytest tests/unit/test_bundled_catalog.py -q`, observe RED caused by this missing behavior.
- [ ] Implement Bundled catalog + validated skills with authorization/validation.
- [ ] Rerun `uv run pytest tests/unit/test_bundled_catalog.py -q`, verify GREEN then refactor.
- [ ] Run neighboring unit/integration/security tests and record actual exit codes.
- [ ] Commit, update gotchas, obtain spec-compliance and quality/security reviews.

## Task P0C-T02: Immutable registry migration
**Depends:** prior applicable tasks. **Spec:** P0C-AC02/AC03.
**Files:** services/api/alembic/versions/0003_registry.py, services/api/app/skills/models.py, services/api/tests/test_registry_migrations.py.
**Interface:** Skill/Release/Listing/Installation distinct and database constrained.
**Test:** `uv run pytest services/api/tests/test_registry_migrations.py -q`.
**Expected RED:** Release can mutate/installation duplicates. **Expected GREEN:** Skill/Release/Listing/Installation distinct and database constrained.
- [ ] Inspect spec and actual dependencies.
- [ ] Write failing test in services/api/tests/test_registry_migrations.py.
- [ ] Run `uv run pytest services/api/tests/test_registry_migrations.py -q`, observe RED caused by this missing behavior.
- [ ] Implement Immutable registry migration with authorization/validation.
- [ ] Rerun `uv run pytest services/api/tests/test_registry_migrations.py -q`, verify GREEN then refactor.
- [ ] Run neighboring unit/integration/security tests and record actual exit codes.
- [ ] Commit, update gotchas, obtain spec-compliance and quality/security reviews.

## Task P0C-T03: Authorized install/disable/uninstall API
**Depends:** prior applicable tasks. **Spec:** P0C-AC02/AC03.
**Files:** services/api/app/skills/routes.py, services/api/app/skills/service.py, services/api/tests/test_installations.py.
**Interface:** per-Workspace pinned Release and idempotency.
**Test:** `uv run pytest services/api/tests/test_installations.py -q`.
**Expected RED:** unauthorized install or repeated install duplicates data. **Expected GREEN:** per-Workspace pinned Release and idempotency.
- [ ] Inspect spec and actual dependencies.
- [ ] Write failing test in services/api/tests/test_installations.py.
- [ ] Run `uv run pytest services/api/tests/test_installations.py -q`, observe RED caused by this missing behavior.
- [ ] Implement Authorized install/disable/uninstall API with authorization/validation.
- [ ] Rerun `uv run pytest services/api/tests/test_installations.py -q`, verify GREEN then refactor.
- [ ] Run neighboring unit/integration/security tests and record actual exit codes.
- [ ] Commit, update gotchas, obtain spec-compliance and quality/security reviews.

## Task P0C-T04: Controlled Pi ResourceLoader
**Depends:** prior applicable tasks. **Spec:** P0C-AC03/AC08.
**Files:** services/pi-worker/src/pi/allowed-skills.ts, services/pi-worker/test/resource-loader.test.ts.
**Interface:** only enabled verified digest in next-run snapshot; Tool Gateway still applies.
**Test:** `pnpm --filter @agent-console/pi-worker test -- resource-loader.test.ts`.
**Expected RED:** foreign/disabled skill or project extension visible. **Expected GREEN:** only enabled verified digest in next-run snapshot; Tool Gateway still applies.
- [ ] Inspect spec and actual dependencies.
- [ ] Write failing test in services/pi-worker/test/resource-loader.test.ts.
- [ ] Run `pnpm --filter @agent-console/pi-worker test -- resource-loader.test.ts`, observe RED caused by this missing behavior.
- [ ] Implement Controlled Pi ResourceLoader with authorization/validation.
- [ ] Rerun `pnpm --filter @agent-console/pi-worker test -- resource-loader.test.ts`, verify GREEN then refactor.
- [ ] Run neighboring unit/integration/security tests and record actual exit codes.
- [ ] Commit, update gotchas, obtain spec-compliance and quality/security reviews.

## Task P0C-T05: Web Explore/Detail/Installed
**Depends:** prior applicable tasks. **Spec:** P0C-AC01/AC02.
**Files:** apps/web/app/skills/page.tsx, apps/web/app/skills/[skillId]/page.tsx, apps/web/app/skills/installed/page.tsx, tests/e2e/skill-store-ui.spec.ts.
**Interface:** offline browse/installation state accurate.
**Test:** `pnpm exec playwright test tests/e2e/skill-store-ui.spec.ts`.
**Expected RED:** offline Store missing, UI state not persisted. **Expected GREEN:** offline browse/installation state accurate.
- [ ] Inspect spec and actual dependencies.
- [ ] Write failing test in tests/e2e/skill-store-ui.spec.ts.
- [ ] Run `pnpm exec playwright test tests/e2e/skill-store-ui.spec.ts`, observe RED caused by this missing behavior.
- [ ] Implement Web Explore/Detail/Installed with authorization/validation.
- [ ] Rerun `pnpm exec playwright test tests/e2e/skill-store-ui.spec.ts`, verify GREEN then refactor.
- [ ] Run neighboring unit/integration/security tests and record actual exit codes.
- [ ] Commit, update gotchas, obtain spec-compliance and quality/security reviews.

## Task P0C-T06: Real Pi Skill invocation
**Depends:** prior applicable tasks. **Spec:** P0C-AC04.
**Files:** tests/fixtures/skill-reuse/, tests/e2e/skill-invocation.spec.ts.
**Interface:** actual Pi loads pinned skill and output verified.
**Test:** `pnpm exec playwright test tests/e2e/skill-invocation.spec.ts`.
**Expected RED:** Pi never loads installed skill or disabled still triggers. **Expected GREEN:** actual Pi loads pinned skill and output verified.
- [ ] Inspect spec and actual dependencies.
- [ ] Write failing test in tests/e2e/skill-invocation.spec.ts.
- [ ] Run `pnpm exec playwright test tests/e2e/skill-invocation.spec.ts`, observe RED caused by this missing behavior.
- [ ] Implement Real Pi Skill invocation with authorization/validation.
- [ ] Rerun `pnpm exec playwright test tests/e2e/skill-invocation.spec.ts`, verify GREEN then refactor.
- [ ] Run neighboring unit/integration/security tests and record actual exit codes.
- [ ] Commit, update gotchas, obtain spec-compliance and quality/security reviews.

## Task P0C-T07: Package and extension negative tests
**Depends:** prior applicable tasks. **Spec:** P0C-AC05/AC08.
**Files:** services/api/app/skills/package_validator.py, services/api/tests/test_registry_security.py, tests/security/skill-packages.spec.ts.
**Interface:** rejected with no installation or tool authorization.
**Test:** `uv run pytest services/api/tests/test_registry_security.py -q`.
**Expected RED:** zip slip/oversize/unknown extension accepted. **Expected GREEN:** rejected with no installation or tool authorization.
- [ ] Inspect spec and actual dependencies.
- [ ] Write failing test in tests/security/skill-packages.spec.ts.
- [ ] Run `uv run pytest services/api/tests/test_registry_security.py -q`, observe RED caused by this missing behavior.
- [ ] Implement Package and extension negative tests with authorization/validation.
- [ ] Rerun `uv run pytest services/api/tests/test_registry_security.py -q`, verify GREEN then refactor.
- [ ] Run neighboring unit/integration/security tests and record actual exit codes.
- [ ] Commit, update gotchas, obtain spec-compliance and quality/security reviews.

## Task P0C-T08: Cold-start browser + backup/restore drill
**Depends:** prior applicable tasks. **Spec:** P0C-AC06/AC07/AC08.
**Files:** tests/e2e/full-local-journey.spec.ts, tests/ops/restore_smoke.sh, docs/deployment/backup.md.
**Interface:** Compose→model→Pi file→Skill→restart/restore works with evidence.
**Test:** `pnpm exec playwright test tests/e2e/full-local-journey.spec.ts`.
**Expected RED:** on restart Skill or session missing, artifact invalid. **Expected GREEN:** Compose→model→Pi file→Skill→restart/restore works with evidence.
- [ ] Inspect spec and actual dependencies.
- [ ] Write failing test in docs/deployment/backup.md.
- [ ] Run `pnpm exec playwright test tests/e2e/full-local-journey.spec.ts`, observe RED caused by this missing behavior.
- [ ] Implement Cold-start browser + backup/restore drill with authorization/validation.
- [ ] Rerun `pnpm exec playwright test tests/e2e/full-local-journey.spec.ts`, verify GREEN then refactor.
- [ ] Run neighboring unit/integration/security tests and record actual exit codes.
- [ ] Commit, update gotchas, obtain spec-compliance and quality/security reviews.

## Exit Gate & Handoff
- [ ] AC01–AC08 mapped to real tests and concrete run logs.
- [ ] No extra script execution privilege from installing a Skill.
- [ ] Browser cold start and restore drill documented with SHA and host versions.
- [ ] Test failures, BLOCKED and NOT RUN listed without false claim.
**Handoff:** Review P0C spec and this task plan before executing; don't merge automatically.
