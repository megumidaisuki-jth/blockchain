"""Generate the immutable-file SHA-256 manifest for the advisor bundle."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "BUNDLE_SHA256SUMS.txt"
EXCLUDED_DIRS = {
    "__pycache__",
    ".pytest_cache",
    ".tmp",
    "reproduction_logs",
    "reproduced_results",
}
EXCLUDED_FILES = {MANIFEST.name}


def included(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    return (
        path.name not in EXCLUDED_FILES
        and not any(part in EXCLUDED_DIRS for part in relative.parts)
        and path.suffix.lower() not in {".pyc", ".pyo"}
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    files = sorted(
        (path for path in ROOT.rglob("*") if path.is_file() and included(path)),
        key=lambda path: path.relative_to(ROOT).as_posix(),
    )
    lines = [f"{sha256(path)}  {path.relative_to(ROOT).as_posix()}" for path in files]
    MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    total_bytes = sum(path.stat().st_size for path in files)
    print(f"WROTE {MANIFEST}")
    print(f"FILES {len(files)}")
    print(f"BYTES {total_bytes}")


if __name__ == "__main__":
    main()
