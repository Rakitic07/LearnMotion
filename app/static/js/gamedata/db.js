export const WORDS = [
  { answer: "TABLE", term: "Table", clue: "A relation: a set of rows that all share the same columns" },
  { answer: "ROW", term: "Row", clue: "One record in a table, also called a tuple" },
  { answer: "COLUMN", term: "Column", clue: "A named, typed attribute shared by every row" },
  { answer: "SCHEMA", term: "Schema", clue: "The structure of a database: its tables, columns, types and constraints" },
  { answer: "PRIMARYKEY", term: "Primary key", clue: "A column (or set of columns) that uniquely identifies each row" },
  { answer: "FOREIGNKEY", term: "Foreign key", clue: "A column whose values must exist in another table's key" },
  { answer: "JOIN", term: "JOIN", clue: "Combines rows from two tables using a matching condition" },
  { answer: "INNER", term: "INNER JOIN", clue: "Join kind that keeps only rows with a match on both sides" },
  { answer: "LEFT", term: "LEFT JOIN", clue: "Join kind that keeps every row of the first table, filling NULLs" },
  { answer: "NULL", term: "NULL", clue: "Marker for an unknown or missing value; never equals anything" },
  { answer: "WHERE", term: "WHERE", clue: "Clause that filters rows before grouping" },
  { answer: "HAVING", term: "HAVING", clue: "Clause that filters groups after aggregation" },
  { answer: "GROUPBY", term: "GROUP BY", clue: "Collapses rows that share values into one row per group" },
  { answer: "INDEX", term: "Index", clue: "Extra sorted structure that turns a scan into a quick lookup" },
  { answer: "BTREE", term: "B-tree", clue: "Balanced tree used by most database indexes; supports ranges" },
  { answer: "SCAN", term: "Full table scan", clue: "Query plan step that reads every row of a table" },
  { answer: "EXPLAIN", term: "EXPLAIN", clue: "Shows the plan the database will use to run a query" },
  { answer: "TRANSACTION", term: "Transaction", clue: "A group of statements that succeed or fail as one unit" },
  { answer: "ATOMIC", term: "Atomicity", clue: "The A in ACID: all or nothing" },
  { answer: "DURABLE", term: "Durability", clue: "The D in ACID: committed data survives a crash" },
  { answer: "COMMIT", term: "COMMIT", clue: "Makes a transaction's changes permanent and visible" },
  { answer: "ROLLBACK", term: "ROLLBACK", clue: "Discards everything the current transaction changed" },
  { answer: "MVCC", term: "MVCC", clue: "Concurrency scheme where writers create new row versions so readers never block" },
  { answer: "SNAPSHOT", term: "Snapshot", clue: "Consistent view of the data as of a moment, used by repeatable read" },
  { answer: "DEADLOCK", term: "Deadlock", clue: "Two transactions each wait for a lock the other holds" },
  { answer: "PHANTOM", term: "Phantom read", clue: "Anomaly where a re-run range query returns new rows" },
  { answer: "NORMALIZATION", term: "Normalization", clue: "Splitting tables so each fact is stored exactly once" },
  { answer: "DENORMALIZE", term: "Denormalize", clue: "Deliberately duplicate data to make reads faster" },
  { answer: "REPLICA", term: "Replica", clue: "Copy of a database that follows the primary and serves reads" },
  { answer: "SHARD", term: "Shard", clue: "One horizontal partition of data, living on its own server" },
  { answer: "WAL", term: "Write-ahead log", clue: "Log written before data pages, enabling crash recovery and replication" },
  { answer: "CAP", term: "CAP theorem", clue: "During a network partition you must choose consistency or availability" },
  { answer: "VIEW", term: "View", clue: "A stored query that behaves like a virtual table" },
  { answer: "CTE", term: "CTE", clue: "WITH-clause named subquery; can be recursive" },
];

export const RUSH = [
  { task: "Customers who have never ordered", answer: "LEFT JOIN orders … WHERE o.id IS NULL", wrong: ["INNER JOIN orders … WHERE o.id IS NULL", "LEFT JOIN orders … WHERE o.id = NULL", "RIGHT JOIN customers … HAVING COUNT(*) = 0"] },
  { task: "Keep only categories with revenue over 1000", answer: "GROUP BY category HAVING SUM(total) > 1000", wrong: ["WHERE SUM(total) > 1000 GROUP BY category", "GROUP BY category WHERE SUM(total) > 1000", "ORDER BY SUM(total) > 1000"] },
  { task: "Rank orders per customer by date", answer: "ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY created_at)", wrong: ["RANK() GROUP BY customer_id", "COUNT(*) OVER (ORDER BY customer_id)", "ROW_NUMBER() PARTITION customer_id"] },
  { task: "Speed up WHERE email = ?", answer: "CREATE INDEX idx_email ON customers(email)", wrong: ["ALTER TABLE customers SORT BY email", "CREATE VIEW v AS SELECT email FROM customers", "ANALYZE customers(email) FAST"] },
  { task: "Best index for WHERE status = ? ORDER BY created_at", answer: "(status, created_at)", wrong: ["(created_at, status)", "(created_at) only", "separate indexes on each, always"] },
  { task: "Transfer money atomically", answer: "BEGIN; UPDATE …; UPDATE …; COMMIT;", wrong: ["UPDATE …; UPDATE …; SAVE;", "LOCK TABLE; UPDATE …; UNLOCK;", "INSERT … ON CONFLICT DO NOTHING"] },
  { task: "Prevent the lost-update race on a counter", answer: "UPDATE t SET n = n + 1 WHERE id = 1", wrong: ["SELECT n, then UPDATE t SET n = :n + 1", "Use READ UNCOMMITTED", "Add an index on n"] },
  { task: "Isolation level that blocks write skew", answer: "SERIALIZABLE", wrong: ["READ COMMITTED", "REPEATABLE READ (snapshot)", "READ UNCOMMITTED"] },
  { task: "Count rows where a column is NULL", answer: "WHERE col IS NULL", wrong: ["WHERE col = NULL", "WHERE col == NULL", "WHERE NULL(col)"] },
  { task: "Insert or update if the key exists (Postgres / SQLite)", answer: "INSERT … ON CONFLICT (id) DO UPDATE SET …", wrong: ["INSERT OR MERGE …", "UPDATE … IF NOT EXISTS INSERT", "UPSERT INTO … KEY id"] },
  { task: "Pagination that stays fast deep into the list", answer: "WHERE id > :last_id ORDER BY id LIMIT 20", wrong: ["LIMIT 20 OFFSET 100000", "ORDER BY RANDOM() LIMIT 20", "SELECT * then slice in the app"] },
  { task: "Show how a query will run", answer: "EXPLAIN QUERY PLAN SELECT …", wrong: ["DESCRIBE SELECT …", "SHOW PLAN …", "TRACE SELECT …"] },
  { task: "Scale reads for a read-heavy app first", answer: "Add read replicas (and a cache)", wrong: ["Shard by user id immediately", "Switch to SERIALIZABLE", "Drop all indexes"] },
  { task: "Pick a shard key", answer: "High cardinality, even spread, matches the main access pattern", wrong: ["A boolean column", "created_at, so new data lands together", "Whatever column is first"] },
  { task: "During a partition, a CP store will…", answer: "Refuse some requests to stay consistent", wrong: ["Accept writes on both sides", "Lose committed data", "Switch to eventual consistency silently"] },
  { task: "Remove a transitive dependency (3NF)", answer: "Move the dependent columns to their own table", wrong: ["Add a composite primary key", "Add more indexes", "Store the values as JSON"] },
  { task: "Running total of revenue by day", answer: "SUM(total) OVER (ORDER BY day)", wrong: ["SUM(total) GROUP BY day", "COUNT(total) OVER (PARTITION BY day)", "CUMSUM(total)"] },
  { task: "Wide-column store built for huge write volume", answer: "Cassandra", wrong: ["SQLite", "Redis", "Neo4j"] },
];

export const BUGS = [
  {
    symptom: "Customers without any orders are missing from the report.",
    lang: "sql",
    code: `SELECT c.name, COUNT(o.id) AS orders
FROM customers c
JOIN orders o ON o.customer_id = c.id
GROUP BY c.id
ORDER BY orders DESC;`,
    bug: [2],
    why: "An inner JOIN drops customers with no matching orders. Use LEFT JOIN so they appear with COUNT(o.id) = 0.",
  },
  {
    symptom: "Error: misuse of aggregate function SUM().",
    lang: "sql",
    code: `SELECT category, SUM(price) AS revenue
FROM products
WHERE SUM(price) > 500
GROUP BY category;`,
    bug: [2],
    why: "WHERE filters rows before grouping, so aggregates are not available yet. Filter groups with HAVING SUM(price) > 500 after GROUP BY.",
  },
  {
    symptom: "The query returns no rows even though some customers have no city.",
    lang: "sql",
    code: `SELECT id, name
FROM customers
WHERE city = NULL;`,
    bug: [2],
    why: "Nothing equals NULL, not even NULL: the comparison is unknown. Use WHERE city IS NULL.",
  },
  {
    symptom: "Every transfer sometimes loses money under load.",
    lang: "python",
    code: `def transfer(db, src, dst, amount):
    bal = db.one("SELECT balance FROM accounts WHERE id = ?", src)
    db.run("UPDATE accounts SET balance = ? WHERE id = ?", bal - amount, src)
    db.run("UPDATE accounts SET balance = balance + ? WHERE id = ?", amount, dst)
    db.commit()`,
    bug: [2],
    why: "Read-modify-write in the app: two concurrent transfers read the same balance and one update is lost. Use SET balance = balance - ? (atomic in the database), or SELECT … FOR UPDATE inside a transaction.",
  },
  {
    symptom: "This lookup does a full scan despite the index on (last_name, first_name).",
    lang: "sql",
    code: `CREATE INDEX idx_name ON employees(last_name, first_name);

SELECT *
FROM employees
WHERE first_name = 'Ada';`,
    bug: [4],
    why: "A composite index is sorted by its leftmost column first. Filtering only on first_name cannot use it; filter on last_name too or add an index that starts with first_name.",
  },
  {
    symptom: "Page 5,000 of the order history takes seconds to load.",
    lang: "sql",
    code: `SELECT id, total, created_at
FROM orders
ORDER BY created_at DESC
LIMIT 20 OFFSET 100000;`,
    bug: [3],
    why: "OFFSET still reads and throws away 100,000 rows. Use keyset pagination: WHERE created_at < :last_seen ORDER BY created_at DESC LIMIT 20.",
  },
  {
    symptom: "Orders reference customers that were deleted months ago.",
    lang: "sql",
    code: `CREATE TABLE orders (
  id INTEGER PRIMARY KEY,
  customer_id INTEGER NOT NULL,
  total REAL NOT NULL CHECK (total >= 0),
  created_at TEXT NOT NULL
);`,
    bug: [2],
    why: "customer_id has no FOREIGN KEY, so the database cannot stop orphans. Add REFERENCES customers(id) (with ON DELETE RESTRICT or CASCADE).",
  },
];

export const META = {
  rushLabel: "SQL Rush",
  rushIntro: "Pick the SQL or design choice that does the job.",
  rushMono: false,
  bugLabel: "Query Bug Hunt",
  bugNoun: "symptom",
};
