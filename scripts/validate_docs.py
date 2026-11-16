#!/usr/bin/env python3
"""Simple markdown framework self-check. Not a product test suite."""
from pathlib import Path
import re
root = Path(__file__).resolve().parents[1]
docs = root / 'docs'
expected = [
    'PRODUCT_PRD.md',
    'AGENT_RUNTIME_ARCHITECTURE.md',
    'SKILL_REGISTRY_SPEC.md',
    'SECURITY_MODEL.md',
    'DATA_MODEL.md',
    'MVP_EXECUTION_PLAN.md',
    'SELF_HOSTED_WORKSPACE_ARCHITECTURE.md',
    'PI_AGENT_INTEGRATION.md',
    'functional-decomposition/README.md',
    'functional-decomposition/01_USERS_AND_JOURNEYS.md',
    'functional-decomposition/02_CLIENT_IA_AND_INTERACTIONS.md',
    'functional-decomposition/03_MODEL_ONBOARDING.md',
    'functional-decomposition/04_WORKSPACE_AND_ARTIFACTS.md',
    'functional-decomposition/05_PI_RUNTIME_AND_SESSIONS.md',
    'functional-decomposition/06_SKILL_CREATOR_AND_STORE.md',
    'functional-decomposition/07_ROLES_ADMIN_AND_SECURITY.md',
    'functional-decomposition/08_DATA_API_CONTRACTS.md',
    'functional-decomposition/09_DOCKER_DEPLOY_AND_OPERATIONS.md',
    'functional-decomposition/10_QUALITY_SECURITY_EVALS.md',
    'functional-decomposition/11_ROADMAP_AND_BACKLOG.md',
    'functional-decomposition/12_DECISIONS_AND_RISKS.md',
    'functional-decomposition/13_FEATURE_MATRIX_AND_TRACEABILITY.md',
    'functional-decomposition/14_OPENWEBUI_PI_REFERENCE_MAPPING.md',
    'superpowers/README.md',
    'superpowers/WORKFLOW_AND_HANDOFF.md',
    'superpowers/PHASE_DEPENDENCIES_AND_GATES.md',
    'superpowers/VERIFICATION_AND_TEST_STRATEGY.md',
    'superpowers/AGENT_EXECUTION_PLAYBOOK.md',
    'superpowers/IMPLEMENTATION_STATUS.md',
    'superpowers/specs/2026-11-16-master-product-architecture.md',
    'superpowers/plans/2026-11-16-master-execution-plan.md',
    'superpowers/specs/2026-11-16-p0a-bootstrap-models-spec.md',
    'superpowers/plans/2026-11-16-p0a-bootstrap-models-plan.md',
    'superpowers/specs/2026-11-16-p0b-pi-workspace-spec.md',
    'superpowers/plans/2026-11-16-p0b-pi-workspace-plan.md',
    'superpowers/specs/2026-11-16-p0c-local-store-e2e-spec.md',
    'superpowers/plans/2026-11-16-p0c-local-store-e2e-plan.md',
    'superpowers/specs/2026-11-16-p1-creator-sandbox-spec.md',
    'superpowers/plans/2026-11-16-p1-creator-sandbox-plan.md',
    'superpowers/specs/2026-11-16-p2-governance-registry-spec.md',
    'superpowers/plans/2026-11-16-p2-governance-registry-plan.md',
    'superpowers/specs/2026-11-16-p3-ecosystem-spec.md',
    'superpowers/plans/2026-11-16-p3-ecosystem-plan.md',
]
errors=[]
for name in expected:
    path=docs/name
    if not path.is_file():
        errors.append(f'Missing {name}')
        continue
    text=path.read_text(encoding='utf-8')
    if not text.startswith('# '):
        errors.append(f'{name}: missing H1')
    if sum(line.startswith('```') for line in text.splitlines())%2:
        errors.append(f'{name}: unbalanced code fences')
    for link in re.findall(r'\]\(([^)]+\.md)\)',text):
        if link.startswith(('http://', 'https://')) or link.startswith('#'):
            continue
        if not (path.parent/link).is_file():
            errors.append(f'{name}: broken relative link {link}')
print(f'Checked {len(expected)} expected document files.')
if errors:
    for e in errors: print('FAIL', e)
    raise SystemExit(1)
print('PASS: basic document structure and cross-links (not implementation tests)')
