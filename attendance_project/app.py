from flask import Flask, render_template, request, redirect, session
from datetime import date, datetime
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "attendance_secret_key"


DB_NAME = os.path.join(os.path.dirname(__file__), "database.db")
# ---------------- DATABASE SETUP ----------------
def init_db():
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()

        # Users table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
        """)

        # Attendance table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            status TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL
        )
        """)

        # Insert default users
        cur.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('teacher', '123', 'teacher')")
        cur.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('student', '123', 'student')")

        conn.commit()
        conn.close()
        print("Database initialized.")

init_db()


# ---------------- LOGIN ----------------
@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT role, password FROM users WHERE username=?", (username,))
        user = cur.fetchone()
        conn.close()

        if user:
            if user[1] == password:
                session['username'] = username
                session['role'] = user[0]
                return redirect('/dashboard')
            else:
                error = "Invalid password"
        else:
            error = "Invalid username"

    return render_template('login.html', error=error)


# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/')
    return render_template(
        'dashboard.html',
        username=session.get('username'),
        role=session.get('role')
    )


# ---------------- TEACHER ROUTES ----------------
@app.route('/mark_attendance', methods=['GET', 'POST'])
def mark_attendance():
    role = session.get('role')
    if role not in ["teacher", "student"]:
        return redirect('/dashboard')

    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        if role == "teacher":
            cur.execute("SELECT username FROM users WHERE role='student'")
            students = [s[0] for s in cur.fetchall()]
        else:
            students = []

        if request.method == 'POST':
            if role == "student":
                student_username = session.get('username')
                status = request.form.get('status')
            else:
                student_username = request.form.get('student_username')
                status = request.form.get('status')

            today = date.today().strftime("%Y-%m-%d")
            now = datetime.now().strftime("%H:%M:%S")

            if student_username and status:
                try:
                    cur.execute(
                        "INSERT INTO attendance (username, status, date, time) VALUES (?, ?, ?, ?)",
                        (student_username, status, today, now)
                    )
                    conn.commit()
                    if role == "teacher":
                        return redirect('/view_attendance')
                    else:
                        return redirect('/my_attendance')
                except sqlite3.Error as e:
                    # Handle database error, e.g., log it and show message
                    return f"Error marking attendance: {str(e)}"

    return render_template('mark_attendance.html', students=students, role=role)


@app.route('/view_attendance')
def view_attendance():
    if session.get('role') != "teacher":
        return redirect('/dashboard')

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT username, date, time, status FROM attendance ORDER BY date DESC, time DESC")
    records = cur.fetchall()
    conn.close()

    return render_template('view_attendance.html', records=records)


# ---------------- STUDENT ROUTE ----------------
@app.route('/my_attendance')
def my_attendance():
    if session.get('role') != "student":
        return redirect('/dashboard')

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    username = session.get('username')
    cur.execute("SELECT id, date, time, status FROM attendance WHERE username=? ORDER BY date DESC, time DESC", (username,))
    records = cur.fetchall()
    conn.close()

    return render_template('my_attendance.html', records=records)


@app.route('/delete_attendance', methods=['POST'])
def delete_attendance():
    if session.get('role') != "student":
        return redirect('/dashboard')

    id_str = request.form.get('id')
    if not id_str:
        return redirect('/my_attendance')

    try:
        id = int(id_str)
    except ValueError:
        return redirect('/my_attendance')

    username = session.get('username')
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    # Ensure the record belongs to the logged-in student
    cur.execute("SELECT username FROM attendance WHERE id=?", (id,))
    record = cur.fetchone()
    if record and record[0] == username:
        cur.execute("DELETE FROM attendance WHERE id=?", (id,))
        conn.commit()
    conn.close()

    return redirect('/my_attendance')


# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# ---------------- RUN SERVER ----------------
if __name__ == '__main__':
    app.run(debug=True)
