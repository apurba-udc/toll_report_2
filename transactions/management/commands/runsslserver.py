"""
Custom Django management command to run server with SSL
"""
import os
import ssl
import socket
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.core.servers.basehttp import WSGIServer
from django.core.wsgi import get_wsgi_application
from django.conf import settings

class SSLWSGIServer(WSGIServer):
    def __init__(self, server_address, RequestHandlerClass, certfile, keyfile, **kwargs):
        super().__init__(server_address, RequestHandlerClass, **kwargs)
        
        # Create SSL context
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile, keyfile)
        
        # Wrap socket with SSL
        self.socket = context.wrap_socket(self.socket, server_side=True)

class Command(BaseCommand):
    help = 'Run Django development server with SSL support'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'addrport',
            nargs='?',
            default='toll.sdlbdcloud.com:8000',
            help='Port number or ipaddr:port'
        )
        parser.add_argument(
            '--cert',
            default='cert/ssl_cert.pem',
            help='SSL certificate file path'
        )
        parser.add_argument(
            '--key-file',
            default='cert/private.key',
            help='SSL private key file path'
        )
    
    def handle(self, *args, **options):
        addrport = options['addrport']
        certfile = options['cert']
        keyfile = options['key_file']
        
        # Check if certificate files exist
        if not os.path.exists(certfile):
            self.stdout.write(
                self.style.ERROR(f'Certificate file not found: {certfile}')
            )
            return
        
        if not os.path.exists(keyfile):
            self.stdout.write(
                self.style.ERROR(f'Private key file not found: {keyfile}')
            )
            return
        
        # Parse address and port
        if ':' in addrport:
            addr, port = addrport.split(':', 1)
            port = int(port)
        else:
            addr = '127.0.0.1'
            port = int(addrport)
        
        self.stdout.write(
            self.style.SUCCESS(f'Starting SSL server on https://{addr}:{port}')
        )
        self.stdout.write(f'Certificate: {certfile}')
        self.stdout.write(f'Private Key: {keyfile}')
        
        try:
            # Create SSL server
            server = SSLWSGIServer(
                (addr, port),
                self.get_handler(),
                certfile,
                keyfile
            )
            
            # Set WSGI application
            server.set_app(get_wsgi_application())
            
            self.stdout.write(
                self.style.SUCCESS('SSL server started successfully!')
            )
            self.stdout.write('Press Ctrl+C to stop the server')
            
            # Start server
            server.serve_forever()
            
        except KeyboardInterrupt:
            self.stdout.write('\nServer stopped by user')
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error starting SSL server: {e}')
            )
    
    def get_handler(self):
        """Get the request handler class"""
        from django.core.servers.basehttp import WSGIRequestHandler
        return WSGIRequestHandler 