#!/bin/bash
# Example: Deploy website via FTP
#
# Usage: ./deploy.sh [--backup]

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
FTP="python3 $SCRIPT_DIR/../scripts/ftp.py"

REMOTE_ROOT="/public_html"
LOCAL_BUILD="./build"

# Backup current version if requested
if [[ "$1" == "--backup" ]]; then
    echo "📦 Backing up current remote files..."
    BACKUP_DIR="$HOME/backups/ftp-website-$(date +%Y%m%d-%H%M%S)"
    $FTP backup "$REMOTE_ROOT" "$BACKUP_DIR"
    echo "✅ Backup saved to $BACKUP_DIR"
fi

# Check if build dir exists
if [[ ! -d "$LOCAL_BUILD" ]]; then
    echo "❌ Build directory not found: $LOCAL_BUILD"
    exit 1
fi

# Sync to remote
echo "🚀 Uploading website..."
$FTP sync-upload "$LOCAL_BUILD" "$REMOTE_ROOT" | jq .

echo "✅ Deployment complete!"
