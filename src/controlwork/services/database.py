from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path


class Database:
    def __init__(self, path: Path) -> None:
        self._conn = sqlite3.connect(path)
        self._conn.row_factory = sqlite3.Row
        self._ensure_schema()

    def close(self) -> None:
        self._conn.close()

    def _ensure_schema(self) -> None:
        self._conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS sessions (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              started_at TEXT NOT NULL,
              ended_at TEXT,
              active_sec INTEGER NOT NULL DEFAULT 0,
              idle_sec INTEGER NOT NULL DEFAULT 0,
              break_sec INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS reminder_events (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              ts TEXT NOT NULL,
              type TEXT NOT NULL,
              point_min INTEGER NOT NULL,
              action_taken TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS break_events (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              started_at TEXT NOT NULL,
              ended_at TEXT,
              valid_idle_sec INTEGER NOT NULL DEFAULT 0,
              completed INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS app_settings (
              key TEXT PRIMARY KEY,
              value_json TEXT NOT NULL
            );
            """
        )
        self._conn.commit()

    def close_open_sessions(self, ended_at: datetime) -> None:
        self._conn.execute(
            "UPDATE sessions SET ended_at = ? WHERE ended_at IS NULL",
            (ended_at.isoformat(),),
        )
        self._conn.commit()

    def create_session(self, started_at: datetime) -> int:
        cur = self._conn.execute(
            "INSERT INTO sessions(started_at) VALUES (?)",
            (started_at.isoformat(),),
        )
        self._conn.commit()
        return int(cur.lastrowid)

    def update_session_totals(self, session_id: int, active_sec: int, idle_sec: int, break_sec: int) -> None:
        self._conn.execute(
            """
            UPDATE sessions
               SET active_sec = ?, idle_sec = ?, break_sec = ?
             WHERE id = ?
            """,
            (active_sec, idle_sec, break_sec, session_id),
        )
        self._conn.commit()

    def close_session(self, session_id: int, ended_at: datetime) -> None:
        self._conn.execute(
            "UPDATE sessions SET ended_at = ? WHERE id = ?",
            (ended_at.isoformat(), session_id),
        )
        self._conn.commit()

    def log_reminder(self, ts: datetime, event_type: str, point_min: int, action_taken: str) -> None:
        self._conn.execute(
            "INSERT INTO reminder_events(ts, type, point_min, action_taken) VALUES (?,?,?,?)",
            (ts.isoformat(), event_type, point_min, action_taken),
        )
        self._conn.commit()

    def start_break_event(self, started_at: datetime) -> int:
        cur = self._conn.execute(
            "INSERT INTO break_events(started_at) VALUES (?)",
            (started_at.isoformat(),),
        )
        self._conn.commit()
        return int(cur.lastrowid)

    def update_break_event(self, break_id: int, valid_idle_sec: int) -> None:
        self._conn.execute(
            "UPDATE break_events SET valid_idle_sec = ? WHERE id = ?",
            (valid_idle_sec, break_id),
        )
        self._conn.commit()

    def close_break_event(self, break_id: int, ended_at: datetime, completed: bool) -> None:
        self._conn.execute(
            "UPDATE break_events SET ended_at = ?, completed = ? WHERE id = ?",
            (ended_at.isoformat(), 1 if completed else 0, break_id),
        )
        self._conn.commit()

    def get_today_stats(self, start_dt: datetime, end_dt: datetime) -> dict[str, int]:
        range_params = (start_dt.isoformat(), end_dt.isoformat())
        session_row = self._conn.execute(
            """
            SELECT
              COALESCE(SUM(active_sec), 0) AS active_sec,
              COALESCE(SUM(idle_sec), 0) AS idle_sec,
              COALESCE(SUM(break_sec), 0) AS break_sec
            FROM sessions
            WHERE started_at >= ? AND started_at < ?
            """,
            range_params,
        ).fetchone()

        reminder_rows = self._conn.execute(
            """
            SELECT action_taken, COUNT(*) AS cnt
            FROM reminder_events
            WHERE ts >= ? AND ts < ?
            GROUP BY action_taken
            """,
            range_params,
        ).fetchall()

        action_counts = {row["action_taken"]: int(row["cnt"]) for row in reminder_rows}
        return {
            "active_sec": int(session_row["active_sec"]),
            "idle_sec": int(session_row["idle_sec"]),
            "break_sec": int(session_row["break_sec"]),
            "snoozes": int(action_counts.get("snooze", 0)),
            "skips": int(action_counts.get("skip", 0)),
        }

    def get_skip_count(self, start_dt: datetime, end_dt: datetime) -> int:
        row = self._conn.execute(
            """
            SELECT COUNT(*) AS cnt
            FROM reminder_events
            WHERE ts >= ? AND ts < ? AND action_taken = 'skip'
            """,
            (start_dt.isoformat(), end_dt.isoformat()),
        ).fetchone()
        return int(row["cnt"])

    def save_settings_cache(self, payload: dict[str, object]) -> None:
        for key, value in payload.items():
            self._conn.execute(
                """
                INSERT INTO app_settings(key, value_json)
                VALUES(?, ?)
                ON CONFLICT(key)
                DO UPDATE SET value_json = excluded.value_json
                """,
                (key, json.dumps(value, ensure_ascii=False)),
            )
        self._conn.commit()
