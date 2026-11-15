import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

DB_PATH = Path(__file__).resolve().parent / "meetings.db"

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS meetings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(1000) NOT NULL,
                people VARCHAR(1000) NOT NULL,
                notes TEXT NOT NULL,
                summary TEXT NOT NULL,
                actions TEXT NOT NULL,
                result TEXT NOT NULL,
                created_at VARCHAR(100) NOT NULL
            )
            """
        )
        conn.commit()

def save_meeting(title: str, people: str, notes: str, summary: str, actions: str, result: str) -> int:
    created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO meetings (title, people, notes, summary, actions, result, created_at) VALUES
            (?, ?, ?, ?, ?, ?, ?)
            """, (title, people, notes, summary, actions, result, created_at)
        )
        conn.commit()
        return int(cursor.lastrowid)


def list_meetings(limit: int = 20) -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, title, people, summary, created_at 
            FROM meetings
            ORDER BY id DESC
            LIMIT ?
            """, (limit,)
        ).fetchall()
    return [dict(row) for row in rows]

def format_meetings_markdown(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "저장된 회의가 없습니다."
    lines = ["### 저장된 회의 목룍", ""]
    for row in rows:
        lines.append(
            f"- #{row['id']} {row['title']}"
            f"({row['people'] or '참가자 없음'}) - {row['created_at']}"
        )
        lines.append(f" - 요약: {row['summary']}")
    return "\n".join(lines)


def get_meeting(meeting_id: int) -> list[dict[str, Any]] | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM meetings WHERE id = ?", (meeting_id,)
        ).fetchone()
    return [dict(row)] if row else None
