#!/usr/bin/env python
"""
Simple SSL-enabled Django server runner
"""
import os
import sys
import ssl
import socket
from http.server import HTTPServer, SimpleHTTPRequestHandler
from django.core.management import execute_from_command_line

def create_ssl_context():
    """Create SSL context with certificates"""
    cert_dir = os.path.join(os.path.dirname(__file__), 'cert')
    private_key = os.path.join(cert_dir, 'private.key')
    certificate = os.path.join(cert_dir, 'certificate.crt')
    chain_cert = os.path.join(cert_dir, 'combined_cert.crt')
    
    # Check if files exist
    for file_path in [private_key, certificate, chain_cert]:
        if not os.path.exists(file_path):
            print(f"Error: File not found: {file_path}")
            return None
    
    # Create combined certificate
    combined_cert_path = os.path.join(cert_dir, 'ssl_cert.pem')
    try:
        with open(certificate, 'r') as cert_file:
            cert_content = cert_file.read()
        
        with open(chain_cert, 'r') as chain_file:
            chain_content = chain_file.read()
        
        with open(combined_cert_path, 'w') as combined_file:
            combined_file.write(cert_content + '\n' + chain_content)
        
        print(f"Combined certificate created: {combined_cert_path}")
        
        # Create SSL context
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(combined_cert_path, private_key)
        
        return context, combined_cert_path
        
    except Exception as e:
        print(f"Error creating SSL context: {e}")
        return None

def run_django_ssl():
    """Run Django with SSL using manage.py"""
    print("Starting Django with SSL...")
    print("Make sure your certificate files are in the 'cert' folder:")
    print("- private.key")
    print("- certificate.crt") 
    print("- combined_cert.crt")
    print("\nServer will be available at: https://toll.sdlbdcloud.com:8000")
    
    # Set environment variable for SSL
    os.environ['DJANGO_SETTINGS_MODULE'] = 'toll_system.settings'
    
    # Run Django with SSL
    try:
        execute_from_command_line([
            'manage.py', 'runserver',
            'toll.sdlbdcloud.com:8000'
        ])
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    run_django_ssl() 