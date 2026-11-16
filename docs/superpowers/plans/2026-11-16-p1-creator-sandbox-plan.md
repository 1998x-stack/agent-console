# P1 Private Creator & Safe Writes — Implementation Plan
> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans. Each task must be independently reviewable and test driven.

**Goal:** Turn successful work into a tested private Skill and allow reviewed, safely sandboxed file/code changes.
**Architecture:** Creator Draft/Eval/immutable Release in Registry, user Studio UX, per-run sandbox and Git Worktree staging. No public publishing yet.
**Tech Stack:** FastAPI/pytest/Alembic, Next.js/Playwright, Pi Worker, Docker sandbox, Git.
**Spec:** [P1 Design Spec](../specs/2026-11-16-p1-creator-sandbox-spec.md).

## Global Constraints
- Requires P0 gate. Creator is a normal User; owns Draft and Release, no platform-admin privilege needed.
- No untrusted Pi Extension autoload; install and script execution are distinct rights.
- Private data/Key must be excluded from Skill generated/exported package.
- Write/bash enabled only after sandbox isolation verified, never on API process.
- Release bytes immutable; installed digest frozen for each active Run.
- Every Task RED/GREEN/neighbor tests with actual outputs; NOT RUN blocks claim.

## Review Focus
1. Draft write conflict and owner ACL.
2. PII/credential leakage in generated Skill.
3. Zip slip, unexpected .pi/extensions and external dependencies.
4. Sandbox escape and missing process cleanup on cancellation.
5. Apply stale Diff over dirty repo and release digest drift.

## Task P1-T01: Creator Draft schema + object ownership
**Depends:** P0C Gate. **Spec:** P1-AC01/AC02.
**Files:** services/api/alembic/versions/0004_skill_drafts.py; services/api/app/skills/drafts.py; services/api/tests/test_skill_drafts.py.
**Interface:** owner ACL and expected_revision CAS with 409 conflict.
**Test:** `uv run pytest services/api/tests/test_skill_drafts.py -q`.
**Expected RED:** other user can edit Draft or revision conflict silently overwrites.
**Expected GREEN:** owner ACL and expected_revision CAS with 409 conflict.

- [ ] Review the phase Spec and prerequisite interface signatures.
- [ ] Write focused failing positive + negative tests in declared test file.
- [ ] Execute `uv run pytest services/api/tests/test_skill_drafts.py -q`, confirm RED is a legitimate missing feature assertion.
- [ ] Implement minimum contract for Creator Draft schema + object ownership; no hidden permissions or scope creep.
- [ ] Re-run `uv run pytest services/api/tests/test_skill_drafts.py -q` to GREEN and refactor.
- [ ] Run `make test-unit && make test-contract && make test-security` where applicable; record exit and model/sandbox conditions.
- [ ] Commit, log gotchas, obtain both spec and code/security review.

## Task P1-T02: Safe ZIP/.skill import
**Depends:** T01. **Spec:** P1-AC05.
**Files:** services/api/app/skills/package_validator.py; services/api/tests/test_skill_import.py; tests/fixtures/skill-malicious/.
**Interface:** bounded safe import and digest verification, never activate .pi/extensions.
**Test:** `uv run pytest services/api/tests/test_skill_import.py -q`.
**Expected RED:** ZIP slip, symlink or decompression bomb accepted.
**Expected GREEN:** bounded safe import and digest verification, never activate .pi/extensions.

- [ ] Review the phase Spec and prerequisite interface signatures.
- [ ] Write focused failing positive + negative tests in declared test file.
- [ ] Execute `uv run pytest services/api/tests/test_skill_import.py -q`, confirm RED is a legitimate missing feature assertion.
- [ ] Implement minimum contract for Safe ZIP/.skill import; no hidden permissions or scope creep.
- [ ] Re-run `uv run pytest services/api/tests/test_skill_import.py -q` to GREEN and refactor.
- [ ] Run `make test-unit && make test-contract && make test-security` where applicable; record exit and model/sandbox conditions.
- [ ] Commit, log gotchas, obtain both spec and code/security review.

## Task P1-T03: Skill Studio editor and Draft revision UX
**Depends:** T01. **Spec:** P1-AC02.
**Files:** apps/web/app/my-skills/page.tsx; apps/web/app/my-skills/[id]/page.tsx; apps/web/components/SkillEditor.tsx; tests/e2e/skill-studio.spec.ts.
**Interface:** draft editor works with revision conflict dialog and file tree.
**Test:** `pnpm exec playwright test tests/e2e/skill-studio.spec.ts`.
**Expected RED:** can't edit or refresh; concurrent edit loses content.
**Expected GREEN:** draft editor works with revision conflict dialog and file tree.

- [ ] Review the phase Spec and prerequisite interface signatures.
- [ ] Write focused failing positive + negative tests in declared test file.
- [ ] Execute `pnpm exec playwright test tests/e2e/skill-studio.spec.ts`, confirm RED is a legitimate missing feature assertion.
- [ ] Implement minimum contract for Skill Studio editor and Draft revision UX; no hidden permissions or scope creep.
- [ ] Re-run `pnpm exec playwright test tests/e2e/skill-studio.spec.ts` to GREEN and refactor.
- [ ] Run `make test-unit && make test-contract && make test-security` where applicable; record exit and model/sandbox conditions.
- [ ] Commit, log gotchas, obtain both spec and code/security review.

## Task P1-T04: Run → Save as Skill with redaction
**Depends:** T01,T03. **Spec:** P1-AC01.
**Files:** services/api/app/skills/generate_from_run.py; services/api/tests/test_generate_skill.py; apps/web/components/SaveAsSkill.tsx.
**Interface:** user-selected inputs become sanitized editable Draft; incomplete LLM text not released.
**Test:** `uv run pytest services/api/tests/test_generate_skill.py -q`.
**Expected RED:** private file or test secret copied into package.
**Expected GREEN:** user-selected inputs become sanitized editable Draft; incomplete LLM text not released.

- [ ] Review the phase Spec and prerequisite interface signatures.
- [ ] Write focused failing positive + negative tests in declared test file.
- [ ] Execute `uv run pytest services/api/tests/test_generate_skill.py -q`, confirm RED is a legitimate missing feature assertion.
- [ ] Implement minimum contract for Run → Save as Skill with redaction; no hidden permissions or scope creep.
- [ ] Re-run `uv run pytest services/api/tests/test_generate_skill.py -q` to GREEN and refactor.
- [ ] Run `make test-unit && make test-contract && make test-security` where applicable; record exit and model/sandbox conditions.
- [ ] Commit, log gotchas, obtain both spec and code/security review.

## Task P1-T05: Skill positive/negative and two-fixture evaluator
**Depends:** T02,T04. **Spec:** P1-AC03.
**Files:** services/api/app/skills/evaluation.py; tests/fixtures/skill-evals/; services/api/tests/test_skill_evaluation.py.
**Interface:** positive + negative trigger and 2 different input Oracles; status PASSED/FAILED/NOT_RUN.
**Test:** `uv run pytest services/api/tests/test_skill_evaluation.py -q`.
**Expected RED:** single memorized input passes, wrong trigger never tested.
**Expected GREEN:** positive + negative trigger and 2 different input Oracles; status PASSED/FAILED/NOT_RUN.

- [ ] Review the phase Spec and prerequisite interface signatures.
- [ ] Write focused failing positive + negative tests in declared test file.
- [ ] Execute `uv run pytest services/api/tests/test_skill_evaluation.py -q`, confirm RED is a legitimate missing feature assertion.
- [ ] Implement minimum contract for Skill positive/negative and two-fixture evaluator; no hidden permissions or scope creep.
- [ ] Re-run `uv run pytest services/api/tests/test_skill_evaluation.py -q` to GREEN and refactor.
- [ ] Run `make test-unit && make test-contract && make test-security` where applicable; record exit and model/sandbox conditions.
- [ ] Commit, log gotchas, obtain both spec and code/security review.

## Task P1-T06: Immutable private Release, upgrade and rollback
**Depends:** T05. **Spec:** P1-AC04/AC08.
**Files:** services/api/app/skills/releases.py; services/api/tests/test_private_releases.py; apps/web/components/ReleaseHistory.tsx.
**Interface:** new immutable Release, pinned Installation, explicit update/rollback and audit.
**Test:** `uv run pytest services/api/tests/test_private_releases.py -q`.
**Expected RED:** old digest changes during upgrade or rollback to revoked blob allowed.
**Expected GREEN:** new immutable Release, pinned Installation, explicit update/rollback and audit.

- [ ] Review the phase Spec and prerequisite interface signatures.
- [ ] Write focused failing positive + negative tests in declared test file.
- [ ] Execute `uv run pytest services/api/tests/test_private_releases.py -q`, confirm RED is a legitimate missing feature assertion.
- [ ] Implement minimum contract for Immutable private Release, upgrade and rollback; no hidden permissions or scope creep.
- [ ] Re-run `uv run pytest services/api/tests/test_private_releases.py -q` to GREEN and refactor.
- [ ] Run `make test-unit && make test-contract && make test-security` where applicable; record exit and model/sandbox conditions.
- [ ] Commit, log gotchas, obtain both spec and code/security review.

## Task P1-T07: Real write/bash sandbox + Tool Gate negative suite
**Depends:** P0B-T06,T05. **Spec:** P1-AC06.
**Files:** services/runner-manager/sandbox_policy.py; services/pi-worker/src/pi/tool-policy.ts; tests/security/sandbox-write.spec.ts.
**Interface:** staged writes, no unauthorized network/mount/credential, enforced execution timeout.
**Test:** `pnpm exec playwright test tests/security/sandbox-write.spec.ts`.
**Expected RED:** process reads host secrets/other user dirs or writes outside staging.
**Expected GREEN:** staged writes, no unauthorized network/mount/credential, enforced execution timeout.

- [ ] Review the phase Spec and prerequisite interface signatures.
- [ ] Write focused failing positive + negative tests in declared test file.
- [ ] Execute `pnpm exec playwright test tests/security/sandbox-write.spec.ts`, confirm RED is a legitimate missing feature assertion.
- [ ] Implement minimum contract for Real write/bash sandbox + Tool Gate negative suite; no hidden permissions or scope creep.
- [ ] Re-run `pnpm exec playwright test tests/security/sandbox-write.spec.ts` to GREEN and refactor.
- [ ] Run `make test-unit && make test-contract && make test-security` where applicable; record exit and model/sandbox conditions.
- [ ] Commit, log gotchas, obtain both spec and code/security review.

## Task P1-T08: Git Worktree Diff, tests and explicit Apply
**Depends:** T07. **Spec:** P1-AC07.
**Files:** services/api/app/workspaces/changes.py; services/api/tests/test_apply_changes.py; apps/web/components/ReviewChanges.tsx.
**Interface:** worktree diff with real test command, atomic apply requires approval and base revision.
**Test:** `uv run pytest services/api/tests/test_apply_changes.py -q`.
**Expected RED:** dirty repo lost, stale baseline silently overwritten, unapproved apply succeeds.
**Expected GREEN:** worktree diff with real test command, atomic apply requires approval and base revision.

- [ ] Review the phase Spec and prerequisite interface signatures.
- [ ] Write focused failing positive + negative tests in declared test file.
- [ ] Execute `uv run pytest services/api/tests/test_apply_changes.py -q`, confirm RED is a legitimate missing feature assertion.
- [ ] Implement minimum contract for Git Worktree Diff, tests and explicit Apply; no hidden permissions or scope creep.
- [ ] Re-run `uv run pytest services/api/tests/test_apply_changes.py -q` to GREEN and refactor.
- [ ] Run `make test-unit && make test-contract && make test-security` where applicable; record exit and model/sandbox conditions.
- [ ] Commit, log gotchas, obtain both spec and code/security review.

## Task P1-T09: Integrated Creator/Sandbox E2E + restart
**Depends:** T03-T08. **Spec:** P1-AC01-AC09.
**Files:** tests/e2e/p1-creator.spec.ts; tests/ops/p1-restore.sh; docs/gotchas.md.
**Interface:** real Skill created/tested/installed; Code diff approved; restore and negative cases pass.
**Test:** `pnpm exec playwright test tests/e2e/p1-creator.spec.ts`.
**Expected RED:** draft/release/tests vanish after restart, unsafe execution or hash drift.
**Expected GREEN:** real Skill created/tested/installed; Code diff approved; restore and negative cases pass.

- [ ] Review the phase Spec and prerequisite interface signatures.
- [ ] Write focused failing positive + negative tests in declared test file.
- [ ] Execute `pnpm exec playwright test tests/e2e/p1-creator.spec.ts`, confirm RED is a legitimate missing feature assertion.
- [ ] Implement minimum contract for Integrated Creator/Sandbox E2E + restart; no hidden permissions or scope creep.
- [ ] Re-run `pnpm exec playwright test tests/e2e/p1-creator.spec.ts` to GREEN and refactor.
- [ ] Run `make test-unit && make test-contract && make test-security` where applicable; record exit and model/sandbox conditions.
- [ ] Commit, log gotchas, obtain both spec and code/security review.

## Self-review & Gate G3
- [ ] P1-AC01–AC09 covered by actual tests and logs.
- [ ] At least two independent Skill evaluation fixtures; negative trigger included.
- [ ] No tested shell/network/mount bypass; if sandbox blocked, keep Feature Flag disabled.
- [ ] Write changes apply only with user authorization and base version guard.
- [ ] Backups/restart preserve drafts, releases and current installation pin.
- [ ] Do not merge automatically; report PASS/FAILED/BLOCKED/NOT RUN.
