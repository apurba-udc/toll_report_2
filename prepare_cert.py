#!/usr/bin/env python
"""
Prepare SSL certificate files for Django SSL server
"""
import os
import shutil

def prepare_certificates():
    """Prepare SSL certificate files"""
    cert_dir = os.path.join(os.path.dirname(__file__), 'cert')
    
    # Check if cert directory exists
    if not os.path.exists(cert_dir):
        print(f"Creating cert directory: {cert_dir}")
        os.makedirs(cert_dir)
    
    # Required files
    required_files = {
        'private.key': 'Private key file',
        'certificate.crt': 'Certificate file',
        'combined_cert.crt': 'Combined certificate file (with chain)'
    }
    
    # Check if all required files exist
    missing_files = []
    for filename, description in required_files.items():
        filepath = os.path.join(cert_dir, filename)
        if not os.path.exists(filepath):
            missing_files.append(f"{filename} ({description})")
    
    if missing_files:
        print("Error: The following certificate files are missing:")
        for file in missing_files:
            print(f"  - {file}")
        print(f"\nPlease place all certificate files in the '{cert_dir}' directory.")
        return False
    
    # Create combined SSL certificate
    certificate_path = os.path.join(cert_dir, 'certificate.crt')
    chain_path = os.path.join(cert_dir, 'combined_cert.crt')
    ssl_cert_path = os.path.join(cert_dir, 'ssl_cert.pem')
    
    try:
        # Read certificate files
        with open(certificate_path, 'r') as cert_file:
            cert_content = cert_file.read().strip()
        
        with open(chain_path, 'r') as chain_file:
            chain_content = chain_file.read().strip()
        
        # Create combined certificate
        combined_content = cert_content + '\n' + chain_content
        
        with open(ssl_cert_path, 'w') as ssl_file:
            ssl_file.write(combined_content)
        
        print("✅ SSL certificate files prepared successfully!")
        print(f"Combined certificate created: {ssl_cert_path}")
        print("\nYou can now run the SSL server using:")
        print("python manage.py runsslserver")
        print("\nOr:")
        print("python run_ssl.py")
        
        return True
        
    except Exception as e:
        print(f"Error preparing certificates: {e}")
        return False

if __name__ == '__main__':
    prepare_certificates() 