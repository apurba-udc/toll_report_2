#!/usr/bin/env python
"""
SSL-enabled Django development server runner
"""
import os
import sys
import django
from django.core.management import execute_from_command_line
from django.conf import settings

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'toll_system.settings')
django.setup()

def run_ssl_server():
    """Run Django server with SSL enabled"""
    
    # Certificate file paths
    cert_dir = os.path.join(os.path.dirname(__file__), 'cert')
    private_key = os.path.join(cert_dir, 'private.key')
    certificate = os.path.join(cert_dir, 'certificate.crt')
    chain_cert = os.path.join(cert_dir, 'combined_cert.crt')
    
    # Check if certificate files exist
    if not os.path.exists(private_key):
        print(f"Error: Private key file not found at {private_key}")
        return
    
    if not os.path.exists(certificate):
        print(f"Error: Certificate file not found at {certificate}")
        return
    
    if not os.path.exists(chain_cert):
        print(f"Error: Combined certificate file not found at {chain_cert}")
        return
    
    # Create combined certificate file for SSL
    combined_cert_path = os.path.join(cert_dir, 'ssl_cert.pem')
    try:
        with open(certificate, 'r') as cert_file:
            cert_content = cert_file.read()
        
        with open(chain_cert, 'r') as chain_file:
            chain_content = chain_file.read()
        
        with open(combined_cert_path, 'w') as combined_file:
            combined_file.write(cert_content + '\n' + chain_content)
        
        print(f"Combined certificate created at: {combined_cert_path}")
    except Exception as e:
        print(f"Error creating combined certificate: {e}")
        return
    
    # Get server address from command line arguments
    server_addr = '115.127.158.186:443'  # Default
    if len(sys.argv) > 1:
        server_addr = sys.argv[1]
    
    # Run the server with SSL
    try:
        print("Starting Django server with SSL...")
        print(f"Certificate: {combined_cert_path}")
        print(f"Private Key: {private_key}")
        print(f"Server will be available at: https://{server_addr}")
        print("Press Ctrl+C to stop the server")
        
        # Use Django's runserver command with SSL
        execute_from_command_line([
            'manage.py', 'runsslserver',
            '--cert', combined_cert_path,
            '--key-file', private_key,
            server_addr
        ])
        
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error running server: {e}")
    finally:
        # Clean up combined certificate file
        if os.path.exists(combined_cert_path):
            os.remove(combined_cert_path)
            print("Cleaned up temporary certificate file")

if __name__ == '__main__':
    run_ssl_server() 
