"""Databases: relational basics to MVCC, replication and NoSQL. SQL examples run on app.sqlrun.SEED."""

from ._dsl import ex, flow, node, pkt, qa, step

CATEGORIES = [
    {"id": "foundations", "title": "Foundations", "color": "sky", "blurb": "Tables, keys and the shape of data."},
    {"id": "querying", "title": "Querying", "color": "mint", "blurb": "Ask precise questions with SQL."},
    {"id": "performance", "title": "Performance", "color": "lemon", "blurb": "Indexes and query plans."},
    {"id": "transactions", "title": "Transactions", "color": "lilac", "blurb": "ACID, isolation and concurrency."},
    {"id": "scale", "title": "Scale & NoSQL", "color": "peach", "blurb": "Replicas, shards and other data models."},
]

TOPICS = [
    {
        "id": "relational-model", "title": "Relational Model & Keys", "category": "foundations", "level": "basic", "code": "RM",
        "tagline": "Tables of rows, primary keys that identify them and foreign keys that connect them.",
        "analogy": "A library: every book has a unique barcode (primary key), and each loan slip records the barcode of the book and the card number of the member (foreign keys).",
        "what": "Data lives in relations (tables). Each row is one fact, each column one attribute with a type. A primary key uniquely identifies a row; a foreign key references another table's key and the database enforces it (referential integrity). Constraints such as NOT NULL, UNIQUE and CHECK keep bad data out at the source instead of in application code.",
        "use_cases": [
            "Orders that must always belong to a real customer (FOREIGN KEY).",
            "Emails that must never repeat (UNIQUE).",
            "Prices that can never be negative (CHECK).",
        ],
        "key_points": [
            "Natural key (email) vs surrogate key (auto id): surrogates never change, so prefer them for joins.",
            "Composite keys: order_items is keyed by (order_id, product_id).",
            "ON DELETE CASCADE / RESTRICT / SET NULL decide what happens to children.",
            "Constraints are documentation the database actually enforces.",
        ],
        "examples": [
            ex("Look at the schema", "basic", "List the columns and keys of the orders table.", "sql", """
                PRAGMA table_info(orders);
                PRAGMA foreign_key_list(orders);
            """),
            ex("Constraints in action", "intermediate", "Each statement is rejected by a constraint. Run them one at a time to see which.", "sql", """
                -- CHECK: price must be positive
                INSERT INTO products (name, category, price) VALUES ('Free lunch', 'grocery', 0);
            """),
            ex("Foreign key protects orders", "intermediate", "Customer 999 does not exist, so the insert fails.", "sql", """
                INSERT INTO orders (customer_id, status, created_at) VALUES (999, 'paid', '2024-08-01');
            """),
        ],
        "commands": ["PRIMARY KEY (id)", "FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE RESTRICT", "UNIQUE (email)", "CHECK (price > 0)", "PRAGMA table_info(table)"],
        "gotchas": [
            "Using a mutable natural key (email) as the primary key makes every rename a cascade.",
            "Foreign keys are only enforced if enabled (SQLite: PRAGMA foreign_keys = ON).",
            "Missing index on a foreign key column makes deletes on the parent table slow.",
        ],
        "interview": [
            qa("basic", "Primary key vs unique constraint?", "Both enforce uniqueness. A table has one primary key, which cannot be NULL and is the row's identity (often the clustered index). You can have many UNIQUE constraints and they may allow NULLs depending on the engine."),
            qa("basic", "What is a foreign key and why use it?", "A column that must match a key in another table. The database rejects orphans and can cascade deletes, so integrity holds even if application code has bugs."),
            qa("intermediate", "Surrogate or natural keys?", "Surrogates (auto-increment, UUID) are stable and compact, so they make good join keys. Natural keys carry business meaning but can change. Common practice: surrogate PK plus a UNIQUE constraint on the natural key."),
            qa("intermediate", "UUID vs auto-increment primary keys?", "Auto-increment is small and index friendly but leaks counts and needs a central generator. Random UUIDv4 fragments B-tree inserts; time-ordered UUIDv7/ULID keep locality and work across services."),
        ],
        "related": ["normalization", "joins"],
        "flow": flow(
            [node("cust", "customers", 18, 30, "sky", "id PK · email UNIQUE"), node("ord", "orders", 50, 30, "mint", "id PK · customer_id FK"),
             node("items", "order_items", 82, 30, "lemon", "PK (order_id, product_id)"), node("prod", "products", 82, 78, "peach", "id PK · CHECK price>0"),
             node("bad", "orders row", 50, 80, "rose", "customer_id = 999", hidden=True)],
            [("cust", "ord"), ("ord", "items"), ("prod", "items")],
            [
                step("Rows have identity", "Each table has a primary key. <b>customers.id</b> identifies exactly one customer.", ["cust"]),
                step("Foreign keys connect tables", "<b>orders.customer_id</b> must match an existing customers.id.", ["cust", "ord"], [pkt("ord", "cust", "customer_id=1")]),
                step("Composite keys", "<b>order_items</b> is identified by the pair (order_id, product_id): one line per product per order.", ["items", "ord", "prod"], [pkt("items", "ord", "order_id"), pkt("items", "prod", "product_id")]),
                step("Integrity is enforced", "Inserting an order for customer 999 is rejected: <b>FOREIGN KEY constraint failed</b>.", ["bad", "cust"], [pkt("bad", "cust", "999?", "rose")], {"bad": {"hidden": False}}),
            ],
        ),
    },
    {
        "id": "sql-basics", "title": "SQL Basics: SELECT, WHERE, ORDER", "category": "querying", "level": "basic", "code": "SQ",
        "tagline": "Filter, sort, page and shape rows with declarative queries.",
        "analogy": "Ordering at a counter: you say WHAT you want (two large coffees, no sugar), not HOW to brew it. The barista (query planner) decides the steps.",
        "what": "SQL is declarative. SELECT picks columns, FROM names the table, WHERE filters rows, ORDER BY sorts and LIMIT/OFFSET pages. Logical evaluation order is FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT, which explains why a column alias works in ORDER BY but not in WHERE.",
        "use_cases": ["Find all paid orders this month.", "Show the 5 most expensive products.", "Search customers by city with IN / LIKE."],
        "key_points": [
            "NULL is unknown: use IS NULL, never = NULL.",
            "LIKE 'abc%' can use an index; LIKE '%abc' cannot.",
            "OFFSET pagination gets slower with depth; use keyset (WHERE id > last_id).",
            "Always ORDER BY when using LIMIT, otherwise the order is not guaranteed.",
        ],
        "examples": [
            ex("Filter and sort", "basic", "Electronics under 150, cheapest first.", "sql", """
                SELECT name, price
                FROM products
                WHERE category = 'electronics' AND price < 150
                ORDER BY price;
            """),
            ex("IN, LIKE and NULL", "basic", "Customers in two cities, and employees without a manager.", "sql", """
                SELECT name, city FROM customers WHERE city IN ('Berlin', 'Bengaluru') ORDER BY name;
                SELECT name, title FROM employees WHERE manager_id IS NULL;
            """),
            ex("Keyset pagination", "intermediate", "Page 2 of events without OFFSET: remember the last id you saw.", "sql", """
                SELECT id, user_id, kind FROM events ORDER BY id LIMIT 5;
                SELECT id, user_id, kind FROM events WHERE id > 5 ORDER BY id LIMIT 5;
            """),
        ],
        "commands": ["SELECT col FROM t WHERE cond ORDER BY col LIMIT n", "WHERE col IN (...)", "WHERE col LIKE 'pre%'", "WHERE col IS NULL", "SELECT DISTINCT col FROM t"],
        "gotchas": ["WHERE x = NULL is never true.", "SELECT * in production breaks when columns change and fetches more than you need.", "String comparisons may be case sensitive depending on collation."],
        "interview": [
            qa("basic", "What is the logical order of SQL clause evaluation?", "FROM/JOIN → WHERE → GROUP BY → HAVING → SELECT → DISTINCT → ORDER BY → LIMIT. That is why aliases defined in SELECT are not visible in WHERE."),
            qa("basic", "WHERE vs HAVING?", "WHERE filters rows before grouping; HAVING filters groups after aggregation, so it can reference COUNT/SUM."),
            qa("intermediate", "Why is OFFSET pagination slow for deep pages?", "The database still reads and discards all skipped rows. Keyset pagination (WHERE id > :last ORDER BY id LIMIT n) uses the index to jump straight there."),
            qa("intermediate", "Why does NOT IN behave strangely with NULLs?", "If the subquery returns a NULL, x NOT IN (...) is unknown for every row, so nothing is returned. Prefer NOT EXISTS."),
        ],
        "related": ["joins", "aggregation"],
        "flow": flow(
            [node("from", "FROM products", 12, 50, "sky", "12 rows"), node("where", "WHERE", 34, 50, "mint", "category, price"),
             node("select", "SELECT", 56, 50, "lilac", "name, price"), node("order", "ORDER BY", 76, 50, "lemon", "price"), node("limit", "LIMIT", 92, 50, "peach", "first n")],
            [("from", "where"), ("where", "select"), ("select", "order"), ("order", "limit")],
            [
                step("Start from the table", "Logically, every query starts with <b>FROM</b>: all rows of products.", ["from"]),
                step("Filter rows", "<b>WHERE</b> keeps only rows that match. 12 rows become 4.", ["where"], [pkt("from", "where", "12 rows")]),
                step("Shape columns", "<b>SELECT</b> picks and computes the output columns.", ["select"], [pkt("where", "select", "4 rows")]),
                step("Sort and page", "<b>ORDER BY</b> sorts, then <b>LIMIT</b> keeps the first n. Without ORDER BY the order is undefined.", ["order", "limit"], [pkt("select", "order", "4 rows"), pkt("order", "limit", "sorted")]),
            ],
        ),
    },
    {
        "id": "joins", "title": "Joins", "category": "querying", "level": "basic", "code": "JN",
        "tagline": "Combine rows across tables: inner, left, self and anti joins.",
        "analogy": "Matching guests to a seating plan. INNER JOIN shows only guests with a seat; LEFT JOIN lists every guest and leaves the seat blank if they have none.",
        "what": "A join pairs rows from two tables using a condition, usually key equality. INNER returns matches only. LEFT returns every left row plus matches (NULLs when none). FULL keeps unmatched rows from both sides. A self join relates a table to itself (employee → manager). Anti joins (LEFT JOIN ... WHERE right.id IS NULL, or NOT EXISTS) find rows with no match.",
        "use_cases": ["Orders with customer names.", "Customers who never ordered (anti join).", "Employee and manager names (self join)."],
        "key_points": [
            "Join conditions go in ON; filters on the right table in WHERE turn a LEFT JOIN into an INNER JOIN.",
            "Join order is chosen by the planner; you choose the semantics.",
            "Algorithms: nested loop (small/indexed), hash join (large, equality), merge join (sorted inputs).",
            "Joining on a non-unique key multiplies rows: watch your counts.",
        ],
        "examples": [
            ex("Inner join", "basic", "Every order with its customer's name.", "sql", """
                SELECT o.id, c.name, o.status
                FROM orders o
                JOIN customers c ON c.id = o.customer_id
                ORDER BY o.id
                LIMIT 8;
            """),
            ex("Anti join: customers without orders", "intermediate", "LEFT JOIN plus IS NULL, and the NOT EXISTS equivalent.", "sql", """
                SELECT c.name FROM customers c
                LEFT JOIN orders o ON o.customer_id = c.id
                WHERE o.id IS NULL;

                SELECT name FROM customers c
                WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id);
            """),
            ex("Self join and three-way join", "intermediate", "Managers, then revenue per order.", "sql", """
                SELECT e.name AS employee, m.name AS manager
                FROM employees e LEFT JOIN employees m ON m.id = e.manager_id;

                SELECT o.id, c.name, SUM(i.qty * i.unit_price) AS total
                FROM orders o
                JOIN customers c ON c.id = o.customer_id
                JOIN order_items i ON i.order_id = o.id
                GROUP BY o.id, c.name
                ORDER BY total DESC LIMIT 5;
            """),
        ],
        "commands": ["SELECT ... FROM a JOIN b ON b.a_id = a.id", "LEFT JOIN b ON ... WHERE b.id IS NULL", "WHERE NOT EXISTS (SELECT 1 FROM b WHERE ...)", "FROM t a JOIN t b ON b.parent_id = a.id"],
        "gotchas": ["A WHERE condition on the right table of a LEFT JOIN silently removes the NULL rows; move it into ON.", "Joining two one-to-many tables at once multiplies rows and inflates SUMs.", "Implicit comma joins without a condition are cross joins."],
        "interview": [
            qa("basic", "INNER vs LEFT JOIN?", "INNER keeps only rows matching in both tables. LEFT keeps every row of the left table and fills right columns with NULL when there is no match."),
            qa("intermediate", "How do you find rows in A with no match in B?", "LEFT JOIN B ... WHERE B.key IS NULL, or WHERE NOT EXISTS (...). Avoid NOT IN when B.key can be NULL."),
            qa("advanced", "Nested loop vs hash vs merge join?", "Nested loop: for each outer row probe the inner (great with an index or tiny inputs). Hash: build a hash table on the smaller input, probe with the larger (equality only). Merge: walk two sorted inputs together (good when already sorted by an index)."),
            qa("advanced", "Why might a join query return more rows than expected?", "One-to-many fan-out: each order joins to N items, so joining payments too yields N×M rows. Aggregate in subqueries before joining."),
        ],
        "related": ["sql-basics", "aggregation", "indexes"],
        "flow": flow(
            [node("c1", "Asha", 15, 20, "sky", "customer 1"), node("c2", "Ben", 15, 50, "sky", "customer 2"), node("c5", "Kiran", 15, 80, "sky", "customer 11"),
             node("o1", "order 1", 60, 15, "mint", "customer_id 1"), node("o2", "order 2", 60, 38, "mint", "customer_id 1"), node("o3", "order 3", 60, 61, "mint", "customer_id 2"),
             node("res", "result", 90, 50, "lilac", "joined rows", "round")],
            [],
            [
                step("Two tables", "customers on the left, orders on the right, matched by <b>o.customer_id = c.id</b>.", ["c1", "c2", "c5", "o1", "o2", "o3"]),
                step("Inner join matches", "Asha matches two orders, Ben one. Each match becomes a result row.", ["c1", "c2", "o1", "o2", "o3"], [pkt("o1", "c1", "1"), pkt("o2", "c1", "1"), pkt("o3", "c2", "2")]),
                step("Left join keeps everyone", "Kiran has never ordered: LEFT JOIN still returns her with NULL order columns.", ["c5", "res"], [pkt("c5", "res", "NULL", "rose")]),
                step("Anti join", "Add <b>WHERE o.id IS NULL</b> and only the unmatched customers remain.", ["c5"], [pkt("c5", "res", "no orders", "lemon")]),
            ],
        ),
    },
    {
        "id": "aggregation", "title": "Aggregation & Window Functions", "category": "querying", "level": "intermediate", "code": "AG",
        "tagline": "GROUP BY summaries, HAVING filters and per-row analytics with OVER().",
        "analogy": "GROUP BY is sorting receipts into envelopes per month and writing the total on each envelope. A window function writes the running total on every receipt without merging them.",
        "what": "Aggregates (COUNT, SUM, AVG, MIN, MAX) collapse many rows into one per group. HAVING filters groups. Window functions compute over a set of rows related to the current row (PARTITION BY ... ORDER BY ...) without collapsing them: ranking (ROW_NUMBER, RANK, DENSE_RANK), running totals (SUM OVER), comparisons with neighbours (LAG/LEAD). CTEs (WITH) name intermediate results; recursive CTEs walk hierarchies.",
        "use_cases": ["Revenue per category.", "Top-N per group (best-selling product per category).", "Org chart traversal with a recursive CTE."],
        "key_points": [
            "Every selected column must be grouped or aggregated.",
            "COUNT(*) counts rows; COUNT(col) skips NULLs.",
            "ROW_NUMBER is unique; RANK leaves gaps on ties; DENSE_RANK does not.",
            "Window functions run after WHERE/GROUP BY, so filter on them in an outer query.",
        ],
        "examples": [
            ex("GROUP BY and HAVING", "basic", "Revenue per category, only categories above 1000.", "sql", """
                SELECT p.category, SUM(i.qty * i.unit_price) AS revenue, COUNT(DISTINCT i.order_id) AS orders
                FROM order_items i JOIN products p ON p.id = i.product_id
                GROUP BY p.category
                HAVING revenue > 1000
                ORDER BY revenue DESC;
            """),
            ex("Top earner per department", "intermediate", "RANK inside each department, then keep rank 1.", "sql", """
                WITH ranked AS (
                  SELECT name, dept, salary,
                         RANK() OVER (PARTITION BY dept ORDER BY salary DESC) AS rnk
                  FROM employees
                )
                SELECT dept, name, salary FROM ranked WHERE rnk = 1 ORDER BY dept;
            """),
            ex("Running total and recursive CTE", "advanced", "Cumulative revenue by day, then everyone reporting to the CTO.", "sql", """
                SELECT o.created_at, SUM(i.qty * i.unit_price) AS day_total,
                       SUM(SUM(i.qty * i.unit_price)) OVER (ORDER BY o.created_at) AS running
                FROM orders o JOIN order_items i ON i.order_id = o.id
                GROUP BY o.created_at ORDER BY o.created_at LIMIT 8;

                WITH RECURSIVE chain(id, name, depth) AS (
                  SELECT id, name, 0 FROM employees WHERE id = 1
                  UNION ALL
                  SELECT e.id, e.name, c.depth + 1 FROM employees e JOIN chain c ON e.manager_id = c.id
                )
                SELECT depth, name FROM chain ORDER BY depth, name;
            """),
        ],
        "commands": ["GROUP BY col HAVING SUM(x) > n", "ROW_NUMBER() OVER (PARTITION BY g ORDER BY x DESC)", "SUM(x) OVER (ORDER BY d ROWS UNBOUNDED PRECEDING)", "LAG(x) OVER (ORDER BY d)", "WITH RECURSIVE cte AS (...)"],
        "gotchas": ["AVG of integers may be integer division in some engines.", "COUNT(col) ignores NULLs, which can hide missing data.", "You cannot use a window function in WHERE; wrap it in a CTE."],
        "interview": [
            qa("intermediate", "Second highest salary?", "SELECT MAX(salary) FROM employees WHERE salary < (SELECT MAX(salary) FROM employees), or DENSE_RANK() OVER (ORDER BY salary DESC) = 2 which also handles ties."),
            qa("intermediate", "ROW_NUMBER vs RANK vs DENSE_RANK?", "On ties: ROW_NUMBER gives 1,2,3 arbitrarily; RANK gives 1,1,3; DENSE_RANK gives 1,1,2."),
            qa("advanced", "Top 3 products per category?", "ROW_NUMBER() OVER (PARTITION BY category ORDER BY sales DESC) in a CTE, then WHERE rn <= 3."),
            qa("advanced", "What is a recursive CTE used for?", "Walking hierarchies and graphs (org charts, folders, bill of materials) and generating series: an anchor query plus a recursive part joined to the CTE until no new rows."),
        ],
        "related": ["joins", "query-plans"],
        "flow": flow(
            [node("rows", "order_items", 14, 50, "sky", "28 rows"), node("g1", "electronics", 50, 22, "mint", "Σ revenue"), node("g2", "furniture", 50, 50, "lemon", "Σ revenue"),
             node("g3", "books", 50, 78, "peach", "Σ revenue"), node("having", "HAVING > 1000", 84, 50, "lilac", "filter groups")],
            [("rows", "g1"), ("rows", "g2"), ("rows", "g3"), ("g1", "having"), ("g2", "having"), ("g3", "having")],
            [
                step("Rows go into buckets", "<b>GROUP BY category</b> sends each line item to its category bucket.", ["rows"], [pkt("rows", "g1", "kbd"), pkt("rows", "g2", "desk"), pkt("rows", "g3", "book")]),
                step("Aggregate per bucket", "SUM, COUNT and AVG run once per group. 28 rows become 4 (grocery not shown).", ["g1", "g2", "g3"], set={"g1": {"sub": "Σ 1280"}, "g2": {"sub": "Σ 1391"}, "g3": {"sub": "Σ 397"}}),
                step("Filter groups", "<b>HAVING revenue > 1000</b> drops books. WHERE could not do this because sums do not exist yet.", ["having"], [pkt("g1", "having"), pkt("g2", "having"), pkt("g3", "having", "✕", "rose")], {"g3": {"tint": "slate"}}),
                step("Window functions keep rows", "<b>OVER (PARTITION BY ...)</b> computes per group but returns every row, e.g. rank within department.", ["rows"], set={"rows": {"sub": "rank on every row"}}),
            ],
        ),
    },
    {
        "id": "normalization", "title": "Normalization & Modeling", "category": "foundations", "level": "intermediate", "code": "NF",
        "tagline": "1NF to BCNF, and when to denormalize on purpose.",
        "analogy": "Writing a customer's address on every invoice means a move requires editing hundreds of invoices. Keep the address once on the customer card and point to it.",
        "what": "Normalization removes redundancy so each fact is stored once. 1NF: atomic values, no repeating groups. 2NF: no partial dependency on part of a composite key. 3NF: no transitive dependency (non-key → non-key). BCNF: every determinant is a key. Denormalization deliberately duplicates data (counters, snapshots, read models) to make reads cheap, accepting extra write work.",
        "use_cases": ["Splitting a spreadsheet export into customers, orders and items.", "Storing unit_price on order_items as a historical snapshot (intentional duplication).", "Materialized summary tables for dashboards."],
        "key_points": [
            "Anomalies: update (change in many places), insert (cannot add without unrelated data), delete (lose facts).",
            "OLTP schemas lean normalized; analytics (star schema) leans denormalized.",
            "Snapshot columns are not redundancy when the value is time-specific.",
            "Many-to-many needs a junction table.",
        ],
        "examples": [
            ex("Junction table", "basic", "Products per order through order_items (many-to-many).", "sql", """
                SELECT o.id AS order_id, GROUP_CONCAT(p.name, ', ') AS products
                FROM orders o
                JOIN order_items i ON i.order_id = o.id
                JOIN products p ON p.id = i.product_id
                GROUP BY o.id LIMIT 5;
            """),
            ex("Snapshot vs current price", "intermediate", "unit_price records what the customer paid; products.price can change later.", "sql", """
                UPDATE products SET price = 99.0 WHERE id = 1;
                SELECT i.order_id, p.name, i.unit_price AS paid, p.price AS current
                FROM order_items i JOIN products p ON p.id = i.product_id
                WHERE p.id = 1;
            """),
            ex("Denormalized summary table", "advanced", "A read model for dashboards, rebuilt from the normalized source.", "sql", """
                CREATE TABLE customer_stats AS
                SELECT c.id, c.name, COUNT(DISTINCT o.id) AS orders, COALESCE(SUM(i.qty * i.unit_price), 0) AS lifetime_value
                FROM customers c
                LEFT JOIN orders o ON o.customer_id = c.id AND o.status != 'cancelled'
                LEFT JOIN order_items i ON i.order_id = o.id
                GROUP BY c.id;
                SELECT * FROM customer_stats ORDER BY lifetime_value DESC LIMIT 5;
            """),
        ],
        "commands": ["CREATE TABLE a_b (a_id, b_id, PRIMARY KEY (a_id, b_id))", "CREATE TABLE summary AS SELECT ...", "CREATE MATERIALIZED VIEW mv AS ... (Postgres)"],
        "gotchas": ["Over-normalizing lookup data (a table for 'yes/no') adds joins for no gain.", "Denormalized copies drift unless one process owns updating them.", "JSON columns are convenient but hide structure from constraints and indexes."],
        "interview": [
            qa("intermediate", "Explain 1NF, 2NF and 3NF briefly.", "1NF: atomic columns, no repeating groups. 2NF: 1NF and every non-key column depends on the whole key. 3NF: 2NF and non-key columns depend only on the key, not on other non-key columns."),
            qa("intermediate", "When would you denormalize?", "When read latency or join cost dominates and the duplicated data has a clear owner to keep it in sync: counters, read models, analytics star schemas, caches."),
            qa("advanced", "Star schema vs normalized OLTP?", "Star schema: a fact table (events, sales) with denormalized dimension tables, optimized for scans and aggregations. OLTP: normalized for correctness of many small concurrent writes."),
            qa("basic", "How do you model many-to-many?", "A junction table with foreign keys to both sides and a composite primary key (or surrogate key plus UNIQUE)."),
        ],
        "related": ["relational-model", "aggregation"],
        "flow": flow(
            [node("flat", "orders_export.csv", 15, 50, "rose", "name, email, city, product…"), node("c", "customers", 60, 18, "sky", "once per customer"),
             node("o", "orders", 60, 50, "mint", "customer_id"), node("i", "order_items", 60, 82, "lemon", "order_id, product_id"), node("p", "products", 90, 82, "peach", "once per product")],
            [("o", "c"), ("i", "o"), ("i", "p")],
            [
                step("One flat table", "A spreadsheet repeats the customer's email and city on every row. Changing a city means editing many rows.", ["flat"]),
                step("Extract entities", "Customer facts move to <b>customers</b>, product facts to <b>products</b>.", ["c", "p"], [pkt("flat", "c", "customer"), pkt("flat", "p", "product")]),
                step("Relationships become keys", "orders point to customers; order_items is the junction between orders and products.", ["o", "i"], [pkt("flat", "o", "order"), pkt("flat", "i", "line")]),
                step("One fact, one place", "Now a city change is a single UPDATE. Read models can still be denormalized on purpose.", ["c"], set={"flat": {"tint": "slate", "sub": "replaced by 4 tables"}}),
            ],
        ),
    },
    {
        "id": "indexes", "title": "Indexes & B-Trees", "category": "performance", "level": "intermediate", "code": "IX",
        "tagline": "Turn full scans into lookups: B-trees, composite, covering and partial indexes.",
        "analogy": "The index at the back of a book. Instead of reading every page for 'B-tree', you jump to the entry and get page numbers. Every extra index is another index the author must update when the book changes.",
        "what": "An index is a separate sorted structure (usually a B+tree) mapping key values to row locations. Lookups go from O(n) scans to O(log n) seeks. Composite indexes sort by the first column, then the next (leftmost-prefix rule). A covering index contains every column the query needs, so the table is not touched. Indexes speed reads but cost writes, storage and memory.",
        "use_cases": ["Look up a user's events by user_id.", "Range queries on timestamps.", "Enforce uniqueness (unique index)."],
        "key_points": [
            "Leftmost prefix: an index on (a, b) helps WHERE a = ? and WHERE a = ? AND b = ?, not WHERE b = ?.",
            "Functions on the column (WHERE lower(email) = ?) bypass a plain index; use an expression index.",
            "Low-selectivity columns (boolean) rarely benefit alone.",
            "Hash indexes: equality only. B-trees: equality, ranges, ORDER BY.",
        ],
        "examples": [
            ex("Scan vs search", "intermediate", "Compare query plans before and after creating an index (turn on Explain).", "sql", """
                EXPLAIN QUERY PLAN SELECT COUNT(*) FROM events WHERE user_id = 42;
                CREATE INDEX ix_events_user ON events(user_id);
                EXPLAIN QUERY PLAN SELECT COUNT(*) FROM events WHERE user_id = 42;
            """),
            ex("Composite index and leftmost prefix", "advanced", "The (user_id, ts) index helps the first query, not the second.", "sql", """
                CREATE INDEX ix_user_ts ON events(user_id, ts);
                EXPLAIN QUERY PLAN SELECT * FROM events WHERE user_id = 7 AND ts > 1700300000;
                EXPLAIN QUERY PLAN SELECT * FROM events WHERE ts > 1700300000;
            """),
            ex("Expression and partial index", "advanced", "Index lower(email) for case-insensitive lookups, and only 'buy' events.", "sql", """
                CREATE INDEX ix_email_lower ON customers(lower(email));
                EXPLAIN QUERY PLAN SELECT * FROM customers WHERE lower(email) = 'asha@example.com';
                CREATE INDEX ix_buys ON events(user_id) WHERE kind = 'buy';
                EXPLAIN QUERY PLAN SELECT COUNT(*) FROM events WHERE kind = 'buy' AND user_id = 3;
            """),
        ],
        "commands": ["CREATE INDEX ix ON t(col)", "CREATE UNIQUE INDEX ux ON t(col)", "CREATE INDEX ix ON t(a, b) -- leftmost prefix", "CREATE INDEX ix ON t(lower(email))", "CREATE INDEX ix ON t(col) WHERE cond -- partial"],
        "gotchas": ["Indexes on every column slow every INSERT/UPDATE.", "Leading wildcard LIKE '%x' cannot use a B-tree.", "Implicit type casts (string vs int) can stop index use."],
        "interview": [
            qa("intermediate", "How does a B-tree index work?", "A balanced tree of sorted keys with high fan-out; internal nodes route, leaves hold keys plus row pointers and are linked for range scans. Depth stays ~3-4 even for millions of rows, so a lookup is a few page reads."),
            qa("intermediate", "What is a covering index?", "An index that contains every column the query reads, so the engine answers from the index alone (index-only scan) without visiting the table."),
            qa("advanced", "Why might the planner ignore your index?", "Low selectivity (it is cheaper to scan), stale statistics, a function or cast on the column, a non-leftmost column of a composite index, or OR conditions across columns."),
            qa("advanced", "Clustered vs secondary index?", "Clustered (InnoDB primary key) stores rows in key order, so the table is the index. Secondary indexes store the key plus a pointer (or the PK), requiring a second lookup unless covering."),
        ],
        "related": ["query-plans", "relational-model"],
        "flow": flow(
            [node("root", "root", 50, 12, "lilac", "[ 500 ]"), node("l", "inner", 25, 45, "sky", "[ 100 | 300 ]"), node("r", "inner", 75, 45, "sky", "[ 700 | 900 ]"),
             node("l1", "leaf", 10, 82, "mint", "1..99"), node("l2", "leaf", 30, 82, "mint", "100..299"), node("l3", "leaf", 50, 82, "mint", "300..499"),
             node("r1", "leaf", 70, 82, "mint", "500..699"), node("r2", "leaf", 90, 82, "mint", "700+")],
            [("root", "l"), ("root", "r"), ("l", "l1"), ("l", "l2"), ("l", "l3"), ("r", "r1"), ("r", "r2")],
            [
                step("Without an index", "WHERE user_id = 42 reads all 20,000 rows: a <b>full table scan</b>.", ["l1", "l2", "l3", "r1", "r2"]),
                step("Start at the root", "With a B-tree, compare 42 with the root key 500 and go left.", ["root"], [pkt("root", "l", "42 < 500")]),
                step("Route through inner nodes", "42 < 100, so take the first child.", ["l"], [pkt("l", "l1", "42 < 100")]),
                step("Read one leaf", "The leaf holds key 42 and pointers to its rows. 3 page reads instead of thousands.", ["l1"], set={"l1": {"sub": "42 → rows"}}),
                step("Range scans follow leaf links", "Leaves are linked, so <b>ts BETWEEN a AND b</b> walks neighbours in order.", ["l2", "l3"], [pkt("l1", "l2", "next"), pkt("l2", "l3", "next")]),
            ],
        ),
    },
    {
        "id": "query-plans", "title": "Query Plans & Optimization", "category": "performance", "level": "advanced", "code": "QP",
        "tagline": "Read EXPLAIN, spot full scans and fix slow queries methodically.",
        "analogy": "A GPS chooses a route from traffic data. EXPLAIN shows you the route it picked; stale statistics are an old map that sends you through a closed road.",
        "what": "The optimizer turns SQL into a plan: access paths (scan, index seek), join order and join algorithms, sorts and aggregations, chosen by estimated cost using table statistics. EXPLAIN shows the plan; EXPLAIN ANALYZE (Postgres/MySQL 8) runs it and shows actual rows and time. Fix slow queries by measuring first, then adding the right index, rewriting (sargable predicates, avoid SELECT *), or reshaping data.",
        "use_cases": ["A dashboard query that got slower as data grew.", "N+1 queries from an ORM.", "Sorting large results without an index."],
        "key_points": [
            "Look for: full scans on big tables, estimated vs actual row mismatches, temp B-tree sorts, nested loops over large inputs.",
            "Sargable: WHERE ts >= x can use an index; WHERE date(ts) = x usually cannot.",
            "ANALYZE keeps statistics fresh.",
            "The fastest query is the one you do not run: cache, batch, precompute.",
        ],
        "examples": [
            ex("Sort without and with an index", "intermediate", "USE TEMP B-TREE FOR ORDER BY disappears once an index provides the order.", "sql", """
                EXPLAIN QUERY PLAN SELECT * FROM events ORDER BY ts DESC LIMIT 10;
                CREATE INDEX ix_ts ON events(ts);
                EXPLAIN QUERY PLAN SELECT * FROM events ORDER BY ts DESC LIMIT 10;
            """),
            ex("Non-sargable predicate", "advanced", "Wrapping the column in arithmetic hides it from the index.", "sql", """
                CREATE INDEX ix_ts2 ON events(ts);
                EXPLAIN QUERY PLAN SELECT COUNT(*) FROM events WHERE ts + 0 > 1700500000;
                EXPLAIN QUERY PLAN SELECT COUNT(*) FROM events WHERE ts > 1700500000;
            """),
            ex("N+1 vs one query", "advanced", "One join replaces one query per order.", "sql", """
                -- N+1: SELECT * FROM order_items WHERE order_id = ? (once per order)
                SELECT o.id, COUNT(i.product_id) AS lines
                FROM orders o LEFT JOIN order_items i ON i.order_id = o.id
                GROUP BY o.id ORDER BY o.id LIMIT 10;
            """),
        ],
        "commands": ["EXPLAIN QUERY PLAN <query> (SQLite)", "EXPLAIN (ANALYZE, BUFFERS) <query> (Postgres)", "EXPLAIN ANALYZE <query> (MySQL 8)", "ANALYZE table", "pg_stat_statements: top queries by total time"],
        "gotchas": ["EXPLAIN ANALYZE actually runs the statement, including UPDATE/DELETE: wrap in a transaction and roll back.", "Optimizing a query that runs once a day while a 5 ms query runs a million times.", "Adding indexes without checking write impact."],
        "interview": [
            qa("advanced", "Walk me through debugging a slow query.", "Reproduce with real parameters, EXPLAIN ANALYZE, find the expensive node (scan, sort, bad join), compare estimated vs actual rows (stale stats?), add or adjust an index or rewrite the predicate, verify the new plan and measure under load."),
            qa("intermediate", "What is the N+1 problem?", "Fetching a list with one query and then each child with another query per row. Fix with a join, IN batch loading, or the ORM's eager loading."),
            qa("advanced", "What makes a predicate sargable?", "The indexed column stands alone on one side of a comparison (col op constant), so the engine can seek. Functions, arithmetic or casts on the column usually prevent that."),
            qa("advanced", "Why do estimated and actual row counts differ, and why care?", "Stale or coarse statistics, correlated columns, skewed data. Bad estimates lead the optimizer to the wrong join type or order, which is often the root cause of slow queries."),
        ],
        "related": ["indexes", "aggregation"],
        "flow": flow(
            [node("sql", "SQL", 10, 50, "slate", "SELECT …"), node("parse", "Parser", 30, 50, "sky", "syntax tree"), node("opt", "Optimizer", 52, 50, "lilac", "cost model"),
             node("stats", "Statistics", 52, 15, "lemon", "row counts, histograms"), node("plan", "Plan", 74, 50, "mint", "Index seek → sort"), node("exec", "Executor", 92, 50, "peach", "rows")],
            [("sql", "parse"), ("parse", "opt"), ("stats", "opt"), ("opt", "plan"), ("plan", "exec")],
            [
                step("Parse", "The query is parsed and names are resolved.", ["sql", "parse"], [pkt("sql", "parse", "text")]),
                step("Estimate costs", "The optimizer enumerates plans and estimates their cost using <b>statistics</b>.", ["opt", "stats"], [pkt("stats", "opt", "rows≈20k"), pkt("parse", "opt", "tree")]),
                step("Pick the cheapest plan", "Index seek on user_id beats a full scan when few rows match.", ["plan"], [pkt("opt", "plan", "seek")]),
                step("Execute and verify", "EXPLAIN ANALYZE shows actual rows and time per node, so you can spot bad estimates.", ["exec"], [pkt("plan", "exec", "rows")]),
            ],
        ),
    },
    {
        "id": "transactions-acid", "title": "Transactions & ACID", "category": "transactions", "level": "intermediate", "code": "TX",
        "tagline": "All-or-nothing changes that survive crashes and respect constraints.",
        "analogy": "A bank transfer is two entries in a ledger: debit Alice, credit Bob. ACID guarantees nobody ever sees money vanish halfway, even if the power cuts out.",
        "what": "A transaction groups statements into one unit. Atomicity: all or nothing (ROLLBACK undoes). Consistency: constraints hold before and after. Isolation: concurrent transactions do not see each other's partial work (to a chosen degree). Durability: once COMMIT returns, the change survives crashes, thanks to the write-ahead log (WAL) flushed to disk.",
        "use_cases": ["Money transfers.", "Placing an order and decrementing stock together.", "Multi-step migrations that must fully apply or not at all."],
        "key_points": [
            "Keep transactions short: long ones hold locks and bloat MVCC versions.",
            "Savepoints allow partial rollback inside a transaction.",
            "Autocommit runs every statement in its own transaction.",
            "Distributed transactions (2PC) are costly; prefer sagas/outbox across services.",
        ],
        "examples": [
            ex("Atomic transfer", "basic", "Move 100 from alice to bob in one transaction.", "sql", """
                BEGIN;
                UPDATE accounts SET balance = balance - 100 WHERE owner = 'alice';
                UPDATE accounts SET balance = balance + 100 WHERE owner = 'bob';
                COMMIT;
                SELECT owner, balance FROM accounts;
            """),
            ex("Constraint failure", "intermediate", "carol has 0: the CHECK constraint rejects the debit, so the transfer must roll back.", "sql", """
                BEGIN;
                UPDATE accounts SET balance = balance + 50 WHERE owner = 'bob';
                UPDATE accounts SET balance = balance - 50 WHERE owner = 'carol';
            """),
            ex("Savepoints", "advanced", "Undo only part of a transaction.", "sql", """
                BEGIN;
                UPDATE accounts SET balance = balance - 10 WHERE owner = 'alice';
                SAVEPOINT before_bonus;
                UPDATE accounts SET balance = balance + 1000 WHERE owner = 'bob';
                ROLLBACK TO before_bonus;
                COMMIT;
                SELECT owner, balance FROM accounts;
            """),
        ],
        "commands": ["BEGIN; ... COMMIT;", "ROLLBACK;", "SAVEPOINT name; ROLLBACK TO name;", "SELECT ... FOR UPDATE (lock rows, Postgres/MySQL)"],
        "gotchas": ["Catching an exception in app code but forgetting ROLLBACK leaves the transaction aborted.", "Calling external APIs inside a transaction holds locks for seconds.", "ORMs may open implicit transactions you did not expect."],
        "interview": [
            qa("basic", "Explain ACID.", "Atomicity: all or nothing. Consistency: invariants and constraints hold. Isolation: concurrent transactions behave as if separated (to the chosen level). Durability: committed data survives crashes."),
            qa("intermediate", "How does a database guarantee durability?", "Write-ahead logging: changes are appended to the WAL and fsynced before COMMIT returns; data pages are written later. After a crash, the log is replayed (redo) and incomplete transactions are undone."),
            qa("advanced", "How do you keep data consistent across microservices without 2PC?", "Sagas: a sequence of local transactions with compensating actions on failure, coordinated by orchestration or events. Use the transactional outbox pattern so the DB write and event publish are atomic."),
            qa("intermediate", "Why are long transactions harmful?", "They hold locks (blocking others), keep old MVCC versions alive (bloat, vacuum cannot clean), and increase conflict and deadlock probability."),
        ],
        "related": ["isolation-mvcc", "replication-sharding"],
        "flow": flow(
            [node("app", "App", 12, 50, "slate", "transfer 100"), node("tx", "Transaction", 40, 50, "lilac", "BEGIN"), node("wal", "WAL", 68, 20, "lemon", "append + fsync"),
             node("a", "alice", 68, 60, "sky", "500"), node("b", "bob", 68, 85, "sky", "300"), node("disk", "Data files", 92, 50, "mint", "written later")],
            [("app", "tx"), ("tx", "wal"), ("tx", "a"), ("tx", "b"), ("wal", "disk")],
            [
                step("BEGIN", "The app opens a transaction. Nothing is visible to others yet.", ["app", "tx"], [pkt("app", "tx", "BEGIN")]),
                step("Two updates", "Debit alice, credit bob, inside the same transaction.", ["a", "b"], [pkt("tx", "a", "−100"), pkt("tx", "b", "+100")], {"a": {"sub": "400 (uncommitted)"}, "b": {"sub": "400 (uncommitted)"}}),
                step("COMMIT writes the log", "COMMIT returns only after the WAL record is fsynced: <b>durability</b>.", ["wal"], [pkt("tx", "wal", "COMMIT")], {"tx": {"sub": "COMMIT"}}),
                step("Crash? Replay", "If the server crashes now, the WAL is replayed on restart, so both updates survive or neither does.", ["disk", "wal"], [pkt("wal", "disk", "redo")], {"a": {"sub": "400"}, "b": {"sub": "400"}}),
            ],
        ),
    },
    {
        "id": "isolation-mvcc", "title": "Isolation Levels, Locks & MVCC", "category": "transactions", "level": "advanced", "code": "IL",
        "tagline": "Dirty reads, lost updates, phantoms, and how MVCC and locks prevent them.",
        "analogy": "MVCC is a photocopy machine: each reader gets a snapshot of the document as of when they started, while writers work on new versions. Locks are a 'do not disturb' sign on a page.",
        "what": "Isolation levels trade anomalies for concurrency. Read Uncommitted allows dirty reads. Read Committed (Postgres default) sees only committed data but each statement may see a newer snapshot (non-repeatable reads). Repeatable Read / Snapshot Isolation (MySQL default) keeps one snapshot per transaction but can allow write skew. Serializable behaves like some serial order (SSI in Postgres aborts conflicting transactions). MVCC keeps row versions so readers do not block writers; locks (row, gap, predicate) serialize conflicting writes.",
        "use_cases": ["Preventing double-booking a seat.", "Stock decrement without overselling.", "Reports that need a consistent snapshot."],
        "key_points": [
            "Lost update fix: atomic UPDATE x = x - 1, SELECT ... FOR UPDATE, or optimistic version columns.",
            "Write skew: two transactions read the same condition and write different rows (on-call doctors).",
            "Serializable transactions may fail with serialization errors: retry them.",
            "Deadlocks: lock rows in a consistent order and keep transactions short.",
        ],
        "examples": [
            ex("Atomic decrement avoids lost updates", "intermediate", "Read-modify-write in app code can lose updates; a single UPDATE cannot.", "sql", """
                -- risky: SELECT balance, then UPDATE balance = <value computed in app>
                UPDATE accounts SET balance = balance - 30 WHERE owner = 'alice' AND balance >= 30;
                SELECT owner, balance FROM accounts WHERE owner = 'alice';
            """),
            ex("Optimistic concurrency with a version column", "advanced", "The second writer's UPDATE matches 0 rows because the version moved on.", "sql", """
                ALTER TABLE accounts ADD COLUMN version INTEGER NOT NULL DEFAULT 1;
                UPDATE accounts SET balance = 450, version = version + 1 WHERE owner = 'alice' AND version = 1;
                UPDATE accounts SET balance = 470, version = version + 1 WHERE owner = 'alice' AND version = 1;
                SELECT owner, balance, version FROM accounts WHERE owner = 'alice';
            """),
            ex("Pessimistic locking (Postgres)", "advanced", "Lock the row for the rest of the transaction.", "sql", """
                BEGIN ISOLATION LEVEL READ COMMITTED;
                SELECT balance FROM accounts WHERE owner = 'alice' FOR UPDATE;
                UPDATE accounts SET balance = balance - 30 WHERE owner = 'alice';
                COMMIT;
            """, runnable=False),
        ],
        "commands": ["SET TRANSACTION ISOLATION LEVEL SERIALIZABLE", "SELECT ... FOR UPDATE / FOR SHARE", "SELECT ... FOR UPDATE SKIP LOCKED (job queues)", "UPDATE t SET v = v + 1, version = version + 1 WHERE id = ? AND version = ?"],
        "gotchas": ["Assuming your database's default is Serializable: it almost never is.", "Repeatable Read in MySQL and Postgres differ in details (gap locks vs snapshot).", "Not retrying serialization failures turns safety into errors for users."],
        "interview": [
            qa("intermediate", "Name the read anomalies and which levels prevent them.", "Dirty read (prevented from Read Committed up), non-repeatable read (prevented from Repeatable Read), phantom read (prevented by Serializable; Postgres RR also prevents it). Write skew is only prevented by Serializable."),
            qa("advanced", "What is MVCC?", "Multi-version concurrency control: each write creates a new row version tagged with transaction ids; each transaction reads the versions visible to its snapshot. Readers never block writers; old versions are cleaned by vacuum/purge."),
            qa("advanced", "Explain write skew with an example.", "Two doctors on call; each transaction checks 'at least 2 on call' and removes itself. Both see 2, both commit, now 0 are on call. Snapshot isolation allows it; Serializable or locking the checked rows prevents it."),
            qa("advanced", "Optimistic vs pessimistic concurrency control?", "Optimistic: no locks, detect conflicts at write time (version column, SSI) and retry; great for low contention. Pessimistic: lock first (FOR UPDATE); better when conflicts are frequent or retries are expensive."),
            qa("intermediate", "How do you avoid deadlocks?", "Access rows/tables in a consistent order, keep transactions short, use appropriate indexes so fewer rows are locked, and retry the victim transaction."),
        ],
        "related": ["transactions-acid", "indexes"],
        "flow": flow(
            [node("t1", "T1", 15, 25, "sky", "snapshot @100"), node("t2", "T2", 15, 75, "peach", "writer"), node("v1", "row v1", 60, 25, "mint", "balance 500 (xmin 90)"),
             node("v2", "row v2", 60, 75, "lemon", "balance 400 (xmin 120)", hidden=True), node("vac", "vacuum", 90, 50, "slate", "cleans old versions")],
            [("t1", "v1"), ("t2", "v2"), ("v1", "vac")],
            [
                step("T1 takes a snapshot", "T1 starts at transaction id 100 and reads balance 500.", ["t1", "v1"], [pkt("v1", "t1", "500")]),
                step("T2 writes a new version", "T2 updates the row. MVCC creates <b>version 2</b> instead of overwriting.", ["t2", "v2"], [pkt("t2", "v2", "400")], {"v2": {"hidden": False}}),
                step("Readers are not blocked", "T1 reads again and still sees 500: its snapshot predates T2's commit (repeatable read).", ["t1", "v1"], [pkt("v1", "t1", "500 again")]),
                step("New readers see v2", "Transactions that start after T2 commits read 400. Under Read Committed, T1's next statement would too.", ["v2"], [pkt("v2", "t1", "400 (RC)", "lemon")]),
                step("Garbage collection", "When no snapshot needs v1, <b>vacuum</b> reclaims it. Long transactions delay this and cause bloat.", ["vac"], [pkt("v1", "vac", "reclaim")], {"v1": {"tint": "slate"}}),
            ],
        ),
    },
    {
        "id": "replication-sharding", "title": "Replication, Partitioning & Sharding", "category": "scale", "level": "advanced", "code": "RS",
        "tagline": "Copy data for availability and reads; split it for write scale.",
        "analogy": "Replication is photocopying the phone book for every branch office. Sharding is splitting it A–M and N–Z across two buildings: twice the capacity, but a search for everyone named 'Rao' must ask both.",
        "what": "Replication keeps copies on several nodes: single-leader (writes to primary, async or sync replicas for reads/failover), multi-leader, or leaderless (Dynamo-style quorums, W + R > N). Async replicas lag, causing stale reads. Partitioning splits a table by key; sharding spreads partitions across servers. Strategies: range (good for scans, risk of hot spots), hash (even spread, no range scans), directory/lookup. Rebalancing and cross-shard queries are the hard parts.",
        "use_cases": ["Read replicas for reporting traffic.", "Hot standby for automatic failover.", "Sharding users by user_id when one primary cannot take the writes."],
        "key_points": [
            "Read-your-writes: route a user's reads to the primary briefly after they write.",
            "Failover risks: split brain, losing un-replicated writes with async replication.",
            "Choose a shard key with high cardinality and even access; avoid monotonically increasing keys for range sharding.",
            "Consistent hashing reduces data movement when adding nodes.",
        ],
        "examples": [
            ex("Range partition by month (Postgres)", "intermediate", "Old partitions can be dropped instantly instead of DELETE.", "sql", """
                CREATE TABLE events (id bigint, user_id bigint, ts timestamptz NOT NULL)
                  PARTITION BY RANGE (ts);
                CREATE TABLE events_2024_06 PARTITION OF events
                  FOR VALUES FROM ('2024-06-01') TO ('2024-07-01');
            """, runnable=False),
            ex("Hash shard routing", "advanced", "Which shard owns each user if we have 4 shards? (modulo hashing)", "sql", """
                SELECT user_id, user_id % 4 AS shard, COUNT(*) AS events
                FROM events GROUP BY user_id ORDER BY user_id LIMIT 8;
            """),
            ex("Hot keys", "advanced", "Find users whose events would overload one shard.", "sql", """
                SELECT user_id, COUNT(*) AS n FROM events GROUP BY user_id ORDER BY n DESC LIMIT 5;
                SELECT user_id % 4 AS shard, COUNT(*) AS n FROM events GROUP BY shard;
            """),
        ],
        "commands": ["Postgres: CREATE PUBLICATION / SUBSCRIPTION (logical replication)", "SELECT * FROM pg_stat_replication; -- lag", "MySQL: SHOW REPLICA STATUS", "PARTITION BY RANGE | LIST | HASH"],
        "gotchas": ["Reading from an async replica right after a write shows stale data.", "Cross-shard joins and transactions become application problems.", "Resharding with modulo hashing moves almost all keys; plan for it early."],
        "interview": [
            qa("intermediate", "Sync vs async replication?", "Sync: commit waits for a replica ack, so no data loss on failover but higher latency and availability depends on the replica. Async: fast commits, but a failover can lose the latest writes and replicas lag."),
            qa("advanced", "How do you pick a shard key?", "High cardinality, even distribution, and aligned with the dominant access pattern so most queries hit one shard (e.g. tenant_id). Avoid keys that create hot spots (timestamps for range sharding, celebrity users)."),
            qa("advanced", "Explain quorum reads and writes.", "With N replicas, writes wait for W acks and reads query R replicas. If W + R > N, read and write sets overlap, so reads see the latest write (with conflict resolution such as versions)."),
            qa("advanced", "How do you handle a celebrity hot key?", "Split the key (salting into sub-keys), cache aggressively, separate fan-out paths, or move hot tenants to dedicated shards."),
        ],
        "related": ["nosql-cap", "transactions-acid"],
        "flow": flow(
            [node("app", "App", 10, 50, "slate", "reads + writes"), node("p", "Primary", 42, 30, "lilac", "writes", "db"), node("r1", "Replica 1", 74, 15, "sky", "reads", "db"),
             node("r2", "Replica 2", 74, 45, "sky", "reads", "db"), node("s1", "Shard A", 42, 82, "mint", "user_id % 2 = 0", "db", True), node("s2", "Shard B", 74, 82, "peach", "user_id % 2 = 1", "db", True)],
            [("app", "p"), ("p", "r1"), ("p", "r2"), ("app", "r1"), ("app", "r2")],
            [
                step("Writes go to the primary", "Single-leader replication: every write lands on the primary first.", ["app", "p"], [pkt("app", "p", "INSERT")]),
                step("Changes stream to replicas", "The WAL/binlog is shipped to replicas, usually asynchronously.", ["r1", "r2"], [pkt("p", "r1", "WAL"), pkt("p", "r2", "WAL")]),
                step("Reads scale out", "Reads go to replicas, but may be slightly stale (replication lag).", ["r1", "r2"], [pkt("r1", "app", "rows"), pkt("r2", "app", "rows")]),
                step("Writes outgrow one primary", "Shard by key: each shard owns part of the users and has its own primary.", ["s1", "s2"], [pkt("app", "s1", "user 42"), pkt("app", "s2", "user 7")], {"s1": {"hidden": False}, "s2": {"hidden": False}}),
            ],
        ),
    },
    {
        "id": "nosql-cap", "title": "NoSQL Models & CAP", "category": "scale", "level": "intermediate", "code": "NS",
        "tagline": "Key-value, document, wide-column and graph stores, and the trade-offs they make.",
        "analogy": "Tools in a kitchen: a knife (key-value) is fast for one job, a food processor (document) handles mixed ingredients, a spice rack by row (wide-column) suits huge append-heavy data, and a recipe web (graph) connects everything.",
        "what": "NoSQL databases relax the relational model for scale or flexibility. Key-value (Redis, DynamoDB): O(1) lookups by key. Document (MongoDB): JSON documents, good when data is read as a whole. Wide-column (Cassandra): partitions of sorted rows, massive write throughput, query-driven modelling. Graph (Neo4j): relationships are first-class. CAP: during a network partition you must choose consistency or availability; PACELC adds that without partitions you trade latency vs consistency.",
        "use_cases": ["Session store and caching (key-value).", "Product catalogue with varied attributes (document).", "Time-series and event logs at scale (wide-column).", "Recommendations and fraud rings (graph)."],
        "key_points": [
            "Model NoSQL around queries, not entities; denormalize for read paths.",
            "DynamoDB: partition key + sort key; design single-table access patterns.",
            "Many NoSQL stores now offer transactions and secondary indexes, with limits.",
            "Polyglot persistence: use more than one store when the access patterns differ.",
        ],
        "examples": [
            ex("JSON in a relational database", "intermediate", "SQLite's JSON functions show the document-style trade-off.", "sql", """
                CREATE TABLE docs (id INTEGER PRIMARY KEY, body TEXT);
                INSERT INTO docs (body) VALUES
                  ('{"name":"Keyboard","specs":{"switch":"brown","layout":"US"}}'),
                  ('{"name":"Chair","specs":{"colour":"black"}}');
                SELECT json_extract(body, '$.name') AS name, json_extract(body, '$.specs.switch') AS switch FROM docs;
            """),
            ex("Key-value access pattern", "basic", "What a key-value lookup looks like in SQL terms.", "sql", """
                CREATE TABLE kv (k TEXT PRIMARY KEY, v TEXT, expires_at INTEGER);
                INSERT INTO kv VALUES ('session:abc', '{"user":1}', 1999999999);
                SELECT v FROM kv WHERE k = 'session:abc';
            """),
            ex("Cassandra table designed for one query", "advanced", "Partition by user, cluster by time, so 'latest events of user X' is one partition read.", "sql", """
                CREATE TABLE events_by_user (
                  user_id uuid, ts timeuuid, kind text,
                  PRIMARY KEY ((user_id), ts)
                ) WITH CLUSTERING ORDER BY (ts DESC);
            """, runnable=False),
        ],
        "commands": ["Redis: SET key value EX 3600 / GET key", "MongoDB: db.products.find({ 'specs.switch': 'brown' })", "DynamoDB: Query PK = USER#1 AND begins_with(SK, 'ORDER#')", "Cassandra: PRIMARY KEY ((partition), clustering)"],
        "gotchas": ["Choosing NoSQL for 'scale' and then needing joins everywhere.", "Unbounded partitions (one hot partition key) in Cassandra/DynamoDB.", "Treating eventual consistency as instant in UI flows."],
        "interview": [
            qa("intermediate", "Explain the CAP theorem.", "In a network partition, a distributed store must choose between consistency (every read sees the latest write, or errors) and availability (every request gets a response, possibly stale). Without partitions you can have both; PACELC adds the latency-consistency trade-off."),
            qa("intermediate", "When would you choose a document database over SQL?", "When entities are read and written as a whole, schemas vary per item, and relationships are few. If you need ad-hoc joins and strong multi-row constraints, SQL fits better."),
            qa("advanced", "How do you model in DynamoDB?", "Start from access patterns, pick partition and sort keys so each pattern is a Query on one partition, use GSIs for alternate patterns, and often store several entity types in one table with prefixed keys."),
            qa("advanced", "Strong vs eventual consistency in practice?", "Strong: reads reflect the latest committed write (higher latency, less availability across regions). Eventual: replicas converge over time; fine for feeds and counters, risky for balances or inventory."),
        ],
        "related": ["replication-sharding", "relational-model"],
        "flow": flow(
            [node("q", "Query", 10, 50, "slate", "access pattern"), node("kv", "Key-value", 45, 14, "sky", "GET session:abc"), node("doc", "Document", 45, 38, "mint", "{ name, specs }"),
             node("wc", "Wide-column", 45, 62, "lemon", "partition → sorted rows"), node("g", "Graph", 45, 86, "lilac", "(user)-[:FOLLOWS]->(user)"),
             node("n1", "Node A", 82, 30, "peach", "replica", "db"), node("n2", "Node B", 82, 72, "peach", "replica", "db")],
            [("q", "kv"), ("q", "doc"), ("q", "wc"), ("q", "g"), ("n1", "n2")],
            [
                step("Start from the query", "NoSQL modelling begins with how data is read, not with entities.", ["q"]),
                step("Pick the model", "Lookups by id → key-value. Whole objects → document. Huge time-ordered writes → wide-column. Relationships → graph.", ["kv", "doc", "wc", "g"], [pkt("q", "kv"), pkt("q", "doc"), pkt("q", "wc"), pkt("q", "g")]),
                step("Replicas talk", "Distributed stores replicate across nodes.", ["n1", "n2"], [pkt("n1", "n2", "replicate")]),
                step("Partition: choose C or A", "If the link breaks, a CP system rejects some requests; an AP system answers with possibly stale data.", ["n1", "n2"], [pkt("n1", "n2", "✕", "rose")], {"n2": {"sub": "stale or unavailable?"}}),
            ],
        ),
    },
]

SCENARIOS = [
    {"level": "intermediate", "topic": "indexes", "q": "A query filtering on created_at got 50× slower after the table reached 10M rows. What do you do?", "a": "EXPLAIN ANALYZE it. Likely a sequential scan or a non-sargable predicate (date(created_at) = ...). Add or fix an index on created_at (or a composite matching the WHERE + ORDER BY), rewrite the predicate as a range, refresh statistics, and confirm the new plan."},
    {"level": "advanced", "topic": "isolation-mvcc", "q": "Customers are occasionally charged twice for the same order under load.", "a": "A race between check and write (lost update / duplicate insert). Add an idempotency key with a UNIQUE constraint, make the payment insert conditional, or lock the order row (SELECT ... FOR UPDATE) during the payment step. Retry on serialization failures."},
    {"level": "advanced", "topic": "replication-sharding", "q": "Users update their profile and immediately see the old value.", "a": "Reads are served by lagging async replicas. Provide read-your-writes: route the user's reads to the primary for a short window after a write, or wait for the replica to reach the write's LSN, or use synchronous replication for that path."},
    {"level": "intermediate", "topic": "transactions-acid", "q": "Postgres disk usage keeps growing even though row counts are flat.", "a": "MVCC bloat: dead tuples not being vacuumed, often due to a long-running or idle-in-transaction session holding an old snapshot. Find it in pg_stat_activity, end it, tune autovacuum, and consider VACUUM (FULL) or pg_repack for heavily bloated tables."},
    {"level": "basic", "topic": "joins", "q": "A revenue report doubled overnight, but sales didn't.", "a": "A new join introduced fan-out (one-to-many, e.g. joining payments and items together), so each row is counted multiple times. Aggregate each child table in a subquery before joining, or use COUNT(DISTINCT) carefully."},
]

from .db_more import CATEGORIES as _MORE_CATEGORIES, SCENARIOS as _MORE_SCENARIOS, TOPICS as _MORE_TOPICS

CATEGORIES += _MORE_CATEGORIES
TOPICS += _MORE_TOPICS
SCENARIOS += _MORE_SCENARIOS
