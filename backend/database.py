"""
SQLite database layer.
All persistence lives here — no external DB needed.
"""
import sqlite3
import json
import os

DB_PATH = os.environ.get("DB_PATH", "flashcards.db")

def get_deck_by_source_file(source_file: str) -> dict | None:
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM decks WHERE source_file=?", (source_file,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS decks (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            source_file TEXT,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS cards (
            id TEXT PRIMARY KEY,
            deck_id TEXT NOT NULL,
            front TEXT NOT NULL,
            back TEXT NOT NULL,
            category TEXT DEFAULT 'concept',
            difficulty TEXT DEFAULT 'medium',
            hint TEXT DEFAULT '',
            repetitions INTEGER DEFAULT 0,
            interval_days INTEGER DEFAULT 1,
            ease_factor REAL DEFAULT 2.5,
            due_date TEXT NOT NULL,
            last_reviewed TEXT,
            mastery INTEGER DEFAULT 0,
            FOREIGN KEY (deck_id) REFERENCES decks(id)
        );
    """)
    conn.commit()
    conn.close()

# ── Deck helpers ──────────────────────────────────────────────────────────────

def insert_deck(deck: dict):
    conn = get_conn()
    conn.execute(
        "INSERT INTO decks (id, name, source_file, created_at) VALUES (?,?,?,?)",
        (deck["id"], deck["name"], deck["source_file"], deck["created_at"])
    )
    conn.commit()
    conn.close()

def get_all_decks() -> list[dict]:
    conn = get_conn()
    rows = conn.execute("SELECT * FROM decks ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_deck_by_id(deck_id: str) -> dict | None:
    conn = get_conn()
    row = conn.execute("SELECT * FROM decks WHERE id=?", (deck_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def delete_deck(deck_id: str):
    conn = get_conn()
    conn.execute("DELETE FROM cards WHERE deck_id=?", (deck_id,))
    conn.execute("DELETE FROM decks WHERE id=?", (deck_id,))
    conn.commit()
    conn.close()

# ── Card helpers ──────────────────────────────────────────────────────────────

def insert_cards(cards: list[dict]):
    conn = get_conn()
    conn.executemany(
        """INSERT INTO cards
           (id, deck_id, front, back, category, difficulty, hint,
            repetitions, interval_days, ease_factor, due_date, last_reviewed, mastery)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        [(c["id"], c["deck_id"], c["front"], c["back"],
          c["category"], c["difficulty"], c["hint"],
          c["repetitions"], c["interval_days"], c["ease_factor"],
          c["due_date"], c["last_reviewed"], c["mastery"]) for c in cards]
    )
    conn.commit()
    conn.close()

def get_cards_for_deck(deck_id: str) -> list[dict]:
    conn = get_conn()
    rows = conn.execute("SELECT * FROM cards WHERE deck_id=?", (deck_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_card_by_id(card_id: str) -> dict | None:
    conn = get_conn()
    row = conn.execute("SELECT * FROM cards WHERE id=?", (card_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def update_card(card: dict):
    conn = get_conn()
    conn.execute(
        """UPDATE cards SET
           repetitions=?, interval_days=?, ease_factor=?,
           due_date=?, last_reviewed=?, mastery=?
           WHERE id=?""",
        (card["repetitions"], card["interval_days"], card["ease_factor"],
         card["due_date"], card["last_reviewed"], card["mastery"], card["id"])
    )
    conn.commit()
    conn.close()