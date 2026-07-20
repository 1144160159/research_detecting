#!/usr/bin/env bash
set -euo pipefail

# The nine-archive JSON queue is now an extended/deferred selection.  The core
# baseline deliberately uses one official representation per run, including
# THEIA-6r and TRACE-1 binary archives, so an accidental invocation here would
# create duplicate representations and waste quota/bandwidth.
if [[ "${EACR_ENABLE_DARPA_TC_EXTENDED_JSON:-0}" != "1" ]]; then
  echo "DARPA TC E3 JSON extended queue is deferred; set EACR_ENABLE_DARPA_TC_EXTENDED_JSON=1 only after an explicit representation-policy decision." >&2
  exit 2
fi

ROOT=${1:-/opt/data/private/wangwt/ParkAttackKE/datasets/apt_public/darpa_tc}
RAW="$ROOT/raw/json"
MAN="$ROOT/manifests"
STATE="$ROOT/state"
LOG="$ROOT/logs"
mkdir -p "$RAW" "$MAN" "$STATE/files" "$LOG" "$ROOT/tmp" "$ROOT/quarantine"

QUEUE="$MAN/e3_json_queue.tsv"
cat > "$QUEUE" <<'EOF'
theia_5m	THEIA	5m	1zbgWJgF7F0fI6JhViqQZoo6AWdoV5YFK	ta1-theia-e3-official-5m.json.tar.gz	28549962
theia_3	THEIA	3	1dWJecuLXZMksKAPo8348Q6L5DiccsS1u	ta1-theia-e3-official-3.json.tar.gz	38217897
cadets_2	CADETS	2	1EycO23tEvZVnN3VxOHZ7gdbSCwqEZTI1	ta1-cadets-e3-official-2.json.tar.gz	358244121
cadets_official	CADETS	official	1AcWrYiBmgAqp7DizclKJYYJJBQbnDMfb	ta1-cadets-e3-official.json.tar.gz	585737522
cadets_1	CADETS	1	1XLCEhf5DR8xw3S-Fimcj32IKnfzHFPJW	ta1-cadets-e3-official-1.json.tar.gz	949955569
theia_1r	THEIA	1r	10cecNtR3VsHfV0N-gNEeoVeB89kCnse5	ta1-theia-e3-official-1r.json.tar.gz	1167693020
trace_1	TRACE	1	1GG1aUnPjjzzdbxznVTN8X6oVfA-K4oIV	ta1-trace-e3-official-1.json.tar.gz	1281892428
theia_6r	THEIA	6r	1Kadc6CUTb4opVSDE4x6RFFnEy0P1cRp0	ta1-theia-e3-official-6r.json.tar.gz	1546028723
trace_official	TRACE	official	1sfIbavsUFwmB-irSGY1TZZ0Sq1dZqF9G	ta1-trace-e3-official.json.tar.gz	37072393089
EOF

update_aggregate() {
  python3 - "$ROOT" "$QUEUE" <<'PY'
import datetime
import json
import os
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
queue = pathlib.Path(sys.argv[2])
rows = []
for line in queue.read_text().splitlines():
    label, corpus, run, gid, name, expected = line.split("\t")
    expected = int(expected)
    final_path = root / "raw" / "json" / name
    partial_path = pathlib.Path(str(final_path) + ".part")
    status_path = root / "state" / "files" / f"{label}.json"
    status = json.loads(status_path.read_text()) if status_path.exists() else {}
    if final_path.exists():
        present = final_path.stat().st_size
    elif partial_path.exists():
        present = partial_path.stat().st_size
    else:
        present = 0
    rows.append(
        {
            "label": label,
            "corpus": corpus,
            "run": run,
            "google_drive_id": gid,
            "filename": name,
            "expected_bytes": expected,
            "present_bytes": present,
            "complete": bool(status.get("complete", False)),
            "tar_integrity": status.get("tar_integrity", "pending"),
            "sha256": status.get("sha256"),
        }
    )

state = {
    "dataset": "DARPA Transparent Computing E3",
    "selection": "9 official JSON tar.gz archives only; duplicate BIN archives intentionally excluded",
    "source_folder_id": "1QlbUFWAGq3Hpl8wVdzOdIoZLFxkII4EK",
    "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "expected_file_count": len(rows),
    "expected_bytes": sum(row["expected_bytes"] for row in rows),
    "completed_file_count": sum(row["complete"] for row in rows),
    "completed_bytes": sum(row["expected_bytes"] for row in rows if row["complete"]),
    "downloaded_or_partial_bytes": sum(
        min(row["present_bytes"], row["expected_bytes"]) for row in rows
    ),
    "complete": all(row["complete"] for row in rows),
    "files": rows,
}
tmp_path = root / "state" / f"darpa_tc_e3_json_state.json.tmp.{os.getpid()}"
tmp_path.write_text(json.dumps(state, indent=2) + "\n")
tmp_path.replace(root / "state" / "darpa_tc_e3_json_state.json")
print(
    json.dumps(
        {
            key: state[key]
            for key in (
                "updated_at",
                "completed_file_count",
                "expected_file_count",
                "completed_bytes",
                "downloaded_or_partial_bytes",
                "expected_bytes",
                "complete",
            )
        }
    )
)
PY
}

mark_status() {
  local label=$1 corpus=$2 run=$3 gid=$4 name=$5 expected=$6 status=$7 sha=${8:-}
  python3 - "$STATE/files/$label.json" "$label" "$corpus" "$run" "$gid" "$name" "$expected" "$status" "$sha" <<'PY'
import datetime
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
status = sys.argv[8]
obj = {
    "label": sys.argv[2],
    "corpus": sys.argv[3],
    "run": sys.argv[4],
    "google_drive_id": sys.argv[5],
    "filename": sys.argv[6],
    "expected_bytes": int(sys.argv[7]),
    "status": status,
    "complete": status == "verified",
    "tar_integrity": (
        "pass" if status == "verified" else "fail" if status == "validation_failed" else "pending"
    ),
    "sha256": sys.argv[9] or None,
    "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
}
tmp_path = path.with_suffix(".json.tmp")
tmp_path.write_text(json.dumps(obj, indent=2) + "\n")
tmp_path.replace(path)
PY
}

download_one() {
  local label=$1 corpus=$2 run=$3 gid=$4 name=$5 expected=$6
  local dest="$RAW/$name" part="$RAW/$name.part" file_log="$LOG/$label.log"
  local url="https://drive.usercontent.google.com/download?id=$gid&export=download&confirm=t"
  {
    echo "[$(date -Is)] START label=$label id=$gid expected=$expected file=$name"
    if [[ -f "$dest" ]] && [[ "$(stat -c %s "$dest")" != "$expected" ]]; then
      mv "$dest" "$ROOT/quarantine/$name.wrong-size.$(date +%s)"
    fi
    if [[ -f "$dest" ]] && [[ "$(stat -c %s "$dest")" == "$expected" ]] && tar -tzf "$dest" >/dev/null; then
      sha=$(sha256sum "$dest" | awk '{print $1}')
      printf '%s  %s\n' "$sha" "$name" > "$MAN/$name.sha256"
      mark_status "$label" "$corpus" "$run" "$gid" "$name" "$expected" verified "$sha"
      update_aggregate
      echo "[$(date -Is)] VERIFIED_EXISTING sha256=$sha"
      return 0
    fi

    mark_status "$label" "$corpus" "$run" "$gid" "$name" "$expected" downloading
    update_aggregate
    attempt=0
    while true; do
      attempt=$((attempt + 1))
      present=0
      [[ -f "$part" ]] && present=$(stat -c %s "$part")
      if (( present > expected )); then
        mv "$part" "$ROOT/quarantine/$name.oversize.$(date +%s)"
        present=0
      fi
      echo "[$(date -Is)] DOWNLOAD attempt=$attempt present=$present expected=$expected"
      set +e
      curl --socks5-hostname 127.0.0.1:9999 --location --fail --show-error --continue-at - \
        --connect-timeout 30 --max-time 0 --retry 20 --retry-delay 15 --limit-rate 16M \
        --output "$part" "$url"
      rc=$?
      set -e
      present=0
      [[ -f "$part" ]] && present=$(stat -c %s "$part")
      echo "[$(date -Is)] CURL_EXIT rc=$rc present=$present expected=$expected"
      update_aggregate
      if [[ "$present" == "$expected" ]]; then
        break
      fi
      if [[ "$rc" == 0 && "$present" -lt "$expected" ]]; then
        echo "[$(date -Is)] SHORT_SUCCESS; retrying"
      fi
      sleep 20
    done

    mv "$part" "$dest"
    echo "[$(date -Is)] HASH_START"
    sha=$(sha256sum "$dest" | awk '{print $1}')
    printf '%s  %s\n' "$sha" "$name" > "$MAN/$name.sha256"
    echo "[$(date -Is)] TAR_TEST_START sha256=$sha"
    if tar -tzf "$dest" >/dev/null; then
      mark_status "$label" "$corpus" "$run" "$gid" "$name" "$expected" verified "$sha"
      update_aggregate
      echo "[$(date -Is)] VERIFIED sha256=$sha"
    else
      mark_status "$label" "$corpus" "$run" "$gid" "$name" "$expected" validation_failed "$sha"
      update_aggregate
      echo "[$(date -Is)] TAR_TEST_FAILED sha256=$sha"
      return 1
    fi
  } >>"$file_log" 2>&1
}

export ROOT RAW MAN STATE LOG QUEUE
export -f update_aggregate mark_status download_one

update_aggregate >>"$LOG/aggregate.log" 2>&1
(
  head -n 8 "$QUEUE" | while IFS=$'\t' read -r label corpus run gid name expected; do
    download_one "$label" "$corpus" "$run" "$gid" "$name" "$expected"
  done
) &
small_pid=$!
(
  tail -n 1 "$QUEUE" | while IFS=$'\t' read -r label corpus run gid name expected; do
    download_one "$label" "$corpus" "$run" "$gid" "$name" "$expected"
  done
) &
trace_pid=$!

wait "$small_pid"
wait "$trace_pid"
update_aggregate >>"$LOG/aggregate.log" 2>&1

python3 - "$ROOT" <<'PY'
import csv
import datetime
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
state = json.loads((root / "state" / "darpa_tc_e3_json_state.json").read_text())
if not state["complete"]:
    raise SystemExit("collection not complete after workers")
manifest = {
    "dataset": state["dataset"],
    "source_folder_id": state["source_folder_id"],
    "selection": state["selection"],
    "completed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "file_count": state["completed_file_count"],
    "total_bytes": state["completed_bytes"],
    "files": state["files"],
}
(root / "manifests" / "e3_json_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
with (root / "manifests" / "e3_json_manifest.tsv").open("w", newline="") as handle:
    fields = [
        "label",
        "corpus",
        "run",
        "google_drive_id",
        "filename",
        "expected_bytes",
        "sha256",
        "tar_integrity",
    ]
    writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", extrasaction="ignore")
    writer.writeheader()
    writer.writerows(manifest["files"])
(root / "state" / "COLLECTION.COMPLETE").write_text(manifest["completed_at"] + "\n")
print(
    json.dumps(
        {
            "complete": True,
            "file_count": manifest["file_count"],
            "total_bytes": manifest["total_bytes"],
            "manifest": str(root / "manifests" / "e3_json_manifest.json"),
        }
    )
)
PY
