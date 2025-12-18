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
    user_level = data.get('user_level', 'Contractor')

    if not all([username, display_name, email, password]):
        return jsonify({"error": "All fields are required"}), 400

    if user_level not in ['Manager', 'Contractor']:
        return jsonify({"error": "Invalid user level"}), 400

    try:
        # Hash the password
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
