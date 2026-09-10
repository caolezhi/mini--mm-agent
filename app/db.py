import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent.parent / "chat.db"


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                previous_response_id TEXT
            )
        """)


def save_message(session_id: str, role: str, content: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO messages (session_id, role, content)
            VALUES (?, ?, ?)
            """,
            (session_id, role, content),
        )


def get_messages(session_id: str):
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            """
            SELECT role, content
            FROM messages
            WHERE session_id = ?
            ORDER BY id
            """,
            (session_id,),
        ).fetchall()

    return [
        {"role": role, "content": content}
        for role, content in rows
    ]


def get_previous_response_id(session_id: str):
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            """
            SELECT previous_response_id
            FROM sessions
            WHERE session_id = ?
            """,
            (session_id,),
        ).fetchone()

    return row[0] if row else None


def set_previous_response_id(session_id: str, response_id: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO sessions (session_id, previous_response_id)
            VALUES (?, ?)
            ON CONFLICT(session_id)
            DO UPDATE SET previous_response_id = excluded.previous_response_id
            """,
            (session_id, response_id),
        )


def clear_session(session_id: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "DELETE FROM messages WHERE session_id = ?",
            (session_id,),
        )

        conn.execute(
            "DELETE FROM sessions WHERE session_id = ?",
            (session_id,),
        )
