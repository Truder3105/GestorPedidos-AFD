# inventory.py
from typing import Dict, Optional
import threading
import sqlite3


class Inventory:
    """
    Inventario simple en memoria con persistencia (opcional) por SQLite.
    Mantiene cantidades por sku (str).
    Thread-safe con lock simple.
    """
    def __init__(self, persistence_db: Optional[str] = None):
        self._lock = threading.RLock()
        self._stock: Dict[str, int] = {}
        self._db = persistence_db
        if self._db:
            self._init_db()

    def _init_db(self):
        with sqlite3.connect(self._db) as conn:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS inventory (
                    sku TEXT PRIMARY KEY,
                    qty INTEGER NOT NULL
                )
            """)
            conn.commit()
            # cargar en memoria
            cur.execute("SELECT sku, qty FROM inventory")
            rows = cur.fetchall()
            with self._lock:
                for sku, qty in rows:
                    self._stock[sku] = qty

    def add_product(self, sku: str, qty: int):
        if qty < 0:
            raise ValueError("qty debe ser >= 0")
        with self._lock:
            self._stock[sku] = self._stock.get(sku, 0) + qty
        if self._db:
            with sqlite3.connect(self._db) as conn:
                cur = conn.cursor()
                cur.execute("INSERT INTO inventory(sku, qty) VALUES(?, ?) ON CONFLICT(sku) DO UPDATE SET qty=qty+?;",
                            (sku, qty, qty))
                conn.commit()

    def remove_stock(self, sku: str, qty: int) -> bool:
        """
        Intenta reservar/sacar stock. Devuelve True si fue posible, False si no hay suficiente.
        """
        if qty <= 0:
            raise ValueError("qty debe ser > 0")
        with self._lock:
            available = self._stock.get(sku, 0)
            if available < qty:
                return False
            self._stock[sku] = available - qty
            new_q = self._stock[sku]
        if self._db:
            with sqlite3.connect(self._db) as conn:
                cur = conn.cursor()
                cur.execute("UPDATE inventory SET qty = ? WHERE sku = ?", (new_q, sku))
                conn.commit()
        return True

    def get_stock(self, sku: str) -> int:
        with self._lock:
            return self._stock.get(sku, 0)

    def list_all(self) -> Dict[str, int]:
        with self._lock:
            return dict(self._stock)
