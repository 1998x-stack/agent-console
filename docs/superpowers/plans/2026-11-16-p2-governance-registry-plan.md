# P2 Organization & Public Registry — Implementation Plan
> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans. Follow RED→GREEN→REFACTOR for each independently reviewable task.

**Goal:** Add safe multi-user workspaces, org policy, optional public Skill Registry, approval, creator Unlist and security Revoke.
**Architecture:** Separate client creator, org-admin and public moderator permissions; verified OS isolation, immutable releases, scoped policy and audit.
**Tech Stack:** FastAPI/Alembic/Postgres, Next.js/Playwright, Pi Runner, isolated sandbox, optional HTTPS Registry.
**Spec:** [P2 Design Spec](../specs/2026-11-16-p2-governance-registry-spec.md).

## Global Constraints
- P2 begins only after P1 and multi-user sandbox negative tests pass.
- No client role flag grants platform moderation or unscoped file/Key reads.
- Public approval binds immutable Release digest; Unlist != Revoke; Installation separate.
- Local Store works offline when optional remote service fails.
- All user-facing moderation records include audit and appeal path.

## Review Focus
1. File/session/Key cross-user leak from Pi Worker.
2. Organization role escalation and policy cache stale.
3. Public submission approval race and digest replacement.
4. Unlist vs revoked installed version semantics.
5. Remote Registry offline, poisoned package or tampered signature.

## Task P2-T01: Multi-user runtime isolation threat model and measured gate
**Depends:** P1 Gate. **Spec:** P2-AC01.
**Files:** docs/security/multi-user-isolation.md; tests/security/multitenant-mount.spec.ts; services/runner-manager/policies/multiuser.yaml.
**Interface:** per-user mount/process/secret/network boundaries actually verified, unsafe mode off by default.
**Test:** `pnpm exec playwright test tests/security/multitenant-mount.spec.ts`.
**Expected RED:** sandbox A sees B files/session/Key or untrusted extension runs.
**Expected GREEN:** per-user mount/process/secret/network boundaries actually verified, unsafe mode off by default.

- [ ] Inspect P2 Spec, existing ACL/RunSpec/Skill Release contracts and prerequisite gate.
- [ ] Add targeted failing test and negative abuse case.
- [ ] Run `pnpm exec playwright test tests/security/multitenant-mount.spec.ts` and verify expected RED (sandbox A sees B files/session/Key or untrusted extension runs).
- [ ] Implement minimum transaction or permission boundary for Multi-user runtime isolation threat model and measured gate.
- [ ] Run `pnpm exec playwright test tests/security/multitenant-mount.spec.ts` to GREEN, then refactor with immutable version guarantees.
- [ ] Run `make test-security && make test-integration` and any matching browser E2E; record outputs.
- [ ] Commit task, update gotchas, request spec + security/quality reviews.

## Task P2-T02: Organization membership and Invitation ACL
**Depends:** T01. **Spec:** P2-AC02.
**Files:** services/api/alembic/versions/0005_organizations.py; services/api/app/organizations/routes.py; services/api/tests/test_org_membership.py.
**Interface:** org owner/admin/member scope and invite/revoke with no private leakage.
**Test:** `uv run pytest services/api/tests/test_org_membership.py -q`.
**Expected RED:** membership forging/leaving retains workspace access.
**Expected GREEN:** org owner/admin/member scope and invite/revoke with no private leakage.

- [ ] Inspect P2 Spec, existing ACL/RunSpec/Skill Release contracts and prerequisite gate.
- [ ] Add targeted failing test and negative abuse case.
- [ ] Run `uv run pytest services/api/tests/test_org_membership.py -q` and verify expected RED (membership forging/leaving retains workspace access).
- [ ] Implement minimum transaction or permission boundary for Organization membership and Invitation ACL.
- [ ] Run `uv run pytest services/api/tests/test_org_membership.py -q` to GREEN, then refactor with immutable version guarantees.
- [ ] Run `make test-security && make test-integration` and any matching browser E2E; record outputs.
- [ ] Commit task, update gotchas, request spec + security/quality reviews.

## Task P2-T03: Org policy for model, tool and Skill scopes
**Depends:** T02. **Spec:** P2-AC02/AC09.
**Files:** services/api/app/policy/organization.py; services/api/tests/test_org_policies.py; apps/web/app/admin/organization/page.tsx.
**Interface:** policy hard-filtered at API/RunSpec/Tool Gateway, admin UI correct.
**Test:** `uv run pytest services/api/tests/test_org_policies.py -q`.
**Expected RED:** member installs disallowed Skill or reads admin Key.
**Expected GREEN:** policy hard-filtered at API/RunSpec/Tool Gateway, admin UI correct.

- [ ] Inspect P2 Spec, existing ACL/RunSpec/Skill Release contracts and prerequisite gate.
- [ ] Add targeted failing test and negative abuse case.
- [ ] Run `uv run pytest services/api/tests/test_org_policies.py -q` and verify expected RED (member installs disallowed Skill or reads admin Key).
- [ ] Implement minimum transaction or permission boundary for Org policy for model, tool and Skill scopes.
- [ ] Run `uv run pytest services/api/tests/test_org_policies.py -q` to GREEN, then refactor with immutable version guarantees.
- [ ] Run `make test-security && make test-integration` and any matching browser E2E; record outputs.
- [ ] Commit task, update gotchas, request spec + security/quality reviews.

## Task P2-T04: Optional remote Registry protocol and digest verification
**Depends:** T01,T03. **Spec:** P2-AC07.
**Files:** services/api/app/skills/remote_registry.py; services/api/tests/test_remote_registry.py; packages/contracts/schemas/remote-registry.schema.json.
**Interface:** TLS/digest/allowlist checked and local bundled/private Store remains offline.
**Test:** `uv run pytest services/api/tests/test_remote_registry.py -q`.
**Expected RED:** remote response substitutes unverified blob or offline blocks local Store.
**Expected GREEN:** TLS/digest/allowlist checked and local bundled/private Store remains offline.

- [ ] Inspect P2 Spec, existing ACL/RunSpec/Skill Release contracts and prerequisite gate.
- [ ] Add targeted failing test and negative abuse case.
- [ ] Run `uv run pytest services/api/tests/test_remote_registry.py -q` and verify expected RED (remote response substitutes unverified blob or offline blocks local Store).
- [ ] Implement minimum transaction or permission boundary for Optional remote Registry protocol and digest verification.
- [ ] Run `uv run pytest services/api/tests/test_remote_registry.py -q` to GREEN, then refactor with immutable version guarantees.
- [ ] Run `make test-security && make test-integration` and any matching browser E2E; record outputs.
- [ ] Commit task, update gotchas, request spec + security/quality reviews.

## Task P2-T05: Public submission + automated scan pipeline
**Depends:** T04. **Spec:** P2-AC03/AC09.
**Files:** services/api/alembic/versions/0006_listings_review.py; services/api/app/moderation/submissions.py; services/api/tests/test_submissions.py.
**Interface:** submission bound to immutable digest with static/dynamic scan evidence.
**Test:** `uv run pytest services/api/tests/test_submissions.py -q`.
**Expected RED:** unvalidated/private-unauthorized Release publicly visible.
**Expected GREEN:** submission bound to immutable digest with static/dynamic scan evidence.

- [ ] Inspect P2 Spec, existing ACL/RunSpec/Skill Release contracts and prerequisite gate.
- [ ] Add targeted failing test and negative abuse case.
- [ ] Run `uv run pytest services/api/tests/test_submissions.py -q` and verify expected RED (unvalidated/private-unauthorized Release publicly visible).
- [ ] Implement minimum transaction or permission boundary for Public submission + automated scan pipeline.
- [ ] Run `uv run pytest services/api/tests/test_submissions.py -q` to GREEN, then refactor with immutable version guarantees.
- [ ] Run `make test-security && make test-integration` and any matching browser E2E; record outputs.
- [ ] Commit task, update gotchas, request spec + security/quality reviews.

## Task P2-T06: Moderator review/decision and publication transaction
**Depends:** T05. **Spec:** P2-AC03/AC06/AC09.
**Files:** services/api/app/moderation/reviews.py; services/api/tests/test_review_queue.py; apps/web/app/admin/reviews/page.tsx.
**Interface:** independent moderator permission, approved digest only, auditable decision.
**Test:** `uv run pytest services/api/tests/test_review_queue.py -q`.
**Expected RED:** creator self-approves or concurrent review double-publishes.
**Expected GREEN:** independent moderator permission, approved digest only, auditable decision.

- [ ] Inspect P2 Spec, existing ACL/RunSpec/Skill Release contracts and prerequisite gate.
- [ ] Add targeted failing test and negative abuse case.
- [ ] Run `uv run pytest services/api/tests/test_review_queue.py -q` and verify expected RED (creator self-approves or concurrent review double-publishes).
- [ ] Implement minimum transaction or permission boundary for Moderator review/decision and publication transaction.
- [ ] Run `uv run pytest services/api/tests/test_review_queue.py -q` to GREEN, then refactor with immutable version guarantees.
- [ ] Run `make test-security && make test-integration` and any matching browser E2E; record outputs.
- [ ] Commit task, update gotchas, request spec + security/quality reviews.

## Task P2-T07: Creator Unlist vs Security Revoke & notices
**Depends:** T06. **Spec:** P2-AC04/AC05/AC06.
**Files:** services/api/app/skills/distribution.py; services/api/app/moderation/revocations.py; services/api/tests/test_unlist_revoke.py; apps/web/app/my-skills/[id]/distribution/page.tsx.
**Interface:** unlist stops new installs, revoke blocks affected digest and audits impact.
**Test:** `uv run pytest services/api/tests/test_unlist_revoke.py -q`.
**Expected RED:** unlist deletes installed blobs or revoked digest still allowed new tool.
**Expected GREEN:** unlist stops new installs, revoke blocks affected digest and audits impact.

- [ ] Inspect P2 Spec, existing ACL/RunSpec/Skill Release contracts and prerequisite gate.
- [ ] Add targeted failing test and negative abuse case.
- [ ] Run `uv run pytest services/api/tests/test_unlist_revoke.py -q` and verify expected RED (unlist deletes installed blobs or revoked digest still allowed new tool).
- [ ] Implement minimum transaction or permission boundary for Creator Unlist vs Security Revoke & notices.
- [ ] Run `uv run pytest services/api/tests/test_unlist_revoke.py -q` to GREEN, then refactor with immutable version guarantees.
- [ ] Run `make test-security && make test-integration` and any matching browser E2E; record outputs.
- [ ] Commit task, update gotchas, request spec + security/quality reviews.

## Task P2-T08: Cross-tenant publish/install/revoke security & fault E2E
**Depends:** T01-T07. **Spec:** P2-AC01-AC09.
**Files:** tests/e2e/p2-registry-governance.spec.ts; tests/security/org-isolation.spec.ts; tests/fixtures/registry-malicious/; docs/gotchas.md.
**Interface:** real multi-user OS isolation and full reviewed lifecycle with offline fallback.
**Test:** `pnpm exec playwright test tests/e2e/p2-registry-governance.spec.ts`.
**Expected RED:** cross-user access, bypass public approval, inconsistent concurrent lifecycle.
**Expected GREEN:** real multi-user OS isolation and full reviewed lifecycle with offline fallback.

- [ ] Inspect P2 Spec, existing ACL/RunSpec/Skill Release contracts and prerequisite gate.
- [ ] Add targeted failing test and negative abuse case.
- [ ] Run `pnpm exec playwright test tests/e2e/p2-registry-governance.spec.ts` and verify expected RED (cross-user access, bypass public approval, inconsistent concurrent lifecycle).
- [ ] Implement minimum transaction or permission boundary for Cross-tenant publish/install/revoke security & fault E2E.
- [ ] Run `pnpm exec playwright test tests/e2e/p2-registry-governance.spec.ts` to GREEN, then refactor with immutable version guarantees.
- [ ] Run `make test-security && make test-integration` and any matching browser E2E; record outputs.
- [ ] Commit task, update gotchas, request spec + security/quality reviews.

## Gate G4 Review
- [ ] P2-AC01–AC09 mapped to executed security/behavior tests.
- [ ] Actual multi-user shell and filesystem negative tests run on supported host; otherwise disable risky feature.
- [ ] Role/permission attack and approval races audited.
- [ ] Creator Unlist does not delete previous users' installation; moderator Revoke blocks actual execution.
- [ ] Local mode unchanged and verified; no merge without user approval.

## Explicit AC Coverage (implementation ownership)

- P2-AC01 → P2-T01, P2-T08.
- P2-AC02 → P2-T02, P2-T03, P2-T08.
- P2-AC03 → P2-T05, P2-T06, P2-T08.
- P2-AC04 → P2-T07, P2-T08.
- P2-AC05 → P2-T07, P2-T08.
- P2-AC06 → P2-T06, P2-T07, P2-T08.
- P2-AC07 → P2-T04, P2-T08.
- P2-AC08 → P2-T08.
- P2-AC09 → P2-T03, P2-T05, P2-T06, P2-T08.

**Current test state:** ALL NOT RUN until a developer executes these exact tasks and records evidence.
