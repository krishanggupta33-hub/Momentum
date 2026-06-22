import sqlite3
from datetime import date, timedelta

DB_NAME = "momentum.db"

def connect():
    return sqlite3.connect(DB_NAME)

def create_tables():
    conn = connect()
    cursor = conn.cursor()

    # Tasks Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            completed INTEGER DEFAULT 0
        )
    """)

    # Habits Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_name TEXT NOT NULL,
            streak INTEGER DEFAULT 0,
            last_completed TEXT
        )
    """)

    conn.commit()
    conn.close()

# ==========================================
# TASKS LOGIC
# ==========================================
def add_task(task):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (task) VALUES (?)", (task,))
    conn.commit()
    conn.close()

def get_tasks():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id, task, completed FROM tasks")
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def delete_task(task_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

def complete_task(task_id):
    conn = connect()
    cursor = conn.cursor()
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

# ==========================================
# HABITS LOGIC
# ==========================================
def add_habit(habit_name):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO habits (habit_name, streak, last_completed) VALUES (?, 0, '')", (habit_name,))
    conn.commit()
    conn.close()

def get_habits():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id, habit_name, streak, last_completed FROM habits")
    habits = cursor.fetchall()
    conn.close()
    return habits

def delete_habit(habit_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
    conn.commit()
    conn.close()

def check_in_habit(habit_id):
    conn = connect()
    cursor = conn.cursor()
    
    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    
    cursor.execute("SELECT streak, last_completed FROM habits WHERE id = ?", (habit_id,))
    result = cursor.fetchone()
    
    if result:
        current_streak, last_completed = result
        if last_completed == today:
            new_streak = current_streak
        elif last_completed == yesterday:
            new_streak = current_streak + 1
        else:
            new_streak = 1
            
        cursor.execute("""
            UPDATE habits 
            SET streak = ?, last_completed = ? 
            WHERE id = ?
        """, (new_streak, today, habit_id))
        
    conn.commit()
    conn.close()

# ==========================================
# DASHBOARD STATS LOGIC
# ==========================================
def get_task_stats():
    conn = connect()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(id) FROM tasks WHERE completed = 1")
    completed = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(id) FROM tasks WHERE completed = 0")
    pending = cursor.fetchone()[0]
    
    conn.close()
    return completed, pending

create_tables()