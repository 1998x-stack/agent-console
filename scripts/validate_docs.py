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
