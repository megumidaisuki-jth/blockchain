"""One-command validation entry point for the advisor reproduction bundle."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
QUICK_MODULES = [
    "test_drift",
    "test_final_formula",
    "test_hyperedge",
    "test_gaussian_discrete_bridge",
]


def run_and_tee(command: list[str], log_path: Path) -> int:
    with log_path.open("w", encoding="utf-8", newline="\n") as log:
        process = subprocess.Popen(
            command,
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        assert process.stdout is not None
        for line in process.stdout:
            print(line, end="")
            log.write(line)
        return process.wait()


def main() -> int:
    parser = argparse.ArgumentParser(description="运行超图支付通道停止时间公式复现验证。")
    parser.add_argument("--mode", choices=("quick", "full"), default="quick")
    args = parser.parse_args()

    log_dir = ROOT / "reproduction_logs"
    log_dir.mkdir(exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    test_log = log_dir / f"{args.mode}_tests_{timestamp}.txt"
    integrity_log = log_dir / f"{args.mode}_integrity_{timestamp}.txt"

    if args.mode == "quick":
        test_command = [sys.executable, "-m", "unittest", "-v", *QUICK_MODULES]
    else:
        test_command = [sys.executable, "-m", "unittest", "discover", "-v", "-s", ".", "-p", "test_*.py"]

    print(f"BUNDLE_ROOT {ROOT}")
    print(f"MODE {args.mode}")
    print("STEP 1/2 TESTS")
    test_exit = run_and_tee(test_command, test_log)

    print("STEP 2/2 INTEGRITY")
    integrity_exit = run_and_tee(
        [sys.executable, str(ROOT / "verify_bundle_integrity.py")], integrity_log
    )

    summary = {
        "timestamp_utc": timestamp,
        "mode": args.mode,
        "python": sys.version,
        "test_exit_code": test_exit,
        "integrity_exit_code": integrity_exit,
        "status": "PASS" if test_exit == 0 and integrity_exit == 0 else "FAIL",
        "test_log": test_log.name,
        "integrity_log": integrity_log.name,
    }
    summary_path = log_dir / f"{args.mode}_summary_{timestamp}.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"SUMMARY {summary_path}")
    print(f"REPRODUCTION {summary['status']}")
    return 0 if summary["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
