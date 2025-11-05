-- migrations/init.sql
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS inventory (
    sku TEXT PRIMARY KEY,
    qty INTEGER NOT NULL CHECK(qty >= 0)
);

CREATE TABLE IF NOT EXISTS orders (
    id TEXT PRIMARY KEY,
    sku TEXT NOT NULL,
    qty INTEGER NOT NULL CHECK(qty > 0),
    events TEXT NOT NULL, -- JSON array
    state TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (sku) REFERENCES inventory(sku)
);

CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at);
