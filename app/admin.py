"""Admin panel page and API: usage metrics, users and their progress, activity feed, feedback triage and reset approvals."""

import json
from collections import Counter
from functools import lru_cache

from flask import Blueprint, jsonify, render_template, request

from . import auth, db, subjects
from .account import Invalid, feedback_row, load_settings

bp = Blueprint("admin", __name__)

FEEDBACK_STATUSES = {"open", "in_progress", "resolved", "wontfix"}


@bp.errorhandler(Invalid)
def handle_invalid(exc):
    return jsonify({"ok": False, "error": str(exc)}), 400


@lru_cache(maxsize=1)
def _titles() -> dict:
    return {(r["sid"], r["id"]): r["title"] for r in subjects.search_index()}


def _subject_name(sid) -> str:
    s = subjects.subject(sid or "")
    return s["name"] if s else (sid or "")


def _topic_title(sid, topic) -> str | None:
    return _titles().get((sid, topic)) if topic else None


def _event(r) -> dict:
    return {
        "id": r["id"], "type": r["type"], "sid": r["sid"], "subject": _subject_name(r["sid"]) if r["sid"] else None,
        "topic": r["topic"], "topicTitle": _topic_title(r["sid"], r["topic"]), "detail": r["detail"],
        "createdAt": r["created_at"], **({"user": {"id": r["user_id"], "name": r["name"]}} if "name" in r.keys() else {}),
    }


def _learned_by_subject(data: dict) -> dict:
    out = {}
    for key, value in data.items():
        if key == "learned" or key.startswith("learned:"):
            out[key.split(":", 1)[1] if ":" in key else "k8s"] = value
    return out


def _known_by_subject(data: dict) -> dict:
    out = {}
    for key, value in data.items():
        if key == "known-qs" or key.startswith("known-qs:"):
            out[key.split(":", 1)[1] if ":" in key else "k8s"] = len(value)
    return out


def _progress_map(conn) -> dict:
    return {r["user_id"]: json.loads(r["data"]) for r in conn.execute("SELECT user_id, data FROM progress")}


def _series(rows, days: int) -> list:
    buckets = {db.days_ago(i)[:10]: 0 for i in range(days - 1, -1, -1)}
    for r in rows:
        day = r[0][:10]
        if day in buckets:
            buckets[day] += 1
    return [{"date": d, "count": c} for d, c in buckets.items()]


@bp.get("/admin")
def admin_page():
    return render_template("admin.html")


@bp.get("/api/admin/metrics")
@auth.admin_required
def metrics():
    conn = db.get()
    d1, d7, d14, d30 = db.days_ago(0), db.days_ago(7), db.days_ago(13), db.days_ago(30)
    scalar = lambda sql, *args: conn.execute(sql, args).fetchone()[0]
    progress = _progress_map(conn)

    learned_topics = Counter()
    learners = Counter()
    for data in progress.values():
        for sid, ids in _learned_by_subject(data).items():
            if ids:
                learners[sid] += 1
            learned_topics.update((sid, t) for t in ids)

    views = conn.execute(
        "SELECT sid, topic, COUNT(*) AS n, COUNT(DISTINCT user_id) AS u FROM events "
        "WHERE type = 'view_topic' AND created_at >= ? AND topic IS NOT NULL GROUP BY sid, topic ORDER BY n DESC LIMIT 15", (d30,),
    ).fetchall()
    subject_views = {r["sid"]: r["n"] for r in conn.execute(
        "SELECT sid, COUNT(*) AS n FROM events WHERE created_at >= ? AND sid IS NOT NULL GROUP BY sid", (d30,))}
    tabs = conn.execute(
        "SELECT detail, COUNT(*) AS n FROM events WHERE type = 'view_tab' AND created_at >= ? GROUP BY detail ORDER BY n DESC", (d30,),
    ).fetchall()
    searches = conn.execute(
        "SELECT detail, COUNT(*) AS n FROM events WHERE type = 'search' AND created_at >= ? AND detail IS NOT NULL "
        "GROUP BY lower(detail) ORDER BY n DESC LIMIT 10", (d30,),
    ).fetchall()
    recent = conn.execute(
        "SELECT e.*, u.name FROM events e JOIN users u ON u.id = e.user_id ORDER BY e.created_at DESC, e.id DESC LIMIT 25",
    ).fetchall()
    active_by_day = conn.execute(
        "SELECT substr(created_at, 1, 10) AS day, COUNT(DISTINCT user_id) AS n FROM events WHERE created_at >= ? GROUP BY day", (d14,),
    ).fetchall()
    active_map = {r["day"]: r["n"] for r in active_by_day}
    activity = _series(conn.execute("SELECT created_at FROM events WHERE created_at >= ?", (d14,)).fetchall(), 14)
    for point in activity:
        point["activeUsers"] = active_map.get(point["date"], 0)

    return jsonify({
        "ok": True,
        "generatedAt": db.now(),
        "totals": {
            "users": scalar("SELECT COUNT(*) FROM users"),
            "activeToday": scalar("SELECT COUNT(*) FROM users WHERE last_seen_at >= ?", d1),
            "active7": scalar("SELECT COUNT(*) FROM users WHERE last_seen_at >= ?", d7),
            "newUsers7": scalar("SELECT COUNT(*) FROM users WHERE created_at >= ?", d7),
            "events7": scalar("SELECT COUNT(*) FROM events WHERE created_at >= ?", d7),
            "topicsLearned": sum(learned_topics.values()),
            "feedbackOpen": scalar("SELECT COUNT(*) FROM feedback WHERE status IN ('open', 'in_progress')"),
            "feedbackTotal": scalar("SELECT COUNT(*) FROM feedback"),
            "resetPending": scalar("SELECT COUNT(*) FROM reset_requests WHERE status = 'pending'"),
        },
        "signups": _series(conn.execute("SELECT created_at FROM users WHERE created_at >= ?", (d14,)).fetchall(), 14),
        "activity": activity,
        "subjects": sorted(
            [{"sid": s["id"], "name": s["name"], "learners": learners.get(s["id"], 0), "views30": subject_views.get(s["id"], 0),
              "learned": sum(n for (sid, _), n in learned_topics.items() if sid == s["id"])} for s in subjects.SUBJECTS],
            key=lambda s: (-s["views30"], -s["learners"], s["name"]),
        ),
        "topViewed": [{"sid": r["sid"], "subject": _subject_name(r["sid"]), "topic": r["topic"],
                       "title": _topic_title(r["sid"], r["topic"]) or r["topic"], "views": r["n"], "users": r["u"]} for r in views],
        "topLearned": [{"sid": sid, "subject": _subject_name(sid), "topic": t, "title": _topic_title(sid, t) or t, "learners": n}
                       for (sid, t), n in learned_topics.most_common(15)],
        "tabs": [{"tab": r["detail"] or "learn", "views": r["n"]} for r in tabs],
        "searches": [{"query": r["detail"], "count": r["n"]} for r in searches],
        "recent": [_event(r) for r in recent],
    })


@bp.get("/api/admin/users")
@auth.admin_required
def users():
    conn = db.get()
    q = " ".join(request.args.get("q", "").split()).lower()[:40]
    rows = conn.execute(
        "SELECT u.*, (SELECT COUNT(*) FROM events e WHERE e.user_id = u.id) AS events, "
        "(SELECT COUNT(*) FROM feedback f WHERE f.user_id = u.id) AS feedback "
        "FROM users u WHERE u.name_key LIKE ? ESCAPE ? ORDER BY COALESCE(u.last_seen_at, u.created_at) DESC LIMIT 200",
        ("%" + q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%", "\\"),
    ).fetchall()
    progress = _progress_map(conn)
    out = []
    for r in rows:
        learned = _learned_by_subject(progress.get(r["id"], {}))
        out.append({
            "id": r["id"], "name": r["name"], "createdAt": r["created_at"], "lastSeenAt": r["last_seen_at"],
            "events": r["events"], "feedback": r["feedback"], "learned": sum(len(v) for v in learned.values()),
            "subjects": sorted(({"sid": sid, "name": _subject_name(sid), "learned": len(ids)} for sid, ids in learned.items() if ids),
                               key=lambda s: -s["learned"]),
        })
    return jsonify({"ok": True, "users": out})


@bp.get("/api/admin/users/<user_id>")
@auth.admin_required
def user_detail(user_id):
    conn = db.get()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not row:
        return jsonify({"ok": False, "error": "User not found."}), 404
    data = _progress_map(conn).get(user_id, {})
    learned, known = _learned_by_subject(data), _known_by_subject(data)
    summaries = {s["id"]: s for s in subjects.summaries()}
    progress = []
    for s in subjects.SUBJECTS:
        ids = learned.get(s["id"], [])
        if ids or known.get(s["id"]):
            progress.append({
                "sid": s["id"], "name": s["name"], "total": summaries.get(s["id"], {}).get("topics", 0), "known": known.get(s["id"], 0),
                "learned": [{"id": t, "title": _topic_title(s["id"], t) or t} for t in ids],
            })
    events = conn.execute("SELECT * FROM events WHERE user_id = ? ORDER BY created_at DESC, id DESC LIMIT 200", (user_id,)).fetchall()
    feedback = conn.execute("SELECT * FROM feedback WHERE user_id = ? ORDER BY created_at DESC", (user_id,)).fetchall()
    return jsonify({
        "ok": True,
        "user": {"id": row["id"], "name": row["name"], "createdAt": row["created_at"], "lastSeenAt": row["last_seen_at"]},
        "progress": progress,
        "lastVisit": data.get("last-visit"),
        "settings": load_settings(user_id),
        "events": [_event(e) for e in events],
        "feedback": [feedback_row(f) for f in feedback],
    })


@bp.delete("/api/admin/users/<user_id>")
@auth.admin_required
def delete_user(user_id):
    conn = db.get()
    cur = conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    if not cur.rowcount:
        return jsonify({"ok": False, "error": "User not found."}), 404
    return jsonify({"ok": True})


@bp.get("/api/admin/events")
@auth.admin_required
def events():
    clauses, args = [], []
    for column, key in (("e.user_id", "user"), ("e.type", "type"), ("e.sid", "sid")):
        if request.args.get(key):
            clauses.append(f"{column} = ?")
            args.append(request.args[key][:40])
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    limit = max(1, min(int(request.args.get("limit", 100) or 100), 500))
    rows = db.get().execute(
        f"SELECT e.*, u.name FROM events e JOIN users u ON u.id = e.user_id {where} ORDER BY e.created_at DESC, e.id DESC LIMIT ?",
        (*args, limit),
    ).fetchall()
    return jsonify({"ok": True, "events": [_event(r) for r in rows]})


@bp.get("/api/admin/feedback")
@auth.admin_required
def feedback_list():
    status = request.args.get("status", "")
    where, args = ("WHERE f.status = ?", (status,)) if status in FEEDBACK_STATUSES else ("", ())
    rows = db.get().execute(
        f"SELECT f.*, u.name, u.id AS uid FROM feedback f JOIN users u ON u.id = f.user_id {where} "
        "ORDER BY CASE f.status WHEN 'open' THEN 0 WHEN 'in_progress' THEN 1 ELSE 2 END, f.created_at DESC LIMIT 300",
        args,
    ).fetchall()
    return jsonify({"ok": True, "feedback": [
        {**feedback_row(r), "user": {"id": r["uid"], "name": r["name"]}, "subject": _subject_name(r["sid"]) if r["sid"] else None,
         "topicTitle": _topic_title(r["sid"], r["topic"])} for r in rows
    ]})


@bp.patch("/api/admin/feedback/<int:feedback_id>")
@auth.admin_required
def feedback_update(feedback_id):
    body = request.get_json(silent=True) or {}
    status = body.get("status")
    if status not in FEEDBACK_STATUSES:
        raise Invalid("status must be open, in_progress, resolved or wontfix.")
    note = str(body.get("note") or "").strip()[:1000] or None
    conn = db.get()
    resolved = db.now() if status in {"resolved", "wontfix"} else None
    cur = conn.execute("UPDATE feedback SET status = ?, admin_note = ?, resolved_at = ? WHERE id = ?", (status, note, resolved, feedback_id))
    conn.commit()
    if not cur.rowcount:
        return jsonify({"ok": False, "error": "Feedback not found."}), 404
    return jsonify({"ok": True, "feedback": feedback_row(conn.execute("SELECT * FROM feedback WHERE id = ?", (feedback_id,)).fetchone())})


@bp.get("/api/admin/reset-requests")
@auth.admin_required
def reset_requests():
    conn = db.get()
    rows = conn.execute(
        "SELECT r.*, u.name, u.created_at AS joined, u.last_seen_at FROM reset_requests r JOIN users u ON u.id = r.user_id "
        "ORDER BY CASE r.status WHEN 'pending' THEN 0 ELSE 1 END, r.created_at DESC LIMIT 100",
    ).fetchall()
    progress = _progress_map(conn)
    out = []
    for r in rows:
        learned = _learned_by_subject(progress.get(r["user_id"], {}))
        recent = conn.execute(
            "SELECT sid, topic, MAX(created_at) AS last_seen FROM events "
            "WHERE user_id = ? AND type = 'view_topic' GROUP BY sid, topic ORDER BY last_seen DESC LIMIT 8", (r["user_id"],),
        ).fetchall()
        out.append({
            "id": r["id"], "status": r["status"], "createdAt": r["created_at"], "resolvedAt": r["resolved_at"],
            "answers": json.loads(r["questionnaire"]),
            "user": {"id": r["user_id"], "name": r["name"], "joined": r["joined"], "lastSeenAt": r["last_seen_at"]},
            "truth": {
                "subjects": [f"{_subject_name(sid)} ({len(ids)} learned)" for sid, ids in learned.items() if ids],
                "recentTopics": [_topic_title(e["sid"], e["topic"]) or e["topic"] for e in recent],
            },
        })
    return jsonify({"ok": True, "requests": out})


@bp.post("/api/admin/reset-requests/<int:request_id>")
@auth.admin_required
def resolve_reset(request_id):
    action = (request.get_json(silent=True) or {}).get("action")
    if action not in {"approve", "reject"}:
        raise Invalid("action must be approve or reject.")
    conn = db.get()
    row = conn.execute("SELECT * FROM reset_requests WHERE id = ?", (request_id,)).fetchone()
    if not row:
        return jsonify({"ok": False, "error": "Request not found."}), 404
    if row["status"] != "pending":
        return jsonify({"ok": False, "error": f"Already {row['status']}."}), 409
    if action == "approve":
        conn.execute("UPDATE users SET pass_hash = ?, session_ver = session_ver + 1 WHERE id = ?", (row["proposed_hash"], row["user_id"]))
    status = "approved" if action == "approve" else "rejected"
    conn.execute("UPDATE reset_requests SET status = ?, resolved_at = ? WHERE id = ?", (status, db.now(), request_id))
    conn.commit()
    return jsonify({"ok": True, "status": status})
