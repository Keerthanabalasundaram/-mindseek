import sqlite3
import os
import json
from datetime import datetime

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mindseek.db")

def get_connection(db_path=DEFAULT_DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path=DEFAULT_DB_PATH):
    """Auto-creates SQLite database and required tables if they do not exist."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS papers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            methodology TEXT,
            dataset TEXT,
            accuracy REAL,
            extracted_text TEXT,
            github_repos TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comparisons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            paper_ids TEXT NOT NULL,
            report_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()

def get_or_create_user(name: str, email: str, db_path=DEFAULT_DB_PATH):
    """Fetches existing user by email or creates a new user."""
    init_db(db_path)
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE LOWER(email) = LOWER(?)", (email.strip(),))
    row = cursor.fetchone()

    if row:
        user = dict(row)
        if not user.get("name") and name:
            cursor.execute("UPDATE users SET name = ? WHERE id = ?", (name.strip(), user["id"]))
            conn.commit()
            user["name"] = name.strip()
    else:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO users (name, email, created_at) VALUES (?, ?, ?)", 
                       (name.strip(), email.strip(), now))
        conn.commit()
        user_id = cursor.lastrowid
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = dict(cursor.fetchone())

    conn.close()
    return user

def save_paper(user_id: int, filename: str, methodology: str, dataset: str, accuracy: float, 
               extracted_text: str, github_repos, db_path=DEFAULT_DB_PATH) -> int:
    """Saves extracted paper analysis to the database."""
    init_db(db_path)
    conn = get_connection(db_path)
    cursor = conn.cursor()

    if not isinstance(github_repos, str):
        github_repos_json = json.dumps(github_repos if github_repos is not None else [])
    else:
        github_repos_json = github_repos

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO papers (user_id, filename, methodology, dataset, accuracy, extracted_text, github_repos, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, filename, methodology, dataset, accuracy, extracted_text, github_repos_json, now))

    conn.commit()
    paper_id = cursor.lastrowid
    conn.close()
    return paper_id

def get_paper(paper_id: int, db_path=DEFAULT_DB_PATH):
    """Retrieves single paper by id. Returns dict or None."""
    if not paper_id:
        return None
    init_db(db_path)
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM papers WHERE id = ?", (paper_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        d = dict(row)
        try:
            d["github_repos"] = json.loads(d.get("github_repos") or "[]")
        except Exception:
            d["github_repos"] = []
        return d
    return None

def get_papers(user_id=None, db_path=DEFAULT_DB_PATH):
    """Retrieves papers. NEVER returns None, ALWAYS returns a list."""
    init_db(db_path)
    conn = get_connection(db_path)
    cursor = conn.cursor()
    if user_id is not None:
        cursor.execute("SELECT * FROM papers WHERE user_id = ? ORDER BY id DESC", (user_id,))
    else:
        cursor.execute("SELECT * FROM papers ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    papers = []
    for r in (rows or []):
        d = dict(r)
        try:
            d["github_repos"] = json.loads(d.get("github_repos") or "[]")
        except Exception:
            d["github_repos"] = []
        papers.append(d)
    return papers

# Alias as requested in prompt: papers = db.get_papers() or []
get_user_papers = get_papers

def get_papers_by_ids(paper_ids: list, db_path=DEFAULT_DB_PATH):
    """Retrieves multiple papers by a list of ids. NEVER returns None."""
    if not paper_ids:
        return []
    init_db(db_path)
    conn = get_connection(db_path)
    cursor = conn.cursor()
    placeholders = ",".join(["?"] * len(paper_ids))
    cursor.execute(f"SELECT * FROM papers WHERE id IN ({placeholders}) ORDER BY id ASC", paper_ids)
    rows = cursor.fetchall()
    conn.close()
    papers = []
    for r in (rows or []):
        d = dict(r)
        try:
            d["github_repos"] = json.loads(d.get("github_repos") or "[]")
        except Exception:
            d["github_repos"] = []
        papers.append(d)
    return papers

def save_comparison(user_id: int, paper_ids: list, report_path: str = None, db_path=DEFAULT_DB_PATH) -> int:
    """Saves a comparison record to the comparisons table."""
    init_db(db_path)
    conn = get_connection(db_path)
    cursor = conn.cursor()
    paper_ids_str = ",".join(str(p) for p in (paper_ids or []))
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO comparisons (user_id, paper_ids, report_path, created_at)
        VALUES (?, ?, ?, ?)
    """, (user_id, paper_ids_str, report_path, now))

    conn.commit()
    comp_id = cursor.lastrowid
    conn.close()
    return comp_id

def get_comparisons(user_id=None, db_path=DEFAULT_DB_PATH):
    """Retrieves comparisons. NEVER returns None, ALWAYS returns a list."""
    init_db(db_path)
    conn = get_connection(db_path)
    cursor = conn.cursor()
    if user_id is not None:
        cursor.execute("SELECT * FROM comparisons WHERE user_id = ? ORDER BY id DESC", (user_id,))
    else:
        cursor.execute("SELECT * FROM comparisons ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in (rows or [])]

# Alias as requested in prompt: comparisons = db.get_comparisons() or []
get_user_comparisons = get_comparisons

def find_cached_paper(user_id: int, filename: str, db_path=DEFAULT_DB_PATH):
    """Checks if a paper has already been extracted for this user to enable instant cache loads."""
    if not user_id or not filename:
        return None
    init_db(db_path)
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM papers WHERE user_id = ? AND filename = ? ORDER BY id DESC LIMIT 1", (user_id, filename))
    row = cursor.fetchone()
    conn.close()
    if row:
        d = dict(row)
        try:
            d["github_repos"] = json.loads(d.get("github_repos") or "[]")
        except Exception:
            d["github_repos"] = []
        return d
    return None

def get_user_stats(user_id: int, db_path=DEFAULT_DB_PATH):
    """Calculates statistics for dashboard cards. NEVER returns None."""
    init_db(db_path)
    conn = get_connection(db_path)
    cursor = conn.cursor()

    today_str = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("SELECT COUNT(*) as count FROM papers WHERE user_id = ? AND created_at LIKE ?", 
                   (user_id, f"{today_str}%"))
    row_today = cursor.fetchone()
    today_count = row_today["count"] if row_today else 0

    cursor.execute("SELECT COUNT(*) as count FROM papers WHERE user_id = ?", (user_id,))
    row_total = cursor.fetchone()
    total_papers = row_total["count"] if row_total else 0

    cursor.execute("""
        SELECT methodology, COUNT(methodology) as mcount 
        FROM papers 
        WHERE user_id = ? AND methodology IS NOT NULL AND methodology NOT IN ('Not specified', 'N/A', 'signing', 'investigated', 'proposed')
        GROUP BY methodology 
        ORDER BY mcount DESC LIMIT 1
    """, (user_id,))
    top_m_row = cursor.fetchone()
    top_methodology = top_m_row["methodology"] if top_m_row else "Not specified"

    cursor.execute("""
        SELECT AVG(accuracy) as avg_acc 
        FROM papers 
        WHERE user_id = ? AND accuracy > 0
    """, (user_id,))
    avg_acc_row = cursor.fetchone()
    avg_accuracy = round(avg_acc_row["avg_acc"], 1) if (avg_acc_row and avg_acc_row["avg_acc"] is not None) else 0.0

    conn.close()

    return {
        "papers_today": today_count,
        "top_methodology": top_methodology,
        "avg_accuracy": avg_accuracy,
        "total_papers": total_papers
    }
