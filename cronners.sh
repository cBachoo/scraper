#!/bin/bash
# Purpose: Every x days: rebuild docker compose → git add info.json → commit & push if changed
# Runs as root - assumes SSH key is set up for passwordless git push
# Usage: cronners.sh [--dry-run]   (or DRY_RUN=1 cronners.sh)
#   --dry-run: still builds & runs the scraper, but only shows what git would
#              commit/push instead of doing it

set -euo pipefail

DRY_RUN="${DRY_RUN:-0}"
for arg in "$@"; do
    case "$arg" in
        -n|--dry-run) DRY_RUN=1 ;;
        *) echo "Unknown argument: $arg (usage: $0 [--dry-run])"; exit 2 ;;
    esac
done

# ================= CONFIG =================
PROJECT_DIR="/root/scraper"
LOG_FILE="/var/log/cronners_script.log"
GIT_BRANCH="docker"
SSH_KEY="/root/.ssh/id_ed25519_cron"
GIT_COMMIT_MSG="cron automation $(date '+%Y-%m-%d %H:%M:%S')"

# Docker Compose binary (full path - good for cron)
DOCKER_COMPOSE="/usr/bin/docker compose"   # confirm this with `which docker` when docker is plugin

# ==========================================

# Send ALL output (stdout + stderr) to BOTH the terminal and the log file.
# `tee -a` appends, matching the original per-line logging behaviour, so a
# manual run is now visible live while still being recorded for cron.
exec > >(tee -a "$LOG_FILE") 2>&1

echo "=== START $(date '+%Y-%m-%d %H:%M:%S') ==="
[ "$DRY_RUN" = "1" ] && echo "*** DRY RUN: no git add/commit/push will be performed ***"

# Go to project directory (very important in cron!)
cd "$PROJECT_DIR" || { echo "ERROR: Cannot cd to $PROJECT_DIR"; exit 1; }

# Force correct SSH key for git (no agent in cron!)
export GIT_SSH_COMMAND="ssh -i $SSH_KEY -o IdentitiesOnly=yes -o StrictHostKeyChecking=no"

# 1. Run scraper (rebuild if needed, wait for completion)
echo "[$(date '+%H:%M:%S')] Running docker compose run --build scraper..."
$DOCKER_COMPOSE run --build scraper || {
    echo "[$(date '+%H:%M:%S')] ERROR: docker compose run failed - check above output"
    # Optional: exit 1  ← uncomment if you want to stop on docker failure
}

# 2. Git operations - only commit if there are actual changes
echo "[$(date '+%H:%M:%S')] Checking for changes..."
/usr/bin/git status --porcelain

CHANGES=$(git status --porcelain | grep -c '^' || true)

if [ "$CHANGES" -eq 0 ]; then
    echo "[$(date '+%H:%M:%S')] No changes detected → skipping commit & push"
elif [ "$DRY_RUN" = "1" ]; then
    echo "[$(date '+%H:%M:%S')] $CHANGES change(s) found → DRY RUN, would commit & push:"
    /usr/bin/git --no-pager diff --stat
    echo "  would run: git add ."
    echo "  would run: git commit --no-gpg-sign -m \"$GIT_COMMIT_MSG\""
    echo "  would run: git push origin $GIT_BRANCH"
else
    echo "[$(date '+%H:%M:%S')] $CHANGES change(s) found → committing & pushing"

    /usr/bin/git add . || true

    # Commit without GPG (prevents hanging)
    /usr/bin/git commit --no-gpg-sign -m "$GIT_COMMIT_MSG" || {
        echo "Commit skipped (nothing new after add?)"
    }

    # Push
    /usr/bin/git push origin "$GIT_BRANCH" || {
        echo "ERROR: git push failed - check SSH key / permissions / network"
        exit 1
    }

    echo "[$(date '+%H:%M:%S')] Successfully pushed to $GIT_BRANCH"
fi

echo "=== END $(date '+%Y-%m-%d %H:%M:%S') ==="
echo ""
