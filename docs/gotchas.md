# Gotchas — Reproductions, Root Causes & Preventive Tests

> This log begins empty. Do not fabricate incidents or mark a theoretical risk as observed. Use the template below whenever a real failure occurs.

## Logging rules

For every real integration, Docker, Pi SDK, Model Gateway, data, Skill or security problem, record a minimal reproduction and the command/output that demonstrated it. Differentiate FIXED from UNVERIFIED and NOT RUN. Never paste API Keys, user documents or personal secrets into a public Git repository.

## Template (copy for every verified incident)

### GOTCHA-YYYYMMDD-NN — Short symptom

- **Status:** OPEN / REPRODUCED / FIXED_UNVERIFIED / VERIFIED
- **Severity:** P0 / P1 / P2
- **Phase & Task:** P0A-Txx
- **Environment:** OS, Docker/Node/Python/Pi versions, commit SHA
- **User-visible impact:** which workflow fails
- **Minimal reproduction:** exact safe commands/fixture
- **Expected vs actual:** output and exit code
- **Hypotheses considered / experiment:** why one root cause was selected
- **Root cause:** validated cause, or UNKNOWN if unresolved
- **Fix:** paths/commit (if implemented)
- **Regression test:** name and observed RED/GREEN commands
- **Rollback:** how to restore without losing user data
- **Prevention:** contract, CI, setup guide or guard to change
- **Evidence:** sanitized logs/artifact location (not secrets)

## Incidents

None documented yet. Implementation/runtime verification is NOT RUN.
