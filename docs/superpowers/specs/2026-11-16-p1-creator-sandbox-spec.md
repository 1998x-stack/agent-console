# P1 Design Spec — Private Skill Creator, Evaluations & Safe Write Sandbox

> DRAFT / NOT IMPLEMENTED. Prerequisite P0A+B+C Gate. Implementation: [P1 Plan](../plans/2026-11-16-p1-creator-sandbox-plan.md).

## Outcome

A normal user can save a successful Pi task as a draft Skill, inspect/edit `SKILL.md` and related assets, test on at least two distinct fixtures, publish an immutable private Release, install it, upgrade/rollback in their own Workspace, and review controlled file/code changes. All untrusted script execution remains constrained by a validated sandbox and capability grants.

## Users/Jobs

- Office user wants to turn a recurring CSV/Markdown workflow into a reproducible Skill without writing code.
- Developer wants to package test diagnosis instructions, track versions and compare changes.
- Skill creator must not have special platform-admin status.
- Same user must understand that import/install ≠ permission and public Listing is future scope.

## Client IA

`My Skills` with Drafts, Releases, Evaluations, Installations, Forks; `Skill Studio` with structured form + Markdown editor + file tree, Diff, Test Run, Publish Private, Update, Rollback; `Save as Skill` at Run result. Show source inputs selected for generalization and explicitly excluded sensitive files.

## Skill Draft / Release / Evaluation

- Draft: editable metadata, frontmatter, references, assets, scripts, expected_revision and owner.
- Release: immutable content digest, version, source provenance/license, manifest, validation evidence.
- Evaluation: positive/negative trigger fixtures, at least two task input variants, deterministic artifact/test oracle, passed/failed/blocked/not_run states.
- Installation: per-Workspace pin, allowed enabled state, selected/last-used release hash.
- Imported package: ZIP / .skill safe extraction with file count/decompression quotas, zip-slip/symlink protections, no extension autoactivation.
- Fork: new owner Skill ID, retain attribution and source version, avoid silently copying private data or violating license.

## AI-assisted Creation

After Run succeeds, user explicitly selects safe steps/files to include. Pi proposes concise description/when-to-use/procedure/input/output/verification. Run extraction under a trust boundary: prompts, file content, tool outputs and model summary are untrusted; secret scanner, PII filters and human review gate release. Keep source documents out of distributable package by default.

Bad generations: truncation, hallucinated commands, version mismatch, accidental hard-coded original input, stale reference paths. Display actionable diagnostics and keep Draft editable; never auto-release from one model answer.

## Code & Office Controlled Writes

- P0 readonly + new artifact flow remains.
- P1 applies changes via Git worktree or per-Run staging directory, not directly to the only working copy.
- `Review Changes` displays file list, diff, tests, origin Run, expected base version; explicit Apply with optimistic concurrency to prevent stomping edits.
- `bash` runs only inside real restricted sandbox (user namespace/mount/CPU/memory/network restrictions and no host docker.sock). A generic Docker container alone is not a proof of malicious multi-tenant isolation.
- External Git push, email send and production deploy are not part of P1; keep disabled by default.

## Security & Permissions

- Review file path, tool name, target and capabilities at execution time via Tool Gateway. Permission cannot be granted by Skill prompt or name.
- Installed Skill scripts are not Pi Extensions. Never permit arbitrary `.pi/extensions` or untrusted npm module as part of a Skill import.
- Encrypt and withhold provider Keys from shell/tool environments; policy separate for reading Workspace files versus network access.
- Prevent malicious ZIP, tar traversal, symlink, hardlink and script dependency supply chain.
- Creation tests run in isolated fixture with no real user credentials; use explicit resource budgets and kill timeouts.
- A user can always disable/uninstall their own Skill but cannot revoke other users' release rights by removing a draft.

## Error & Recovery Matrix

| Situation | Expected |
|---|---|
| Two browser edits to same Draft | 409 revision conflict with diff/reload |
| Generated Skill includes secret sentinel | block release, show remediation, no exported secret |
| Skill test fails/NOT RUN | no claim of verified quality; optional user can keep local Draft |
| Pi selected wrong Skill | negative fixture reveals misfire; user may explicitly choose Skill |
| Code base changed after diff | optimistic conflict; no silent overwrite |
| Bash timeout / crash | failed Run, isolated subprocess terminated, partial files retained only in staging |
| Private Release update | old installation unchanged until authorized update |
| Release referenced by historic Run | cannot delete blob while referenced; archive record instead |

## APIs & Data

- `POST /api/v1/skills`, `PATCH /api/v1/skills/{id}/draft` with revision, `POST /api/v1/skills/{id}/evaluate`, `POST /api/v1/skills/{id}/releases`, `POST /api/v1/skills/import`.
- `POST /api/v1/workspaces/{id}/installations` and `PATCH /api/v1/workspaces/{id}/installations/{install_id}` support pinned upgrade/disable.
- `POST /api/v1/runs/{id}/apply-changes` needs action hash, expected base revision and approval. Final OpenAPI signature must be reconciled with prior drafts.
- Schema: skill_drafts, evaluations, skill_releases, lineage, capability_grants, artifact_versions, action_approvals as needed; additive migrations and ACL.

## Acceptance

| AC | Oracle |
|---|---|
| P1-AC01 | Save-as-Skill creates sanitized Draft with correct user ownership |
| P1-AC02 | Studio edit/save with revision lock and conflict path works |
| P1-AC03 | positive/negative Skill trigger and two-input tasks produce real results |
| P1-AC04 | private Release hash and version immutable; existing installation does not drift |
| P1-AC05 | import malicious archive / extension denied before execution |
| P1-AC06 | sandbox prevents sensitive host read, secrets access and unauthorized egress |
| P1-AC07 | Code worktree Diff/test, explicit Apply, base-conflict tests pass |
| P1-AC08 | upgrade/rollback/disable next Run behavior and audit verified |
| P1-AC09 | Docker restart preserves Draft, Release, Eval and code changes without silently mutating originals |

## Open Decisions

Exact sandbox implementation must be chosen via PoC and threat model, including Linux/macOS/Windows Docker semantics. Semantic eval threshold should be set from a fixture dataset baseline, not guessed. No P1 publish claim without security negative tests.
