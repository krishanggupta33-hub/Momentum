import sqlite3

DB_NAME = "momentum.db"

def connect():
    """Establishes and returns a connection to the SQLite database."""
    return sqlite3.connect(DB_NAME)

def create_tables():
    """Initializes the database schema if it doesn't already exist."""
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            completed INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()

def add_task(task):
    """Inserts a new task into the database."""
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO tasks (task) VALUES (?)",
        (task,)
    )

    conn.commit()
    conn.close()

def get_tasks():
    """Retrieves all tasks, returning a list of tuples: (id, task, completed)."""
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, task, completed FROM tasks"
    )

    tasks = cursor.fetchall()

    conn.close()

    return tasks

def delete_task(task_id):
    """Permanently removes a task from the database by its ID."""
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM tasks WHERE id = ?",
        (task_id,)
    )

    conn.commit()
    conn.close()

def complete_task(task_id):
    """Toggles the completion status of a task (0 to 1, or 1 to 0)."""
    conn = connect()
    cursor = conn.cursor()

    # Uses a SQL CASE statement to flip the boolean state so you can un-check boxes
    cursor.execute("""
        UPDATE tasks 
        SET completed = CASE 
            WHEN completed = 1 THEN 0 
            ELSE 1 
        END 
        WHERE id = ?
    """, (task_id,))

    conn.commit()
    conn.close()

# Automatically ensure tables exist when this module is imported
create_tables()