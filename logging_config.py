import os

# Django Logging Configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {asctime} {message}',
            'style': '{',
        },
        'detailed': {
            'format': '[{levelname}] {asctime} {name} {pathname}:{lineno} {funcName} {message}',
            'style': '{',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'django_file': {
            'class': 'logging.FileHandler',
            'filename': 'logs/django/django.log',
            'formatter': 'verbose',
        },
        'db_file': {
            'class': 'logging.FileHandler', 
            'filename': 'logs/database/database.log',
            'formatter': 'detailed',
        },
        'auth_file': {
            'class': 'logging.FileHandler',
            'filename': 'logs/auth/authentication.log', 
            'formatter': 'detailed',
        },
        'ssl_file': {
            'class': 'logging.FileHandler',
            'filename': 'logs/ssl/ssl_connections.log',
            'formatter': 'verbose',
        },
        'debug_file': {
            'class': 'logging.FileHandler',
            'filename': 'logs/debug/debug.log',
            'formatter': 'detailed',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'django_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['db_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.contrib.auth': {
            'handlers': ['auth_file'],
            'level': 'DEBUG', 
            'propagate': False,
        },
        'django.security': {
            'handlers': ['auth_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'transactions': {
            'handlers': ['console', 'django_file', 'debug_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'ssl': {
            'handlers': ['ssl_file'],
            'level': 'DEBUG',
            'propagate': False,
        }
    },
    'root': {
        'handlers': ['console', 'debug_file'],
        'level': 'DEBUG',
    }
}
