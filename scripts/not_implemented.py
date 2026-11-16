"""Explicitly fail unimplemented developer commands (never manufacture green CI)."""
import sys

target = sys.argv[1] if len(sys.argv) > 1 else "unspecified"
print(
    f"NOT RUN: {target} is not implemented in the current phase; "
    "see docs/superpowers/IMPLEMENTATION_STATUS.md",
    file=sys.stderr,
)
raise SystemExit(2)
