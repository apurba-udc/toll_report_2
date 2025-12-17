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
