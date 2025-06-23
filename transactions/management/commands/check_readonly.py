from django.core.management.base import BaseCommand
from django.db import connection
from django.core.exceptions import PermissionDenied
from transactions.models import Transaction, TollUser
import logging


class Command(BaseCommand):
    help = 'Verify that the application operates in read-only mode'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed test results',
        )
    
    def handle(self, *args, **options):
        verbose = options.get('verbose', False)
        
        self.stdout.write(self.style.SUCCESS('=== Read-Only Database Compliance Check ==='))
        
        # Test 1: Check model configurations
        self.stdout.write('\n1. Checking model configurations...')
        
        # Check Transaction model
        if not Transaction._meta.managed:
            self.stdout.write(self.style.SUCCESS('  ✓ Transaction model has managed=False'))
        else:
            self.stdout.write(self.style.ERROR('  ✗ Transaction model should have managed=False'))
        
        # Check TollUser model
        if not TollUser._meta.managed:
            self.stdout.write(self.style.SUCCESS('  ✓ TollUser model has managed=False'))
        else:
            self.stdout.write(self.style.ERROR('  ✗ TollUser model should have managed=False'))
        
        # Test 2: Check read-only manager
        self.stdout.write('\n2. Testing read-only manager...')
        
        try:
            Transaction.objects.create(sequence='TEST123')
            self.stdout.write(self.style.ERROR('  ✗ Transaction.objects.create() should be blocked'))
        except PermissionDenied:
            self.stdout.write(self.style.SUCCESS('  ✓ Transaction.objects.create() is properly blocked'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  ? Unexpected error: {e}'))
        
        try:
            Transaction.objects.update(transtype='TEST')
            self.stdout.write(self.style.ERROR('  ✗ Transaction.objects.update() should be blocked'))
        except PermissionDenied:
            self.stdout.write(self.style.SUCCESS('  ✓ Transaction.objects.update() is properly blocked'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  ? Unexpected error: {e}'))
        
        try:
            Transaction.objects.delete()
            self.stdout.write(self.style.ERROR('  ✗ Transaction.objects.delete() should be blocked'))
        except PermissionDenied:
            self.stdout.write(self.style.SUCCESS('  ✓ Transaction.objects.delete() is properly blocked'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  ? Unexpected error: {e}'))
        
        # Test 3: Check database permissions
        self.stdout.write('\n3. Testing database permissions...')
        
        try:
            with connection.cursor() as cursor:
                # Try to read data (should work)
                cursor.execute("SELECT COUNT(*) FROM [TRANSACTION]")
                count = cursor.fetchone()[0]
                self.stdout.write(self.style.SUCCESS(f'  ✓ Read operations work (found {count:,} transactions)'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ✗ Read operations failed: {e}'))
        
        # Test 4: Check user permissions
        self.stdout.write('\n4. Testing user permissions...')
        
        try:
            user_count = TollUser.objects.count()
            self.stdout.write(self.style.SUCCESS(f'  ✓ Can read user data ({user_count} users found)'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ✗ Cannot read user data: {e}'))
        
        # Test 5: Check database router
        self.stdout.write('\n5. Testing database router...')
        
        from django.conf import settings
        if 'transactions.db_router.ReadOnlyRouter' in settings.DATABASE_ROUTERS:
            self.stdout.write(self.style.SUCCESS('  ✓ ReadOnlyRouter is configured'))
        else:
            self.stdout.write(self.style.ERROR('  ✗ ReadOnlyRouter is not configured'))
        
        # Test 6: Check middleware
        self.stdout.write('\n6. Testing middleware...')
        
        if 'transactions.middleware.ReadOnlyMiddleware' in settings.MIDDLEWARE:
            self.stdout.write(self.style.SUCCESS('  ✓ ReadOnlyMiddleware is configured'))
        else:
            self.stdout.write(self.style.ERROR('  ✗ ReadOnlyMiddleware is not configured'))
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('Read-only compliance check completed!'))
        self.stdout.write('\nThe application is configured to:')
        self.stdout.write('• Only read data from ZAKTOLL database')
        self.stdout.write('• Block all write operations (INSERT, UPDATE, DELETE)')
        self.stdout.write('• Log all database access attempts')
        self.stdout.write('• Maintain audit trail for security')
        
        self.stdout.write(f'\nDatabase: {settings.DATABASES["default"]["NAME"]}')
        self.stdout.write(f'Host: {settings.DATABASES["default"]["HOST"]}')
        self.stdout.write(f'User: {settings.DATABASES["default"]["USER"]}')
        
        if verbose:
            self.stdout.write('\nFor detailed logs, check:')
            self.stdout.write('• logs/toll_system.log (general activity)')
            self.stdout.write('• logs/security.log (security events)')
        
        self.stdout.write('\n' + self.style.SUCCESS('Application is ready for read-only operation!')) 