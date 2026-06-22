import sqlite3
import json
from datetime import date, timedelta

DB_NAME = "momentum.db"

def connect():
    return sqlite3.connect(DB_NAME)

def create_tables():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            completed INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_name TEXT NOT NULL,
            streak INTEGER DEFAULT 0,
            last_completed TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            goal_name TEXT NOT NULL,
            target_amount INTEGER NOT NULL,
            current_amount INTEGER DEFAULT 0,
            deadline TEXT
        )
    """)

    # NEW: Profile table for Gamification XP
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1
        )
    """)

    # Initialize the profile row if it doesn't exist
    cursor.execute("SELECT COUNT(*) FROM profile")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO profile (xp, level) VALUES (0, 1)")

    conn.commit()
    conn.close()

# ==========================================
# GAMIFICATION LOGIC (NEW)
# ==========================================
def get_profile():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT xp, level FROM profile WHERE id = 1")
    xp, level = cursor.fetchone()
    conn.close()
    return xp, level

def add_xp(amount):
    conn = connect()
    cursor = conn.cursor()
    
    cursor.execute("SELECT xp FROM profile WHERE id = 1")
    current_xp = cursor.fetchone()[0]
    
    new_xp = current_xp + amount
    # Mathematical Leveling System: 1 Level per 100 XP
    new_level = (new_xp // 100) + 1 
    
    cursor.execute("UPDATE profile SET xp = ?, level = ? WHERE id = 1", (new_xp, new_level))
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
    
    # Check if we are completing or uncompleting to award XP properly
    cursor.execute("SELECT completed FROM tasks WHERE id = ?",(task_id,))
    is_completed = cursor.fetchone()[0]
    
    if is_completed == 0: # Turning it ON
        cursor.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()
        add_xp(10) # 10 XP for a task
        return True
    else: # Turning it OFF
        cursor.execute("UPDATE tasks SET completed = 0 WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()
        return False

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
    
    awarded_xp = False
    
    if result:
        current_streak, last_completed = result
        if last_completed == today:
            new_streak = current_streak
        elif last_completed == yesterday:
            new_streak = current_streak + 1
            awarded_xp = True
        else:
            new_streak = 1
            awarded_xp = True
            
        cursor.execute("""
            UPDATE habits 
            SET streak = ?, last_completed = ? 
            WHERE id = ?
        """, (new_streak, today, habit_id))
        
    conn.commit()
    conn.close()
    
    if awarded_xp:
        add_xp(15) # 15 XP for habit consistency

# ==========================================
# GOALS LOGIC
# ==========================================
def add_goal(goal_name, target_amount, deadline):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO goals (goal_name, target_amount, current_amount, deadline) VALUES (?, ?, 0, ?)", 
        (goal_name, target_amount, deadline)
    )
    conn.commit()
    conn.close()

def get_goals():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id, goal_name, target_amount, current_amount, deadline FROM goals")
    goals = cursor.fetchall()
    conn.close()
    return goals

def update_goal_progress(goal_id, amount_to_add):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT current_amount, target_amount FROM goals WHERE id = ?", (goal_id,))
    result = cursor.fetchone()
    
    awarded_xp = False
    
    if result:
        current, target = result
        new_amount = current + amount_to_add
        if new_amount > target:
            new_amount = target 
        elif new_amount > current:
            awarded_xp = True
            
        cursor.execute("UPDATE goals SET current_amount = ? WHERE id = ?", (new_amount, goal_id))
        
    conn.commit()
    conn.close()
    
    if awarded_xp:
        add_xp(20) # 20 XP for long-term goal progress

def delete_goal(goal_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM goals WHERE id = ?", (goal_id,))
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

# ==========================================
# DATA BACKUP & RESTORE LOGIC
# ==========================================
def export_data(filepath):
    conn = connect()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, task, completed FROM tasks")
    tasks = [{"id": r[0], "task": r[1], "completed": r[2]} for r in cursor.fetchall()]
    
    cursor.execute("SELECT id, habit_name, streak, last_completed FROM habits")
    habits = [{"id": r[0], "name": r[1], "streak": r[2], "last": r[3]} for r in cursor.fetchall()]
    
    cursor.execute("SELECT id, goal_name, target_amount, current_amount, deadline FROM goals")
    goals = [{"id": r[0], "name": r[1], "target": r[2], "current": r[3], "deadline": r[4]} for r in cursor.fetchall()]
    
    cursor.execute("SELECT xp, level FROM profile WHERE id = 1")
    p_data = cursor.fetchone()
    profile = {"xp": p_data[0], "level": p_data[1]}
    
    conn.close()
    
    data = {"tasks": tasks, "habits": habits, "goals": goals, "profile": profile}
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

def import_data(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
        
    conn = connect()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM tasks")
    cursor.execute("DELETE FROM habits")
    cursor.execute("DELETE FROM goals")
    
    for t in data.get("tasks", []):
        cursor.execute("INSERT INTO tasks (task, completed) VALUES (?, ?)", (t["task"], t["completed"]))
        
    for h in data.get("habits", []):
        cursor.execute("INSERT INTO habits (habit_name, streak, last_completed) VALUES (?, ?, ?)", (h["name"], h["streak"], h["last"]))
        
    for g in data.get("goals", []):
        cursor.execute("INSERT INTO goals (goal_name, target_amount, current_amount, deadline) VALUES (?, ?, ?, ?)", (g["name"], g["target"], g["current"], g["deadline"]))
        
    p = data.get("profile", {"xp": 0, "level": 1})
    cursor.execute("UPDATE profile SET xp = ?, level = ? WHERE id = 1", (p["xp"], p["level"]))
        
    conn.commit()
    conn.close()

create_tables()