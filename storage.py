# storage.py
import sqlite3
from typing import Optional, List, Tuple, Dict
import json
import datetime


class Storage:
    """
    Persistencia simple de pedidos y trazas en SQLite.
    """
    def __init__(self, db_path: str = "data.db"):
        self.db = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()
            cur.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id TEXT PRIMARY KEY,
                sku TEXT,
                qty INTEGER,
                events TEXT,
                state TEXT,
                created_at TEXT
            )
            """)
            conn.commit()

    def save_order(self, order_id: str, sku: str, qty: int, events: List[str], state: str):
        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()
            cur.execute("""
            INSERT INTO orders(id, sku, qty, events, state, created_at)
            VALUES(?,?,?,?,?,?)
            ON CONFLICT(id) DO UPDATE SET events=?, state=?
            """, (order_id, sku, qty, json.dumps(events), state, datetime.datetime.utcnow().isoformat(),
                  json.dumps(events), state))
            conn.commit()

    def get_order(self, order_id: str) -> Optional[Dict]:
        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, sku, qty, events, state, created_at FROM orders WHERE id = ?", (order_id,))
            row = cur.fetchone()
            if not row:
                return None
            return {
                "id": row[0],
                "sku": row[1],
                "qty": row[2],
                "events": json.loads(row[3]),
                "state": row[4],
                "created_at": row[5]
            }

    def list_orders(self) -> List[Dict]:
        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, sku, qty, events, state, created_at FROM orders ORDER BY created_at DESC")
            rows = cur.fetchall()
            out = []
            for row in rows:
                out.append({
                    "id": row[0],
                    "sku": row[1],
                    "qty": row[2],
                    "events": json.loads(row[3]),
                    "state": row[4],
                    "created_at": row[5]
                })
            return out
