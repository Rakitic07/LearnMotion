"""Account API: sign up, log in, recovery, admin-approved resets, progress sync, activity events and feedback."""

import json
import re
import secrets

from flask import Blueprint, jsonify, make_response, request

from . import auth, db, subjects

bp = Blueprint("account", __name__)

NAME_RE = re.compile(r"^[\w .'-]{2,40}$", re.UNICODE)
TOPIC_RE = re.compile(r"^[a-z0-9-]{1,80}$")
ITEM_RE = re.compile(r"^[a-z0-9-]{1,80}(#\d{1,4})?$")
PROGRESS_KEY_RE = re.compile(r"^(learned|known-qs|game-best)(:[a-z0-9]{1,20})?$|^last-visit$")
MAX_PROGRESS_BYTES = 200_000
EVENT_TYPES = {"view_topic", "view_tab", "learned", "unlearned", "run_code", "game_done", "search"}
FEEDBACK_KINDS = {"missing_topic", "content_error", "bug", "idea", "other"}
MAX_EVENTS_PER_BATCH = 40


class Invalid(ValueError):
    pass


@bp.errorhandler(Invalid)
def handle_invalid(exc):
    return jsonify({"ok": False, "error": str(exc)}), 400


@bp.errorhandler(auth.AuthConfigError)
def handle_config(exc):
    return jsonify({"ok": False, "error": str(exc)}), 503


def _body() -> dict:
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


def _name(body) -> str:
    name = " ".join(str(body.get("name", "")).split())
    if not NAME_RE.match(name):
        raise Invalid("Name must be 2-40 characters: letters, numbers, spaces, dots, dashes or apostrophes.")
    return name


def _passphrase(body, key="passphrase") -> str:
    value = str(body.get(key, ""))
    if len(value) < 6:
        raise Invalid("Passphrase must be at least 6 characters.")
    if len(value) > 64 or len(value.encode()) > 72:
        raise Invalid("Passphrase is too long (64 characters max).")
    return value


def _text(value, limit: int) -> str:
    return str(value or "").strip()[:limit]


def _sid(value) -> str | None:
    sid = str(value or "")
    return sid if subjects.subject(sid) else None


def _topic(value) -> str | None:
    topic = str(value or "")
    return topic if TOPIC_RE.match(topic) else None


def _limited(bucket: str):
    if not auth.auth_limiter.allow(bucket):
        return jsonify({"ok": False, "error": "Too many attempts. Wait a few minutes and try again."}), 429
    return None


def public_user(row) -> dict:
    return {"id": row["id"], "name": row["name"], "createdAt": row["created_at"]}


def _signed_in(row, status=200, **extra):
    response = make_response(jsonify({"ok": True, "user": public_user(row), **extra}), status)
    auth.set_session(response, row)
    return response


def _user_by_name(name: str):
    return db.get().execute("SELECT * FROM users WHERE name_key = ?", (name.lower(),)).fetchone()


@bp.post("/api/auth/register")
def register():
    if (blocked := _limited("register")):
        return blocked
    auth.validate_auth_secret()
    body = _body()
    name, passphrase = _name(body), _passphrase(body)
    conn = db.get()
    if _user_by_name(name):
        return jsonify({"ok": False, "error": "That name is already taken. Log in with its passphrase instead."}), 409
    code = auth.new_recovery_code()
    user_id = secrets.token_hex(12)
    conn.execute(
        "INSERT INTO users (id, name, name_key, pass_hash, recovery_hash, created_at, last_seen_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (user_id, name, name.lower(), auth.hash_secret(passphrase), auth.hash_secret(auth.normalize_code(code)), db.now(), db.now()),
    )
    conn.commit()
    return _signed_in(conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone(), 201, recoveryCode=code)


@bp.post("/api/auth/login")
def login():
    if (blocked := _limited("login")):
        return blocked
    auth.validate_auth_secret()
    body = _body()
    name = " ".join(str(body.get("name", "")).split())
    passphrase = str(body.get("passphrase", ""))[:128]
    row = _user_by_name(name) if name else None
    if not auth.check_secret(passphrase, row["pass_hash"] if row else None):
        return jsonify({"ok": False, "error": "Incorrect name or passphrase."}), 401
    conn = db.get()
    conn.execute("UPDATE users SET last_seen_at = ? WHERE id = ?", (db.now(), row["id"]))
    conn.commit()
    return _signed_in(row)


@bp.post("/api/auth/recover")
def recover():
    if (blocked := _limited("recover")):
        return blocked
    auth.validate_auth_secret()
    body = _body()
    name = " ".join(str(body.get("name", "")).split())
    code = auth.normalize_code(_text(body.get("recoveryCode"), 64))
    passphrase = _passphrase(body)
    row = _user_by_name(name) if name else None
    if not code or not auth.check_secret(code, row["recovery_hash"] if row else None):
        return jsonify({"ok": False, "error": "Incorrect name or recovery code."}), 401
    new_code = auth.new_recovery_code()
    conn = db.get()
    conn.execute(
        "UPDATE users SET pass_hash = ?, recovery_hash = ?, session_ver = session_ver + 1, last_seen_at = ? WHERE id = ?",
        (auth.hash_secret(passphrase), auth.hash_secret(auth.normalize_code(new_code)), db.now(), row["id"]),
    )
    conn.commit()
    return _signed_in(conn.execute("SELECT * FROM users WHERE id = ?", (row["id"],)).fetchone(), recoveryCode=new_code)


@bp.post("/api/auth/reset-request")
def reset_request():
    """Ask the admin to reset the passphrase. Only the hash of the proposed passphrase is stored until approval."""
    if (blocked := _limited("reset-request")):
        return blocked
    body = _body()
    name, passphrase = _name(body), _passphrase(body)
    raw = body.get("questionnaire") if isinstance(body.get("questionnaire"), dict) else {}
    questionnaire = {k: _text(raw.get(k), 300) for k in ("subjects", "topics", "joined", "note")}
    if not any(questionnaire.values()):
        raise Invalid("Answer at least one question so the admin can verify it is you.")
    row = _user_by_name(name)
    if not row:
        return jsonify({"ok": False, "error": "No LearnMotion account uses that name."}), 404
    ticket = auth.new_ticket()
    conn = db.get()
    conn.execute("DELETE FROM reset_requests WHERE user_id = ? AND status = 'pending'", (row["id"],))
    conn.execute(
        "INSERT INTO reset_requests (user_id, ticket_hash, proposed_hash, questionnaire, created_at) VALUES (?, ?, ?, ?, ?)",
        (row["id"], auth.ticket_hash(ticket), auth.hash_secret(passphrase), json.dumps(questionnaire), db.now()),
    )
    conn.commit()
    return jsonify({"ok": True, "ticket": ticket}), 201


@bp.post("/api/auth/reset-status")
def reset_status():
    if (blocked := _limited("reset-status")):
        return blocked
    body = _body()
    name = " ".join(str(body.get("name", "")).split()).lower()
    row = db.get().execute(
        "SELECT r.status, r.resolved_at, u.name_key FROM reset_requests r JOIN users u ON u.id = r.user_id WHERE r.ticket_hash = ?",
        (auth.ticket_hash(_text(body.get("ticket"), 64)),),
    ).fetchone()
    if not row or row["name_key"] != name:
        return jsonify({"ok": False, "error": "No request found for that name and ticket."}), 404
    return jsonify({"ok": True, "status": row["status"], "resolvedAt": row["resolved_at"]})


@bp.get("/api/auth/me")
def me():
    user = auth.current_user()
    return jsonify({"authenticated": bool(user), "user": public_user(user) if user else None})


@bp.post("/api/auth/logout")
def logout():
    response = make_response(jsonify({"ok": True}))
    auth.clear_session(response)
    return response


def _load_progress(user_id: str) -> dict:
    row = db.get().execute("SELECT data FROM progress WHERE user_id = ?", (user_id,)).fetchone()
    return json.loads(row["data"]) if row else {}


def _clean_progress_value(key: str, value):
    if key.startswith(("learned", "known-qs")):
        if not isinstance(value, list):
            raise Invalid(f"{key} must be a list.")
        return sorted({str(v) for v in value if ITEM_RE.match(str(v))})[:2000]
    if key.startswith("game-best"):
        if not isinstance(value, dict):
            raise Invalid(f"{key} must be an object.")
        return {str(k)[:40]: v for k, v in list(value.items())[:50] if isinstance(v, (int, float)) and not isinstance(v, bool)}
    if not isinstance(value, dict):
        raise Invalid("last-visit must be an object.")
    return {"sid": _sid(value.get("sid")), "topic": _topic(value.get("topic"))}


@bp.get("/api/me/progress")
@auth.login_required
def get_progress():
    return jsonify({"ok": True, "data": _load_progress(auth.current_user()["id"])})


@bp.post("/api/me/progress")
@auth.login_required
def save_progress():
    """Replaces the keys sent; other keys stay as they are. The client merges local and server data on login."""
    incoming = _body().get("data")
    if not isinstance(incoming, dict):
        raise Invalid("data must be an object.")
    user_id = auth.current_user()["id"]
    data = _load_progress(user_id)
    for key, value in incoming.items():
        if not PROGRESS_KEY_RE.match(str(key)):
            continue
        data[key] = _clean_progress_value(key, value)
    blob = json.dumps(data, separators=(",", ":"))
    if len(blob) > MAX_PROGRESS_BYTES:
        raise Invalid("Progress data is too large.")
    conn = db.get()
    conn.execute(
        "INSERT INTO progress (user_id, data, updated_at) VALUES (?, ?, ?) "
        "ON CONFLICT(user_id) DO UPDATE SET data = excluded.data, updated_at = excluded.updated_at",
        (user_id, blob, db.now()),
    )
    conn.execute("UPDATE users SET last_seen_at = ? WHERE id = ?", (db.now(), user_id))
    conn.commit()
    return jsonify({"ok": True, "data": data})


DEFAULT_SETTINGS = {"animSpeed": 1.0}
ANIM_SPEED_RANGE = (0.1, 2.0)


def load_settings(user_id: str) -> dict:
    row = db.get().execute("SELECT data FROM user_settings WHERE user_id = ?", (user_id,)).fetchone()
    return {**DEFAULT_SETTINGS, **(json.loads(row["data"]) if row else {})}


def _anim_speed(value) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise Invalid("Animation speed must be a number.")
    low, high = ANIM_SPEED_RANGE
    if not low <= value <= high:
        raise Invalid(f"Animation speed must be between {low}x and {high}x.")
    return round(float(value), 2)


@bp.get("/api/me/settings")
@auth.login_required
def get_settings():
    return jsonify({"ok": True, "settings": load_settings(auth.current_user()["id"])})


@bp.post("/api/me/settings")
@auth.login_required
def save_settings():
    incoming = _body().get("settings")
    if not isinstance(incoming, dict):
        raise Invalid("settings must be an object.")
    user_id = auth.current_user()["id"]
    settings = load_settings(user_id)
    if "animSpeed" in incoming:
        settings["animSpeed"] = _anim_speed(incoming["animSpeed"])
    conn = db.get()
    conn.execute(
        "INSERT INTO user_settings (user_id, data, updated_at) VALUES (?, ?, ?) "
        "ON CONFLICT(user_id) DO UPDATE SET data = excluded.data, updated_at = excluded.updated_at",
        (user_id, json.dumps(settings, separators=(",", ":")), db.now()),
    )
    conn.commit()
    return jsonify({"ok": True, "settings": settings})


@bp.post("/api/events")
@auth.login_required
def record_events():
    events = _body().get("events")
    if not isinstance(events, list):
        raise Invalid("events must be a list.")
    rows = []
    user_id = auth.current_user()["id"]
    for e in events[:MAX_EVENTS_PER_BATCH]:
        if not isinstance(e, dict) or e.get("type") not in EVENT_TYPES:
            continue
        rows.append((user_id, e["type"], _sid(e.get("sid")), _topic(e.get("topic")), _text(e.get("detail"), 120) or None, db.now()))
    conn = db.get()
    if rows:
        conn.executemany("INSERT INTO events (user_id, type, sid, topic, detail, created_at) VALUES (?, ?, ?, ?, ?, ?)", rows)
    conn.execute("UPDATE users SET last_seen_at = ? WHERE id = ?", (db.now(), user_id))
    conn.commit()
    return jsonify({"ok": True, "saved": len(rows)})


def feedback_row(r) -> dict:
    return {
        "id": r["id"], "kind": r["kind"], "sid": r["sid"], "topic": r["topic"], "page": r["page"],
        "message": r["message"], "status": r["status"], "adminNote": r["admin_note"],
        "createdAt": r["created_at"], "resolvedAt": r["resolved_at"],
    }


@bp.post("/api/feedback")
@auth.login_required
def send_feedback():
    if (blocked := _limited("feedback")):
        return blocked
    body = _body()
    kind = body.get("kind") if body.get("kind") in FEEDBACK_KINDS else "other"
    message = _text(body.get("message"), 2000)
    if len(message) < 5:
        raise Invalid("Please write a few words so we know what to fix or add.")
    conn = db.get()
    cur = conn.execute(
        "INSERT INTO feedback (user_id, kind, sid, topic, page, message, created_at) VALUES (?, ?, ?, ?, ?, ?, ?) RETURNING id",
        (auth.current_user()["id"], kind, _sid(body.get("sid")), _topic(body.get("topic")), _text(body.get("page"), 200) or None, message, db.now()),
    )
    feedback_id = cur.fetchone()["id"]
    conn.commit()
    return jsonify({"ok": True, "feedback": feedback_row(conn.execute("SELECT * FROM feedback WHERE id = ?", (feedback_id,)).fetchone())}), 201


@bp.get("/api/me/feedback")
@auth.login_required
def my_feedback():
    rows = db.get().execute(
        "SELECT * FROM feedback WHERE user_id = ? ORDER BY created_at DESC, id DESC LIMIT 50", (auth.current_user()["id"],),
    ).fetchall()
    return jsonify({"ok": True, "feedback": [feedback_row(r) for r in rows]})
