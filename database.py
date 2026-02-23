import sqlite3
from pathlib import Path

DB_PATH = Path("portfolio.db")


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    """
    Creates the holdings table if it doesn't exist.
    """
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS holdings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            shares REAL NOT NULL,
            price REAL NOT NULL,
            asset_class TEXT NOT NULL,
            market_value REAL NOT NULL
        );
        """
    )
    conn.commit()


def clear_holdings(conn: sqlite3.Connection) -> None:
    conn.execute("DELETE FROM holdings;")
    conn.commit()


def insert_holdings(conn: sqlite3.Connection, rows: list[dict]) -> None:
    """
    rows: list of dicts with keys:
      ticker, shares, price, asset_class, market_value
    """
    conn.executemany(
        """
        INSERT INTO holdings (ticker, shares, price, asset_class, market_value)
        VALUES (:ticker, :shares, :price, :asset_class, :market_value);
        """,
        rows,
    )
    conn.commit()


def fetch_all_holdings(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    cur = conn.execute(
        "SELECT ticker, shares, price, asset_class, market_value FROM holdings;"
    )
    return cur.fetchall()