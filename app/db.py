"""SQLite locally and PostgreSQL when DATABASE_URL is configured."""

import os
import re
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from flask import current_app, g

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id            TEXT PRIMARY KEY,
    name          TEXT NOT NULL,
    name_key      TEXT NOT NULL UNIQUE,
    pass_hash     TEXT NOT NULL,
    recovery_hash TEXT,
    session_ver   INTEGER NOT NULL DEFAULT 1,
    created_at    TEXT NOT NULL,
    last_seen_at  TEXT
);
CREATE TABLE IF NOT EXISTS progress (
    user_id    TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    data       TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS user_settings (
    user_id    TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    data       TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS events (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type       TEXT NOT NULL,
    sid        TEXT,
    topic      TEXT,
    detail     TEXT,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS events_user_time ON events(user_id, created_at);
CREATE INDEX IF NOT EXISTS events_time ON events(created_at);
CREATE INDEX IF NOT EXISTS events_topic ON events(type, sid, topic);
CREATE TABLE IF NOT EXISTS feedback (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    kind        TEXT NOT NULL,
    sid         TEXT,
    topic       TEXT,
    page        TEXT,
    message     TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'open',
    admin_note  TEXT,
    created_at  TEXT NOT NULL,
    resolved_at TEXT
);
CREATE INDEX IF NOT EXISTS feedback_status ON feedback(status, created_at);
CREATE TABLE IF NOT EXISTS reset_requests (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    ticket_hash   TEXT NOT NULL UNIQUE,
    proposed_hash TEXT NOT NULL,
    questionnaire TEXT NOT NULL,
    status        TEXT NOT NULL DEFAULT 'pending',
    created_at    TEXT NOT NULL,
    resolved_at   TEXT
);
CREATE INDEX IF NOT EXISTS reset_status ON reset_requests(status, created_at);
"""

POSTGRES_SCHEMA = SCHEMA.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "BIGSERIAL PRIMARY KEY")


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def days_ago(n: int) -> str:
    d = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=n)
    return d.strftime("%Y-%m-%dT%H:%M:%SZ")


def database_url() -> str | None:
    return current_app.config.get("DATABASE_URL") or os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL")


def default_path() -> str:
    return os.environ.get("LEARNMOTION_DB") or str(Path(current_app.instance_path) / "learnmotion.db")


def _postgres_url(value: str) -> str:
    if value.startswith("postgres://"):
        return "postgresql://" + value[len("postgres://"):]
    return value


class PostgresConnection:
    """Keep the app's small sqlite-style DB API while using psycopg for Postgres."""

    def __init__(self, raw):
        self.raw = raw

    @staticmethod
    def _sql(query: str) -> str:
        # App queries use positional '?' parameters; psycopg uses '%s'.
        return re.sub(r"\?", "%s", query)

    def execute(self, query: str, params=()):
        return self.raw.execute(self._sql(query), params)

    def executemany(self, query: str, params):
        return self.raw.cursor().executemany(self._sql(query), params)

    def commit(self):
        self.raw.commit()

    def close(self):
        self.raw.close()


class HybridRow(dict):
    """Mapping row with positional access to match sqlite3.Row where the app uses it."""

    def __getitem__(self, key):
        if isinstance(key, int):
            return tuple(self.values())[key]
        return super().__getitem__(key)


def _hybrid_row(cursor):
    columns = [column.name for column in cursor.description]
    return lambda values: HybridRow(zip(columns, values))


def connect(path: str | None = None):
    url = database_url()
    if url:
        try:
            import psycopg
        except ImportError as exc:
            raise RuntimeError("DATABASE_URL is set, but psycopg is missing. Install requirements.txt.") from exc
        raw = psycopg.connect(_postgres_url(url), row_factory=_hybrid_row, connect_timeout=10)
        return PostgresConnection(raw)

    if os.environ.get("VERCEL"):
        raise RuntimeError("DATABASE_URL is required on Vercel. Connect a PostgreSQL storage integration and set DATABASE_URL.")
    if not path:
        path = default_path()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def _initialize(conn) -> None:
    if isinstance(conn, PostgresConnection):
        for statement in POSTGRES_SCHEMA.split(";"):
            if statement.strip():
                conn.execute(statement)
        conn.commit()
    else:
        conn.executescript(SCHEMA)


def get():
    if "db" not in g:
        g.db = connect(current_app.config.get("DB_PATH"))
    return g.db


def close(_exc=None) -> None:
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def init_app(app) -> None:
    app.config.setdefault("DB_PATH", None)
    app.config.setdefault("DATABASE_URL", os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL"))
    with app.app_context():
        if not app.config["DB_PATH"] and not app.config["DATABASE_URL"]:
            if os.environ.get("VERCEL"):
                raise RuntimeError("DATABASE_URL is required on Vercel. Connect a PostgreSQL storage integration and set DATABASE_URL.")
            app.config["DB_PATH"] = default_path()
        conn = connect(app.config.get("DB_PATH"))
        _initialize(conn)
        conn.close()
    app.teardown_appcontext(close)
