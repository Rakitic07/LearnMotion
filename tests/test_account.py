import secrets

import pytest

from app import auth, create_app

HEADERS = {"X-K8s-Playground": "1"}
ADMIN = secrets.token_urlsafe(24)


@pytest.fixture()
def app(tmp_path):
    auth.auth_limiter.reset()
    auth.admin_limiter.reset()
    return create_app({"DB_PATH": str(tmp_path / "acct.db"), "AUTH_SECRET": secrets.token_urlsafe(48), "ADMIN_SECRET": ADMIN})


@pytest.fixture()
def client(app):
    return app.test_client()


def post(client, path, body=None, **kw):
    return client.post(path, json=body or {}, headers={**HEADERS, **kw.pop("headers", {})}, **kw)


def admin(client, method, path, body=None):
    headers = {**HEADERS, "X-Admin-Secret": ADMIN}
    if method == "get":
        return client.get(path, headers=headers)
    if method == "delete":
        return client.delete(path, headers=headers)
    return getattr(client, method)(path, json=body or {}, headers=headers)


def signup(client, name="Asha", passphrase="river-stone-42"):
    res = post(client, "/api/auth/register", {"name": name, "passphrase": passphrase})
    assert res.status_code == 201, res.get_json()
    return res.get_json()


def test_register_login_logout_and_me(client):
    data = signup(client)
    assert data["user"]["name"] == "Asha"
    assert len(data["recoveryCode"].split("-")) == 4
    cookie = client.get_cookie("learnmotion_session")
    assert cookie is not None and cookie.http_only and cookie.same_site == "Lax"
    assert client.get("/api/auth/me").get_json()["user"]["name"] == "Asha"

    assert post(client, "/api/auth/logout").status_code == 200
    assert client.get("/api/auth/me").get_json()["authenticated"] is False

    assert post(client, "/api/auth/login", {"name": "asha", "passphrase": "wrong-pass"}).status_code == 401
    assert post(client, "/api/auth/login", {"name": "ghost", "passphrase": "river-stone-42"}).status_code == 401
    assert post(client, "/api/auth/login", {"name": "ASHA", "passphrase": "river-stone-42"}).status_code == 200


def test_register_validation_and_duplicates(client):
    signup(client)
    assert post(client, "/api/auth/register", {"name": "asha", "passphrase": "another-pass"}).status_code == 409
    assert post(client, "/api/auth/register", {"name": "A", "passphrase": "another-pass"}).status_code == 400
    assert post(client, "/api/auth/register", {"name": "Ravi", "passphrase": "short"}).status_code == 400
    assert post(client, "/api/auth/register", {"name": "Ravi", "passphrase": "x" * 65}).status_code == 400
    assert post(client, "/api/auth/register", {"name": "<script>", "passphrase": "another-pass"}).status_code == 400


def test_passphrase_is_hashed_with_bcrypt(app, client):
    signup(client)
    from app import db
    with app.app_context():
        row = db.get().execute("SELECT pass_hash, recovery_hash FROM users").fetchone()
    assert row["pass_hash"].startswith("$2b$12$") and "river-stone-42" not in row["pass_hash"]
    assert row["recovery_hash"].startswith("$2b$12$")


def test_recovery_code_resets_and_rotates(client):
    code = signup(client)["recoveryCode"]
    other = secrets.SystemRandom().choice(["AAAA-BBBB-CCCC-DDDD", "ZZZZ-YYYY-XXXX-WWWW"])
    assert post(client, "/api/auth/recover", {"name": "Asha", "recoveryCode": other, "passphrase": "new-pass-123"}).status_code == 401
    res = post(client, "/api/auth/recover", {"name": "Asha", "recoveryCode": code.lower().replace("-", " "), "passphrase": "new-pass-123"})
    assert res.status_code == 200
    new_code = res.get_json()["recoveryCode"]
    assert new_code != code
    assert post(client, "/api/auth/login", {"name": "Asha", "passphrase": "new-pass-123"}).status_code == 200
    assert post(client, "/api/auth/recover", {"name": "Asha", "recoveryCode": code, "passphrase": "again-pass-1"}).status_code == 401


def test_old_sessions_are_revoked_after_reset(app, client):
    code = signup(client)["recoveryCode"]
    other = app.test_client()
    post(other, "/api/auth/login", {"name": "Asha", "passphrase": "river-stone-42"})
    assert other.get("/api/auth/me").get_json()["authenticated"] is True
    post(client, "/api/auth/recover", {"name": "Asha", "recoveryCode": code, "passphrase": "new-pass-123"})
    assert other.get("/api/auth/me").get_json()["authenticated"] is False
    assert client.get("/api/auth/me").get_json()["authenticated"] is True


def test_admin_reset_request_flow(app, client):
    signup(client)
    post(client, "/api/me/progress", {"data": {"learned:db": ["indexes", "joins"]}})
    post(client, "/api/auth/logout")
    assert post(client, "/api/auth/reset-request", {"name": "Asha", "passphrase": "approved-pass", "questionnaire": {}}).status_code == 400
    assert post(client, "/api/auth/reset-request", {"name": "Nobody", "passphrase": "approved-pass", "questionnaire": {"note": "hi"}}).status_code == 404
    res = post(client, "/api/auth/reset-request", {"name": "Asha", "passphrase": "approved-pass", "questionnaire": {"subjects": "Databases", "topics": "indexes"}})
    ticket = res.get_json()["ticket"]
    status = lambda t=ticket, n="Asha": post(client, "/api/auth/reset-status", {"name": n, "ticket": t})
    assert status().get_json()["status"] == "pending"
    assert status(n="Someone").status_code == 404

    requests = admin(client, "get", "/api/admin/reset-requests").get_json()["requests"]
    assert requests[0]["answers"]["subjects"] == "Databases"
    assert "Databases (2 learned)" in requests[0]["truth"]["subjects"]
    rid = requests[0]["id"]
    assert post(client, "/api/auth/login", {"name": "Asha", "passphrase": "approved-pass"}).status_code == 401
    assert admin(client, "post", f"/api/admin/reset-requests/{rid}", {"action": "approve"}).get_json()["status"] == "approved"
    assert admin(client, "post", f"/api/admin/reset-requests/{rid}", {"action": "reject"}).status_code == 409
    assert status().get_json()["status"] == "approved"
    assert post(client, "/api/auth/login", {"name": "Asha", "passphrase": "approved-pass"}).status_code == 200


def test_progress_sync_whitelists_and_validates(client):
    assert client.get("/api/me/progress").status_code == 401
    signup(client)
    res = post(client, "/api/me/progress", {"data": {
        "learned": ["pods", "pods", "hpa"], "learned:db": ["indexes"], "known-qs:db": ["indexes#0", "scenario#2"],
        "game-best:db": {"rush": 12, "bad": "x"}, "last-visit": {"sid": "db", "topic": "indexes"},
        "theme": {"name": "x"}, "learned:db2": ["<b>"],
    }})
    data = res.get_json()["data"]
    assert data["learned"] == ["hpa", "pods"]
    assert data["known-qs:db"] == ["indexes#0", "scenario#2"]
    assert data["game-best:db"] == {"rush": 12}
    assert "theme" not in data and data["learned:db2"] == []
    post(client, "/api/me/progress", {"data": {"learned": ["pods"]}})
    assert client.get("/api/me/progress").get_json()["data"]["learned"] == ["pods"]
    assert client.get("/api/me/progress").get_json()["data"]["learned:db"] == ["indexes"]


def test_settings_are_saved_per_user_and_validated(client):
    assert client.get("/api/me/settings").status_code == 401
    user = signup(client)["user"]
    assert client.get("/api/me/settings").get_json()["settings"] == {"animSpeed": 1.0}
    for bad in (0.05, 2.5, "fast", True, None):
        res = post(client, "/api/me/settings", {"settings": {"animSpeed": bad}})
        assert res.status_code == 400, bad
    res = post(client, "/api/me/settings", {"settings": {"animSpeed": 0.333, "theme": "x"}})
    assert res.get_json()["settings"] == {"animSpeed": 0.33}
    for edge in (0.1, 2):
        assert post(client, "/api/me/settings", {"settings": {"animSpeed": edge}}).status_code == 200
    post(client, "/api/auth/logout")
    post(client, "/api/auth/login", {"name": "Asha", "passphrase": "river-stone-42"})
    assert client.get("/api/me/settings").get_json()["settings"]["animSpeed"] == 2.0
    assert admin(client, "get", f"/api/admin/users/{user['id']}").get_json()["settings"]["animSpeed"] == 2.0
    signup(client, name="Ben")
    assert client.get("/api/me/settings").get_json()["settings"]["animSpeed"] == 1.0


def test_events_feedback_and_admin_views(client):
    assert post(client, "/api/feedback", {"kind": "bug", "message": "hello there"}).status_code == 401
    user = signup(client)["user"]
    post(client, "/api/me/progress", {"data": {"learned:db": ["indexes"]}})
    res = post(client, "/api/events", {"events": [
        {"type": "view_topic", "sid": "db", "topic": "indexes"},
        {"type": "view_tab", "sid": "db", "detail": "lab"},
        {"type": "search", "detail": "kafka"},
        {"type": "hack", "sid": "db"},
        {"type": "view_topic", "sid": "nope", "topic": "<x>"},
    ]})
    assert res.get_json()["saved"] == 4
    assert post(client, "/api/feedback", {"kind": "missing_topic", "message": "no"}).status_code == 400
    fb = post(client, "/api/feedback", {"kind": "missing_topic", "message": "Please add Kafka streams", "sid": "sysdesign", "page": "#/sysdesign"})
    assert fb.status_code == 201
    fid = fb.get_json()["feedback"]["id"]

    m = admin(client, "get", "/api/admin/metrics").get_json()
    assert m["totals"]["users"] == 1 and m["totals"]["feedbackOpen"] == 1 and m["totals"]["topicsLearned"] == 1
    assert m["topViewed"][0]["title"] and m["topViewed"][0]["topic"] == "indexes"
    assert m["topLearned"][0]["topic"] == "indexes"
    assert m["searches"][0]["query"] == "kafka"

    users = admin(client, "get", "/api/admin/users?q=as").get_json()["users"]
    assert users[0]["name"] == "Asha" and users[0]["learned"] == 1
    detail = admin(client, "get", f"/api/admin/users/{user['id']}").get_json()
    assert detail["progress"][0]["learned"][0]["id"] == "indexes"
    assert {e["type"] for e in detail["events"]} == {"view_topic", "view_tab", "search"}

    items = admin(client, "get", "/api/admin/feedback").get_json()["feedback"]
    assert items[0]["message"] == "Please add Kafka streams" and items[0]["user"]["name"] == "Asha"
    upd = admin(client, "patch", f"/api/admin/feedback/{fid}", {"status": "resolved", "note": "Added in the next release"})
    assert upd.get_json()["feedback"]["status"] == "resolved"
    mine = client.get("/api/me/feedback").get_json()["feedback"]
    assert mine[0]["adminNote"] == "Added in the next release"

    assert admin(client, "delete", f"/api/admin/users/{user['id']}").status_code == 200
    assert client.get("/api/auth/me").get_json()["authenticated"] is False


def test_admin_gate(app, client):
    assert client.get("/api/admin/metrics").status_code == 401
    assert client.get("/api/admin/metrics", headers={"X-Admin-Secret": "wrong-secret-value"}).status_code == 401
    assert client.get("/admin").status_code == 200
    bare = create_app({"DB_PATH": app.config["DB_PATH"], "ADMIN_SECRET": ""}).test_client()
    assert bare.get("/api/admin/metrics", headers={"X-Admin-Secret": "anything"}).status_code in {401, 503}


def test_admin_lockout_after_failures(client):
    for _ in range(30):
        client.get("/api/admin/metrics", headers={"X-Admin-Secret": "nope"})
    assert client.get("/api/admin/metrics", headers={"X-Admin-Secret": ADMIN}).status_code == 429


def test_login_rate_limit(client):
    codes = [post(client, "/api/auth/login", {"name": "x1", "passphrase": "whatever"}).status_code for _ in range(21)]
    assert codes[-1] == 429


def test_state_changes_need_csrf_header(client):
    assert client.post("/api/auth/register", json={"name": "Asha", "passphrase": "river-stone-42"}).status_code == 403
    assert client.delete("/api/admin/users/x", headers={"X-Admin-Secret": ADMIN}).status_code == 403
