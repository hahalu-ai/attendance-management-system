#!/usr/bin/env python3
"""
Attendance Management System - Backend Server
Run this file to start the Flask application
"""

from app import create_app
from app.config import Config

app = create_app()

if __name__ == '__main__':
    print(f"""
    ╔══════════════════════════════════════════════════════╗
    ║   Attendance Management System - Backend Server     ║
    ╠══════════════════════════════════════════════════════╣
    ║   Server running on: http://{Config.HOST}:{Config.PORT}      ║
    ║   Database: {Config.DB_NAME}                           ║
    ║   Debug Mode: {Config.DEBUG}                              ║
    ╚══════════════════════════════════════════════════════╝
    """)

    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
