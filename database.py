import logging
import os

logger = logging.getLogger(__name__)


def _get_pyodbc():
    try:
        import pyodbc
    except ImportError as exc:
        raise RuntimeError(
            "pyodbc is not available. Install the SQL Server ODBC driver and dependency first."
        ) from exc

    return pyodbc


def get_connection():
    connection_string = os.getenv("SQL_CONNECTION_STRING")
    if not connection_string:
        raise ValueError("SQL_CONNECTION_STRING is not configured.")

    pyodbc = _get_pyodbc()
    return pyodbc.connect(connection_string, timeout=30)


def fetch_feedback(limit=10):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT TOP (?) Id, Name, Message, CreatedAt
            FROM Feedback
            ORDER BY CreatedAt DESC
            """,
            limit,
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
            "INSERT INTO Feedback (Name, Message) VALUES (?, ?)",
            cleaned_name,
            cleaned_message,
        )
        connection.commit()
    finally:
        cursor.close()
        connection.close()
