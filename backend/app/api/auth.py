from flask import Blueprint, request, jsonify
from ..models.database import execute_query, get_connection
import hashlib

auth_bp = Blueprint('auth', __name__)

def hash_password(password):
    """Simple password hashing (use bcrypt in production)"""
    return hashlib.sha256(password.encode()).hexdigest()

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    try:
        # Hash the password
        hashed_password = hash_password(password)

        # Query user
        query = """
            SELECT id, username, display_name, email, user_level
            FROM users
            WHERE username = %s AND password = %s
        """
        user = execute_query(query, (username, hashed_password), fetch_one=True)

        if not user:
            return jsonify({"error": "Invalid credentials"}), 401

        # Prevent Members from logging in (they only use QR codes)
        if user['user_level'] == 'Member':
            return jsonify({"error": "Members cannot log in. Please use QR code check-in."}), 403

        return jsonify({
            "message": "Login successful",
            "user": user
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    """User registration endpoint"""
    data = request.get_json() or {}
    username = data.get('username')
    display_name = data.get('display_name')
    email = data.get('email')
    password = data.get('password')
    user_level = data.get('user_level', 'Lead')

    # Members don't need passwords (QR code only access)
    # Manager and Lead require passwords
    if user_level in ['Manager', 'Lead']:
        if not all([username, display_name, email, password]):
            return jsonify({"error": "All fields are required for Manager and Lead"}), 400
    else:  # Member
        if not all([username, display_name, email]):
            return jsonify({"error": "username, display_name, and email are required for Members"}), 400

    if user_level not in ['Manager', 'Lead', 'Member']:
        return jsonify({"error": "Invalid user level"}), 400

    try:
        # Hash the password (or use empty string for Members)
        if user_level == 'Member' or not password:
            # Members don't have passwords - they only use QR codes
            hashed_password = ''
        else:
            hashed_password = hash_password(password)

        # Insert new user
        query = """
            INSERT INTO users (username, display_name, email, password, user_level)
            VALUES (%s, %s, %s, %s, %s)
        """
        user_id = execute_query(
            query,
            (username, display_name, email, hashed_password, user_level),
            commit=True
        )

        return jsonify({
            "message": "User registered successfully",
            "user_id": user_id,
            "username": username
        }), 201

    except Exception as e:
        if "Duplicate entry" in str(e):
            return jsonify({"error": "Username or email already exists"}), 409
        return jsonify({"error": str(e)}), 500
