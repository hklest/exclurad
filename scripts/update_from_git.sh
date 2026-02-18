#!/usr/bin/env bash
set -euo pipefail

# Update local checkout from a remote branch with safe defaults.
#
# Usage examples:
#   ./scripts/update_from_git.sh
#   ./scripts/update_from_git.sh --remote origin --branch main
#   ./scripts/update_from_git.sh --stash

REMOTE="origin"
BRANCH=""
DO_STASH=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --remote)
      REMOTE="$2"
      shift 2
      ;;
    --branch)
      BRANCH="$2"
      shift 2
      ;;
    --stash)
      DO_STASH=1
      shift
      ;;
    -h|--help)
      sed -n '1,28p' "$0"
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Error: run this script from inside a git repository." >&2
  exit 1
fi

current_branch="$(git rev-parse --abbrev-ref HEAD)"
if [[ "$current_branch" == "HEAD" ]]; then
  echo "Error: detached HEAD is not supported by this updater." >&2
  exit 1
fi

if [[ -z "$BRANCH" ]]; then
  BRANCH="$current_branch"
fi

if ! git remote get-url "$REMOTE" >/dev/null 2>&1; then
  echo "Error: remote '$REMOTE' does not exist." >&2
  exit 1
fi

if ! git diff --quiet || ! git diff --cached --quiet; then
  if [[ "$DO_STASH" -eq 1 ]]; then
    echo "Stashing local changes..."
    git stash push -u -m "autostash: update_from_git.sh $(date -Iseconds)" >/dev/null
  else
    echo "Error: working tree has uncommitted changes." >&2
    echo "Commit/stash first, or rerun with --stash." >&2
    exit 1
  fi
fi

echo "Fetching $REMOTE..."
git fetch --prune "$REMOTE"

if ! git show-ref --verify --quiet "refs/remotes/$REMOTE/$BRANCH"; then
  echo "Error: remote branch '$REMOTE/$BRANCH' not found." >&2
  exit 1
fi

if [[ "$current_branch" != "$BRANCH" ]]; then
  echo "Switching to branch '$BRANCH'..."
  git checkout "$BRANCH"
fi

echo "Fast-forwarding '$BRANCH' from '$REMOTE/$BRANCH'..."
git merge --ff-only "$REMOTE/$BRANCH"

echo "Update complete."
git --no-pager log --oneline -n 3
