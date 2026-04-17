import sqlite3

conn = sqlite3.connect("data.db", check_same_thread=False)
cursor = conn.cursor()

# 使用者訂閱
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER,
    target TEXT
)
""")

# 推播歷史（避免重複）
cursor.execute("""
CREATE TABLE IF NOT EXISTS history (
    content TEXT
)
""")

conn.commit()


def subscribe(user_id, target):
    cursor.execute("INSERT INTO users VALUES (?, ?)", (user_id, target))
    conn.commit()


def get_users():
    cursor.execute("SELECT DISTINCT user_id FROM users")
    return [r[0] for r in cursor.fetchall()]


def get_user_targets(user_id):
    cursor.execute("SELECT target FROM users WHERE user_id=?", (user_id,))
    return [r[0] for r in cursor.fetchall()]


def is_new(content):
    cursor.execute("SELECT 1 FROM history WHERE content=?", (content,))
    return cursor.fetchone() is None


def save_history(content):
    cursor.execute("INSERT INTO history VALUES (?)", (content,))
    conn.commit()
