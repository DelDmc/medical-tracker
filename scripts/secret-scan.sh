#!/usr/bin/env bash
# Repository secret scan (TC-SEC-004-01, ADS-SEC-004-01).
#
# Scans the tracked files of the current tree and the full committed history with
# detect-secrets. Exits non-zero when anything is found that is not recorded in
# .secrets.baseline as an audited false positive (is_secret: false).
#
# Usage: bash scripts/secret-scan.sh   (detect-secrets must be on PATH; it is installed
#        by backend/requirements-dev.txt into the backend virtualenv)
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"
baseline=".secrets.baseline"

if ! command -v detect-secrets >/dev/null 2>&1; then
    echo "secret-scan: detect-secrets is not on PATH (activate backend/.venv)." >&2
    exit 2
fi
if [[ ! -f "$baseline" ]]; then
    echo "secret-scan: $baseline is missing." >&2
    exit 2
fi

workdir="$(mktemp -d)"
trap 'rm -rf "$workdir"' EXIT
mkdir "$workdir/history"

# 1. The current tree: every tracked file, as it is on disk.
detect-secrets scan --exclude-files '^\.secrets\.baseline$' >"$workdir/tree.json"

# 2. The committed history: every version of every file reachable from any ref,
#    written out under its original path so detect-secrets applies the same
#    filename-based filters (lock files, for example) as it does to the tree.
python3 - "$workdir/history" <<'PY'
import os
import subprocess
import sys

destination = sys.argv[1]
listing = subprocess.run(
    ["git", "rev-list", "--all", "--objects"], check=True, capture_output=True, text=True
).stdout.splitlines()
paths = {}
for line in listing:
    sha, _, path = line.partition(" ")
    if path and not path.endswith(".secrets.baseline"):
        paths.setdefault(sha, path)
checks = subprocess.run(
    ["git", "cat-file", "--batch-check=%(objecttype) %(objectname)"],
    input="\n".join(paths),
    check=True,
    capture_output=True,
    text=True,
).stdout.splitlines()
for check in checks:
    kind, sha = check.split()
    if kind != "blob":
        continue
    target = os.path.join(destination, sha, paths[sha])
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "wb") as handle:
        handle.write(subprocess.run(["git", "cat-file", "blob", sha], check=True,
                                    capture_output=True).stdout)
PY
(cd "$workdir/history" && detect-secrets scan --all-files . >"$workdir/history.json")

python3 - "$baseline" "$workdir/tree.json" "$workdir/history.json" <<'PY'
import json
import sys

baseline_path, tree_path, history_path = sys.argv[1:]
with open(baseline_path) as handle:
    baseline = json.load(handle)

allowed = set()
failures = []
for filename, results in baseline["results"].items():
    for result in results:
        if result.get("is_secret") is False:
            allowed.add(result["hashed_secret"])
        else:
            failures.append(
                f"{baseline_path}: unaudited or confirmed secret recorded for "
                f"{filename}:{result['line_number']} ({result['type']})"
            )

for label, path in (("tree", tree_path), ("history", history_path)):
    with open(path) as handle:
        scan = json.load(handle)
    for filename, results in scan["results"].items():
        for result in results:
            if result["hashed_secret"] not in allowed:
                failures.append(
                    f"{label}: {filename}:{result['line_number']} ({result['type']})"
                )

if failures:
    print("secret-scan: FAILED", file=sys.stderr)
    for failure in failures:
        print(f"  {failure}", file=sys.stderr)
    sys.exit(1)
print("secret-scan: no secrets found in the tree or the committed history.")
PY
