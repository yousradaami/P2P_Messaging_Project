
import sqlite3
import bcrypt
from pathlib import Path

# Database location
DATABASE = Path(__file__).resolve().parent / "users.db"


def initialize_database():
    """Create the users table if it does not exist."""

    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash BLOB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


def register_user(email, password):
    """Register a new user."""

    email = email.strip().lower()

    if not email or not password:
        return False, "Email and password are required."

    if len(password) < 8:
        return False, "Password must contain at least 8 characters."

    # Hash the password
    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    )

    try:
        connection = sqlite3.connect(DATABASE)
        cursor = connection.cursor()

        cursor.execute(
            "INSERT INTO users (email, password_hash) VALUES (?, ?)",
            (email, password_hash)
        )

        connection.commit()
        connection.close()

        return True, "Registration successful!"

    except sqlite3.IntegrityError:
        return False, "This email is already registered."

    except sqlite3.Error as error:
        return False, f"Database error: {error}"


def login_user(email, password):
    """Verify user login credentials."""

    email = email.strip().lower()

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT password_hash FROM users WHERE email = ?",
        (email,)
    )

    result = cursor.fetchone()
    connection.close()

    if result is None:
        return False

    stored_hash = result[0]

    return bcrypt.checkpw(
        password.encode("utf-8"),
        stored_hash
    )


# Initialize the database
initialize_database()

print("Database initialized successfully!")
