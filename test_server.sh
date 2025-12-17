#!/bin/bash

# ==================================================
# Toll System Server Testing and Troubleshooting Script
# ==================================================

PROJECT_ROOT="/home/atonu/toll_report"
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

test_django_setup() {
    print_status "INFO" "Django setup test করা হচ্ছে..."
    
    cd "$PROJECT_ROOT"
    source venv/bin/activate
    
    # Test Django check
    print_status "INFO" "Django check চালানো হচ্ছে..."
    python manage.py check
    
    # Test collectstatic
    print_status "INFO" "Static files collect করা হচ্ছে..."
    python manage.py collectstatic --noinput
    
    # Test template availability
    print_status "INFO" "Template files যাচাই করা হচ্ছে..."
    
    if [ -f "templates/auth/login.html" ]; then
        print_status "SUCCESS" "Login template পাওয়া গেছে।"
    else
        print_status "ERROR" "Login template পাওয়া যায়নি!"
    fi
    
    # Test URL patterns
    print_status "INFO" "URL patterns test করা হচ্ছে..."
    python manage.py show_urls 2>/dev/null || echo "show_urls command not available"
}

test_ssl_certificates() {
    print_status "INFO" "SSL certificates test করা হচ্ছে..."
    
    CERT_DIR="$PROJECT_ROOT/cert"
    
    if [ -f "$CERT_DIR/private.key" ]; then
        print_status "SUCCESS" "Private key পাওয়া গেছে।"
        # Check key validity
        if openssl rsa -in "$CERT_DIR/private.key" -check -noout 2>/dev/null; then
            print_status "SUCCESS" "Private key valid।"
        else
            print_status "ERROR" "Private key invalid!"
        fi
    else
        print_status "ERROR" "Private key পাওয়া যায়নি!"
    fi
    
    if [ -f "$CERT_DIR/certificate.crt" ]; then
        print_status "SUCCESS" "Certificate পাওয়া গেছে।"
        # Check certificate validity
        if openssl x509 -in "$CERT_DIR/certificate.crt" -text -noout 2>/dev/null; then
            print_status "SUCCESS" "Certificate valid।"
            print_status "INFO" "Certificate details:"
            openssl x509 -in "$CERT_DIR/certificate.crt" -subject -dates -noout 2>/dev/null
        else
            print_status "ERROR" "Certificate invalid!"
        fi
    else
        print_status "ERROR" "Certificate পাওয়া যায়নি!"
    fi
}

test_database_connection() {
    print_status "INFO" "Database connection test করা হচ্ছে..."
    
    cd "$PROJECT_ROOT"
    source venv/bin/activate
    
    # Test database connection
    python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'toll_system.settings')
django.setup()

from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
        result = cursor.fetchone()
        print('✅ Database connection successful!')
        print(f'Result: {result}')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
"
}

test_user_authentication() {
    print_status "INFO" "User authentication test করা হচ্ছে..."
    
    cd "$PROJECT_ROOT"
    source venv/bin/activate
    
    python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'toll_system.settings')
django.setup()

from transactions.models import TollUser
try:
    users = TollUser.objects.filter(active=True)[:5]
    print(f'✅ Found {users.count()} active users')
    for user in users:
        print(f'  - {user.username} ({user.name}) - Role: {user.role}')
except Exception as e:
    print(f'❌ User authentication test failed: {e}')
"
}

test_server_ports() {
    print_status "INFO" "Server ports যাচাই করা হচ্ছে..."
    
    # Check port 443
    if netstat -tuln | grep -q ":443 "; then
        print_status "WARNING" "Port 443 already in use:"
        netstat -tulnp | grep ":443 "
    else
        print_status "SUCCESS" "Port 443 available।"
    fi
    
    # Check port 8000 (alternative)
    if netstat -tuln | grep -q ":8000 "; then
        print_status "WARNING" "Port 8000 already in use:"
        netstat -tulnp | grep ":8000 "
    else
        print_status "SUCCESS" "Port 8000 available।"
    fi
}

start_development_server() {
    print_status "INFO" "Development server (without SSL) চালু করা হচ্ছে..."
    
    cd "$PROJECT_ROOT"
    source venv/bin/activate
    
    print_status "SUCCESS" "=== DEVELOPMENT SERVER ==="
    print_status "INFO" "Server URL: http://localhost:8000"
    print_status "INFO" "Press Ctrl+C to stop"
    print_status "SUCCESS" "=========================="
    
    python manage.py runserver 0.0.0.0:8000
}

fix_template_issues() {
    print_status "INFO" "Template issues ঠিক করা হচ্ছে..."
    
    cd "$PROJECT_ROOT"
    
    # Ensure templates directory exists
    mkdir -p templates/auth
    
    # Check if login template exists
    if [ ! -f "templates/auth/login.html" ]; then
        print_status "ERROR" "Login template missing! একটি basic template তৈরি করুন।"
        return 1
    fi
    
    # Run collectstatic to ensure static files are available
    source venv/bin/activate
    python manage.py collectstatic --noinput
    
    print_status "SUCCESS" "Template issues fixed।"
}

show_logs() {
    print_status "INFO" "Recent logs দেখানো হচ্ছে..."
    
    echo "=== Server Startup Logs ==="
    if [ -f "$PROJECT_ROOT/logs/server_startup.log" ]; then
        tail -20 "$PROJECT_ROOT/logs/server_startup.log"
    else
        print_status "INFO" "No startup logs found।"
    fi
    
    echo -e "\n=== Django Logs ==="
    if [ -f "$PROJECT_ROOT/logs/toll_system.log" ]; then
        tail -20 "$PROJECT_ROOT/logs/toll_system.log"
    else
        print_status "INFO" "No Django logs found।"
    fi
    
    echo -e "\n=== Error Logs ==="
    if [ -f "$PROJECT_ROOT/logs/server_errors.log" ]; then
        tail -20 "$PROJECT_ROOT/logs/server_errors.log"
    else
        print_status "INFO" "No error logs found।"
    fi
}

show_help() {
    echo "=== Toll System Server Testing Script ==="
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  all        - সমস্ত tests চালান"
    echo "  django     - Django setup test"
    echo "  ssl        - SSL certificates test"
    echo "  db         - Database connection test"
    echo "  auth       - User authentication test"
    echo "  ports      - Server ports check"
    echo "  dev        - Development server start (no SSL)"
    echo "  fix        - Template issues ঠিক করুন"
    echo "  logs       - Recent logs দেখান"
    echo "  help       - এই help message"
    echo ""
}

case "${1:-all}" in
    "all")
        test_django_setup
        echo ""
        test_ssl_certificates
        echo ""
        test_database_connection
        echo ""
        test_user_authentication
        echo ""
        test_server_ports
        ;;
    "django")
        test_django_setup
        ;;
    "ssl")
        test_ssl_certificates
        ;;
    "db")
        test_database_connection
        ;;
    "auth")
        test_user_authentication
        ;;
    "ports")
        test_server_ports
        ;;
    "dev")
        start_development_server
        ;;
    "fix")
        fix_template_issues
        ;;
    "logs")
        show_logs
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        print_status "ERROR" "Unknown option: $1"
        show_help
        exit 1
        ;;
esac 