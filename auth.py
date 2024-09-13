import hashlib
import gettext
from database import get_db_connection

# Set up localization
it = gettext.translation('messages', localedir='locales', languages=['it'])
it.install()
_ = it.gettext

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password, role):
    conn = get_db_connection()
    if conn is None:
        return False

    hashed_password = hash_password(password)
    try:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                           (username, hashed_password, role))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error creating user: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def login(username, password):
    conn = get_db_connection()
    if conn is None:
        return None

    hashed_password = hash_password(password)
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, hashed_password))
            user = cursor.fetchone()
        if user:
            return {'username': user[1], 'role': user[3]}
        return None
    except Exception as e:
        print(f"Error during login: {e}")
        return None
    finally:
        conn.close()
