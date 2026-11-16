# Agent Console — Master Product & Architecture Spec

> **DRAFT v0.5 | 2026-11-16 | Design only; all implementation checks NOT RUN.**

## Goal

Local-first, Docker Compose deployed Web Agent. Users configure their own provider, API Key, Base URL and Model ID in the browser; Pi executes real Office and Code tasks within an authorized logical `/{user-id}/workspace`; a built-in Skill Store lets every user discover, install, create and reuse Skills.

## Users & JTBD

- Developer: inspect source, diagnose failures, generate reviewable diff, run verifiable tests, retain control of Git.
- Office user: upload files, analyze, generate actually parsable artifacts, download, preserve originals.
- Creator: convert a successful process into a reusable Skill, evaluate, edit, release and share it.
- Local deployment admin: install, connect models, manage health, backups and security; no default access to other users' plaintext keys.

## Non-goals

P0 excludes remote SaaS control plane, centralized public publishing, payments, arbitrary shell access, unsandboxed extensions, production deployment and broad multi-Agent swarms. Office does not initially mean all file formats; Code does not initially mean full IDE.

## Architecture

```text
Browser :3000
 └─ Next.js UI: chat, workspace, models, skills
      └─ FastAPI: auth, vault, ACL, run state, event log, registry, audit
          ├─ PostgreSQL: business state / transactional queue
          ├─ data/users/{uuid}/workspace: durable files and artifacts
          ├─ Model Gateway → BYOK provider or local Ollama
          └─ Node Pi Worker: Pi AgentSession, SessionManager, ResourceLoader
               └─ constrained per-run file/tool executor and sandbox
```

Pi handles the agent loop; the host handles identity, authorization, policy, approvals, event truth, file persistence, cryptographic secrets, and public listing. Web/API must never have broad Docker socket access.

## Ten Cross-Phase Invariants

1. Every filesystem operation uses a server-authenticated principal and verified Workspace ID; user-provided URL/Prompt is not a mount directive.
2. `/{user-id}/workspace` is a logical Agent path mapped from immutable internal UUID to the persistent host directory.
3. Provider Key is encrypted at rest and redacted everywhere outside the vault; Pi should use a short-lived model proxy credential.
4. Pi SDK version/tag and actual package are pinned and smoke-tested; no homemade second Agent loop.
5. Run/Step/Event state in DB is authoritative; token text and Pi settled events are not a PASS claim.
6. Tool authorization happens before invocation; workspace mount and OS sandbox enforce least privilege independently.
7. Pi project Extensions, MCP results, Skill instruction text, retrieved files and model output are untrusted inputs.
8. Skill, immutable Release, Listing and workspace Installation remain separate; install != permission, unlist != revoke.
9. User data, sessions and installed releases persist across container restarts; backups include files, DB and encryption key custody.
10. No test is PASS without actual command/exit/fixture evidence; unavailable checks are NOT RUN.

## Interfaces and Ownership

| Contract | Owning service | Frozen rule | First phase |
|---|---|---|---|
| AuthContext / Admin bootstrap | API | initialization once; ACL server-side | P0A |
| ModelConnection / ModelAlias | API / Gateway | encrypted secret and provider capability probe | P0A |
| RunSpec | API → Pi Worker | server generated, signed or authenticated, pinned model/skills/tools | P0B |
| Conversation / PiSessionRef | API + Pi | one active writer per session, restore or explicit failure | P0B |
| RunEvent | API | ordered seq, replay via Last-Event-ID | P0B |
| Workspace/Artifact | API + runner | no traversal/symlink escape, validator required before success | P0B |
| SkillRelease/Installation | Registry + loader | immutable digest, only installed/authorized skills | P0C |
| SkillDraft / Evaluation | Creator | revision lock, sanitization and test evidence | P1 |
| Listing/Moderation | Public Registry | owner unlist vs admin revoke distinct | P2 |
| CLI / MCP / Operations | Extensibility | reuse authorization and event contracts | P3 |

## Golden User Journeys

- Docker cold start without model Key, local admin setup, add provider, model connection probe and real Pi stream.
- Office file upload → controlled read → new verified file → download and persistence after restart.
- Code fixture → bounded read → analysis → controlled diff/test in sandbox (unsafe write delayed until P1).
- Bundled offline Store → install release → Pi loader sees it in next run → disabled skill not invoked.
- Task-to-Skill → sanitize → edit draft → test different fixture → private release → install → optionally apply for public listing later.

## Security / Failure Behaviors

Bad Key, model endpoint unavailable, model with no Tool calls, cancel, SSE disconnect, Pi worker crash, directory traversal, disk full, conflicting write, malicious Skill package and revoked release each need a user-visible diagnostic and a measurable negative test. Prompt-based restrictions are not security boundaries.

P0 only advertises single-user trusted operations until true multi-user isolation and untrusted script sandbox testing have passed.

## Exit Conditions

See [PHASE_DEPENDENCIES_AND_GATES](../PHASE_DEPENDENCIES_AND_GATES.md) and [VERIFICATION_AND_TEST_STRATEGY](../VERIFICATION_AND_TEST_STRATEGY.md). P0 MVP requires a real Pi model run, verified Workspace artifacts, local Skill installation/invocation, restart persistence and negative security tests. A nice UI, mocks and documents alone do not satisfy these conditions.

## Reference Specs

- [Pi Integration](../../PI_AGENT_INTEGRATION.md)
- [Self-hosted Architecture](../../SELF_HOSTED_WORKSPACE_ARCHITECTURE.md)
- [Security Model](../../SECURITY_MODEL.md)
- [Skill Registry](../../SKILL_REGISTRY_SPEC.md)
- [Data Model](../../DATA_MODEL.md)
- [79-feature Matrix](../../functional-decomposition/13_FEATURE_MATRIX_AND_TRACEABILITY.md)
- [Superpowers](https://github.com/obra/superpowers)

## Open Decisions / Experiments

- Confirm actual Pi npm release, SDK API and license at coding time.
- Model proxy injection and supported local Base URL restrictions; do not claim success without experiment.
- Sandbox mechanism/host compatibility across Linux/macOS/Windows Docker.
- SessionManager persistence and disabling untrusted project extensions.
- PostgreSQL draft DDL vs actual applied migrations; implement additive reversible changes.
