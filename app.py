from flask import Flask, request, jsonify
from db import get_connection
from datetime import date, timedelta


app = Flask(__name__)


def get_user_role(conn, user_id):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT role FROM user WHERE id = %s", (user_id,))
    row = cursor.fetchone()
    cursor.close()
    return row["role"] if row else None


def employee_has_manager(conn, user_id):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM manager_employee WHERE employee_id = %s LIMIT 1",
        (user_id,),
    )
    row = cursor.fetchone()
    cursor.close()
    return row is not None


def get_open_record(conn, user_id):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT id
        FROM attendance_record
        WHERE user_id = %s
          AND check_out_time IS NULL
        ORDER BY check_in_time DESC
        LIMIT 1
        """,
        (user_id,),
    )
    row = cursor.fetchone()
    cursor.close()
    return row

def get_month_range(year, month):
    start = date(year, month, 1)
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    return start, next_month


def count_weekdays(start_date, end_date):
    current = start_date
    count = 0
    while current < end_date:
        if current.weekday() < 5:  
            count += 1
        current += timedelta(days=1)
    return count

@app.route("/check-in", methods=["POST"])
def check_in():
    data = request.get_json() or {}
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "缺少 user_id"}), 400

    conn = get_connection()

    try:
        role = get_user_role(conn, user_id)
        if role is None:
            return jsonify({"error": "用户不存在"}), 404

        open_record = get_open_record(conn, user_id)
        if open_record:
            return jsonify({"error": "已有未下班记录，请先 check-out"}), 400

        cursor = conn.cursor()

        if role == "manager":
            cursor.execute(
                """
                INSERT INTO attendance_record
                    (user_id, check_in_time, status, approved_by, approved_at)
                VALUES
                    (%s, NOW(), 'approved', %s, NOW())
                """,
                (user_id, user_id),
            )
            conn.commit()
            cursor.close()
            return jsonify({"message": "Manager check-in success (auto approved)"}), 201

        if role == "employee":
            if not employee_has_manager(conn, user_id):
                return jsonify({"error": "该员工没有对应 manager，不能打卡"}), 403

            cursor.execute(
                """
                INSERT INTO attendance_record
                    (user_id, check_in_time, status)
                VALUES
                    (%s, NOW(), 'pending')
                """,
                (user_id,),
            )
            conn.commit()
            cursor.close()
            return jsonify(
                {"message": "Check-in submitted, waiting for manager approval"}
            ), 201

        return jsonify({"error": "未知角色"}), 400

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


@app.route("/check-out", methods=["POST"])
def check_out():
    data = request.get_json() or {}
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "缺少 user_id"}), 400

    conn = get_connection()

    try:
        open_record = get_open_record(conn, user_id)
        if not open_record:
            return jsonify({"error": "没有需要下班的打卡记录"}), 400

        record_id = open_record["id"]

        cursor = conn.cursor()
        cursor.execute(
            "UPDATE attendance_record "
            "SET check_out_time = NOW() "
            "WHERE id = %s",
            (record_id,),
        )
        conn.commit()
        cursor.close()

        return jsonify({"message": "Check-out success", "record_id": record_id}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


@app.route("/records", methods=["GET"])
def list_records():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "缺少 user_id 参数"}), 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT id, user_id, check_in_time, check_out_time,
               status, approved_by, approved_at
        FROM attendance_record
        WHERE user_id = %s
        ORDER BY check_in_time DESC
        """,
        (user_id,),
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(rows), 200


@app.route("/pending-requests", methods=["GET"])
def pending_requests():
    manager_id = request.args.get("manager_id")
    if not manager_id:
        return jsonify({"error": "缺少 manager_id 参数"}), 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        role = get_user_role(conn, manager_id)
        if role != "manager":
            return jsonify({"error": "只有 manager 可以查看待审批记录"}), 403

        cursor.execute(
            """
            SELECT ar.id,
                   ar.user_id,
                   u.name,
                   ar.check_in_time,
                   ar.check_out_time,
                   ar.status
            FROM attendance_record ar
            JOIN manager_employee me
              ON ar.user_id = me.employee_id
            JOIN user u
              ON ar.user_id = u.id
            WHERE me.manager_id = %s
              AND ar.status = 'pending'
            ORDER BY ar.check_in_time DESC
            """,
            (manager_id,),
        )
        rows = cursor.fetchall()
        return jsonify(rows), 200

    finally:
        cursor.close()
        conn.close()


@app.route("/approve-attendance", methods=["POST"])
def approve_attendance():
    data = request.get_json() or {}
    manager_id = data.get("manager_id")
    record_id = data.get("record_id")
    new_status = data.get("status")

    if not (manager_id and record_id and new_status):
        return jsonify({"error": "缺少 manager_id / record_id / status"}), 400

    if new_status not in ("approved", "rejected"):
        return jsonify({"error": "status 必须是 approved 或 rejected"}), 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        role = get_user_role(conn, manager_id)
        if role != "manager":
            return jsonify({"error": "你没有相关权限"}), 403

        cursor.execute(
            "SELECT user_id FROM attendance_record WHERE id = %s",
            (record_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return jsonify({"error": "考勤记录不存在"}), 404

        employee_id = row["user_id"]

        cursor.execute(
            "SELECT 1 FROM manager_employee "
            "WHERE manager_id = %s AND employee_id = %s LIMIT 1",
            (manager_id, employee_id),
        )
        rel = cursor.fetchone()
        if rel is None:
            return jsonify({"error": "你没有改员工权限审批"}), 403

        cursor2 = conn.cursor()
        cursor2.execute(
            """
            UPDATE attendance_record
            SET status = %s,
                approved_by = %s,
                approved_at = NOW()
            WHERE id = %s
            """,
            (new_status, manager_id, record_id),
        )
        conn.commit()
        cursor2.close()

        return jsonify(
            {"message": "审批成功", "record_id": record_id, "new_status": new_status}
        ), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route("/employee/monthly-summary", methods=["GET"])
def employee_monthly_summary():
    try:
        user_id = int(request.args.get("user_id"))
        year = int(request.args.get("year"))
        month = int(request.args.get("month"))
    except (TypeError, ValueError):
        return jsonify({"error": "请提供正确的 user_id, year, month 参数"}), 400

    conn = get_connection()
    try:
        month_start, next_month_start = get_month_range(year, month)
        expected_workdays = count_weekdays(month_start, next_month_start)

        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT 
                DATE(attendance_record.check_in_time) AS work_date,
                MIN(attendance_record.check_in_time) AS first_check_in,
                MAX(attendance_record.check_out_time) AS last_check_out,
                SUM(
                    TIMESTAMPDIFF(
                        MINUTE, 
                        attendance_record.check_in_time, 
                        attendance_record.check_out_time
                    )
                ) / 60.0 AS hours_worked
            FROM attendance_record
            WHERE 
                attendance_record.user_id = %s
                AND attendance_record.status = 'approved'
                AND attendance_record.check_out_time IS NOT NULL
                AND attendance_record.check_in_time >= %s
                AND attendance_record.check_in_time <  %s
            GROUP BY work_date
            ORDER BY work_date;
            """,
            (user_id, month_start, next_month_start),
        )
        rows = cursor.fetchall()
        cursor.close()

        total_hours = sum(
            float(row["hours_worked"]) for row in rows
            if row["hours_worked"] is not None
        )
        days_worked = len(rows)
        is_full_attendance = days_worked >= expected_workdays

        details = []
        for row in rows:
            details.append(
                {
                    "work_date": row["work_date"].isoformat()
                    if hasattr(row["work_date"], "isoformat")
                    else row["work_date"],
                    "first_check_in": row["first_check_in"].isoformat()
                    if row["first_check_in"]
                    else None,
                    "last_check_out": row["last_check_out"].isoformat()
                    if row["last_check_out"]
                    else None,
                    "hours_worked": float(row["hours_worked"])
                    if row["hours_worked"] is not None
                    else 0.0,
                }
            )

        return jsonify(
            {
                "user_id": user_id,
                "year": year,
                "month": month,
                "summary": {
                    "days_worked": days_worked,
                    "expected_workdays": expected_workdays,
                    "total_hours": total_hours,
                    "is_full_attendance": is_full_attendance,
                },
                "details": details,
            }
        ), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


@app.route("/manager/monthly-summary", methods=["GET"])
def manager_monthly_summary():
    try:
        manager_id = int(request.args.get("manager_id"))
        year = int(request.args.get("year"))
        month = int(request.args.get("month"))
    except (TypeError, ValueError):
        return jsonify({"error": "请提供正确的 manager_id, year, month 参数"}), 400

    conn = get_connection()
    try:
        role = get_user_role(conn, manager_id)
        if role != "manager":
            return jsonify({"error": "只有 manager 可以查看该统计"}), 403

        month_start, next_month_start = get_month_range(year, month)
        expected_workdays = count_weekdays(month_start, next_month_start)

        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT 
                attendance_record.user_id,
                user.name,
                DATE(attendance_record.check_in_time) AS work_date,
                MIN(attendance_record.check_in_time) AS first_check_in,
                MAX(attendance_record.check_out_time) AS last_check_out,
                SUM(
                    TIMESTAMPDIFF(
                        MINUTE,
                        attendance_record.check_in_time,
                        attendance_record.check_out_time
                    )
                ) / 60.0 AS hours_worked
            FROM attendance_record
            JOIN manager_employee
                ON attendance_record.user_id = manager_employee.employee_id
            JOIN user
                ON attendance_record.user_id = user.id
            WHERE 
                manager_employee.manager_id = %s
                AND attendance_record.status = 'approved'
                AND attendance_record.check_out_time IS NOT NULL
                AND attendance_record.check_in_time >= %s
                AND attendance_record.check_in_time <  %s
            GROUP BY attendance_record.user_id, user.name, work_date
            ORDER BY attendance_record.user_id, work_date;
            """,
            (manager_id, month_start, next_month_start),
        )
        rows = cursor.fetchall()
        cursor.close()

        employees = {}
        for row in rows:
            user_id = row["user_id"]
            if user_id not in employees:
                employees[user_id] = {
                    "user_id": user_id,
                    "name": row["name"],
                    "details": [],
                    "total_hours": 0.0,
                }

            employees[user_id]["details"].append(
                {
                    "work_date": row["work_date"].isoformat()
                    if hasattr(row["work_date"], "isoformat")
                    else row["work_date"],
                    "first_check_in": row["first_check_in"].isoformat()
                    if row["first_check_in"]
                    else None,
                    "last_check_out": row["last_check_out"].isoformat()
                    if row["last_check_out"]
                    else None,
                    "hours_worked": float(row["hours_worked"])
                    if row["hours_worked"] is not None
                    else 0.0,
                }
            )

            if row["hours_worked"] is not None:
                employees[user_id]["total_hours"] += float(row["hours_worked"])

        result_list = []
        for employee in employees.values():
            days_worked = len(employee["details"])
            employee["days_worked"] = days_worked
            employee["expected_workdays"] = expected_workdays
            employee["is_full_attendance"] = days_worked >= expected_workdays
            result_list.append(employee)

        return jsonify(
            {
                "manager_id": manager_id,
                "year": year,
                "month": month,
                "employees": result_list,
            }
        ), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


@app.route("/")
def index():
    return "Attendance API is running."


if __name__ == "__main__":
    app.run(debug=True, port=5001)

