# Toll Report System (Django)

This is a Django-based toll transaction reporting system converted from a Laravel application. It provides comprehensive toll transaction reporting and management capabilities for the Shaheed Wasim Akram Expressway.

## Features

- **Transaction Reporting**: View detailed transaction records with filtering options
- **Daily Reports**: Generate reports based on date and time ranges
- **Lane-wise Analysis**: Filter transactions by specific lanes, vehicle types, and payment methods
- **Revenue Summary**: Analyze revenue data by lane and vehicle class (Cash only)
- **Traffic Analysis**: Review traffic patterns and exempt transactions
- **PDF Export**: Generate PDF reports of transaction data
- **Image Display**: View vehicle images associated with transactions

## Database Configuration

This application connects to an MSSQL database containing the TRANSACTION table/view.

### Database Connection Details:
- **Host**: 115.127.158.186
- **Port**: 1433
- **Driver**: ODBC Driver 17 for SQL Server

## Installation & Setup

### 1. Prerequisites

- Python 3.8 or higher
- ODBC Driver 17 for SQL Server
- Access to the MSSQL database

### 2. Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Configuration

Create a `.env` file in the project root with your database credentials:

```env
# Database Configuration
DB_NAME=your_database_name
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=115.127.158.186
DB_PORT=1433

# Django Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True
```

Update the `DATABASES` configuration in `toll_system/settings.py` to use your credentials.

### 4. Run the Application

```bash
# Create superuser for admin access
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Run the development server
python manage.py runserver 0.0.0.0:8000
```

The application will be available at: `http://localhost:8000`

## Application Structure

```
toll_report/
├── toll_system/           # Main Django project
│   ├── settings.py        # Project settings
│   ├── urls.py           # Main URL configuration
│   └── wsgi.py           # WSGI configuration
├── transactions/          # Main application
│   ├── models.py         # Transaction model
│   ├── views.py          # Business logic (converted from Laravel Controller)
│   ├── urls.py           # URL routing
│   └── admin.py          # Admin interface configuration
├── templates/            # HTML templates
│   ├── base.html         # Base template with navigation
│   └── transactions/     # Transaction-specific templates
├── static/               # Static files (CSS, JS, images)
└── requirements.txt      # Python dependencies
```

## Features Overview

### 1. Overview Page (`/`)
- Main dashboard with navigation to different reports
- Quick access to key features

### 2. Transaction Details (`/report_date/`)
- Form to select date and time range
- Generates detailed transaction reports

### 3. Selected Transaction Details (`/report_date_lane/`)
- Advanced filtering by lane, vehicle type, and payment method
- Supports all filtering combinations

### 4. Revenue Summary (`/summary_brief/`)
- Lane-wise revenue analysis (Cash transactions only)
- Aggregated data by lane

### 5. Traffic Summary (`/summary_detail/`)
- Lane-wise traffic analysis (Cash transactions only)
- Includes transaction counts and revenue

### 6. Exempt Traffic Summary (`/exempt_detail/`)
- Analysis of exempt transactions
- Lane-wise exempt transaction reporting

## Database Schema

The application uses the existing `TRANSACTION` table/view with the following key fields:

- `PLAZAID`: Plaza identifier
- `PLAZANAME`: Plaza name
- `LANE`: Lane identifier
- `SEQUENCE`: Transaction sequence number
- `COLLECTORID`: Collector identifier
- `CAPTUREDATE`: Transaction timestamp
- `TRANSTYPE`: Transaction type
- `CLASS`: Vehicle class
- `REGNUMBER`: Vehicle registration number
- `FARE`: Transaction amount
- `PAYTYPE`: Payment type (CSH, VCH, ETC, TnG)
- `PIC`: Vehicle image (binary data)

## API Endpoints

- `/api/image/<transaction_id>/`: Get vehicle image for a specific transaction

## Admin Interface

Access the Django admin at `/admin/` to:
- View transaction records
- Filter and search transactions
- Export data (read-only access)

## Deployment Notes

1. **Production Settings**: Update `DEBUG = False` and configure `ALLOWED_HOSTS`
2. **Static Files**: Configure a web server (nginx/Apache) to serve static files
3. **Database**: Ensure MSSQL server connectivity and proper firewall rules
4. **Security**: Use environment variables for sensitive configuration

## Original Laravel to Django Conversion

This application was converted from a Laravel-based system with the following mappings:

- **Laravel Controllers** → **Django Views**
- **Blade Templates** → **Django Templates**
- **Laravel Routes** → **Django URL patterns**
- **Eloquent Models** → **Django Models**

## Support

For technical support or questions about the toll system, contact the system administrator.

## License

This project is proprietary software for toll road operations. 