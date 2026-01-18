#!/bin/bash
# Purpose: Every x days: run docker compose → git add info.json → commit & push if changed
# Runs as root - assumes SSH key is set up for passwordless git push

set -euo pipefail

# ================= CONFIG =================
PROJECT_DIR="/root/scraper"   # ← CHANGE THIS !!
LOG_FILE="/var/log/cronners.log"
GIT_BRANCH="docker"
SSH_KEY="/root/.ssh/id_ed25519_cron"
GIT_COMMIT_MSG="cron automation $(date '+%Y-%m-%d %H:%M:%S')"

# Docker Compose binary (use full path - helps in cron)
DOCKER_COMPOSE="/usr/bin/docker compose"

# ==========================================

echo "=== START $(date '+%Y-%m-%d %H:%M:%S') ===" >> "$LOG_FILE"

# Go to project directory
cd "$PROJECT_DIR" || { echo "ERROR: Cannot cd to $PROJECT_DIR" >> "$LOG_FILE"; exit 1; }

# Tell git to use our dedicated cron SSH key
export GIT_SSH_COMMAND="ssh -i $SSH_KEY -o IdentitiesOnly=yes -o StrictHostKeyChecking=no"

# 1. Rebuild & restart containers
echo "[$(date '+%H:%M:%S')] Running docker compose up --force-recreate --build..." >> "$LOG_FILE"
$DOCKER_COMPOSE up -d --force-recreate --build >> "$LOG_FILE" 2>&1

# Small pause - sometimes git sees files still being written
sleep 3

# 2. Git operations - only commit if there are actual changes
echo "[$(date '+%H:%M:%S')] Checking for changes..." >> "$LOG_FILE"
git status --porcelain >> "$LOG_FILE" 2>&1

CHANGES=$(git status --porcelain | grep -c '^' || true)

if [ "$CHANGES" -eq 0 ]; then
    echo "[$(date '+%H:%M:%S')] No changes detected → skipping commit & push" >> "$LOG_FILE"
else
    echo "[$(date '+%H:%M:%S')] $CHANGES change(s) found → committing & pushing" >> "$LOG_FILE"

    # Add only the file you care about (safer than git add .)
    /usr/bin/git add info.json >> "$LOG_FILE" 2>&1 || true

    # Commit (skip GPG signing - prevents hanging in cron)
    /usr/bin/git commit --no-gpg-sign -m "$GIT_COMMIT_MSG" >> "$LOG_FILE" 2>&1 || {
        echo "Commit skipped (nothing to commit after add?)" >> "$LOG_FILE"
    }

    # Push
    /usr/bin/git push origin "$GIT_BRANCH" >> "$LOG_FILE" 2>&1 || {
        echo "ERROR: git push failed - check SSH key / permissions" >> "$LOG_FILE"
        exit 1
    }

    echo "[$(date '+%H:%M:%S')] Successfully pushed to $GIT_BRANCH" >> "$LOG_FILE"
fi

echo "=== END $(date '+%Y-%m-%d %H:%M:%S') ===" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
