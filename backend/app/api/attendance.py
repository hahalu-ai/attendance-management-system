from flask import Blueprint, request, jsonify
from ..models.database import execute_query, get_connection
from datetime import datetime, date, timedelta
import hashlib
import secrets

attendance_bp = Blueprint('attendance', __name__)

def generate_qr_token(lead_username, member_username, action_type):
    """Generate a secure token for QR code check-in/check-out"""
    timestamp = datetime.now().isoformat()
    random_salt = secrets.token_hex(16)
    data = f"{lead_username}:{member_username}:{action_type}:{timestamp}:{random_salt}"
    token = hashlib.sha256(data.encode()).hexdigest()
    return token, timestamp

def get_month_range(year, month):
    """Get start and end date for a given month"""
    start = date(year, month, 1)
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    return start, next_month

def count_weekdays(start_date, end_date):
    """Count weekdays between two dates"""
    current = start_date
    count = 0
    while current < end_date:
        if current.weekday() < 5:  # Monday=0, Friday=4
            count += 1
        current += timedelta(days=1)
    return count

@attendance_bp.route('/check-in', methods=['POST'])
def check_in():
    """Clock in for work"""
    data = request.get_json() or {}
    username = data.get('username')

    if not username:
        return jsonify({"error": "Username is required"}), 400

    try:
        # Get user info
        user_query = "SELECT username, user_level FROM users WHERE username = %s"
        user = execute_query(user_query, (username,), fetch_one=True)

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Check for open time entry
        open_query = """
            SELECT id FROM time_entries
            WHERE username = %s AND out_time IS NULL
            ORDER BY in_time DESC LIMIT 1
        """
        open_entry = execute_query(open_query, (username,), fetch_one=True)

        if open_entry:
            return jsonify({"error": "You have an open time entry. Please check out first."}), 400

        # Managers and Leads auto-approve their own time entries
        if user['user_level'] in ['Manager', 'Lead']:
            insert_query = """
                INSERT INTO time_entries
                (username, in_time, status, approved_by, approved_at)
                VALUES (%s, NOW(), 'Approved', %s, NOW())
            """
            entry_id = execute_query(insert_query, (username, username), commit=True)
            return jsonify({
                "message": "Check-in successful (auto-approved)",
                "entry_id": entry_id
            }), 201

        # Members need approval from their Lead (but Members shouldn't use manual check-in)
        else:
            # Check if member has a lead
            lead_query = """
                SELECT lead_username FROM lead_assignments
                WHERE member_username = %s
            """
            lead = execute_query(lead_query, (username,), fetch_one=True)

            if not lead:
                return jsonify({"error": "No lead assigned. Members should use QR code check-in."}), 403

            insert_query = """
                INSERT INTO time_entries
                (username, in_time, status)
                VALUES (%s, NOW(), 'Pending')
            """
            entry_id = execute_query(insert_query, (username,), commit=True)
            return jsonify({
                "message": "Check-in submitted. Waiting for lead approval.",
                "entry_id": entry_id
            }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@attendance_bp.route('/check-out', methods=['POST'])
def check_out():
    """Clock out from work"""
    data = request.get_json() or {}
    username = data.get('username')

    if not username:
        return jsonify({"error": "Username is required"}), 400

    try:
        # Find open time entry
        query = """
            SELECT id FROM time_entries
            WHERE username = %s AND out_time IS NULL
            ORDER BY in_time DESC LIMIT 1
        """
        entry = execute_query(query, (username,), fetch_one=True)

        if not entry:
            return jsonify({"error": "No open time entry found"}), 400

        # Update with checkout time
        update_query = """
            UPDATE time_entries
            SET out_time = NOW()
            WHERE id = %s
        """
        execute_query(update_query, (entry['id'],), commit=True)

        return jsonify({
            "message": "Check-out successful",
            "entry_id": entry['id']
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@attendance_bp.route('/my-entries', methods=['GET'])
def my_entries():
    """Get time entries for the current user"""
    username = request.args.get('username')

    if not username:
        return jsonify({"error": "Username parameter is required"}), 400

    try:
        query = """
            SELECT id, username, in_time, out_time, status,
                   approved_by, approved_at, notes
            FROM time_entries
            WHERE username = %s
            ORDER BY in_time DESC
            LIMIT 100
        """
        entries = execute_query(query, (username,), fetch_all=True)

        return jsonify({"entries": entries}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@attendance_bp.route('/pending-approvals', methods=['GET'])
def pending_approvals():
    """Get pending time entries for a Manager or Lead to approve"""
    approver_username = request.args.get('username')

    if not approver_username:
        return jsonify({"error": "username parameter is required"}), 400

    try:
        # Verify user is a Manager or Lead
        user_query = "SELECT user_level FROM users WHERE username = %s"
        user = execute_query(user_query, (approver_username,), fetch_one=True)

        if not user or user['user_level'] not in ['Manager', 'Lead']:
            return jsonify({"error": "Only Managers and Leads can view pending approvals"}), 403

        # Managers see ALL pending entries
        if user['user_level'] == 'Manager':
            query = """
                SELECT te.id, te.username, u.display_name, te.in_time, te.out_time, te.status
                FROM time_entries te
                JOIN users u ON te.username = u.username
                WHERE te.status = 'Pending'
                ORDER BY te.in_time DESC
            """
            entries = execute_query(query, fetch_all=True)
        else:  # Lead
            # Get pending entries for this Lead's Members
            query = """
                SELECT te.id, te.username, u.display_name, te.in_time, te.out_time, te.status
                FROM time_entries te
                JOIN lead_assignments la ON te.username = la.member_username
                JOIN users u ON te.username = u.username
                WHERE la.lead_username = %s AND te.status = 'Pending'
                ORDER BY te.in_time DESC
            """
            entries = execute_query(query, (approver_username,), fetch_all=True)

        return jsonify({"pending_entries": entries}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@attendance_bp.route('/approve', methods=['POST'])
def approve_entry():
    """Approve or reject a time entry"""
    data = request.get_json() or {}
    approver_username = data.get('approver_username') or data.get('manager_username')  # Support both parameter names
    entry_id = data.get('entry_id')
    status = data.get('status')  # 'Approved' or 'Rejected'
    notes = data.get('notes', '')

    if not all([approver_username, entry_id, status]):
        return jsonify({"error": "approver_username, entry_id, and status are required"}), 400

    if status not in ['Approved', 'Rejected']:
        return jsonify({"error": "Status must be 'Approved' or 'Rejected'"}), 400

    try:
        # Verify approver is Manager or Lead
        user_query = "SELECT user_level FROM users WHERE username = %s"
        user = execute_query(user_query, (approver_username,), fetch_one=True)

        if not user or user['user_level'] not in ['Manager', 'Lead']:
            return jsonify({"error": "Only Managers and Leads can approve entries"}), 403

        # Managers can approve any entry
        if user['user_level'] == 'Manager':
            entry_query = """
                SELECT te.username FROM time_entries te
                WHERE te.id = %s
            """
            entry = execute_query(entry_query, (entry_id,), fetch_one=True)
        else:  # Lead
            # Get the time entry and verify Lead has authority over this Member
            entry_query = """
                SELECT te.username FROM time_entries te
                JOIN lead_assignments la ON te.username = la.member_username
                WHERE te.id = %s AND la.lead_username = %s
            """
            entry = execute_query(entry_query, (entry_id, approver_username), fetch_one=True)

        if not entry:
            return jsonify({"error": "Entry not found or you don't have permission"}), 404

        # Update the entry
        update_query = """
            UPDATE time_entries
            SET status = %s, approved_by = %s, approved_at = NOW(), notes = %s
            WHERE id = %s
        """
        execute_query(update_query, (status, approver_username, notes, entry_id), commit=True)

        return jsonify({
            "message": f"Entry {status.lower()} successfully",
            "entry_id": entry_id,
            "status": status
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@attendance_bp.route('/monthly-summary', methods=['GET'])
def monthly_summary():
    """Get monthly attendance summary"""
    username = request.args.get('username')
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)

    if not all([username, year, month]):
        return jsonify({"error": "username, year, and month parameters are required"}), 400

    try:
        month_start, next_month_start = get_month_range(year, month)
        expected_workdays = count_weekdays(month_start, next_month_start)

        query = """
            SELECT
                DATE(in_time) AS work_date,
                MIN(in_time) AS first_check_in,
                MAX(out_time) AS last_check_out,
                SUM(TIMESTAMPDIFF(MINUTE, in_time, out_time)) / 60.0 AS hours_worked
            FROM time_entries
            WHERE username = %s
              AND status = 'Approved'
              AND out_time IS NOT NULL
              AND in_time >= %s
              AND in_time < %s
            GROUP BY work_date
            ORDER BY work_date
        """
        entries = execute_query(query, (username, month_start, next_month_start), fetch_all=True)

        total_hours = sum(float(e['hours_worked'] or 0) for e in entries)
        days_worked = len(entries)

        return jsonify({
            "username": username,
            "year": year,
            "month": month,
            "summary": {
                "days_worked": days_worked,
                "expected_workdays": expected_workdays,
                "total_hours": round(total_hours, 2),
                "is_full_attendance": days_worked >= expected_workdays
            },
            "details": entries
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =============================================
# QR Code-based Check-in/Check-out Endpoints
# =============================================

@attendance_bp.route('/qr/generate', methods=['POST'])
def generate_qr_request():
    """
    Lead generates a QR code request for a Member to check in/out
    Request body: {
        "lead_username": "jsmith",
        "member_username": "member01",
        "action": "check-in" or "check-out"
    }
    """
    data = request.get_json() or {}
    lead_username = data.get('lead_username') or data.get('manager_username')  # Support old parameter name
    member_username = data.get('member_username') or data.get('worker_username')  # Support old parameter name
    action = data.get('action')  # 'check-in' or 'check-out'

    if not all([lead_username, member_username, action]):
        return jsonify({"error": "lead_username, member_username, and action are required"}), 400

    if action not in ['check-in', 'check-out']:
        return jsonify({"error": "action must be 'check-in' or 'check-out'"}), 400

    try:
        # Verify Lead
        lead_query = "SELECT user_level FROM users WHERE username = %s"
        lead = execute_query(lead_query, (lead_username,), fetch_one=True)

        if not lead or lead['user_level'] != 'Lead':
            return jsonify({"error": "Only Leads can generate QR codes"}), 403

        # Verify Member exists
        member_query = "SELECT username, display_name, user_level FROM users WHERE username = %s"
        member = execute_query(member_query, (member_username,), fetch_one=True)

        if not member:
            return jsonify({"error": "Member not found"}), 404

        if member['user_level'] != 'Member':
            return jsonify({"error": "QR codes can only be generated for Members"}), 400

        # Verify Lead-Member relationship
        relationship_query = """
            SELECT 1 FROM lead_assignments
            WHERE lead_username = %s AND member_username = %s
        """
        relationship = execute_query(
            relationship_query,
            (lead_username, member_username),
            fetch_one=True
        )

        if not relationship:
            return jsonify({"error": "Member is not assigned to this Lead"}), 403

        # For check-out, verify there's an open time entry
        if action == 'check-out':
            open_query = """
                SELECT id FROM time_entries
                WHERE username = %s AND out_time IS NULL
                ORDER BY in_time DESC LIMIT 1
            """
            open_entry = execute_query(open_query, (member_username,), fetch_one=True)

            if not open_entry:
                return jsonify({"error": "Member has no open time entry to check out"}), 400

        # For check-in, verify there's no open time entry
        if action == 'check-in':
            open_query = """
                SELECT id FROM time_entries
                WHERE username = %s AND out_time IS NULL
                ORDER BY in_time DESC LIMIT 1
            """
            open_entry = execute_query(open_query, (member_username,), fetch_one=True)

            if open_entry:
                return jsonify({"error": "Member already has an open time entry"}), 400

        # Generate QR token
        token, timestamp = generate_qr_token(lead_username, member_username, action)

        # Store the QR request in database (expires in 5 minutes)
        insert_query = """
            INSERT INTO qr_requests
            (token, lead_username, member_username, action_type, created_at, expires_at, status)
            VALUES (%s, %s, %s, %s, %s, DATE_ADD(%s, INTERVAL 5 MINUTE), 'pending')
        """
        execute_query(
            insert_query,
            (token, lead_username, member_username, action, timestamp, timestamp),
            commit=True
        )

        return jsonify({
            "message": "QR code generated successfully",
            "token": token,
            "member_username": member_username,
            "member_name": member.get('display_name', member_username),
            "action": action,
            "expires_in_seconds": 300,
            "timestamp": timestamp
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@attendance_bp.route('/qr/verify', methods=['POST'])
def verify_qr_code():
    """
    Member scans QR code to confirm check-in/check-out
    Request body: {
        "token": "abc123...",
        "member_username": "member01"  # Optional, for verification
    }
    """
    data = request.get_json() or {}
    token = data.get('token')
    member_username = data.get('member_username') or data.get('worker_username')  # Support old parameter name

    if not token:
        return jsonify({"error": "Token is required"}), 400

    try:
        # Find the QR request
        query = """
            SELECT *
            FROM qr_requests
            WHERE token = %s AND status = 'pending' AND expires_at > NOW()
        """
        qr_request = execute_query(query, (token,), fetch_one=True)

        if not qr_request:
            return jsonify({"error": "Invalid or expired QR code"}), 400

        # Verify member if username provided
        if member_username and qr_request['member_username'] != member_username:
            return jsonify({"error": "QR code is not for this member"}), 403

        action = qr_request['action_type']
        member_user = qr_request['member_username']
        lead_user = qr_request['lead_username']

        # Perform the action
        if action == 'check-in':
            # Check again for open entry (in case status changed)
            open_query = """
                SELECT id FROM time_entries
                WHERE username = %s AND out_time IS NULL
                ORDER BY in_time DESC LIMIT 1
            """
            open_entry = execute_query(open_query, (member_user,), fetch_one=True)

            if open_entry:
                # Mark QR request as failed
                update_query = "UPDATE qr_requests SET status = 'failed' WHERE token = %s"
                execute_query(update_query, (token,), commit=True)
                return jsonify({"error": "Member already has an open time entry"}), 400

            # Create check-in entry (auto-approved via QR code)
            insert_query = """
                INSERT INTO time_entries
                (username, in_time, status, approved_by, approved_at)
                VALUES (%s, NOW(), 'Approved', %s, NOW())
            """
            entry_id = execute_query(insert_query, (member_user, lead_user), commit=True)

        else:  # check-out
            # Find open entry
            open_query = """
                SELECT id FROM time_entries
                WHERE username = %s AND out_time IS NULL
                ORDER BY in_time DESC LIMIT 1
            """
            open_entry = execute_query(open_query, (member_user,), fetch_one=True)

            if not open_entry:
                # Mark QR request as failed
                update_query = "UPDATE qr_requests SET status = 'failed' WHERE token = %s"
                execute_query(update_query, (token,), commit=True)
                return jsonify({"error": "No open time entry found"}), 400

            # Update with checkout time
            update_entry_query = """
                UPDATE time_entries
                SET out_time = NOW()
                WHERE id = %s
            """
            execute_query(update_entry_query, (open_entry['id'],), commit=True)
            entry_id = open_entry['id']

        # Mark QR request as used
        update_qr_query = """
            UPDATE qr_requests
            SET status = 'used', used_at = NOW()
            WHERE token = %s
        """
        execute_query(update_qr_query, (token,), commit=True)

        return jsonify({
            "message": f"{action.title()} successful",
            "action": action,
            "member_username": member_user,
            "entry_id": entry_id,
            "timestamp": datetime.now().isoformat()
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@attendance_bp.route('/qr/status/<token>', methods=['GET'])
def get_qr_status(token):
    """Check the status of a QR request"""
    try:
        query = "SELECT * FROM qr_requests WHERE token = %s"
        qr_request = execute_query(query, (token,), fetch_one=True)

        if not qr_request:
            return jsonify({"error": "QR request not found"}), 404

        return jsonify({
            "token": qr_request['token'],
            "member_username": qr_request['member_username'],
            "lead_username": qr_request['lead_username'],
            "action": qr_request['action_type'],
            "status": qr_request['status'],
            "created_at": qr_request['created_at'].isoformat() if qr_request['created_at'] else None,
            "expires_at": qr_request['expires_at'].isoformat() if qr_request['expires_at'] else None,
            "used_at": qr_request['used_at'].isoformat() if qr_request['used_at'] else None,
            "is_expired": qr_request['expires_at'] < datetime.now() if qr_request['expires_at'] else True
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
