import os

class Config:
    """
    Centralized Configuration for School Lost & Found Application.
    Designed for Class 12 CBSE Computer Science (083) Project.
    """
    # Flask Session Security Key
    SECRET_KEY = os.environ.get('SECRET_KEY', 'cbse-class12-cs-lost-found-secret-key-2026')

    # MySQL Database Connection Parameters
    MYSQL_HOST = os.environ.get('MYSQL_HOST', '127.0.0.1')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'Manvik@2020')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'school_lost_found')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))

    # Application Settings
    APP_NAME = "School Lost & Found"
    ADMIN_EMAIL = "admin@school.local"
    ADMIN_DEFAULT_PASSWORD = "Admin@123"

    # Server & Port Settings (Local School Lab / Workstation)
    PORT = int(os.environ.get('PORT', 5000))
    HOST = os.environ.get('HOST', '127.0.0.1')

    # Database Mode ('mysql' primary for CBSE 083, or 'sqlite' fallback)
    DB_MODE = os.environ.get('DB_MODE', 'mysql').lower()
    SQLITE_PATH = os.environ.get('SQLITE_PATH', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'school_lost_found.db'))
