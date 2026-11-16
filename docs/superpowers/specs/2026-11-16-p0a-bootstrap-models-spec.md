# P0A Design Spec — Local Bootstrap, Auth & Model BYOK

> DRAFT / NOT IMPLEMENTED. Parent: [Master Spec](2026-11-16-master-product-architecture.md). Execution: [P0A Plan](../plans/2026-11-16-p0a-bootstrap-models-plan.md).

## Goal & Exit Outcome

On a fresh Linux/Docker host, `docker compose up -d --build` starts a local Web UI at `http://localhost:3000` without a model Key; the user creates a first admin account once, adds a model connection (protocol/Base URL/API Key/Model ID), tests reachability and real inference, and chooses it as default. Persisted data survives restart. This phase **does not claim Pi Agent file execution yet**.

## Target User, UI & Happy Path

1. Browser opens Setup; no default user/password; state shows storage ready and model unconfigured.
2. An instance-unique initialization capability or equivalent secure one-time flow allows the first owner to create a local admin. Race between concurrent tabs yields exactly one success, the second 409.
3. Authenticated user opens Models, adds OpenAI-compatible or configured local Ollama endpoint; API Key never returned.
4. Save Connection (status UNVERIFIED), run Test: URL/Host/TLS/auth/model ID minimal completion; tool-calling ability separately marked TESTED/UNTESTED/UNSUPPORTED.
5. Choose available ModelAlias as workspace default; logout/login and Docker restart preserve setting.

## Non-goals & Assumptions

No public signup, billing, OAuth enterprise SSO, multi-user sharing or model provider automatic fallback. The user owns a local Docker instance; local LAN model access is an explicit deployment-owner exception. No silent automatic model downloads. Phase test must use real provider with user-approved credential or explicitly report NOT RUN.

## Proposed Architecture

```text
web:/setup,/login,/settings/models
      → api:/setup,/auth,/model-connections
         → postgres: users/admin_bootstrap/model_connections/model_aliases/probe_results
         → Vault: envelope-encrypted secrets using persistent APP_ENCRYPTION_KEY
         → Model Gateway: policy-validated outbound connector and completion probe
```

First-run capability cannot be a public, unauthenticated endpoint permanently enabled after owner creation. Use an initialization token generated at deployment and displayed only to local operator, or an equivalent single-use local-console mechanism; choose in ADR before implementation.

## Core Contracts

| Interface | Request / Output | Guarantee |
|---|---|---|
| `GET /api/v1/setup/status` | state enum and readiness, no token | no credentials returned |
| `POST /api/v1/setup/initialize-admin` | setup credential + username/password | only first authenticated bootstrap is committed |
| `POST /api/v1/auth/session` | credentials | HttpOnly SameSite cookie, CSRF controls |
| `POST /api/v1/model-connections` | name/protocol/base_url/secret optional | secret encrypted, response redacted |
| `POST /api/v1/model-connections/{id}/test` | model id optional | probe step results and observed_at |
| `GET /api/v1/models` | authorized alias list | never exposes raw provider Key |

Input limits: model URL length / scheme, label length, model ID length, timeouts and allowed address ranges; implement schema validation. A test response containing remote error body must be scrubbed before returning to browser. Service remains ready when no model configured.

## Security & Failure Stories

- Two simultaneous setup requests: DB transaction/unique constraint ensures one owner, other 409, no partially initialized account.
- LAN SSRF dilemma: admin may allow Host/LAN provider; non-admin may not freely target internal URLs; cloud metadata IP / redirects denied; DNS change revalidated at actual request.
- Wrong Key: clear 401/403 diagnostic; secret masked in API body, logs, Pi data.
- Local Docker network: `localhost` inside container isn't host; recommend `host.docker.internal` with Linux gateway mapping, and show connection failure with diagnostics.
- Model list absent: allow manual Model ID; successful `/models` response not enough without inference.
- Invalid or rotated encryption key: instance must fail safely, not silently erase or overwrite encrypted provider configuration.
- Unknown provider tool capability: mark UNKNOWN; do not allow File Agent feature to claim availability.
- Startup with DB inaccessible: setup UI reports degraded readiness and does not accept writes; process liveness distinguished from dependency readiness.

## Data & State

Use PostgreSQL migrations for users, local setup state, model_connections, model_aliases and optional probe history; proposed base DDL in [Data Model](../../DATA_MODEL.md). Never store decrypted Key in SQL text or logs. Test state enum `UNVERIFIED/HEALTHY/UNHEALTHY` and time; provider capability probe `PASSED/FAILED/UNKNOWN` separately.

Persistence: a fixed `APP_ENCRYPTION_KEY` stored outside database, backed up separately. `docker compose down` must not remove persistent volumes. Backup/restore test is mandatory before durable release.

## Acceptance & Traceability

| AC ID | Test | Oracle |
|---|---|---|
| P0A-AC01 | Compose fresh-volume browser smoke | UI loads without provider credentials |
| P0A-AC02 | simultaneous admin bootstrap | exactly one success; no weak default password |
| P0A-AC03 | Web save, list, logout/login | configured Key not recoverable by API |
| P0A-AC04 | wrong Key / unreachable URL / missing model | distinct diagnostics and failure status |
| P0A-AC05 | real model completion + tool probe | actual generation observed; unknown tool marked unknown |
| P0A-AC06 | restart data store | admin/model alias/encrypted connection persist |
| P0A-AC07 | endpoint SSRF negative | forbidden addresses and redirects fail |
| P0A-AC08 | log/trace inspection | sentinel secret absent |

## Design Decisions / Experiments

- Pin Node/Python/PostgreSQL and dependency versions via lockfiles; do not invent “latest stable” in docs.
- Decide auth library + CSRF for Next.js ↔ FastAPI cross-origin (prefer same-origin proxy).
- Decide persistent encryption key file ownership and backup instructions.
- Proxy local endpoint exception vs broad SSRF restrictions; test Docker Linux/macOS.
- Provider probing must be explicit to avoid surprise user token costs.

## P0A Exit

AC01–AC08 have real evidence, unit/contract/integration checks pass, no P0 security finding, and broken scenarios are documented. Pi is explicitly NOT IMPLEMENTED in P0A. Any missing real provider check blocks a claim of complete model compatibility.
