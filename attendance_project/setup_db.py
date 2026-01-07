import sqlite3

conn = sqlite3.connect("database.db")
cur = conn.cursor()

# Create users table
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
)
""")

# Insert default users
cur.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('teacher', '123', 'teacher')")
cur.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('student', '123', 'student')")

conn.commit()
conn.close()
print("Database setup complete!")
