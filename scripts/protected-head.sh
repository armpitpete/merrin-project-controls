#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 <40-character-commit-sha> [--remote <name>] [--skip-remote-check]" >&2
}

if [[ $# -lt 1 ]]; then
  usage
  exit 2
fi

expected="${1,,}"
shift
remote="origin"
skip_remote=false

if [[ ! "$expected" =~ ^[0-9a-f]{40}$ ]]; then
  echo "Expected commit must be a full 40-character SHA." >&2
  exit 2
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    --remote)
      [[ $# -ge 2 ]] || { usage; exit 2; }
      remote="$2"
      shift 2
      ;;
    --skip-remote-check)
      skip_remote=true
      shift
      ;;
    *)
      usage
      exit 2
      ;;
  esac
done

git rev-parse --git-dir >/dev/null

head_sha="$(git rev-parse HEAD | tr '[:upper:]' '[:lower:]')"
if [[ "$head_sha" != "$expected" ]]; then
  echo "HEAD mismatch. Expected $expected but found $head_sha." >&2
  exit 1
fi

status="$(git status --porcelain)"
if [[ -n "$status" ]]; then
  echo "Working tree is not clean:" >&2
  echo "$status" >&2
  exit 1
fi

branch="$(git branch --show-current)"
if [[ -z "$branch" ]]; then
  echo "Detached HEAD is not allowed for a protected action." >&2
  exit 1
fi

if [[ "$skip_remote" == false ]]; then
  git fetch --quiet "$remote" "$branch"
  remote_head="$(git rev-parse "$remote/$branch" | tr '[:upper:]' '[:lower:]')"
  if [[ "$remote_head" != "$expected" ]]; then
    echo "Remote head mismatch. Expected $expected but $remote/$branch is $remote_head." >&2
    exit 1
  fi
fi

echo "Protected head accepted: $expected on branch $branch."
