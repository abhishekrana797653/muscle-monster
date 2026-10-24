"""
Flask Backend Application for Muscle Monster Gym.
Provides RESTful APIs for User Registration, Authentication with bcrypt & JWT, and Protected Dashboard.
"""

import os
import re
import datetime
from functools import wraps
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import bcrypt
import jwt
from dotenv import load_dotenv

import db

# Load environment configuration
load_dotenv()

app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates"
)

# Enable CORS for cross-origin frontend requests
CORS(app)

SECRET_KEY = os.getenv("SECRET_KEY", "muscle_monster_default_secure_secret_2026")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Ensure tables are initialized on startup
with app.app_context():
    try:
        db.init_db()
    except Exception as e:
        print(f"[WARN] Database initialization notice: {e}")

# -----------------------------------------------------------------------------
# Authentication Helpers & Decorators
# -----------------------------------------------------------------------------

def is_valid_email(email):
    """Simple regex to validate email format."""
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return bool(re.match(pattern, email))

def generate_jwt_token(user):
    """Generate a signed JWT token valid for 24 hours."""
    payload = {
        "user_id": user["id"],
        "email": user["email"],
        "full_name": user.get("full_name", ""),
        "membership_tier": user.get("membership_tier", "Standard Athlete"),
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.datetime.now(datetime.timezone.utc)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)

def token_required(f):
    """Decorator to protect API routes with JWT authorization."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get("Authorization")
        
        if auth_header:
            parts = auth_header.split(" ")
            if len(parts) == 2 and parts[0].lower() == "bearer":
                token = parts[1]

        # Alternatively check query param or cookie
        if not token:
            token = request.args.get("token") or request.cookies.get("token")

        if not token:
            return jsonify({
                "success": False,
                "message": "Authorization token is missing. Please log in."
            }), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
            current_user = db.find_user_by_id(data["user_id"])
            if not current_user:
                return jsonify({
                    "success": False,
                    "message": "User session no longer exists."
                }), 401
        except jwt.ExpiredSignatureError:
            return jsonify({
                "success": False,
                "message": "Token has expired. Please log in again."
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                "success": False,
                "message": "Invalid authentication token."
            }), 401

        return f(current_user, *args, **kwargs)
    return decorated

# -----------------------------------------------------------------------------
# Frontend Page Routes (Serves HTML)
# -----------------------------------------------------------------------------

@app.route("/")
def serve_index():
    """Serves the main landing page."""
    return send_from_directory(".", "index.html")

@app.route("/login")
def serve_login():
    """Serves the User Login page."""
    return send_from_directory("templates", "login.html")

@app.route("/register")
def serve_register():
    """Serves the User Registration page."""
    return send_from_directory("templates", "register.html")

@app.route("/dashboard")
def serve_dashboard():
    """Serves the Protected Member Dashboard page."""
    return send_from_directory("templates", "dashboard.html")

# Serve root CSS/JS files if referenced directly
@app.route("/<path:filename>")
def serve_root_files(filename):
    if os.path.exists(os.path.join(".", filename)):
        return send_from_directory(".", filename)
    return jsonify({"error": "File not found"}), 440

# -----------------------------------------------------------------------------
# REST API Endpoints
# -----------------------------------------------------------------------------

@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint to inspect server and active database."""
    return jsonify({
        "status": "online",
        "service": "Muscle Monster Gym Backend",
        "active_database": db.ACTIVE_DB_TYPE,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }), 200

@app.route("/api/register", methods=["POST"])
def register():
    """
    Register a new user.
    Body JSON: { full_name, email, password, (optional) membership_tier }
    """
    data = request.get_json(silent=True) or request.form.to_dict()

    full_name = data.get("full_name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    tier = data.get("membership_tier", "Standard Athlete")

    # Validation
    if not full_name or len(full_name) < 2:
        return jsonify({"success": False, "message": "Full name must be at least 2 characters."}), 400

    if not email or not is_valid_email(email):
        return jsonify({"success": False, "message": "Please provide a valid email address."}), 400

    if not password or len(password) < 6:
        return jsonify({"success": False, "message": "Password must be at least 6 characters long."}), 400

    # Check for existing email
    existing_user = db.find_user_by_email(email)
    if existing_user:
        return jsonify({
            "success": False,
            "message": "An athlete with this email is already registered. Please log in."
        }), 409

    # Hash password safely with bcrypt
    salt = bcrypt.gensalt(rounds=12)
    password_hash = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    try:
        user_id = db.create_user(full_name, email, password_hash, tier)
        new_user = {
            "id": user_id,
            "full_name": full_name,
            "email": email,
            "membership_tier": tier
        }
        token = generate_jwt_token(new_user)

        return jsonify({
            "success": True,
            "message": "Account created successfully! Welcome to Muscle Monster Gym.",
            "token": token,
            "user": new_user
        }), 201
    except Exception as e:
        return jsonify({"success": False, "message": f"Registration failed: {str(e)}"}), 500

@app.route("/api/login", methods=["POST"])
def login():
    """
    Authenticate a user.
    Body JSON: { email, password }
    """
    data = request.get_json(silent=True) or request.form.to_dict()

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"success": False, "message": "Please enter both email and password."}), 400

    user = db.find_user_by_email(email)
    if not user:
        return jsonify({"success": False, "message": "Invalid email or password credentials."}), 401

    # Verify password hash
    stored_hash = user["password_hash"].encode("utf-8")
    if not bcrypt.checkpw(password.encode("utf-8"), stored_hash):
        return jsonify({"success": False, "message": "Invalid email or password credentials."}), 401

    # Generate JWT Token
    token = generate_jwt_token(user)

    return jsonify({
        "success": True,
        "message": "Login successful. Welcome back!",
        "token": token,
        "user": {
            "id": user["id"],
            "full_name": user["full_name"],
            "email": user["email"],
            "membership_tier": user.get("membership_tier", "Standard Athlete")
        }
    }), 200

@app.route("/api/dashboard", methods=["GET"])
@token_required
def dashboard_data(current_user):
    """
    Protected dashboard endpoint.
    Requires Authorization: Bearer <JWT_TOKEN>
    """
    # Sample personalized telemetry & workout plan
    return jsonify({
        "success": True,
        "user": {
            "id": current_user["id"],
            "full_name": current_user["full_name"],
            "email": current_user["email"],
            "membership_tier": current_user.get("membership_tier", "Standard Athlete"),
            "member_since": str(current_user.get("created_at", "2026-10-24"))
        },
        "gym_data": {
            "facility_location": "Chauraha, Bareilly - Nainital Rd, near Motahaldu, Haldwani",
            "active_batch": "Evening Shift (4:00 PM - 10:00 PM)",
            "next_workout": "Chest, Deltoids & Triceps Hypertrophy",
            "assigned_trainer": "Head Coach Vikram Rawat",
            "locker_number": f"L-{current_user['id'] + 100}",
            "attendance_this_month": 18,
            "pass_status": "Active VIP Athlete"
        }
    }), 200

@app.route("/api/logout", methods=["POST"])
def logout():
    """Logs out user (instructs client to clear stored JWT token)."""
    return jsonify({
        "success": True,
        "message": "Logged out successfully."
    }), 200

# -----------------------------------------------------------------------------
# Main Application Entrypoint
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5000))
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    debug = os.getenv("FLASK_ENV", "development") == "development"
    print(f"\n=======================================================")
    print(f" Muscle Monster Gym Server Running on http://{host}:{port}")
    print(f" Database Mode: {db.ACTIVE_DB_TYPE}")
    print(f"=======================================================\n")
    app.run(host=host, port=port, debug=debug)
