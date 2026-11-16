# Agent Console Master Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended when available) or superpowers:executing-plans to implement this plan task-by-task. This is a design plan; it has not been executed.
>
> **Goal:** Progress from an empty documentation-first repository to a tested self-hosted Pi Agent Console with Workspace and Skill Store, then expand creators, governance and integrations only after explicit gates.
>
> **Architecture:** Next.js + FastAPI control plane + Node Pi Worker + PostgreSQL + per-run constrained workspace + local Registry. Server owns auth, secrets, ACL and RunEvent state; Pi owns agent loop and resource loading.
>
> **Tech Stack:** TypeScript/pnpm, Next.js, Python/FastAPI/uv/pytest, PostgreSQL/Alembic, Docker Compose, Pi SDK, Playwright. Pin tested versions before shipping; these are target choices not installed packages.
>
> **Spec:** [Master Product Architecture](../specs/2026-11-16-master-product-architecture.md).

## Global Constraints

1. Read the master spec, current phase spec, this plan and [Workflow](../WORKFLOW_AND_HANDOFF.md) before any implementation.
2. No public SaaS dependency for first run: local Docker boots with no model Key.
3. Runtime must be **Pi**; don't build a second home-grown agent loop.
4. Logical path `/{user-id}/workspace` is derived from backend authenticated UUID and constrained runner; user-supplied cwd/mount is forbidden.
5. BYOK Key stored encrypted and never exposed in logs, Pi Session, Tool Env or browser read responses.
6. Security policy + OS sandbox apply independently of Pi prompts and tool allowlist.
7. `Skill, Release, Listing, Installation` separate; release immutable, install digest pinned.
8. No skipped/removed tests as workaround; report FAIL and NOT RUN; no merge to main without authorization.

## Dependency Plan

```text
P0A   A00 repo/CI + A01 Docker/auth + A02 model config
   ↓
P0B   A03 Pi SDK worker + A04 Run/Event + A05 Workspace/files + A06 Office/Code
   ↓
P0C   A07 bundled Store/installation/loader + A08 full browser E2E
   ↓
P1    B01 creator draft/tests + B02 safe code edits + B03 backups & upgrades
   ↓
P2    C01 multi-user OS isolation + C02 org/public registry & governance
   ↓
P3    measured value: CLI, MCP, search, operations
```

The A00–C02 labels preserve prior [functional backlog](../../functional-decomposition/11_ROADMAP_AND_BACKLOG.md), while each phase plan introduces finer `P0A-Txx` etc IDs.

## Exact Phase Plans

| Order | Phase | Plan | Prerequisite Gate | Must deliver |
|---|---|---|---|---|
| 1 | P0A | [Bootstrap + Model BYOK](2026-11-16-p0a-bootstrap-models-plan.md) | architecture / security spec approved | clean Compose + encrypted model settings |
| 2 | P0B | [Pi + Workspace](2026-11-16-p0b-pi-workspace-plan.md) | P0A PASS | actual Pi session/tool events + file/artifact |
| 3 | P0C | [Local Store + E2E](2026-11-16-p0c-local-store-e2e-plan.md) | P0B PASS | offline Skill installed and invoked from Web |
| 4 | P1 | [Creator + Sandbox](2026-11-16-p1-creator-sandbox-plan.md) | P0C + threat model PASS | private Skill lifecycle, review changes |
| 5 | P2 | [Governance + Registry](2026-11-16-p2-governance-registry-plan.md) | P1 + multi-user isolation PASS | publish/unlist/revoke/org ACL |
| 6 | P3 | [Ecosystem](2026-11-16-p3-ecosystem-plan.md) | demand evidence + relevant security PASS | CLI/MCP/search/ops as justified |

## Per Task Execution Cadence

Each task should be bounded by one reviewer-meaningful deliverable, commonly ~2–5 minute **steps**, not a fixed elapsed task duration. Every task file block states:
- exact proposed paths and signatures;
- dependent Task IDs;
- failing test filename/command and expected **RED** reason;
- implementation minimal **GREEN** behavior;
- neighbor tests, edge/security negative tests and commit boundary;
- a spec AC / requirement ID.

An implementer should not need to invent a security policy while “following” a plan. If an interface isn't experimentally known, use an explicit PoC Task and ADR first.

## Integration Gates

- **Gate G0** (P0A): clean Docker/bootstrap + model tested, Key redaction, SSRF.
- **Gate G1** (P0B): true Pi, safe workspace, SSE/cancel/session, validated artifacts.
- **Gate G2** (P0C): skill pin/loader, offline Store, browser end-to-end and restart/restore.
- **Gate G3** (P1): creator two-input eval + safe sandbox/changes.
- **Gate G4** (P2): cross-user OS isolation + policy + reviewed public lifecycle.
- **Gate G5** (P3): actual adoption/operational metrics and no regression.

Critical security failures block progression. Detailed conditions: [Gates](../PHASE_DEPENDENCIES_AND_GATES.md). Evidence: [Verification](../VERIFICATION_AND_TEST_STRATEGY.md).

## Recommended First PRs

1. **A00**: repository worktree, monorepo skeleton, package managers/lockfiles, real lint/typecheck/pytest/Playwright skeleton, docs link checks, CI; no business UX.
2. **A01**: DB + Compose + secure first-time local admin setup, readiness. Confirm cold boot without API Key.
3. **A02**: Web BYOK provider config + encrypted vault + local/remote provider probes, real model smoke. No Pi file execution claim.

Keep separate PRs with independent RED/GREEN evidence; later steps depend on stable contracts, not optimistic UI mocks.

## Review Focus

1. Container can reach host local model but other tenants cannot SSRF internal metadata.
2. User-specific `/{user-id}/workspace` cannot be changed via URL/header/Prompt/tool input.
3. Pi Session restart and one-writer lease cannot lose or duplicate tool effects.
4. Installed Skill cannot activate unsafe Pi Extensions or inherit network/shell rights.
5. Missing/corrupt artifact, partial test or truncated model output cannot become SUCCEEDED.

## Self-review checklist (apply before implementation)

- [ ] Every spec AC maps to at least one Task and executable test command.
- [ ] Interfaces produced by one Task match consumers in the next.
- [ ] Each step is one action; RED/GREEN expected outcomes are meaningful.
- [ ] Negative tests cover five Review Focus risks above.
- [ ] Plan code is no longer than necessary; never paste complete implementation.
- [ ] Unverified dependencies and version choices recorded as experiments/ADR.
- [ ] Tool credentials, user private content and external side effects are never automatically consented.
- [ ] Merge/branch operations remain subject to the repository's PR policy.

## Human/Agent Handoff

The user requested phased docs; these plans are ready to review, **not permission to claim implementation success**. Once the phase spec is accepted, follow the user's chosen executor (Codex/Pi). Subagent-driven mode should use fresh implementer plus independent spec/quality review per task when supported; otherwise inline work must clearly state review limitations.

Current status: **SPEC/PLAN DOCUMENTATION ONLY**. All real Pi, Docker, schema and browser tests are NOT RUN.
