"""Validate the curated inventory and run all manuscript experiment tests."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest


EXPERIMENT_DIR = Path(__file__).resolve().parent
INVENTORY_PATH = EXPERIMENT_DIR / "inventory.json"


def validate_inventory() -> None:
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    declared_sources = set(inventory["source_files"])
    declared_tests = set(inventory["test_files"])

    actual_sources = {
        path.name
        for path in EXPERIMENT_DIR.glob("*.py")
        if path.name != Path(__file__).name
    }
    actual_tests = {
        path.name for path in (EXPERIMENT_DIR / "tests").glob("test_*.py")
    }

    if actual_sources != declared_sources:
        missing = sorted(declared_sources - actual_sources)
        extra = sorted(actual_sources - declared_sources)
        raise RuntimeError(f"source inventory mismatch: missing={missing}, extra={extra}")
    if actual_tests != declared_tests:
        missing = sorted(declared_tests - actual_tests)
        extra = sorted(actual_tests - declared_tests)
        raise RuntimeError(f"test inventory mismatch: missing={missing}, extra={extra}")


def main() -> int:
    validate_inventory()
    sys.path.insert(0, str(EXPERIMENT_DIR))
    suite = unittest.defaultTestLoader.discover(
        start_dir=str(EXPERIMENT_DIR / "tests"), pattern="test_*.py"
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
