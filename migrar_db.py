# migrar_db.py
import sqlite3
from pathlib import Path

db = "project.db"
path = Path("migrations/init.sql")

if not path.exists():
    print("❌ No se encontró el archivo:", path)
else:
    sql = path.read_text()
    conn = sqlite3.connect(db)
    conn.executescript(sql)
    conn.commit()
    conn.close()
    print("✅ Migración aplicada correctamente a:", db)
