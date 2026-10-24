"""
Automated Backend Integration Test for Muscle Monster Gym.
Tests User Registration, bcrypt Password Verification, JWT Authentication, and Protected Dashboard.
"""

import sys
import json
import bcrypt
from app import app
import db

def run_tests():
    print("==================================================")
    print("🧪 RUNNING MUSCLE MONSTER GYM BACKEND TEST SUITE")
    print("==================================================")

    client = app.test_client()

    # 1. Test Health Check
    health_res = client.get("/api/health")
    print(f"[1] Health Check: Status {health_res.status_code}")
    assert health_res.status_code == 200, "Health check failed"
    data = health_res.get_json()
    print(f"    Active Database: {data.get('active_database')}")

    # 2. Test User Registration
    test_email = "test.athlete@musclemonster.com"
    test_password = "SecretPassword123!"
    test_name = "Vikram Test Athlete"

    reg_payload = {
        "full_name": test_name,
        "email": test_email,
        "password": test_password,
        "membership_tier": "Transformation Beast"
    }

    # Delete if exists in test db
    existing = db.find_user_by_email(test_email)
    if existing:
        conn, db_type = db.get_db()
        try:
            if db_type == "MYSQL":
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM users WHERE email = %s", (test_email,))
            else:
                with conn:
                    conn.execute("DELETE FROM users WHERE email = ?", (test_email,))
        finally:
            conn.close()

    reg_res = client.post("/api/register", json=reg_payload)
    print(f"[2] User Registration: Status {reg_res.status_code}")
    assert reg_res.status_code == 201, f"Registration failed: {reg_res.get_data(as_text=True)}"
    reg_data = reg_res.get_json()
    assert reg_data["success"] is True
    jwt_token = reg_data["token"]
    assert jwt_token is not None
    print("    JWT Token Generated successfully.")

    # 3. Verify bcrypt hash in database
    user_in_db = db.find_user_by_email(test_email)
    assert user_in_db is not None
    stored_hash = user_in_db["password_hash"]
    assert stored_hash != test_password, "CRITICAL: Password is not hashed!"
    assert bcrypt.checkpw(test_password.encode("utf-8"), stored_hash.encode("utf-8")), "bcrypt hash verification failed!"
    print("    bcrypt password hash verified securely.")

    # 4. Test Duplicate Email Prevention
    dup_res = client.post("/api/register", json=reg_payload)
    print(f"[3] Duplicate Registration Check: Status {dup_res.status_code}")
    assert dup_res.status_code == 409, "Duplicate email was not rejected!"
    print("    Duplicate prevention verified.")

    # 5. Test Login (Success)
    login_payload = {
        "email": test_email,
        "password": test_password
    }
    login_res = client.post("/api/login", json=login_payload)
    print(f"[4] User Login (Valid Credentials): Status {login_res.status_code}")
    assert login_res.status_code == 200, "Login failed with valid credentials"
    login_data = login_res.get_json()
    auth_token = login_data["token"]
    print("    Login token obtained.")

    # 6. Test Login (Invalid Credentials)
    bad_login_res = client.post("/api/login", json={"email": test_email, "password": "WrongPassword"})
    print(f"[5] User Login (Invalid Password): Status {bad_login_res.status_code}")
    assert bad_login_res.status_code == 401, "Bad password was not rejected!"
    print("    Rejection of invalid password verified.")

    # 7. Test Protected Dashboard Route (Without Token -> Should Fail)
    unauth_dash_res = client.get("/api/dashboard")
    print(f"[6] Protected Dashboard (No Token): Status {unauth_dash_res.status_code}")
    assert unauth_dash_res.status_code == 401, "Unauthenticated access should be blocked!"
    print("    401 Unauthorized correctly enforced.")

    # 8. Test Protected Dashboard Route (With Valid JWT Token -> Should Succeed)
    dash_res = client.get("/api/dashboard", headers={"Authorization": f"Bearer {auth_token}"})
    print(f"[7] Protected Dashboard (Valid JWT): Status {dash_res.status_code}")
    assert dash_res.status_code == 200, f"Dashboard access failed: {dash_res.get_data(as_text=True)}"
    dash_data = dash_res.get_json()
    assert dash_data["user"]["email"] == test_email
    assert dash_data["gym_data"]["pass_status"] == "Active VIP Athlete"
    print(f"    Dashboard Data for Athlete: {dash_data['user']['full_name']}")
    print(f"    Assigned Locker: {dash_data['gym_data']['locker_number']}")
    print(f"    Active Workout: {dash_data['gym_data']['next_workout']}")

    print("\n==================================================")
    print("✅ ALL BACKEND AND AUTHENTICATION TESTS PASSED!")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
