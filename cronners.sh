#!/bin/bash
# Purpose: Every x days: rebuild docker compose → git add info.json → commit & push if changed
# Runs as root - assumes SSH key is set up for passwordless git push

set -euo pipefail

# ================= CONFIG =================
PROJECT_DIR="/root/scraper"
LOG_FILE="/var/log/cronners_script.log"
GIT_BRANCH="docker"
SSH_KEY="/root/.ssh/id_ed25519_cron"
GIT_COMMIT_MSG="cron automation $(date '+%Y-%m-%d %H:%M:%S')"

# Docker Compose binary (full path - good for cron)
DOCKER_COMPOSE="/usr/bin/docker compose"   # confirm this with `which docker` when docker is plugin

# ==========================================

echo "=== START $(date '+%Y-%m-%d %H:%M:%S') ===" >> "$LOG_FILE"

# Go to project directory (very important in cron!)
cd "$PROJECT_DIR" || { echo "ERROR: Cannot cd to $PROJECT_DIR" >> "$LOG_FILE"; exit 1; }

# Force correct SSH key for git (no agent in cron!)
export GIT_SSH_COMMAND="ssh -i $SSH_KEY -o IdentitiesOnly=yes -o StrictHostKeyChecking=no"

# 1. Rebuild & (re)start containers in BACKGROUND!
echo "[$(date '+%H:%M:%S')] Running docker compose up -d --force-recreate --build..." >> "$LOG_FILE"
$DOCKER_COMPOSE up -d --force-recreate --build >> "$LOG_FILE" 2>&1 || {
    echo "[$(date '+%H:%M:%S')] ERROR: docker compose failed - check above output" >> "$LOG_FILE"
    # Optional: exit 1  ← uncomment if you want to stop on docker failure
}

# Give containers a moment to settle (optional but helps git see fresh changes)
sleep 60

# 2. Git operations - only commit if there are actual changes
echo "[$(date '+%H:%M:%S')] Checking for changes..." >> "$LOG_FILE"
/usr/bin/git status --porcelain >> "$LOG_FILE" 2>&1

CHANGES=$(git status --porcelain | grep -c '^' || true)

if [ "$CHANGES" -eq 0 ]; then
    echo "[$(date '+%H:%M:%S')] No changes detected → skipping commit & push" >> "$LOG_FILE"
else
    echo "[$(date '+%H:%M:%S')] $CHANGES change(s) found → committing & pushing" >> "$LOG_FILE"

    /usr/bin/git add . >> "$LOG_FILE" 2>&1 || true

    # Commit without GPG (prevents hanging)
    /usr/bin/git commit --no-gpg-sign -m "$GIT_COMMIT_MSG" >> "$LOG_FILE" 2>&1 || {
        echo "Commit skipped (nothing new after add?)" >> "$LOG_FILE"
    }

    # Push
    /usr/bin/git push origin "$GIT_BRANCH" >> "$LOG_FILE" 2>&1 || {
        echo "ERROR: git push failed - check SSH key / permissions / network" >> "$LOG_FILE"
        exit 1
    }

    echo "[$(date '+%H:%M:%S')] Successfully pushed to $GIT_BRANCH" >> "$LOG_FILE"
fi

echo "=== END $(date '+%Y-%m-%d %H:%M:%S') ===" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
