from flask import Flask, send_from_directory, jsonify
from .config import Config
import os

def create_app():
    """Application factory pattern"""
    app = Flask(__name__, static_folder='../../frontend')
    app.config.from_object(Config)

    # Add health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({
            "status": "ok",
            "message": "Application is running"
        }), 200

    # Add debug endpoint to check configuration
    @app.route('/debug-config')
    def debug_config():
        import os
        return jsonify({
            "variables_found": {
                "DB_HOST": os.getenv('DB_HOST', 'NOT SET'),
                "DB_PORT": os.getenv('DB_PORT', 'NOT SET'),
                "DB_NAME": os.getenv('DB_NAME', 'NOT SET'),
                "DB_USER": os.getenv('DB_USER', 'NOT SET'),
                "DB_PASSWORD": "***" if os.getenv('DB_PASSWORD') else 'NOT SET',
                "MYSQLHOST": os.getenv('MYSQLHOST', 'NOT SET'),
                "MYSQLPORT": os.getenv('MYSQLPORT', 'NOT SET'),
                "MYSQLDATABASE": os.getenv('MYSQLDATABASE', 'NOT SET'),
                "MYSQLUSER": os.getenv('MYSQLUSER', 'NOT SET'),
                "MYSQLPASSWORD": "***" if os.getenv('MYSQLPASSWORD') else 'NOT SET',
                "MYSQL_HOST": os.getenv('MYSQL_HOST', 'NOT SET'),
                "MYSQL_PORT": os.getenv('MYSQL_PORT', 'NOT SET'),
                "MYSQL_DATABASE": os.getenv('MYSQL_DATABASE', 'NOT SET'),
                "MYSQL_USER": os.getenv('MYSQL_USER', 'NOT SET'),
                "MYSQL_PASSWORD": "***" if os.getenv('MYSQL_PASSWORD') else 'NOT SET',
            },
            "config_values_used": {
                "DB_HOST": Config.DB_HOST,
                "DB_PORT": Config.DB_PORT,
                "DB_NAME": Config.DB_NAME,
                "DB_USER": Config.DB_USER,
                "DB_PASSWORD": "***" if Config.DB_PASSWORD else 'NOT SET',
            },
            "app_config": {
                "PORT": os.getenv('PORT', 'NOT SET'),
                "HOST": os.getenv('HOST', 'NOT SET'),
                "DEBUG": os.getenv('DEBUG', 'NOT SET')
            }
        }), 200

    # Database connection test endpoint
    @app.route('/test-db')
    def test_db():
        try:
            import mysql.connector
            from .config import Config

            # Show what we're trying to connect to
            connection_info = {
                "host": Config.DB_HOST,
                "port": Config.DB_PORT,
                "user": Config.DB_USER,
                "database": Config.DB_NAME,
                "password_set": bool(Config.DB_PASSWORD)
            }

            # Try to connect
            conn = mysql.connector.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME
            )

            # Try a simple query
            cursor = conn.cursor()
            cursor.execute("SELECT DATABASE(), VERSION()")
            db_name, version = cursor.fetchone()
            cursor.close()
            conn.close()

            return jsonify({
                "status": "success",
                "message": "Database connection successful!",
                "connection_info": connection_info,
                "database": db_name,
                "mysql_version": version
            }), 200

        except mysql.connector.Error as err:
            return jsonify({
                "status": "error",
                "message": str(err),
                "error_code": err.errno if hasattr(err, 'errno') else None,
                "connection_info": connection_info
            }), 500
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Unexpected error: {str(e)}",
                "type": type(e).__name__
            }), 500

    # Register blueprints
    from .api.auth import auth_bp
    from .api.users import users_bp
    from .api.attendance import attendance_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(attendance_bp, url_prefix='/api/attendance')

    # Enable CORS
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', Config.CORS_ORIGINS)
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response

    # Frontend routes
    frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'frontend')

    @app.route('/')
    def index():
        return send_from_directory(frontend_dir, 'index.html')

    @app.route('/<path:path>')
    def serve_frontend(path):
        # Don't serve frontend for API routes
        if path.startswith('api/'):
            return {"error": "Not found"}, 404

        if os.path.exists(os.path.join(frontend_dir, path)):
            return send_from_directory(frontend_dir, path)
        return {"error": "Not found"}, 404

    return app
