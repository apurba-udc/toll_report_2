#!/bin/bash

# ==================================================
# Toll Management System SSL Server Startup Script
# ==================================================
# This script starts the Django toll management system with SSL
# replacing the Python-based run_ssl.py script for better reliability
# ==================================================

# Set script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SERVER_HOST="115.127.158.188"
SERVER_PORT="443"
CERT_DIR="$PROJECT_ROOT/cert"
VENV_DIR="$PROJECT_ROOT/venv"
MANAGE_PY="$PROJECT_ROOT/manage.py"

# Certificate files
PRIVATE_KEY="$CERT_DIR/private.key"
CERTIFICATE="$CERT_DIR/certificate.crt"
CHAIN_CERT="$CERT_DIR/combined_cert.crt"
SSL_CERT="$CERT_DIR/ssl_cert.pem"

# Logging
LOG_FILE="$PROJECT_ROOT/logs/server_startup.log"
ERROR_LOG="$PROJECT_ROOT/logs/server_errors.log"

# ==================================================
# Helper Functions
# ==================================================

log_message() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

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
    log_message "$level" "$message"
}

check_requirements() {
    print_status "INFO" "Certificate requirements যাচাই করা হচ্ছে..."
    
    # Check if cert directory exists
    if [ ! -d "$CERT_DIR" ]; then
        print_status "ERROR" "Certificate directory পাওয়া যায়নি: $CERT_DIR"
        return 1
    fi
    
    # Check certificate files
    local missing_files=()
    
    if [ ! -f "$PRIVATE_KEY" ]; then
        missing_files+=("private.key")
    fi
    
    if [ ! -f "$CERTIFICATE" ]; then
        missing_files+=("certificate.crt")
    fi
    
    if [ ! -f "$CHAIN_CERT" ]; then
        missing_files+=("combined_cert.crt")
    fi
    
    if [ ${#missing_files[@]} -gt 0 ]; then
        print_status "ERROR" "নিম্নলিখিত certificate files পাওয়া যায়নি:"
        for file in "${missing_files[@]}"; do
            print_status "ERROR" "  - $CERT_DIR/$file"
        done
        print_status "ERROR" "দয়া করে সমস্ত certificate files cert/ ফোল্ডারে রাখুন।"
        return 1
    fi
    
    # Check virtual environment
    if [ ! -d "$VENV_DIR" ]; then
        print_status "ERROR" "Virtual environment পাওয়া যায়নি: $VENV_DIR"
        return 1
    fi
    
    # Check manage.py
    if [ ! -f "$MANAGE_PY" ]; then
        print_status "ERROR" "Django manage.py পাওয়া যায়নি: $MANAGE_PY"
        return 1
    fi
    
    print_status "SUCCESS" "সমস্ত requirements পূরণ হয়েছে।"
    return 0
}

create_ssl_certificate() {
    print_status "INFO" "SSL certificate তৈরি করা হচ্ছে..."
    
    # Remove existing SSL certificate if it exists
    if [ -f "$SSL_CERT" ]; then
        rm -f "$SSL_CERT"
        print_status "INFO" "পুরাতন SSL certificate সরানো হয়েছে।"
    fi
    
    # Create combined certificate
    if cat "$CERTIFICATE" "$CHAIN_CERT" > "$SSL_CERT" 2>/dev/null; then
        print_status "SUCCESS" "SSL certificate তৈরি হয়েছে: $SSL_CERT"
        # Set proper permissions
        chmod 600 "$SSL_CERT"
        return 0
    else
        print_status "ERROR" "SSL certificate তৈরি করতে ব্যর্থ হয়েছে।"
        return 1
    fi
}

check_port() {
    print_status "INFO" "Port $SERVER_PORT availability যাচাই করা হচ্ছে..."
    
    if command -v netstat >/dev/null 2>&1; then
        if netstat -tuln | grep -q ":$SERVER_PORT "; then
            print_status "WARNING" "Port $SERVER_PORT ইতিমধ্যে ব্যবহৃত হচ্ছে।"
            print_status "INFO" "Port ব্যবহারকারী processes:"
            netstat -tulnp | grep ":$SERVER_PORT " || true
            return 1
        fi
    elif command -v ss >/dev/null 2>&1; then
        if ss -tuln | grep -q ":$SERVER_PORT "; then
            print_status "WARNING" "Port $SERVER_PORT ইতিমধ্যে ব্যবহৃত হচ্ছে।"
            print_status "INFO" "Port ব্যবহারকারী processes:"
            ss -tulnp | grep ":$SERVER_PORT " || true
            return 1
        fi
    else
        print_status "WARNING" "Port checking tools (netstat/ss) পাওয়া যায়নি।"
    fi
    
    print_status "SUCCESS" "Port $SERVER_PORT available।"
    return 0
}

kill_existing_servers() {
    print_status "INFO" "বিদ্যমান Django servers বন্ধ করা হচ্ছে..."
    
    # Kill Django processes
    if pgrep -f "manage.py.*runserver\|runsslserver" >/dev/null 2>&1; then
        print_status "INFO" "Django server processes খুঁজে পাওয়া গেছে।"
        pkill -f "manage.py.*runserver\|runsslserver" 2>/dev/null || true
        sleep 2
        
        # Force kill if still running
        if pgrep -f "manage.py.*runserver\|runsslserver" >/dev/null 2>&1; then
            print_status "WARNING" "Force killing remaining Django processes..."
            pkill -9 -f "manage.py.*runserver\|runsslserver" 2>/dev/null || true
            sleep 1
        fi
        
        print_status "SUCCESS" "Django server processes বন্ধ করা হয়েছে।"
    else
        print_status "INFO" "কোনো চলমান Django server পাওয়া যায়নি।"
    fi
}

activate_virtualenv() {
    print_status "INFO" "Virtual environment activate করা হচ্ছে..."
    
    # Activate virtual environment
    if [ -f "$VENV_DIR/bin/activate" ]; then
        source "$VENV_DIR/bin/activate"
        print_status "SUCCESS" "Virtual environment activated।"
        return 0
    else
        print_status "ERROR" "Virtual environment activation script পাওয়া যায়নি।"
        return 1
    fi
}

check_django_setup() {
    print_status "INFO" "Django setup যাচাই করা হচ্ছে..."
    
    # Check if Django is properly installed and configured
    cd "$PROJECT_ROOT"
    
    if python "$MANAGE_PY" check --deploy 2>/dev/null; then
        print_status "SUCCESS" "Django configuration সঠিক।"
        return 0
    else
        print_status "WARNING" "Django deployment check warnings রয়েছে। Server চালু করা হবে তবে warnings check করুন।"
        python "$MANAGE_PY" check 2>&1 | tee -a "$ERROR_LOG" || true
        return 0
    fi
}

start_ssl_server() {
    print_status "INFO" "SSL server চালু করা হচ্ছে..."
    
    cd "$PROJECT_ROOT"
    
    # Set Django settings
    export DJANGO_SETTINGS_MODULE="toll_system.settings"
    
    print_status "SUCCESS" "=== TOLL MANAGEMENT SYSTEM SSL SERVER ==="
    print_status "INFO" "Certificate: $SSL_CERT"
    print_status "INFO" "Private Key: $PRIVATE_KEY"
    print_status "INFO" "Server URL: https://$SERVER_HOST:$SERVER_PORT"
    print_status "INFO" "Press Ctrl+C to stop the server"
    print_status "SUCCESS" "================================================"
    
    # Create a cleanup function for when script exits
    cleanup() {
        print_status "INFO" "Server shutdown করা হচ্ছে..."
        if [ -f "$SSL_CERT" ]; then
            rm -f "$SSL_CERT"
            print_status "INFO" "Temporary SSL certificate সরানো হয়েছে।"
        fi
        print_status "SUCCESS" "Server বন্ধ হয়েছে।"
        exit 0
    }
    
    # Set trap for cleanup
    trap cleanup SIGINT SIGTERM EXIT
    
    # Start the Django SSL server
    python "$MANAGE_PY" runsslserver \
        --cert "$SSL_CERT" \
        --key-file "$PRIVATE_KEY" \
        "$SERVER_HOST:$SERVER_PORT" 2>&1 | tee -a "$LOG_FILE"
}

show_help() {
    echo "=== Toll Management System SSL Server ==="
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  start     - Start the SSL server (default)"
    echo "  stop      - Stop running Django servers"
    echo "  restart   - Restart the SSL server"
    echo "  status    - Check server status"
    echo "  check     - Check requirements only"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0              # Start server"
    echo "  $0 start        # Start server"
    echo "  $0 stop         # Stop all Django servers"
    echo "  $0 restart      # Restart server"
    echo "  $0 status       # Check status"
    echo ""
}

show_status() {
    print_status "INFO" "Server status যাচাই করা হচ্ছে..."
    
    if pgrep -f "manage.py.*runserver\|runsslserver" >/dev/null 2>&1; then
        print_status "SUCCESS" "Django server চলমান রয়েছে।"
        print_status "INFO" "Running processes:"
        pgrep -f -l "manage.py.*runserver\|runsslserver" || true
    else
        print_status "INFO" "কোনো Django server চলমান নেই।"
    fi
    
    # Check port status
    check_port
}

# ==================================================
# Main Execution
# ==================================================

main() {
    local action="${1:-start}"
    
    # Create logs directory if it doesn't exist
    mkdir -p "$(dirname "$LOG_FILE")"
    
    print_status "SUCCESS" "=== Toll System SSL Server Script ==="
    print_status "INFO" "Script started with action: $action"
    
    case "$action" in
        "start")
            if ! check_requirements; then
                exit 1
            fi
            
            kill_existing_servers
            
            if ! check_port; then
                print_status "ERROR" "Port $SERVER_PORT উপলব্ধ নেই। অন্য একটি service এই port ব্যবহার করছে।"
                print_status "INFO" "চালমান processes বন্ধ করার চেষ্টা করুন অথবা অন্য একটি port ব্যবহার করুন।"
                exit 1
            fi
            
            if ! activate_virtualenv; then
                exit 1
            fi
            
            if ! check_django_setup; then
                exit 1
            fi
            
            if ! create_ssl_certificate; then
                exit 1
            fi
            
            start_ssl_server
            ;;
        "stop")
            kill_existing_servers
            if [ -f "$SSL_CERT" ]; then
                rm -f "$SSL_CERT"
                print_status "INFO" "SSL certificate সরানো হয়েছে।"
            fi
            ;;
        "restart")
            print_status "INFO" "Server restart করা হচ্ছে..."
            kill_existing_servers
            sleep 2
            exec "$0" start
            ;;
        "status")
            show_status
            ;;
        "check")
            check_requirements
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_status "ERROR" "অজানা action: $action"
            show_help
            exit 1
            ;;
    esac
}

# Check if script is run as root for port 443
if [ "$EUID" -ne 0 ] && [ "$SERVER_PORT" = "443" ]; then
    print_status "WARNING" "Port 443 ব্যবহারের জন্য root privileges প্রয়োজন।"
    print_status "INFO" "Script restart করা হচ্ছে sudo দিয়ে..."
    exec sudo "$0" "$@"
fi

# Run main function with all arguments
main "$@" 
