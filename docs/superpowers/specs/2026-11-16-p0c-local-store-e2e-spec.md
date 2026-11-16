# P0C Design Spec — Bundled Skill Store, Installation, Pi Loader & Full Docker E2E

> DRAFT / NOT IMPLEMENTED. Requires P0A/P0B passing. Plan: [P0C](../plans/2026-11-16-p0c-local-store-e2e-plan.md).

## Goal

Web sidebar opens an offline usable Skill Store with a small set of trusted bundled skills. A user can inspect source/permissions/version, install an immutable Release to their Workspace, enable/disable it and see Pi use it on the next real Run. Fresh Docker E2E covers the whole journey. **Public publishing and user-generated arbitrary code are not P0C scope.**

## Client UX

- Store entry is visible beside Workspace/Chat without visiting Admin.
- Explore has categories (Office/Code/General), search, source and trust/permission disclosure. Zero results, offline, corrupt bundled catalog have explicit states.
- Skill Detail displays description, source, author, release version/content hash, required tools, trust, example input/output and install button.
- Installed shows installed version, enabled, compatibility, last use, disable, uninstall. Changing status affects **new Runs**; ongoing Run still uses pinned snapshot.
- No “community downloads” metric unless real source data exists. Built-in skills must be useful, not decorative cards.

## Domain Model

`Skill(id, slug, owner/source)` + `SkillRelease(id, version, manifest, content_sha256)` + `Installation(workspace_id, release_id, enabled)`. Listing can be represented as builtin/private catalog listing but not conflate with installation. Release files are content-addressed read-only. Pi gets only enabled, authorized Release IDs via ResourceLoader.

## Store/Agent Integration

```text
bundled manifest (verified) → catalog indexed locally → user reviews Skill
→ installation transaction pins digest
→ API snapshots authorized skills for a new run
→ Pi ResourceLoader injects allowed Skill names/descriptions
→ Pi optionally reads SKILL.md when matched
→ Tool Gateway checks independent actual tool privileges
→ RunEvent records used release digest
```

Loading an installed Skill does not imply safe execution of scripts. Unknown Pi Extensions and imported Skill scripts remain disabled. Test both explicit Skill selection and safe automatic selection; if trigger precision insufficient, use explicit invocation for P0.

## Trusted Seed Content

Provide two minimal, verifiable Skills:
1. `summarize-project`: instructs Pi to read only allowed Markdown/README and produce traceable summary.
2. `csv-insights`: uses guarded file parsing and summary with deterministic test oracle, does not execute user shell.
A third `ci-diagnosis-readonly` is optional if bounded and tested. Seed bundles must use valid `SKILL.md` metadata and be tracked with digests.

## Error/Recovery

- Manifest missing/unsupported fields, digest mismatch, zip traversal → reject without installing.
- User double-click install / duplicate request → idempotent single Installation.
- Attempt to install another user's private Release → 403/404 with no metadata leakage.
- Installed skill later disabled while Run active → current Run immutable, next Run excludes it.
- Bundled catalog changes on upgrade → old Installation points to prior cached immutable content; never silently overwrite old Release.
- Registry blob missing/corrupt → runtime refuses to load with explicit diagnostic, does not silently swap version.
- Agent invokes tool beyond grant → Tool Gateway denies, not “Skill trusted therefore allowed”.
- Offline environment → Store still loads bundled content; remote catalog not contacted without opt-in.

## Acceptance

| AC | Expected evidence |
|---|---|
| P0C-AC01 | Completely offline initial web Store shows real seeded Skill metadata |
| P0C-AC02 | install/uninstall/enable/disable persists after Docker restart |
| P0C-AC03 | Pi ResourceLoader sees only enabled/authorized pinned releases |
| P0C-AC04 | real Pi Run uses installed Skill on matching fixture; disabled skill absent next run |
| P0C-AC05 | wrong digest/zip traversal/unknown extension/import denied |
| P0C-AC06 | full browser journey from empty Docker volumes to artifact+Skill invocation passes |
| P0C-AC07 | health/backup restore of DB+files+sessions+release cache passes minimal exercise |
| P0C-AC08 | no default shell/network permission escalation from Skill install |

## Non-goals / Gate

No public Listing, moderation, revenue, remote Registry, creator UI or enterprise sharing. P0 is complete only when P0A+B+C passing with real Pi/real provider, end-to-end artifacts and security negative tests; no mock-only claims.
