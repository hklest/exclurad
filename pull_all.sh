#!/usr/bin/env bash
set -euo pipefail

# Convenience wrapper expected by some local workflows.
# Delegates to the main updater with auto-stash behavior.

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$repo_root"

exec ./scripts/update_from_git.sh "$@"
