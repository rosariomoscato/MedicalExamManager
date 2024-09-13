import sqlite3
import hashlib
import gettext

# Set up localization
it = gettext.translation('messages', localedir='locales', languages=['it'])
it.install()
_ = it.gettext

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password, role):
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    hashed_password = hash_password(password)
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       (username, hashed_password, role))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login(username, password):
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    hashed_password = hash_password(password)
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password))
    user = cursor.fetchone()
    conn.close()
    if user:
        return {'username': user[1], 'role': user[3]}
    return None
