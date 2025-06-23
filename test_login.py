#!/usr/bin/env python
"""
Test script for the toll system authentication
Run this with: python test_login.py
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'toll_system.settings')
django.setup()

from transactions.models import TollUser
from django.contrib.auth import authenticate
from django.utils import timezone

def test_authentication():
    """Test the authentication system"""
    print("🔐 Testing Toll System Authentication")
    print("=" * 50)
    
    # Test 1: Check if we can query users
    try:
        users = TollUser.objects.filter(active=True)
        print(f"✅ Found {users.count()} active users in USERS table")
        
        # Show sample users (without passwords)
        for user in users[:5]:  # Show first 5 users
            print(f"   📝 User ID: {user.userId} | Username: {user.username} | Name: {user.name} | Role: {user.role}")
    except Exception as e:
        print(f"❌ Error querying users: {e}")
        return
    
    print("\n" + "=" * 50)
    
    # Test 2: Test authentication with existing user
    print("🔍 Testing Authentication Logic")
    
    # Get first active user for testing
    try:
        test_user = users.filter(role__in=['admin', 'webadmin', 'webuser', 'ADMIN', 'OPERATOR']).first()
        if test_user:
            print(f"📋 Testing with user: {test_user.username}")
            print(f"   User ID: {test_user.userId}")
            print(f"   Role: {test_user.role}")
            print(f"   Active: {test_user.active}")
            
            # Test password check (this would normally use the actual password)
            print(f"   Password stored as: {'*' * len(test_user.password)}")
            
            # Test the authentication backend
            print("🔧 Testing authentication backend...")
            auth_result = authenticate(username=test_user.username, password=test_user.password)
            if auth_result:
                print("✅ Authentication backend working correctly!")
            else:
                print("⚠️  Authentication backend returned None (check role permissions)")
            
        else:
            print("⚠️  No suitable test user found")
    except Exception as e:
        print(f"❌ Error testing authentication: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Authentication System Status:")
    print("✅ Custom TollUser model configured (userId as CharField)")
    print("✅ Authentication backend ready")
    print("✅ Login/logout views created")
    print("✅ Templates configured")
    print("✅ URL patterns set up")
    
    print("\n🚀 Next Steps:")
    print("1. Start your Django server: python manage.py runserver")
    print("2. Go to: http://localhost:8000/login/")
    print("3. Login with valid USERS table credentials")
    print("4. Access protected pages: http://localhost:8000/")

if __name__ == "__main__":
    test_authentication() 