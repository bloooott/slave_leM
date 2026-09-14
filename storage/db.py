import sqlite3
from datetime import datetime, timezone, timedelta
from contextlib import contextmanager

DB_PATH = "jobs.db"

@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS offers (
                id TEXT PRIMARY KEY,
                title TEXT,
                company TEXT,
                description TEXT,
                url TEXT,
                location TEXT,
                source TEXT,
                posted_date TEXT,
                scraped_at TEXT,
                score REAL,
                feedback TEXT,
                notified INTEGER DEFAULT 0
            )
        """)

def save_offers(offers: list) -> int:
    """Insère les nouvelles offres, ignore les doublons (par id). Retourne le nombre de nouvelles offres."""
    new_count = 0
    now_iso = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        for o in offers:
            cursor = conn.execute("SELECT 1 FROM offers WHERE id = ?", (o.id,))
            if cursor.fetchone() is None:
                conn.execute("""
                    INSERT INTO offers (id, title, company, description, url, location, source, posted_date, scraped_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (o.id, o.title, o.company, o.description, o.url, o.location, o.source, o.posted_date, now_iso))
                new_count += 1
    return new_count

def get_unscored_offers():
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM offers WHERE score IS NULL")
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

def delete_old_offers(max_hours: int = 48) -> int:
    """Supprime les offres dont scraped_at dépasse max_hours. Retourne le nombre supprimé."""
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=max_hours)).isoformat()
    with get_connection() as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM offers WHERE scraped_at < ?", (cutoff,))
        count = cursor.fetchone()[0]
        conn.execute("DELETE FROM offers WHERE scraped_at < ?", (cutoff,))
    return count

def get_all_offers(limit: int = 100):
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT id, title, company, location, score, url, source, posted_date FROM offers "
            "ORDER BY score DESC NULLS LAST LIMIT ?", (limit,)
        )
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]