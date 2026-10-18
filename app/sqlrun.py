"""Runs learner SQL against a fresh in-memory SQLite database seeded with a small shop dataset."""

from __future__ import annotations

import re
import sqlite3
import time

MAX_SQL = 20_000
MAX_STATEMENTS = 40
MAX_ROWS = 200
TIME_LIMIT = 3.0

SEED = """
CREATE TABLE customers (
  id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL,
  city TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE products (
  id INTEGER PRIMARY KEY, name TEXT NOT NULL, category TEXT NOT NULL, price REAL NOT NULL CHECK (price > 0)
);
CREATE TABLE orders (
  id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL REFERENCES customers(id),
  status TEXT NOT NULL CHECK (status IN ('pending','paid','shipped','cancelled')), created_at TEXT NOT NULL
);
CREATE TABLE order_items (
  order_id INTEGER NOT NULL REFERENCES orders(id), product_id INTEGER NOT NULL REFERENCES products(id),
  qty INTEGER NOT NULL CHECK (qty > 0), unit_price REAL NOT NULL,
  PRIMARY KEY (order_id, product_id)
);
CREATE TABLE employees (
  id INTEGER PRIMARY KEY, name TEXT NOT NULL, title TEXT NOT NULL, dept TEXT NOT NULL,
  salary INTEGER NOT NULL, manager_id INTEGER REFERENCES employees(id)
);
CREATE TABLE accounts (id INTEGER PRIMARY KEY, owner TEXT NOT NULL, balance INTEGER NOT NULL CHECK (balance >= 0));
CREATE TABLE events (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, kind TEXT NOT NULL, ts INTEGER NOT NULL);

INSERT INTO customers VALUES
 (1,'Asha Rao','asha@example.com','Bengaluru','2024-01-05'),
 (2,'Ben Carter','ben@example.com','London','2024-01-19'),
 (3,'Chen Wei','chen@example.com','Singapore','2024-02-02'),
 (4,'Diya Shah','diya@example.com','Mumbai','2024-02-14'),
 (5,'Eli Novak','eli@example.com','Berlin','2024-03-01'),
 (6,'Fatima Khan','fatima@example.com','Bengaluru','2024-03-22'),
 (7,'Goro Sato','goro@example.com','Tokyo','2024-04-10'),
 (8,'Hana Park','hana@example.com','Seoul','2024-05-03'),
 (9,'Ivan Petrov','ivan@example.com','Berlin','2024-05-28'),
 (10,'Jaya Iyer','jaya@example.com','Chennai','2024-06-15'),
 (11,'Kiran Das','kiran@example.com','Kolkata','2024-07-20'),
 (12,'Luis Ortega','luis@example.com','Madrid','2024-07-28');

INSERT INTO products VALUES
 (1,'Mechanical Keyboard','electronics',89.0),(2,'USB-C Hub','electronics',39.5),
 (3,'Noise-cancelling Headphones','electronics',199.0),(4,'Standing Desk','furniture',349.0),
 (5,'Ergonomic Chair','furniture',279.0),(6,'Desk Lamp','furniture',45.0),
 (7,'Kubernetes in Action','books',49.0),(8,'Designing Data-Intensive Apps','books',55.0),
 (9,'Pro Git','books',35.0),(10,'Coffee Beans 1kg','grocery',24.0),
 (11,'Green Tea 100 bags','grocery',12.5),(12,'Webcam 4K','electronics',129.0);

INSERT INTO orders VALUES
 (1,1,'shipped','2024-06-01'),(2,1,'paid','2024-06-20'),(3,2,'shipped','2024-06-03'),
 (4,3,'cancelled','2024-06-05'),(5,3,'shipped','2024-06-21'),(6,4,'paid','2024-06-22'),
 (7,5,'pending','2024-06-23'),(8,6,'shipped','2024-06-10'),(9,6,'shipped','2024-06-25'),
 (10,7,'paid','2024-06-26'),(11,8,'shipped','2024-06-12'),(12,9,'pending','2024-06-27'),
 (13,1,'shipped','2024-07-02'),(14,2,'paid','2024-07-03'),(15,4,'shipped','2024-07-04'),
 (16,6,'cancelled','2024-07-05'),(17,7,'shipped','2024-07-06'),(18,10,'paid','2024-07-07');

INSERT INTO order_items VALUES
 (1,1,1,89.0),(1,7,1,49.0),(2,10,3,24.0),(3,3,1,199.0),(3,2,2,39.5),(4,4,1,349.0),
 (5,8,1,55.0),(5,9,1,35.0),(6,5,1,279.0),(6,6,2,45.0),(7,12,1,129.0),(8,1,1,89.0),
 (8,11,4,12.5),(9,3,1,199.0),(10,7,2,49.0),(10,8,1,55.0),(11,2,1,39.5),(11,10,2,24.0),
 (12,4,1,349.0),(13,12,1,129.0),(13,6,1,45.0),(14,9,3,35.0),(15,5,1,279.0),(15,1,1,89.0),
 (16,11,2,12.5),(17,3,1,199.0),(18,10,5,24.0),(18,2,1,39.5);

INSERT INTO employees VALUES
 (1,'Meera','CTO','engineering',300000,NULL),(2,'Arjun','Eng Manager','engineering',190000,1),
 (3,'Lena','Staff Engineer','engineering',210000,2),(4,'Omar','Backend Engineer','engineering',150000,2),
 (5,'Priya','Backend Engineer','engineering',155000,2),(6,'Tom','SRE','engineering',160000,2),
 (7,'Sara','VP Sales','sales',220000,NULL),(8,'Kofi','Account Exec','sales',120000,7),
 (9,'Yuki','Account Exec','sales',125000,7),(10,'Raj','Data Engineer','data',165000,1),
 (11,'Nina','Analyst','data',110000,10),(12,'Leo','Analyst','data',105000,10);

INSERT INTO accounts VALUES (1,'alice',500),(2,'bob',300),(3,'carol',0);

INSERT INTO events (user_id, kind, ts)
WITH RECURSIVE seq(n) AS (SELECT 1 UNION ALL SELECT n + 1 FROM seq WHERE n < 20000)
SELECT (n * 7919) % 1000, CASE n % 4 WHEN 0 THEN 'click' WHEN 1 THEN 'view' WHEN 2 THEN 'cart' ELSE 'buy' END, 1700000000 + n * 37
FROM seq;
"""

ALLOWED_PRAGMAS = {"table_info", "table_xinfo", "index_list", "index_info", "index_xinfo", "foreign_key_list"}
# VACUUM INTO and ATTACH can write files on disk; the authorizer cannot see every variant, so reject them up front.
BLOCKED = re.compile(r"\b(attach|detach|vacuum|load_extension)\b", re.IGNORECASE)


class SQLError(Exception):
    pass


def _authorizer(action, arg1, arg2, dbname, source):
    if action in (sqlite3.SQLITE_ATTACH, sqlite3.SQLITE_DETACH):
        return sqlite3.SQLITE_DENY
    if action == sqlite3.SQLITE_PRAGMA and (arg1 or "").lower() not in ALLOWED_PRAGMAS:
        return sqlite3.SQLITE_DENY
    if action == sqlite3.SQLITE_FUNCTION and (arg2 or "").lower() == "load_extension":
        return sqlite3.SQLITE_DENY
    return sqlite3.SQLITE_OK


def split_statements(sql: str) -> list[str]:
    statements, buf = [], ""
    for ch in sql:
        buf += ch
        if ch == ";" and sqlite3.complete_statement(buf):
            if buf.strip(" \n\t;"):
                statements.append(buf.strip())
            buf = ""
    if buf.strip():
        statements.append(buf.strip())
    return statements


def _cell(v):
    if isinstance(v, bytes):
        return f"<{len(v)} bytes>"
    return v


def _plan(con: sqlite3.Connection, stmt: str) -> list[dict]:
    rows = con.execute("EXPLAIN QUERY PLAN " + stmt).fetchall()
    return [{"id": r[0], "parent": r[1], "detail": r[3]} for r in rows]


def connect() -> sqlite3.Connection:
    con = sqlite3.connect(":memory:", isolation_level=None)
    con.executescript(SEED)
    con.execute("PRAGMA foreign_keys = ON")
    con.setlimit(sqlite3.SQLITE_LIMIT_LENGTH, 1_000_000)
    con.set_authorizer(_authorizer)
    return con


def run(sql: str, explain: bool = False) -> dict:
    sql = sql or ""
    if len(sql) > MAX_SQL:
        raise SQLError(f"SQL is longer than {MAX_SQL} characters.")
    if BLOCKED.search(sql):
        raise SQLError("ATTACH, DETACH, VACUUM and load_extension are disabled in the playground.")
    statements = split_statements(sql)
    if not statements:
        raise SQLError("Nothing to run.")
    if len(statements) > MAX_STATEMENTS:
        raise SQLError(f"At most {MAX_STATEMENTS} statements per run.")

    con = connect()
    deadline = time.monotonic() + TIME_LIMIT
    con.set_progress_handler(lambda: 1 if time.monotonic() > deadline else 0, 2000)
    results = []
    started = time.monotonic()
    try:
        for i, stmt in enumerate(statements):
            before = con.total_changes
            try:
                plan = _plan(con, stmt) if explain and re.match(r"\s*(select|with)\b", stmt, re.IGNORECASE) else None
                cur = con.execute(stmt)
                if cur.description:
                    rows = cur.fetchmany(MAX_ROWS + 1)
                    results.append({
                        "sql": stmt,
                        "columns": [d[0] for d in cur.description],
                        "rows": [[_cell(v) for v in r] for r in rows[:MAX_ROWS]],
                        "truncated": len(rows) > MAX_ROWS,
                        "plan": plan,
                    })
                else:
                    results.append({"sql": stmt, "changes": con.total_changes - before})
            except sqlite3.OperationalError as exc:
                msg = "Query took longer than 3 seconds and was stopped." if "interrupted" in str(exc) else str(exc)
                return {"ok": False, "results": results, "error": msg, "failed": i, "ms": _ms(started)}
            except sqlite3.DatabaseError as exc:
                return {"ok": False, "results": results, "error": str(exc), "failed": i, "ms": _ms(started)}
    finally:
        con.close()
    return {"ok": True, "results": results, "ms": _ms(started)}


def schema() -> list[dict]:
    con = connect()
    try:
        tables = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY rowid")]
        out = []
        for t in tables:
            cols = [{"name": c[1], "type": c[2], "pk": bool(c[5])} for c in con.execute(f"PRAGMA table_info({t})")]
            count = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            out.append({"name": t, "columns": cols, "rows": count})
        return out
    finally:
        con.close()


def _ms(start: float) -> int:
    return round((time.monotonic() - start) * 1000)
