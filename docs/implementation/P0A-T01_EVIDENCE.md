# P0A-T01 — Foundation / CI evidence

> Real GitHub Actions runs on 2026-11-16. This is the first implementation task, **not a completed P0A phase**.

## Change

Established repo-level package manifests, pnpm workspace and empty-dependency lockfile, Python/Node unit test harness, Makefile targets with honest NOT RUN failures for unimplemented suites, .gitignore and Foundation CI. Web/API/Pi package manifests are **reserved scaffolding**, not runnable services.

## RED (observed)

- Commit: `40cb6ed98ca8456d93b384fae3a306c20e1abeb5`
- Workflow: https://github.com/1998x-stack/agent-console/actions/runs/43836229995
- Test: `python3 -m unittest discover -s tests/unit -p 'test_*.py' -v`
- Result: **FAILED** as expected, due to missing Makefile, package manifests, workspace, lockfile and stub-failure runner. Actual GitHub job log confirms these specific failures; this was not a missing test runner.

## GREEN (observed)

- Commit: `50d4641237d9b53960df378c967561b5a78d1334`
- Workflow: https://github.com/1998x-stack/agent-console/actions/runs/43836421797
- Results: **PASSED** Python layout tests, Node package tests, existing documentation validators.
- Commit: `13f4d2a80fb875b6ee276028d5e343c4a98089bb`
- Workflow: https://github.com/1998x-stack/agent-console/actions/runs/43836531603
- Results: **PASSED** frozen pnpm lockfile install, Python tests, Node tests, docs validation, `make check` aggregate.

## Verification scope and limitations

- Verified: repository structure, package manifests, frozen empty lockfile, executable Makefile/test targets, both documentation validators.
- **NOT RUN:** Next.js dev/build, FastAPI app, PostgreSQL, Docker Compose, Pi Agent SDK, real LLM, model BYOK, Web browser E2E, API security tests. They belong to later tasks.
- Review: self-check and GitHub CI executed; **independent Spec compliance / security review NOT RUN**. Task status remains IMPLEMENTED_UNVERIFIED until PR review is complete.
- Security: no actual user API Keys or project user data were introduced.
- Next: `P0A-T02` — real Docker Compose + Web/API liveness and dependency readiness. Add failures before implementation, then execute Docker on supported host/CI.

## Safeguard

The Makefile deliberately exits 2 with `NOT RUN` for `setup`, `test-contract`, `test-integration`, `test-e2e`, `test-security`, `compose-up` and `compose-down` while not implemented, to avoid false-green developer checks.
