import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (username) REFERENCES users (username)
)
""")

cursor.execute("DELETE FROM users")

cursor.execute(
    "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
    ("teacher1", "1234", "teacher")
)

cursor.execute(
    "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
    ("student1", "1234", "student")
)

conn.commit()
conn.close()

print("Database initialized successfully")
