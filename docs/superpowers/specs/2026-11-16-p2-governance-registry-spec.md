# P2 Design Spec — Multi-user Isolation, Organization Skills & Public Registry Governance

> DRAFT / NOT IMPLEMENTED. P2 starts only after verified P1 and multi-user sandbox safety. Implementation: [P2 Plan](../plans/2026-11-16-p2-governance-registry-plan.md).

## Outcome

The same Web user can create, privately use, share to an authorized organization, request publication to a public Registry, unlist their own public listing, and maintain/version their Skills. Team administrators manage membership and policy; public moderators review and take security actions. A user cannot access other users' files, model Keys, sessions or private Releases, including via executable Tools.

## Three Surfaces

1. **User Client / Creator Studio**: normal user discovers, creates, forks, edits, tests, submits for sharing, maintains personal Listing, may voluntarily unlist.
2. **Organization Admin**: membership, allowed models/tools, org Skill policies, team approval, shared asset access. Org admin not automatically privileged to recover personal Key or unrelated private files.
3. **Public Registry Governance**: public review queue, security scan, malware reports, quarantine, release revoke and appeal/audit. Not a Creator replacement.

## Critical Security Prerequisite

P0 single-user local mode must evolve to actual multi-user isolation: independent session store, per-user mount, credentials, process identity, network policy, queue fairness, and cross-workspace ACL. Even if the API rejects user B files, the Pi Worker/Skill shell must not have access to host volume containing user B. If this cannot be proven by red-team negative tests, **keep multi-user arbitrary execution disabled**, though non-executing private share UX may be separately assessed.

## Publication & Distribution State

- Private Release is immutable.
- Organization Listing requires Org policy and optional approval; org-admin can suspend team distribution, without deleting creator's private source.
- Public submission always references a validated Release and declared permissions, license/provenance, scan/eval evidence.
- Queue states: DRAFT → SUBMITTED → CHECKING → NEEDS_REVIEW → APPROVED/REJECTED → PUBLISHED (formal state definitions finalized in migrations).
- Owner Unlist stops new public installs, preserves already installed version rights according to policy.
- Moderator Revoke / Quarantine blocks affected content digest from execution (including existing installation) and requires notification/audit/appeal.
- Updating a published Skill creates new Release and new review decision when policy requires; cannot edit approved blob in place.

## Data & API

Organizations, members/roles, organization policies, moderation_cases, listing_submissions, review_decisions, revoke_events, notifications, audit_events. Every action records actor, scope, source release hash, effective time, reason, policy version.

Public Registry may be separate optional service; local private store must continue functioning offline. Do not assume centralized online service is required at startup. Registry install URL requires version hash validation, domain policy, cache, install ACL.

## Abuse/Failure Paths

| Risk | Required behavior |
|---|---|
| Creator submits malicious manifest | automated scan/quarantine + review evidence |
| Race: approve then source Release updated | impossible because Release immutable; decision binds digest |
| Owner unlists while user installing | DB transaction rules define linearizable result; no ghost installation |
| Moderator revokes digest in running task | policy checks before next tool call; stop affected future invocations; current effects audited |
| Member leaves org | future read/share/Run rights revoked, installed org skills policy re-evaluated |
| Public Registry offline | cached authorized Release may continue by policy, no unverified new install |
| User guesses another's private Skill UUID | no metadata leak |
| User B manipulates Pi Session path / SSE ID | no session/event cross-access |
| Public license source missing | reject or flag for human review; do not silently erase attribution |

## Acceptance

| AC | Oracle |
|---|---|
| P2-AC01 | multi-user filesystem/OS/runner negative tests cannot cross user boundary |
| P2-AC02 | org membership/role policy gates sharing and model/Skill access |
| P2-AC03 | public submission scans and approved digest is installed; unapproved absent |
| P2-AC04 | owner Unlist stops new installs but retains earlier installation semantics |
| P2-AC05 | security Revoke blocks affected installed digest and records reason, not only hides listing |
| P2-AC06 | report/appeal/review audit trail immutable and properly authorized |
| P2-AC07 | offline local store continues despite remote registry failure |
| P2-AC08 | concurrent publish/install/revoke transactions remain consistent |
| P2-AC09 | approval and moderator operations cannot be forged by ordinary Client |

## Non-goals

Paid marketplace, rating manipulation detection at scale, complex revenue share and universal public licensing enforcement are P3/independent legal/product projects. Public moderation should not exist as a fake local “admin app” before remote Registry deployment is genuinely justified.
