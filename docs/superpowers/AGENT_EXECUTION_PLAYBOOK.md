# Coding Agent / Pi Agent Task Execution Playbook

> Applied by future Codex/Pi implementers; no coding steps have been run by publishing this document. Never merge, deploy, delete user volumes or publish without authorization.

## 1. Read before touching code

- `docs/superpowers/README.md` and master spec;
- current phase spec and implementation plan;
- `docs/superpowers/WORKFLOW_AND_HANDOFF.md` and `VERIFICATION_AND_TEST_STRATEGY.md`;
- `docs/PI_AGENT_INTEGRATION.md`, `docs/SECURITY_MODEL.md`, `docs/DATA_MODEL.md` as relevant;
- `docs/gotchas.md` and last branch test results;
- if official Superpowers Skills are installed in this Agent environment, read the relevant CURRENT skill (brainstorming, writing-plans, TDD, debugging, verify-before-completion). Do not claim skill invocation if unavailable.

## 2. Preflight

Record Git base/head SHAs, branch/worktree, clean status, node/pnpm/uv/Python/Docker/Pi versions and baseline test status. If no test harness exists yet, mark NOT AVAILABLE and start at P0A-T01; don't fabricate a baseline. Check prior tasks' Interfaces blocks for compatibility before starting the current task.

## 3. Task loop

```text
read spec + exact task → check prerequisites
→ write failing test → execute RED and inspect output
→ implement minimum → execute GREEN
→ refactor → test related paths → evidence + gotchas + commit
→ review A: requirement compliance
→ review B: code/security quality
→ mark VERIFIED or BLOCKED and continue
```

If platform has no subagent capability, execute inline and explicitly label review as SELF-REVIEW; request independent whole-branch code review when possible. Never invent a fresh reviewer.

## 4. Copy-ready execution prompt

```text
Act as an implementer of ONE task from the Agent Console implementation plan.
Repository: 1998x-stack/agent-console.
Read the master spec, phase spec, phase plan, workflow, security model, and
docs/gotchas.md. Work in an isolated worktree/feature branch.
Use Pi SDK as the agent engine; Web model BYOK and server-derived
/{user-id}/workspace are hard requirements. Do not bypass the tool gateway,
secret vault, sandbox policy or feature flags.
Run RED then GREEN then neighboring tests, and preserve their outputs.
Tests never executed must be marked NOT RUN. No false green CI.
Update gotchas on each reproducible issue.
Provide changed paths, commit SHA, real tests and exit codes, security impact,
review status and the next exact Task ID. Do not merge or deploy.
```

## 5. Review protocol

**Spec compliance reviewer:** verify target AC, cross-module contracts, permission checks, negative behavior and absence of scope creep.

**Code/security reviewer:** examine test quality, types, API/DB compatibility, secrets, path traversal, concurrency, cleanup, performance, tool safety and fragile mocks. Critical/Important findings block task completion until repaired and rerun. Reviewer findings must be preserved.

## 6. Agent handoff YAML

```yaml
repository: 1998x-stack/agent-console
branch: feature/<task-id>
base_sha: "<actual>"
head_sha: "<actual>"
phase: P0A
task_id: P0A-T01
spec_path: docs/superpowers/specs/<phase>-spec.md
plan_path: docs/superpowers/plans/<phase>-plan.md
status: VERIFIED | BLOCKED | IMPLEMENTED_UNVERIFIED
tests:
  - command: "<actual>"
    result: PASSED | FAILED | NOT_RUN
    exit_code: "<actual code or null>"
reviews:
  spec: PASSED | FAILED | NOT_RUN
  quality: PASSED | FAILED | NOT_RUN
gotchas: []
next_task_id: "<id or null>"
```

## 7. Mandatory stops

Irreversible data loss, production deployment, public publishing, external cost not explicitly authorized, new sensitive access or merging shared main; if the phase spec fundamentally contradicts security, record blocker and ask for a ruling. Routine implementation ambiguity may be resolved via small PoC + ADR while preserving original requirements.
