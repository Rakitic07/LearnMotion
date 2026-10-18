"""Name + passphrase accounts: bcrypt hashes, a signed session cookie, one-time recovery codes and admin tickets."""

import hashlib
import hmac
import os
import secrets
import threading
import time
from collections import defaultdict, deque
from functools import wraps
from pathlib import Path

import bcrypt
import jwt
from flask import current_app, g, jsonify, request

from . import db

COOKIE_NAME = "learnmotion_session"
MAX_AGE_SECONDS = 60 * 60 * 24 * 30
BCRYPT_ROUNDS = 12
CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"

# Compared against when the account does not exist, so a failed login takes the same time either way.
_DUMMY_HASH = bcrypt.hashpw(secrets.token_bytes(16), bcrypt.gensalt(BCRYPT_ROUNDS))


class AuthConfigError(RuntimeError):
    pass


def _auth_secret() -> bytes:
    secret = current_app.config.get("AUTH_SECRET") or os.environ.get("AUTH_SECRET")
    if secret:
        if len(secret) < 32:
            raise AuthConfigError("AUTH_SECRET must be at least 32 characters.")
        return secret.encode()
    if os.environ.get("VERCEL") or os.environ.get("LEARNMOTION_ENV") == "production":
        raise AuthConfigError("AUTH_SECRET is not set. Add a long random value to the environment.")
    # Local development only: a random per-machine secret kept outside source control.
    path = Path(current_app.instance_path) / "auth_secret"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(secrets.token_urlsafe(48))
        path.chmod(0o600)
    return path.read_text().strip().encode()


def validate_auth_secret() -> None:
    """Fail before a credential-changing request writes data if sessions cannot be signed."""
    _auth_secret()


def admin_secret() -> str | None:
    secret = current_app.config.get("ADMIN_SECRET") or os.environ.get("ADMIN_SECRET")
    return secret if secret and len(secret) >= 16 else None


def secrets_match(provided: str, expected: str) -> bool:
    a = hashlib.sha256(provided.encode()).digest()
    b = hashlib.sha256(expected.encode()).digest()
    return hmac.compare_digest(a, b)


def hash_secret(value: str) -> str:
    return bcrypt.hashpw(value.encode(), bcrypt.gensalt(BCRYPT_ROUNDS)).decode()


def check_secret(value: str, hashed: str | None) -> bool:
    target = hashed.encode() if hashed else _DUMMY_HASH
    ok = bcrypt.checkpw(value.encode(), target)
    return ok and hashed is not None


def _random_code(groups: int, size: int) -> str:
    return "-".join("".join(secrets.choice(CODE_ALPHABET) for _ in range(size)) for _ in range(groups))


def new_recovery_code() -> str:
    return _random_code(4, 4)


def new_ticket() -> str:
    return _random_code(3, 4)


def normalize_code(code: str) -> str:
    return "".join(ch for ch in str(code).upper() if ch.isalnum())


def ticket_hash(ticket: str) -> str:
    return hashlib.sha256(normalize_code(ticket).encode()).hexdigest()


def set_session(response, user) -> None:
    payload = {
        "sub": user["id"],
        "ver": user["session_ver"],
        "iat": int(time.time()),
        "exp": int(time.time()) + MAX_AGE_SECONDS,
    }
    token = jwt.encode(payload, _auth_secret(), algorithm="HS256")
    response.set_cookie(
        COOKIE_NAME, token, max_age=MAX_AGE_SECONDS, httponly=True, samesite="Lax", path="/",
        secure=request.is_secure or bool(os.environ.get("VERCEL")),
    )


def clear_session(response) -> None:
    response.delete_cookie(COOKIE_NAME, path="/", samesite="Lax", httponly=True)


def current_user():
    """The signed-in user row, or None. Tokens are rejected after a passphrase reset bumps session_ver."""
    if "user" in g:
        return g.user
    g.user = None
    token = request.cookies.get(COOKIE_NAME)
    if token:
        try:
            payload = jwt.decode(token, _auth_secret(), algorithms=["HS256"], options={"require": ["sub", "exp"]})
        except jwt.PyJWTError:
            payload = None
        if payload:
            row = db.get().execute("SELECT * FROM users WHERE id = ?", (payload["sub"],)).fetchone()
            if row and row["session_ver"] == payload.get("ver"):
                g.user = row
    return g.user


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if current_user() is None:
            return jsonify({"ok": False, "error": "Please log in first."}), 401
        return view(*args, **kwargs)
    return wrapper


def admin_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        expected = admin_secret()
        if not expected:
            return jsonify({"ok": False, "error": "Admin access is not configured. Set ADMIN_SECRET (16+ characters)."}), 503
        if admin_limiter.blocked("admin-fail"):
            return jsonify({"ok": False, "error": "Too many wrong attempts. Try again in 15 minutes."}), 429
        provided = request.headers.get("X-Admin-Secret", "")
        if not provided or not secrets_match(provided, expected):
            admin_limiter.record("admin-fail")
            return jsonify({"ok": False, "error": "Invalid admin secret."}), 401
        return view(*args, **kwargs)
    return wrapper


class RateLimiter:
    """Sliding-window limit per client IP and bucket. In-memory, so it resets when the process restarts."""

    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window = window_seconds
        self.hits: dict[str, deque] = defaultdict(deque)
        self.lock = threading.Lock()

    def _queue(self, bucket: str) -> deque:
        q = self.hits[f"{bucket}:{request.remote_addr}"]
        cutoff = time.monotonic() - self.window
        while q and q[0] < cutoff:
            q.popleft()
        return q

    def blocked(self, bucket: str) -> bool:
        with self.lock:
            return len(self._queue(bucket)) >= self.limit

    def record(self, bucket: str) -> None:
        with self.lock:
            self._queue(bucket).append(time.monotonic())

    def allow(self, bucket: str) -> bool:
        with self.lock:
            q = self._queue(bucket)
            if len(q) >= self.limit:
                return False
            q.append(time.monotonic())
            return True

    def reset(self) -> None:
        with self.lock:
            self.hits.clear()


auth_limiter = RateLimiter(limit=20, window_seconds=15 * 60)
admin_limiter = RateLimiter(limit=30, window_seconds=15 * 60)
