import customtkinter as ctk
import database
from datetime import date  # NEW: Needed to check today's date in the UI

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class Momentum(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Momentum")
        self.geometry("1000x600")

        # Global Timer State Variables
        self.timer_running = False
        self.time_left = 25 * 60  
        self.timer_id = None

        # --- Sidebar Navigation ---
        self.sidebar = ctk.CTkFrame(self, width=200)
        self.sidebar.pack(side="left", fill="y")

        self.logo = ctk.CTkLabel(
            self.sidebar,
            text="Momentum",
            font=("Arial", 24, "bold")
        )
        self.logo.pack(pady=20)

        self.dashboard_btn = ctk.CTkButton(self.sidebar, text="Dashboard", command=self.show_dashboard)
        self.dashboard_btn.pack(pady=10, padx=10)

        self.tasks_btn = ctk.CTkButton(self.sidebar, text="Tasks", command=self.show_tasks)
        self.tasks_btn.pack(pady=10, padx=10)

        # NEW: Habits Navigation Button
        self.habits_btn = ctk.CTkButton(self.sidebar, text="Habits", command=self.show_habits)
        self.habits_btn.pack(pady=10, padx=10)

        self.timer_btn = ctk.CTkButton(self.sidebar, text="Pomodoro", command=self.show_timer)
        self.timer_btn.pack(pady=10, padx=10)

        # --- Main Content Display Area ---
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.show_dashboard()

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # ==========================================
    # DASHBOARD VIEW
    # ==========================================
    def show_dashboard(self):
        self.clear_frame()
        title = ctk.CTkLabel(self.main_frame, text="Dashboard", font=("Arial", 28, "bold"))
        title.pack(pady=20)
        ctk.CTkLabel(self.main_frame, text="Welcome to Momentum Version 2.0!", font=("Arial", 16)).pack()

    # ==========================================
    # TASKS VIEW
    # ==========================================
    def show_tasks(self):
        self.clear_frame()
        title = ctk.CTkLabel(self.main_frame, text="Tasks", font=("Arial", 28, "bold"))
        title.pack(pady=20)

        self.task_entry = ctk.CTkEntry(self.main_frame, width=300, placeholder_text="Enter task...")
        self.task_entry.pack(pady=10)

        add_btn = ctk.CTkButton(self.main_frame, text="Add Task", command=self.ui_add_task)
        add_btn.pack(pady=5)

        self.tasks_container = ctk.CTkScrollableFrame(self.main_frame, width=600, height=350)
        self.tasks_container.pack(pady=20, fill="both", expand=True)

        self.load_tasks_from_db()

    def load_tasks_from_db(self):
        for widget in self.tasks_container.winfo_children():
            widget.destroy()

        all_tasks = database.get_tasks()

        for task_id, task_text, is_completed in all_tasks:
            row_frame = ctk.CTkFrame(self.tasks_container)
            row_frame.pack(fill="x", pady=5, padx=10)

            checkbox = ctk.CTkCheckBox(
                row_frame, text=task_text, command=lambda t_id=task_id: self.ui_complete_task(t_id)
            )
            checkbox.pack(side="left", padx=10, pady=5)

            if is_completed == 1:
                checkbox.select()
                checkbox.configure(font=("Arial", 13, "overstrike"), text_color="gray")

            delete_btn = ctk.CTkButton(
                row_frame, text="Delete", width=60, fg_color="#A83232", hover_color="#822525",
                command=lambda t_id=task_id: self.ui_delete_task(t_id)
            )
            delete_btn.pack(side="right", padx=10, pady=5)

    def ui_add_task(self):
        task_text = self.task_entry.get().strip()
        if task_text:
            database.add_task(task_text)
            self.task_entry.delete(0, "end")
            self.load_tasks_from_db()

    def ui_complete_task(self, task_id):
        database.complete_task(task_id)
        self.load_tasks_from_db()

    def ui_delete_task(self, task_id):
        database.delete_task(task_id)
        self.load_tasks_from_db()

    # ==========================================
    # HABITS VIEW (NEW)
    # ==========================================
    def show_habits(self):
        self.clear_frame()
        title = ctk.CTkLabel(self.main_frame, text="Habit Tracker", font=("Arial", 28, "bold"))
        title.pack(pady=20)

        self.habit_entry = ctk.CTkEntry(self.main_frame, width=300, placeholder_text="Enter new daily habit...")
        self.habit_entry.pack(pady=10)

        add_btn = ctk.CTkButton(self.main_frame, text="Add Habit", command=self.ui_add_habit)
        add_btn.pack(pady=5)

        self.habits_container = ctk.CTkScrollableFrame(self.main_frame, width=600, height=350)
        self.habits_container.pack(pady=20, fill="both", expand=True)

        self.load_habits_from_db()

    def load_habits_from_db(self):
        for widget in self.habits_container.winfo_children():
            widget.destroy()

        all_habits = database.get_habits()
        today_str = date.today().isoformat()

        for habit_id, habit_name, streak, last_completed in all_habits:
            row_frame = ctk.CTkFrame(self.habits_container)
            row_frame.pack(fill="x", pady=5, padx=10)

            name_label = ctk.CTkLabel(row_frame, text=habit_name, font=("Arial", 16, "bold"))
            name_label.pack(side="left", padx=10, pady=10)

            # Fire emoji logic for visual reward
            streak_text = f"🔥 Streak: {streak}" if streak > 0 else "Streak: 0"
            streak_color = "#FFA500" if streak > 0 else "gray"
            
            streak_label = ctk.CTkLabel(row_frame, text=streak_text, text_color=streak_color, font=("Arial", 14, "bold"))
            streak_label.pack(side="left", padx=20)

            # Button Color and State Logic
            already_done_today = (last_completed == today_str)
            btn_text = "Done Today" if already_done_today else "Check In"
            btn_color = "#2E8B57" if already_done_today else ["#3B8ED0", "#1F6AA5"]
            btn_state = "disabled" if already_done_today else "normal"

            check_btn = ctk.CTkButton(
                row_frame, text=btn_text, width=100, fg_color=btn_color, state=btn_state,
                command=lambda h_id=habit_id: self.ui_check_in_habit(h_id)
            )
            check_btn.pack(side="right", padx=10, pady=5)

            delete_btn = ctk.CTkButton(
                row_frame, text="Drop", width=60, fg_color="#A83232", hover_color="#822525",
                command=lambda h_id=habit_id: self.ui_delete_habit(h_id)
            )
            delete_btn.pack(side="right", padx=10, pady=5)

    def ui_add_habit(self):
        habit_text = self.habit_entry.get().strip()
        if habit_text:
            database.add_habit(habit_text)
            self.habit_entry.delete(0, "end")
            self.load_habits_from_db()

    def ui_check_in_habit(self, habit_id):
        database.check_in_habit(habit_id)
        self.load_habits_from_db()

    def ui_delete_habit(self, habit_id):
        database.delete_habit(habit_id)
        self.load_habits_from_db()

    # ==========================================
    # POMODORO TIMER VIEW
    # ==========================================
    def show_timer(self):
        self.clear_frame()
        title = ctk.CTkLabel(self.main_frame, text="Pomodoro Timer", font=("Arial", 28, "bold"))
        title.pack(pady=20)

        mins, secs = divmod(self.time_left, 60)
        time_string = f"{mins:02d}:{secs:02d}" if self.time_left > 0 else "Time's Up!"

        self.time_label = ctk.CTkLabel(self.main_frame, text=time_string, font=("Arial", 80, "bold"))
        self.time_label.pack(pady=40)

        btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        btn_frame.pack(pady=10)

        btn_text = "Pause" if self.timer_running else "Start"
        btn_color = "#A83232" if self.timer_running else ["#3B8ED0", "#1F6AA5"]

        self.start_btn = ctk.CTkButton(
            btn_frame, text=btn_text, width=100, fg_color=btn_color, command=self.toggle_timer
        )
        self.start_btn.pack(side="left", padx=10)

        reset_btn = ctk.CTkButton(btn_frame, text="Reset", width=100, command=self.reset_timer)
        reset_btn.pack(side="left", padx=10)

    def toggle_timer(self):
        if not self.timer_running:
            self.timer_running = True
            if hasattr(self, 'start_btn') and self.start_btn.winfo_exists():
                self.start_btn.configure(text="Pause", fg_color="#A83232")
            self.update_timer_countdown()
        else:
            self.timer_running = False
            if hasattr(self, 'start_btn') and self.start_btn.winfo_exists():
                self.start_btn.configure(text="Start", fg_color=["#3B8ED0", "#1F6AA5"])
            if self.timer_id:
                self.after_cancel(self.timer_id)

    def update_timer_countdown(self):
        if self.timer_running and self.time_left > 0:
            self.time_left -= 1
            if hasattr(self, 'time_label') and self.time_label.winfo_exists():
                mins, secs = divmod(self.time_left, 60)
                self.time_label.configure(text=f"{mins:02d}:{secs:02d}")
            self.timer_id = self.after(1000, self.update_timer_countdown)
        elif self.time_left == 0:
            self.timer_running = False
            if hasattr(self, 'time_label') and self.time_label.winfo_exists():
                self.time_label.configure(text="Time's Up!")
            if hasattr(self, 'start_btn') and self.start_btn.winfo_exists():
                self.start_btn.configure(text="Start", fg_color=["#3B8ED0", "#1F6AA5"])

    def reset_timer(self):
        self.timer_running = False
        if self.timer_id:
            self.after_cancel(self.timer_id)
        self.time_left = 25 * 60
        if hasattr(self, 'time_label') and self.time_label.winfo_exists():
            self.time_label.configure(text="25:00")
        if hasattr(self, 'start_btn') and self.start_btn.winfo_exists():
            self.start_btn.configure(text="Start", fg_color=["#3B8ED0", "#1F6AA5"])

if __name__ == "__main__":
    app = Momentum()
    app.mainloop()