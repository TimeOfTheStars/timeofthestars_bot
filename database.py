import sqlite3
from threading import Lock

lock = Lock()

def init_db():
    with lock, sqlite3.connect("users.db") as con:
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS subscribers (
                user_id INTEGER PRIMARY KEY
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS last_notified (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        con.commit()

def add_subscriber(user_id: int):
    with lock, sqlite3.connect("users.db") as con:
        con.execute("INSERT OR IGNORE INTO subscribers (user_id) VALUES (?)", (user_id,))
        con.commit()

def remove_subscriber(user_id: int):
    with lock, sqlite3.connect("users.db") as con:
        con.execute("DELETE FROM subscribers WHERE user_id = ?", (user_id,))
        con.commit()

def get_subscribers():
    with lock, sqlite3.connect("users.db") as con:
        cur = con.cursor()
        cur.execute("SELECT user_id FROM subscribers")
        return [row[0] for row in cur.fetchall()]

def set_last_notified(game_id: int):
    with lock, sqlite3.connect("users.db") as con:
        con.execute("INSERT OR REPLACE INTO last_notified (key, value) VALUES ('last_game', ?)", (str(game_id),))
        con.commit()

def get_last_notified() -> int | None:
    with lock, sqlite3.connect("users.db") as con:
        cur = con.cursor()
        cur.execute("SELECT value FROM last_notified WHERE key = 'last_game'")
        row = cur.fetchone()
        return int(row[0]) if row else None