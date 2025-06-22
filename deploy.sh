#!/bin/bash

# Django Toll Report System Deployment Script

echo "=== Django Toll Report System Deployment ==="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "Installing Python packages..."
pip install -r requirements.txt

# Check Django configuration
echo "Checking Django configuration..."
python manage.py check

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser (optional - comment out if not needed)
echo "To create a superuser account, run: python manage.py createsuperuser"

# Start development server
echo "Starting Django development server..."
echo "Access the application at: http://115.127.158.188:8000"
echo "Admin interface at: http://115.127.158.188:8000/admin/"
echo ""
echo "Press Ctrl+C to stop the server"

python manage.py runserver 0.0.0.0:8000 