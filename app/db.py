import psycopg2
from config import Config


def get_connection():
    return psycopg2.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        database=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        connect_timeout=5,
    )


def check_database():
    connection = None

    try:
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()

        return True, "Database connection successful"

    except Exception as exc:
        return False, str(exc)

    finally:
        if connection:
            connection.close()


def get_order_count():
    connection = None

    try:
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM orders")
            return cursor.fetchone()[0]

    except Exception:
        return None

    finally:
        if connection:
            connection.close()