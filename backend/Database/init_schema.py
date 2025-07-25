# File: /SIGMA/backend/Database/init_schema.py

from db import get_connection


def create_tables():
    """
    Create database tables required for the SIGMA project.
    """
    connection = get_connection()
    cursor = connection.cursor()

    create_query = """
    CREATE TABLE IF NOT EXISTS missions (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        difficulty TEXT,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    try:
        cursor.execute(create_query)
        connection.commit()
        print("[✅] Table 'missions' created or already exists.")
    except Exception as e:
        print(f"[❌] Failed to create table: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    create_tables()
