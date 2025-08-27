from engine import engine
from sqlalchemy import text
with engine.begin() as conn:
    conn.execute(text("""CREATE TABLE IF NOT EXISTS users(
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT,
                      email TEXT)"""))
    
    conn.execute(text("""CREATE TABLE IF NOT EXISTS habits(
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT,
                      owner_id TEXT,
                      last_mark TEXT,
                      streak INTEGER
                      FOREIGN KEY (owner_id) REFERENCES users(id))"""))
    