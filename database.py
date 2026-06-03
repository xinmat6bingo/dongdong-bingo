import sqlite3
from datetime import datetime

DB_NAME = "bingo.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS draws (
            period TEXT PRIMARY KEY,
            draw_time TEXT,
            nums TEXT,
            super_num INTEGER,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_draw(period, draw_time, nums, super_num):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO draws
        VALUES (?, ?, ?, ?, ?)
    """, (
        period,
        draw_time,
        ",".join(f"{n:02d}" for n in nums),
        super_num,
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()

def load_draws():
    import pandas as pd

    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query(
        "SELECT * FROM draws ORDER BY period DESC",
        conn
    )
    conn.close()

    if df.empty:
        return df

    df["號碼"] = df["nums"].apply(lambda x: [int(n) for n in x.split(",")])
    df["期別"] = df["period"]
    df["時間"] = df["draw_time"]
    df["超級獎號"] = df["super_num"].astype(int)

    return df