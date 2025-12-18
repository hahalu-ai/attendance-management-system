from flask import Blueprint, request, jsonify
from ..models.database import execute_query, get_connection

users_bp = Blueprint('users', __name__)

@users_bp.route('/<username>', methods=['GET'])
def get_user(username):
    """Get user information by username"""
    try:
        query = """
            SELECT id, username, display_name, email, user_level, created_at
            FROM users
            WHERE username = %s
        """
        user = execute_query(query, (username,), fetch_one=True)

        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify(user), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_bp.route('/<username>/manager', methods=['GET'])
def get_user_manager(username):
    """Get the manager for a contractor"""
    try:
        query = """
            SELECT u.username, u.display_name, u.email, u.user_level
            FROM users u
            JOIN manager_assignments ma ON u.username = ma.manager_username
            WHERE ma.contractor_username = %s
        """
        manager = execute_query(query, (username,), fetch_one=True)

        if not manager:
            return jsonify({"error": "No manager assigned"}), 404

        return jsonify(manager), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_bp.route('/<username>/contractors', methods=['GET'])
def get_manager_contractors(username):
    """Get all contractors for a manager"""
    try:
        # Verify the user is a manager
        user_query = "SELECT user_level FROM users WHERE username = %s"
        user = execute_query(user_query, (username,), fetch_one=True)

        if not user or user['user_level'] != 'Manager':
            return jsonify({"error": "User is not a manager"}), 403

        # Get contractors
        query = """
            SELECT u.username, u.display_name, u.email, ma.assigned_at
            FROM users u
            JOIN manager_assignments ma ON u.username = ma.contractor_username
            WHERE ma.manager_username = %s
            ORDER BY u.display_name
        """
        contractors = execute_query(query, (username,), fetch_all=True)

        return jsonify({"contractors": contractors}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_bp.route('/assign-manager', methods=['POST'])
def assign_manager():
    """Assign a contractor to a manager"""
    data = request.get_json() or {}
    manager_username = data.get('manager_username')
    contractor_username = data.get('contractor_username')

    if not manager_username or not contractor_username:
        return jsonify({"error": "Both manager_username and contractor_username are required"}), 400

    try:
        # Verify manager exists and is a manager
        manager_query = "SELECT user_level FROM users WHERE username = %s"
        manager = execute_query(manager_query, (manager_username,), fetch_one=True)

        if not manager or manager['user_level'] != 'Manager':
            return jsonify({"error": "Invalid manager username"}), 400

        # Verify contractor exists and is a contractor
        contractor_query = "SELECT user_level FROM users WHERE username = %s"
        contractor = execute_query(contractor_query, (contractor_username,), fetch_one=True)

        if not contractor or contractor['user_level'] != 'Contractor':
            return jsonify({"error": "Invalid contractor username"}), 400

        # Create assignment
        insert_query = """
            INSERT INTO manager_assignments (manager_username, contractor_username)
            VALUES (%s, %s)
        """
        execute_query(insert_query, (manager_username, contractor_username), commit=True)

        return jsonify({"message": "Manager assigned successfully"}), 201

    except Exception as e:
        if "Duplicate entry" in str(e):
            return jsonify({"error": "Assignment already exists"}), 409
        return jsonify({"error": str(e)}), 500
