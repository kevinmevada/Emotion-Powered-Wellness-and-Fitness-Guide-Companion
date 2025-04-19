import sqlite3
import bcrypt
import numpy as np
import hashlib

# Database connection
def get_db_connection():
    conn = sqlite3.connect('users.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize the database and migrate passwords
def init_db():
    conn = get_db_connection()
    conn.execute(''' 
        CREATE TABLE IF NOT EXISTS users ( 
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            username TEXT UNIQUE NOT NULL, 
            email TEXT UNIQUE NOT NULL, 
            password TEXT NOT NULL,
            hash_method TEXT DEFAULT 'bcrypt'
        ) 
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS face_embeddings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            embedding BLOB NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS workout_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            plan_id INTEGER,
            completed BOOLEAN DEFAULT FALSE,
            feedback TEXT,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (plan_id) REFERENCES workout_plans (id)
        )
    ''')
    
    migration_needed = conn.execute("PRAGMA table_info(users)").fetchall()
    if not any(col[1] == 'hash_method' for col in migration_needed):
        conn.execute("ALTER TABLE users ADD COLUMN hash_method TEXT DEFAULT 'sha256'")
        users = conn.execute("SELECT id, username, email, password FROM users").fetchall()
        for user in users:
            if len(user['password']) == 64:
                new_hash = bcrypt.hashpw(user['password'].encode(), bcrypt.gensalt()).decode()
                conn.execute("UPDATE users SET password = ?, hash_method = 'bcrypt' WHERE id = ?",
                            (new_hash, user['id']))
        conn.commit()
    
    conn.commit()
    conn.close()

# Hash passwords
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# Verify password (support both bcrypt and SHA-256 during migration)
def verify_password(password, hashed, hash_method='bcrypt'):
    if hash_method == 'bcrypt':
        try:
            return bcrypt.checkpw(password.encode(), hashed.encode())
        except ValueError:
            return False
    elif hash_method == 'sha256':
        return hashlib.sha256(password.encode()).hexdigest() == hashed
    return False

# Add a new user
def create_user(username, email, password):
    conn = get_db_connection()
    hashed_password = hash_password(password)
    try:
        conn.execute('INSERT INTO users (username, email, password, hash_method) VALUES (?, ?, ?, ?)', 
                    (username, email, hashed_password, 'bcrypt'))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        if conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone():
            return "Username already exists."
        elif conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone():
            return "Email already exists."
        return "Registration failed."
    finally:
        conn.close()

# Authenticate a user
def authenticate(username, password):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    if user and verify_password(password, user['password'], user['hash_method']):
        return user
    return None

# Save face embedding
def save_face_embedding(user_id, embedding):
    conn = get_db_connection()
    embedding_array = np.array(embedding)
    conn.execute(
        "INSERT INTO face_embeddings (user_id, embedding) VALUES (?, ?)",
        (user_id, embedding_array.tobytes())
    )
    conn.commit()
    conn.close()

# Retrieve face embedding
def get_face_embedding(user_id):
    conn = get_db_connection()
    embedding = conn.execute('SELECT embedding FROM face_embeddings WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    return np.frombuffer(embedding["embedding"], dtype=np.float64) if embedding else None

# Save workout plan
def save_workout_plan(user_id, plan_type, workouts):
    conn = get_db_connection()
    plan_id = conn.execute('INSERT INTO workout_plans (user_id, type, data) VALUES (?, ?, ?)', 
                          (user_id, plan_type, workouts.to_json())).lastrowid
    conn.commit()
    conn.close()
    return plan_id

# Get workout plans
def get_workout_plans(user_id):
    conn = get_db_connection()
    plans = conn.execute('SELECT * FROM workout_plans WHERE user_id = ? ORDER BY created_at DESC', (user_id,)).fetchall()
    conn.close()
    return plans

# Save progress
def save_progress(user_id, plan_id, completed, feedback):
    conn = get_db_connection()
    conn.execute('INSERT INTO progress (user_id, plan_id, completed, feedback) VALUES (?, ?, ?, ?)', 
                (user_id, plan_id, completed, feedback))
    conn.commit()
    conn.close()

# Get progress
def get_progress(user_id):
    conn = get_db_connection()
    progress = conn.execute('SELECT * FROM progress WHERE user_id = ? ORDER BY completed_at DESC', (user_id,)).fetchall()
    conn.close()
    return progress

# Initialize database
init_db()