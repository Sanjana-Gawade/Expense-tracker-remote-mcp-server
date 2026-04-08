from mcp.server.fastmcp import FastMCP
import os
import aiosqlite
import tempfile

# DO NOT hardcode host/port for cloud
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# Use temp directory (safe for cloud)
TEMP_DIR = tempfile.gettempdir()
DB_PATH = os.path.join(TEMP_DIR, "expenses.db")
CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "categories.json")

print(f"[STARTUP] Database path: {DB_PATH}")

mcp = FastMCP("ExpenseTracker")


# ---------- DB INIT ----------
def init_db():
    try:
        import sqlite3
        with sqlite3.connect(DB_PATH) as c:
            c.execute("PRAGMA journal_mode=WAL")
            c.execute("""
                CREATE TABLE IF NOT EXISTS expenses(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    subcategory TEXT DEFAULT '',
                    note TEXT DEFAULT ''
                )
            """)
            c.execute("INSERT OR IGNORE INTO expenses(date, amount, category) VALUES ('2000-01-01', 0, 'test')")
            c.execute("DELETE FROM expenses WHERE category = 'test'")
        print("[STARTUP] Database initialized successfully")
    except Exception as e:
        print(f"[ERROR] DB Init Failed: {e}")
        raise


init_db()


# ---------- TOOLS ----------
@mcp.tool()
async def add_expense(date, amount, category, subcategory="", note=""):
    """Add a new expense entry to the database."""
    try:
        async with aiosqlite.connect(DB_PATH) as c:
            cur = await c.execute(
                "INSERT INTO expenses(date, amount, category, subcategory, note) VALUES (?,?,?,?,?)",
                (date, amount, category, subcategory, note)
            )
            await c.commit()
            return {
                "status": "success",
                "id": cur.lastrowid,
                "message": "Expense added successfully"
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
async def list_expenses(start_date, end_date):
    """List expenses between dates."""
    try:
        async with aiosqlite.connect(DB_PATH) as c:
            cur = await c.execute("""
                SELECT id, date, amount, category, subcategory, note
                FROM expenses
                WHERE date BETWEEN ? AND ?
                ORDER BY date DESC, id DESC
            """, (start_date, end_date))

            cols = [d[0] for d in cur.description]
            rows = await cur.fetchall()
            return [dict(zip(cols, r)) for r in rows]
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
async def summarize(start_date, end_date, category=None):
    """Summarize expenses."""
    try:
        async with aiosqlite.connect(DB_PATH) as c:
            query = """
                SELECT category, SUM(amount) as total_amount, COUNT(*) as count
                FROM expenses
                WHERE date BETWEEN ? AND ?
            """
            params = [start_date, end_date]

            if category:
                query += " AND category = ?"
                params.append(category)

            query += " GROUP BY category ORDER BY total_amount DESC"

            cur = await c.execute(query, params)
            cols = [d[0] for d in cur.description]
            rows = await cur.fetchall()
            return [dict(zip(cols, r)) for r in rows]
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ---------- RESOURCE ----------
@mcp.resource("expense:///categories", mime_type="application/json")
def categories():
    try:
        default_categories = {
            "categories": [
                "Food & Dining",
                "Transportation",
                "Shopping",
                "Entertainment",
                "Bills & Utilities",
                "Healthcare",
                "Travel",
                "Education",
                "Business",
                "Other"
            ]
        }

        try:
            with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            import json
            return json.dumps(default_categories, indent=2)

    except Exception as e:
        return f'{{"error": "{str(e)}"}}'

