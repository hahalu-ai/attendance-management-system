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
            "DB_HOST": os.getenv('DB_HOST', 'NOT SET'),
            "DB_PORT": os.getenv('DB_PORT', 'NOT SET'),
            "DB_NAME": os.getenv('DB_NAME', 'NOT SET'),
            "DB_USER": os.getenv('DB_USER', 'NOT SET'),
            "DB_PASSWORD": "***" if os.getenv('DB_PASSWORD') else 'NOT SET',
            "PORT": os.getenv('PORT', 'NOT SET'),
            "HOST": os.getenv('HOST', 'NOT SET')
        }), 200

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
