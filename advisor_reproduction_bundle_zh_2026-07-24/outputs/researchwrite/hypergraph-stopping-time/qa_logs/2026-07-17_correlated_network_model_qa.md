# Correlated network model final QA

Execution date: 2026-07-18 (Asia/Hong_Kong)  
Scope: Task 9 final internal QA for the frozen correlated-network evidence package  
Current visual state: `PENDING_USER_CONFIRMATION` (the controller's local `file://` navigation was rejected by the browser security policy; no alternate browser path was used)

## Verification ledger

| Gate | Command/input | Expected | Observed | Status | Artifact/hash |
|---|---|---|---|---|---|
| Model invariants | `python -m unittest test_network_model -v`; frozen uniform two-triad kernel | conservation, zero drift, cross-block covariance and spectrum match the contract | 31/31 tests in 9.776 s; drift max `2.7755575615628914e-17`; cross-block Frobenius norm `0.59999999999999998`; positive eigenvalues `[0.30000000000000016, 0.49999999999999983, 0.5000000000000001, 1.5]` | PASS | `network_model.py` `96584fb75029c9ad5f5ce63cb26a19bc2d9a7154c54b2bc5afca624856704fb6` |
| Exact solver | `python network_phase_validation.py --output results/network`; N=1,2,3 | state counts `1 / 100 / 784`, reachability true, maximum residual `< 1e-10`, public survival finite/in-range/non-increasing | counts `1 / 100 / 784`; all reachable; maximum residual `6.8833827526759706e-15`; survival min/max `0 / 1`; exact range and monotonicity true | PASS | `network-exact.csv` `4a95eb7d31b4cfb6f397c721d5d7258520d468ed789b01b880e360c24d5984db` |
| MC vs exact | frozen seeds `2026071700+N`, 50,000 repetitions per N | N=1 exact; N=2,3 `abs(z) <= 2.58` | N=1 `z=0`; N=2 `z=-0.31266219051909072`; N=3 `z=-0.90398923077979931`; all gate fields true | PASS | `network-mc-exact-check.csv` `bf1053d1f838d82eee15735a57041f2e01010eb10c904e8f6e42924f3e2b6aa4` |
| Phase diagnostics | frozen alpha/N grid, amplitude `0.01`, 20,000 repetitions per cell | 12 complete descriptive rows; no fitted rate | 12 rows; alpha `{0.5,1.0,1.5}` x N `{10,20,40,80}`; frozen inputs retained | PASS | `network-phase-scaling.csv` `774b47efb90a4de16503ca3bb6684c582375449534817e639e528c053db23b43` |
| Paired proxy | frozen N `{10,20,40}`, 50,000 paired repetitions | 3 summaries, 243 survival rows, estimates and 95% CIs reported | N=10 `0.0411542`, CI `[0.034523628141084298,0.047784771858915692]`; N=20 `0.04696265`, CI `[0.040338539143959219,0.05358676085604077]`; N=40 `0.048223975`, CI `[0.041592497774724582,0.054855452225275422]`; 3 summaries and 243 survival rows | PASS | summary `08f7a5df559b9eee613fabff1f29375e9c40d50537e39668d19bbe370ff25dda`; survival `6b4d12ecb3d90ff2e631b65ddcb50e6e9db8fa9beb58108d1e865370a27b680a` |
| Proof completeness | proof packages 13/14 scanned for `TBD\|TODO\|待补\|显然\|不难\|全球首次` | no placeholders or prohibited shortcuts | 2 files, 0 matches | PASS | package 13 `95d664d40e050b75b58966c9d77e7e60f445d21120a5dfc892718a05b1a40fe3`; package 14 `18c50ca65057bb9d1b8c584e097b511c2a93c8b497c32bddfd0ccba499778801` |
| Authority consistency | README, authority 00–06, contract 12 and main progress audit; novelty/sign/equivalence polarity scan | no unsupported affirmative novelty, universal-sign or stop-event-equivalence claim | 10 files; 7 matches; all 7 classified as explicit negation/boundary; 0 unsupported affirmative claims | PASS | authority file list recorded below |
| Artifact integrity | reproducible read-only Python command recorded below; JSON/CSV/BibTeX/Markdown links/text controls plus manifest recomputation | zero parse/schema/duplicate/broken-link/control/hash errors | 21 JSON, 68 CSV, 5/5 network schemas, 36 BibTeX keys, 34 normalized DOIs, 30 Markdown files/112 relative links, 308 UTF-8 text files; every error count `0`; 6/6 manifest entries match | PASS | metadata `a1e3c4756deca22f459b4d4d1c29d05821f537c82872befbc693e20a3e093af8`; manifest `615a951f7457c11141a49a7ac7a24d73ec13a201e6fe06a1baebd0b6f6f8d30d` |
| HTML render | required renderer command plus strict UTF-8/DOM/link/MathJax assertions; visual inspection | structurally readable; visual inspection by controller or user | structure PASS: 50,493 bytes, 8,815 CJK characters, T16/T17/T18 and two title recommendations present, publication readiness false, 4 tables, 75 inline and 3 display math delimiters, 62 local and 26 external links, 0 broken local links; controller browser rejected the local `file://` URL and visual PASS is not claimed | PENDING USER CHECK | HTML `babf45d3ee1ae1455dfbf8d6c6d78d05fb296b87fdec6aca2902dc4a9b4f88cb` |

## Survival-defect root cause and TDD evidence

The defect is introduced before serialization. For N=3, the sparse transient matrix has a largest floating-point row sum of `1.0000000000000002`. Starting from the balanced state, sparse probability-mass propagation gives raw survival values `1.0`, `1.0000000000000002`, and `0.9180000000000004` at steps 1–3. `solve_exact` returned the same values, and the CSV JSON decoded byte-for-value to that in-memory result. Therefore serialization did not create the excursion.

The specific root-cause hypothesis, stated before editing, was that sparse floating-point probability accumulation creates a tolerance-scale excursion and that validation/normalization belongs at the public `solve_exact` return boundary. The minimal fix declares `SURVIVAL_NUMERICAL_TOLERANCE = 1e-12`, rejects non-finite values, rejects range or monotonicity violations beyond that tolerance, clips only tolerance-scale range excursions, and applies a cumulative non-increase. Raw transition propagation, the Poisson solution, exact means, residuals, state counts and reachability are unchanged. Because serialized evidence semantics changed, the pipeline version was bumped from `1` to `2`; the frozen configuration hash and input hash remain unchanged.

Red/green chronology:

1. RED: `python -m unittest test_network_model.ExactNetworkTests.test_exact_survival_obeys_public_probability_invariants -v` failed 1/1 in 0.112 s at the exact `[0,1]` assertion for N=3.
2. GREEN: the same selector passed 1/1 in 0.111 s after the public-boundary fix. The test also verifies finite/range/monotonicity invariants and material non-finite, out-of-range and increasing sequences raising `ValueError`.
3. Network regression: `python -m unittest test_network_model -v` passed 31/31 in 9.776 s.
4. Complete regression: the implementer run passed 42/42 in 19.270 s; a fresh controller rerun of the identical selector passed 42/42 in 18.208 s.
5. Formal-review RED: after adding `[0.5, 0.5+0.75e-12, 0.5+1.5e-12]`, the focused selector failed 1/1 in 0.116 s because the cumulative material increase did not raise.
6. Formal-review minimal fix: monotonicity validation now compares every later value with the minimum of all preceding values, instead of checking only adjacent differences.
7. Formal-review GREEN: the same focused selector passed 1/1 in 0.113 s. It also confirms that a total increase no greater than `1e-12` remains an allowed tolerance-scale disturbance and is flattened.
8. Formal-review full regression: `python -m unittest test_hyperedge test_final_formula test_drift test_network_model -v` passed 42/42 in 18.348 s.

## Frozen evidence run

The frozen full pipeline was rerun after the formal-review GREEN so that provenance and the manifest correspond to the final validator implementation:

```powershell
python network_phase_validation.py --output results/network
Get-FileHash -Algorithm SHA256 results/network/* | Sort-Object Path
```

Observed reviewer-fix pipeline summary: `gates=PASS rows=264 runtime=65.398s`. No seed, grid, repetition count, amplitude, confidence multiplier, exact gate or stop-event semantic was changed. The stop-event string remains exactly `first balance coordinate equal to zero`. The canonical configuration SHA-256 remains `9336ec1d3de052b3e361081ed776643aa7703c2c9faed617f8ca9fd9670694a6`; the canonical input SHA-256 remains `972cf7f2abd485b9b9d5a0da1f8279e20f4b839d7d9e21d089f857665ad17b8f`. All five mathematical CSV hashes remained unchanged; only runtime-bearing metadata and the dependent manifest changed.

### Generated artifact SHA-256 values

| Artifact | SHA-256 |
|---|---|
| `results/network/network-correlated-vs-proxy.csv` | `08f7a5df559b9eee613fabff1f29375e9c40d50537e39668d19bbe370ff25dda` |
| `results/network/network-exact.csv` | `4a95eb7d31b4cfb6f397c721d5d7258520d468ed789b01b880e360c24d5984db` |
| `results/network/network-mc-exact-check.csv` | `bf1053d1f838d82eee15735a57041f2e01010eb10c904e8f6e42924f3e2b6aa4` |
| `results/network/network-phase-scaling.csv` | `774b47efb90a4de16503ca3bb6684c582375449534817e639e528c053db23b43` |
| `results/network/network-run-metadata.json` | `a1e3c4756deca22f459b4d4d1c29d05821f537c82872befbc693e20a3e093af8` |
| `results/network/network-survival-curves.csv` | `6b4d12ecb3d90ff2e631b65ddcb50e6e9db8fa9beb58108d1e865370a27b680a` |
| `results/network/SHA256SUMS.txt` | `615a951f7457c11141a49a7ac7a24d73ec13a201e6fe06a1baebd0b6f6f8d30d` |
| `项目进展审计_超图支付通道停止时间_2026-07-17.html` | `babf45d3ee1ae1455dfbf8d6c6d78d05fb296b87fdec6aca2902dc4a9b4f88cb` |

## Read-only artifact and authority audit

The final read-only audit was invoked with the complete copy-pasteable PowerShell command recorded below. It strictly parsed every workspace JSON and CSV, enforced the five canonical network schemas, normalized DOI strings before duplicate checking, resolved every relative Markdown link under the research project, decoded text artifacts as strict UTF-8, rejected forbidden controls, scanned proof packages 13/14, classified authority matches by section and explicit negation, recomputed all network gates, and independently checked all six manifest entries.

Authority files scanned were `README.md`, authority documents `00`–`06`, contract `12`, and the current exported progress audit. The first classifier run produced two false positives because it did not carry the `Forbidden claims` section heading and did not recognize `不在……前使用` as a negation. No source was edited. After correcting those audit rules, the complete audit was rerun from the beginning. The final post-review invocation returned `READ_ONLY_AUDIT_PASS errors=0` with 21 JSON files, 68 CSV files, 30 project Markdown files/112 relative links, 308 strict UTF-8 text files, 0 proof matches, 7/7 negated authority matches, the exact counts `1/100/784`, maximum residual `6.8833827526759706e-15`, z-scores `0/-0.3126621905190907/-0.9039892307797993`, row counts `12/3/243`, and 0 manifest mismatches.

### Reproducible read-only audit command

Run this command from the workspace root. It writes no file:

~~~~powershell
@'
import csv
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

import numpy as np

ROOT = Path.cwd().resolve()
PROJECT = ROOT / "outputs" / "researchwrite" / "hypergraph-stopping-time"
NETWORK = ROOT / "results" / "network"
errors = []


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


json_paths = sorted(ROOT.rglob("*.json"))
json_values = {}
for path in json_paths:
    try:
        json_values[path] = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"JSON_PARSE:{path.relative_to(ROOT)}:{exc}")

required_headers = {
    "network-exact.csv": ["scale", "state_count", "exact_mean", "max_abs_residual", "all_states_reach_boundary", "survival_horizon", "survival_json"],
    "network-mc-exact-check.csv": ["scale", "repetitions", "seed", "exact_mean", "mc_mean", "mc_sd", "standard_error", "ci_low", "ci_high", "z_score", "gate_pass"],
    "network-phase-scaling.csv": ["alpha", "scale", "repetitions", "seed", "mean", "sd", "q10", "q50", "q90", "normalizer", "normalized_mean", "normalized_q10", "normalized_q50", "normalized_q90"],
    "network-correlated-vs-proxy.csv": ["scale", "repetitions", "seed", "correlated_mean", "proxy_mean", "normalized_correlated_mean", "normalized_proxy_mean", "mean_difference", "paired_standard_error", "ci_low", "ci_high", "sign", "q10_difference", "q50_difference", "q90_difference", "nonidentical_fraction"],
    "network-survival-curves.csv": ["scale", "normalized_time", "correlated_survival", "proxy_survival", "difference"],
}
csv_paths = sorted(ROOT.rglob("*.csv"))
csv_rows = {}
for path in csv_paths:
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle, strict=True)
            rows = list(reader)
            if reader.fieldnames is None:
                errors.append(f"CSV_HEADER:{path.relative_to(ROOT)}:missing")
            if any(None in row for row in rows):
                errors.append(f"CSV_WIDTH:{path.relative_to(ROOT)}")
            csv_rows[path] = (reader.fieldnames, rows)
    except Exception as exc:
        errors.append(f"CSV_PARSE:{path.relative_to(ROOT)}:{exc}")
for name, expected in required_headers.items():
    observed = csv_rows.get(NETWORK / name, (None,))[0]
    if observed != expected:
        errors.append(f"NETWORK_SCHEMA:{name}:{observed!r}")

bib_path = PROJECT / "sources" / "references.bib"
bib = bib_path.read_text(encoding="utf-8")
keys = re.findall(r"(?im)^\s*@[a-z]+\s*\{\s*([^,\s]+)", bib)
dois = re.findall(r"(?im)^\s*doi\s*=\s*[\{\"]([^}\"]+)", bib)
normalized_dois = []
for value in dois:
    value = value.strip().lower()
    value = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", value).rstrip(" ./")
    normalized_dois.append(value)
duplicate_keys = sorted({key for key in keys if keys.count(key) > 1})
duplicate_dois = sorted({doi for doi in normalized_dois if normalized_dois.count(doi) > 1})
if duplicate_keys:
    errors.append(f"BIB_DUP_KEYS:{duplicate_keys}")
if duplicate_dois:
    errors.append(f"BIB_DUP_DOIS:{duplicate_dois}")


def markdown_targets(text):
    text = re.sub(r"~~~~[\s\S]*?~~~~", "", text)
    text = re.sub(r"```[\s\S]*?```", "", text)
    start = 0
    while True:
        marker = text.find("](", start)
        if marker < 0:
            return
        cursor = marker + 2
        depth = 1
        if cursor < len(text) and text[cursor] == "<":
            end = text.find(">", cursor + 1)
            if end >= 0:
                yield text[cursor + 1:end]
                start = end + 1
                continue
        end = cursor
        while end < len(text) and depth:
            char = text[end]
            if char == "\\":
                end += 2
                continue
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    yield text[cursor:end].split()[0]
                    start = end + 1
                    break
            end += 1
        else:
            return


markdown_paths = sorted(PROJECT.rglob("*.md"))
relative_links = 0
broken_links = []
for md_path in markdown_paths:
    for target in markdown_targets(md_path.read_text(encoding="utf-8")):
        target = target.strip()
        if not target or target.startswith("#"):
            continue
        parsed = urlsplit(target)
        if parsed.scheme or target.startswith("/") or re.match(r"^[A-Za-z]:[\\/]", target):
            continue
        relative_links += 1
        if not (md_path.parent / unquote(parsed.path)).resolve().exists():
            broken_links.append(f"{md_path.relative_to(ROOT)} -> {target}")
if broken_links:
    errors.extend(f"BROKEN_LINK:{value}" for value in broken_links)

text_suffixes = {".bib", ".csv", ".css", ".diff", ".html", ".json", ".md", ".mjs", ".py", ".svg", ".txt"}
text_paths = sorted(path for path in ROOT.rglob("*") if path.is_file() and (path.suffix.lower() in text_suffixes or path.name == ".gitignore"))
utf8_errors = []
invalid_controls = []
for path in text_paths:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        utf8_errors.append(f"{path.relative_to(ROOT)}:{exc}")
        continue
    bad = [(index, ord(char)) for index, char in enumerate(text) if ord(char) < 32 and char not in "\n\r\t"]
    if bad:
        invalid_controls.append(f"{path.relative_to(ROOT)}:{bad[:3]}")
if utf8_errors:
    errors.extend(f"UTF8:{value}" for value in utf8_errors)
if invalid_controls:
    errors.extend(f"CONTROL:{value}" for value in invalid_controls)

proof_terms = (
    "TBD",
    "TODO",
    "\u5f85\u8865",
    "\u663e\u7136",
    "\u4e0d\u96be",
    "\u5168\u7403\u9996\u6b21",
)
proof_paths = [PROJECT / "13_correlated_network_proof_package.md", PROJECT / "14_correlated_network_external_review_packet.md"]
proof_matches = []
for path in proof_paths:
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if any(term.lower() in line.lower() for term in proof_terms):
            proof_matches.append(f"{path.name}:{number}:{line.strip()}")
if proof_matches:
    errors.extend(f"PROOF_PLACEHOLDER:{value}" for value in proof_matches)

authority_paths = [ROOT / "README.md"] + sorted(PROJECT.glob("0[0-6]_*.md"))
authority_paths += [PROJECT / "12_correlated_hypergraph_network_model_and_theorem_contract.md"]
authority_paths += list((PROJECT / "exports").glob("*.md"))
claim_pattern = re.compile(
    "\u9996\u6b21\u63d0\u51fa\u8d85\u56fe|\u9996\u6b21\u7814\u7a76.*depletion|"
    "\u5168\u7403\u9996\u6b21|\u76f8\u5173\u8bef\u5dee\u603b\u662f|"
    "\u7b49\u540c\u4e8e\u7f51\u7edc\u65ad\u8fde|\u7b49\u540c\u4e8e\u652f\u4ed8\u5931\u8d25|"
    "\u7b49\u540c\u4e8e\u901a\u9053\u5173\u95ed|\u7b49\u4ef7\u4e8e\u7f51\u7edc\u65ad\u8fde|"
    "\u7b49\u4ef7\u4e8e\u652f\u4ed8\u5931\u8d25|\u7b49\u4ef7\u4e8e\u901a\u9053\u5173\u95ed",
    re.I,
)
negation_terms = (
    "\u4e0d\u7b49\u4e8e", "\u4e0d\u7b49\u540c", "\u4e0d\u6210\u7acb", "\u6ca1\u6709\u5efa\u7acb",
    "\u4e0d\u80fd", "\u4e0d\u5f97", "\u4e0d\u53ef", "\u4e0d\u5728", "\u7981\u6b62", "\u5e76\u975e",
    "\u4e0d\u662f", "\u4e0d\u628a", "\u672a", "\u65e0\u666e\u904d", "forbidden", "not equivalent", "no universal",
)
authority_matches = []
unsupported_claims = []
for path in authority_paths:
    lines = path.read_text(encoding="utf-8").splitlines()
    current_heading = ""
    for index, line in enumerate(lines):
        if line.startswith("#"):
            current_heading = line
        if not claim_pattern.search(line):
            continue
        context = "\n".join(lines[max(0, index - 1):index + 1]).lower() + "\n" + current_heading.lower()
        classification = "NEGATED_BOUNDARY" if any(term.lower() in context for term in negation_terms) else "UNSUPPORTED_AFFIRMATIVE"
        item = f"{path.relative_to(ROOT)}:{index + 1}:{classification}:{line.strip()}"
        authority_matches.append(item)
        if classification == "UNSUPPORTED_AFFIRMATIVE":
            unsupported_claims.append(item)
if unsupported_claims:
    errors.extend(f"AUTHORITY_CLAIM:{value}" for value in unsupported_claims)

exact_rows = csv_rows[NETWORK / "network-exact.csv"][1]
mc_rows = csv_rows[NETWORK / "network-mc-exact-check.csv"][1]
phase_rows = csv_rows[NETWORK / "network-phase-scaling.csv"][1]
proxy_rows = csv_rows[NETWORK / "network-correlated-vs-proxy.csv"][1]
survival_rows = csv_rows[NETWORK / "network-survival-curves.csv"][1]
metadata = json_values[NETWORK / "network-run-metadata.json"]
state_counts = [int(row["state_count"]) for row in exact_rows]
max_residual = max(float(row["max_abs_residual"]) for row in exact_rows)
if state_counts != [1, 100, 784]:
    errors.append(f"EXACT_COUNTS:{state_counts}")
if not max_residual < 1e-10:
    errors.append(f"EXACT_RESIDUAL:{max_residual}")
if any(row["all_states_reach_boundary"] != "True" for row in exact_rows):
    errors.append("EXACT_REACHABILITY")
for row in exact_rows:
    values = np.asarray(json.loads(row["survival_json"]), dtype=np.float64)
    if not np.isfinite(values).all():
        errors.append(f"EXACT_SURVIVAL_FINITE:N={row['scale']}")
    if np.any((values < 0.0) | (values > 1.0)):
        errors.append(f"EXACT_SURVIVAL_RANGE:N={row['scale']}")
    if np.any(np.diff(values) > 0.0):
        errors.append(f"EXACT_SURVIVAL_MONOTONIC:N={row['scale']}")
mc_z = {int(row["scale"]): float(row["z_score"]) for row in mc_rows}
if float(mc_rows[0]["mc_mean"]) != float(mc_rows[0]["exact_mean"]):
    errors.append("MC_N1_NOT_EXACT")
if any(abs(mc_z[scale]) > 2.58 for scale in (2, 3)):
    errors.append(f"MC_Z:{mc_z}")
if any(row["gate_pass"] != "True" for row in mc_rows):
    errors.append("MC_GATE_FIELD")
if (len(phase_rows), len(proxy_rows), len(survival_rows)) != (12, 3, 243):
    errors.append("ROW_COUNTS")
config = metadata["config"]
if config["master_seed"] != 20260717:
    errors.append("MASTER_SEED")
if config["phase_grid"] != {"0.5": [10, 20, 40, 80], "1.0": [10, 20, 40, 80], "1.5": [10, 20, 40, 80]}:
    errors.append("PHASE_GRID")
if config["repetitions"]["selected"] != {"mc": 50000, "paired": 50000, "phase": 20000}:
    errors.append("REPETITIONS")
if config["amplitude"] != 0.01 or config["confidence"] != {"ci_multiplier": 1.959963984540054, "mc_z_limit": 2.58}:
    errors.append("FROZEN_CONSTANTS")
if metadata["stop_event"] != "first balance coordinate equal to zero":
    errors.append("STOP_EVENT")
if metadata["pipeline_version"] != "2" or not metadata["all_gates_pass"]:
    errors.append("METADATA_GATE")
if metadata["config_sha256"] != "9336ec1d3de052b3e361081ed776643aa7703c2c9faed617f8ca9fd9670694a6":
    errors.append("CONFIG_HASH_CHANGED")
if metadata["input_sha256"] != "972cf7f2abd485b9b9d5a0da1f8279e20f4b839d7d9e21d089f857665ad17b8f":
    errors.append("INPUT_HASH_CHANGED")
if len(metadata["files"]) != 7 or not all(Path(path).exists() for path in metadata["files"]):
    errors.append("METADATA_FILES")
manifest = {}
for line in (NETWORK / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
    digest, name = line.split("  ", 1)
    manifest[name] = digest
if sorted(manifest) != sorted(list(required_headers) + ["network-run-metadata.json"]):
    errors.append(f"MANIFEST_NAMES:{sorted(manifest)}")
manifest_mismatches = [name for name, digest in manifest.items() if sha256(NETWORK / name) != digest]
if manifest_mismatches:
    errors.append(f"MANIFEST_HASH:{manifest_mismatches}")

print(f"JSON_AUDIT files={len(json_paths)} errors={sum(error.startswith('JSON_PARSE') for error in errors)}")
print(f"CSV_AUDIT files={len(csv_paths)} parse_errors={sum(error.startswith('CSV_PARSE') for error in errors)} schema_errors={sum(error.startswith('NETWORK_SCHEMA') for error in errors)}")
print(f"BIB_AUDIT keys={len(keys)} dois={len(normalized_dois)} duplicate_keys={len(duplicate_keys)} duplicate_dois={len(duplicate_dois)}")
print(f"LINK_AUDIT markdown_files={len(markdown_paths)} relative_links={relative_links} broken={len(broken_links)}")
print(f"TEXT_AUDIT files={len(text_paths)} utf8_errors={len(utf8_errors)} invalid_controls={len(invalid_controls)}")
print("PROOF_TERMS_DECODED=" + "|".join(proof_terms[2:]))
print(f"PROOF_AUDIT files=2 matches={len(proof_matches)}")
print(f"AUTHORITY_AUDIT files={len(authority_paths)} matches={len(authority_matches)} negated={len(authority_matches)-len(unsupported_claims)} unsupported_affirmative={len(unsupported_claims)}")
print(f"EVIDENCE_AUDIT state_counts={state_counts} max_residual={max_residual:.17g} z={mc_z} rows={len(phase_rows)}/{len(proxy_rows)}/{len(survival_rows)} manifest_mismatches={len(manifest_mismatches)}")
if errors:
    print(f"READ_ONLY_AUDIT_FAIL errors={len(errors)}")
    for error in errors:
        print(error)
    raise SystemExit(1)
print("READ_ONLY_AUDIT_PASS errors=0")
'@ | python -B -
~~~~

Reproducibility-record fix verification:

- The outer audit fence uses four tildes, so the internal `r"```[\s\S]*?```"` literal cannot terminate it.
- The final tilde-fence block was extracted from this QA record and executed verbatim. It printed `PROOF_TERMS_DECODED=待补|显然|不难|全球首次`, `PROOF_AUDIT files=2 matches=0`, and `READ_ONLY_AUDIT_PASS errors=0`.
- Independent check: `rg -n "待补|显然|不难|全球首次" "outputs/researchwrite/hypergraph-stopping-time/13_correlated_network_proof_package.md" "outputs/researchwrite/hypergraph-stopping-time/14_correlated_network_external_review_packet.md"` returned the expected no-match exit status, recorded as `INDEPENDENT_RG_PROOF_SCAN_PASS matches=0`.
- The first execution after switching the outer fence to tildes exposed that the link scanner stripped only backtick fences and therefore misread two Python regex fragments as links. The recorded command was corrected to strip the outer tilde block first and ordinary backtick blocks second; the final execution below is the post-correction PASS evidence.

## Render and structural verification

The required command was attempted exactly:

```powershell
node render_research_html.mjs "outputs/researchwrite/hypergraph-stopping-time/exports/项目进展审计_超图支付通道停止时间_2026-07-17.md" "项目进展审计_超图支付通道停止时间_2026-07-17.html" "超图支付通道停止时间研究：项目进展审计与论文推进路线"
```

The PATH-selected Node v12.18.3 could not parse the renderer's top-level `await`. The installed Node v24.15.0 could parse it but initially could not resolve `marked`. Without modifying the renderer or dependencies, the successful recovery explicitly used Node v24.15.0 and the existing Codex runtime module directory:

```powershell
$env:NODE_PATH='C:\Users\jiate\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\node_modules'
& 'C:\Program Files\nodejs\node.exe' render_research_html.mjs "outputs/researchwrite/hypergraph-stopping-time/exports/项目进展审计_超图支付通道停止时间_2026-07-17.md" "项目进展审计_超图支付通道停止时间_2026-07-17.html" "超图支付通道停止时间研究：项目进展审计与论文推进路线"
```

The structural audit passed. It did not infer visual correctness from strings. On 2026-07-18 the controller attempted to open the rendered local HTML in the in-app browser, but browser security policy rejected navigation to the `file://` URL and explicitly prohibited alternate-browser workarounds. No workaround was attempted. Visual inspection therefore remains `PENDING_USER_CONFIRMATION`; this blocks a visual-PASS claim and HTML delivery as fully inspected, but it does not invalidate the mathematical or numerical gates.

## Failure policy

- A deterministic invariant, exact residual or manifest failure blocks authority promotion.
- A fixed-seed MC failure stops the run for diagnosis; only a predeclared repetition sensitivity may follow, and seed shopping is prohibited.
- A proof gap downgrades only the affected T17 subregime.
- A literature conflict narrows the contribution statement before manuscript drafting.
- A render or link failure blocks HTML delivery without invalidating mathematical results.

No failure policy was triggered by the final evidence or audit gates. The two audit-classifier false positives and the Node runtime/module-resolution failures were diagnosed as tooling issues and corrected without changing scientific inputs or authority sources.

## Retained publication blockers

- External packet 14 remains unsigned; independent probability review is incomplete.
- The broader MathSciNet/zbMATH/Scopus/WoS novelty search remains incomplete.
- T18 cross-topology robustness remains incomplete, and no universal sign theorem is claimed.
- Manuscript assembly and target-journal formatting remain incomplete.
- Barnett (1964) full-text transition kernel remains unverified; no full text or attachment was downloaded in this task.
- Existing v4 reproduction-chain, real-traffic mapping, positive-drift second-order error and robust-interval debts remain.

Publication status: not submission-ready
