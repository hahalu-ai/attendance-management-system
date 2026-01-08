from flask import Blueprint, request, jsonify
from ..models.database import execute_query, get_connection
import hashlib

users_bp = Blueprint('users', __name__)

def hash_password(password):
    """Simple password hashing (use bcrypt in production)"""
    return hashlib.sha256(password.encode()).hexdigest()

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

@users_bp.route('/', methods=['GET'])
def list_users():
    """List all users - Manager only"""
    manager_username = request.args.get('manager_username')

    if not manager_username:
        return jsonify({"error": "manager_username parameter is required"}), 400

    try:
        # Verify the requester is a manager
        manager_query = "SELECT user_level FROM users WHERE username = %s"
        manager = execute_query(manager_query, (manager_username,), fetch_one=True)

        if not manager or manager['user_level'] != 'Manager':
            return jsonify({"error": "Only managers can list users"}), 403

        # Get all users
        query = """
            SELECT id, username, display_name, email, user_level, created_at
            FROM users
            ORDER BY created_at DESC
        """
        users = execute_query(query, fetch_all=True)

        return jsonify({"users": users}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_bp.route('/', methods=['POST'])
def create_user():
    """Create a new user - Manager only"""
    data = request.get_json() or {}
    manager_username = data.get('manager_username')
    username = data.get('username')
    display_name = data.get('display_name')
    email = data.get('email')
    password = data.get('password')
    user_level = data.get('user_level', 'Contractor')

    if not all([manager_username, username, display_name, email, password]):
        return jsonify({"error": "manager_username, username, display_name, email, and password are required"}), 400

    if user_level not in ['Manager', 'Contractor']:
        return jsonify({"error": "user_level must be 'Manager' or 'Contractor'"}), 400

    try:
        # Verify the requester is a manager
        manager_query = "SELECT user_level FROM users WHERE username = %s"
        manager = execute_query(manager_query, (manager_username,), fetch_one=True)

        if not manager or manager['user_level'] != 'Manager':
            return jsonify({"error": "Only managers can create users"}), 403

        # Hash the password
        hashed_password = hash_password(password)

        # Insert new user
        insert_query = """
            INSERT INTO users (username, display_name, email, password, user_level)
            VALUES (%s, %s, %s, %s, %s)
        """
        user_id = execute_query(
            insert_query,
            (username, display_name, email, hashed_password, user_level),
            commit=True
        )

        return jsonify({
            "message": "User created successfully",
            "user_id": user_id,
            "username": username
        }), 201

    except Exception as e:
        if "Duplicate entry" in str(e):
            return jsonify({"error": "Username or email already exists"}), 409
        return jsonify({"error": str(e)}), 500

@users_bp.route('/<username>', methods=['DELETE'])
def delete_user(username):
    """Delete a user - Manager only"""
    data = request.get_json() or {}
    manager_username = data.get('manager_username')

    if not manager_username:
        return jsonify({"error": "manager_username is required"}), 400

    try:
        # Verify the requester is a manager
        manager_query = "SELECT user_level FROM users WHERE username = %s"
        manager = execute_query(manager_query, (manager_username,), fetch_one=True)

        if not manager or manager['user_level'] != 'Manager':
            return jsonify({"error": "Only managers can delete users"}), 403

        # Prevent deleting yourself
        if manager_username == username:
            return jsonify({"error": "You cannot delete your own account"}), 400

        # Check if user exists
        user_query = "SELECT username FROM users WHERE username = %s"
        user = execute_query(user_query, (username,), fetch_one=True)

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Delete user (CASCADE will handle related records)
        delete_query = "DELETE FROM users WHERE username = %s"
        execute_query(delete_query, (username,), commit=True)

        return jsonify({"message": f"User {username} deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_bp.route('/<username>/self-delete', methods=['DELETE'])
def self_delete_account(username):
    """Self-service account deletion - User deletes their own account"""
    data = request.get_json() or {}
    password = data.get('password')

    if not password:
        return jsonify({"error": "Password is required for account deletion"}), 400

    try:
        # Verify password
        hashed_password = hash_password(password)
        verify_query = """
            SELECT username, user_level FROM users
            WHERE username = %s AND password = %s
        """
        user = execute_query(verify_query, (username, hashed_password), fetch_one=True)

        if not user:
            return jsonify({"error": "Invalid password"}), 401

        # Check for pending time entries (business logic validation)
        pending_query = """
            SELECT COUNT(*) as pending_count FROM time_entries
            WHERE username = %s AND status = 'Pending'
        """
        pending = execute_query(pending_query, (username,), fetch_one=True)

        if pending and pending['pending_count'] > 0:
            return jsonify({
                "error": "Cannot delete account with pending time entries. Please wait for manager approval or contact your manager.",
                "pending_entries": pending['pending_count']
            }), 400

        # For managers, check if they have contractors assigned
        if user['user_level'] == 'Manager':
            contractor_query = """
                SELECT COUNT(*) as contractor_count FROM manager_assignments
                WHERE manager_username = %s
            """
            contractors = execute_query(contractor_query, (username,), fetch_one=True)

            if contractors and contractors['contractor_count'] > 0:
                return jsonify({
                    "error": "Cannot delete account while contractors are assigned to you. Please reassign them first.",
                    "assigned_contractors": contractors['contractor_count']
                }), 400

        # Delete user (CASCADE will handle related records)
        delete_query = "DELETE FROM users WHERE username = %s"
        execute_query(delete_query, (username,), commit=True)

        return jsonify({
            "message": f"Account {username} deleted successfully",
            "username": username
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_bp.route('/<username>/change-password', methods=['PUT'])
def change_password(username):
    """Change user password - User can change their own password"""
    data = request.get_json() or {}
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not old_password or not new_password:
        return jsonify({"error": "Both old_password and new_password are required"}), 400

    if len(new_password) < 6:
        return jsonify({"error": "New password must be at least 6 characters"}), 400

    try:
        # Verify old password
        hashed_old_password = hash_password(old_password)
        verify_query = """
            SELECT username FROM users
            WHERE username = %s AND password = %s
        """
        user = execute_query(verify_query, (username, hashed_old_password), fetch_one=True)

        if not user:
            return jsonify({"error": "Current password is incorrect"}), 401

        # Update to new password
        hashed_new_password = hash_password(new_password)
        update_query = "UPDATE users SET password = %s WHERE username = %s"
        execute_query(update_query, (hashed_new_password, username), commit=True)

        return jsonify({
            "message": "Password changed successfully",
            "username": username
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_bp.route('/<username>/role', methods=['PUT'])
def update_user_role(username):
    """Update a user's role - Manager only"""
    data = request.get_json() or {}
    manager_username = data.get('manager_username')
    new_role = data.get('user_level')

    if not manager_username or not new_role:
        return jsonify({"error": "manager_username and user_level are required"}), 400

    if new_role not in ['Manager', 'Contractor']:
        return jsonify({"error": "user_level must be 'Manager' or 'Contractor'"}), 400

    try:
        # Verify the requester is a manager
        manager_query = "SELECT user_level FROM users WHERE username = %s"
        manager = execute_query(manager_query, (manager_username,), fetch_one=True)

        if not manager or manager['user_level'] != 'Manager':
            return jsonify({"error": "Only managers can update user roles"}), 403

        # Prevent changing your own role
        if manager_username == username:
            return jsonify({"error": "You cannot change your own role"}), 400

        # Check if user exists
        user_query = "SELECT username, user_level FROM users WHERE username = %s"
        user = execute_query(user_query, (username,), fetch_one=True)

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Update user role
        update_query = "UPDATE users SET user_level = %s WHERE username = %s"
        execute_query(update_query, (new_role, username), commit=True)

        return jsonify({
            "message": f"User {username} role updated to {new_role}",
            "username": username,
            "new_role": new_role
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
