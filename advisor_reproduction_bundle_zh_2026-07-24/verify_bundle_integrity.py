"""Verify bundle-level and result-directory SHA-256 manifests."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_manifest(manifest: Path, base: Path) -> tuple[int, list[str]]:
    checked = 0
    errors: list[str] = []
    for line_number, raw_line in enumerate(manifest.read_text(encoding="utf-8-sig").splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(maxsplit=1)
        if len(parts) != 2 or len(parts[0]) != 64:
            errors.append(f"{manifest}: malformed line {line_number}")
            continue
        expected, relative_text = parts
        relative_text = relative_text.lstrip("* ").replace("\\", "/")
        target = base / Path(relative_text)
        checked += 1
        if not target.is_file():
            errors.append(f"{manifest}: missing {relative_text}")
        elif sha256(target).lower() != expected.lower():
            errors.append(f"{manifest}: hash mismatch {relative_text}")
    return checked, errors


def main() -> int:
    parser = argparse.ArgumentParser(description="校验导师复现包及权威结果目录的 SHA-256。")
    parser.add_argument(
        "--bundle-only", action="store_true", help="只检查包级清单，不检查各结果目录清单"
    )
    args = parser.parse_args()

    manifests = [ROOT / "BUNDLE_SHA256SUMS.txt"]
    if not args.bundle_only:
        manifests.extend(sorted((ROOT / "results").rglob("SHA256SUMS")))
        manifests.extend(sorted((ROOT / "results").rglob("SHA256SUMS.txt")))

    errors: list[str] = []
    checked_files = 0
    checked_manifests = 0
    for manifest in manifests:
        if not manifest.is_file():
            errors.append(f"missing manifest: {manifest}")
            continue
        base = ROOT if manifest.name == "BUNDLE_SHA256SUMS.txt" else manifest.parent
        count, current_errors = verify_manifest(manifest, base)
        checked_files += count
        checked_manifests += 1
        errors.extend(current_errors)

    print(f"MANIFESTS_CHECKED {checked_manifests}")
    print(f"FILE_HASHES_CHECKED {checked_files}")
    print(f"ERRORS {len(errors)}")
    for error in errors:
        print(f"ERROR {error}")
    if errors:
        print("INTEGRITY FAIL")
        return 1
    print("INTEGRITY PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
