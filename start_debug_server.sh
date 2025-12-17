#!/bin/bash

# ==================================================
# Debug Mode SSL Server Script
# ==================================================

PROJECT_ROOT="/home/atonu/toll_report"
LOG_DIR="$PROJECT_ROOT/logs"

# Enable all debug output
export DJANGO_DEBUG=1
export PYTHONUNBUFFERED=1
export DJANGO_SETTINGS_MODULE=toll_system.settings

# Create debug log file
DEBUG_LOG="$LOG_DIR/debug/server_debug_$(date +%Y%m%d_%H%M%S).log"

echo "=== TOLL SYSTEM DEBUG MODE ==="
echo "All logs will be saved to: $DEBUG_LOG"
echo "Press Ctrl+C to stop server"
echo "=========================="

# Change to project directory
cd "$PROJECT_ROOT"

# Activate virtual environment
source venv/bin/activate

# Start server with maximum debugging
exec > >(tee -a "$DEBUG_LOG") 2>&1

echo "[$(date)] Starting debug server..."

# Run with bash debug mode and Django debug
bash -x "$PROJECT_ROOT/start_toll_server.sh" start
