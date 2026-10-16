from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash

from database import get_connection

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/api/register")
def register():
    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = data.get("password", "")

    if not name or not email or not isinstance(password, str):
        return jsonify({"error": "All fields are required"}), 400

    if len(password) < 8:
        return jsonify({
            "error": "Password must contain at least 8 characters"
        }), 400

    if len(name) > 100 or len(email) > 255:
        return jsonify({"error": "Input is too long"}), 400

    if "@" not in email:
        return jsonify({"error": "Enter a valid email"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """INSERT INTO users (name, email, password_hash)
               VALUES (%s, %s, %s)""",
            (name, email, generate_password_hash(password))
        )
        conn.commit()

        user_id = cursor.lastrowid
        session.clear()
        session["user_id"] = user_id

        return jsonify({
            "message": "Account created successfully",
            "user": {"id": user_id, "name": name}
        }), 201

    except Exception as error:
        conn.rollback()

        if getattr(error, "errno", None) == 1062:
            return jsonify({"error": "Email already registered"}), 409

        raise

    finally:
        cursor.close()
        conn.close()


@auth_bp.post("/api/login")
def login():
    data = request.get_json(silent=True) or {}

    email = str(data.get("email", "")).strip().lower()
    password = data.get("password", "")

    if not email or not isinstance(password, str):
        return jsonify({"error": "Email and password are required"}), 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT id, name, password_hash FROM users WHERE email = %s",
            (email,)
        )
        user = cursor.fetchone()

        if not user or not check_password_hash(
            user["password_hash"], password
        ):
            return jsonify({"error": "Invalid email or password"}), 401

        session.clear()
        session["user_id"] = user["id"]

        return jsonify({
            "message": "Login successful",
            "user": {
                "id": user["id"],
                "name": user["name"]
            }
        })

    finally:
        cursor.close()
        conn.close()


@auth_bp.post("/api/logout")
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"})


@auth_bp.get("/api/me")
def current_user():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Login required"}), 401

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT id, name, email FROM users WHERE id = %s",
            (user_id,)
        )
        user = cursor.fetchone()

        if not user:
            session.clear()
            return jsonify({"error": "User not found"}), 401

        return jsonify({"user": user})

    finally:
        cursor.close()
        conn.close()