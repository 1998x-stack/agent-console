# Agent Console — Repository Agent Instructions

This repo is currently **documentation-first**. Read docs/superpowers/README.md and docs/superpowers/IMPLEMENTATION_STATUS.md first, then the master spec, current phase spec and matching implementation plan. Do not treat a design doc as proof of code running.

## Mandatory workflow

1. Work in an isolated feature branch/worktree; never modify main directly.
2. Choose exactly one Task ID from the active phase plan.
3. Read prerequisite interfaces and the task's expected tests before editing.
4. Write a failing regression/test first; execute it and confirm correct RED.
5. Implement minimum GREEN, then refactor and rerun neighboring suites.
6. Verify by actual commands, logs, exit codes and test fixture Oracle.
7. Commit one reviewable change and update docs/gotchas.md when discovering reproducible problems.
8. Request spec-compliance and code/security review; do not invent reviews that did not happen.
9. Do not merge/deploy/delete volumes/publish without user authorization.

## Architectural invariants

- Web-first Docker self-hosted; user BYOK Provider/API Key/Base URL/Model ID.
- Pi SDK Agent Engine runs in a separate Node worker; API owns authorization, secrets and RunEvent state.
- The logical /{user-id}/workspace path is derived from authenticated internal UUID and safe filesystem mapping; never trust arbitrary cwd or host-path user inputs.
- Pi Tool selection is not OS security. Unknown project extensions, scripts and arbitrary shell execution are disabled until sandbox/security gate passes.
- Skill, Release, Listing and Installation are distinct; installing a Skill grants no tool rights.
- No fake green CI: mark tests PASSED, FAILED, NOT RUN or BLOCKED with real evidence.

## References

- docs/superpowers/WORKFLOW_AND_HANDOFF.md
- docs/superpowers/VERIFICATION_AND_TEST_STRATEGY.md
- docs/superpowers/AGENT_EXECUTION_PLAYBOOK.md
- docs/SECURITY_MODEL.md
- docs/PI_AGENT_INTEGRATION.md

Agent instructions here do not authorize running commands or external actions automatically; follow the user's permissions and runtime security policy.
