#!/bin/bash
# Installs (or reinstalls) the automatic-rebuild scheduler.
# Run once after your GitHub remote is set up:  bash install_scheduler.sh
set -e
PLIST=com.sophia.website.plist
DEST="$HOME/Library/LaunchAgents/$PLIST"

cp "$(dirname "$0")/$PLIST" "$DEST"
launchctl unload "$DEST" 2>/dev/null || true
launchctl load "$DEST"
echo "Installed and loaded $PLIST"
echo "It will rebuild daily at noon and whenever the CV folder changes."
echo "To stop it later:  launchctl unload \"$DEST\""
