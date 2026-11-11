
import bcrypt
from db.connection import get_db_connection


def register_user(username, email, password):
    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    )

    connection = get_db_connection()

    try:
        connection.execute(
            """
            INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)
            """,
            (username, email, password_hash.decode("utf-8"))
        )

        connection.commit()
        return True

    except Exception:
        return False

    finally:
        connection.close()


def authenticate_user(email, password):
    connection = get_db_connection()

    try:
        user = connection.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        if user is None:
            return None

        password_valid = bcrypt.checkpw(
            password.encode("utf-8"),
            user["password_hash"].encode("utf-8")
        )

        if password_valid:
            return user

        return None

    finally:
        connection.close()
