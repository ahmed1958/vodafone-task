import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, redirect, render_template, request, url_for
from dotenv import load_dotenv

from services.ai_provider import AIProviderError, generate_response

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("DATABASE_PATH", BASE_DIR / "prompt_history.db"))
MAX_PROMPT_LENGTH = int(os.getenv("MAX_PROMPT_LENGTH", "5000"))

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS prompt_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                prompt TEXT NOT NULL,
                template TEXT NOT NULL,
                provider_mode TEXT NOT NULL,
                response TEXT,
                status TEXT NOT NULL
            )
            """
        )
        conn.commit()


def save_history(prompt, template, provider_mode, response, status):
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO prompt_history
            (timestamp, prompt, template, provider_mode, response, status)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now(timezone.utc).isoformat(timespec="seconds"),
                prompt,
                template,
                provider_mode,
                response,
                status,
            ),
        )
        conn.commit()


@app.get("/")
def index():
    return render_template("index.html", max_prompt_length=MAX_PROMPT_LENGTH)


@app.post("/api/prompt")
def prompt_api():
    data = request.get_json(silent=True) or request.form

    prompt = (data.get("prompt") or "").strip()
    template_name = (data.get("template") or "general").strip()

    if not prompt:
        return jsonify({"ok": False, "error": "Please enter a prompt."}), 400

    if len(prompt) > MAX_PROMPT_LENGTH:
        return jsonify(
            {
                "ok": False,
                "error": f"Prompt is too long. Maximum length is {MAX_PROMPT_LENGTH} characters.",
            }
        ), 413

    allowed_templates = {"general", "explain", "summarize", "interview"}
    if template_name not in allowed_templates:
        return jsonify({"ok": False, "error": "Invalid prompt template."}), 400

    try:
        result = generate_response(prompt, template_name)
    except AIProviderError as exc:
        save_history(prompt, template_name, os.getenv("AI_PROVIDER", "auto"), "", "provider_error")
        return jsonify(
            {"ok": False, "error": str(exc), "status": "provider_error"}
        ), 502
    except TimeoutError:
        save_history(prompt, template_name, os.getenv("AI_PROVIDER", "auto"), "", "timeout")
        return jsonify(
            {"ok": False, "error": "The AI provider took too long to respond.", "status": "timeout"}
        ), 504
    except Exception:
        app.logger.exception("Unexpected provider failure")
        save_history(prompt, template_name, "unknown", "", "error")
        return jsonify(
            {"ok": False, "error": "Something went wrong while processing the prompt.", "status": "error"}
        ), 500

    save_history(
        prompt,
        template_name,
        result.provider_mode,
        result.text,
        "success",
    )

    return jsonify(
        {
            "ok": True,
            "response": result.text,
            "provider_mode": result.provider_mode,
        }
    )


@app.get("/history")
def history():
    keyword = (request.args.get("q") or "").strip()

    with get_db() as conn:
        if keyword:
            rows = conn.execute(
                """
                SELECT * FROM prompt_history
                WHERE prompt LIKE ? OR response LIKE ? OR template LIKE ?
                ORDER BY id DESC
                LIMIT 100
                """,
                (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT * FROM prompt_history
                ORDER BY id DESC
                LIMIT 100
                """
            ).fetchall()

    return render_template("history.html", rows=rows, keyword=keyword)


@app.errorhandler(404)
def not_found(_):
    return jsonify({"ok": False, "error": "Page not found."}), 404


@app.errorhandler(413)
def too_large(_):
    return jsonify({"ok": False, "error": "Request is too large."}), 413


init_db()

if __name__ == "__main__":
    app.run(
        host=os.getenv("FLASK_HOST", "127.0.0.1"),
        port=int(os.getenv("FLASK_PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "false").lower() == "true",
    )
