#!/usr/bin/env bash
set -euo pipefail

ROOT=/opt/data/private/wangwt/ParkAttackKE/datasets/apt_public/provcon
REPO="$ROOT/repository"
CLONE_TMP="$ROOT/repository.clone-partial"
STATE="$ROOT/state"
PROXY=socks5h://127.0.0.1:9998
SOURCE=https://github.com/NUS-Curiosity/provcon.git

mkdir -p "$ROOT/logs" "$STATE"

if [[ ! -d "$REPO/.git" ]]; then
  if [[ -e "$REPO" ]] && [[ -n "$(find "$REPO" -mindepth 1 -maxdepth 1 -print -quit)" ]]; then
    echo "Refusing to replace non-empty non-Git path: $REPO" >&2
    exit 2
  fi
  rmdir "$REPO" 2>/dev/null || true
  while [[ ! -d "$CLONE_TMP/.git" ]]; do
    rm -rf "$CLONE_TMP"
    if GIT_LFS_SKIP_SMUDGE=1 git \
      -c http.proxy="$PROXY" \
      -c http.version=HTTP/1.1 \
      clone "$SOURCE" "$CLONE_TMP"; then
      break
    fi
    date -u +"%FT%TZ Git clone failed; retrying in five minutes" >&2
    sleep 300
  done
  mv "$CLONE_TMP" "$REPO"
else
  git -C "$REPO" -c http.proxy="$PROXY" -c http.version=HTTP/1.1 fetch --all --tags --prune
  git -C "$REPO" checkout main
  git -C "$REPO" merge --ff-only origin/main
fi

git -C "$REPO" config http.proxy "$PROXY"
git -C "$REPO" config lfs.concurrenttransfers 4
git -C "$REPO" lfs install --local

while ! git -C "$REPO" lfs pull; do
  date -u +"%FT%TZ Git LFS pull failed; retrying in one hour" >&2
  sleep 3600
done

git -C "$REPO" lfs fsck
git -C "$REPO" fsck --full

commit=$(git -C "$REPO" rev-parse HEAD)
lfs_count=$(git -C "$REPO" lfs ls-files -n | wc -l)
tracked_count=$(git -C "$REPO" ls-files | wc -l)
bytes=$(du -sb "$REPO" | awk '{print $1}')
generated_at=$(date -u +"%FT%TZ")

cat > "$STATE/collection_state.json.tmp" <<EOF
{
  "source": "$SOURCE",
  "commit": "$commit",
  "generated_at": "$generated_at",
  "tracked_files": $tracked_count,
  "lfs_files": $lfs_count,
  "repository_bytes": $bytes,
  "git_fsck": "passed",
  "git_lfs_fsck": "passed",
  "complete": true
}
EOF
mv "$STATE/collection_state.json.tmp" "$STATE/collection_state.json"
