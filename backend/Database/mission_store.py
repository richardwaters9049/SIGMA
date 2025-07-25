# File: /SIGMA/backend/Database/mission_store.py

from .db import get_connection
from datetime import datetime


def insert_mission(name: str, difficulty: str = "medium", is_active: bool = True):
    """
    Inserts a new mission into the 'missions' table.

    Args:
        name (str): The name/title of the mission.
        difficulty (str): Difficulty level, e.g., 'easy', 'medium', 'hard'.
        is_active (bool): Whether the mission is currently active.
    """
    connection = get_connection()
    cursor = connection.cursor()

    insert_query = """
    INSERT INTO missions (name, difficulty, is_active, created_at)
    VALUES (%s, %s, %s, %s)
    RETURNING id;
    """
    try:
        created_at = datetime.now()
        cursor.execute(insert_query, (name, difficulty, is_active, created_at))
        mission_id = cursor.fetchone()[0]
        connection.commit()
        print(f"[✅] Mission '{name}' inserted with ID: {mission_id}")
        return mission_id
    except Exception as e:
        print(f"[❌] Failed to insert mission: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()


def fetch_all_missions():
    """
    Retrieves all missions from the 'missions' table.

    Returns:
        list[dict]: A list of missions as dictionaries.
    """
    connection = get_connection()
    cursor = connection.cursor()

    fetch_query = "SELECT id, name, difficulty, is_active, created_at FROM missions ORDER BY id ASC;"

    try:
        cursor.execute(fetch_query)
        rows = cursor.fetchall()
        missions = []
        for row in rows:
            missions.append(
                {
                    "id": row[0],
                    "name": row[1],
                    "difficulty": row[2],
                    "is_active": row[3],
                    "created_at": row[4].strftime("%Y-%m-%d %H:%M:%S"),
                }
            )
        print(f"[✅] Retrieved {len(missions)} mission(s).")
        return missions
    except Exception as e:
        print(f"[❌] Failed to fetch missions: {e}")
        return []
    finally:
        cursor.close()
        connection.close()
