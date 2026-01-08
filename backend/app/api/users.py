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

# =============================================
# Manager Endpoints
# =============================================

@users_bp.route('/manager/<username>/leads', methods=['GET'])
def get_manager_leads(username):
    """Get all Leads managed by a Manager (or all Leads if super-user)"""
    try:
        # Verify the user is a Manager
        user_query = "SELECT user_level FROM users WHERE username = %s"
        user = execute_query(user_query, (username,), fetch_one=True)

        if not user or user['user_level'] != 'Manager':
            return jsonify({"error": "User is not a Manager"}), 403

        # Managers see ALL Leads (super-user access)
        query = """
            SELECT u.username, u.display_name, u.email, u.created_at
            FROM users u
            WHERE u.user_level = 'Lead'
            ORDER BY u.display_name
        """
        leads = execute_query(query, fetch_all=True)

        return jsonify({"leads": leads}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_bp.route('/manager/<username>/all-members', methods=['GET'])
def get_all_members(username):
    """Get all Members across all Leads (Manager only)"""
    try:
        # Verify the user is a Manager
        user_query = "SELECT user_level FROM users WHERE username = %s"
        user = execute_query(user_query, (username,), fetch_one=True)

        if not user or user['user_level'] != 'Manager':
            return jsonify({"error": "User is not a Manager"}), 403

        # Get all Members with their assigned Lead
        query = """
            SELECT u.username, u.display_name, u.email, u.created_at,
                   la.lead_username, lead.display_name as lead_name
            FROM users u
            LEFT JOIN lead_assignments la ON u.username = la.member_username
            LEFT JOIN users lead ON la.lead_username = lead.username
            WHERE u.user_level = 'Member'
            ORDER BY u.display_name
        """
        members = execute_query(query, fetch_all=True)

        return jsonify({"members": members}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =============================================
# Lead Endpoints
# =============================================

@users_bp.route('/lead/<username>/members', methods=['GET'])
def get_lead_members(username):
    """Get all Members assigned to a Lead"""
    try:
        # Verify the user is a Lead
        user_query = "SELECT user_level FROM users WHERE username = %s"
        user = execute_query(user_query, (username,), fetch_one=True)

        if not user or user['user_level'] != 'Lead':
            return jsonify({"error": "User is not a Lead"}), 403

        # Get Members assigned to this Lead
        query = """
            SELECT u.username, u.display_name, u.email, la.assigned_at
            FROM users u
            JOIN lead_assignments la ON u.username = la.member_username
            WHERE la.lead_username = %s
            ORDER BY u.display_name
        """
        members = execute_query(query, (username,), fetch_all=True)

        return jsonify({"members": members}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_bp.route('/lead/<username>/members', methods=['POST'])
def add_member_to_lead(username):
    """Lead adds a new Member to their team"""
    data = request.get_json() or {}
    member_username = data.get('member_username')
    member_display_name = data.get('display_name')
    member_email = data.get('email')

    if not all([member_username, member_display_name, member_email]):
        return jsonify({"error": "member_username, display_name, and email are required"}), 400

    try:
        # Verify the requester is a Lead
        lead_query = "SELECT user_level FROM users WHERE username = %s"
        lead = execute_query(lead_query, (username,), fetch_one=True)

        if not lead or lead['user_level'] != 'Lead':
            return jsonify({"error": "Only Leads can add Members"}), 403

        # Create the Member user (no password needed)
        insert_user_query = """
            INSERT INTO users (username, display_name, email, password, user_level)
            VALUES (%s, %s, %s, '', 'Member')
        """
        user_id = execute_query(
            insert_user_query,
            (member_username, member_display_name, member_email),
            commit=True
        )

        # Assign Member to Lead
        assign_query = """
            INSERT INTO lead_assignments (lead_username, member_username)
            VALUES (%s, %s)
        """
        execute_query(assign_query, (username, member_username), commit=True)

        return jsonify({
            "message": "Member created and assigned successfully",
            "user_id": user_id,
            "member_username": member_username
        }), 201

    except Exception as e:
        if "Duplicate entry" in str(e):
            # Member might already exist, just try to assign
            try:
                assign_query = """
                    INSERT INTO lead_assignments (lead_username, member_username)
                    VALUES (%s, %s)
                """
                execute_query(assign_query, (username, member_username), commit=True)
                return jsonify({
                    "message": "Existing Member assigned successfully",
                    "member_username": member_username
                }), 201
            except Exception as assign_error:
                if "Duplicate entry" in str(assign_error):
                    return jsonify({"error": "Member already assigned to this Lead"}), 409
                return jsonify({"error": str(assign_error)}), 500
        return jsonify({"error": str(e)}), 500

@users_bp.route('/lead/<username>/members/<member_username>', methods=['DELETE'])
def remove_member_from_lead(username, member_username):
    """Lead removes a Member from their team"""
    try:
        # Verify the requester is a Lead
        lead_query = "SELECT user_level FROM users WHERE username = %s"
        lead = execute_query(lead_query, (username,), fetch_one=True)

        if not lead or lead['user_level'] != 'Lead':
            return jsonify({"error": "Only Leads can remove Members"}), 403

        # Verify the Member is assigned to this Lead
        check_query = """
            SELECT id FROM lead_assignments
            WHERE lead_username = %s AND member_username = %s
        """
        assignment = execute_query(check_query, (username, member_username), fetch_one=True)

        if not assignment:
            return jsonify({"error": "Member not found in your team"}), 404

        # Remove assignment
        delete_assignment_query = """
            DELETE FROM lead_assignments
            WHERE lead_username = %s AND member_username = %s
        """
        execute_query(delete_assignment_query, (username, member_username), commit=True)

        # Optionally delete the Member user entirely (they're orphaned now)
        # Uncomment this if you want to delete the Member when unassigned:
        # delete_user_query = "DELETE FROM users WHERE username = %s"
        # execute_query(delete_user_query, (member_username,), commit=True)

        return jsonify({
            "message": f"Member {member_username} removed from your team"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =============================================
# Manager User Management Endpoints
# =============================================

@users_bp.route('/', methods=['GET'])
def list_users():
    """List all users - Manager only"""
    manager_username = request.args.get('manager_username')

    if not manager_username:
        return jsonify({"error": "manager_username parameter is required"}), 400

    try:
        # Verify the requester is a Manager
        manager_query = "SELECT user_level FROM users WHERE username = %s"
        manager = execute_query(manager_query, (manager_username,), fetch_one=True)

        if not manager or manager['user_level'] != 'Manager':
            return jsonify({"error": "Only Managers can list users"}), 403

        # Get all users
        query = """
            SELECT id, username, display_name, email, user_level, created_at
            FROM users
            ORDER BY user_level, created_at DESC
        """
        users = execute_query(query, fetch_all=True)

        return jsonify({"users": users}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_bp.route('/', methods=['POST'])
def create_user():
    """Create a new user - Manager creates Leads, Leads create Members"""
    data = request.get_json() or {}
    requester_username = data.get('requester_username')
    username = data.get('username')
    display_name = data.get('display_name')
    email = data.get('email')
    password = data.get('password')
    user_level = data.get('user_level', 'Member')

    if not all([requester_username, username, display_name, email]):
        return jsonify({"error": "requester_username, username, display_name, and email are required"}), 400

    if user_level not in ['Manager', 'Lead', 'Member']:
        return jsonify({"error": "user_level must be 'Manager', 'Lead', or 'Member'"}), 400

    try:
        # Verify the requester's permissions
        requester_query = "SELECT user_level FROM users WHERE username = %s"
        requester = execute_query(requester_query, (requester_username,), fetch_one=True)

        if not requester:
            return jsonify({"error": "Requester not found"}), 404

        # Authorization check
        if requester['user_level'] == 'Manager':
            # Managers can create Leads and Members
            if user_level not in ['Manager', 'Lead', 'Member']:
                return jsonify({"error": "Managers can create Managers, Leads, or Members"}), 403
            # Managers and Leads need passwords
            if user_level in ['Manager', 'Lead'] and not password:
                return jsonify({"error": "Password required for Manager and Lead"}), 400
        elif requester['user_level'] == 'Lead':
            # Leads can only create Members
            if user_level != 'Member':
                return jsonify({"error": "Leads can only create Members"}), 403
        else:
            return jsonify({"error": "Insufficient permissions"}), 403

        # Hash the password (or use empty string for Members)
        if user_level == 'Member' or not password:
            hashed_password = ''
        else:
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

        # If Lead created a Member, auto-assign to that Lead
        if requester['user_level'] == 'Lead' and user_level == 'Member':
            assign_query = """
                INSERT INTO lead_assignments (lead_username, member_username)
                VALUES (%s, %s)
            """
            execute_query(assign_query, (requester_username, username), commit=True)

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
    """Delete a user - Manager only (can delete Leads or Members)"""
    data = request.get_json() or {}
    manager_username = data.get('manager_username')

    if not manager_username:
        return jsonify({"error": "manager_username is required"}), 400

    try:
        # Verify the requester is a Manager
        manager_query = "SELECT user_level FROM users WHERE username = %s"
        manager = execute_query(manager_query, (manager_username,), fetch_one=True)

        if not manager or manager['user_level'] != 'Manager':
            return jsonify({"error": "Only Managers can delete users"}), 403

        # Prevent deleting yourself
        if manager_username == username:
            return jsonify({"error": "You cannot delete your own account"}), 400

        # Check if user exists
        user_query = "SELECT username, user_level FROM users WHERE username = %s"
        user = execute_query(user_query, (username,), fetch_one=True)

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Additional checks for Leads with Members
        if user['user_level'] == 'Lead':
            member_count_query = """
                SELECT COUNT(*) as count FROM lead_assignments
                WHERE lead_username = %s
            """
            member_count = execute_query(member_count_query, (username,), fetch_one=True)
            if member_count and member_count['count'] > 0:
                return jsonify({
                    "error": f"Cannot delete Lead with {member_count['count']} assigned Members. Reassign or remove Members first."
                }), 400

        # Delete user (CASCADE will handle related records)
        delete_query = "DELETE FROM users WHERE username = %s"
        execute_query(delete_query, (username,), commit=True)

        return jsonify({"message": f"User {username} deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =============================================
# Assignment Management
# =============================================

@users_bp.route('/assign-lead-to-manager', methods=['POST'])
def assign_lead_to_manager():
    """Assign a Lead to a Manager (for tracking purposes, Managers see all by default)"""
    data = request.get_json() or {}
    manager_username = data.get('manager_username')
    lead_username = data.get('lead_username')

    if not manager_username or not lead_username:
        return jsonify({"error": "Both manager_username and lead_username are required"}), 400

    try:
        # Verify manager exists and is a Manager
        manager_query = "SELECT user_level FROM users WHERE username = %s"
        manager = execute_query(manager_query, (manager_username,), fetch_one=True)

        if not manager or manager['user_level'] != 'Manager':
            return jsonify({"error": "Invalid Manager username"}), 400

        # Verify lead exists and is a Lead
        lead_query = "SELECT user_level FROM users WHERE username = %s"
        lead = execute_query(lead_query, (lead_username,), fetch_one=True)

        if not lead or lead['user_level'] != 'Lead':
            return jsonify({"error": "Invalid Lead username"}), 400

        # Create assignment
        insert_query = """
            INSERT INTO manager_lead_assignments (manager_username, lead_username)
            VALUES (%s, %s)
        """
        execute_query(insert_query, (manager_username, lead_username), commit=True)

        return jsonify({"message": "Lead assigned to Manager successfully"}), 201

    except Exception as e:
        if "Duplicate entry" in str(e):
            return jsonify({"error": "Assignment already exists"}), 409
        return jsonify({"error": str(e)}), 500

@users_bp.route('/assign-member-to-lead', methods=['POST'])
def assign_member_to_lead():
    """Assign an existing Member to a Lead"""
    data = request.get_json() or {}
    lead_username = data.get('lead_username')
    member_username = data.get('member_username')

    if not lead_username or not member_username:
        return jsonify({"error": "Both lead_username and member_username are required"}), 400

    try:
        # Verify lead exists and is a Lead
        lead_query = "SELECT user_level FROM users WHERE username = %s"
        lead = execute_query(lead_query, (lead_username,), fetch_one=True)

        if not lead or lead['user_level'] != 'Lead':
            return jsonify({"error": "Invalid Lead username"}), 400

        # Verify member exists and is a Member
        member_query = "SELECT user_level FROM users WHERE username = %s"
        member = execute_query(member_query, (member_username,), fetch_one=True)

        if not member or member['user_level'] != 'Member':
            return jsonify({"error": "Invalid Member username"}), 400

        # Members can only be assigned to one Lead
        # Check if already assigned
        existing_query = """
            SELECT lead_username FROM lead_assignments
            WHERE member_username = %s
        """
        existing = execute_query(existing_query, (member_username,), fetch_one=True)

        if existing:
            return jsonify({
                "error": f"Member already assigned to Lead: {existing['lead_username']}"
            }), 400

        # Create assignment
        insert_query = """
            INSERT INTO lead_assignments (lead_username, member_username)
            VALUES (%s, %s)
        """
        execute_query(insert_query, (lead_username, member_username), commit=True)

        return jsonify({"message": "Member assigned to Lead successfully"}), 201

    except Exception as e:
        if "Duplicate entry" in str(e):
            return jsonify({"error": "Assignment already exists"}), 409
        return jsonify({"error": str(e)}), 500

# =============================================
# Password and Settings Management
# =============================================

@users_bp.route('/<username>/change-password', methods=['PUT'])
def change_password(username):
    """Change user password - Manager and Lead only (Members don't have passwords)"""
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
            SELECT username, user_level FROM users
            WHERE username = %s AND password = %s
        """
        user = execute_query(verify_query, (username, hashed_old_password), fetch_one=True)

        if not user:
            return jsonify({"error": "Current password is incorrect"}), 401

        # Members don't have passwords
        if user['user_level'] == 'Member':
            return jsonify({"error": "Members do not have passwords"}), 403

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

    if new_role not in ['Manager', 'Lead', 'Member']:
        return jsonify({"error": "user_level must be 'Manager', 'Lead', or 'Member'"}), 400

    try:
        # Verify the requester is a Manager
        manager_query = "SELECT user_level FROM users WHERE username = %s"
        manager = execute_query(manager_query, (manager_username,), fetch_one=True)

        if not manager or manager['user_level'] != 'Manager':
            return jsonify({"error": "Only Managers can update user roles"}), 403

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
