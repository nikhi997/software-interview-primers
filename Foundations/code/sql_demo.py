"""
sql_demo.py — Foundations track, runnable with Python's stdlib `sqlite3`.
No installation needed (sqlite3 ships with Python).

Demonstrates the concepts from chapters 1-3:
  - creating tables with a primary key / foreign key
  - INNER JOIN and LEFT JOIN ("customers who never ordered")
  - GROUP BY with aggregates, and HAVING
  - a window function (ROW_NUMBER for "top N per group")  [SQLite 3.25+]
  - how an INDEX changes the query plan (EXPLAIN QUERY PLAN)

Run:  python3 sql_demo.py
"""

import sqlite3


def build_db():
    # In-memory database so the demo leaves no files behind.
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()

    cur.executescript(
        """
        CREATE TABLE customers (
            id      INTEGER PRIMARY KEY,
            name    TEXT NOT NULL,
            country TEXT NOT NULL
        );

        CREATE TABLE orders (
            id          INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            total       REAL    NOT NULL,
            status      TEXT    NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        );
        """
    )

    customers = [
        (1, "Ada", "UK"),
        (2, "Bjarne", "Denmark"),
        (3, "Grace", "USA"),
        (4, "Linus", "Finland"),   # will have NO orders -> tests LEFT JOIN
    ]
    orders = [
        (1, 1, 120.0, "completed"),
        (2, 1, 80.0, "completed"),
        (3, 1, 50.0, "cancelled"),
        (4, 2, 200.0, "completed"),
        (5, 3, 30.0, "completed"),
        (6, 3, 30.0, "completed"),
        (7, 3, 500.0, "completed"),
    ]
    cur.executemany("INSERT INTO customers VALUES (?, ?, ?)", customers)
    cur.executemany("INSERT INTO orders VALUES (?, ?, ?, ?)", orders)
    conn.commit()
    return conn


def section(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def main():
    conn = build_db()
    cur = conn.cursor()

    # --- 1. INNER JOIN: each order paired with its customer -------------
    section("INNER JOIN — orders with their customer")
    cur.execute(
        """
        SELECT c.name, o.total, o.status
        FROM customers c
        JOIN orders o ON o.customer_id = c.id
        ORDER BY c.name, o.total DESC
        """
    )
    for name, total, status in cur.fetchall():
        print(f"  {name:8} {total:7.2f}  {status}")

    # --- 2. LEFT JOIN: customers who never ordered ---------------------
    section("LEFT JOIN — customers who NEVER ordered")
    cur.execute(
        """
        SELECT c.name
        FROM customers c
        LEFT JOIN orders o ON o.customer_id = c.id
        WHERE o.id IS NULL
        """
    )
    for (name,) in cur.fetchall():
        print(f"  {name} has no orders")

    # --- 3. GROUP BY + HAVING: revenue per customer over a threshold ---
    section("GROUP BY + HAVING — completed revenue per customer > 100")
    cur.execute(
        """
        SELECT c.name, SUM(o.total) AS revenue
        FROM customers c
        JOIN orders o ON o.customer_id = c.id
        WHERE o.status = 'completed'      -- filter rows BEFORE grouping
        GROUP BY c.id
        HAVING SUM(o.total) > 100         -- filter groups AFTER aggregating
        ORDER BY revenue DESC
        """
    )
    for name, revenue in cur.fetchall():
        print(f"  {name:8} revenue = {revenue:.2f}")

    # --- 4. Window function: top 2 orders per customer ----------------
    section("WINDOW FUNCTION — top 2 orders per customer (ROW_NUMBER)")
    try:
        cur.execute(
            """
            WITH ranked AS (
                SELECT c.name, o.total,
                       ROW_NUMBER() OVER (
                           PARTITION BY o.customer_id
                           ORDER BY o.total DESC
                       ) AS rn
                FROM customers c
                JOIN orders o ON o.customer_id = c.id
            )
            SELECT name, total FROM ranked WHERE rn <= 2
            ORDER BY name, total DESC
            """
        )
        for name, total in cur.fetchall():
            print(f"  {name:8} {total:7.2f}")
    except sqlite3.OperationalError as exc:
        print(f"  (window functions need SQLite 3.25+; skipped: {exc})")

    # --- 5. Indexes change the query plan -----------------------------
    section("EXPLAIN QUERY PLAN — before vs after adding an index")
    query = "SELECT * FROM orders WHERE customer_id = 3"

    print("  BEFORE index:")
    for row in cur.execute("EXPLAIN QUERY PLAN " + query).fetchall():
        print("   ", row[-1])  # the human-readable detail column

    cur.execute("CREATE INDEX idx_orders_customer ON orders(customer_id)")

    print("  AFTER  index:")
    for row in cur.execute("EXPLAIN QUERY PLAN " + query).fetchall():
        print("   ", row[-1])

    print(
        "\n  Note how the plan changes from a SCAN (read every row) to a\n"
        "  SEARCH USING INDEX — the same speedup an index gives a real database."
    )

    conn.close()


if __name__ == "__main__":
    main()
