import os
import json
from pathlib import Path
from functools import wraps

from flask import (
    Flask, request, jsonify, session,
    send_from_directory
)
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"

# Always load backend/.env, regardless of the terminal's current folder.
load_dotenv(BASE_DIR / ".env")

from database import get_connection
from auth import auth_bp
from resume_parser import extract_resume_text
from scoring import calculate_match
from gemini_service import generate_suggestions

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

if not app.config["SECRET_KEY"]:
    raise RuntimeError("Set SECRET_KEY in your .env file")

app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = (
    os.getenv("COOKIE_SECURE", "false").lower() == "true"
)

app.register_blueprint(auth_bp)


def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify({"error": "Please log in first"}), 401
        return function(*args, **kwargs)

    return wrapper


@app.get("/")
def home():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/dashboard")
def dashboard():
    return send_from_directory(FRONTEND_DIR, "dashboard.html")


@app.get("/history")
def history_page():
    return send_from_directory(FRONTEND_DIR, "history.html")


@app.get("/frontend/<path:filename>")
def frontend_files(filename):
    return send_from_directory(FRONTEND_DIR, filename)


@app.post("/api/analyze")
@login_required
def analyze_resume():
    pdf = request.files.get("resume")
    job_title = request.form.get("job_title", "").strip()
    job_description = request.form.get(
        "job_description", ""
    ).strip()

    if not pdf or not pdf.filename:
        return jsonify({"error": "Upload a PDF resume"}), 400

    if not job_description:
        return jsonify({
            "error": "Enter the job description"
        }), 400

    if len(job_description) > 20000:
        return jsonify({
            "error": "Job description is too long"
        }), 400

    if len(job_title) > 150:
        return jsonify({"error": "Job title is too long"}), 400

    pdf_bytes = pdf.read()

    if not pdf_bytes.startswith(b"%PDF-"):
        return jsonify({
            "error": "The uploaded file is not a valid PDF"
        }), 400

    try:
        resume_text = extract_resume_text(pdf_bytes)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    score_data = calculate_match(
        resume_text, job_description
    )

    if score_data.get("error"):
        return jsonify({"error": score_data["error"]}), 400

    ai_result = generate_suggestions(
        resume_text,
        job_description,
        score_data
    )

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO analyses (
                user_id, job_title, job_description,
                match_score, matched_skills,
                missing_skills, suggestions, summary
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                session["user_id"],
                job_title or "Untitled Job",
                job_description,
                score_data["score"],
                json.dumps(score_data["matched_skills"]),
                json.dumps(score_data["missing_skills"]),
                json.dumps({
                    "strengths": ai_result["strengths"],
                    "suggestions": ai_result["suggestions"],
                    "ai_used": ai_result["ai_used"]
                }),
                ai_result["summary"]
            )
        )

        analysis_id = cursor.lastrowid
        conn.commit()

    except Exception:
        conn.rollback()
        app.logger.exception("Failed to save analysis")
        return jsonify({
            "error": "Could not save the analysis"
        }), 500

    finally:
        cursor.close()
        conn.close()

    return jsonify({
        "id": analysis_id,
        "job_title": job_title or "Untitled Job",
        "match_score": score_data["score"],
        "matched_skills": score_data["matched_skills"],
        "missing_skills": score_data["missing_skills"],
        "resume_skills": score_data["resume_skills"],
        "strengths": ai_result["strengths"],
        "suggestions": ai_result["suggestions"],
        "summary": ai_result["summary"],
        "ai_used": ai_result["ai_used"]
    }), 201


@app.get("/api/analyses")
@login_required
def get_analyses():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT id, job_title, match_score,
                   DATE_FORMAT(created_at, '%Y-%m-%d %H:%i')
                   AS created_at
            FROM analyses
            WHERE user_id = %s
            ORDER BY created_at DESC
            """,
            (session["user_id"],)
        )

        return jsonify({"analyses": cursor.fetchall()})

    finally:
        cursor.close()
        conn.close()


@app.get("/api/analyses/<int:analysis_id>")
@login_required
def get_analysis(analysis_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT id, job_title, job_description,
                   match_score, matched_skills, missing_skills,
                   suggestions, summary,
                   DATE_FORMAT(created_at, '%Y-%m-%d %H:%i')
                   AS created_at
            FROM analyses
            WHERE id = %s AND user_id = %s
            """,
            (analysis_id, session["user_id"])
        )

        result = cursor.fetchone()

        if not result:
            return jsonify({"error": "Analysis not found"}), 404

        # MySQL drivers may return JSON columns as strings.
        for key in (
            "matched_skills", "missing_skills", "suggestions"
        ):
            if isinstance(result[key], str):
                result[key] = json.loads(result[key])

        return jsonify(result)

    finally:
        cursor.close()
        conn.close()


@app.delete("/api/analyses/<int:analysis_id>")
@login_required
def delete_analysis(analysis_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "DELETE FROM analyses WHERE id = %s AND user_id = %s",
            (analysis_id, session["user_id"])
        )
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Analysis not found"}), 404

        return jsonify({"message": "Analysis deleted"})

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()


@app.errorhandler(413)
def file_too_large(error):
    return jsonify({
        "error": "Upload a PDF smaller than 5 MB"
    }), 413


if __name__ == "__main__":
    app.run(debug=False)