"""More db topics, appended to the core module."""

from ._dsl import chain, ex, qa, topic

CATEGORIES = [
    {"id": "nosql", "title": "NoSQL & Specialized Stores", "color": "rose", "blurb": "Key-value, document, wide-column, graph, time-series and vector stores."},
    {"id": "design", "title": "Schema Design & Analytics", "color": "sky", "blurb": "Star schemas, columnar engines and multi-tenant layouts."},
    {"id": "operations", "title": "Operations & Security", "color": "slate", "blurb": "Backups, recovery, access control and encryption."},
]

TOPICS = [
    # ------------------------------------------------------------------ foundations
    topic(
        "data-types-null", "Data Types & NULL Semantics", "foundations", "basic", "DT",
        "Pick the right type for each column and understand three-valued logic.",
        "NULL is a blank on a form, not a zero. 'Unknown age' is different from 'age 0', and asking 'is unknown equal to unknown?' has no yes or no answer.",
        "Every column has a type that controls storage size, valid values, sorting and which operators apply. Use exact numerics (DECIMAL/NUMERIC or integer cents) for money, never binary floats, because 0.1 + 0.2 is not exactly 0.3 in IEEE 754. Store timestamps as TIMESTAMPTZ (or UTC integers) rather than local-time strings. NULL means 'unknown or not applicable' and introduces three-valued logic: any comparison with NULL yields UNKNOWN, and WHERE only keeps rows that evaluate to TRUE. Aggregates skip NULLs (except COUNT(*)), and NULL propagates through arithmetic and concatenation. COALESCE, NULLIF and IS [NOT] DISTINCT FROM are the tools for handling it explicitly. SQLite uses dynamic typing with type affinity, so it accepts values other engines would reject unless the table is declared STRICT.",
        [
            "Storing prices as DECIMAL(12,2) or integer cents to avoid rounding drift.",
            "Distinguishing 'no middle name' (empty string) from 'unknown' (NULL).",
            "Defaulting missing values in reports with COALESCE.",
            "Choosing TIMESTAMPTZ so events from many time zones compare correctly.",
        ],
        [
            "NULL = NULL is UNKNOWN, not TRUE; use IS NULL or IS NOT DISTINCT FROM.",
            "COUNT(col), SUM, AVG ignore NULLs; AVG over NULLs is not the same as AVG treating them as 0.",
            "NOT IN with a NULL in the list returns no rows; NOT EXISTS is NULL-safe.",
            "Use the smallest type that safely fits: it shrinks rows, indexes and cache footprint.",
            "UNIQUE allows multiple NULLs in most engines (Postgres 15+ has NULLS NOT DISTINCT).",
        ],
        [
            ex("Three-valued logic", "basic", "Comparisons with NULL are neither true nor false.", "sql", """
                SELECT NULL = NULL AS eq, NULL IS NULL AS is_null, NULL <> 1 AS ne,
                       1 + NULL AS plus, COALESCE(NULL, 'fallback') AS coalesced,
                       NULLIF(5, 5) AS nullif_same;
            """),
            ex("Aggregates skip NULLs", "intermediate", "COUNT(*) vs COUNT(col), and AVG with and without COALESCE.", "sql", """
                SELECT COUNT(*) AS all_rows, COUNT(manager_id) AS with_manager,
                       AVG(manager_id) AS avg_ignoring_null,
                       AVG(COALESCE(manager_id, 0)) AS avg_null_as_zero
                FROM employees;
            """),
            ex("Float vs integer cents", "intermediate", "Binary floats cannot represent 0.1 exactly; integer cents can.", "sql", """
                SELECT 0.1 + 0.2 = 0.3 AS float_equal, 10 + 20 = 30 AS cents_equal,
                       typeof(0.1) AS float_type, typeof(10) AS int_type;
            """),
        ],
        ["col IS NULL / IS NOT NULL", "COALESCE(a, b, 'default')", "NULLIF(a, b)", "a IS NOT DISTINCT FROM b (Postgres)", "price NUMERIC(12,2) NOT NULL", "CREATE TABLE t (...) STRICT; (SQLite)"],
        [
            "FLOAT/DOUBLE for money causes off-by-a-cent bugs in totals.",
            "Storing dates as 'DD/MM/YYYY' text breaks sorting and range queries.",
            "A NULL in a NOT IN subquery silently empties the result.",
            "Adding NOT NULL to an existing column fails if any row is NULL: backfill first.",
        ],
        [
            qa("basic", "What does NULL mean and how do you compare it?", "NULL means unknown or not applicable, not zero or empty. Any = or <> comparison with NULL yields UNKNOWN, so use IS NULL / IS NOT NULL, or IS NOT DISTINCT FROM for NULL-safe equality."),
            qa("basic", "COUNT(*) vs COUNT(column)?", "COUNT(*) counts rows. COUNT(column) counts rows where that column is not NULL, so the two differ exactly by the number of NULLs."),
            qa("intermediate", "Why should money not be stored as FLOAT?", "Binary floating point cannot represent most decimal fractions exactly, so sums drift (0.1 + 0.2 != 0.3). Use DECIMAL/NUMERIC with fixed scale or integer minor units (cents)."),
            qa("intermediate", "Why does x NOT IN (subquery) sometimes return nothing?", "If the subquery yields a NULL, x NOT IN (...) becomes x <> a AND x <> NULL ..., which is UNKNOWN for every row. NOT EXISTS or filtering NULLs in the subquery avoids it."),
            qa("advanced", "TIMESTAMP vs TIMESTAMPTZ in Postgres?", "TIMESTAMP stores a wall-clock value without zone. TIMESTAMPTZ normalizes to UTC on input and converts to the session time zone on output, so instants compare correctly across zones. Use TIMESTAMPTZ for events."),
        ],
        ["relational-model", "constraints-keys", "sql-basics"],
        chain(
            ("Value", "NULL or data", "Input value", "A row arrives with some columns NULL (unknown)."),
            ("Compare", "col = ?", "Comparison", "Comparing NULL with anything yields <b>UNKNOWN</b>, not FALSE.", "NULL"),
            ("3-valued", "T / F / UNKNOWN", "Three-valued logic", "AND/OR/NOT follow three-valued truth tables; NOT UNKNOWN is still UNKNOWN.", "UNKNOWN"),
            ("WHERE", "keeps TRUE only", "Filtering", "WHERE keeps only TRUE rows, so UNKNOWN rows vanish silently.", "drop"),
            ("Handle", "IS NULL, COALESCE", "Explicit handling", "Use IS NULL, COALESCE or NOT EXISTS to say what NULL should mean.", "fix"),
        ),
    ),
    topic(
        "constraints-keys", "Constraints & Keys in Depth", "foundations", "basic", "CK",
        "NOT NULL, UNIQUE, CHECK, PRIMARY and FOREIGN keys: let the database guard invariants.",
        "Constraints are the bouncer at the door. Application code is a polite sign saying 'adults only'; the bouncer actually checks ID for every single guest, including ones who came in through the back door (scripts, admin tools, other services).",
        "Constraints declare rules the database enforces on every write, no matter which client performs it. NOT NULL forbids missing values, UNIQUE forbids duplicates (backed by a unique index), CHECK enforces a boolean expression per row, PRIMARY KEY combines NOT NULL and UNIQUE as the row identity, and FOREIGN KEY guarantees a referenced row exists. Foreign keys also define what happens on parent delete or update: RESTRICT/NO ACTION, CASCADE, SET NULL or SET DEFAULT. Postgres adds EXCLUDE constraints (for example no overlapping bookings) and DEFERRABLE constraints that are checked at commit instead of per statement. Constraints are the last line of defence against race conditions: two concurrent requests can both pass an application-level 'does it exist?' check, but only one can pass a UNIQUE index. They also give the optimizer facts it can use, such as eliminating joins.",
        [
            "Preventing duplicate signups for the same email under concurrency.",
            "Ensuring order quantities and prices stay positive.",
            "Blocking deletion of a customer who still has orders.",
            "Preventing double-booking of a room with an exclusion constraint.",
        ],
        [
            "Uniqueness enforced only in application code is a race condition waiting to happen.",
            "Name constraints (CONSTRAINT uq_users_email ...) so errors and migrations are readable.",
            "Index foreign key columns on the child table: parent deletes and joins need them.",
            "DEFERRABLE INITIALLY DEFERRED lets circular references be inserted inside one transaction.",
            "Adding a constraint to a big table may scan it; Postgres supports NOT VALID then VALIDATE CONSTRAINT.",
        ],
        [
            ex("Named constraints", "basic", "Each insert after the first valid one violates a different rule. The CHECK failure stops the script.", "sql", """
                CREATE TABLE bookings (
                  id INTEGER PRIMARY KEY,
                  room TEXT NOT NULL,
                  nights INTEGER NOT NULL CONSTRAINT ck_nights_positive CHECK (nights > 0),
                  guest_email TEXT NOT NULL,
                  CONSTRAINT uq_room_guest UNIQUE (room, guest_email)
                );
                INSERT INTO bookings (room, nights, guest_email) VALUES ('101', 2, 'asha@example.com');
                SELECT * FROM bookings;
                INSERT INTO bookings (room, nights, guest_email) VALUES ('102', 0, 'ben@example.com');
            """),
            ex("ON DELETE behaviour", "intermediate", "CASCADE removes children with the parent; the seed's orders use RESTRICT-style protection.", "sql", """
                CREATE TABLE carts (id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL REFERENCES customers(id));
                CREATE TABLE cart_lines (
                  cart_id INTEGER NOT NULL REFERENCES carts(id) ON DELETE CASCADE,
                  product_id INTEGER NOT NULL REFERENCES products(id),
                  qty INTEGER NOT NULL CHECK (qty > 0)
                );
                INSERT INTO carts VALUES (1, 1);
                INSERT INTO cart_lines VALUES (1, 1, 2), (1, 2, 1);
                DELETE FROM carts WHERE id = 1;
                SELECT COUNT(*) AS remaining_lines FROM cart_lines;
            """),
            ex("Exclusion constraint (Postgres)", "advanced", "No two bookings for the same room may overlap in time.", "sql", """
                CREATE EXTENSION IF NOT EXISTS btree_gist;
                CREATE TABLE room_bookings (
                  room_id int NOT NULL,
                  during tstzrange NOT NULL,
                  EXCLUDE USING gist (room_id WITH =, during WITH &&)
                );
            """, runnable=False),
        ],
        ["CONSTRAINT uq_x UNIQUE (a, b)", "CHECK (qty > 0)", "REFERENCES parent(id) ON DELETE CASCADE", "ALTER TABLE t ADD CONSTRAINT ... NOT VALID; VALIDATE CONSTRAINT ...", "DEFERRABLE INITIALLY DEFERRED"],
        [
            "ON DELETE CASCADE on the wrong relationship can wipe out far more data than intended.",
            "SQLite ignores foreign keys unless PRAGMA foreign_keys = ON per connection.",
            "CHECK constraints cannot reference other rows or tables; use triggers or exclusion constraints for that.",
        ],
        [
            qa("basic", "List the main SQL constraint types.", "NOT NULL, UNIQUE, CHECK, PRIMARY KEY (NOT NULL + UNIQUE identity) and FOREIGN KEY (referential integrity). Postgres also has EXCLUDE constraints for rules like non-overlapping ranges."),
            qa("intermediate", "Why enforce uniqueness in the database if the app already checks?", "Two concurrent requests can both check 'not exists' and then both insert. A unique index makes the second insert fail atomically, so integrity holds regardless of races or other clients."),
            qa("intermediate", "CASCADE vs RESTRICT vs SET NULL?", "CASCADE deletes or updates children with the parent, RESTRICT/NO ACTION blocks the parent change while children exist, SET NULL clears the child's FK. Choose by ownership: owned children (order lines) cascade, independent entities restrict."),
            qa("advanced", "How do you add a constraint to a huge table without long locks?", "In Postgres add it as NOT VALID (enforced for new rows, no full scan), then run VALIDATE CONSTRAINT, which scans with a weaker lock. For uniqueness, build the index CONCURRENTLY and attach it with ADD CONSTRAINT ... USING INDEX."),
            qa("advanced", "What is a deferrable constraint?", "One checked at COMMIT rather than after each statement. It allows temporarily inconsistent states inside a transaction, such as inserting two rows that reference each other or swapping unique values."),
        ],
        ["relational-model", "data-types-null", "ddl-migrations"],
        chain(
            ("Write", "INSERT / UPDATE", "A write arrives", "Any client (app, script, admin) sends a write."),
            ("NOT NULL", "required cols", "Required columns", "Missing required values are rejected first.", "row"),
            ("CHECK", "row rule", "Row rules", "CHECK expressions must not evaluate to FALSE.", "row"),
            ("UNIQUE", "index probe", "Uniqueness", "The unique index is probed; a duplicate key fails atomically.", "key"),
            ("FK", "parent exists?", "Referential integrity", "The referenced parent row must exist (or ON DELETE action applies).", "fk"),
            ("Commit", "invariants hold", "Committed", "Only rows that satisfy every rule are stored.", "ok"),
        ),
    ),
    topic(
        "ddl-migrations", "DDL & Schema Migrations", "foundations", "intermediate", "MG",
        "Evolve schemas safely with versioned, reversible, zero-downtime migrations.",
        "Renovating a restaurant while it stays open: you build the new counter next to the old one, move staff over gradually, and only then remove the old counter. Tearing it out first means no one gets served.",
        "DDL (CREATE, ALTER, DROP) changes the schema. In production, schema changes are applied as versioned migration files (Flyway, Liquibase, Alembic, Rails, Django) tracked in a table so every environment converges to the same version. Some DDL takes strong locks or rewrites the whole table: adding a column with a volatile default on old Postgres versions, changing a column type, or building an index without CONCURRENTLY can block traffic for minutes. Zero-downtime changes follow expand-and-contract: add the new structure (nullable column, new table), deploy code that writes both, backfill in batches, switch reads, then remove the old structure in a later release. Postgres runs most DDL inside transactions, so a failed migration rolls back cleanly; MySQL commits DDL implicitly. Always set a lock_timeout so a migration waiting behind a long query does not queue every other request behind itself.",
        [
            "Renaming a column without breaking the running application version.",
            "Adding an index to a 500M-row table during business hours.",
            "Splitting a table into two as a feature evolves.",
        ],
        [
            "Expand, migrate, contract: never rename or drop in the same deploy that introduces the replacement.",
            "Backfill in small batches with commits between them to avoid long locks and replication lag.",
            "Postgres: CREATE INDEX CONCURRENTLY, ADD COLUMN with constant default is metadata-only (11+).",
            "Set lock_timeout and statement_timeout for migration sessions.",
            "Migrations are code: review them, test them against production-sized data, keep them idempotent where possible.",
        ],
        [
            ex("Expand and contract a column rename", "intermediate", "Add the new column, backfill, then (later) drop the old one.", "sql", """
                ALTER TABLE customers ADD COLUMN full_name TEXT;
                UPDATE customers SET full_name = name WHERE full_name IS NULL;
                SELECT id, name, full_name FROM customers LIMIT 3;
                -- later release, after all code reads full_name:
                ALTER TABLE customers DROP COLUMN name;
                SELECT * FROM customers LIMIT 2;
            """),
            ex("Batched backfill pattern", "advanced", "Update a bounded id range per statement instead of the whole table.", "sql", """
                ALTER TABLE events ADD COLUMN is_purchase INTEGER;
                UPDATE events SET is_purchase = (kind = 'buy') WHERE id BETWEEN 1 AND 5000 AND is_purchase IS NULL;
                UPDATE events SET is_purchase = (kind = 'buy') WHERE id BETWEEN 5001 AND 10000 AND is_purchase IS NULL;
                SELECT COUNT(*) AS done, SUM(is_purchase) AS purchases FROM events WHERE is_purchase IS NOT NULL;
            """),
            ex("Safe Postgres migration session", "advanced", "Fail fast instead of blocking traffic behind a lock queue.", "sql", """
                SET lock_timeout = '3s';
                SET statement_timeout = '15min';
                ALTER TABLE orders ADD COLUMN source text;           -- metadata only
                CREATE INDEX CONCURRENTLY ix_orders_source ON orders(source);  -- outside a transaction
            """, runnable=False),
        ],
        ["ALTER TABLE t ADD COLUMN c type", "ALTER TABLE t RENAME COLUMN a TO b", "CREATE INDEX CONCURRENTLY ix ON t(c)", "SET lock_timeout = '3s'", "flyway migrate / alembic upgrade head"],
        [
            "A migration waiting for an ACCESS EXCLUSIVE lock blocks every query queued behind it.",
            "Dropping a column the old app version still selects breaks rolling deploys.",
            "Huge single-statement backfills bloat WAL and lag replicas.",
            "MySQL DDL auto-commits, so a multi-step migration can fail halfway.",
        ],
        [
            qa("intermediate", "How do you rename a column with zero downtime?", "Expand and contract: add the new column, deploy code that writes both and reads old, backfill in batches, switch reads to the new column, stop writing the old one, then drop it in a later release."),
            qa("intermediate", "Why is CREATE INDEX dangerous on a big Postgres table and what is the fix?", "A plain CREATE INDEX blocks writes for the whole build. CREATE INDEX CONCURRENTLY builds without blocking writes (slower, cannot run in a transaction, must be checked for INVALID state on failure)."),
            qa("advanced", "What is lock queueing and why set lock_timeout?", "If ALTER TABLE waits for an exclusive lock behind a long query, every new query on that table queues behind the ALTER, causing an outage. lock_timeout makes the migration give up quickly and retry later."),
            qa("basic", "Why use a migration tool instead of running SQL by hand?", "Versioned, ordered, reviewed scripts recorded in a schema history table make every environment reproducible, enable CI testing and give an audit trail of what changed when."),
        ],
        ["constraints-keys", "indexes", "transactions-acid"],
        chain(
            ("Expand", "add new column", "Expand", "Add the new nullable column or table. Old code keeps working.", ""),
            ("Dual write", "app writes both", "Dual write", "Deploy code that writes old and new structures.", "deploy"),
            ("Backfill", "batches", "Backfill", "Copy historical data in small committed batches.", "rows"),
            ("Switch", "read new", "Switch reads", "Deploy code that reads the new structure only.", "deploy"),
            ("Contract", "drop old", "Contract", "In a later release, drop the old column safely.", "drop"),
        ),
    ),
    topic(
        "views-materialized", "Views & Materialized Views", "foundations", "intermediate", "VW",
        "Name a query as a virtual table, or store its result for fast reads.",
        "A view is a saved search in your email client: every time you open it, it re-runs. A materialized view is printing the search results: instant to read, but stale until you print again.",
        "A view is a stored SELECT that behaves like a table in queries; it holds no data and is expanded (inlined) into the outer query by the planner. Views simplify complex joins, provide stable interfaces while underlying tables change, and restrict what users can see (a security boundary when combined with grants or security_barrier/row-level security). Simple single-table views can be updatable. A materialized view stores the result physically, so reads are as fast as a table and it can be indexed, but it must be refreshed. Postgres REFRESH MATERIALIZED VIEW recomputes everything; CONCURRENTLY avoids blocking readers but requires a unique index. Other engines offer incremental maintenance (Oracle fast refresh, SQL Server indexed views, ClickHouse and Materialize streaming views). Choose views for abstraction and materialized views when the query is expensive and some staleness is acceptable.",
        [
            "A reporting view that hides join complexity from analysts.",
            "Exposing only non-sensitive columns to a read-only role.",
            "A nightly materialized view of revenue per day for dashboards.",
        ],
        [
            "Plain views cost nothing to store but run their full query every time.",
            "Materialized views trade freshness for read speed and must be refreshed on a schedule or trigger.",
            "REFRESH MATERIALIZED VIEW CONCURRENTLY needs a unique index on the view.",
            "Stacking views on views hides cost and makes plans hard to read.",
        ],
        [
            ex("A view as a stable interface", "basic", "Order totals as a virtual table; query it like any table.", "sql", """
                CREATE VIEW order_totals AS
                SELECT o.id AS order_id, c.name AS customer, o.status,
                       SUM(i.qty * i.unit_price) AS total
                FROM orders o
                JOIN customers c ON c.id = o.customer_id
                JOIN order_items i ON i.order_id = o.id
                GROUP BY o.id, c.name, o.status;
                SELECT customer, SUM(total) AS spent FROM order_totals WHERE status <> 'cancelled'
                GROUP BY customer ORDER BY spent DESC LIMIT 5;
            """),
            ex("Emulating a materialized view", "intermediate", "SQLite has no MATERIALIZED VIEW, so snapshot into a table and rebuild it to refresh.", "sql", """
                CREATE TABLE mv_daily_revenue AS
                SELECT o.created_at AS day, SUM(i.qty * i.unit_price) AS revenue
                FROM orders o JOIN order_items i ON i.order_id = o.id
                WHERE o.status <> 'cancelled' GROUP BY o.created_at;
                CREATE UNIQUE INDEX ux_mv_day ON mv_daily_revenue(day);
                SELECT * FROM mv_daily_revenue ORDER BY revenue DESC LIMIT 5;
                -- refresh = DELETE FROM mv_daily_revenue; INSERT INTO mv_daily_revenue SELECT ...
            """),
            ex("Postgres materialized view", "advanced", "Concurrent refresh keeps the old contents readable during recompute.", "sql", """
                CREATE MATERIALIZED VIEW mv_daily_revenue AS
                SELECT date_trunc('day', created_at) AS day, sum(total) AS revenue
                FROM orders GROUP BY 1;
                CREATE UNIQUE INDEX ON mv_daily_revenue(day);
                REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_revenue;
            """, runnable=False),
        ],
        ["CREATE VIEW v AS SELECT ...", "CREATE OR REPLACE VIEW v AS ...", "CREATE MATERIALIZED VIEW mv AS ... (Postgres)", "REFRESH MATERIALIZED VIEW CONCURRENTLY mv", "GRANT SELECT ON v TO reporting"],
        [
            "Expecting a view to make a slow query fast: it runs the same query.",
            "Forgetting to schedule refreshes, so dashboards show week-old data.",
            "Non-concurrent refresh takes an exclusive lock that blocks readers.",
        ],
        [
            qa("basic", "View vs table?", "A table stores rows. A view stores only a query; each time you select from it the query runs against current data. It is a named, reusable abstraction."),
            qa("intermediate", "View vs materialized view?", "A view is computed on every read and always fresh. A materialized view stores the result, so reads are fast and indexable, but data is stale until refreshed."),
            qa("intermediate", "How can views help security?", "Grant users SELECT on a view that exposes only allowed columns or rows instead of the base table. In Postgres use security_barrier views or row-level security to stop predicate leaks."),
            qa("advanced", "How would you keep a materialized aggregate fresh with low latency?", "Options: frequent REFRESH CONCURRENTLY, incremental maintenance via triggers or CDC into a summary table, or a streaming engine (Materialize, ClickHouse materialized views, Flink) that updates aggregates per change."),
        ],
        ["aggregation", "star-schema", "database-security"],
        chain(
            ("Base tables", "orders, items", "Source data", "Normalized tables hold the facts."),
            ("View", "stored SELECT", "Plain view", "A view is only a saved query; it is inlined at read time.", "query"),
            ("Mat. view", "stored rows", "Materialized", "A materialized view runs the query once and stores the rows.", "rows"),
            ("Read", "fast, indexed", "Fast reads", "Dashboards read the stored rows like a table.", "SELECT"),
            ("Refresh", "recompute", "Refresh", "Periodically recompute; CONCURRENTLY keeps readers unblocked.", "refresh"),
        ),
    ),
    topic(
        "procedures-triggers", "Stored Procedures, Functions & Triggers", "foundations", "intermediate", "PT",
        "Run logic inside the database: reusable routines and automatic reactions to writes.",
        "A trigger is a motion-sensor light: you never press a switch, it reacts automatically whenever someone walks by. A stored procedure is a speed-dial button that runs a whole routine with one press.",
        "Stored functions and procedures package SQL (and procedural code such as PL/pgSQL or T-SQL) inside the database. Functions return values and can be used in queries; procedures (Postgres 11+, SQL Server, MySQL) can manage transactions and are invoked with CALL. They reduce network round trips, centralize logic shared by many clients and can run with definer rights to expose a narrow operation without granting table access. Triggers run automatically BEFORE or AFTER INSERT, UPDATE or DELETE, per row or per statement; INSTEAD OF triggers make views writable. Typical uses are audit logs, maintaining updated_at timestamps, denormalized counters and enforcing cross-row rules. The downsides are hidden behaviour, harder testing and versioning, vendor lock-in and write amplification, so keep triggers small, deterministic and documented.",
        [
            "Writing an audit row for every change to a sensitive table.",
            "Maintaining updated_at or a denormalized counter automatically.",
            "A SECURITY DEFINER function that lets the app transfer money without direct UPDATE rights.",
        ],
        [
            "BEFORE row triggers can modify NEW; AFTER triggers see the final row and suit auditing.",
            "Triggers run inside the same transaction as the statement: a failure rolls back the write.",
            "Mark functions IMMUTABLE/STABLE/VOLATILE correctly; it affects planning and index usage.",
            "SECURITY DEFINER functions must set a safe search_path to avoid hijacking.",
            "Business logic split between app and triggers is hard to reason about; document it.",
        ],
        [
            ex("Audit trigger", "intermediate", "Every balance change writes an audit row automatically.", "sql", """
                CREATE TABLE account_audit (
                  account_id INTEGER, old_balance INTEGER, new_balance INTEGER,
                  changed_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TRIGGER trg_accounts_audit AFTER UPDATE OF balance ON accounts
                FOR EACH ROW BEGIN
                  INSERT INTO account_audit (account_id, old_balance, new_balance)
                  VALUES (OLD.id, OLD.balance, NEW.balance);
                END;
                UPDATE accounts SET balance = balance - 50 WHERE owner = 'alice';
                UPDATE accounts SET balance = balance + 50 WHERE owner = 'bob';
                SELECT account_id, old_balance, new_balance FROM account_audit;
            """),
            ex("Trigger enforcing a cross-table rule", "advanced", "Lines on live orders pass; change order_id to 4 (cancelled) to see RAISE(ABORT) reject the insert.", "sql", """
                CREATE TRIGGER trg_no_lines_on_cancelled BEFORE INSERT ON order_items
                FOR EACH ROW WHEN (SELECT status FROM orders WHERE id = NEW.order_id) = 'cancelled'
                BEGIN
                  SELECT RAISE(ABORT, 'order is cancelled');
                END;
                INSERT INTO order_items VALUES (1, 2, 1, 39.5);
                SELECT COUNT(*) AS lines_on_order_1 FROM order_items WHERE order_id = 1;
            """),
            ex("PL/pgSQL function and procedure", "advanced", "A transfer routine callable without UPDATE grants on accounts.", "sql", """
                CREATE FUNCTION transfer(src int, dst int, amount numeric) RETURNS void
                LANGUAGE plpgsql SECURITY DEFINER SET search_path = app, pg_temp AS $$
                BEGIN
                  UPDATE accounts SET balance = balance - amount WHERE id = src AND balance >= amount;
                  IF NOT FOUND THEN RAISE EXCEPTION 'insufficient funds'; END IF;
                  UPDATE accounts SET balance = balance + amount WHERE id = dst;
                END $$;
                SELECT transfer(1, 2, 100);
            """, runnable=False),
        ],
        ["CREATE TRIGGER t AFTER UPDATE ON tbl FOR EACH ROW ...", "CREATE FUNCTION f(...) RETURNS ... LANGUAGE plpgsql", "CREATE PROCEDURE p(...) ...; CALL p(...)", "RAISE(ABORT, 'msg') (SQLite)", "SECURITY DEFINER SET search_path = ..."],
        [
            "Triggers fire for bulk loads too, making imports far slower.",
            "Recursive or cascading triggers can loop or explode write volume.",
            "Logic hidden in triggers surprises developers reading only application code.",
        ],
        [
            qa("basic", "Function vs stored procedure?", "A function returns a value or table and can be used inside SELECT. A procedure is invoked with CALL, may return nothing and (in Postgres 11+) can COMMIT/ROLLBACK inside its body."),
            qa("intermediate", "BEFORE vs AFTER triggers?", "BEFORE row triggers run before the write and can modify or reject NEW (normalization, validation). AFTER triggers see the final committed-to-be row and are used for audit logs and side tables."),
            qa("intermediate", "Pros and cons of putting business logic in the database?", "Pros: one enforcement point for all clients, fewer round trips, strong integrity. Cons: harder to test, version and debug, vendor lock-in, and scaling compute on the database is expensive."),
            qa("advanced", "What are the risks of SECURITY DEFINER functions?", "They run with the owner's privileges, so a caller could hijack name resolution through search_path or pass unsafe dynamic SQL. Pin search_path, avoid dynamic SQL or bind parameters, and grant EXECUTE narrowly."),
        ],
        ["constraints-keys", "transactions-acid", "change-data-capture"],
        chain(
            ("Statement", "UPDATE accounts", "Write arrives", "A client updates a row."),
            ("BEFORE", "validate / modify", "BEFORE trigger", "Can change NEW or abort with an error.", "NEW"),
            ("Write row", "heap + indexes", "Row written", "The row and its indexes are updated.", "row"),
            ("AFTER", "audit, side rows", "AFTER trigger", "Writes the audit row in the same transaction.", "OLD/NEW"),
            ("Commit", "all or nothing", "Commit", "Statement and trigger effects commit or roll back together.", "commit"),
        ),
    ),
    # ------------------------------------------------------------------ querying
    topic(
        "subqueries", "Subqueries & Correlated Subqueries", "querying", "basic", "SB",
        "Queries inside queries: scalar, IN/EXISTS and correlated forms.",
        "Asking a librarian 'which books are longer than the average book?' requires first computing the average (inner question), then filtering (outer question). A correlated subquery is asking 'longer than the average of its own genre?' for each book separately.",
        "A subquery is a SELECT nested inside another statement. Scalar subqueries return one value and can appear wherever an expression can. Row-set subqueries feed IN, ANY/ALL or EXISTS. Derived tables (subqueries in FROM) act as inline views. A correlated subquery references columns of the outer row, so logically it runs once per outer row; modern optimizers often decorrelate it into a join or semi-join. EXISTS stops at the first match and is NULL-safe, which makes it the preferred form for existence checks and anti-joins. A scalar subquery that returns more than one row is an error in most engines (SQLite silently takes the first).",
        [
            "Products priced above their category average (correlated).",
            "Customers who placed at least one paid order (EXISTS).",
            "Filtering on an aggregate computed in a derived table.",
        ],
        [
            "EXISTS / NOT EXISTS are semi- and anti-joins; prefer NOT EXISTS over NOT IN.",
            "Correlated subqueries can be O(n*m) if the optimizer cannot rewrite them; check the plan.",
            "Derived tables let you aggregate before joining, avoiding fan-out.",
            "Scalar subqueries must return at most one row.",
        ],
        [
            ex("Scalar and IN subqueries", "basic", "Products above the overall average price, and customers with paid orders.", "sql", """
                SELECT name, price FROM products
                WHERE price > (SELECT AVG(price) FROM products) ORDER BY price DESC;

                SELECT name FROM customers
                WHERE id IN (SELECT customer_id FROM orders WHERE status = 'paid') ORDER BY name;
            """),
            ex("Correlated subquery", "intermediate", "Each product compared with the average of its own category.", "sql", """
                SELECT p.category, p.name, p.price
                FROM products p
                WHERE p.price > (SELECT AVG(p2.price) FROM products p2 WHERE p2.category = p.category)
                ORDER BY p.category;
            """),
            ex("Aggregate before joining", "advanced", "A derived table computes per-customer totals once, then joins.", "sql", """
                SELECT c.name, t.orders, t.spent
                FROM customers c
                JOIN (
                  SELECT o.customer_id, COUNT(DISTINCT o.id) AS orders, SUM(i.qty * i.unit_price) AS spent
                  FROM orders o JOIN order_items i ON i.order_id = o.id
                  WHERE o.status <> 'cancelled'
                  GROUP BY o.customer_id
                ) t ON t.customer_id = c.id
                ORDER BY t.spent DESC LIMIT 5;
            """),
        ],
        ["WHERE x > (SELECT AVG(x) FROM t)", "WHERE id IN (SELECT ...)", "WHERE EXISTS (SELECT 1 FROM t2 WHERE t2.fk = t.id)", "FROM (SELECT ...) AS derived", "x > ALL (SELECT ...)"],
        [
            "NOT IN with a nullable subquery column returns no rows.",
            "A scalar subquery returning multiple rows errors at runtime only when data changes.",
            "Correlated subqueries in SELECT run per row and can be slow on large outputs.",
        ],
        [
            qa("basic", "What is a correlated subquery?", "A subquery that references columns from the outer query, so it is logically evaluated once per outer row, for example comparing each product with its own category's average."),
            qa("intermediate", "IN vs EXISTS?", "IN compares a value with a set; EXISTS checks whether a correlated subquery returns any row and stops at the first match. Results match for positive checks, but NOT EXISTS is NULL-safe while NOT IN is not. Modern planners treat both as semi-joins."),
            qa("intermediate", "When would you rewrite a subquery as a join?", "When the optimizer fails to decorrelate it and runs it per row, or when you need columns from the inner table. Watch for duplicates: a join can multiply rows where IN/EXISTS would not."),
            qa("advanced", "How does an optimizer handle correlated subqueries?", "It tries to decorrelate them into semi-joins, anti-joins or joins against a grouped derived table, so the inner query runs once instead of per row. If it cannot, it may cache results per distinct outer value or fall back to nested-loop evaluation."),
        ],
        ["joins", "ctes-recursive", "sql-basics"],
        chain(
            ("Outer row", "product p", "Outer query", "The outer query walks products."),
            ("Inner query", "AVG by category", "Correlated inner", "For each row, the inner query uses p.category.", "p.category"),
            ("Value", "avg price", "Scalar result", "The subquery returns one value: that category's average.", "avg"),
            ("Compare", "price > avg", "Filter", "The outer row is kept only if the comparison is TRUE.", "keep?"),
            ("Optimizer", "decorrelate", "Rewrite", "Planners often rewrite this into a join against grouped averages.", "join"),
        ),
    ),
    topic(
        "ctes-recursive", "CTEs & Recursive CTEs", "querying", "intermediate", "CT",
        "Name intermediate results with WITH, and walk trees and graphs with WITH RECURSIVE.",
        "A CTE is writing sub-totals on a scratch pad before computing the final answer. A recursive CTE is a family tree exercise: start with grandma, then repeatedly add the children of everyone already on the list until no one new appears.",
        "A common table expression (WITH name AS (...)) names a subquery so the main query reads top-down like a pipeline. CTEs can reference earlier CTEs, which replaces deeply nested subqueries. In Postgres 12+ non-recursive CTEs are inlined unless marked MATERIALIZED; earlier versions always materialized them, acting as an optimization fence. A recursive CTE has an anchor member and a recursive member joined with UNION [ALL]; the engine repeatedly runs the recursive part against the rows produced in the previous iteration until it yields nothing new. It is the standard way to traverse hierarchies (org charts, categories, bill of materials), find paths in graphs and generate series. Always include a termination condition (depth limit or cycle detection), because cyclic data otherwise recurses forever.",
        [
            "Org chart: everyone who reports (directly or indirectly) to a manager.",
            "Breaking a complex report into readable named steps.",
            "Generating a calendar of dates to left join sparse data against.",
        ],
        [
            "UNION ALL is faster; UNION removes duplicates and can stop simple cycles.",
            "Track depth or a path string to limit recursion and detect cycles.",
            "Postgres: WITH x AS MATERIALIZED / NOT MATERIALIZED controls inlining.",
            "Data-modifying CTEs (Postgres) can chain INSERT/UPDATE ... RETURNING in one statement.",
        ],
        [
            ex("Readable pipeline with CTEs", "basic", "Revenue per customer, then the top three, in named steps.", "sql", """
                WITH line_totals AS (
                  SELECT o.customer_id, i.qty * i.unit_price AS amount
                  FROM orders o JOIN order_items i ON i.order_id = o.id
                  WHERE o.status <> 'cancelled'
                ),
                per_customer AS (
                  SELECT customer_id, SUM(amount) AS spent FROM line_totals GROUP BY customer_id
                )
                SELECT c.name, p.spent FROM per_customer p JOIN customers c ON c.id = p.customer_id
                ORDER BY p.spent DESC LIMIT 3;
            """),
            ex("Org chart with path and depth", "intermediate", "Walk down from the CTO, building a readable path.", "sql", """
                WITH RECURSIVE org(id, name, depth, path) AS (
                  SELECT id, name, 0, name FROM employees WHERE manager_id IS NULL AND id = 1
                  UNION ALL
                  SELECT e.id, e.name, o.depth + 1, o.path || ' > ' || e.name
                  FROM employees e JOIN org o ON e.manager_id = o.id
                  WHERE o.depth < 10
                )
                SELECT depth, path FROM org ORDER BY path;
            """),
            ex("Generate a date series", "advanced", "Fill missing days with zero revenue by left joining a generated calendar.", "sql", """
                WITH RECURSIVE days(d) AS (
                  SELECT '2024-06-01'
                  UNION ALL
                  SELECT date(d, '+1 day') FROM days WHERE d < '2024-06-10'
                )
                SELECT days.d, COUNT(o.id) AS orders
                FROM days LEFT JOIN orders o ON o.created_at = days.d
                GROUP BY days.d ORDER BY days.d;
            """),
        ],
        ["WITH a AS (...), b AS (SELECT ... FROM a) SELECT ...", "WITH RECURSIVE r AS (anchor UNION ALL recursive) ...", "WITH x AS MATERIALIZED (...) (Postgres)", "generate_series(a, b) (Postgres)", "CYCLE id SET is_cycle USING path (Postgres 14)"],
        [
            "Cyclic data (A manages B manages A) recurses forever without a guard.",
            "Old Postgres versions materialize every CTE, blocking predicate pushdown.",
            "A CTE referenced twice may be computed twice when inlined.",
        ],
        [
            qa("basic", "What is a CTE and why use it?", "A named temporary result defined with WITH for one statement. It improves readability, lets later steps reuse earlier ones, and enables recursion."),
            qa("intermediate", "How does a recursive CTE execute?", "The anchor query produces the initial working set. The recursive part runs against the previous iteration's rows, its output is appended and becomes the new working set, and this repeats until an iteration yields no rows."),
            qa("intermediate", "How do you prevent infinite recursion?", "Add a depth limit in the recursive WHERE, track a visited path and skip ids already in it, use UNION instead of UNION ALL for simple cycles, or use Postgres 14's CYCLE clause."),
            qa("advanced", "CTE vs subquery vs temp table for performance?", "Modern planners inline non-recursive CTEs like subqueries, so performance is usually equal. Materializing (MATERIALIZED hint or a temp table) helps when an expensive result is reused or when you want to fence the planner; temp tables can also be indexed and analyzed."),
        ],
        ["aggregation", "subqueries", "graph-databases"],
        chain(
            ("Anchor", "CTO row", "Anchor member", "The anchor selects the starting rows: the root of the tree."),
            ("Recurse", "join children", "Recursive member", "Join employees whose manager is in the previous set.", "level 0"),
            ("Append", "UNION ALL", "Accumulate", "New rows are appended and become the next working set.", "level 1"),
            ("Repeat", "until empty", "Iterate", "The loop repeats until an iteration finds no new rows.", "level n"),
            ("Result", "full tree", "Final result", "The main query reads all accumulated rows.", "rows"),
        ),
    ),
    topic(
        "window-functions", "Window Functions Deep Dive", "querying", "advanced", "WF",
        "Rankings, running totals, moving averages and gaps-and-islands without collapsing rows.",
        "A window function is a race official who writes each runner's position, gap to the leader and lap-time change on that runner's own card, instead of replacing all cards with one summary sheet.",
        "Window functions compute a value for each row from a related set of rows, the window, defined by OVER (PARTITION BY ... ORDER BY ... frame). PARTITION BY splits rows into independent groups; ORDER BY defines sequence within a partition; the frame (ROWS or RANGE BETWEEN ...) limits which neighbours are included. Ranking functions (ROW_NUMBER, RANK, DENSE_RANK, NTILE, PERCENT_RANK), offset functions (LAG, LEAD, FIRST_VALUE, LAST_VALUE, NTH_VALUE) and any aggregate used with OVER are available. When ORDER BY is present the default frame is RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW, which treats ties as peers and surprises people with LAST_VALUE. Window functions are evaluated after WHERE, GROUP BY and HAVING, so filtering on them requires a CTE or subquery (or QUALIFY in some engines). They usually require a sort per distinct window definition, so an index matching PARTITION BY + ORDER BY can remove that cost.",
        [
            "Top-N per group (best three products per category).",
            "Running totals and 7-day moving averages for dashboards.",
            "Day-over-day change with LAG.",
            "Gaps-and-islands: finding consecutive streaks of activity.",
        ],
        [
            "ROWS frames count physical rows; RANGE frames group peers with equal ORDER BY values.",
            "LAST_VALUE needs ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING to see the partition end.",
            "Define a named WINDOW w AS (...) to reuse the same window across columns.",
            "Filter on window results in an outer query (or QUALIFY in Snowflake/BigQuery/DuckDB).",
            "Aggregates with FILTER (WHERE ...) compute conditional totals in one pass.",
        ],
        [
            ex("Running total and moving average", "intermediate", "Per-day revenue with cumulative sum and a 3-day moving average.", "sql", """
                WITH daily AS (
                  SELECT o.created_at AS day, SUM(i.qty * i.unit_price) AS revenue
                  FROM orders o JOIN order_items i ON i.order_id = o.id
                  WHERE o.status <> 'cancelled' GROUP BY o.created_at
                )
                SELECT day, revenue,
                       SUM(revenue) OVER (ORDER BY day ROWS UNBOUNDED PRECEDING) AS running,
                       ROUND(AVG(revenue) OVER (ORDER BY day ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2) AS ma3
                FROM daily ORDER BY day LIMIT 10;
            """),
            ex("LAG, share of total and named windows", "advanced", "Salary compared with the previous person in the department and with the department total.", "sql", """
                SELECT dept, name, salary,
                       salary - LAG(salary) OVER w AS diff_prev,
                       ROUND(100.0 * salary / SUM(salary) OVER (PARTITION BY dept), 1) AS pct_of_dept,
                       NTILE(2) OVER w AS half
                FROM employees
                WINDOW w AS (PARTITION BY dept ORDER BY salary)
                ORDER BY dept, salary;
            """),
            ex("Gaps and islands", "advanced", "Consecutive login days per user collapse into streaks: date minus row_number is constant within a streak.", "sql", """
                CREATE TABLE logins (user_id INTEGER, day TEXT);
                INSERT INTO logins VALUES
                  (1,'2024-06-01'),(1,'2024-06-02'),(1,'2024-06-03'),(1,'2024-06-07'),(1,'2024-06-08'),
                  (2,'2024-06-01'),(2,'2024-06-03'),(2,'2024-06-04');
                WITH g AS (
                  SELECT user_id, day,
                         julianday(day) - ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY day) AS grp
                  FROM (SELECT DISTINCT user_id, day FROM logins)
                )
                SELECT user_id, MIN(day) AS streak_start, MAX(day) AS streak_end, COUNT(*) AS days
                FROM g GROUP BY user_id, grp ORDER BY user_id, streak_start;
            """),
        ],
        ["fn() OVER (PARTITION BY g ORDER BY x)", "ROWS BETWEEN 6 PRECEDING AND CURRENT ROW", "LAG(x, 1, 0) OVER (ORDER BY d)", "WINDOW w AS (PARTITION BY g ORDER BY x)", "SUM(x) FILTER (WHERE cond) OVER (...)", "QUALIFY ROW_NUMBER() OVER (...) = 1 (Snowflake/BigQuery)"],
        [
            "Default RANGE frame makes running totals jump on tied ORDER BY values.",
            "LAST_VALUE returns the current row unless you widen the frame.",
            "Window functions cannot be used in WHERE or GROUP BY directly.",
        ],
        [
            qa("intermediate", "Difference between GROUP BY and a window function?", "GROUP BY collapses rows into one per group. A window function computes over a group but keeps every input row, adding the computed value as a column."),
            qa("advanced", "ROWS vs RANGE frames?", "ROWS counts physical rows relative to the current row. RANGE uses ORDER BY values, so all peers with the same value are included together. With duplicates, a RANGE running sum assigns the same total to all tied rows."),
            qa("advanced", "How would you find consecutive login streaks?", "Gaps-and-islands: number each user's distinct login dates with ROW_NUMBER ordered by date, subtract that number (in days) from the date; consecutive days share the same difference, so GROUP BY user and that key gives each streak."),
            qa("advanced", "Why might LAST_VALUE return the current row?", "With ORDER BY, the default frame ends at the current row, so the last value in the frame is the current row (or its last peer). Use ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING."),
            qa("intermediate", "How do you deduplicate rows keeping the latest per key?", "ROW_NUMBER() OVER (PARTITION BY key ORDER BY updated_at DESC) in a CTE, then keep rn = 1 (or delete rn > 1)."),
        ],
        ["aggregation", "ctes-recursive", "pagination"],
        chain(
            ("Rows", "after WHERE/GROUP", "Input rows", "Window functions run after WHERE, GROUP BY and HAVING."),
            ("Partition", "PARTITION BY dept", "Partition", "Rows are split into independent groups.", "groups"),
            ("Order", "ORDER BY salary", "Order", "Each partition is sorted (an index can provide this).", "sorted"),
            ("Frame", "ROWS n PRECEDING", "Frame", "For each row, the frame picks the neighbours to include.", "frame"),
            ("Compute", "rank, lag, sum", "Compute per row", "The function is evaluated per row; no rows are collapsed.", "values"),
        ),
    ),
    topic(
        "set-operations", "Set Operations: UNION, INTERSECT, EXCEPT", "querying", "basic", "SO",
        "Combine, intersect or subtract the results of compatible queries.",
        "Two guest lists for a party: UNION is everyone invited by either host, INTERSECT is guests both hosts invited, and EXCEPT is guests on host A's list who are not on host B's.",
        "Set operators combine the result sets of two SELECTs with the same number of columns and compatible types. UNION returns rows from either side and removes duplicates (requiring a sort or hash); UNION ALL keeps duplicates and is much cheaper. INTERSECT returns rows present in both, and EXCEPT (MINUS in Oracle) returns rows in the first result but not the second. Column names come from the first query, and ORDER BY / LIMIT apply to the whole combined result. Set operations compare entire rows and treat NULLs as equal for duplicate elimination, unlike = in WHERE. They are useful for reconciliation (what is in staging but not in production), merging partitions or similar tables, and building simple OR alternatives that each use a different index.",
        [
            "Reconciling two data sources: rows in A but not in B.",
            "Combining active and archived orders into one report.",
            "Customers who are both buyers and newsletter subscribers.",
        ],
        [
            "Default to UNION ALL unless you truly need deduplication.",
            "Columns are matched by position, not by name.",
            "Set operators treat NULLs as equal when removing duplicates.",
            "Rewriting OR across different columns as UNION can let each branch use its own index.",
        ],
        [
            ex("UNION vs UNION ALL", "basic", "Cities of customers with paid vs shipped orders, deduplicated and not.", "sql", """
                SELECT c.city FROM customers c JOIN orders o ON o.customer_id = c.id WHERE o.status = 'paid'
                UNION
                SELECT c.city FROM customers c JOIN orders o ON o.customer_id = c.id WHERE o.status = 'shipped'
                ORDER BY 1;

                SELECT COUNT(*) AS union_all_rows FROM (
                  SELECT customer_id FROM orders WHERE status = 'paid'
                  UNION ALL
                  SELECT customer_id FROM orders WHERE status = 'shipped'
                );
            """),
            ex("INTERSECT and EXCEPT", "intermediate", "Customers with both paid and shipped orders, and customers who never had a shipped order.", "sql", """
                SELECT customer_id FROM orders WHERE status = 'paid'
                INTERSECT
                SELECT customer_id FROM orders WHERE status = 'shipped';

                SELECT id FROM customers
                EXCEPT
                SELECT customer_id FROM orders WHERE status = 'shipped';
            """),
            ex("Data reconciliation", "advanced", "Find rows that differ between a copy and the source in both directions.", "sql", """
                CREATE TABLE products_copy AS SELECT * FROM products;
                UPDATE products_copy SET price = 95.0 WHERE id = 1;
                DELETE FROM products_copy WHERE id = 12;
                SELECT 'only_in_source' AS side, * FROM (SELECT * FROM products EXCEPT SELECT * FROM products_copy)
                UNION ALL
                SELECT 'only_in_copy', * FROM (SELECT * FROM products_copy EXCEPT SELECT * FROM products);
            """),
        ],
        ["q1 UNION q2", "q1 UNION ALL q2", "q1 INTERSECT q2", "q1 EXCEPT q2 (MINUS in Oracle)", "(q1 UNION ALL q2) ORDER BY col LIMIT n"],
        [
            "UNION silently removes legitimate duplicate rows and costs a sort.",
            "Column order mismatches produce wrong but type-compatible results.",
            "ORDER BY inside a branch is not allowed (or is ignored) without a subquery.",
        ],
        [
            qa("basic", "UNION vs UNION ALL?", "UNION removes duplicate rows, which requires sorting or hashing. UNION ALL concatenates results and keeps duplicates, so it is faster; use it whenever duplicates are impossible or wanted."),
            qa("basic", "UNION vs JOIN?", "UNION stacks rows vertically from compatible queries. JOIN combines columns horizontally from related tables based on a condition."),
            qa("intermediate", "How do you find rows in table A that are not in table B by all columns?", "SELECT * FROM a EXCEPT SELECT * FROM b, which compares full rows and treats NULLs as equal. For key-based comparison use NOT EXISTS."),
            qa("advanced", "Why might rewriting OR as UNION speed up a query?", "WHERE a = ? OR b = ? may force a full scan if no single index covers both. Two branches, each using its own index, combined with UNION (or UNION ALL plus a dedupe guard) can be far cheaper. Many planners do this automatically with bitmap OR."),
        ],
        ["sql-basics", "subqueries", "joins"],
        chain(
            ("Query A", "rows set 1", "Left query", "The first SELECT defines column names and count."),
            ("Query B", "rows set 2", "Right query", "The second SELECT must have compatible columns.", "rows"),
            ("Combine", "UNION/INTERSECT", "Operator", "Rows are combined, intersected or subtracted by whole-row comparison.", "compare"),
            ("Dedupe", "unless ALL", "Duplicates", "Without ALL, duplicates are removed via sort or hash.", "distinct"),
            ("Order", "ORDER BY / LIMIT", "Final shaping", "ORDER BY and LIMIT apply to the combined result.", "result"),
        ),
    ),
    topic(
        "case-functions", "CASE, String & Date Functions", "querying", "basic", "CF",
        "Conditional logic, text manipulation and date arithmetic inside queries.",
        "CASE is a sorting clerk with a rule card: 'if the parcel is over 20 kg put it in bin A, else if fragile bin B, otherwise bin C'. String and date functions are the clerk's scissors, tape and calendar.",
        "CASE evaluates conditions in order and returns the first matching result (or ELSE, or NULL if there is no ELSE). The searched form (CASE WHEN cond THEN ...) handles arbitrary predicates; the simple form (CASE x WHEN 1 THEN ...) compares one value. CASE inside aggregates implements pivots and conditional counts (SUM(CASE WHEN ... THEN 1 ELSE 0 END)), which the standard FILTER clause expresses more cleanly. String functions (LOWER, UPPER, TRIM, SUBSTR, REPLACE, LENGTH, concatenation with ||, LIKE patterns) clean and match text, but functions on a column in WHERE usually prevent index use. Date handling differs a lot by engine: Postgres has date_trunc, intervals and EXTRACT; MySQL has DATE_FORMAT and DATE_ADD; SQLite uses date(), strftime() and julianday() over ISO-8601 text. Store timestamps in UTC and convert at the edges, and filter with half-open ranges (>= start AND < end) instead of functions on the column.",
        [
            "Bucketing customers into tiers by lifetime spend.",
            "Pivoting order counts by status into columns.",
            "Normalizing emails with LOWER/TRIM before comparing.",
            "Monthly reports using date truncation.",
        ],
        [
            "CASE returns the first matching branch; order the WHEN clauses from most to least specific.",
            "Missing ELSE yields NULL, which then propagates through arithmetic.",
            "SUM(CASE WHEN ... THEN 1 ELSE 0 END) or COUNT(*) FILTER (WHERE ...) for conditional counts.",
            "Use half-open ranges (ts >= '2024-06-01' AND ts < '2024-07-01') to stay sargable.",
            "Date functions are not portable; isolate them or use an ORM/dialect layer.",
        ],
        [
            ex("Bucketing with CASE", "basic", "Price bands for products.", "sql", """
                SELECT name, price,
                       CASE WHEN price >= 200 THEN 'premium'
                            WHEN price >= 50 THEN 'mid'
                            ELSE 'budget' END AS band
                FROM products ORDER BY price DESC;
            """),
            ex("Pivot with conditional aggregation", "intermediate", "Order counts per status as columns, per month.", "sql", """
                SELECT strftime('%Y-%m', created_at) AS month,
                       SUM(CASE WHEN status = 'paid' THEN 1 ELSE 0 END) AS paid,
                       SUM(CASE WHEN status = 'shipped' THEN 1 ELSE 0 END) AS shipped,
                       COUNT(*) FILTER (WHERE status = 'cancelled') AS cancelled
                FROM orders GROUP BY month ORDER BY month;
            """),
            ex("String and date functions", "intermediate", "Email domains, name initials, and days since signup relative to a fixed date.", "sql", """
                SELECT name,
                       UPPER(SUBSTR(name, 1, 1)) AS initial,
                       SUBSTR(email, INSTR(email, '@') + 1) AS domain,
                       CAST(julianday('2024-08-01') - julianday(created_at) AS INTEGER) AS days_since_signup,
                       date(created_at, 'start of month') AS signup_month
                FROM customers ORDER BY created_at LIMIT 6;
            """),
        ],
        ["CASE WHEN c1 THEN a WHEN c2 THEN b ELSE d END", "COUNT(*) FILTER (WHERE cond)", "LOWER(TRIM(s)), SUBSTR(s, i, n), REPLACE(s, a, b)", "date_trunc('month', ts) (Postgres) / strftime('%Y-%m', ts) (SQLite)", "ts >= :start AND ts < :end"],
        [
            "WHERE date(created_at) = '2024-06-01' cannot use a plain index on created_at.",
            "CASE branches with different types are coerced, sometimes surprisingly.",
            "Local-time strings break across daylight-saving changes.",
        ],
        [
            qa("basic", "What happens if no WHEN matches and there is no ELSE?", "CASE returns NULL. In arithmetic or concatenation that NULL propagates, so add an explicit ELSE when a default is meaningful."),
            qa("intermediate", "How do you pivot rows into columns in SQL?", "Conditional aggregation: SUM(CASE WHEN status = 'paid' THEN 1 ELSE 0 END) AS paid per column, or COUNT(*) FILTER (WHERE ...). Some engines also offer PIVOT or crosstab, but conditional aggregation is portable."),
            qa("intermediate", "Why avoid functions on columns in WHERE?", "WHERE LOWER(email) = ? or date(ts) = ? hides the raw column from a B-tree index, forcing a scan. Rewrite as a range on the raw column or create an expression index matching the function."),
            qa("advanced", "How should timestamps be stored across time zones?", "Store instants in UTC (TIMESTAMPTZ or epoch), convert to local time only for display, and keep the user's IANA time zone separately when you need local calendar semantics such as 'midnight in their zone'."),
        ],
        ["sql-basics", "aggregation", "data-types-null"],
        chain(
            ("Row", "price = 89", "Input row", "Each row reaches the CASE expression."),
            ("WHEN 1", "price >= 200?", "First branch", "Conditions are tested in order. 89 >= 200 is false.", "89"),
            ("WHEN 2", "price >= 50?", "Second branch", "89 >= 50 is true, so evaluation stops here.", "89"),
            ("Result", "'mid'", "Return value", "The first matching THEN value is returned; ELSE only if none match.", "mid"),
        ),
    ),
    topic(
        "upserts", "Upserts & Idempotent Writes", "querying", "intermediate", "UP",
        "INSERT ... ON CONFLICT and MERGE: insert or update atomically, safely under concurrency.",
        "A hotel check-in desk: if you already have a reservation they update it, otherwise they create one. Doing it at one desk atomically avoids two clerks both creating a room for you.",
        "An upsert inserts a row or, if it collides with a unique constraint, updates (or ignores) the existing one, all in one atomic statement. Postgres and SQLite use INSERT ... ON CONFLICT (cols) DO UPDATE SET ... with the excluded pseudo-table holding the proposed values; MySQL uses ON DUPLICATE KEY UPDATE; SQL Server, Oracle and Postgres 15+ support MERGE. Upserts replace the racy 'SELECT then INSERT or UPDATE' pattern, where two concurrent requests both see no row and both insert. They are the backbone of idempotent APIs: store an idempotency key with a unique constraint so a retried request does not create duplicates. The conflict target must match a unique index or constraint, and a WHERE clause on DO UPDATE can skip stale updates (for example only if the incoming version is newer). MERGE in some engines is not concurrency-safe without extra locking, so prefer ON CONFLICT where available.",
        [
            "Counters: increment a page-view row or create it at 1.",
            "Syncing data from an external feed without duplicates.",
            "Idempotency keys for payment APIs.",
        ],
        [
            "ON CONFLICT requires a unique index or constraint matching the conflict target.",
            "excluded.col refers to the value you tried to insert.",
            "DO NOTHING is ideal for idempotent 'create if missing' semantics.",
            "Add WHERE to DO UPDATE to ignore out-of-order (older) updates.",
            "Postgres consumes a sequence value even when the upsert takes the update path.",
        ],
        [
            ex("Counter upsert", "basic", "Create the counter at 1 or increment it.", "sql", """
                CREATE TABLE page_views (path TEXT PRIMARY KEY, views INTEGER NOT NULL);
                INSERT INTO page_views VALUES ('/home', 1) ON CONFLICT (path) DO UPDATE SET views = views + 1;
                INSERT INTO page_views VALUES ('/home', 1) ON CONFLICT (path) DO UPDATE SET views = views + 1;
                INSERT INTO page_views VALUES ('/docs', 1) ON CONFLICT (path) DO UPDATE SET views = views + 1;
                SELECT * FROM page_views ORDER BY path;
            """),
            ex("Sync with excluded and a version guard", "intermediate", "Apply feed rows; ignore updates older than what we already have.", "sql", """
                CREATE TABLE prices (sku TEXT PRIMARY KEY, price REAL NOT NULL, version INTEGER NOT NULL);
                INSERT INTO prices VALUES ('KB-1', 89.0, 3);
                INSERT INTO prices (sku, price, version) VALUES ('KB-1', 79.0, 2), ('HUB-2', 39.5, 1)
                ON CONFLICT (sku) DO UPDATE SET price = excluded.price, version = excluded.version
                WHERE excluded.version > prices.version;
                SELECT * FROM prices ORDER BY sku;
            """),
            ex("Idempotency key", "advanced", "A retried payment request does not create a second charge.", "sql", """
                CREATE TABLE payments (
                  id INTEGER PRIMARY KEY, idempotency_key TEXT NOT NULL UNIQUE,
                  order_id INTEGER NOT NULL REFERENCES orders(id), amount REAL NOT NULL
                );
                INSERT INTO payments (idempotency_key, order_id, amount) VALUES ('req-7f3a', 2, 72.0)
                ON CONFLICT (idempotency_key) DO NOTHING;
                INSERT INTO payments (idempotency_key, order_id, amount) VALUES ('req-7f3a', 2, 72.0)
                ON CONFLICT (idempotency_key) DO NOTHING;
                SELECT COUNT(*) AS charges FROM payments;
            """),
        ],
        ["INSERT ... ON CONFLICT (k) DO UPDATE SET c = excluded.c", "INSERT ... ON CONFLICT DO NOTHING", "INSERT ... ON DUPLICATE KEY UPDATE c = VALUES(c) (MySQL)", "MERGE INTO t USING s ON ... WHEN MATCHED THEN UPDATE ... WHEN NOT MATCHED THEN INSERT ...", "INSERT ... RETURNING id"],
        [
            "SELECT-then-INSERT in application code races under concurrency.",
            "Upserting many rows that hit the same key twice in one statement errors in Postgres.",
            "MERGE is not atomic against concurrent inserts in some engines without locks.",
        ],
        [
            qa("basic", "What is an upsert?", "A single atomic statement that inserts a row or updates the existing one if a unique key already exists, such as INSERT ... ON CONFLICT DO UPDATE."),
            qa("intermediate", "Why is 'check if exists, then insert' unsafe?", "Two transactions can both see no row and both insert, creating duplicates or a unique violation. An upsert backed by a unique index resolves the race inside the database."),
            qa("intermediate", "How do you make an API endpoint idempotent?", "Require a client-supplied idempotency key, store it with a UNIQUE constraint alongside the result, insert with ON CONFLICT DO NOTHING, and on conflict return the stored result instead of repeating the side effect."),
            qa("advanced", "How do you prevent out-of-order updates overwriting newer data in an upsert?", "Carry a version or event timestamp and add WHERE excluded.version > t.version to DO UPDATE, so older messages become no-ops."),
        ],
        ["constraints-keys", "isolation-mvcc", "optimistic-pessimistic"],
        chain(
            ("INSERT", "proposed row", "Attempt insert", "The statement tries to insert the row."),
            ("Unique idx", "probe key", "Conflict check", "The unique index is probed for the key.", "key"),
            ("No conflict", "insert", "Insert path", "If the key is free, the row is inserted.", "new"),
            ("Conflict", "DO UPDATE", "Update path", "If it exists, DO UPDATE applies excluded values (optionally guarded by WHERE).", "excluded"),
            ("Atomic", "one statement", "Race-free", "Concurrent upserts serialize on the index entry: no duplicates.", "done"),
        ),
    ),
    topic(
        "pagination", "Pagination: OFFSET vs Keyset", "querying", "intermediate", "PG",
        "Page through large results without slowing down or skipping rows.",
        "OFFSET is counting from the first page every time to reach page 500. Keyset pagination is a bookmark: you open the book exactly where you stopped.",
        "OFFSET/LIMIT pagination is simple and supports jumping to arbitrary pages, but the database must still read and discard all skipped rows, so page N costs O(N) and deep pages get slow. It is also unstable: if rows are inserted or deleted between requests, users see duplicates or miss rows. Keyset (seek, cursor) pagination remembers the sort key of the last row and asks for rows after it: WHERE (created_at, id) < (:last_ts, :last_id) ORDER BY created_at DESC, id DESC LIMIT 20. With an index on the sort columns, every page is an index seek, regardless of depth, and results stay stable under concurrent writes. The sort must be deterministic, so include a unique tiebreaker (usually the primary key). APIs expose the position as an opaque cursor (base64 of the last key) instead of a page number. Total counts are expensive on large tables; show estimates or 'more results' instead.",
        [
            "Infinite scroll feeds and activity timelines.",
            "Exporting a large table in chunks.",
            "Admin tables where jumping to page N is required (OFFSET is acceptable for shallow pages).",
        ],
        [
            "OFFSET cost grows linearly with depth; keyset cost stays constant.",
            "Always ORDER BY a unique key (add id as tiebreaker).",
            "Row-value comparison (a, b) > (x, y) expresses multi-column keysets cleanly.",
            "Keyset cannot jump to arbitrary page numbers; offer next/previous only.",
            "Encode cursors opaquely so clients do not depend on internals.",
        ],
        [
            ex("OFFSET vs keyset plans", "intermediate", "Both return the same page; the keyset version seeks straight to it (enable Explain to compare).", "sql", """
                SELECT id, user_id, kind FROM events ORDER BY id LIMIT 5 OFFSET 15000;
                SELECT id, user_id, kind FROM events WHERE id > 15000 ORDER BY id LIMIT 5;
            """),
            ex("Multi-column keyset with tiebreaker", "advanced", "Newest orders first, ties on date broken by id; the second query fetches the page after (2024-06-25, 9).", "sql", """
                CREATE INDEX ix_orders_created_id ON orders(created_at DESC, id DESC);
                SELECT id, created_at FROM orders ORDER BY created_at DESC, id DESC LIMIT 4;
                SELECT id, created_at FROM orders
                WHERE (created_at, id) < ('2024-06-25', 9)
                ORDER BY created_at DESC, id DESC LIMIT 4;
            """),
            ex("Opaque cursor in an API", "advanced", "Encode the last row's key, decode it on the next request.", "python", """
                import base64, json

                def encode_cursor(row):
                    return base64.urlsafe_b64encode(json.dumps([row["created_at"], row["id"]]).encode()).decode()

                def decode_cursor(cursor):
                    created_at, id_ = json.loads(base64.urlsafe_b64decode(cursor))
                    return created_at, id_

                SQL = ("SELECT id, created_at FROM orders WHERE (created_at, id) < (?, ?) "
                       "ORDER BY created_at DESC, id DESC LIMIT ?")
            """, runnable=False),
        ],
        ["LIMIT n OFFSET m", "WHERE id > :last_id ORDER BY id LIMIT n", "WHERE (ts, id) < (:ts, :id) ORDER BY ts DESC, id DESC LIMIT n", "CREATE INDEX ix ON t(ts DESC, id DESC)", "cursor = base64(last_key)"],
        [
            "ORDER BY a non-unique column alone makes pages overlap or skip rows.",
            "SELECT COUNT(*) for page counts on huge tables is a full scan.",
            "Changing the sort order invalidates existing cursors.",
        ],
        [
            qa("basic", "Why is deep OFFSET pagination slow?", "The engine must produce and discard all OFFSET rows before returning the page, so page 10,000 reads 10,000 x page_size rows."),
            qa("intermediate", "How does keyset pagination work?", "Remember the sort key of the last row returned and query WHERE key > :last ORDER BY key LIMIT n. An index on the key lets the engine seek directly, so each page costs the same."),
            qa("intermediate", "Why is OFFSET pagination inconsistent under writes?", "Inserting a row before the current position shifts everything by one, so the next page repeats a row; deleting one skips a row. Keyset anchors on values, not positions."),
            qa("advanced", "How do you implement keyset pagination on a non-unique sort column?", "Add a unique tiebreaker such as id to both ORDER BY and the predicate: WHERE (created_at, id) < (:ts, :id) ORDER BY created_at DESC, id DESC, with a composite index in the same order."),
        ],
        ["sql-basics", "composite-covering-indexes", "query-plans"],
        chain(
            ("Page 1", "ORDER BY ts, id", "First page", "Fetch the first n rows in a deterministic order."),
            ("Cursor", "last (ts, id)", "Remember position", "Return the last row's key as an opaque cursor.", "cursor"),
            ("Seek", "WHERE > cursor", "Next request", "The next query seeks past the cursor using the index.", "ts, id"),
            ("Page 2", "constant cost", "Next page", "Every page costs one index seek, regardless of depth.", "rows"),
        ),
    ),
    topic(
        "json-in-sql", "JSON in Relational Databases", "querying", "intermediate", "JS",
        "Store semi-structured data in JSON/JSONB columns and query it with SQL.",
        "A JSON column is a junk drawer inside a well-organized kitchen: perfect for odds and ends that do not deserve their own shelf, a mess if you start keeping the cutlery there.",
        "Modern relational databases store JSON documents in columns and provide operators to extract, filter and modify them. Postgres JSONB stores a parsed binary form that supports containment (@>), key existence (?) and GIN indexes; plain JSON keeps the original text. MySQL has a JSON type with generated-column indexing, and SQLite offers json_extract, ->, ->>, json_each and json_group_array. JSON is ideal for genuinely variable attributes (product specs, webhook payloads, user preferences) while keeping relational integrity for core fields. The trade-offs: no foreign keys or column-level constraints inside the document, weaker statistics for the planner, larger rows, and update-in-place rewrites the whole value. A good rule is to promote any field you filter, join or aggregate on frequently into a real column (or a generated column with an index).",
        [
            "Product attributes that differ per category.",
            "Storing raw webhook payloads for replay and audit.",
            "User preferences and feature flags per account.",
        ],
        [
            "Postgres: prefer JSONB over JSON for querying and indexing.",
            "GIN index on a JSONB column accelerates @> containment and key existence queries.",
            "Index a hot field with an expression or generated column: ((body->>'status')).",
            "->  returns JSON, ->> returns text (SQL value).",
            "Validate shape with CHECK (json_valid(...)) or JSON Schema in the app.",
        ],
        [
            ex("Extract and filter JSON", "basic", "Store product specs as JSON and query nested fields.", "sql", """
                CREATE TABLE product_specs (product_id INTEGER PRIMARY KEY REFERENCES products(id), specs TEXT CHECK (json_valid(specs)));
                INSERT INTO product_specs VALUES
                  (1, '{"switch":"brown","layout":"US","wireless":false}'),
                  (3, '{"anc":true,"battery_h":30,"colors":["black","silver"]}'),
                  (12, '{"resolution":"4K","fps":30,"wireless":false}');
                SELECT p.name, s.specs ->> '$.wireless' AS wireless, s.specs ->> '$.battery_h' AS battery
                FROM product_specs s JOIN products p ON p.id = s.product_id;
            """),
            ex("Explode arrays and build JSON", "intermediate", "json_each turns an array into rows; json_group_array aggregates rows into JSON.", "sql", """
                CREATE TABLE product_specs (product_id INTEGER PRIMARY KEY, specs TEXT);
                INSERT INTO product_specs VALUES (3, '{"colors":["black","silver","blue"]}');
                SELECT s.product_id, c.value AS color FROM product_specs s, json_each(s.specs, '$.colors') c;
                SELECT category, json_group_array(name) AS products FROM products GROUP BY category;
            """),
            ex("Index a JSON field with a generated column", "advanced", "Promote a hot field so the planner can use an index.", "sql", """
                CREATE TABLE webhooks (id INTEGER PRIMARY KEY, body TEXT NOT NULL,
                  event_type TEXT GENERATED ALWAYS AS (json_extract(body, '$.type')) VIRTUAL);
                CREATE INDEX ix_webhooks_type ON webhooks(event_type);
                INSERT INTO webhooks (body) VALUES ('{"type":"payment.succeeded","amount":72}'), ('{"type":"refund.created","amount":10}');
                EXPLAIN QUERY PLAN SELECT id FROM webhooks WHERE event_type = 'refund.created';
                SELECT id, event_type FROM webhooks WHERE event_type = 'refund.created';
            """),
        ],
        ["body->>'key' (Postgres/SQLite)", "body @> '{\"status\":\"paid\"}' (Postgres JSONB)", "CREATE INDEX ON t USING gin (body jsonb_path_ops)", "json_each(col, '$.arr') (SQLite)", "jsonb_set(body, '{a,b}', '1')"],
        [
            "Putting everything in JSON loses constraints, types and good statistics.",
            "Comparing JSON numbers extracted as text sorts lexically ('10' < '9').",
            "Large documents updated frequently cause write amplification and bloat.",
        ],
        [
            qa("basic", "When should you use a JSON column?", "For genuinely variable or sparse attributes and raw payloads that you mostly read as a whole. Core fields you filter, join or constrain belong in typed columns."),
            qa("intermediate", "JSON vs JSONB in Postgres?", "JSON stores the original text and reparses on every access. JSONB stores a decomposed binary form (keys deduplicated, order not preserved) that is faster to query and supports GIN indexing and containment operators."),
            qa("intermediate", "How do you index a field inside a JSON document?", "Use an expression index on (body->>'field') or a generated column with a B-tree index for equality/range, or a GIN index on the whole JSONB column for containment and key-existence queries."),
            qa("advanced", "What are the downsides of a heavily JSON-based schema?", "No foreign keys or per-field constraints, weak planner statistics on nested values, larger rows, whole-document rewrites on update, and implicit schemas that drift. Validation moves to application code."),
        ],
        ["nosql-cap", "document-databases", "index-types"],
        chain(
            ("Row", "id + body JSON", "Stored document", "A typed row carries a JSON column for variable attributes."),
            ("Extract", "body->>'type'", "Extract", "Operators pull nested fields out as SQL values.", "path"),
            ("Filter", "WHERE ...", "Filter", "Without an index, every document is parsed during the scan.", "scan"),
            ("Index", "GIN / expression", "Index", "A GIN or expression index lets the planner seek instead.", "seek"),
            ("Promote", "real column", "Promote hot fields", "Frequently queried fields become typed columns.", "column"),
        ),
    ),
    # ------------------------------------------------------------------ performance
    topic(
        "composite-covering-indexes", "Composite & Covering Indexes", "performance", "intermediate", "CI",
        "Design multi-column indexes that match WHERE, ORDER BY and SELECT together.",
        "A phone book sorted by last name, then first name: great for 'Rao, Asha', useless for 'everyone named Asha'. If the entry also lists the phone number, you never have to open the address card (covering).",
        "A composite index sorts by its first column, then by the second within equal first values, and so on. It can serve any query that constrains a leftmost prefix of its columns. The classic design rule is equality columns first, then the range or sort column: an index on (customer_id, created_at) answers WHERE customer_id = ? ORDER BY created_at DESC LIMIT 10 with a single seek and no sort. Once a range predicate is used on a column, later columns can no longer narrow the seek (they can only be filtered within the range). A covering index contains every column a query needs, either as key columns or as non-key INCLUDE columns (Postgres 11+, SQL Server), enabling index-only scans that never touch the table. Column order should follow query patterns and selectivity, and one well-designed composite index often replaces several single-column ones.",
        [
            "Latest N orders of a customer: (customer_id, created_at DESC).",
            "Dashboard counts by (tenant_id, status) answered from the index alone.",
            "Replacing three single-column indexes with one composite that serves all queries.",
        ],
        [
            "Leftmost prefix rule: (a, b, c) serves a, (a, b) and (a, b, c), not b or c alone.",
            "Equality columns first, then range/ORDER BY columns.",
            "Columns after the first range predicate cannot narrow the seek.",
            "INCLUDE adds payload columns for covering without widening the key.",
            "Postgres index-only scans also depend on the visibility map (vacuum).",
        ],
        [
            ex("Equality then sort", "intermediate", "The composite index removes both the scan and the temp sort.", "sql", """
                EXPLAIN QUERY PLAN SELECT id, ts FROM events WHERE user_id = 42 ORDER BY ts DESC LIMIT 5;
                CREATE INDEX ix_events_user_ts ON events(user_id, ts);
                EXPLAIN QUERY PLAN SELECT id, ts FROM events WHERE user_id = 42 ORDER BY ts DESC LIMIT 5;
            """),
            ex("Covering index", "advanced", "All needed columns are in the index: SQLite reports USING COVERING INDEX.", "sql", """
                CREATE INDEX ix_events_user_kind ON events(user_id, kind);
                EXPLAIN QUERY PLAN SELECT kind, COUNT(*) FROM events WHERE user_id = 42 GROUP BY kind;
                SELECT kind, COUNT(*) FROM events WHERE user_id = 42 GROUP BY kind;
            """),
            ex("Column order matters", "advanced", "A range on the first column means the second cannot narrow the seek.", "sql", """
                CREATE INDEX ix_ts_user ON events(ts, user_id);
                EXPLAIN QUERY PLAN SELECT COUNT(*) FROM events WHERE ts > 1700100000 AND user_id = 42;
                CREATE INDEX ix_user_ts2 ON events(user_id, ts);
                EXPLAIN QUERY PLAN SELECT COUNT(*) FROM events WHERE ts > 1700100000 AND user_id = 42;
            """),
        ],
        ["CREATE INDEX ix ON t(eq_col, range_col)", "CREATE INDEX ix ON t(a, b) INCLUDE (c) (Postgres/SQL Server)", "CREATE INDEX ix ON t(customer_id, created_at DESC)", "EXPLAIN: Index Only Scan / USING COVERING INDEX"],
        [
            "Putting the range column first makes the composite nearly useless for equality filters.",
            "Redundant indexes: (a) is unnecessary if (a, b) exists.",
            "Wide covering indexes cost memory and slow writes.",
        ],
        [
            qa("intermediate", "Explain the leftmost prefix rule.", "A composite index on (a, b, c) is sorted by a, then b, then c, so it can seek on a, on (a, b) or on (a, b, c). A predicate only on b or c cannot use the ordering for a seek."),
            qa("intermediate", "How do you order columns in a composite index?", "Put columns compared with equality first, then the column used for range filtering or ORDER BY. Among equality columns, order by how many queries share them and by selectivity."),
            qa("advanced", "What is an index-only scan and what can prevent it?", "The engine answers from the index without visiting the table because all needed columns are present. In Postgres it still checks the visibility map; if pages are not all-visible (vacuum lagging), it must visit the heap."),
            qa("advanced", "INCLUDE columns vs adding them to the key?", "INCLUDE columns are stored only in leaf entries, not in the sort key, so they make the index covering without affecting ordering, uniqueness or inner-node size."),
        ],
        ["indexes", "index-types", "query-plans"],
        chain(
            ("Query", "user=42 ORDER ts", "Query shape", "Equality on user_id, sort by ts, LIMIT 5."),
            ("Seek", "user_id = 42", "Seek prefix", "The index jumps to the first entry for user 42.", "42"),
            ("Ordered", "ts within user", "Ordered walk", "Within that user, entries are already sorted by ts: no sort needed.", "ts"),
            ("Covering?", "cols in index", "Covering check", "If every selected column is in the index, skip the table.", "cols"),
            ("Stop", "LIMIT 5", "Early stop", "The walk stops after 5 entries.", "5 rows"),
        ),
    ),
    topic(
        "index-types", "Index Types: B-tree, Hash, GIN, GiST, BRIN", "performance", "advanced", "IT",
        "Match the index structure to the operator: equality, range, containment, similarity or huge append-only tables.",
        "Different catalogues for different questions: an alphabetical list (B-tree) for names, a lookup by exact ticket number (hash), a back-of-book word index (GIN) for 'which pages mention X', a map with regions (GiST) for 'what is near here', and a shelf label per aisle (BRIN) for 'which aisle has books from 1990'.",
        "B-tree is the default and supports equality, ranges, prefix LIKE and ORDER BY. Hash indexes support only equality but can be smaller for long keys (crash-safe in Postgres since 10). GIN (generalized inverted index) maps each element (array item, JSONB key, full-text lexeme, trigram) to the rows containing it, making containment and full-text queries fast, at the cost of slower writes (mitigated by fastupdate pending lists). GiST is a balanced tree of bounding predicates used for geometric data, ranges, nearest-neighbour (ORDER BY distance) and exclusion constraints. BRIN stores min/max summaries per block range, staying tiny for huge naturally ordered tables like append-only logs. Other engines have equivalents: MySQL InnoDB uses B+trees plus FULLTEXT and spatial R-trees, and many analytical engines rely on zone maps similar to BRIN. Choosing the wrong type means the planner simply cannot use the index for your operator.",
        [
            "GIN on JSONB or tags arrays for containment queries.",
            "GiST for PostGIS 'within 5 km' searches and range overlap.",
            "BRIN on a 2 TB append-only events table ordered by time.",
            "pg_trgm GIN index for fuzzy ILIKE '%term%' search.",
        ],
        [
            "B-tree: =, <, >, BETWEEN, prefix LIKE, ORDER BY.",
            "GIN: @>, ?, @@ (full text), array && - fast reads, slower writes.",
            "GiST: overlap, distance, nearest neighbour, exclusion constraints.",
            "BRIN: tiny, effective only when physical order correlates with the column.",
            "Hash: equality only; rarely better than B-tree in practice.",
        ],
        [
            ex("B-tree serves equality, range and order", "intermediate", "The same index answers three query shapes in SQLite (which only has B-trees).", "sql", """
                CREATE INDEX ix_products_price ON products(price);
                EXPLAIN QUERY PLAN SELECT name FROM products WHERE price = 49.0;
                EXPLAIN QUERY PLAN SELECT name FROM products WHERE price BETWEEN 40 AND 100;
                EXPLAIN QUERY PLAN SELECT name FROM products ORDER BY price LIMIT 3;
            """),
            ex("GIN, GiST, BRIN and trigram in Postgres", "advanced", "One index per operator family.", "sql", """
                CREATE INDEX ix_docs_body ON docs USING gin (body jsonb_path_ops);     -- body @> '{"k":"v"}'
                CREATE INDEX ix_posts_tsv ON posts USING gin (to_tsvector('english', text));
                CREATE INDEX ix_places_geo ON places USING gist (location);           -- ST_DWithin, <->
                CREATE INDEX ix_events_ts ON events USING brin (ts) WITH (pages_per_range = 64);
                CREATE EXTENSION IF NOT EXISTS pg_trgm;
                CREATE INDEX ix_users_name_trgm ON users USING gin (name gin_trgm_ops); -- ILIKE '%asha%'
            """, runnable=False),
        ],
        ["USING btree (default)", "USING hash (equality only)", "USING gin (jsonb_col) / gin (tsvector)", "USING gist (geom) / gist (tstzrange)", "USING brin (ts)", "gin (col gin_trgm_ops) for LIKE '%x%'"],
        [
            "A B-tree cannot help LIKE '%term%'; use trigram GIN or full-text search.",
            "GIN on write-heavy tables can slow inserts; tune fastupdate and gin_pending_list_limit.",
            "BRIN on randomly ordered data is useless: the min/max ranges all overlap.",
        ],
        [
            qa("intermediate", "When would you use a GIN index?", "When a row contains many indexable elements and you query for containment: JSONB @>, array overlap, full-text @@, trigram similarity. GIN maps each element to the rows containing it."),
            qa("advanced", "GiST vs GIN?", "GIN is an inverted index: exact element lookup, fast reads, slower updates, larger. GiST is a lossy tree of bounding predicates: supports ranges, geometry, nearest-neighbour ordering and exclusion constraints, with faster updates but rechecks."),
            qa("advanced", "When is BRIN a good choice?", "For very large tables where the column correlates with physical order, such as append-only time-series. It stores min/max per block range, so it is tiny and lets scans skip irrelevant ranges."),
            qa("intermediate", "Why are hash indexes rarely used?", "They support only equality and no ordering or range scans, while B-trees handle equality nearly as fast plus everything else. Hash can win for very long keys where B-tree entries would be large."),
        ],
        ["indexes", "json-in-sql", "time-series-databases"],
        chain(
            ("Operator", "=, <, @>, &&, <->", "What do you ask?", "Start from the operator your queries use."),
            ("B-tree", "eq, range, order", "Ordered data", "Comparisons and sorting go to a B-tree.", "<, ="),
            ("GIN", "contains element", "Many elements per row", "Containment and full text go to GIN.", "@>"),
            ("GiST", "overlap, nearest", "Spatial and ranges", "Geometry, ranges and KNN go to GiST.", "&&"),
            ("BRIN", "block min/max", "Huge ordered tables", "Append-only time data can use tiny BRIN summaries.", "ts"),
        ),
    ),
    topic(
        "partial-expression-indexes", "Partial & Expression Indexes", "performance", "intermediate", "PX",
        "Index only the rows you query, or the computed value you filter on.",
        "A partial index is a 'to-do' list that only contains open tasks instead of every task ever created. An expression index is a contact list sorted by lowercase name, so 'asha', 'Asha' and 'ASHA' all land in the same place.",
        "A partial index has a WHERE clause and contains only matching rows, so it is smaller, cheaper to maintain and more cache-friendly. It is ideal when queries target a small, hot subset: unprocessed jobs, active users, non-deleted rows. The query's predicate must imply the index predicate for the planner to use it. Partial unique indexes enforce conditional uniqueness, for example one active subscription per user or unique emails among non-deleted accounts. An expression (functional) index stores the result of an expression such as lower(email) or date(created_at), so queries using exactly that expression become sargable. Expressions must be deterministic (IMMUTABLE in Postgres). Both features exist in Postgres and SQLite; MySQL 8 supports functional indexes, and SQL Server offers filtered indexes and indexed computed columns.",
        [
            "Job queue: index only status = 'pending' rows.",
            "Soft deletes: unique email WHERE deleted_at IS NULL.",
            "Case-insensitive login lookup via lower(email).",
        ],
        [
            "The query must contain a predicate that matches or implies the partial index WHERE.",
            "Partial unique indexes model conditional uniqueness rules elegantly.",
            "Expression indexes only help queries that use the identical expression.",
            "Expressions must be deterministic; now() or random() are not allowed.",
        ],
        [
            ex("Partial index for a hot subset", "intermediate", "Only pending orders are indexed; the query matching the predicate uses it.", "sql", """
                CREATE INDEX ix_orders_pending ON orders(created_at) WHERE status = 'pending';
                EXPLAIN QUERY PLAN SELECT id FROM orders WHERE status = 'pending' ORDER BY created_at;
                SELECT id, created_at FROM orders WHERE status = 'pending' ORDER BY created_at;
            """),
            ex("Conditional uniqueness with soft deletes", "advanced", "Two deleted rows may share an email, but only one live row can.", "sql", """
                CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT NOT NULL, deleted_at TEXT);
                CREATE UNIQUE INDEX ux_users_email_live ON users(lower(email)) WHERE deleted_at IS NULL;
                INSERT INTO users (email, deleted_at) VALUES ('Asha@example.com', '2024-01-01');
                INSERT INTO users (email, deleted_at) VALUES ('asha@example.com', '2024-02-01');
                INSERT INTO users (email) VALUES ('ASHA@example.com');
                SELECT id, email, deleted_at FROM users;
            """),
            ex("Expression index", "intermediate", "Case-insensitive lookups become index seeks.", "sql", """
                EXPLAIN QUERY PLAN SELECT id FROM customers WHERE lower(email) = 'ben@example.com';
                CREATE INDEX ix_customers_email_lower ON customers(lower(email));
                EXPLAIN QUERY PLAN SELECT id FROM customers WHERE lower(email) = 'ben@example.com';
            """),
        ],
        ["CREATE INDEX ix ON t(col) WHERE status = 'pending'", "CREATE UNIQUE INDEX ux ON t(email) WHERE deleted_at IS NULL", "CREATE INDEX ix ON t(lower(email))", "CREATE INDEX ix ON t((body->>'type')) (Postgres)", "MySQL 8: CREATE INDEX ix ON t((lower(email)))"],
        [
            "Parameterized predicates (status = ?) may not match a partial index at plan time.",
            "WHERE LOWER(email) uses the index; WHERE UPPER(email) does not.",
            "Partial indexes can hide data issues: rows outside the predicate are unindexed.",
        ],
        [
            qa("intermediate", "What is a partial index and when is it useful?", "An index with a WHERE clause that includes only matching rows. It is smaller and cheaper when queries focus on a small subset such as pending jobs or non-deleted rows."),
            qa("intermediate", "How do you enforce unique emails with soft deletes?", "A partial unique index: CREATE UNIQUE INDEX ... ON users(lower(email)) WHERE deleted_at IS NULL. Deleted rows are excluded, so a user can re-register after deletion."),
            qa("advanced", "Why might a partial index not be used with a prepared statement?", "With a generic plan the planner cannot prove that the parameter value satisfies the index predicate (status = $1 vs status = 'pending'), so it falls back. Use a literal for the constant part of the predicate."),
            qa("basic", "What is an expression index?", "An index on the result of an expression such as lower(email). Queries that filter on the exact same expression can seek in the index instead of scanning."),
        ],
        ["indexes", "composite-covering-indexes", "case-functions"],
        chain(
            ("Table", "all rows", "Whole table", "Most rows are historical and rarely queried."),
            ("Predicate", "WHERE pending", "Index predicate", "The partial index includes only rows matching its WHERE.", "filter"),
            ("Small index", "hot rows only", "Small and hot", "Fewer entries mean less memory and cheaper writes.", "subset"),
            ("Query", "same predicate", "Matching query", "A query with the same predicate can use the index.", "seek"),
        ),
    ),
    topic(
        "statistics-cardinality", "Statistics & Cardinality Estimation", "performance", "advanced", "ST",
        "How the optimizer guesses row counts, and what happens when it guesses wrong.",
        "A delivery planner guesses parcel volume from last month's report. If the report is stale or treats 'Bengaluru' and 'monsoon season' as unrelated, it sends a bicycle where a truck was needed.",
        "Cost-based optimizers choose plans from estimated cardinalities: how many rows each step will produce. They rely on statistics collected by ANALYZE: row counts, number of distinct values, null fraction, most common values and histograms of value distribution per column. Selectivity of predicates is estimated from these and combined under an independence assumption, which fails for correlated columns (city and country, model and manufacturer), leading to big under-estimates. Errors compound through joins, so a 10x mistake at one step can become 1000x later, causing nested loops over millions of rows or hash joins that spill to disk. Fixes include running ANALYZE after bulk loads, raising the statistics target for skewed columns, extended statistics (CREATE STATISTICS for dependencies, ndistinct and MCV lists), and rewriting queries to avoid opaque expressions. Postgres autovacuum triggers ANALYZE automatically, but large changes between runs can still leave stale stats.",
        [
            "A query that suddenly switched to a bad plan after a bulk load.",
            "Correlated filters like city = 'Paris' AND country = 'FR' under-estimated.",
            "Skewed tenant data where one tenant owns 60% of rows.",
        ],
        [
            "Compare estimated vs actual rows in EXPLAIN ANALYZE; big gaps point to stats issues.",
            "ANALYZE after bulk loads, large deletes or new indexes on expressions.",
            "Independence assumption breaks with correlated columns: use extended statistics.",
            "Histograms and most-common-values handle skew; raise default_statistics_target for key columns.",
            "Parameter sniffing / generic plans can lock in a plan good for one value but bad for another.",
        ],
        [
            ex("Collect and inspect statistics", "intermediate", "SQLite's ANALYZE stores per-index stats: total rows, then average rows per distinct key prefix.", "sql", """
                CREATE INDEX ix_events_kind ON events(kind);
                CREATE INDEX ix_events_user ON events(user_id);
                ANALYZE;
                SELECT tbl, idx, stat FROM sqlite_stat1 WHERE tbl = 'events';
            """),
            ex("Estimates drive the plan", "advanced", "With stats, the planner knows user_id is far more selective than kind and picks that index.", "sql", """
                CREATE INDEX ix_events_kind ON events(kind);
                CREATE INDEX ix_events_user ON events(user_id);
                ANALYZE;
                EXPLAIN QUERY PLAN SELECT COUNT(*) FROM events WHERE kind = 'buy' AND user_id = 7;
            """),
            ex("Postgres extended statistics", "advanced", "Teach the planner that city determines country.", "sql", """
                CREATE STATISTICS st_addr_city_country (dependencies, ndistinct, mcv) ON city, country FROM addresses;
                ALTER TABLE events ALTER COLUMN tenant_id SET STATISTICS 1000;
                ANALYZE addresses;
                SELECT attname, n_distinct, most_common_vals FROM pg_stats WHERE tablename = 'addresses';
                EXPLAIN ANALYZE SELECT * FROM addresses WHERE city = 'Paris' AND country = 'FR';
            """, runnable=False),
        ],
        ["ANALYZE [table]", "SELECT * FROM pg_stats WHERE tablename = 't'", "CREATE STATISTICS s (dependencies) ON a, b FROM t", "ALTER TABLE t ALTER COLUMN c SET STATISTICS 1000", "EXPLAIN (ANALYZE) - compare rows= estimates vs actual"],
        [
            "Bulk-loading into a new table and querying before autovacuum analyzes it.",
            "Temporary tables are never auto-analyzed in Postgres.",
            "Functions in predicates get default selectivity guesses (often 0.5% or 33%).",
        ],
        [
            qa("intermediate", "What statistics does an optimizer keep?", "Per table: row and page counts. Per column: null fraction, number of distinct values, most common values with frequencies, a histogram of the remaining distribution, and correlation with physical order."),
            qa("advanced", "Why do correlated columns break estimates?", "The planner multiplies selectivities assuming independence. For city = 'Paris' AND country = 'FR' it might estimate 1% x 5% = 0.05% when the true answer is 1%, a 20x under-estimate that can choose nested loops wrongly."),
            qa("advanced", "A query got slow after a nightly bulk load. What do you check?", "Whether statistics are stale: compare estimated and actual rows in EXPLAIN ANALYZE, check last_analyze in pg_stat_user_tables, run ANALYZE, and consider adding ANALYZE to the load job."),
            qa("advanced", "What is parameter sniffing?", "The engine builds and caches a plan using the first parameter values it sees. If data is skewed, a plan good for a rare value is terrible for a common one. Mitigations: recompile hints, custom plans, plan guides or splitting queries by value class."),
        ],
        ["query-plans", "indexes", "index-types"],
        chain(
            ("ANALYZE", "sample rows", "Collect stats", "ANALYZE samples rows and builds per-column statistics."),
            ("Stats", "ndistinct, MCV", "Store", "Distinct counts, common values and histograms are stored.", "stats"),
            ("Estimate", "selectivity", "Estimate", "The planner estimates rows per predicate and multiplies them.", "rows?"),
            ("Plan", "join type/order", "Choose plan", "Estimated rows decide index vs scan and join algorithms.", "cost"),
            ("Verify", "est vs actual", "Verify", "EXPLAIN ANALYZE reveals bad estimates to fix.", "actual"),
        ),
    ),
    topic(
        "n-plus-one-orm", "N+1 Queries & ORM Pitfalls", "performance", "basic", "OR",
        "Spot and fix the hidden query storms ORMs generate.",
        "Sending a courier to the warehouse once per item on a shopping list instead of handing them the whole list. Each trip is quick, but 200 trips are not.",
        "ORMs map rows to objects and load relationships lazily by default: accessing order.customer issues a query the first time. Looping over N parents and touching a relationship produces 1 query for the list plus N queries for children, the N+1 problem. Each query is fast in isolation, so it hides in development and explodes in production as network round trips and connection time add up. Fixes are eager loading (JOIN-based or a second batched IN query: select_related/prefetch_related in Django, joinedload/selectinload in SQLAlchemy, includes in Rails, JOIN FETCH in JPA), or writing the aggregate query directly. Other ORM pitfalls include SELECT * of wide rows, loading entire tables into memory, per-row saves instead of bulk operations, implicit transactions held open across network calls, and unbounded queries without LIMIT. Query logging, APM traces and tests that assert query counts catch regressions.",
        [
            "A list API that issues one query per item for its author.",
            "Admin pages that slow down as rows grow.",
            "Background jobs saving rows one at a time.",
        ],
        [
            "Detect with query logs, APM spans or assertNumQueries-style tests.",
            "JOIN eager loading suits to-one; batched IN loading suits to-many (avoids row explosion).",
            "Bulk insert/update APIs reduce round trips by orders of magnitude.",
            "Select only needed columns for list views.",
            "Keep the ORM, but drop to SQL for reports and heavy aggregates.",
        ],
        [
            ex("N+1 vs batched loading", "basic", "One query per order (simulated) vs one IN query for all customers at once.", "sql", """
                -- N+1: for each order, SELECT name FROM customers WHERE id = ?
                SELECT name FROM customers WHERE id = 1;
                SELECT name FROM customers WHERE id = 2;
                SELECT name FROM customers WHERE id = 3;
                -- batched: one query for all customer ids on the page
                SELECT id, name FROM customers WHERE id IN (1, 2, 3, 4, 5, 6);
            """),
            ex("Replace a loop with one aggregate", "intermediate", "Item counts and totals for every order in a single round trip.", "sql", """
                SELECT o.id, c.name, COUNT(i.product_id) AS lines, SUM(i.qty * i.unit_price) AS total
                FROM orders o
                JOIN customers c ON c.id = o.customer_id
                LEFT JOIN order_items i ON i.order_id = o.id
                GROUP BY o.id, c.name ORDER BY o.id LIMIT 10;
            """),
            ex("Eager loading in SQLAlchemy and Django", "intermediate", "Same data, two queries total instead of N+1.", "python", """
                # SQLAlchemy 2.x
                from sqlalchemy import select
                from sqlalchemy.orm import selectinload, joinedload
                stmt = (select(Order)
                        .options(joinedload(Order.customer), selectinload(Order.items))
                        .limit(50))
                orders = session.scalars(stmt).unique().all()

                # Django
                orders = (Order.objects.select_related("customer")
                          .prefetch_related("items")[:50])
            """, runnable=False),
        ],
        ["Django: select_related (JOIN), prefetch_related (IN)", "SQLAlchemy: joinedload, selectinload", "Rails: includes / preload / eager_load", "JPA: JOIN FETCH, @EntityGraph", "bulk_create / executemany / COPY"],
        [
            "Fixing N+1 with a JOIN on a to-many relationship can multiply rows and memory.",
            "Lazy loading in templates triggers queries far from the code that fetched the list.",
            "ORM save() in a loop runs one INSERT and often one transaction per row.",
        ],
        [
            qa("basic", "What is the N+1 query problem?", "Running one query to fetch N parent rows, then one more query per row to fetch related data, so N+1 round trips instead of one or two. It usually comes from ORM lazy loading in a loop."),
            qa("intermediate", "How do you fix N+1?", "Eager load: a JOIN for to-one relations, or a second query with WHERE id IN (...) for to-many relations. Alternatively write one aggregate SQL query that returns exactly what the page needs."),
            qa("intermediate", "How do you detect N+1 problems before production?", "Enable query logging in development, use APM traces showing repeated similar queries, add tests asserting the number of queries per endpoint, and use tools such as Bullet (Rails) or nplusone (Python)."),
            qa("advanced", "JOIN-based eager loading vs separate IN query: trade-offs?", "A JOIN is one round trip but duplicates parent columns for each child and can explode with multiple to-many joins. Separate IN queries cost one extra round trip per relation but return compact results. Use JOIN for to-one and IN for to-many."),
        ],
        ["query-plans", "connection-pooling", "joins"],
        chain(
            ("List", "1 query", "Fetch list", "The page fetches 50 orders in one query."),
            ("Loop", "for each order", "Lazy access", "Template accesses order.customer for each row.", "50x"),
            ("N queries", "50 round trips", "Query storm", "Each access issues its own SELECT: 1 + 50 queries.", "SELECT"),
            ("Eager load", "JOIN / IN", "Fix", "Eager loading fetches all customers in one batched query.", "IN (...)"),
            ("2 queries", "constant", "Result", "Query count stays constant regardless of page size.", "done"),
        ),
    ),
    topic(
        "connection-pooling", "Connection Pooling", "performance", "intermediate", "CP",
        "Reuse a small set of database connections instead of opening one per request.",
        "A taxi rank: a handful of taxis serve a queue of passengers. Buying a new car for every passenger and scrapping it after the ride would be absurd, and parking 5,000 taxis at the station would block the road.",
        "Opening a database connection is expensive: TCP and TLS handshakes, authentication, and in Postgres a new backend process with its own memory. A connection pool keeps a set of open connections and lends them to requests, returning them afterwards. Pools exist in the application (HikariCP, SQLAlchemy pool, pgx) and as external proxies (PgBouncer, RDS Proxy, ProxySQL) that multiplex thousands of client connections onto a few server connections. More connections is not more throughput: a database has a limited number of cores and disks, and beyond a small multiple of cores, contention, context switching and memory use make everything slower. PgBouncer's transaction mode gives the best multiplexing but breaks session state (session-level prepared statements, SET, advisory locks, LISTEN). Size pools from the database outward: total connections across all app instances must stay below max_connections with headroom, and timeouts must surface pool exhaustion quickly.",
        [
            "Serverless functions that would otherwise open a connection per invocation.",
            "Hundreds of app pods sharing one Postgres primary.",
            "Smoothing traffic spikes by queueing at the pool rather than overloading the database.",
        ],
        [
            "Start with roughly (cores x 2) + effective spindles active connections on the server side, then measure.",
            "Total pool size = instances x pool size per instance: autoscaling can exhaust max_connections.",
            "PgBouncer modes: session (safe), transaction (best multiplexing), statement (rare).",
            "Set acquire timeouts, max lifetime and idle timeouts; validate connections.",
            "Always return connections (context managers / try-finally) to avoid leaks.",
        ],
        [
            ex("Pool configuration in SQLAlchemy", "intermediate", "Bounded pool with overflow, timeouts and liveness checks; credentials come from the environment.", "python", """
                import os
                from sqlalchemy import create_engine

                engine = create_engine(
                    os.environ["DATABASE_URL"],      # e.g. postgresql+psycopg://app@db.internal/shop
                    pool_size=10,                    # steady-state connections per process
                    max_overflow=5,                  # short bursts
                    pool_timeout=5,                  # seconds to wait for a free connection
                    pool_recycle=1800,               # replace connections every 30 min
                    pool_pre_ping=True,              # detect dead connections
                    connect_args={"sslmode": "verify-full"},
                )

                with engine.connect() as conn:       # returned to the pool on exit
                    conn.exec_driver_sql("SELECT 1")
            """, runnable=False),
            ex("PgBouncer in transaction mode", "advanced", "5,000 clients multiplexed onto 40 server connections.", "text", """
                [databases]
                shop = host=10.0.0.5 port=5432 dbname=shop

                [pgbouncer]
                listen_port = 6432
                pool_mode = transaction
                max_client_conn = 5000
                default_pool_size = 40
                server_tls_sslmode = verify-full
                auth_type = scram-sha-256
                auth_file = /etc/pgbouncer/userlist.txt   ; managed by secrets tooling, not committed
            """, runnable=False),
            ex("Inspect connections in Postgres", "intermediate", "Who is connected and what are they doing.", "sql", """
                SELECT state, count(*) FROM pg_stat_activity GROUP BY state;
                SELECT pid, usename, state, now() - xact_start AS tx_age, query
                FROM pg_stat_activity WHERE state = 'idle in transaction' ORDER BY tx_age DESC;
                SHOW max_connections;
            """, runnable=False),
        ],
        ["pool_size / max_overflow / pool_timeout", "HikariCP: maximumPoolSize, connectionTimeout, maxLifetime", "PgBouncer pool_mode = transaction", "SELECT count(*) FROM pg_stat_activity", "idle_in_transaction_session_timeout = '60s'"],
        [
            "Autoscaling app instances multiplies pool sizes past max_connections.",
            "Transaction-mode poolers break session features: SET, temp tables, session advisory locks.",
            "Leaked connections (not returned on exceptions) slowly exhaust the pool.",
            "Idle-in-transaction sessions hold locks and block vacuum.",
        ],
        [
            qa("basic", "Why use a connection pool?", "Creating connections is slow (TCP, TLS, auth, backend process). A pool reuses open connections, cutting latency and bounding the load placed on the database."),
            qa("intermediate", "Why can a larger pool make things slower?", "The database has finite cores and I/O. Past a point, more concurrent queries cause lock and CPU contention, context switching and memory pressure, so throughput drops and latency rises. Queueing at the pool is cheaper than queueing inside the database."),
            qa("advanced", "PgBouncer session vs transaction pooling?", "Session mode assigns a server connection for the client's whole session: compatible but little multiplexing. Transaction mode assigns one per transaction: high multiplexing but session state (SET, prepared statements without protocol support, temp tables, LISTEN, session advisory locks) is not preserved."),
            qa("intermediate", "How do you size connection pools across many app instances?", "Work backwards from the database: choose a safe total of active connections (near a small multiple of cores), divide by the maximum instance count, leave headroom for admin and replication, or put a proxy like PgBouncer in front."),
        ],
        ["n-plus-one-orm", "transactions-acid", "locking-deadlocks"],
        chain(
            ("Requests", "thousands", "Incoming requests", "Many app threads or pods need the database."),
            ("Pool", "borrow conn", "Borrow", "Each request borrows an open connection from the pool.", "acquire"),
            ("Database", "few backends", "Execute", "A bounded number of server connections run queries.", "query"),
            ("Return", "release", "Return", "The connection goes back to the pool after the transaction.", "release"),
            ("Queue", "timeout", "Backpressure", "When all are busy, requests wait briefly or fail fast.", "wait"),
        ),
    ),
    topic(
        "partitioning", "Table Partitioning", "performance", "advanced", "PA",
        "Split one big table into smaller physical pieces by range, list or hash.",
        "Filing cabinets labelled by year. Looking for a 2024 invoice, you open one drawer instead of all of them, and throwing away 2015 means removing one drawer rather than shredding page by page.",
        "Partitioning splits a logical table into child tables (partitions) inside one database, each holding a subset of rows chosen by a partition key. Range partitioning (by month or id range) suits time-series and retention; list partitioning groups discrete values (region, tenant tier); hash partitioning spreads rows evenly when there is no natural range. The planner performs partition pruning: a query filtering on the partition key reads only matching partitions, and pruning can also happen at execution time for parameters. Maintenance becomes cheap: dropping or detaching an old partition is a metadata operation instead of a massive DELETE that bloats tables and WAL. Each partition has its own smaller indexes, which helps vacuum and cache locality. The costs are planning overhead with thousands of partitions, unique constraints that must include the partition key, and queries that do not filter on the key scanning every partition. Partitioning is local to one server; sharding distributes partitions across servers.",
        [
            "Monthly partitions for events with 13-month retention.",
            "List partitions per region for data residency.",
            "Hash partitions to reduce index contention on a hot table.",
        ],
        [
            "Choose the key your queries filter on most; otherwise pruning never happens.",
            "Drop/detach partitions for retention instead of DELETE.",
            "Primary keys and unique constraints must include the partition key (Postgres).",
            "Pre-create future partitions (pg_partman, cron) and keep a DEFAULT partition for strays.",
            "Too many partitions increases planning time and memory.",
        ],
        [
            ex("Declarative range partitioning (Postgres)", "intermediate", "Monthly partitions; old months are detached instantly.", "sql", """
                CREATE TABLE events (
                  id bigint GENERATED ALWAYS AS IDENTITY,
                  user_id bigint NOT NULL,
                  kind text NOT NULL,
                  ts timestamptz NOT NULL,
                  PRIMARY KEY (id, ts)
                ) PARTITION BY RANGE (ts);
                CREATE TABLE events_2024_06 PARTITION OF events FOR VALUES FROM ('2024-06-01') TO ('2024-07-01');
                CREATE TABLE events_2024_07 PARTITION OF events FOR VALUES FROM ('2024-07-01') TO ('2024-08-01');
                CREATE TABLE events_default PARTITION OF events DEFAULT;
                EXPLAIN SELECT count(*) FROM events WHERE ts >= '2024-07-01' AND ts < '2024-07-15';
                ALTER TABLE events DETACH PARTITION events_2024_06 CONCURRENTLY;
            """, runnable=False),
            ex("Manual partitions with a UNION ALL view", "advanced", "SQLite has no native partitioning; per-period tables plus a view show the idea and cheap retention.", "sql", """
                CREATE TABLE orders_2024_06 AS SELECT * FROM orders WHERE created_at >= '2024-06-01' AND created_at < '2024-07-01';
                CREATE TABLE orders_2024_07 AS SELECT * FROM orders WHERE created_at >= '2024-07-01' AND created_at < '2024-08-01';
                CREATE VIEW orders_all AS
                  SELECT * FROM orders_2024_06 UNION ALL SELECT * FROM orders_2024_07;
                SELECT strftime('%Y-%m', created_at) AS month, COUNT(*) FROM orders_all GROUP BY month;
                DROP VIEW orders_all;
                DROP TABLE orders_2024_06;   -- retention: drop a whole month at once
                SELECT name FROM sqlite_master WHERE name LIKE 'orders_2024%';
            """),
            ex("Hash and list partitions (Postgres)", "advanced", "Even spread by tenant, and residency by region.", "sql", """
                CREATE TABLE sessions (tenant_id bigint, id uuid, data jsonb) PARTITION BY HASH (tenant_id);
                CREATE TABLE sessions_p0 PARTITION OF sessions FOR VALUES WITH (MODULUS 4, REMAINDER 0);
                -- ... p1..p3
                CREATE TABLE customers (id bigint, region text, name text) PARTITION BY LIST (region);
                CREATE TABLE customers_eu PARTITION OF customers FOR VALUES IN ('eu-west', 'eu-central');
            """, runnable=False),
        ],
        ["PARTITION BY RANGE (ts) | LIST (region) | HASH (id)", "CREATE TABLE p PARTITION OF t FOR VALUES FROM (a) TO (b)", "ALTER TABLE t DETACH PARTITION p CONCURRENTLY", "CREATE TABLE p PARTITION OF t DEFAULT", "pg_partman: automated partition creation and retention"],
        [
            "Queries without the partition key in WHERE scan all partitions.",
            "Global uniqueness on a non-key column is impossible across partitions in Postgres.",
            "Forgetting to create next month's partition makes inserts fail (or land in DEFAULT).",
        ],
        [
            qa("intermediate", "Partitioning vs sharding?", "Partitioning splits a table into pieces within one database server; the engine routes and prunes automatically. Sharding distributes data across multiple servers, adding network routing, cross-shard queries and distributed transactions."),
            qa("intermediate", "What is partition pruning?", "The planner (or executor, for parameters) skips partitions whose bounds cannot match the WHERE clause on the partition key, so only relevant partitions are scanned."),
            qa("advanced", "Why is dropping a partition better than DELETE for retention?", "DELETE touches every row, generates massive WAL, leaves dead tuples for vacuum and holds locks. Dropping or detaching a partition is a quick metadata change that frees space immediately."),
            qa("advanced", "When does partitioning hurt?", "When queries rarely filter on the partition key (scans hit every partition), with thousands of partitions (planning overhead), and when you need global unique constraints on non-key columns."),
        ],
        ["replication-sharding", "time-series-databases", "indexes"],
        chain(
            ("Query", "WHERE ts in Jul", "Query arrives", "A query filters on the partition key."),
            ("Router", "partition bounds", "Pruning", "The planner compares the filter with each partition's bounds.", "ts"),
            ("Jul part", "scanned", "Scan one", "Only the July partition and its indexes are read.", "July"),
            ("Others", "skipped", "Skip rest", "Other months are never touched.", "pruned"),
            ("Retention", "DROP partition", "Cheap retention", "Old months are dropped as a metadata operation.", "drop"),
        ),
    ),
    # ------------------------------------------------------------------ transactions
    topic(
        "locking-deadlocks", "Locking & Deadlocks", "transactions", "intermediate", "LK",
        "Row, table and advisory locks, lock waits, and how deadlocks form and are resolved.",
        "Two cars meet on a one-lane bridge from opposite sides; each waits for the other to reverse. The traffic officer (deadlock detector) picks one driver and makes them back up.",
        "Databases take locks to keep concurrent writes correct. Row locks are acquired by UPDATE, DELETE and SELECT ... FOR UPDATE/FOR SHARE and held until the transaction ends. Table-level locks come in modes (Postgres has eight, from ACCESS SHARE to ACCESS EXCLUSIVE) so DDL and maintenance coordinate with normal queries. InnoDB also uses gap and next-key locks under REPEATABLE READ to prevent phantoms. A deadlock occurs when transactions wait for each other in a cycle; the engine's detector finds the cycle (Postgres after deadlock_timeout, default 1s) and aborts one victim, which must retry. Prevention: acquire locks in a consistent order (for example sort ids before updating), keep transactions short, avoid user interaction or network calls inside transactions, and use indexes so fewer rows are locked. Advisory locks provide application-defined mutexes, and NOWAIT or SKIP LOCKED avoid waiting entirely, which is how robust job queues are built.",
        [
            "Transferring money between two accounts in both directions concurrently.",
            "Building a job queue with SELECT ... FOR UPDATE SKIP LOCKED.",
            "Ensuring only one instance runs a cron job via an advisory lock.",
        ],
        [
            "Locks are held until COMMIT/ROLLBACK, not until the statement ends.",
            "Consistent lock ordering prevents most deadlocks.",
            "Deadlock victims get an error; the application must retry the transaction.",
            "SKIP LOCKED lets workers grab different rows without blocking each other.",
            "Missing indexes cause UPDATE ... WHERE to lock (or scan) many more rows.",
        ],
        [
            ex("Deadlock between two sessions (Postgres)", "intermediate", "Opposite lock order across two sessions creates a cycle.", "sql", """
                -- Session A                                  -- Session B
                BEGIN;                                        BEGIN;
                UPDATE accounts SET balance = balance - 10    UPDATE accounts SET balance = balance - 5
                  WHERE id = 1;                                 WHERE id = 2;
                UPDATE accounts SET balance = balance + 10    UPDATE accounts SET balance = balance + 5
                  WHERE id = 2;   -- waits for B                WHERE id = 1;   -- waits for A -> deadlock
                -- ERROR: deadlock detected (one session is aborted, the other proceeds)
                -- Fix: always lock the lower id first, e.g. SELECT ... WHERE id IN (1,2) ORDER BY id FOR UPDATE
            """, runnable=False),
            ex("Job queue with SKIP LOCKED", "advanced", "Each worker claims a different pending job without blocking.", "sql", """
                BEGIN;
                SELECT id, payload FROM jobs
                WHERE status = 'pending'
                ORDER BY created_at
                FOR UPDATE SKIP LOCKED
                LIMIT 1;
                UPDATE jobs SET status = 'running', started_at = now() WHERE id = $1;
                COMMIT;
            """, runnable=False),
            ex("Write lock in SQLite", "basic", "SQLite locks the whole database for writes; BEGIN IMMEDIATE takes the write lock up front.", "sql", """
                BEGIN IMMEDIATE;
                UPDATE accounts SET balance = balance - 25 WHERE id = 1;
                UPDATE accounts SET balance = balance + 25 WHERE id = 2;
                COMMIT;
                SELECT owner, balance FROM accounts;
            """),
        ],
        ["SELECT ... FOR UPDATE [NOWAIT | SKIP LOCKED]", "LOCK TABLE t IN SHARE MODE", "SELECT pg_advisory_xact_lock(42)", "SELECT * FROM pg_locks WHERE NOT granted", "SET deadlock_timeout = '1s'; SET lock_timeout = '5s'"],
        [
            "Holding a transaction open while calling an external API keeps locks for seconds.",
            "Foreign key checks take share locks on parent rows, a common hidden deadlock source.",
            "SKIP LOCKED queues are not strictly FIFO.",
        ],
        [
            qa("basic", "What is a deadlock?", "Two or more transactions each hold a lock the other needs, forming a cycle so none can proceed. The database detects it and aborts one transaction as the victim."),
            qa("intermediate", "How do you prevent deadlocks?", "Acquire locks in a consistent global order, keep transactions short, lock everything needed up front (SELECT ... FOR UPDATE in id order), add indexes so fewer rows are locked, and retry victims automatically."),
            qa("advanced", "How does FOR UPDATE SKIP LOCKED help build a job queue?", "Each worker selects pending rows and locks them, skipping rows already locked by other workers, so many workers dequeue concurrently without blocking or double-processing."),
            qa("intermediate", "Lock wait vs deadlock?", "A lock wait is one transaction waiting for another to finish; it resolves when the holder commits. A deadlock is a cycle of waits that can never resolve on its own, so the engine must abort a participant."),
            qa("advanced", "What are gap locks in InnoDB?", "Under REPEATABLE READ, InnoDB locks the gaps between index records (next-key locks) during range scans and locking reads, preventing other transactions from inserting phantom rows into that range. They can cause unexpected blocking and deadlocks on inserts."),
        ],
        ["isolation-mvcc", "optimistic-pessimistic", "transactions-acid"],
        chain(
            ("T1 locks A", "row 1", "First lock", "T1 updates row 1 and holds its lock."),
            ("T2 locks B", "row 2", "Second lock", "T2 updates row 2 and holds its lock.", "lock"),
            ("Cross wait", "T1->2, T2->1", "Cycle", "T1 wants row 2, T2 wants row 1: a wait cycle.", "wait"),
            ("Detector", "find cycle", "Detection", "After deadlock_timeout the detector finds the cycle.", "cycle"),
            ("Abort", "victim retries", "Resolution", "One transaction is aborted; the app retries it.", "retry"),
        ),
    ),
    topic(
        "optimistic-pessimistic", "Optimistic vs Pessimistic Concurrency", "transactions", "intermediate", "OP",
        "Lock first, or detect conflicts at write time and retry.",
        "Pessimistic: you reserve the meeting room in advance so no one else can take it. Optimistic: you just walk in, and if someone else booked it in the meantime, you go and pick another slot.",
        "Pessimistic concurrency control assumes conflicts are likely and prevents them by locking: SELECT ... FOR UPDATE holds the row until commit, so competing writers wait. It is simple to reason about and avoids wasted work, but reduces concurrency and can deadlock. Optimistic concurrency control assumes conflicts are rare: read without locks, then write with a condition that detects whether the data changed, typically a version number or updated_at column (UPDATE ... WHERE id = ? AND version = ?). If zero rows are updated, someone else won and the operation is retried or reported to the user. Optimistic control fits web applications where a user edits a form for minutes, since you cannot hold a database lock across HTTP requests. HTTP ETags with If-Match bring the same idea to APIs. Serializable Snapshot Isolation is optimistic at the engine level: it aborts conflicting transactions at commit time.",
        [
            "Edit forms where two users might save the same record (optimistic, version column).",
            "Inventory decrement on a hot item during a flash sale (pessimistic or atomic UPDATE).",
            "REST APIs using ETag / If-Match to avoid lost updates.",
        ],
        [
            "Optimistic: no locks, conflict detected by affected-row count, retry on failure.",
            "Pessimistic: FOR UPDATE locks rows until commit; others wait.",
            "High contention favours pessimistic (retries become expensive); low contention favours optimistic.",
            "Never hold a DB lock across user think time; use versions instead.",
            "A single atomic UPDATE (stock = stock - 1 WHERE stock > 0) often avoids both.",
        ],
        [
            ex("Version column", "basic", "Two users loaded version 1; the second save matches 0 rows and must reload.", "sql", """
                CREATE TABLE docs (id INTEGER PRIMARY KEY, body TEXT, version INTEGER NOT NULL DEFAULT 1);
                INSERT INTO docs (id, body) VALUES (1, 'draft');
                UPDATE docs SET body = 'edit by Asha', version = version + 1 WHERE id = 1 AND version = 1;
                SELECT changes() AS asha_rows;
                UPDATE docs SET body = 'edit by Ben', version = version + 1 WHERE id = 1 AND version = 1;
                SELECT changes() AS ben_rows;
                SELECT * FROM docs;
            """),
            ex("Atomic conditional decrement", "intermediate", "No read-modify-write race: the condition and the update are one statement.", "sql", """
                CREATE TABLE stock (sku TEXT PRIMARY KEY, qty INTEGER NOT NULL CHECK (qty >= 0));
                INSERT INTO stock VALUES ('KB-1', 2);
                UPDATE stock SET qty = qty - 1 WHERE sku = 'KB-1' AND qty >= 1;
                UPDATE stock SET qty = qty - 1 WHERE sku = 'KB-1' AND qty >= 1;
                UPDATE stock SET qty = qty - 1 WHERE sku = 'KB-1' AND qty >= 1;
                SELECT changes() AS third_buyer_rows, (SELECT qty FROM stock) AS left;
            """),
            ex("Optimistic retry loop", "advanced", "Application-side retry with a bounded number of attempts.", "python", """
                def rename_doc(conn, doc_id, new_title, attempts=3):
                    for _ in range(attempts):
                        title, version = conn.execute(
                            "SELECT title, version FROM docs WHERE id = ?", (doc_id,)).fetchone()
                        cur = conn.execute(
                            "UPDATE docs SET title = ?, version = version + 1 WHERE id = ? AND version = ?",
                            (new_title, doc_id, version))
                        if cur.rowcount == 1:
                            conn.commit()
                            return True
                        conn.rollback()          # someone else won; reload and retry
                    raise RuntimeError("too much contention, ask the user to retry")
            """, runnable=False),
        ],
        ["UPDATE t SET ..., version = version + 1 WHERE id = ? AND version = ?", "SELECT ... FOR UPDATE", "HTTP: ETag + If-Match -> 412 Precondition Failed", "JPA @Version / Django select_for_update()", "SET TRANSACTION ISOLATION LEVEL SERIALIZABLE (optimistic SSI)"],
        [
            "Forgetting to check the affected row count turns optimistic locking into silent lost updates.",
            "Optimistic retries under heavy contention waste work and can livelock.",
            "Pessimistic locks across slow external calls stall everyone else.",
        ],
        [
            qa("basic", "Optimistic vs pessimistic locking?", "Pessimistic locks data before changing it so others wait. Optimistic does not lock; it checks at write time (version column) whether the data changed and retries if so."),
            qa("intermediate", "How do you implement optimistic locking?", "Add a version column. Read it with the row, then UPDATE ... SET version = version + 1 WHERE id = ? AND version = :read_version. If the update affects 0 rows, there was a conflict: reload and retry or report to the user."),
            qa("intermediate", "When is pessimistic locking the better choice?", "When contention is high and retries are expensive, such as a hot inventory row or a ledger balance, or when the operation has side effects that cannot be safely repeated."),
            qa("advanced", "How does HTTP map to optimistic concurrency?", "The server returns an ETag (version) with GET; the client sends If-Match with PUT/PATCH; the server performs a conditional update and returns 412 Precondition Failed if the version changed."),
        ],
        ["isolation-mvcc", "locking-deadlocks", "upserts"],
        chain(
            ("Read", "row + version 1", "Read", "Both users read the row at version 1."),
            ("Edit", "in the app", "Think time", "Users edit without holding any database lock.", "v1"),
            ("Write A", "WHERE version=1", "First write wins", "A's conditional update matches and bumps version to 2.", "1 row"),
            ("Write B", "0 rows", "Conflict detected", "B's update matches 0 rows: version moved on.", "0 rows"),
            ("Retry", "reload, merge", "Resolve", "B reloads the latest version and retries or merges.", "retry"),
        ),
    ),
    topic(
        "isolation-anomalies", "Isolation Anomalies Deep Dive", "transactions", "advanced", "IA",
        "Dirty reads, lost updates, read skew, write skew and phantoms, with concrete examples.",
        "Accountants working on copies of the same ledger: one reads a figure before the other has finished correcting it (dirty read), two overwrite each other's edits (lost update), and two each approve a withdrawal believing the other account still covers the minimum (write skew).",
        "Isolation anomalies are what goes wrong when concurrent transactions interleave. Dirty read: reading uncommitted data that is later rolled back. Non-repeatable read: re-reading a row returns a different committed value. Read skew: seeing parts of a related set at different points in time (balance of account A before a transfer and B after it). Lost update: two read-modify-write cycles overwrite each other. Phantom read: re-running a range query returns new rows inserted by others. Write skew: two transactions read overlapping data, make decisions, and write disjoint rows, jointly violating an invariant. The SQL standard defines levels by which of these they forbid, but real engines differ: Postgres Repeatable Read is snapshot isolation (no phantoms, but write skew possible and lost updates detected as serialization errors), while MySQL InnoDB Repeatable Read uses snapshots for plain reads and next-key locks for locking reads. Only Serializable (or explicit locking / materialized conflicts) prevents write skew.",
        [
            "Double-booking a meeting room after both transactions checked availability.",
            "On-call scheduling where at least one doctor must remain on call.",
            "Financial reports that must see a consistent snapshot across tables.",
        ],
        [
            "Read Committed: no dirty reads, but non-repeatable reads, read skew and lost updates possible.",
            "Snapshot isolation: consistent snapshot per transaction; write skew still possible.",
            "Serializable: equivalent to some serial order; expect and retry serialization failures.",
            "Materialize the conflict (lock a parent row or a slot row) to fix write skew without Serializable.",
            "Check your engine's actual guarantees; names of levels are not portable.",
        ],
        [
            ex("Write skew walkthrough (Postgres, Repeatable Read)", "advanced", "Both transactions see two doctors on call and both go off call.", "sql", """
                -- invariant: at least one doctor on call for shift 7
                -- T1                                           -- T2
                BEGIN ISOLATION LEVEL REPEATABLE READ;         BEGIN ISOLATION LEVEL REPEATABLE READ;
                SELECT count(*) FROM on_call WHERE shift = 7;  SELECT count(*) FROM on_call WHERE shift = 7;
                -- returns 2                                    -- returns 2
                UPDATE on_call SET active = false              UPDATE on_call SET active = false
                  WHERE shift = 7 AND doctor = 'asha';           WHERE shift = 7 AND doctor = 'ben';
                COMMIT;                                         COMMIT;   -- both succeed: 0 on call!
                -- Under SERIALIZABLE, one COMMIT fails with: could not serialize access (SQLSTATE 40001)
            """, runnable=False),
            ex("Lost update vs atomic update", "intermediate", "Simulated: two read-modify-write cycles based on the same read; the second overwrites the first.", "sql", """
                CREATE TABLE counters (name TEXT PRIMARY KEY, n INTEGER NOT NULL);
                INSERT INTO counters VALUES ('likes', 10);
                -- T1 and T2 both read n = 10, both compute 10 + 1 in the app
                UPDATE counters SET n = 11 WHERE name = 'likes';   -- T1 writes
                UPDATE counters SET n = 11 WHERE name = 'likes';   -- T2 writes: one like lost
                SELECT n AS after_lost_update FROM counters;
                -- fix: let the database do the read-modify-write atomically
                UPDATE counters SET n = n + 1 WHERE name = 'likes';
                UPDATE counters SET n = n + 1 WHERE name = 'likes';
                SELECT n AS after_atomic FROM counters;
            """),
            ex("Materializing the conflict", "advanced", "Lock a shared parent row so concurrent checks serialize even at Read Committed.", "sql", """
                BEGIN;
                SELECT 1 FROM shifts WHERE id = 7 FOR UPDATE;        -- both T1 and T2 must take this lock
                SELECT count(*) FROM on_call WHERE shift = 7 AND active;
                UPDATE on_call SET active = false WHERE shift = 7 AND doctor = 'asha';
                COMMIT;
            """, runnable=False),
        ],
        ["SET TRANSACTION ISOLATION LEVEL READ COMMITTED | REPEATABLE READ | SERIALIZABLE", "SQLSTATE 40001 serialization_failure -> retry", "SQLSTATE 40P01 deadlock_detected -> retry", "SELECT ... FOR UPDATE on a parent row (materialize conflict)", "SHOW transaction_isolation"],
        [
            "Assuming Repeatable Read prevents write skew; it does not under snapshot isolation.",
            "Running reports at Read Committed across several statements can mix snapshots (read skew).",
            "Using Serializable without a retry loop surfaces random errors to users.",
        ],
        [
            qa("intermediate", "What is a lost update and how do you prevent it?", "Two transactions read the same value, modify it in the app and write back; the second write overwrites the first. Prevent with atomic UPDATE x = x + 1, SELECT ... FOR UPDATE, optimistic version checks, or Repeatable Read/Serializable that detect the conflict."),
            qa("advanced", "What is write skew and which isolation level prevents it?", "Two transactions read an overlapping set, each decides based on it and writes different rows, jointly breaking an invariant (both doctors go off call). Snapshot isolation allows it; Serializable (SSI in Postgres) or explicit locking of the checked data prevents it."),
            qa("advanced", "What is read skew?", "Seeing an inconsistent state because different reads come from different points in time, for example account A before a transfer and account B after it, so the total looks wrong. Snapshot isolation prevents it by reading all data from one snapshot."),
            qa("advanced", "Is Postgres Repeatable Read the same as the SQL standard's?", "It is stronger than the standard (it also prevents phantoms, since it is snapshot isolation) but still allows write skew. Concurrent updates to the same row cause a serialization error instead of a lost update."),
            qa("intermediate", "What is a phantom read?", "A transaction re-runs a range query and sees rows inserted or deleted by another committed transaction in between. Prevented by snapshot isolation for plain reads, by predicate/gap locks, or by Serializable."),
        ],
        ["isolation-mvcc", "locking-deadlocks", "optimistic-pessimistic"],
        chain(
            ("T1 reads", "2 on call", "T1 checks", "T1 reads the invariant: two doctors on call."),
            ("T2 reads", "2 on call", "T2 checks", "T2 reads the same snapshot: also two.", "snapshot"),
            ("Disjoint", "different rows", "Disjoint writes", "Each updates a different row, so no row conflict is seen.", "write"),
            ("Both commit", "0 on call", "Invariant broken", "Under snapshot isolation both commit: write skew.", "commit"),
            ("Serializable", "abort one", "Prevention", "SSI detects the dangerous pattern and aborts one; retry.", "40001"),
        ),
    ),
    topic(
        "wal-durability", "WAL, Checkpoints & Durability", "transactions", "advanced", "WL",
        "How write-ahead logging makes commits survive crashes, and what fsync and checkpoints do.",
        "A chef jots every order on a ticket spike before cooking. If the kitchen loses power mid-service, the tickets show exactly what was promised and what still needs to be made.",
        "Write-ahead logging (WAL; redo log in InnoDB) is the rule that a change must be recorded in a sequential log and flushed to stable storage before the modified data pages are written. On COMMIT the engine appends a commit record and calls fsync on the log; data pages stay dirty in the buffer pool and are written later in the background. After a crash, recovery replays (redoes) the log from the last checkpoint so committed changes are reapplied, and uncommitted ones are ignored or undone. Checkpoints periodically flush dirty pages so the log needed for recovery stays bounded; frequent checkpoints shorten recovery but increase I/O, and full-page writes guard against torn pages after each checkpoint. The same log stream powers physical replication, point-in-time recovery and logical decoding for CDC. Durability knobs such as synchronous_commit = off, innodb_flush_log_at_trx_commit = 2 or group commit trade a small window of possible data loss for throughput.",
        [
            "Understanding why COMMIT latency depends on disk fsync latency.",
            "Tuning checkpoint intervals to avoid I/O spikes.",
            "Deciding whether async commit is acceptable for analytics events.",
        ],
        [
            "Log first, data later: sequential log writes are cheap, random page writes are deferred.",
            "Recovery = redo from last checkpoint (+ undo for uncommitted work in ARIES-style engines).",
            "Group commit batches many transactions into one fsync.",
            "WAL is also the replication and PITR stream.",
            "Disks or controllers that lie about fsync (volatile caches) break durability.",
        ],
        [
            ex("WAL mode and commit behaviour (SQLite)", "intermediate", "SQLite's journal modes are set by PRAGMA (blocked in this playground); a transaction still commits atomically.", "sql", """
                -- PRAGMA journal_mode = WAL;   PRAGMA synchronous = FULL;   (run in a real sqlite3 shell)
                BEGIN;
                UPDATE accounts SET balance = balance - 100 WHERE owner = 'alice';
                UPDATE accounts SET balance = balance + 100 WHERE owner = 'carol';
                COMMIT;
                SELECT owner, balance FROM accounts;
            """),
            ex("Postgres WAL settings and inspection", "advanced", "Durability and checkpoint knobs, and where the log is.", "sql", """
                SHOW wal_level;                -- replica | logical
                SHOW synchronous_commit;       -- on (durable) | off (may lose last ~600ms on crash)
                SHOW checkpoint_timeout;       -- e.g. 15min
                SHOW max_wal_size;             -- checkpoint also triggered by WAL volume
                SELECT pg_current_wal_lsn(), pg_walfile_name(pg_current_wal_lsn());
                SET synchronous_commit = off;  -- per transaction, for low-value writes only
            """, runnable=False),
        ],
        ["wal_level = replica | logical", "synchronous_commit = on | off | remote_apply", "checkpoint_timeout, max_wal_size", "innodb_flush_log_at_trx_commit = 1", "PRAGMA journal_mode = WAL (SQLite)"],
        [
            "Turning off fsync for speed risks unrecoverable corruption, not just lost commits.",
            "A huge max_wal_size means fewer checkpoints but longer crash recovery.",
            "A replication slot that is never consumed keeps WAL forever and fills the disk.",
        ],
        [
            qa("intermediate", "What is write-ahead logging?", "Before a data page change is written, a log record describing it is appended to the WAL and flushed. COMMIT waits only for the log flush, and after a crash the log is replayed to restore committed changes."),
            qa("advanced", "Why is writing the log first faster than writing data pages on commit?", "The log is append-only sequential I/O and one fsync can cover many transactions (group commit). Data pages are scattered random writes; deferring them lets the engine batch and coalesce changes."),
            qa("advanced", "What is a checkpoint and what is the trade-off?", "A checkpoint flushes all dirty pages and records a point from which recovery can start. Frequent checkpoints mean faster recovery but more write I/O (and more full-page images); infrequent ones mean smoother I/O but longer recovery."),
            qa("advanced", "What does synchronous_commit = off risk?", "COMMIT returns before the WAL is flushed, so a crash can lose the last few hundred milliseconds of committed transactions. The database stays consistent (no corruption), unlike disabling fsync."),
        ],
        ["transactions-acid", "backups-pitr", "change-data-capture"],
        chain(
            ("Change", "UPDATE row", "Modify in memory", "The page is changed in the buffer pool (dirty)."),
            ("WAL", "append record", "Log first", "A redo record is appended to the WAL buffer.", "record"),
            ("fsync", "on COMMIT", "Durable commit", "COMMIT flushes the log; the client gets OK.", "fsync"),
            ("Checkpoint", "flush pages", "Checkpoint", "Dirty pages are written later in the background.", "pages"),
            ("Recovery", "redo log", "Crash recovery", "After a crash, replay WAL from the last checkpoint.", "redo"),
        ),
    ),
    topic(
        "distributed-transactions", "Distributed Transactions, 2PC & Sagas", "transactions", "advanced", "DX",
        "Atomic changes across databases or services: two-phase commit, sagas and the outbox pattern.",
        "A wedding: the officiant asks both partners 'do you?' (prepare). Only if both say yes does the officiant pronounce them married (commit). If the officiant faints between the vows and the pronouncement, everyone waits in uncertainty.",
        "When one business operation spans multiple databases or services, local ACID transactions are not enough. Two-phase commit (2PC) uses a coordinator: in the prepare phase every participant durably records that it can commit and votes yes or no; in the commit phase the coordinator tells all to commit (or abort). 2PC is atomic but blocking: if the coordinator fails after participants prepared, they hold locks until it recovers, and latency includes multiple round trips. XA and Postgres PREPARE TRANSACTION implement it. Microservice architectures usually prefer sagas: a sequence of local transactions where each step publishes an event and failures trigger compensating actions (refund, release stock), giving eventual consistency without distributed locks. The transactional outbox pattern makes 'update DB and publish event' atomic by inserting the event into an outbox table in the same local transaction and relaying it to the broker (often via CDC). Consumers must be idempotent because delivery is at-least-once.",
        [
            "Order service, payment service and inventory service completing one checkout.",
            "Moving money between two banks' ledgers.",
            "Publishing an OrderPlaced event reliably after inserting the order.",
        ],
        [
            "2PC: prepare (vote) then commit; atomic but blocking on coordinator failure.",
            "Sagas: local transactions plus compensations; orchestration or choreography.",
            "Outbox: write business row and event row in one local transaction; relay asynchronously.",
            "Consumers must deduplicate (idempotency keys, processed-message table).",
            "Compensations are semantic undo, not rollback: a refund, not erasing the charge.",
        ],
        [
            ex("Transactional outbox", "intermediate", "The order and its event are committed atomically; a relay publishes unsent events.", "sql", """
                CREATE TABLE outbox (
                  id INTEGER PRIMARY KEY, aggregate_id INTEGER NOT NULL, event_type TEXT NOT NULL,
                  payload TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP, published_at TEXT
                );
                BEGIN;
                INSERT INTO orders (id, customer_id, status, created_at) VALUES (100, 3, 'pending', '2024-08-01');
                INSERT INTO outbox (aggregate_id, event_type, payload)
                  VALUES (100, 'OrderPlaced', json_object('order_id', 100, 'customer_id', 3));
                COMMIT;
                -- relay: SELECT unpublished, send to broker, then mark published
                SELECT id, event_type, payload FROM outbox WHERE published_at IS NULL ORDER BY id;
                UPDATE outbox SET published_at = CURRENT_TIMESTAMP WHERE id = 1;
            """),
            ex("Two-phase commit in Postgres", "advanced", "Prepare on each participant, then commit everywhere (requires max_prepared_transactions > 0).", "sql", """
                -- on db1 and db2 (coordinator drives both)
                BEGIN;
                UPDATE accounts SET balance = balance - 100 WHERE id = 1;
                PREPARE TRANSACTION 'transfer-7781';     -- phase 1: durable yes vote
                -- after all participants prepared successfully:
                COMMIT PREPARED 'transfer-7781';         -- phase 2
                -- on any failure: ROLLBACK PREPARED 'transfer-7781';
                SELECT gid, prepared FROM pg_prepared_xacts;   -- find stuck in-doubt transactions
            """, runnable=False),
            ex("Orchestrated saga", "advanced", "Each step has a compensation run in reverse on failure.", "python", """
                STEPS = [
                    ("reserve_stock",  "release_stock"),
                    ("charge_payment", "refund_payment"),
                    ("create_shipment", "cancel_shipment"),
                ]

                def run_saga(order, services):
                    done = []
                    for action, compensation in STEPS:
                        try:
                            getattr(services, action)(order)      # local transaction in that service
                            done.append(compensation)
                        except Exception:
                            for comp in reversed(done):
                                getattr(services, comp)(order)    # must be idempotent
                            raise
            """, runnable=False),
        ],
        ["PREPARE TRANSACTION 'gid'; COMMIT PREPARED 'gid'", "XA START / XA PREPARE / XA COMMIT (MySQL)", "outbox table + relay (Debezium outbox router)", "saga: action + compensation per step", "processed_messages(message_id PRIMARY KEY) for idempotent consumers"],
        [
            "Forgotten prepared transactions hold locks and block vacuum indefinitely.",
            "Publishing to a broker inside the DB transaction is not atomic: the broker may get the event and the DB roll back.",
            "Saga intermediate states are visible to other requests; design the UI and invariants for it.",
        ],
        [
            qa("intermediate", "Explain two-phase commit.", "A coordinator asks each participant to prepare: write everything durably and promise to commit. If all vote yes, it sends commit; if any votes no or times out, it sends abort. Participants that prepared must wait for the decision."),
            qa("advanced", "Why is 2PC called blocking?", "Once a participant has voted yes, it cannot decide unilaterally. If the coordinator crashes before sending the outcome, prepared participants hold locks until the coordinator recovers, reducing availability."),
            qa("advanced", "What is the saga pattern?", "A long-running business transaction split into local transactions, each publishing an event that triggers the next. On failure, compensating transactions semantically undo completed steps. It gives eventual consistency without distributed locks."),
            qa("advanced", "What problem does the transactional outbox solve?", "The dual-write problem: updating the database and publishing a message cannot be made atomic directly. Writing the event into an outbox table in the same local transaction, then relaying it, guarantees the event is published if and only if the change committed (at least once)."),
        ],
        ["transactions-acid", "change-data-capture", "consensus-raft"],
        chain(
            ("Coordinator", "begin global tx", "Start", "The coordinator starts a global transaction."),
            ("Prepare", "all participants", "Phase 1", "Each participant writes its changes durably and votes.", "PREPARE"),
            ("Votes", "yes / no", "Collect votes", "All yes means commit; any no or timeout means abort.", "vote"),
            ("Commit", "COMMIT PREPARED", "Phase 2", "The decision is logged and sent to every participant.", "COMMIT"),
            ("Saga alt", "compensate", "Alternative", "Microservices often use sagas with compensations instead.", "events"),
        ),
    ),
    # ------------------------------------------------------------------ scale
    topic(
        "consensus-raft", "Consensus & Leader Election (Raft)", "scale", "advanced", "CR",
        "How replicated databases agree on one leader and one log despite failures.",
        "A committee that can only act when a majority is in the room. If the chair disappears, members vote a new chair; a chair who lost their majority cannot pass motions, even if they still think they are in charge.",
        "Consensus lets a group of nodes agree on a sequence of values even when some crash or the network partitions. Raft, the most widely taught algorithm, elects a leader with randomized election timeouts; a candidate needs votes from a majority in a new term. The leader appends client commands to its log and replicates them; an entry is committed once a majority has stored it, then every node applies committed entries in order to its state machine. Terms act as logical clocks, so a stale leader that rejoins sees a higher term and steps down, preventing split brain. With 2f + 1 nodes the cluster tolerates f failures, which is why clusters use 3 or 5 nodes. Raft and Paxos underpin etcd, Consul, CockroachDB, TiDB, YugabyteDB and MongoDB's replica set elections, while tools like Patroni use a consensus store (etcd) to elect a Postgres primary safely. Fencing (leases, STONITH, fencing tokens) ensures an old primary stops accepting writes.",
        [
            "Automatic primary failover for Postgres via Patroni and etcd.",
            "Distributed SQL databases replicating each range with Raft.",
            "Storing cluster metadata and locks (Kubernetes uses etcd).",
        ],
        [
            "Majority quorum: 3 nodes tolerate 1 failure, 5 tolerate 2; even counts add no tolerance.",
            "Committed = stored on a majority; only then applied and acknowledged.",
            "Terms and log matching ensure at most one effective leader per term.",
            "Leader leases allow fast local reads but depend on bounded clock drift.",
            "Cross-region clusters pay a round trip to a majority on every write.",
        ],
        [
            ex("Raft write path (pseudo)", "intermediate", "How a leader commits one entry.", "text", """
                client -> leader: SET x = 5
                leader: append (term=4, index=101, SET x=5) to local log
                leader -> followers: AppendEntries(term=4, prevIndex=100, entries=[101])
                followers: check prev entry matches, append, reply success
                leader: majority (2 of 3 incl. itself) stored index 101 -> commitIndex = 101
                leader: apply to state machine, reply OK to client
                followers: learn commitIndex=101 on next heartbeat, apply
            """, runnable=False),
            ex("Inspect a Raft cluster (etcd)", "intermediate", "See members, leader and term.", "bash", """
                etcdctl member list -w table
                etcdctl endpoint status --cluster -w table   # shows IS LEADER, RAFT TERM, RAFT INDEX
                etcdctl endpoint health --cluster
            """, runnable=False),
            ex("Patroni-managed Postgres failover", "advanced", "Leader key in etcd decides which Postgres node is primary.", "bash", """
                patronictl -c /etc/patroni.yml list            # Member, Role (Leader/Replica), State, Lag
                patronictl -c /etc/patroni.yml switchover --leader pg1 --candidate pg2
                # Patroni holds a TTL leader key in etcd; if pg1 cannot renew it, it demotes itself
                # and a replica with the least lag acquires the key and is promoted.
            """, runnable=False),
        ],
        ["cluster size = 2f + 1", "etcdctl endpoint status --cluster -w table", "patronictl list / switchover / failover", "Raft RPCs: RequestVote, AppendEntries", "fencing token: monotonically increasing lease id"],
        [
            "Two-node clusters cannot tolerate any failure safely; use 3 or a witness.",
            "Without fencing, an old primary that is merely slow can keep accepting writes (split brain).",
            "Spreading 3 nodes over 2 data centres means losing the bigger DC loses quorum.",
        ],
        [
            qa("intermediate", "Why do consensus clusters use an odd number of nodes?", "Progress needs a majority. 3 nodes tolerate 1 failure and 4 also tolerate only 1 (majority is 3), so the extra node adds cost and latency without extra fault tolerance."),
            qa("advanced", "How does Raft elect a leader?", "Followers that miss heartbeats for a randomized timeout become candidates, increment the term and request votes. Nodes vote once per term and only for candidates whose log is at least as up to date. A majority makes the candidate leader; randomized timeouts make split votes rare."),
            qa("advanced", "How does Raft prevent split brain?", "A leader needs a majority to commit, and two majorities always overlap. A stale leader in a minority partition cannot commit, and when it sees a higher term it steps down."),
            qa("advanced", "What is fencing and why is it needed for database failover?", "Fencing guarantees the old primary can no longer write after a new one is promoted, via STONITH, revoked leases or fencing tokens checked by storage. Without it, a paused but alive primary could resume and accept writes, diverging data."),
        ],
        ["replication-sharding", "distributed-transactions", "nosql-cap"],
        chain(
            ("Follower", "timeout", "Election timeout", "A follower stops hearing heartbeats and becomes a candidate."),
            ("Vote", "majority", "Request votes", "It increments the term and wins votes from a majority.", "term 5"),
            ("Leader", "accept writes", "Leader", "The leader appends client commands to its log.", "SET x"),
            ("Replicate", "AppendEntries", "Replicate", "Followers store the entry and acknowledge.", "entry"),
            ("Commit", "majority stored", "Commit", "Once a majority stores it, the entry is committed and applied.", "commit"),
        ),
    ),
    topic(
        "change-data-capture", "Change Data Capture (CDC)", "scale", "intermediate", "CD",
        "Stream every committed row change from the database log to other systems.",
        "Instead of photocopying the whole ledger every night to see what changed, you subscribe to the clerk's carbon copies: each new entry arrives in order, seconds after it is written.",
        "Change data capture turns database changes into an ordered stream of events. Log-based CDC reads the transaction log (Postgres logical decoding via replication slots, MySQL binlog in ROW format, SQL Server CDC, MongoDB change streams) and emits insert, update and delete events with before and after images, without touching application code or adding query load. Debezium with Kafka Connect is the common open-source stack; managed options include AWS DMS and Datastream. Consumers keep search indexes, caches, data warehouses and microservice read models in sync, and CDC is the standard relay for the transactional outbox. Alternatives such as polling an updated_at column miss deletes and intermediate states, and triggers add write overhead. Operational concerns include initial snapshots, schema evolution, ordering per key, at-least-once delivery (consumers must be idempotent) and replication slots that retain WAL if a consumer stops.",
        [
            "Keeping Elasticsearch/OpenSearch in sync with the primary database.",
            "Streaming OLTP changes into a data warehouse or lake.",
            "Invalidating caches when rows change.",
            "Relaying outbox events to Kafka.",
        ],
        [
            "Log-based CDC captures every committed change, including deletes, in commit order.",
            "Initial snapshot + streaming from a consistent log position avoids gaps.",
            "Events are at-least-once: make consumers idempotent (upsert by key + LSN/version).",
            "Monitor replication slot lag; an abandoned slot fills the disk with WAL.",
            "Order is guaranteed per partition key, not globally across Kafka partitions.",
        ],
        [
            ex("Polling-based CDC and its blind spot", "basic", "updated_at polling catches inserts and updates but not deletes.", "sql", """
                CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT, updated_at INTEGER NOT NULL);
                INSERT INTO items VALUES (1, 'a', 100), (2, 'b', 100), (3, 'c', 100);
                UPDATE items SET name = 'b2', updated_at = 200 WHERE id = 2;
                DELETE FROM items WHERE id = 3;
                SELECT * FROM items WHERE updated_at > 150;   -- sees id 2, never learns that id 3 is gone
            """),
            ex("Postgres logical decoding", "advanced", "Create a slot and peek at decoded changes.", "sql", """
                ALTER SYSTEM SET wal_level = logical;   -- requires restart
                SELECT pg_create_logical_replication_slot('cdc_demo', 'pgoutput');
                CREATE PUBLICATION shop_pub FOR TABLE orders, order_items;
                SELECT slot_name, active, pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS retained
                FROM pg_replication_slots;
            """, runnable=False),
            ex("Debezium connector config", "advanced", "Postgres source connector; credentials are injected from a secret provider.", "json", """
                {
                  "name": "shop-cdc",
                  "config": {
                    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
                    "database.hostname": "db.internal",
                    "database.dbname": "shop",
                    "database.user": "cdc_reader",
                    "database.password": "${secrets:shop/cdc:password}",
                    "database.sslmode": "verify-full",
                    "plugin.name": "pgoutput",
                    "slot.name": "debezium_shop",
                    "publication.name": "shop_pub",
                    "topic.prefix": "shop",
                    "snapshot.mode": "initial"
                  }
                }
            """, runnable=False),
        ],
        ["wal_level = logical", "pg_create_logical_replication_slot('s', 'pgoutput')", "CREATE PUBLICATION p FOR TABLE t", "MySQL: binlog_format = ROW, binlog_row_image = FULL", "SELECT * FROM pg_replication_slots"],
        [
            "An inactive replication slot retains WAL until the disk fills up.",
            "Schema changes can break downstream consumers without a schema registry.",
            "Large transactions arrive as large bursts and may need consumer backpressure.",
        ],
        [
            qa("basic", "What is change data capture?", "A technique for capturing inserts, updates and deletes from a database and delivering them as an ordered stream of events to other systems, usually by reading the transaction log."),
            qa("intermediate", "Log-based CDC vs polling vs triggers?", "Polling on updated_at is simple but misses deletes and intermediate updates and adds query load. Triggers capture everything but slow every write. Log-based CDC reads the existing log: complete, ordered, low overhead, but needs log access and operational care."),
            qa("advanced", "How do you bootstrap a new CDC consumer without gaps or duplicates?", "Take a consistent snapshot tied to a log position (LSN/binlog offset), load it, then stream changes from that exact position. Make the consumer idempotent so overlaps around the boundary are harmless."),
            qa("advanced", "What risks do Postgres replication slots introduce?", "A slot guarantees WAL is kept until the consumer confirms it. If the consumer stops, WAL accumulates and can fill the disk, taking down the primary. Monitor retained bytes and set max_slot_wal_keep_size."),
        ],
        ["wal-durability", "distributed-transactions", "caching-redis"],
        chain(
            ("Commit", "row change", "Write", "The application commits a change as usual."),
            ("Log", "WAL / binlog", "Logged", "The change is recorded in the transaction log.", "LSN"),
            ("Connector", "decode", "Decode", "A CDC connector reads and decodes the log via a slot.", "event"),
            ("Stream", "Kafka topic", "Publish", "Events are published per key, in commit order.", "before/after"),
            ("Consumers", "search, cache, DW", "Apply", "Consumers update search, caches and warehouses idempotently.", "upsert"),
        ),
    ),
    topic(
        "caching-redis", "Caching with Redis", "scale", "intermediate", "RC",
        "Cache-aside, write-through, TTLs, invalidation and stampede protection in front of a database.",
        "A small whiteboard next to the reception desk with the most-asked answers. It is much faster than walking to the archive, but someone has to erase answers when they become wrong.",
        "Redis is an in-memory data structure server (strings, hashes, lists, sets, sorted sets, streams) used as a cache, session store, rate limiter and lightweight queue. The most common pattern is cache-aside: read from Redis, on a miss read from the database and populate the cache with a TTL; on writes update the database and delete (not update) the cache key. Write-through writes to cache and database together; write-behind writes to the cache and flushes later, risking loss. The hard parts are invalidation, consistency and failure modes: stale data after races, cache stampedes when a hot key expires and thousands of requests hit the database at once, and cache penetration from repeated lookups of missing keys. Mitigations include TTL jitter, request coalescing or a short lock (SET key NX EX), probabilistic early refresh, negative caching and bounded memory with an eviction policy such as allkeys-lru. Redis persistence (RDB snapshots, AOF) and replication exist, but treat a cache as disposable unless it is explicitly your system of record.",
        [
            "Caching product pages and expensive aggregate queries.",
            "Session storage with expiry.",
            "Rate limiting with INCR + EXPIRE or sorted sets.",
            "Leaderboards with sorted sets.",
        ],
        [
            "Cache-aside: read-through on miss; on write, update DB then delete the key.",
            "Always set TTLs; add jitter to avoid synchronized expiry.",
            "Protect hot keys from stampedes with locks or early refresh.",
            "Choose maxmemory and an eviction policy deliberately.",
            "Version keys (product:42:v3) to invalidate groups cheaply.",
        ],
        [
            ex("Cache-aside in Python", "intermediate", "Read-through with TTL jitter and delete-on-write; connection details from the environment.", "python", """
                import json, os, random
                import redis

                r = redis.Redis.from_url(os.environ["REDIS_URL"], ssl_cert_reqs="required")  # rediss://

                def get_product(db, product_id):
                    key = f"product:{product_id}"
                    cached = r.get(key)
                    if cached is not None:
                        return json.loads(cached)
                    row = db.fetch_product(product_id)                     # cache miss -> database
                    r.set(key, json.dumps(row), ex=300 + random.randint(0, 60))
                    return row

                def update_price(db, product_id, price):
                    db.update_price(product_id, price)                     # source of truth first
                    r.delete(f"product:{product_id}")                      # then invalidate
            """, runnable=False),
            ex("Redis command cheat sheet", "basic", "Strings with TTL, counters, a stampede lock and a leaderboard.", "bash", """
                SET product:42 '{"name":"Keyboard","price":89}' EX 300
                GET product:42
                TTL product:42
                INCR ratelimit:user:7:202406011200 ; EXPIRE ratelimit:user:7:202406011200 60
                SET lock:product:42 1 NX EX 10           # only one request rebuilds the cache
                ZADD leaderboard 1500 asha 1320 ben
                ZREVRANGE leaderboard 0 9 WITHSCORES
            """, runnable=False),
            ex("Cache table emulation in SQL", "basic", "What cache-aside looks like with a key-value table and expiry timestamps.", "sql", """
                CREATE TABLE cache (k TEXT PRIMARY KEY, v TEXT NOT NULL, expires_at INTEGER NOT NULL);
                INSERT INTO cache VALUES ('product:1', (SELECT json_object('name', name, 'price', price) FROM products WHERE id = 1), 2000)
                ON CONFLICT (k) DO UPDATE SET v = excluded.v, expires_at = excluded.expires_at;
                SELECT v FROM cache WHERE k = 'product:1' AND expires_at > 1500;   -- hit
                SELECT v FROM cache WHERE k = 'product:1' AND expires_at > 2500;   -- expired -> miss
            """),
        ],
        ["SET k v EX 300 / GET k / DEL k", "SET lock:k 1 NX EX 10", "INCR + EXPIRE (rate limiting)", "ZADD / ZREVRANGE (leaderboards)", "maxmemory-policy allkeys-lru", "redis-cli --bigkeys / INFO memory"],
        [
            "Updating the cache on write (instead of deleting) races and leaves stale values.",
            "Keys without TTL accumulate until memory is exhausted.",
            "KEYS * in production blocks the single-threaded server; use SCAN.",
            "Caching failures (nulls) without short TTLs hides recovered data.",
        ],
        [
            qa("basic", "Explain the cache-aside pattern.", "The application checks the cache first; on a miss it reads the database and stores the result in the cache with a TTL. On writes it updates the database and invalidates the cache entry."),
            qa("intermediate", "Why delete the cache key on write instead of updating it?", "Two concurrent writers can update the database in one order and the cache in the other, leaving a stale value indefinitely. Deleting forces the next reader to load fresh data; a short TTL bounds any remaining race."),
            qa("advanced", "What is a cache stampede and how do you prevent it?", "When a hot key expires, many requests miss simultaneously and overload the database. Prevent with a rebuild lock (SET NX), request coalescing, serving stale while refreshing, probabilistic early expiration and TTL jitter."),
            qa("intermediate", "Cache penetration vs cache avalanche?", "Penetration: repeated requests for keys that do not exist bypass the cache every time; fix with negative caching or a Bloom filter. Avalanche: many keys expire at once or the cache goes down; fix with TTL jitter, redundancy and fallbacks with rate limiting."),
        ],
        ["key-value-stores", "change-data-capture", "connection-pooling"],
        chain(
            ("Request", "GET product 42", "Read", "The app needs product 42."),
            ("Redis", "GET key", "Cache lookup", "Check Redis first; a hit returns in microseconds.", "key"),
            ("Miss -> DB", "SELECT ...", "Cache miss", "On a miss, read the database (the source of truth).", "miss"),
            ("Populate", "SET EX 300", "Populate", "Store the result with a TTL plus jitter.", "row"),
            ("Invalidate", "DEL on write", "Invalidate", "Writes update the DB, then delete the key.", "DEL"),
        ),
    ),
    # ------------------------------------------------------------------ nosql
    topic(
        "key-value-stores", "Key-Value Stores & DynamoDB", "nosql", "intermediate", "KV",
        "Blazing-fast lookups by key, and single-table design for access-pattern-driven models.",
        "A coat check: you hand over a ticket number and instantly get your coat back. The attendant cannot answer 'show me all blue coats' without walking every hook.",
        "A key-value store maps an opaque key to a value and offers get, put and delete in O(1), often with TTLs and atomic counters. In-memory stores (Redis, Memcached) give microsecond latency; distributed durable stores (DynamoDB, Riak, etcd, FoundationDB) partition keys across nodes by hashing and replicate them. DynamoDB extends the model with a composite primary key: a partition key that decides placement and an optional sort key that orders items within a partition, so Query can fetch ranges such as all orders of a customer sorted by date. Single-table design stores multiple entity types in one table with prefixed keys (PK = CUSTOMER#1, SK = ORDER#2024-06-01#17) so each access pattern is one Query; global secondary indexes (eventually consistent) provide alternate access paths. Because there are no joins or ad-hoc queries, you design from access patterns first, and a hot partition key throttles regardless of total capacity.",
        [
            "Session and token storage with TTL.",
            "Shopping carts and user profiles keyed by user id.",
            "Serverless backends with predictable single-digit-ms latency (DynamoDB).",
            "Distributed configuration and coordination (etcd).",
        ],
        [
            "Design keys from access patterns; there are no joins or arbitrary filters.",
            "Partition key cardinality and uniform access prevent hot partitions.",
            "Sort keys enable range queries and hierarchical prefixes (begins_with).",
            "GSIs are eventually consistent and cost extra writes.",
            "Conditional writes (attribute_not_exists, version checks) provide optimistic concurrency.",
        ],
        [
            ex("Single-table design emulated in SQL", "intermediate", "PK/SK items for customers and orders; each access pattern is a key-range query.", "sql", """
                CREATE TABLE app (pk TEXT NOT NULL, sk TEXT NOT NULL, data TEXT, PRIMARY KEY (pk, sk));
                INSERT INTO app VALUES
                  ('CUSTOMER#1', 'PROFILE', '{"name":"Asha Rao"}'),
                  ('CUSTOMER#1', 'ORDER#2024-06-01#1', '{"status":"shipped"}'),
                  ('CUSTOMER#1', 'ORDER#2024-06-20#2', '{"status":"paid"}'),
                  ('CUSTOMER#2', 'PROFILE', '{"name":"Ben Carter"}'),
                  ('CUSTOMER#2', 'ORDER#2024-06-03#3', '{"status":"shipped"}');
                -- "orders of customer 1, newest first" = Query PK = CUSTOMER#1 AND begins_with(SK, 'ORDER#')
                SELECT sk, data FROM app WHERE pk = 'CUSTOMER#1' AND sk >= 'ORDER#' AND sk < 'ORDER$' ORDER BY sk DESC;
                EXPLAIN QUERY PLAN SELECT sk FROM app WHERE pk = 'CUSTOMER#1' AND sk >= 'ORDER#' AND sk < 'ORDER$';
            """),
            ex("DynamoDB query and conditional write", "advanced", "AWS CLI: range query on the sort key and an insert that fails if the item exists.", "bash", """
                aws dynamodb query --table-name app \\
                  --key-condition-expression "pk = :pk AND begins_with(sk, :prefix)" \\
                  --expression-attribute-values '{":pk":{"S":"CUSTOMER#1"},":prefix":{"S":"ORDER#"}}' \\
                  --scan-index-forward false

                aws dynamodb put-item --table-name app \\
                  --item '{"pk":{"S":"IDEMPOTENCY#req-7f3a"},"sk":{"S":"META"}}' \\
                  --condition-expression "attribute_not_exists(pk)"
            """, runnable=False),
        ],
        ["Redis: SET/GET/DEL key, EXPIRE", "DynamoDB: GetItem, PutItem, Query (PK + SK condition), Scan (avoid)", "begins_with(sk, 'ORDER#')", "ConditionExpression: attribute_not_exists(pk)", "GSI: alternate PK/SK, eventually consistent"],
        [
            "Scan reads the whole table and is slow and expensive; design for Query.",
            "A low-cardinality partition key (status, date) creates hot partitions.",
            "Item size limits (400 KB in DynamoDB) force splitting large documents.",
        ],
        [
            qa("basic", "What is a key-value store good and bad at?", "Good: very fast get/put by key, simple horizontal scaling, TTLs. Bad: queries by value, joins, ad-hoc analytics and multi-key constraints."),
            qa("intermediate", "Partition key vs sort key in DynamoDB?", "The partition key is hashed to choose the storage partition; all items with the same partition key live together. The sort key orders items within that partition, enabling range queries, prefixes and one-to-many relationships."),
            qa("advanced", "What is single-table design and why use it?", "Storing several entity types in one table with overloaded, prefixed keys so related items share a partition and each access pattern is a single Query. It replaces joins with pre-arranged data locality, at the cost of upfront access-pattern design."),
            qa("advanced", "How do you deal with a hot partition?", "Increase key cardinality (write sharding with a suffix, e.g. COUNTER#0..9 then sum), cache hot reads, spread time-based keys, and reconsider the access pattern; adaptive capacity helps but does not remove per-partition limits."),
        ],
        ["nosql-cap", "caching-redis", "document-databases"],
        chain(
            ("Request", "PK + SK", "Request", "The client asks for a key or key range."),
            ("Hash", "hash(PK)", "Locate partition", "The partition key is hashed to find the owning partition.", "hash"),
            ("Partition", "items by SK", "Partition", "Items inside are sorted by sort key.", "PK"),
            ("Range", "begins_with SK", "Range read", "Query reads a contiguous sort-key range.", "SK range"),
            ("Result", "items", "Return", "Latency stays flat regardless of table size.", "items"),
        ),
    ),
    topic(
        "document-databases", "Document Databases (MongoDB)", "nosql", "intermediate", "DD",
        "JSON-like documents, embedding vs referencing, indexes and the aggregation pipeline.",
        "A patient folder: everything about one patient (visits, prescriptions, notes) is in one folder you can pull out in one go. Great for treating that patient, awkward for 'list every prescription of drug X across all patients'.",
        "Document databases store self-contained documents (BSON in MongoDB, JSON in Couchbase or Firestore) grouped into collections, with flexible schemas per document. The central modelling choice is embedding related data inside the parent (one read, atomic single-document updates) versus referencing it by id (no duplication, unbounded growth handled, but requires extra queries or $lookup). Embed when data is read together and bounded (order with its line items); reference when it is shared, large or unbounded (comments on a viral post). MongoDB supports secondary, compound, multikey (array), text, geospatial and TTL indexes, and the aggregation pipeline ($match, $group, $lookup, $unwind, $project) for transformations. It offers multi-document ACID transactions since 4.0, replica sets with automatic elections, and sharding by a shard key. Write concern (w: majority) and read concern control durability and consistency, and schema validation with $jsonSchema reins in schema drift.",
        [
            "Product catalogues with varied attributes per category.",
            "Content management and user profiles read as whole objects.",
            "Event or IoT payloads with evolving shapes.",
        ],
        [
            "Model for your queries: embed what is read together, reference what grows unbounded.",
            "Single-document writes are atomic; multi-document transactions cost more.",
            "Compound index order follows the ESR rule: Equality, Sort, Range.",
            "Use write concern majority for durable writes that survive failover.",
            "Document size limit is 16 MB; unbounded arrays are an anti-pattern.",
        ],
        [
            ex("Embedding and querying", "intermediate", "An order document embeds its items; query and index nested fields.", "javascript", """
                db.orders.insertOne({
                  _id: 17, customerId: 7, status: "shipped", createdAt: ISODate("2024-07-06"),
                  items: [ { sku: "NC-HP", name: "Noise-cancelling Headphones", qty: 1, price: 199 } ]
                });
                db.orders.createIndex({ customerId: 1, createdAt: -1 });     // equality, then sort
                db.orders.find({ customerId: 7 }).sort({ createdAt: -1 }).limit(10);
                db.orders.find({ "items.sku": "NC-HP" });                      // multikey index candidate
            """, runnable=False),
            ex("Aggregation pipeline", "advanced", "Revenue per category across embedded line items.", "javascript", """
                db.orders.aggregate([
                  { $match: { status: { $ne: "cancelled" } } },
                  { $unwind: "$items" },
                  { $lookup: { from: "products", localField: "items.sku", foreignField: "sku", as: "p" } },
                  { $unwind: "$p" },
                  { $group: { _id: "$p.category", revenue: { $sum: { $multiply: ["$items.qty", "$items.price"] } } } },
                  { $sort: { revenue: -1 } }
                ]);
            """, runnable=False),
            ex("Same shape in SQL with JSON", "basic", "Build order documents from relational tables to compare the models.", "sql", """
                SELECT json_object(
                         'order_id', o.id, 'status', o.status,
                         'items', json_group_array(json_object('product', p.name, 'qty', i.qty, 'price', i.unit_price))
                       ) AS order_doc
                FROM orders o
                JOIN order_items i ON i.order_id = o.id
                JOIN products p ON p.id = i.product_id
                WHERE o.id IN (1, 3)
                GROUP BY o.id;
            """),
        ],
        ["db.c.find({ field: value }).sort({ f: -1 }).limit(n)", "db.c.createIndex({ a: 1, b: -1 })", "db.c.aggregate([{ $match }, { $group }, { $lookup }])", "writeConcern: { w: 'majority' }", "db.c.explain('executionStats').find(...)"],
        [
            "Unbounded embedded arrays grow documents past limits and slow updates.",
            "Missing indexes cause collection scans that look fine in development.",
            "Schemaless does not mean no schema: drift makes queries and migrations painful.",
        ],
        [
            qa("intermediate", "Embed or reference in MongoDB?", "Embed data read together with the parent and bounded in size (order items, addresses) for single-read, atomic access. Reference data that is shared across documents, large or unbounded (users, comments) to avoid duplication and huge documents."),
            qa("intermediate", "Does MongoDB support transactions?", "Single-document operations are always atomic. Since 4.0 (replica sets) and 4.2 (sharded clusters) it supports multi-document ACID transactions, with more overhead and time limits, so models still favour single-document atomicity."),
            qa("advanced", "What is the ESR rule for compound indexes?", "Order index fields as Equality first, then Sort, then Range. This lets the index narrow by equality, return results already sorted, and then bound the range, avoiding in-memory sorts."),
            qa("advanced", "What do write concern and read concern control?", "Write concern sets how many replica acknowledgements are required before success (w: 1 vs w: majority, plus journaling). Read concern sets the consistency of data read (local, majority, linearizable). Majority/majority avoids reading data that could be rolled back after failover."),
        ],
        ["nosql-cap", "json-in-sql", "key-value-stores"],
        chain(
            ("Entity", "order + items", "Model", "Decide what is read together: an order and its items."),
            ("Document", "embed items", "Embed", "Items are embedded in the order document.", "BSON"),
            ("Index", "customerId, date", "Index", "Compound indexes follow Equality, Sort, Range.", "index"),
            ("Query", "find / aggregate", "Query", "find() for lookups, the pipeline for transformations.", "query"),
            ("Replicate", "w: majority", "Durability", "Writes acknowledged by a majority survive failover.", "ack"),
        ),
    ),
    topic(
        "wide-column-cassandra", "Wide-Column Stores (Cassandra)", "nosql", "advanced", "WC",
        "Partitioned, sorted rows built for massive write throughput and query-first modelling.",
        "A post office with sorting bins per postcode. Each bin (partition) lives with specific clerks, and letters inside are kept in date order, so 'latest mail for postcode X' is instant, but 'all letters from sender Y' means visiting every bin.",
        "Wide-column stores such as Cassandra, ScyllaDB, HBase and Bigtable organize data into tables whose primary key has a partition key and clustering columns. The partition key is hashed onto a token ring to decide which nodes own the data; clustering columns sort rows within the partition on disk, so range reads inside one partition are sequential and fast. Writes go to a commit log and an in-memory memtable, later flushed to immutable SSTables and merged by compaction (an LSM-tree), which makes writes extremely cheap; deletes write tombstones that are purged after gc_grace_seconds. Cassandra is leaderless: any node coordinates a request, and tunable consistency (ONE, QUORUM, LOCAL_QUORUM, ALL) with replication factor N gives strong reads when R + W > N. Modelling is query-first: one table per access pattern, data duplicated across tables, no joins, and partitions kept bounded (for example by bucketing time).",
        [
            "Time-series and event logs at very high write rates.",
            "Messaging inboxes and activity feeds partitioned by user.",
            "IoT telemetry across many regions with local writes.",
        ],
        [
            "Primary key = ((partition key), clustering columns); queries must specify the partition key.",
            "One table per query; denormalize and write to several tables.",
            "Keep partitions bounded (e.g. < 100 MB): bucket by day or month.",
            "QUORUM writes + QUORUM reads with RF=3 give read-your-writes.",
            "Tombstones from heavy deletes or TTLs slow reads; design to avoid them.",
        ],
        [
            ex("Query-first table design (CQL)", "advanced", "Latest readings of a sensor per day bucket, newest first.", "sql", """
                CREATE TABLE readings_by_sensor_day (
                  sensor_id uuid,
                  day date,
                  ts timestamp,
                  value double,
                  PRIMARY KEY ((sensor_id, day), ts)
                ) WITH CLUSTERING ORDER BY (ts DESC)
                  AND default_time_to_live = 2592000;

                SELECT ts, value FROM readings_by_sensor_day
                WHERE sensor_id = 5b6962dd-3f90-4c93-8f61-eabfa4a803e2 AND day = '2024-06-01'
                LIMIT 100;
                CONSISTENCY LOCAL_QUORUM;
            """, runnable=False),
            ex("Partition and clustering emulated in SQLite", "intermediate", "A composite key (partition, clustering) makes per-partition range reads one index range.", "sql", """
                CREATE TABLE events_by_user_day (
                  user_id INTEGER, day INTEGER, ts INTEGER, kind TEXT,
                  PRIMARY KEY (user_id, day, ts)
                ) WITHOUT ROWID;
                INSERT INTO events_by_user_day
                  SELECT user_id, ts / 86400, ts, kind FROM events WHERE user_id IN (7, 42);
                SELECT ts, kind FROM events_by_user_day
                WHERE user_id = 42 AND day = 19677 ORDER BY ts DESC LIMIT 5;
                EXPLAIN QUERY PLAN SELECT ts FROM events_by_user_day WHERE user_id = 42 AND day = 19677 ORDER BY ts DESC;
            """),
        ],
        ["PRIMARY KEY ((partition_cols), clustering_cols)", "WITH CLUSTERING ORDER BY (ts DESC)", "CONSISTENCY QUORUM | LOCAL_QUORUM | ONE", "nodetool status / tablestats / compactionstats", "default_time_to_live, gc_grace_seconds"],
        [
            "ALLOW FILTERING scans many partitions and does not scale.",
            "Unbounded partitions (all events of a user forever) become hot and huge.",
            "Secondary indexes and materialized views in Cassandra have sharp edges; prefer extra tables.",
        ],
        [
            qa("intermediate", "Partition key vs clustering column in Cassandra?", "The partition key is hashed to choose the replica nodes and groups rows together; clustering columns sort rows within the partition on disk. Queries must provide the partition key and can range over clustering columns."),
            qa("advanced", "Why are writes so fast in Cassandra?", "It uses an LSM-tree: writes append to a commit log and an in-memory memtable, then flush to immutable SSTables sequentially. No read-before-write or in-place updates; compaction merges files in the background."),
            qa("advanced", "Explain tunable consistency.", "With replication factor N, each request specifies how many replicas must respond (ONE, QUORUM, ALL). If write replicas W plus read replicas R exceed N, every read overlaps the latest write; lower levels trade consistency for latency and availability."),
            qa("advanced", "What are tombstones and why do they hurt?", "Deletes and expired TTLs are written as tombstone markers, because SSTables are immutable. Reads must skip them until compaction purges them after gc_grace_seconds; many tombstones in a partition slow reads or cause query failures."),
        ],
        ["nosql-cap", "time-series-databases", "replication-sharding"],
        chain(
            ("Write", "any coordinator", "Coordinator", "Any node can coordinate a request."),
            ("Token ring", "hash(partition)", "Replica placement", "The partition key's token picks RF replicas.", "token"),
            ("Commit log", "+ memtable", "Write path", "Each replica appends to its commit log and memtable.", "write"),
            ("SSTable", "flush, compact", "Flush", "Memtables flush to immutable SSTables; compaction merges.", "flush"),
            ("Quorum", "R + W > N", "Consistency", "QUORUM reads and writes overlap for strong reads.", "ack"),
        ),
    ),
    topic(
        "graph-databases", "Graph Databases", "nosql", "intermediate", "GR",
        "Nodes and relationships as first-class data, traversed with Cypher or Gremlin.",
        "A detective's corkboard with photos connected by red string. Asking 'who is three strings away from the suspect?' is natural on the board and painful with a stack of index cards.",
        "Graph databases model data as nodes (entities) with labels and properties, connected by typed, directed relationships that can also carry properties (the labelled property graph model, used by Neo4j, Memgraph and Amazon Neptune). Native graph engines use index-free adjacency: each node points directly to its relationships, so traversal cost depends on the size of the neighbourhood visited rather than on the total size of the graph. That makes multi-hop questions (friends of friends, shortest paths, fraud rings, dependency chains) fast where SQL would need repeated self-joins or recursive CTEs. Query languages include Cypher/openCypher and the new ISO GQL standard (pattern matching with ASCII-art syntax like (a)-[:FOLLOWS]->(b)), Gremlin (traversal steps) and SPARQL for RDF triple stores. Graph algorithms such as PageRank, community detection and centrality support recommendations and fraud analytics. Graphs are less suited to bulk aggregations over all records and are harder to shard because relationships cross partitions.",
        [
            "Social networks: mutual friends and recommendations.",
            "Fraud detection: rings of accounts sharing devices or cards.",
            "Knowledge graphs and dependency/impact analysis.",
            "Network and IT topology: what breaks if this router fails?",
        ],
        [
            "Relationships are stored, not computed at query time via joins.",
            "Traversal cost scales with the visited subgraph, not total data size.",
            "Bound variable-length patterns (*1..3) to avoid explosive traversals.",
            "Index node properties used as traversal entry points.",
            "Supernodes (millions of edges) need special handling.",
        ],
        [
            ex("Cypher patterns", "intermediate", "Create a small graph, then find friends-of-friends recommendations.", "text", """
                CREATE (a:Person {name:'Asha'}), (b:Person {name:'Ben'}), (c:Person {name:'Chen'}), (d:Person {name:'Diya'}),
                       (a)-[:FOLLOWS]->(b), (b)-[:FOLLOWS]->(c), (b)-[:FOLLOWS]->(d), (a)-[:FOLLOWS]->(d);

                MATCH (me:Person {name:'Asha'})-[:FOLLOWS]->(:Person)-[:FOLLOWS]->(rec:Person)
                WHERE NOT (me)-[:FOLLOWS]->(rec) AND rec <> me
                RETURN rec.name, count(*) AS via ORDER BY via DESC;

                MATCH p = shortestPath((:Person {name:'Asha'})-[:FOLLOWS*..5]->(:Person {name:'Chen'}))
                RETURN [n IN nodes(p) | n.name];
            """, runnable=False),
            ex("Graph traversal with a recursive CTE", "advanced", "The same multi-hop question in SQL: who is reachable within 2 hops of Asha?", "sql", """
                CREATE TABLE follows (src TEXT, dst TEXT, PRIMARY KEY (src, dst));
                INSERT INTO follows VALUES ('Asha','Ben'),('Ben','Chen'),('Ben','Diya'),('Asha','Diya'),('Diya','Eli'),('Eli','Asha');
                WITH RECURSIVE reach(person, hops, path) AS (
                  SELECT 'Asha', 0, 'Asha'
                  UNION ALL
                  SELECT f.dst, r.hops + 1, r.path || '>' || f.dst
                  FROM reach r JOIN follows f ON f.src = r.person
                  WHERE r.hops < 2 AND instr(r.path, f.dst) = 0
                )
                SELECT person, MIN(hops) AS hops FROM reach WHERE person <> 'Asha' GROUP BY person ORDER BY hops, person;
            """),
        ],
        ["MATCH (a:Label {k:v})-[:REL]->(b) RETURN b", "MATCH (a)-[:REL*1..3]->(b)", "shortestPath((a)-[*..5]-(b))", "CREATE INDEX FOR (p:Person) ON (p.email)", "Gremlin: g.V().has('name','Asha').out('follows').out('follows')"],
        [
            "Unbounded variable-length patterns can explore millions of paths.",
            "Supernodes (celebrities, a 'country' node) make traversals through them expensive.",
            "Using a graph DB for simple tabular reporting adds complexity for no gain.",
        ],
        [
            qa("basic", "When is a graph database a good fit?", "When the questions are about relationships and paths of variable depth: social recommendations, fraud rings, network dependencies, knowledge graphs. If you mostly aggregate rows, a relational or columnar store fits better."),
            qa("intermediate", "What is index-free adjacency?", "Each node stores direct references to its relationships, so following an edge is a pointer hop rather than an index lookup or join. Traversal cost depends on the neighbourhood size, not the total graph size."),
            qa("intermediate", "Why are multi-hop queries hard in SQL?", "Each hop is another self-join on an edge table, and variable depth needs recursive CTEs. Intermediate results can explode and the planner has limited ways to prune paths, whereas graph engines traverse adjacency directly."),
            qa("advanced", "What is a supernode and how do you handle it?", "A node with a huge number of relationships (a celebrity). Traversals through it touch millions of edges. Mitigate with relationship-type or property filters, splitting the node (by time or category), or excluding it from certain traversals."),
        ],
        ["ctes-recursive", "nosql-cap", "vector-databases"],
        chain(
            ("Start", "Asha", "Entry point", "Find the start node via an index on name."),
            ("Hop 1", "FOLLOWS -> Ben", "First hop", "Follow outgoing FOLLOWS relationships directly.", "edge"),
            ("Hop 2", "Ben -> Chen, Diya", "Second hop", "Each hop is a pointer chase, not a join.", "edge"),
            ("Filter", "not followed yet", "Filter", "Exclude people Asha already follows.", "filter"),
            ("Rank", "count paths", "Recommend", "Rank candidates by the number of connecting paths.", "recs"),
        ),
    ),
    topic(
        "time-series-databases", "Time-Series Databases", "nosql", "intermediate", "TS",
        "Append-heavy timestamped data: partition by time, downsample, compress and expire.",
        "A weather station's logbook: one line every minute, forever. Nobody edits old lines; people ask for averages per hour, and after a year the minute-by-minute pages are summarized and archived.",
        "Time-series data is a stream of timestamped measurements identified by a metric and tags (host, region, sensor). Workloads are append-mostly, read in time ranges, aggregated into buckets, and expire after a retention period. Time-series databases optimize for this: TimescaleDB adds hypertables (automatic time partitioning), compression and continuous aggregates on Postgres; InfluxDB and Prometheus use custom storage with series indexes; ClickHouse and QuestDB use columnar storage that compresses timestamps with delta-of-delta encoding and values with Gorilla-style XOR encoding. Core techniques are time partitioning (drop old chunks for retention), downsampling (keep raw data for days and rollups for years), and continuous aggregates that pre-compute buckets incrementally. High cardinality, meaning too many unique tag combinations such as per-request ids as labels, is the classic failure mode that explodes memory and index size.",
        [
            "Infrastructure and application metrics (Prometheus, InfluxDB).",
            "IoT sensor telemetry.",
            "Financial tick data and trading analytics.",
        ],
        [
            "Partition by time; retention = dropping whole chunks.",
            "Downsample: raw for days, 1-minute rollups for months, hourly for years.",
            "Keep tag cardinality bounded; never use user or request ids as labels.",
            "Columnar compression (delta-of-delta, XOR) gives 10x+ savings.",
            "Late-arriving data must be handled by rollup refresh windows.",
        ],
        [
            ex("Time bucketing and downsampling", "intermediate", "Events per hour bucket and kind, as a rollup table.", "sql", """
                CREATE TABLE events_hourly AS
                SELECT (ts / 3600) * 3600 AS bucket, kind, COUNT(*) AS n
                FROM events GROUP BY bucket, kind;
                SELECT datetime(bucket, 'unixepoch') AS hour, kind, n
                FROM events_hourly ORDER BY bucket, kind LIMIT 8;
                SELECT COUNT(*) AS raw_rows, (SELECT COUNT(*) FROM events_hourly) AS rollup_rows FROM events;
            """),
            ex("Rate of change with LAG", "advanced", "Per-bucket counts and the change from the previous bucket.", "sql", """
                WITH b AS (
                  SELECT (ts / 3600) * 3600 AS bucket, COUNT(*) AS n FROM events WHERE kind = 'buy' GROUP BY bucket
                )
                SELECT datetime(bucket, 'unixepoch') AS hour, n, n - LAG(n) OVER (ORDER BY bucket) AS delta
                FROM b ORDER BY bucket LIMIT 8;
            """),
            ex("TimescaleDB hypertable with continuous aggregate", "advanced", "Automatic partitioning, rollups, compression and retention.", "sql", """
                CREATE TABLE metrics (ts timestamptz NOT NULL, host text, cpu double precision);
                SELECT create_hypertable('metrics', 'ts', chunk_time_interval => interval '1 day');
                CREATE MATERIALIZED VIEW metrics_5m WITH (timescaledb.continuous) AS
                  SELECT time_bucket('5 minutes', ts) AS bucket, host, avg(cpu) AS cpu
                  FROM metrics GROUP BY bucket, host;
                SELECT add_continuous_aggregate_policy('metrics_5m', start_offset => interval '1 hour',
                       end_offset => interval '5 minutes', schedule_interval => interval '5 minutes');
                ALTER TABLE metrics SET (timescaledb.compress, timescaledb.compress_segmentby = 'host');
                SELECT add_compression_policy('metrics', interval '7 days');
                SELECT add_retention_policy('metrics', interval '90 days');
            """, runnable=False),
        ],
        ["time_bucket('5 minutes', ts) (TimescaleDB)", "PromQL: rate(http_requests_total[5m])", "InfluxDB: from(bucket) |> range(start: -1h) |> aggregateWindow(every: 1m, fn: mean)", "add_retention_policy('t', interval '90 days')", "ClickHouse: PARTITION BY toYYYYMM(ts) TTL ts + INTERVAL 90 DAY"],
        [
            "High-cardinality labels (user_id, request_id) blow up memory and index size.",
            "Querying raw data over long ranges instead of rollups is slow and expensive.",
            "Clock skew across producers leads to out-of-order or future timestamps.",
        ],
        [
            qa("basic", "What makes time-series workloads different?", "Mostly appends in time order, rare updates, queries over time ranges with aggregation into buckets, and retention-based deletion. Storage and indexing can be specialized around those properties."),
            qa("intermediate", "What is downsampling and why do it?", "Aggregating raw high-resolution points into coarser buckets (1-minute, 1-hour averages, min, max) and keeping those longer than raw data. It cuts storage and makes long-range queries fast."),
            qa("advanced", "What is the cardinality problem in time-series databases?", "Each unique combination of metric and tag values is a separate series with its own index entry and buffers. Unbounded tags such as user ids create millions of series, exhausting memory and slowing queries."),
            qa("advanced", "How do continuous aggregates handle late data?", "They refresh a sliding window (for example the last hour) on a schedule, recomputing buckets that may have received late points, while older buckets are treated as final. Data arriving after the window needs a manual refresh."),
        ],
        ["partitioning", "oltp-olap-columnar", "index-types"],
        chain(
            ("Ingest", "points + tags", "Append", "Points arrive mostly in time order."),
            ("Chunk", "by time", "Partition", "Data lands in the current time chunk.", "point"),
            ("Compress", "columnar", "Compress", "Older chunks are compressed column by column.", "chunk"),
            ("Rollup", "5m / 1h", "Downsample", "Continuous aggregates pre-compute buckets.", "buckets"),
            ("Expire", "drop chunk", "Retention", "Chunks past retention are dropped whole.", "drop"),
        ),
    ),
    topic(
        "vector-databases", "Vector Databases & Similarity Search", "nosql", "advanced", "VD",
        "Store embeddings and find nearest neighbours fast with ANN indexes like HNSW and IVF.",
        "A music shop arranged by sound instead of alphabet: similar-sounding albums sit next to each other, so 'more like this' means looking at the neighbouring shelves rather than reading every label.",
        "Embedding models turn text, images or audio into high-dimensional vectors where semantic similarity becomes geometric closeness, measured by cosine similarity, dot product or Euclidean (L2) distance. A vector database stores these vectors with metadata and answers k-nearest-neighbour queries. Exact search compares the query with every vector, which is too slow at millions of rows, so approximate nearest neighbour (ANN) indexes trade a little recall for orders-of-magnitude speed: HNSW builds a multi-layer proximity graph navigated greedily, IVF clusters vectors and probes only the closest clusters, and product quantization compresses vectors to save memory. Options range from extensions (pgvector in Postgres, sqlite-vec) to dedicated systems (Milvus, Qdrant, Weaviate, Pinecone) and search engines (OpenSearch, Elasticsearch). Real systems combine vector similarity with metadata filters (tenant, language, date) and keyword search (hybrid search with BM25), which is the retrieval step of retrieval-augmented generation (RAG). Tuning parameters (HNSW m and ef_search, IVF lists and probes) balance recall, latency and memory.",
        [
            "Semantic search over documentation or support tickets.",
            "Retrieval-augmented generation for LLM applications.",
            "Recommendations: similar products, images or songs.",
            "Deduplication and near-duplicate detection.",
        ],
        [
            "Use the distance metric the embedding model was trained for (often cosine).",
            "ANN indexes trade recall for speed; measure recall against exact search.",
            "HNSW: fast, high recall, memory hungry; IVF: cheaper build, needs good clustering.",
            "Filtered search can wreck recall if filters are applied after ANN; use pre-filtering support.",
            "Re-embed everything when you change the embedding model; versions are not comparable.",
        ],
        [
            ex("pgvector with an HNSW index", "advanced", "Store embeddings and run filtered nearest-neighbour queries.", "sql", """
                CREATE EXTENSION IF NOT EXISTS vector;
                CREATE TABLE doc_chunks (
                  id bigserial PRIMARY KEY, tenant_id bigint NOT NULL, content text NOT NULL,
                  embedding vector(768) NOT NULL
                );
                CREATE INDEX ON doc_chunks USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
                SET hnsw.ef_search = 80;
                SELECT id, content, 1 - (embedding <=> $1) AS similarity
                FROM doc_chunks
                WHERE tenant_id = $2
                ORDER BY embedding <=> $1          -- cosine distance
                LIMIT 5;
            """, runnable=False),
            ex("Exact cosine similarity by brute force", "intermediate", "Tiny 3-dimensional vectors stored as JSON; similarity computed for every row (what ANN avoids at scale).", "sql", """
                CREATE TABLE vecs (id INTEGER PRIMARY KEY, label TEXT, x REAL, y REAL, z REAL);
                INSERT INTO vecs VALUES (1,'keyboard',0.9,0.1,0.0),(2,'mouse',0.8,0.3,0.1),(3,'novel',0.0,0.2,0.9),(4,'headphones',0.7,0.6,0.1);
                WITH q(x, y, z) AS (SELECT 0.85, 0.2, 0.05)
                SELECT v.label,
                       ROUND((v.x*q.x + v.y*q.y + v.z*q.z) /
                             (sqrt(v.x*v.x + v.y*v.y + v.z*v.z) * sqrt(q.x*q.x + q.y*q.y + q.z*q.z)), 4) AS cosine
                FROM vecs v, q ORDER BY cosine DESC;
            """),
            ex("Embedding and querying in Python", "intermediate", "Index documents and query by meaning; the API key comes from the environment.", "python", """
                import os
                import numpy as np

                def embed(texts):
                    # call your embedding provider here; credentials via os.environ["EMBEDDINGS_API_KEY"]
                    raise NotImplementedError

                docs = ["Reset your password from settings", "Invoices are emailed monthly", "Enable 2FA with an authenticator app"]
                matrix = np.array(embed(docs))
                matrix /= np.linalg.norm(matrix, axis=1, keepdims=True)      # normalise for cosine

                def search(query, k=2):
                    q = np.array(embed([query])[0]); q /= np.linalg.norm(q)
                    scores = matrix @ q
                    return [docs[i] for i in np.argsort(-scores)[:k]]
            """, runnable=False),
        ],
        ["pgvector: embedding <=> q (cosine), <-> (L2), <#> (neg. inner product)", "CREATE INDEX ... USING hnsw (embedding vector_cosine_ops)", "CREATE INDEX ... USING ivfflat (embedding vector_l2_ops) WITH (lists = 1000)", "SET hnsw.ef_search = 100 / SET ivfflat.probes = 10", "hybrid: BM25 score + vector score (reciprocal rank fusion)"],
        [
            "Mixing vectors from different embedding models or versions gives meaningless distances.",
            "Post-filtering ANN results by tenant can return fewer than k results.",
            "HNSW indexes must fit in memory for good latency; plan RAM accordingly.",
        ],
        [
            qa("basic", "What is a vector embedding?", "A fixed-length array of numbers produced by a model so that semantically similar inputs map to nearby points. Distances such as cosine similarity then measure semantic similarity."),
            qa("intermediate", "Why use approximate nearest neighbour search?", "Exact k-NN compares the query against every vector, which is linear in data size and too slow at millions of high-dimensional vectors. ANN indexes like HNSW or IVF visit a small fraction of vectors and return nearly the same results much faster."),
            qa("advanced", "How does HNSW work?", "It builds a hierarchy of proximity graphs: sparse upper layers for long jumps and a dense bottom layer with all vectors. Search starts at the top, greedily moves to closer neighbours, descends layer by layer and keeps a candidate list of size ef_search at the bottom."),
            qa("advanced", "How do you combine metadata filters with vector search?", "Use engines that support filtered ANN (pre-filtering or filter-aware traversal), partition indexes by high-selectivity keys such as tenant, or over-fetch then post-filter. Pure post-filtering can drop recall when the filter is selective."),
            qa("intermediate", "What is hybrid search?", "Combining lexical relevance (BM25 over keywords) with vector similarity, usually by fusing the two rankings (for example reciprocal rank fusion). It handles exact terms like product codes that embeddings miss and semantic matches that keywords miss."),
        ],
        ["index-types", "json-in-sql", "graph-databases"],
        chain(
            ("Content", "text, images", "Input", "Documents are split into chunks."),
            ("Embed", "model -> vector", "Embed", "An embedding model maps each chunk to a vector.", "text"),
            ("Index", "HNSW / IVF", "ANN index", "Vectors go into an approximate nearest neighbour index.", "vector"),
            ("Query", "embed question", "Query", "The question is embedded with the same model.", "q"),
            ("Top-k", "+ filters", "Retrieve", "The index returns the k closest chunks (filtered by tenant).", "k"),
        ),
    ),
    # ------------------------------------------------------------------ design
    topic(
        "star-schema", "Denormalization & Star Schema", "design", "intermediate", "SS",
        "Fact and dimension tables for analytics, slowly changing dimensions and deliberate redundancy.",
        "A sales ledger (facts: what was sold, how many, for how much) with reference binders for products, stores and calendar dates (dimensions). Analysts flip through the binders to slice the ledger any way they like.",
        "Analytical workloads read huge numbers of rows and aggregate them by many attributes, so they favour a dimensional model over a normalized OLTP schema. A star schema has a central fact table holding measures (quantity, revenue) and foreign keys at a declared grain (one row per order line), surrounded by denormalized dimension tables (product, customer, date, store) with descriptive attributes used for filtering and grouping. A snowflake schema normalizes dimensions into sub-tables, saving space but adding joins. Dimensions change over time, handled by slowly changing dimension (SCD) techniques: Type 1 overwrites, Type 2 adds a new row with validity dates and a surrogate key so history is preserved, Type 3 keeps a previous-value column. A date dimension with precomputed attributes (weekday, fiscal quarter, holiday) simplifies time analysis. Denormalization in OLTP (counters, cached totals, read models) follows the same principle of paying at write time to make reads cheap, but needs a single owner that keeps copies in sync.",
        [
            "A sales data mart in a warehouse such as BigQuery, Snowflake or Redshift.",
            "Tracking customer attribute history with SCD Type 2.",
            "Dashboard read models maintained from OLTP via CDC.",
        ],
        [
            "Declare the grain of the fact table first (one row per what?).",
            "Facts are narrow and long; dimensions are wide and short.",
            "SCD Type 2: surrogate key, valid_from, valid_to, is_current.",
            "Conformed dimensions are shared across fact tables for consistent reporting.",
            "Additive measures (revenue) sum across all dimensions; ratios must be recomputed, not summed.",
        ],
        [
            ex("Build a small star schema", "intermediate", "Fact table at order-line grain plus product and date dimensions, then slice revenue.", "sql", """
                CREATE TABLE dim_product AS SELECT id AS product_key, name, category FROM products;
                CREATE TABLE dim_date AS
                  SELECT DISTINCT created_at AS date_key, strftime('%Y-%m', created_at) AS month,
                         CASE strftime('%w', created_at) WHEN '0' THEN 1 WHEN '6' THEN 1 ELSE 0 END AS is_weekend
                  FROM orders;
                CREATE TABLE fact_sales AS
                  SELECT o.created_at AS date_key, i.product_id AS product_key, o.customer_id AS customer_key,
                         i.qty, i.qty * i.unit_price AS revenue
                  FROM orders o JOIN order_items i ON i.order_id = o.id WHERE o.status <> 'cancelled';
                SELECT d.month, p.category, d.is_weekend, SUM(f.revenue) AS revenue, SUM(f.qty) AS units
                FROM fact_sales f
                JOIN dim_date d ON d.date_key = f.date_key
                JOIN dim_product p ON p.product_key = f.product_key
                GROUP BY d.month, p.category, d.is_weekend ORDER BY d.month, revenue DESC;
            """),
            ex("Slowly changing dimension Type 2", "advanced", "A customer moves city: close the old row, insert a new current row, keep history.", "sql", """
                CREATE TABLE dim_customer (
                  customer_sk INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL, city TEXT NOT NULL,
                  valid_from TEXT NOT NULL, valid_to TEXT, is_current INTEGER NOT NULL DEFAULT 1
                );
                INSERT INTO dim_customer (customer_id, city, valid_from) SELECT id, city, created_at FROM customers;
                UPDATE dim_customer SET valid_to = '2024-07-01', is_current = 0 WHERE customer_id = 1 AND is_current = 1;
                INSERT INTO dim_customer (customer_id, city, valid_from) VALUES (1, 'Pune', '2024-07-01');
                SELECT customer_sk, customer_id, city, valid_from, valid_to, is_current
                FROM dim_customer WHERE customer_id = 1 ORDER BY valid_from;
            """),
        ],
        ["fact_sales(date_key, product_key, customer_key, qty, revenue)", "dim_* (surrogate key + descriptive attributes)", "SCD2: valid_from, valid_to, is_current", "JOIN fact -> dims, GROUP BY dim attributes", "dbt snapshots for SCD2"],
        [
            "Mixing grains in one fact table (order lines and order headers) double counts.",
            "Averaging pre-computed averages gives wrong answers; store sums and counts.",
            "Joining facts on natural keys breaks when dimension history is versioned.",
        ],
        [
            qa("basic", "What are fact and dimension tables?", "Fact tables store measurable events (sales, clicks) with numeric measures and foreign keys. Dimension tables store descriptive context (product, customer, date) used to filter and group facts."),
            qa("intermediate", "Star vs snowflake schema?", "A star schema keeps each dimension as one denormalized table, so queries need one join per dimension. A snowflake normalizes dimensions into hierarchies (product -> category -> department), saving space but adding joins and complexity."),
            qa("intermediate", "What is the grain of a fact table?", "The precise meaning of one row, such as one order line or one daily balance per account. Declaring it first determines which dimensions and measures belong and prevents double counting."),
            qa("advanced", "Explain SCD Type 1, 2 and 3.", "Type 1 overwrites the attribute, losing history. Type 2 inserts a new dimension row with a new surrogate key and validity dates, so facts keep pointing to the version in effect at the time. Type 3 adds a column for the previous value, keeping limited history."),
        ],
        ["normalization", "oltp-olap-columnar", "views-materialized"],
        chain(
            ("OLTP", "normalized", "Source", "Orders, items, customers and products in normalized form."),
            ("ETL/ELT", "transform", "Transform", "Pipelines reshape data at a declared grain.", "rows"),
            ("Fact", "order lines", "Fact table", "Measures plus keys to each dimension.", "facts"),
            ("Dimensions", "product, date", "Dimensions", "Wide descriptive tables with surrogate keys.", "keys"),
            ("Query", "slice and dice", "Analyze", "Join facts to dimensions and group by attributes.", "GROUP BY"),
        ),
    ),
    topic(
        "oltp-olap-columnar", "OLTP vs OLAP & Columnar Storage", "design", "intermediate", "OL",
        "Row stores for many small transactions, column stores for scanning billions of rows.",
        "A row store is a filing cabinet of complete customer folders: perfect for pulling one customer's file. A column store is a set of ledgers, one per attribute: to total every purchase amount you read only the 'amount' ledger instead of every folder.",
        "OLTP (online transaction processing) systems handle many short reads and writes touching a few rows by key, need strict consistency and low latency, and store data row by row (Postgres, MySQL, Oracle) so a whole record is read or written in one page. OLAP (online analytical processing) systems run fewer but heavy queries that scan millions or billions of rows and aggregate a handful of columns, so they store each column separately (ClickHouse, Snowflake, BigQuery, Redshift, DuckDB, Parquet files). Columnar layout reads only the referenced columns, compresses extremely well because values in a column are similar (dictionary, run-length, delta encoding), and enables vectorized execution that processes batches of values with SIMD. Zone maps (min/max per block) let scans skip irrelevant blocks. The trade-off is that single-row inserts and updates are expensive, so column stores batch writes and favour append-only data. Typical architectures keep OLTP as the source of truth and feed a warehouse via ETL/ELT or CDC; HTAP systems (TiDB, SingleStore, AlloyDB) try to serve both.",
        [
            "Checkout and payments on a row store (OLTP).",
            "Company-wide BI dashboards on a columnar warehouse (OLAP).",
            "Ad-hoc analysis of Parquet files with DuckDB.",
        ],
        [
            "OLTP: point lookups, small transactions, normalized, row-oriented, indexes.",
            "OLAP: big scans and aggregates, denormalized/star schema, columnar, few indexes.",
            "Columnar wins via column pruning, compression and vectorized execution.",
            "Do not run heavy analytics on the OLTP primary; use replicas or a warehouse.",
            "Batch inserts into column stores; tiny frequent writes create many small parts.",
        ],
        [
            ex("Analytical query shape", "basic", "Scans many rows but touches only two columns: ideal for a column store.", "sql", """
                SELECT kind, COUNT(*) AS events, MIN(ts) AS first_ts, MAX(ts) AS last_ts
                FROM events GROUP BY kind ORDER BY events DESC;
            """),
            ex("OLTP query shape", "basic", "Point lookup by key touching all columns of a few rows: ideal for a row store with an index.", "sql", """
                SELECT o.*, c.name, c.email
                FROM orders o JOIN customers c ON c.id = o.customer_id
                WHERE o.id = 13;
            """),
            ex("ClickHouse MergeTree table", "advanced", "Columnar, sorted by the ORDER BY key, partitioned by month, with TTL.", "sql", """
                CREATE TABLE events (
                  ts DateTime, user_id UInt64, kind LowCardinality(String), amount Decimal(12, 2)
                ) ENGINE = MergeTree
                PARTITION BY toYYYYMM(ts)
                ORDER BY (kind, user_id, ts)
                TTL ts + INTERVAL 1 YEAR;

                SELECT kind, count(), sum(amount) FROM events
                WHERE ts >= now() - INTERVAL 7 DAY GROUP BY kind;
            """, runnable=False),
        ],
        ["Row store: Postgres, MySQL (InnoDB), Oracle", "Column store: ClickHouse, Snowflake, BigQuery, Redshift, DuckDB", "Parquet / ORC columnar files", "ClickHouse: ENGINE = MergeTree ORDER BY (...)", "duckdb: SELECT ... FROM 'events/*.parquet'"],
        [
            "Running month-end reports on the OLTP primary starves customer traffic.",
            "SELECT * on a column store reads every column and loses the main advantage.",
            "Row-at-a-time inserts into a column store create too many small parts or files.",
        ],
        [
            qa("basic", "OLTP vs OLAP?", "OLTP serves many concurrent short transactions on few rows with strict consistency (orders, payments). OLAP serves complex analytical queries that scan and aggregate large volumes of historical data (reports, BI)."),
            qa("intermediate", "Why are column stores faster for analytics?", "They read only the columns a query references, compress columns heavily because similar values sit together, skip blocks using min/max metadata and process values in vectorized batches, cutting I/O and CPU per row dramatically."),
            qa("intermediate", "Why are column stores bad at OLTP?", "Inserting or updating one row touches a separate file or segment per column and breaks compression blocks, so single-row writes are expensive. Point lookups also have to reassemble rows from many columns."),
            qa("advanced", "What is HTAP and what are its challenges?", "Hybrid transactional/analytical processing serves both workloads from one system, typically a row store for writes with a replicated columnar copy for analytics. Challenges are isolating resources so analytics do not hurt transactions and keeping the columnar replica fresh and consistent."),
        ],
        ["star-schema", "time-series-databases", "partitioning"],
        chain(
            ("Row store", "full records", "Row layout", "Rows are stored together: great for fetching one record."),
            ("Column store", "one file per col", "Column layout", "Each column is stored separately.", "pivot"),
            ("Prune", "read 2 of 40 cols", "Column pruning", "A query reads only the columns it references.", "cols"),
            ("Compress", "dict, RLE, delta", "Compression", "Similar values compress 5-20x.", "bytes"),
            ("Vectorize", "SIMD batches", "Execution", "Values are processed in batches, skipping blocks via zone maps.", "batch"),
        ),
    ),
    topic(
        "multi-tenancy", "Multi-Tenant Schema Design", "design", "advanced", "MT",
        "Shared tables, schema per tenant or database per tenant, and how to isolate them safely.",
        "Housing options: a shared office floor with labelled desks (shared tables), separate rooms on one floor (schema per tenant), or separate buildings (database per tenant). More walls mean more privacy and more rent and maintenance.",
        "SaaS applications serve many customers (tenants) from one system and must keep their data isolated. The pool model puts all tenants in shared tables with a tenant_id column on every row: cheapest and easiest to operate and migrate, but every query must filter by tenant, and a noisy tenant affects others. The bridge model gives each tenant its own schema in a shared database: stronger logical separation and easier per-tenant restore, but thousands of schemas strain catalogs and migrations. The silo model gives each tenant its own database or cluster: maximum isolation, per-tenant tuning, data residency and simple deletion, at the highest cost and operational overhead. Many products mix models, placing large or regulated tenants in silos. In the pool model, enforce isolation in depth: tenant_id leading every composite primary key and index, Postgres row-level security (RLS) bound to a session setting, scoped repository code and tests that prove cross-tenant access fails. tenant_id is also the natural shard key when the pool outgrows a single database (Citus distributes tables by it).",
        [
            "A B2B SaaS app with thousands of small customers (pool).",
            "Enterprise customers requiring dedicated databases and regional residency (silo).",
            "Sharding a growing SaaS database by tenant_id.",
        ],
        [
            "Put tenant_id first in primary keys and indexes: (tenant_id, id).",
            "Row-level security enforces isolation even if application code forgets a filter.",
            "Per-tenant quotas and rate limits contain noisy neighbours.",
            "Plan tenant export, deletion and restore from day one.",
            "tenant_id is the natural shard key; keep tenant data co-located.",
        ],
        [
            ex("Pool model with tenant-leading keys", "intermediate", "Every table carries tenant_id; queries and indexes lead with it.", "sql", """
                CREATE TABLE tenants (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
                CREATE TABLE projects (
                  tenant_id INTEGER NOT NULL REFERENCES tenants(id),
                  id INTEGER NOT NULL,
                  name TEXT NOT NULL,
                  PRIMARY KEY (tenant_id, id)
                );
                INSERT INTO tenants VALUES (1, 'Acme'), (2, 'Globex');
                INSERT INTO projects VALUES (1, 1, 'Website'), (1, 2, 'Mobile app'), (2, 1, 'Data lake');
                SELECT id, name FROM projects WHERE tenant_id = 1 ORDER BY id;
                EXPLAIN QUERY PLAN SELECT name FROM projects WHERE tenant_id = 2 AND id = 1;
            """),
            ex("Row-level security in Postgres", "advanced", "The database filters rows by the tenant set for the session.", "sql", """
                ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
                ALTER TABLE projects FORCE ROW LEVEL SECURITY;
                CREATE POLICY tenant_isolation ON projects
                  USING (tenant_id = current_setting('app.tenant_id')::bigint)
                  WITH CHECK (tenant_id = current_setting('app.tenant_id')::bigint);

                -- per request, inside the transaction (app role must not be the table owner or BYPASSRLS):
                BEGIN;
                SET LOCAL app.tenant_id = '42';
                SELECT * FROM projects;          -- only tenant 42's rows
                COMMIT;
            """, runnable=False),
            ex("Per-tenant usage to spot noisy neighbours", "intermediate", "Which tenants (here: customers) generate the most rows and revenue.", "sql", """
                SELECT o.customer_id AS tenant, COUNT(DISTINCT o.id) AS orders,
                       SUM(i.qty * i.unit_price) AS revenue,
                       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM order_items), 1) AS pct_of_rows
                FROM orders o JOIN order_items i ON i.order_id = o.id
                GROUP BY o.customer_id ORDER BY pct_of_rows DESC LIMIT 5;
            """),
        ],
        ["PRIMARY KEY (tenant_id, id)", "CREATE POLICY p ON t USING (tenant_id = current_setting('app.tenant_id')::bigint)", "SET LOCAL app.tenant_id = '42'", "CREATE SCHEMA tenant_42 (bridge model)", "Citus: SELECT create_distributed_table('projects', 'tenant_id')"],
        [
            "A single missing WHERE tenant_id = ? leaks data across customers.",
            "SET (not SET LOCAL) with a transaction-mode pooler leaks tenant context to the next client.",
            "Schema-per-tenant with tens of thousands of schemas makes migrations take hours.",
            "Global unique constraints (email) must decide whether they are per tenant or global.",
        ],
        [
            qa("intermediate", "Compare pool, bridge and silo multi-tenancy.", "Pool: shared tables with tenant_id, cheapest and simplest to operate but weakest isolation. Bridge: schema per tenant, better separation, heavier migrations. Silo: database per tenant, strongest isolation and per-tenant tuning or residency, highest cost and operational overhead."),
            qa("advanced", "How do you guarantee tenant isolation in shared tables?", "Defence in depth: tenant_id in every table and leading every key, Postgres row-level security bound to a per-transaction setting, a data-access layer that always scopes by tenant, and automated tests that attempt cross-tenant reads and writes."),
            qa("advanced", "How do you handle a noisy neighbour?", "Measure per-tenant resource usage, apply rate limits and quotas, move heavy tenants to dedicated shards or silos, and isolate expensive workloads (exports, reports) onto replicas or queues."),
            qa("intermediate", "Why put tenant_id first in composite keys?", "Queries almost always filter by tenant, so a leading tenant_id lets indexes seek to one tenant's data, keeps it physically clustered, and makes tenant_id a ready shard key."),
        ],
        ["replication-sharding", "database-security", "composite-covering-indexes"],
        chain(
            ("Request", "tenant 42", "Authenticate", "The request is authenticated and its tenant resolved."),
            ("Context", "SET LOCAL", "Set context", "The app sets app.tenant_id for this transaction.", "42"),
            ("RLS", "policy filter", "Row-level security", "The policy adds tenant_id = 42 to every query.", "policy"),
            ("Index", "(tenant_id, id)", "Seek", "Tenant-leading indexes seek straight to the tenant's rows.", "seek"),
            ("Result", "only tenant 42", "Isolated result", "Rows of other tenants are never returned.", "rows"),
        ),
    ),
    # ------------------------------------------------------------------ operations
    topic(
        "backups-pitr", "Backups, Restore & Point-in-Time Recovery", "operations", "intermediate", "BK",
        "Logical and physical backups, WAL archiving for PITR, and why untested backups do not exist.",
        "A save point in a video game plus a recording of every move since. If you fall off a cliff, you reload the save and replay the moves up to one second before the jump.",
        "Backups protect against hardware failure, operator mistakes (a DELETE without WHERE), corruption and ransomware; replication alone does not, because it faithfully copies the mistake. Logical backups (pg_dump, mysqldump) export SQL or an archive of objects: portable across versions and selective, but slow to restore for large databases. Physical backups (pg_basebackup, pgBackRest, Percona XtraBackup, storage snapshots) copy data files and restore fast at the same major version. Point-in-time recovery combines a physical base backup with continuously archived WAL or binlogs, so you can restore to any moment, for example just before the bad statement. Two targets drive the design: RPO (how much data you can lose) and RTO (how long recovery may take). Follow the 3-2-1 rule (three copies, two media, one offsite), encrypt backups at rest with KMS-managed keys, restrict and audit access, use immutable or object-lock storage against ransomware, and regularly restore into a scratch environment to prove backups actually work.",
        [
            "Recovering from an accidental DROP TABLE or bad migration.",
            "Restoring to a new cluster after storage failure.",
            "Cloning production into an isolated environment for testing (with masking).",
        ],
        [
            "Replication is not a backup: mistakes replicate instantly.",
            "PITR = base backup + continuous WAL/binlog archive.",
            "Define RPO/RTO and design backup frequency and method to meet them.",
            "Encrypt backups, use immutable storage, and restrict who can read or delete them.",
            "Test restores regularly and time them; monitor archive gaps.",
        ],
        [
            ex("Logical backup and PITR in Postgres", "intermediate", "Dump/restore, plus base backup and WAL archiving for point-in-time recovery.", "bash", """
                # logical: portable, selective
                pg_dump --format=custom --file=shop.dump "$DATABASE_URL"
                pg_restore --dbname="$RESTORE_URL" --jobs=4 shop.dump

                # physical base backup + continuous WAL archiving (postgresql.conf)
                #   archive_mode = on
                #   archive_command = 'pgbackrest --stanza=shop archive-push %p'
                pgbackrest --stanza=shop --type=full backup

                # restore to just before the bad statement
                pgbackrest --stanza=shop --type=time --target="2024-07-05 14:31:59+00" \\
                  --target-action=promote restore
            """, runnable=False),
            ex("Recover rows from a snapshot table", "basic", "Simulates restoring deleted rows from a backup copy after an accidental DELETE.", "sql", """
                CREATE TABLE backup_customers AS SELECT * FROM customers;   -- nightly snapshot
                DELETE FROM customers WHERE city = 'Berlin' AND id NOT IN (SELECT customer_id FROM orders);
                SELECT COUNT(*) AS after_mistake FROM customers;
                INSERT INTO customers SELECT * FROM backup_customers b
                WHERE NOT EXISTS (SELECT 1 FROM customers c WHERE c.id = b.id);
                SELECT COUNT(*) AS after_restore FROM customers;
            """),
            ex("Restore drill checklist", "advanced", "What a scheduled restore test verifies.", "text", """
                1. Pick the latest base backup and restore it into an isolated environment.
                2. Replay archived WAL to a chosen timestamp; record time taken (actual RTO).
                3. Compare the newest restored transaction with the target (actual RPO).
                4. Run integrity checks: amcheck / pg_checksums, row counts, key business queries.
                5. Confirm backup encryption keys are retrievable from KMS by the restore role only.
                6. Destroy the environment and record results; alert if any step failed.
            """, runnable=False),
        ],
        ["pg_dump -Fc / pg_restore -j 4", "pg_basebackup -D /backup -X stream", "archive_mode = on; archive_command = ...", "recovery_target_time = '2024-07-05 14:31:59+00'", "mysqldump --single-transaction / mysqlbinlog --stop-datetime"],
        [
            "Backups that have never been restored are hopes, not backups.",
            "A gap in the WAL archive silently breaks PITR beyond that point.",
            "Backups stored with the same credentials as production can be deleted by the same attacker.",
            "pg_dump without --single-transaction (MySQL) or consistent snapshot gives inconsistent dumps.",
        ],
        [
            qa("basic", "Why is replication not a backup?", "Replication copies every change, including accidental deletes, bad migrations and corruption, to replicas within seconds. Backups preserve past states you can return to."),
            qa("intermediate", "Logical vs physical backups?", "Logical backups export schema and data as SQL or archives: portable across versions and selective, but slow for large databases. Physical backups copy data files and WAL: fast to restore and enable PITR, but tied to the same major version and platform."),
            qa("intermediate", "What are RPO and RTO?", "RPO (recovery point objective) is the maximum acceptable data loss measured in time. RTO (recovery time objective) is the maximum acceptable downtime to restore service. They determine backup frequency, archiving and restore strategy."),
            qa("advanced", "How does point-in-time recovery work?", "Restore a physical base backup taken before the target time, then replay archived WAL or binlogs sequentially until the recovery target (timestamp, transaction id or LSN), then promote the instance. It needs an unbroken log archive since the base backup."),
        ],
        ["wal-durability", "database-security", "replication-sharding"],
        chain(
            ("Base backup", "nightly full", "Base backup", "A physical copy of the data files is taken."),
            ("WAL archive", "continuous", "Archive logs", "Every WAL segment is shipped to encrypted storage.", "WAL"),
            ("Incident", "bad DELETE", "Incident", "A mistake happens at 14:32.", "oops"),
            ("Restore", "base + replay", "Restore", "Restore the base backup and replay WAL.", "replay"),
            ("Target", "14:31:59", "Stop and promote", "Stop just before the mistake and promote.", "promote"),
        ),
    ),
    topic(
        "database-security", "Database Security", "operations", "intermediate", "SE",
        "Least privilege, SQL injection defence, encryption at rest and in transit, auditing and secrets handling.",
        "A bank vault: staff get keys only to the rooms they need, every visit is logged, cash moves between branches in armoured vans (TLS), and the vault itself is locked even if someone breaks into the building (encryption at rest).",
        "Database security is layered. Network: keep databases in private subnets, allow only application hosts, and never expose them to the internet. Authentication: use strong mechanisms (SCRAM-SHA-256, IAM/Kerberos, client certificates), short-lived credentials from a secrets manager rather than passwords in code or config files, and separate roles per service. Authorization: grant least privilege, so the app role gets only SELECT/INSERT/UPDATE on its tables, migrations run under a separate owner role, and nobody uses the superuser for routine work; views and row-level security narrow access further. SQL injection is prevented by parameterized queries (bind variables) everywhere, with allow-lists for dynamic identifiers like sort columns; escaping is fragile. Encryption in transit should use TLS 1.3 with certificate verification (sslmode=verify-full), and encryption at rest uses AES-256-GCM through storage or TDE with keys in a KMS/HSM, plus application-level envelope encryption for especially sensitive fields. Store user passwords only as slow salted hashes (argon2id or bcrypt), never encrypted or with fast hashes, and audit access with pgaudit or the cloud provider's logs.",
        [
            "Locking down an application role to the minimum privileges.",
            "Preventing SQL injection in a search endpoint with dynamic sorting.",
            "Meeting compliance (PCI DSS, HIPAA, GDPR) for encryption and auditing.",
        ],
        [
            "Parameterize every query; allow-list identifiers (columns, sort order) that cannot be bound.",
            "Separate roles: app (DML only), migrator (DDL), read-only analyst, admin (break-glass).",
            "TLS 1.3 with verify-full in transit; AES-256-GCM at rest with KMS-managed keys.",
            "Credentials come from a secrets manager or IAM auth, rotated automatically; never in source code.",
            "Hash user passwords with argon2id or bcrypt; never store them reversibly.",
        ],
        [
            ex("What injection does", "basic", "Concatenating input like ' OR '1'='1 turns a lookup into 'return everything'. Parameters prevent this.", "sql", """
                -- intended: SELECT name FROM customers WHERE email = '<input>'
                -- attacker input:  x' OR '1'='1
                SELECT name, email FROM customers WHERE email = 'x' OR '1'='1';
                -- with a bound parameter the whole input is just a value, so nothing matches:
                SELECT name, email FROM customers WHERE email = 'x'' OR ''1''=''1';
            """),
            ex("Parameterized queries and safe dynamic sorting", "intermediate", "Bind values; map user-chosen sort keys through an allow-list.", "python", """
                import sqlite3

                SORTABLE = {"name": "name", "city": "city", "newest": "created_at DESC"}

                def search_customers(conn: sqlite3.Connection, city: str, sort: str):
                    order_by = SORTABLE.get(sort, "name")          # identifiers cannot be bound
                    sql = f"SELECT id, name, city FROM customers WHERE city = ? ORDER BY {order_by} LIMIT 50"
                    return conn.execute(sql, (city,)).fetchall()   # value is bound, never concatenated
            """, runnable=False),
            ex("Least-privilege roles and TLS 1.3 in Postgres", "advanced", "App role with DML only, migrator owns the schema, TLS 1.3 enforced; secrets come from a vault.", "sql", """
                -- postgresql.conf:  ssl = on;  ssl_min_protocol_version = 'TLSv1.3'
                -- pg_hba.conf:      hostssl shop app_rw 10.0.0.0/16 scram-sha-256
                CREATE ROLE migrator NOLOGIN;
                CREATE ROLE app_rw LOGIN;                 -- password set from the secrets manager, never in code
                REVOKE ALL ON SCHEMA public FROM PUBLIC;
                GRANT USAGE ON SCHEMA app TO app_rw;
                GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA app TO app_rw;
                ALTER DEFAULT PRIVILEGES FOR ROLE migrator IN SCHEMA app
                  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_rw;
                -- client: postgresql://app_rw@db.internal/shop?sslmode=verify-full (password via env/IAM token)
            """, runnable=False),
        ],
        ["cursor.execute('... WHERE id = ?', (user_id,))", "GRANT SELECT, INSERT ON t TO app_rw; REVOKE ALL ... FROM PUBLIC", "ssl_min_protocol_version = 'TLSv1.3'; sslmode=verify-full", "password_encryption = 'scram-sha-256'", "CREATE EXTENSION pgaudit", "AWS RDS: storage encryption with KMS + IAM database auth"],
        [
            "Escaping input instead of parameterizing misses edge cases (encodings, numeric contexts).",
            "The application connecting as superuser turns any injection into full compromise.",
            "sslmode=require encrypts but does not verify the server certificate; use verify-full.",
            "Production data copied to dev/test without masking leaks PII.",
        ],
        [
            qa("basic", "How do you prevent SQL injection?", "Use parameterized queries or prepared statements for every value so input is never parsed as SQL. For identifiers like sort columns that cannot be bound, map user input through an allow-list. Least-privilege roles limit the damage if something slips through."),
            qa("intermediate", "What does least privilege look like for a database?", "Each service has its own role with only the DML it needs on its own schema; DDL runs under a separate migration role; analysts get read-only roles or views; superuser is break-glass only, audited, and never used by applications."),
            qa("intermediate", "How should user passwords be stored?", "As salted, slow, memory-hard hashes such as argon2id (or bcrypt for legacy), verified in constant time. Never store them encrypted or with fast hashes, since a leaked database would let attackers recover or brute-force them quickly."),
            qa("advanced", "Encryption at rest vs in transit vs application-level?", "In transit: TLS 1.3 with certificate verification protects data on the network. At rest: AES-256-GCM via disk, storage or TDE protects stolen disks and backups, with keys in a KMS/HSM. Application-level envelope encryption protects specific fields even from DBAs or a compromised database, at the cost of losing indexing and querying on them."),
            qa("advanced", "How do you manage database credentials safely?", "Never hardcode them. Fetch short-lived credentials from a secrets manager (Vault dynamic secrets, AWS Secrets Manager rotation) or use IAM token authentication, scope them per service, rotate automatically and audit their use."),
        ],
        ["views-materialized", "multi-tenancy", "backups-pitr"],
        chain(
            ("Network", "private subnet", "Network boundary", "Only application hosts can reach the database."),
            ("TLS 1.3", "verify-full", "Encrypted channel", "Connections use TLS 1.3 with certificate verification.", "TLS"),
            ("AuthN", "SCRAM / IAM", "Authenticate", "Short-lived credentials from a secrets manager or IAM.", "creds"),
            ("AuthZ", "least privilege", "Authorize", "The role can only run the DML it needs; RLS narrows rows.", "GRANT"),
            ("Query", "bound params", "Safe queries", "Parameterized SQL keeps input as data, never code.", "?"),
            ("At rest", "AES-256-GCM", "Storage", "Data and backups are encrypted with KMS-managed keys; access is audited.", "KMS"),
        ),
    ),
]

SCENARIOS = [
    {"level": "intermediate", "topic": "connection-pooling", "q": "After autoscaling from 10 to 60 app pods, the database starts rejecting connections with 'too many clients' and latency spikes.", "a": "Each pod opens its own pool, so total connections (pods x pool size) exceeded max_connections and the database thrashes. Cap per-pod pools so the total fits with headroom, put PgBouncer (transaction mode) or RDS Proxy in front to multiplex, fail fast with pool timeouts, and find idle-in-transaction sessions holding connections."},
    {"level": "advanced", "topic": "locking-deadlocks", "q": "Logs show frequent 'deadlock detected' errors from a transfer endpoint during peak hours.", "a": "Concurrent transfers lock the two accounts in opposite orders (A then B vs B then A). Lock rows in a consistent order (SELECT ... WHERE id IN (a, b) ORDER BY id FOR UPDATE), keep the transaction short with no external calls inside, ensure the WHERE uses an index, and retry deadlock victims automatically with backoff."},
    {"level": "intermediate", "topic": "pagination", "q": "An infinite-scroll feed gets slower the further users scroll, and some items appear twice.", "a": "It uses OFFSET pagination: deep offsets scan and discard many rows, and new inserts shift positions so rows repeat. Switch to keyset pagination on (created_at, id) with a matching composite index and an opaque cursor; each page becomes one index seek and results stay stable."},
    {"level": "advanced", "topic": "change-data-capture", "q": "The Postgres primary's disk filled up overnight although data volume barely changed.", "a": "A logical replication slot (for a stopped CDC connector or a dropped subscriber) was retaining WAL. Check pg_replication_slots for inactive slots and retained bytes, restart the consumer or drop the abandoned slot, set max_slot_wal_keep_size, and alert on slot lag."},
    {"level": "advanced", "topic": "statistics-cardinality", "q": "A report query that took 2 seconds now takes 10 minutes right after the nightly bulk import.", "a": "The import changed data distribution but statistics are stale, so the planner underestimates rows and picks a nested loop. EXPLAIN ANALYZE shows estimated vs actual rows diverging. Run ANALYZE as the final step of the import, raise the statistics target or add extended statistics for correlated columns, and verify the plan switches to a hash join."},
    {"level": "intermediate", "topic": "caching-redis", "q": "Every few minutes the database CPU jumps to 100% for a few seconds, aligned with cache expiry of the home page data.", "a": "A cache stampede: the hot key expires and thousands of concurrent requests miss and recompute it. Use a rebuild lock (SET key NX EX) or request coalescing so one request refreshes, serve stale data while refreshing, add TTL jitter, and refresh hot keys proactively before expiry."},
]

from ._catalog import build_lessons

TOPICS += build_lessons([
    ("rdbms-vs-nosql", "RDBMS vs NoSQL: Choose by Access Pattern", "nosql", "intermediate", "Relational databases organize data into relations with constraints, joins and transactional SQL. NoSQL is a family of key-value, document, wide-column and graph stores, each with different access and partitioning trade-offs. Choose from queries and invariants rather than a slogan about scale.", "Relational ledger: constraints + multi-row transactions · document profile: aggregate read by key · graph: multi-hop relationships", "NoSQL does not mean no schema, no transactions or automatic scale; model the query and consistency requirements first.", "Is NoSQL always faster and easier to scale than an RDBMS?", "No. Each NoSQL product optimizes particular access patterns and still has partitioning, hot-key, consistency and operational trade-offs. Relational databases also scale for many workloads. Choose from workload evidence and correctness needs.", ["nosql-cap", "key-value-stores", "document-databases", "graph-databases", "transactions-acid"]),
    ("redis-vs-memcached", "Redis vs Memcached: Cache Behavior & Trade-offs", "nosql", "intermediate", "Redis and Memcached are in-memory data stores often used as caches. Memcached focuses on simple ephemeral key/value caching; Redis adds richer data structures, scripting, streams and optional persistence/replication. Either can become a failure dependency if the app assumes every key exists.", "Redis: sorted set for a leaderboard · Memcached: simple page-fragment get/set with TTL", "Use cache-aside with a bounded TTL and a source-of-truth database; plan eviction, stampede protection and cache-outage behavior.", "Is Redis a drop-in replacement for Memcached?", "Not always. Both can cache values, but APIs, data structures, persistence and operational behavior differ. Choose from required features, client support, failure model and measured workload.", ["caching-redis", "nosql-cap", "transactions-acid", "replication-sharding"]),
], "DB", "A database is a data model plus consistency, access and recovery rules.")
