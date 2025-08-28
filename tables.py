from engine import engine
from sqlalchemy import text
with engine.begin() as conn:
    conn.execute(text("""CREATE TABLE IF NOT EXISTS users(
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT,
                      email TEXT UNIQUE)"""))
    
    conn.execute(text("""CREATE TABLE IF NOT EXISTS habits(
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT,
                      owner_id INTEGER,
                      last_mark DATETIME,
                      streak INTEGER DEFAULT 0,
                      FOREIGN KEY (owner_id) REFERENCES users(id))"""))
    