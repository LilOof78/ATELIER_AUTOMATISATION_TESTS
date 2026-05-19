import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "runs.sqlite3"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                api TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                passed INTEGER NOT NULL,
                failed INTEGER NOT NULL,
                error_rate REAL NOT NULL,
                availability_percent REAL NOT NULL,
                latency_ms_avg REAL NOT NULL,
                latency_ms_p95 REAL NOT NULL,
                raw_json TEXT NOT NULL
            )
        """)
        conn.commit()


def save_run(run_data):
    init_db()

    summary = run_data["summary"]

    with get_connection() as conn:
        conn.execute("""
            INSERT INTO runs (
                api,
                timestamp,
                passed,
                failed,
                error_rate,
                availability_percent,
                latency_ms_avg,
                latency_ms_p95,
                raw_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            run_data["api"],
            run_data["timestamp"],
            summary["passed"],
            summary["failed"],
            summary["error_rate"],
            summary["availability_percent"],
            summary["latency_ms_avg"],
            summary["latency_ms_p95"],
            json.dumps(run_data, ensure_ascii=False)
        ))
        conn.commit()


def list_runs(limit=20):
    init_db()

    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT *
            FROM runs
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()

    runs = []

    for row in rows:
        raw = json.loads(row["raw_json"])
        runs.append({
            "id": row["id"],
            "api": row["api"],
            "timestamp": row["timestamp"],
            "summary": raw["summary"],
            "tests": raw["tests"]
        })

    return runs


def get_last_run():
    runs = list_runs(limit=1)
    return runs[0] if runs else None