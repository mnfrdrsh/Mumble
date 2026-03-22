"""
Packaged launcher for the modern Qt Mumble application.
"""

from __future__ import annotations


def main() -> int:
    """Run the canonical Qt entrypoint."""
    try:
        from ui_redesign.main_app import main as run_app
    except ImportError as exc:
        print(f"Error importing modern UI: {exc}")
        print("Make sure PyQt5 is installed: pip install PyQt5")
        return 1

    try:
        run_app()
    except SystemExit as exc:
        code = exc.code
        if code is None:
            return 0
        if isinstance(code, int):
            return code
        return 1
    except Exception as exc:
        print(f"Error running modern Mumble: {exc}")
        return 1

    return 0
