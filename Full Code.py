import tkinter as tk
from tkinter import ttk, filedialog, Scrollbar, messagebox, Menu
import time
import sqlite3
import csv
import keyboard
from datetime import datetime
import threading
import os


class TimerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Timer App")
        self.master.resizable(False, False)

        # Add menu
        self.menu = Menu(self.master)
        self.master.config(menu=self.menu)

        self.file_menu = Menu(self.menu, tearoff=0, font=("Arial", 12))
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Delete Database", command=self.confirm_delete_database)

        self.time_elapsed = 0.0
        self.timer_running = False
        self._timer_thread = None

        self.display_var = tk.StringVar()
        self.display_var.set("0:00:00.0")
        self.display = tk.Label(self.master, textvariable=self.display_var, font=("Arial", 48))
        self.display.grid(row=0, column=0, columnspan=5, pady=10)

        self.create_buttons()

        self.task_desc = tk.Entry(self.master, font=("Arial", 20))
        self.task_desc.grid(row=3, column=0, columnspan=5, pady=10)

        # Adjusting the size of the listbox and adding a y-scrollbar
        self.db_listbox = tk.Listbox(self.master, font=("Arial", 20), height=10, width=30, selectmode=tk.MULTIPLE)
        self.db_listbox.grid(row=5, column=0, columnspan=5, pady=10, sticky='ew')

        self.scrollbar = Scrollbar(self.master, command=self.db_listbox.yview, width=12)
        self.scrollbar.grid(row=5, column=5, sticky="ns", pady=10, padx=(0, 10))
        self.db_listbox.config(yscrollcommand=self.scrollbar.set)

        self.conn = sqlite3.connect("time_data.db")
        self.c = self.conn.cursor()
        self.c.execute("CREATE TABLE IF NOT EXISTS times (date TEXT, time TEXT, time_elapsed TEXT, task TEXT)")
        self.conn.commit()

        self.update_db_listbox()

    def create_buttons(self):
        self.create_button("Start", self.start_timer, 1, 0, "<Control-Shift-s>")
        self.create_button("Stop", self.stop_timer, 1, 1, "<Control-Shift-d>")
        self.create_button("Save Entry", self.save_time, 1, 2, "<Control-Shift-a>")
        self.create_button("Reset", self.reset_timer, 1, 3, "<Control-Shift-f>")
        self.create_button("Delete Entry", self.delete_entry, 6, 1, "<Control-Shift-e>")
        self.create_button("Show Entries", self.show_all_entries, 6, 2, "<Control-Shift-o>")
        self.create_button("Clear Listbox", self.clear_listbox, 6, 3, "<Control-Shift-x>")
        self.create_button("Export to CSV", self.download_csv, 6, 4, "<Control-Shift-v>")

    def create_button(self, text, command, row, col, key_combination):
        button_frame = tk.Frame(self.master)
        button_frame.grid(row=row, column=col, sticky='nsew', padx=10, pady=5)

        button = tk.Button(button_frame, text=text, command=command, font=("Arial", 20), relief="raised")
        button.pack(fill=tk.BOTH, expand=True)

        key_label = tk.Label(button_frame, text=key_combination, font=("Arial", 10), fg="gray")
        key_label.pack(side=tk.BOTTOM)

        button.bind("<ButtonPress-1>", lambda e: button.config(relief="sunken"))
        button.bind("<ButtonRelease-1>", lambda e: button.config(relief="raised"))

        return button

    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self._timer_thread = threading.Thread(target=self.update_timer)
            self._timer_thread.start()

    def stop_timer(self):
        self.timer_running = False
        if self._timer_thread:
            self._timer_thread.join()

    def update_timer(self):
        while self.timer_running:
            self.time_elapsed += 0.1
            mins, sec = divmod(int(self.time_elapsed), 60)
            hours, mins = divmod(mins, 60)
            self.display_var.set(f"{hours}:{mins:02d}:{sec:02d}.{int((self.time_elapsed * 10) % 10)}")
            time.sleep(0.1)

    def save_time(self):
        task = self.task_desc.get()
        current_datetime = datetime.now()
        date = current_datetime.strftime("%Y-%m-%d")
        time = current_datetime.strftime("%H:%M:%S")
        self.c.execute("INSERT INTO times (date, time, time_elapsed, task) VALUES (?, ?, ?, ?)",
                       (date, time, self.display_var.get(), task))
        self.conn.commit()
        self.update_db_listbox()

    def reset_timer(self):
        self.stop_timer()
        self.time_elapsed = 0.0
        self.display_var.set("0:00:00.0")

    def clear_listbox(self):
        self.db_listbox.delete(0, tk.END)

    def show_all_entries(self):
        self.update_db_listbox()

    def delete_entry(self):
        selected_indices = self.db_listbox.curselection()
        for index in selected_indices:
            entry = self.db_listbox.get(index)
            entry_data = entry.split(" | ")
            if len(entry_data) == 4:
                self.c.execute("DELETE FROM times WHERE date=? AND time=? AND time_elapsed=? AND task=?",
                               (entry_data[0], entry_data[1], entry_data[2], entry_data[3]))
                self.conn.commit()
            else:
                print(f"Unexpected data format for entry: {entry}")

        self.update_db_listbox()

    def confirm_delete_database(self):
        response = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete the entire database?")
        if response:
            self.delete_database_file()

    def delete_database_file(self):
        # Close the SQLite connection
        self.conn.close()
        if os.path.exists("time_data.db"):
            os.remove("time_data.db")
            messagebox.showinfo("Database Deleted", "The database file has been deleted successfully.")

            # Reconnect to the database after deletion
            self.conn = sqlite3.connect("time_data.db")
            self.c = self.conn.cursor()
            self.c.execute("CREATE TABLE IF NOT EXISTS times (date TEXT, time TEXT, time_elapsed TEXT, task TEXT)")
        else:
            messagebox.showwarning("File Not Found", "The database file does not exist.")

    def download_csv(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if filepath:
            with open(filepath, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Date", "Time", "Time Elapsed", "Task"])
                self.c.execute("SELECT * FROM times")
                for row in self.c.fetchall():
                    writer.writerow(row)

    def update_db_listbox(self):
        self.db_listbox.delete(0, tk.END)
        self.c.execute("SELECT * FROM times")
        for row in self.c.fetchall():
            entry = " | ".join(str(item) for item in row)
            self.db_listbox.insert(tk.END, entry)


if __name__ == "__main__":
    root = tk.Tk()
    app = TimerApp(root)
    root.mainloop()
