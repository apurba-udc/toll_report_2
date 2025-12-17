#!/bin/bash

# ==================================================
# Comprehensive Logging Setup for Toll System
# ==================================================
# This script enables all possible logging for debugging

PROJECT_ROOT="/home/atonu/toll_report"
LOG_DIR="$PROJECT_ROOT/logs"

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    local level="$1"
    local message="$2"
    case $level in
        "INFO") echo -e "${BLUE}[INFO]${NC} $message" ;;
        "SUCCESS") echo -e "${GREEN}[SUCCESS]${NC} $message" ;;
        "WARNING") echo -e "${YELLOW}[WARNING]${NC} $message" ;;
        "ERROR") echo -e "${RED}[ERROR]${NC} $message" ;;
        *) echo "$message" ;;
    esac
}

setup_logging_directories() {
    print_status "INFO" "Creating logging directories..."
    
    # Create comprehensive log structure
    mkdir -p "$LOG_DIR"/{system,django,ssl,database,auth,debug,service}
    
    # Set proper permissions
    chmod 755 "$LOG_DIR"
    chmod 755 "$LOG_DIR"/*
    
    print_status "SUCCESS" "Log directories created:"
    echo "  - $LOG_DIR/system/     # System and process logs"
    echo "  - $LOG_DIR/django/     # Django application logs"
    echo "  - $LOG_DIR/ssl/        # SSL certificate and connection logs"
    echo "  - $LOG_DIR/database/   # Database connection and query logs"
    echo "  - $LOG_DIR/auth/       # Authentication and security logs"
    echo "  - $LOG_DIR/debug/      # Debug and troubleshooting logs"
    echo "  - $LOG_DIR/service/    # Systemd service logs"
}

enable_django_debug_logging() {
    print_status "INFO" "Enabling Django debug logging..."
    
    cd "$PROJECT_ROOT"
    source venv/bin/activate
    
    # Create Django logging configuration
    cat > "$PROJECT_ROOT/logging_config.py" << 'EOF'
import os

# Django Logging Configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {asctime} {message}',
            'style': '{',
        },
        'detailed': {
            'format': '[{levelname}] {asctime} {name} {pathname}:{lineno} {funcName} {message}',
            'style': '{',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'django_file': {
            'class': 'logging.FileHandler',
            'filename': 'logs/django/django.log',
            'formatter': 'verbose',
        },
        'db_file': {
            'class': 'logging.FileHandler', 
            'filename': 'logs/database/database.log',
            'formatter': 'detailed',
        },
        'auth_file': {
            'class': 'logging.FileHandler',
            'filename': 'logs/auth/authentication.log', 
            'formatter': 'detailed',
        },
        'ssl_file': {
            'class': 'logging.FileHandler',
            'filename': 'logs/ssl/ssl_connections.log',
            'formatter': 'verbose',
        },
        'debug_file': {
            'class': 'logging.FileHandler',
            'filename': 'logs/debug/debug.log',
            'formatter': 'detailed',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'django_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['db_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.contrib.auth': {
            'handlers': ['auth_file'],
            'level': 'DEBUG', 
            'propagate': False,
        },
        'django.security': {
            'handlers': ['auth_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'transactions': {
            'handlers': ['console', 'django_file', 'debug_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'ssl': {
            'handlers': ['ssl_file'],
            'level': 'DEBUG',
            'propagate': False,
        }
    },
    'root': {
        'handlers': ['console', 'debug_file'],
        'level': 'DEBUG',
    }
}
EOF

    print_status "SUCCESS" "Django logging configuration created."
}

enable_systemd_logging() {
    print_status "INFO" "Setting up systemd service logging..."
    
    # Update service file for maximum logging
    cat > toll-ssl-debug.service << 'EOF'
[Unit]
Description=Toll Management System SSL Server (Debug Mode)
After=network.target
Wants=network.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/home/atonu/toll_report
Environment=DJANGO_SETTINGS_MODULE=toll_system.settings
Environment=PYTHONUNBUFFERED=1
Environment=DJANGO_DEBUG=1
Environment=PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ExecStart=/bin/bash -x /home/atonu/toll_report/start_toll_server.sh start
ExecStop=/bin/bash /home/atonu/toll_report/start_toll_server.sh stop
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=toll-ssl

# Ensure we can write to our directories
ReadWritePaths=/home/atonu/toll_report

[Install]
WantedBy=multi-user.target
EOF

    print_status "SUCCESS" "Debug service file created: toll-ssl-debug.service"
}

create_log_monitoring_script() {
    print_status "INFO" "Creating log monitoring script..."
    
    cat > "$PROJECT_ROOT/monitor_logs.sh" << 'EOF'
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
EOF

    chmod +x "$PROJECT_ROOT/monitor_logs.sh"
    print_status "SUCCESS" "Log monitoring script created: monitor_logs.sh"
}

create_debug_server_script() {
    print_status "INFO" "Creating debug server script..."
    
    cat > "$PROJECT_ROOT/start_debug_server.sh" << 'EOF'
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
EOF

    chmod +x "$PROJECT_ROOT/start_debug_server.sh"
    print_status "SUCCESS" "Debug server script created: start_debug_server.sh"
}

enable_ssl_debugging() {
    print_status "INFO" "Enabling SSL connection debugging..."
    
    # Create SSL debug script
    cat > "$PROJECT_ROOT/test_ssl_connection.sh" << 'EOF'
#!/bin/bash

# SSL Connection Testing and Debugging

HOST="115.127.158.186"
PORT="443"
LOG_FILE="logs/ssl/ssl_test_$(date +%Y%m%d_%H%M%S).log"

echo "=== SSL CONNECTION TEST ==="
echo "Host: $HOST:$PORT"
echo "Log: $LOG_FILE"
echo "=========================="

# Create log directory
mkdir -p logs/ssl

# Test SSL connection
echo "[$(date)] Testing SSL connection to $HOST:$PORT" | tee -a "$LOG_FILE"

# OpenSSL connection test
openssl s_client -connect "$HOST:$PORT" -servername "$HOST" -verify_return_error 2>&1 | tee -a "$LOG_FILE"

# Certificate details
echo -e "\n[$(date)] Certificate details:" | tee -a "$LOG_FILE"
openssl s_client -connect "$HOST:$PORT" -servername "$HOST" 2>/dev/null | openssl x509 -text -noout | tee -a "$LOG_FILE"

# Cipher information
echo -e "\n[$(date)] Cipher information:" | tee -a "$LOG_FILE"
nmap --script ssl-enum-ciphers -p 443 "$HOST" 2>&1 | tee -a "$LOG_FILE"

echo "SSL test completed. Check $LOG_FILE for details."
EOF

    chmod +x "$PROJECT_ROOT/test_ssl_connection.sh"
    print_status "SUCCESS" "SSL testing script created: test_ssl_connection.sh"
}

setup_log_rotation() {
    print_status "INFO" "Setting up log rotation..."
    
    # Create logrotate configuration
    sudo tee /etc/logrotate.d/toll-system > /dev/null << EOF
$PROJECT_ROOT/logs/*/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
    create 0644 root root
}
EOF

    print_status "SUCCESS" "Log rotation configured (30 days retention)"
}

show_log_commands() {
    print_status "INFO" "Available logging commands:"
    echo ""
    echo "=== REAL-TIME MONITORING ==="
    echo "  ./monitor_logs.sh all       # Monitor all logs"
    echo "  ./monitor_logs.sh django    # Django logs only"
    echo "  ./monitor_logs.sh ssl       # SSL logs only"
    echo "  ./monitor_logs.sh service   # Systemd service logs"
    echo "  ./monitor_logs.sh errors    # Error logs only"
    echo ""
    echo "=== DEBUG MODES ==="
    echo "  ./start_debug_server.sh     # Start server in debug mode"
    echo "  ./test_ssl_connection.sh    # Test SSL connections"
    echo ""
    echo "=== SYSTEMD SERVICE LOGS ==="
    echo "  sudo journalctl -u toll-ssl -f                    # Follow service logs"
    echo "  sudo journalctl -u toll-ssl --since '1 hour ago'  # Last hour logs"
    echo "  sudo journalctl -u toll-ssl --since today         # Today's logs"
    echo ""
    echo "=== MANUAL LOG VIEWING ==="
    echo "  tail -f logs/django/django.log                    # Django application"
    echo "  tail -f logs/ssl/ssl_connections.log              # SSL connections"
    echo "  tail -f logs/database/database.log                # Database queries"
    echo "  tail -f logs/auth/authentication.log              # Authentication"
    echo "  tail -f logs/debug/debug.log                      # Debug information"
    echo ""
    echo "=== LOG ANALYSIS ==="
    echo "  grep -r 'ERROR' logs/                             # Find all errors"
    echo "  grep -r 'login' logs/auth/                        # Login activities"
    echo "  grep -r 'SSL' logs/ssl/                           # SSL activities"
    echo ""
}

# Main execution
main() {
    local action="${1:-setup}"
    
    case "$action" in
        "setup")
            print_status "SUCCESS" "=== SETTING UP COMPREHENSIVE LOGGING ==="
            setup_logging_directories
            enable_django_debug_logging
            enable_systemd_logging
            create_log_monitoring_script
            create_debug_server_script
            enable_ssl_debugging
            setup_log_rotation
            show_log_commands
            print_status "SUCCESS" "=== LOGGING SETUP COMPLETE ==="
            ;;
        "monitor")
            ./monitor_logs.sh all
            ;;
        "debug")
            ./start_debug_server.sh
            ;;
        "commands")
            show_log_commands
            ;;
        *)
            echo "Usage: $0 [setup|monitor|debug|commands]"
            exit 1
            ;;
    esac
}

main "$@" 