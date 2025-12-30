import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""

    # Database configuration
    # Support both custom DB_* variables and Railway's MYSQL* variables
    DB_HOST = os.getenv('DB_HOST') or os.getenv('MYSQLHOST') or os.getenv('MYSQL_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT') or os.getenv('MYSQLPORT') or os.getenv('MYSQL_PORT', '3306'))
    DB_USER = os.getenv('DB_USER') or os.getenv('MYSQLUSER') or os.getenv('MYSQL_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD') or os.getenv('MYSQLPASSWORD') or os.getenv('MYSQL_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME') or os.getenv('MYSQLDATABASE') or os.getenv('MYSQL_DATABASE', 'attendance_system')

    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    PORT = int(os.getenv('PORT', 5001))
    HOST = os.getenv('HOST', '0.0.0.0')

    # CORS configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')

    @staticmethod
    def get_db_config():
        """Returns database configuration as dictionary"""
        return {
            'host': Config.DB_HOST,
            'port': Config.DB_PORT,
            'user': Config.DB_USER,
            'password': Config.DB_PASSWORD,
            'database': Config.DB_NAME
        }
