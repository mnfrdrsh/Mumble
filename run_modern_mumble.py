#!/usr/bin/env python3
"""
Canonical launcher for the modern Qt Mumble application.
"""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_ROOT = PROJECT_ROOT / "src"


def _ensure_src_on_path() -> None:
    """Make the local src tree importable when launched from the repo checkout."""
    src_path = str(SRC_ROOT)
    if src_path not in sys.path:
        sys.path.insert(0, src_path)


def main() -> int:
    """Run the canonical Qt entrypoint."""
    _ensure_src_on_path()
    from modern_mumble_launcher import main as run_launcher

    return run_launcher()


if __name__ == "__main__":
    raise SystemExit(main())
