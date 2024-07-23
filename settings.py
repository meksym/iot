from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / 'logs'

DB_HOST = 'localhost'
DB_NAME = 'iot'
DB_USER = 'application'
DB_PASSWORD = 'ConoRuBREsTi'

HTTP_HOST = '0.0.0.0'
HTTP_PORT = 8080

LOGGING_CONFIG = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
        },
        'access_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOG_DIR / 'access.log'),
            'level': 'INFO',
            'maxBytes': 1048576,  # 1 MB
            'backupCount': 5,
        },
        'server_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOG_DIR / 'server.log'),
            'level': 'INFO',
            'maxBytes': 1048576,  # 1 MB
            'backupCount': 5,
        },
    },
    'loggers': {
        'aiohttp.access': {
            'handlers': ['console', 'access_file'],
            'level': 'INFO',
            'propagate': False
        },
        'aiohttp.server': {
            'handlers': ['console', 'server_file'],
            'level': 'INFO',
            'propagate': False
        },
    }
}


if not LOG_DIR.exists():
    LOG_DIR.mkdir()
