#!/bin/bash
# Example: Daily FTP backup of critical directories
#
# Add to crontab:
#   0 2 * * * /path/to/backup.sh

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
FTP="python3 $SCRIPT_DIR/../scripts/ftp.py"

BACKUP_ROOT="$HOME/backups/ftp-daily"
TIMESTAMP=$(date +%Y%m%d)

# Create backup parent dir
mkdir -p "$BACKUP_ROOT"

# Backup multiple remote directories
declare -a REMOTE_DIRS=("/documents" "/databases" "/logs")

for remote_dir in "${REMOTE_DIRS[@]}"; do
    echo "📥 Backing up $remote_dir..."
    local_backup="$BACKUP_ROOT/$TIMESTAMP$remote_dir"
    $FTP sync-download "$remote_dir" "$local_backup" | jq .
done

# Clean up backups older than 30 days
echo "🗑️  Cleaning up old backups..."
find "$BACKUP_ROOT" -type d -mtime +30 -exec rm -rf {} \;

echo "✅ Daily backup complete!"
