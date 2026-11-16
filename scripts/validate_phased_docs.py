#!/usr/bin/env python3
"""Validate phased specs/plans. This does NOT run product code/tests."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "docs" / "superpowers"
PHASES = {
  "p0a": ("bootstrap-models", 9, 8),
  "p0b": ("pi-workspace", 10, 9),
  "p0c": ("local-store-e2e", 8, 8),
  "p1": ("creator-sandbox", 9, 9),
  "p2": ("governance-registry", 8, 9),
  "p3": ("ecosystem", 6, 6),
}
required = [
 BASE / "README.md",
 BASE / "WORKFLOW_AND_HANDOFF.md",
 BASE / "PHASE_DEPENDENCIES_AND_GATES.md",
 BASE / "VERIFICATION_AND_TEST_STRATEGY.md",
 BASE / "AGENT_EXECUTION_PLAYBOOK.md",
 BASE / "IMPLEMENTATION_STATUS.md",
 BASE / "specs/2026-11-16-master-product-architecture.md",
 BASE / "plans/2026-11-16-master-execution-plan.md",
 ROOT / "AGENTS.md",
 ROOT / "docs/gotchas.md",
 ROOT / "docs/adr/README.md",
]
for phase, (slug, _, _) in PHASES.items():
 required.append(BASE / "specs" / f"2026-11-16-{phase}-{slug}-spec.md")
 required.append(BASE / "plans" / f"2026-11-16-{phase}-{slug}-plan.md")

errors = []
links = 0
for path in required:
 if not path.is_file():
  errors.append(f"Missing {path}")
  continue
 s = path.read_text(encoding="utf8")
 if not s.startswith("# "): errors.append(f"{path}: missing H1")
 if "\u00a7" in s: errors.append(f"{path}: unresolved placeholder")
 if sum(line.startswith("```") for line in s.splitlines()) % 2:
  errors.append(f"{path}: unbalanced fenced code")
 for link in re.findall(r"\]\(([^)]+)\)", s):
  rel = link.split("#",1)[0].split("?",1)[0]
  if not rel or rel.startswith(("http:", "https:", "mailto:", "/")): continue
  if not rel.endswith(".md"): continue
  links += 1
  if not (path.parent / rel).is_file():
   errors.append(f"{path}: broken local link {rel}")
for phase, (slug, task_count, ac_count) in PHASES.items():
 prefix = phase.upper()
 spec = BASE / "specs" / f"2026-11-16-{phase}-{slug}-spec.md"
 plan = BASE / "plans" / f"2026-11-16-{phase}-{slug}-plan.md"
 if not spec.is_file() or not plan.is_file(): continue
 st = spec.read_text(encoding="utf8")
 pl = plan.read_text(encoding="utf8")
 for header in ("**Goal:**","**Architecture:**","**Spec:**","## Global Constraints","## Review Focus"):
  if header not in pl: errors.append(f"{phase}: missing {header}")
 task_ids = re.findall(rf"^## Task ({prefix}-T\d{{2}}):", pl, re.M)
 expected = [f"{prefix}-T{i:02d}" for i in range(1,task_count+1)]
 if task_ids != expected: errors.append(f"{phase}: task IDs {task_ids} != {expected}")
 for i in range(1,ac_count+1):
  ac = f"{prefix}-AC{i:02d}"
  if ac not in st: errors.append(f"{phase}: missing spec {ac}")
  if ac not in pl: errors.append(f"{phase}: missing plan coverage {ac}")
 for block in re.split(r"^## Task ",pl, flags=re.M)[1:]:
  task = re.match(r"([A-Z0-9]+-T\d{2}):", block)
  tid = task.group(1) if task else "unknown"
  for part in ("**Files:**","**Expected RED:**","**Expected GREEN:**","- [ ]"):
   if part not in block: errors.append(f"{tid}: missing {part}")
  if "**Test" not in block: errors.append(f"{tid}: missing test command")
  if "RED" not in block or "GREEN" not in block: errors.append(f"{tid}: no RED/GREEN steps")

if errors:
 print(f"FAIL: {len(errors)} errors")
 for e in errors: print(" -",e)
 sys.exit(1)
print(f"PASS: docs structure only, {len(required)} required files, {sum(p[1] for p in PHASES.values())} tasks, {links} links")
print("NOT RUN: Pi SDK, Docker, migrations, model E2E, sandbox security")
