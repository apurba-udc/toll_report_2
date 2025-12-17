#!/bin/bash

# ==================================================
# Real-time Log Monitoring Script
# ==================================================

PROJECT_ROOT="/home/atonu/toll_report"
LOG_DIR="$PROJECT_ROOT/logs"

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

show_help() {
    echo "=== Toll System Log Monitor ==="
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  all       - Show all logs in real-time"
    echo "  django    - Django application logs"
    echo "  ssl       - SSL connection logs"
    echo "  db        - Database logs"
    echo "  auth      - Authentication logs"
    echo "  service   - Systemd service logs"
    echo "  system    - System and process logs"
    echo "  debug     - Debug logs"
    echo "  errors    - Show only error logs"
    echo "  help      - Show this help"
    echo ""
}

monitor_all_logs() {
    echo -e "${GREEN}=== MONITORING ALL LOGS ===${NC}"
    echo "Press Ctrl+C to stop monitoring"
    echo ""
    
    # Use multitail if available, otherwise use tail
    if command -v multitail >/dev/null 2>&1; then
        multitail \
            -ci green "$LOG_DIR/django/django.log" \
            -ci blue "$LOG_DIR/ssl/ssl_connections.log" \
            -ci yellow "$LOG_DIR/database/database.log" \
            -ci red "$LOG_DIR/auth/authentication.log" \
            -ci cyan "$LOG_DIR/debug/debug.log" \
            -ci white "$LOG_DIR/system/server_startup.log"
    else
        # Fallback to regular tail
        tail -f \
            "$LOG_DIR"/django/*.log \
            "$LOG_DIR"/ssl/*.log \
            "$LOG_DIR"/database/*.log \
            "$LOG_DIR"/auth/*.log \
            "$LOG_DIR"/debug/*.log \
            "$LOG_DIR"/system/*.log 2>/dev/null
    fi
}

monitor_service_logs() {
    echo -e "${BLUE}=== SYSTEMD SERVICE LOGS ===${NC}"
    echo "Monitoring toll-ssl service logs..."
    echo ""
    sudo journalctl -u toll-ssl -f --no-pager
}

monitor_errors_only() {
    echo -e "${RED}=== ERROR LOGS ONLY ===${NC}"
    echo "Monitoring error-level logs only..."
    echo ""
    
    tail -f "$LOG_DIR"/*/*.log | grep -i "error\|exception\|failed\|critical"
}

case "${1:-help}" in
    "all")
        monitor_all_logs
        ;;
    "django")
        echo -e "${GREEN}=== DJANGO LOGS ===${NC}"
        tail -f "$LOG_DIR/django"/*.log
        ;;
    "ssl")
        echo -e "${BLUE}=== SSL LOGS ===${NC}"
        tail -f "$LOG_DIR/ssl"/*.log
        ;;
    "db")
        echo -e "${YELLOW}=== DATABASE LOGS ===${NC}"
        tail -f "$LOG_DIR/database"/*.log
        ;;
    "auth")
        echo -e "${CYAN}=== AUTHENTICATION LOGS ===${NC}"
        tail -f "$LOG_DIR/auth"/*.log
        ;;
    "service")
        monitor_service_logs
        ;;
    "system")
        echo -e "${GREEN}=== SYSTEM LOGS ===${NC}"
        tail -f "$LOG_DIR/system"/*.log
        ;;
    "debug")
        echo -e "${CYAN}=== DEBUG LOGS ===${NC}"
        tail -f "$LOG_DIR/debug"/*.log
        ;;
    "errors")
        monitor_errors_only
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        echo "Unknown option: $1"
        show_help
        exit 1
        ;;
esac
