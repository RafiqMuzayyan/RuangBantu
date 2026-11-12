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
        
def get_ticket(ticket_id, user_id, role):
    connection = get_db_connection()

    try:
        if role == "admin":
            ticket = connection.execute(
                """
                SELECT tickets.*, users.username 
                FROM tickets 
                JOIN users ON tickets.user_id = users.id 
                WHERE tickets.id = ?
                """,
                (ticket_id,)
            ).fetchone()
        else:
            ticket = connection.execute(
                """
                SELECT tickets.*, users.username 
                FROM tickets 
                JOIN users ON tickets.user_id = users.id 
                WHERE tickets.id = ? AND tickets.user_id = ?
                """,
                (ticket_id, user_id)
            ).fetchone()

        return dict(ticket) if ticket else None

    finally:
        connection.close()
        
def get_user_tickets(user_id, role):
    connection = get_db_connection()

    try:
        if role == "admin":
            tickets = connection.execute(
                """
                SELECT tickets.*, users.username
                FROM tickets
                JOIN users ON tickets.user_id = users.id
                ORDER BY tickets.created_at DESC
                """
            ).fetchall()
        else:
            tickets = connection.execute(
                """
                SELECT tickets.*, users.username
                FROM tickets
                JOIN users ON tickets.user_id = users.id
                WHERE tickets.user_id = ?
                ORDER BY tickets.created_at DESC
                """,
                (user_id,)
            ).fetchall()

        return [dict(ticket) for ticket in tickets]

    finally:
        connection.close()
        
def update_ticket(
    ticket_id,
    user_id,
    role,
    title,
    category,
    nonce,
    ciphertext
):
    connection = get_db_connection()

    try:
        if role == "admin":
            cursor = connection.execute(
                """
                UPDATE tickets
                SET title = ?,
                    category = ?,
                    description_nonce = ?,
                    description = ?
                WHERE id = ?
                """,
                (
                    title,
                    category,
                    nonce,
                    ciphertext,
                    ticket_id
                )
            )
        else:
            cursor = connection.execute(
                """
                UPDATE tickets
                SET title = ?,
                    category = ?,
                    description_nonce = ?,
                    description = ?
                WHERE id = ? AND user_id = ?
                """,
                (
                    title,
                    category,
                    nonce,
                    ciphertext,
                    ticket_id,
                    user_id
                )
            )

        connection.commit()
        return cursor.rowcount > 0

    finally:
        connection.close()
        

def delete_ticket(ticket_id, user_id, role):
    connection = get_db_connection()

    try:
        if role == "admin":
            cursor = connection.execute(
                """
                DELETE FROM tickets
                WHERE id = ?
                """,
                (ticket_id,)
            )
        else:
            cursor = connection.execute(
                """
                DELETE FROM tickets
                WHERE id = ? AND user_id = ?
                """,
                (ticket_id, user_id)
            )

        connection.commit()
        return cursor.rowcount > 0

    finally:
        connection.close()

