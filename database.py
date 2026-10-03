import logging
import os

logger = logging.getLogger(__name__)


def get_connection():
    server = os.getenv("SQL_SERVER")
    user = os.getenv("SQL_USER")
    password = os.getenv("SQL_PASSWORD")
    database = os.getenv("SQL_DATABASE")

    if not all([server, user, password, database]):
        raise ValueError(
            "Database configuration is missing. Set SQL_SERVER, SQL_USER, SQL_PASSWORD, and SQL_DATABASE to enable Cloud Feedback."
        )

    import pymssql

    return pymssql.connect(
        server=server,
        user=user,
        password=password,
        database=database,
        port=1433,
        login_timeout=30,
        timeout=30,
    )


def fetch_feedback(limit=10):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT TOP (%s) Id, Name, Message, CreatedAt
            FROM Feedback
            ORDER BY CreatedAt DESC
            """,
            (limit,),
        )
        rows = cursor.fetchall()
        return [
            {
                "id": row[0],
                "name": row[1],
                "message": row[2],
                "created_at": row[3],
            }
            for row in rows
        ]
    finally:
        cursor.close()
        connection.close()


def save_feedback(name, message):
    cleaned_name = (name or "").strip()
    cleaned_message = (message or "").strip()

    if not cleaned_name:
        raise ValueError("Name is required.")

    if len(cleaned_name) > 100:
        raise ValueError("Name must be 100 characters or less.")

    if not cleaned_message:
        raise ValueError("Message is required.")

    if len(cleaned_message) > 500:
        raise ValueError("Message must be 500 characters or less.")

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "INSERT INTO Feedback (Name, Message) VALUES (%s, %s)",
            (cleaned_name, cleaned_message),
        )
        connection.commit()
    finally:
        cursor.close()
        connection.close()
