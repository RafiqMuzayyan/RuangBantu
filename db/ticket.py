from db.connection import get_db_connection


def create_ticket(user_id, title, category, nonce, ciphertext):
    connection = get_db_connection()

    try:
        connection.execute(
            """
            INSERT INTO tickets (
                user_id, title, category,
                description_nonce, description
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, title, category, nonce, ciphertext)
        )

        connection.commit()
        return True

    finally:
        connection.close()