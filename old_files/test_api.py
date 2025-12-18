import requests

BASE = "http://127.0.0.1:5000"


def show(name, resp):
    print("\n====", name, "====")
    print("status:", resp.status_code)
    try:
        print("json:", resp.json())
    except Exception:
        print("text:", resp.text)


# 1. 员工 check-in（user_id = 1）
resp1 = requests.post(
    f"{BASE}/check-in",
    json={"user_id": 1}
)
show("employee check-in (user_id=1)", resp1)

# 2. manager check-in（user_id = 2）
resp2 = requests.post(
    f"{BASE}/check-in",
    json={"user_id": 2}
)
show("manager check-in (user_id=2)", resp2)

# 3. manager 查看 pending
resp3 = requests.get(f"{BASE}/pending-requests", params={"manager_id": 2})
show("pending-requests (manager_id=2)", resp3)

# 4. 员工 check-out（user_id = 1）
resp4 = requests.post(
    f"{BASE}/check-out",
    json={"user_id": 1}
)
show("employee check-out (user_id=1)", resp4)

# 5. 查看员工所有记录
resp5 = requests.get(f"{BASE}/records", params={"user_id": 1})
show("records (user_id=1)", resp5)

import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="你的密码",
        database="practice_db",
    )
resp_m_co = requests.post(
    f"{BASE}/check-out",
    json={"user_id": 2}
)
show("manager check-out (user_id=2)", resp_m_co)

