# Evidence, TDD, Failure Injection & Release Gates

> Design only. Existing implementation tests remain NOT RUN until measured.

## 1. Superpowers-inspired verification contract

Every task must prove RED (test fails for missing behavior) → GREEN (minimal implementation passes) → REFACTOR (re-run target and neighboring tests) → review. A test unexpectedly passing before implementation requires investigating test validity. A fix without executed regression remains IMPLEMENTED_UNVERIFIED.

Distinct evidence types: STATIC, UNIT, CONTRACT, INTEGRATION, E2E, MODEL-EVAL, SECURITY, OPERATIONAL. A mocked provider verifies control flow, never compatibility of Pi SDK with a real model. Pi output claiming an artifact exists never proves it exists or is readable.

## 2. Evidence manifest

Proposed local/CI artifact layout (not yet created):

```text
artifacts/test-evidence/{phase}/{commit-sha}/
├── manifest.json          # OS, Docker, Node/Python, Pi, model aliases
├── commands.txt           # exact command, exit code, timestamp
├── junit.xml              # machine-readable statuses
├── run-traces/            # redacted Pi event envelopes
├── screenshots/           # browser end-to-end
├── security/              # negative exploit attempts
└── REVIEW.md              # spec compliance and quality verdict
```

Never upload private task files or API keys to public PR artifacts. CI links should point to scrubbed evidence only. Every PASS is bound to a commit/image digest; relevant code change invalidates stale evidence.

## 3. Command contract (to be created by P0A-T01)

```bash
make setup
make check
make test-unit
make test-contract
make test-integration
make test-e2e
make test-security
make docs-check
make compose-up
make compose-down        # must not erase volumes by default
```

These are **planned commands**, not currently verified scripts. P0A-T01 must create make targets and a genuine test harness. Model-dependent paid smoke tests must be opt-in and never run on a timer by default.

## 4. Phase evidence matrix

| Phase | Positive oracle | Essential negative oracle | Real dependency |
|---|---|---|---|
| P0A | Web bootstrap and actual model completion | bootstrap race, bad key, SSRF, secret redaction | PostgreSQL, Docker, real provider |
| P0B | Pi reads authorized Workspace and verifies file | path escape, cancel, crash, SSE replay | pinned Pi SDK, filesystem, actual LLM |
| P0C | local Skill installs and Pi loads pinned digest | disabled skill, digest mismatch, archive traversal | Registry, ResourceLoader, browser |
| P1 | edited Skill works on two different inputs | injection, data leakage, concurrent write conflict | executable sandbox, eval fixtures |
| P2 | org/public publish and unlist/revoke | cross-tenant leak, bypass review, revoked execution | multi-user OS isolation |
| P3 | CLI/MCP/upgrade and backup | server credentials, incompatible session, scale failure | mixed versions, real workload |

## 5. Hard blockers

- Unauthorized shell/network/file access, secret exposed in logs/Session, wrong-user file disclosure.
- Declaring SUCCEEDED without actual validator pass or a valid artifact.
- Retry duplicates external effects after an uncertain tool response.
- Tests disabled/skipped to create green CI.
- Compose starts UI but Pi Worker and database aren't ready; cannot reproduce actual model run.
- Public Skill listing available without reviewer policy or digest verification.

## 6. Issue lifecycle and gotchas

On defect: reproduce → preserve sanitized trace → write failing regression → identify root cause with controlled experiment → smallest fix → rerun impacted suites → document in `docs/gotchas.md` with symptom, environment, reason, test, commit and prevention. Broken design assumptions require ADR.

## 7. Reviewer evidence checklist

- [ ] Every spec AC maps to one or more real test names and fixture.
- [ ] Tests were RED on missing functionality; GREEN observed.
- [ ] Unit + integration + negative/security tests actually run as needed.
- [ ] Pi/real provider tested separately from mock.
- [ ] Token/API Key not in session/export/log/evidence.
- [ ] Database/files persistent, rollback/backup verified where relevant.
- [ ] Spec compliance review, then code quality and security review.
- [ ] No P0/P1 severity issue unresolved or silently waived.
- [ ] Every NOT RUN is explicit and explained.
- [ ] Gate PASS includes environment, SHA, date, approver and commands.

## 8. Gate decisions

State progression: NOT RUN → RUNNING → PASSED / FAILED / BLOCKED. Never equate a design document or command printed in a plan to observed PASS. Lower-risk capabilities may ship behind explicit off-by-default feature flags, but security-critical unverified capabilities remain disabled.
