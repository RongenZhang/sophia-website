#!/bin/bash
# Wrapper the scheduler calls. Ensures git/python are on PATH (launchd starts
# with a minimal environment), then runs the build and logs the result.
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
cd "$(dirname "$0")" || exit 1
echo "----- $(date '+%Y-%m-%d %H:%M:%S') -----" >> build.log
/usr/bin/python3 build.py >> build.log 2>&1
