import os
import random
from flask import Flask, render_template, request, redirect, session
import pymysql

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "fallbacksecret")


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    with open('init.sql', 'r') as f:
        sql = f.read()
    for statement in sql.split(';'):
        statement = statement.strip()
        if statement:
            cur.execute(statement)
    conn.commit()
    conn.close()
    print("✅ Database initialized!")


def get_db_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST'),
        port=int(os.getenv('DB_PORT')),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        db=os.getenv('MYSQL_DATABASE'),
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=10,
    )


def generate_account_number():
    return str(random.randint(10**9, 10**10 - 1))


# ─── Home ───────────────────────────────────────────────
@app.route('/')
def home():
    return render_template('home.html')


# ─── Register ───────────────────────────────────────────
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cur  = conn.cursor()
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cur.fetchone():
            conn.close()
            return render_template('register.html', error="Username already taken. Please choose another.")

        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        conn.close()
        return redirect('/login')

    return render_template('register.html')


# ─── Login ──────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cur  = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()
        conn.close()

        if user:
            session['username'] = username
            return redirect('/dashboard')
        return render_template('login.html', error="Invalid username or password.")

    return render_template('login.html')


# ─── Logout ─────────────────────────────────────────────
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')


# ─── Open Account ───────────────────────────────────────
@app.route('/open-account', methods=['GET', 'POST'])
def open_account():
    if 'username' not in session:
        return redirect('/login')

    if request.method == 'POST':
        name       = request.form['name']
        email      = request.form['email']
        mobile     = request.form['mobile']
        balance    = request.form['balance']
        acc_number = generate_account_number()

        conn = get_db_connection()
        cur  = conn.cursor()
        cur.execute("""
            INSERT INTO accounts (name, email, mobile, acc_number, balance)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, email, mobile, acc_number, balance))
        conn.commit()
        conn.close()
        return redirect('/dashboard')

    return render_template('open_account.html')


# ─── Dashboard ──────────────────────────────────────────
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/login')

    conn = get_db_connection()
    cur  = conn.cursor()
    cur.execute("SELECT * FROM accounts")
    accounts = cur.fetchall()
    conn.close()
    return render_template('dashboard.html', accounts=accounts)


# ─── Run ────────────────────────────────────────────────
if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)