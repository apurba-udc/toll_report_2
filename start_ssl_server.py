#!/usr/bin/env python3
"""
SSL Django Development Server
Starts Django with SSL using provided certificates
"""
import os
import sys
import django
from django.core.management import execute_from_command_line
from django.core.management.commands.runserver import Command as RunServerCommand
from django.core.servers.basehttp import get_internal_wsgi_application
import ssl
import socket
from wsgiref import simple_server

def start_ssl_server():
    """Start Django development server with SSL"""
    
    # Certificate paths
    cert_file = "/home/atonu/toll_report/cert/ssl_cert.pem"
    key_file = "/home/atonu/toll_report/cert/private.key"
    
    # Check if certificate files exist
    if not os.path.exists(cert_file):
        print(f"Error: Certificate file not found: {cert_file}")
        return False
    
    if not os.path.exists(key_file):
        print(f"Error: Private key file not found: {key_file}")
        return False
    
    print(f"Starting Django server with SSL...")
    print(f"Certificate: {cert_file}")
    print(f"Private Key: {key_file}")
    print(f"Server will be available at: https://0.0.0.0:443")
    print(f"Press Ctrl+C to stop the server")
    
    try:
        # Set up Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'toll_system.settings')
        django.setup()
        
        # Get WSGI application
        application = get_internal_wsgi_application()
        
        # Create SSL context
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cert_file, key_file)
        
        # Create server
        server = simple_server.make_server('0.0.0.0', 443, application)
        server.socket = context.wrap_socket(server.socket, server_side=True)
        
        print("SSL Server started successfully!")
        server.serve_forever()
        
    except PermissionError:
        print("Error: Permission denied. Port 443 requires root privileges.")
        print("Try running with sudo or use a different port (e.g., 8443)")
        return False
    except FileNotFoundError as e:
        print(f"Error: Certificate file issue: {e}")
        return False
    except ssl.SSLError as e:
        print(f"Error: SSL configuration issue: {e}")
        return False
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        return True
    except Exception as e:
        print(f"Error running server: {e}")
        return False

if __name__ == "__main__":
    start_ssl_server() 