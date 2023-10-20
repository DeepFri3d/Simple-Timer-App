import tkinter as tk
from tkinter import ttk, filedialog, Scrollbar, messagebox
import time
import sqlite3
import csv
import keyboard
from datetime import datetime
import threading


class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.show_id = None
        self.hide_id = None

        self.widget.bind("<Enter>", self.schedule_show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def schedule_show_tooltip(self, event=None):
        if not self.show_id:
            self.show_id = self.widget.after(500, self.show_tooltip)

    def show_tooltip(self):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tooltip, text=self.text, background="yellow")
        label.pack()

        # Schedule the hide tooltip after 1 second
        if not self.hide_id:
            self.hide_id = self.widget.after(1000, self.hide_tooltip)

    def hide_tooltip(self, event=None):
        if self.show_id:
            self.widget.after_cancel(self.show_id)
            self.show_id = None
        if self.hide_id:
            self.widget.after_cancel(self.hide_id)
            self.hide_id = None
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None


class TimerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Timer App")
        self.master.resizable(False, False)  # Disabling window resizing

        self.time_elapsed = 0.0
        self.timer_running = False
        self._timer_thread = None

        self.display_var = tk.StringVar()
        self.display_var.set("0:00:00.0")
        self.display = tk.Label(self.master, textvariable=self.display_var, font=("Arial", 48))
        self.display.grid(row=0, columnspan=5)

        self.create_buttons()

        # Keyboard library hotkey bindings
        keyboard.add_hotkey('ctrl+shift+s', self.start_timer)
        keyboard.add_hotkey('ctrl+shift+d', self.stop_timer)
        keyboard.add_hotkey('ctrl+shift+f', self.reset_timer)
        keyboard.add_hotkey('ctrl+shift+a', self.save_time)
        keyboard.add_hotkey('ctrl+shift+c', self.delete_entry)
        keyboard.add_hotkey('ctrl+shift+v', self.download_csv)
        keyboard.add_hotkey('ctrl+shift+l', lambda: self.task_desc.focus())  # Focus on the task description entry
        keyboard.add_hotkey('ctrl+shift+e', self.delete_entry)
        keyboard.add_hotkey('ctrl+shift+x', self.clear_listbox)
        keyboard.add_hotkey('ctrl+shift+o', self.show_all_entries)

        self.csv_button = tk.Button(self.master, text="Save CSV", command=self.download_csv, font=("Arial", 20))
        self.csv_button.grid(row=2, columnspan=5)

        self.task_desc = tk.Entry(self.master, font=("Arial", 20))
        self.task_desc.grid(row=3, columnspan=5)

        # Using Text widget instead of Listbox for wrapping text
        self.db_textbox = tk.Text(self.master, font=("Arial", 20), height=10, width=50, wrap=tk.WORD, state=tk.DISABLED)
        self.db_textbox.grid(row=4, columnspan=5)

        # Adding scrollbar for the Text widget
        self.scrollbar = Scrollbar(self.master, command=self.db_textbox.yview)
        self.scrollbar.grid(row=4, column=5, sticky="nsew")
        self.db_textbox.config(yscrollcommand=self.scrollbar.set)

        self.conn = sqlite3.connect("time_data.db")
        self.c = self.conn.cursor()
        self.c.execute("CREATE TABLE IF NOT EXISTS times (date TEXT, time_elapsed TEXT, task TEXT)")
        self.conn.commit()

        self.update_db_listbox()

    def create_button(self, text, command, row, col, key_combination):
        button_frame = tk.Frame(self.master)
        button_frame.grid(row=row, column=col, sticky='nsew')

        button = tk.Button(button_frame, text=text, command=command, font=("Arial", 20), relief="raised")
        button.pack(pady=10)

        key_label = tk.Label(button_frame, text=key_combination, font=("Arial", 10), fg="gray")
        key_label.pack()

        button.bind("<ButtonPress-1>", lambda e: button.config(relief="sunken"))
        button.bind("<ButtonRelease-1>", lambda e: button.config(relief="raised"))

        return button

    def create_buttons(self):
        self.create_button("Start", self.start_timer, 1, 0, "<Control-Shift-s>")
        self.create_button("Stop", self.stop_timer, 1, 1, "<Control-Shift-d>")
        self.create_button("Save", self.save_time, 1, 2, "<Control-Shift-a>")
        self.create_button("Reset", self.reset_timer, 1, 3, "<Control-Shift-f>")
        self.create_button("Clear Entry", self.delete_entry, 1, 4, "<Control-Shift-c>")
        self.create_button("Delete Entry", self.delete_entry, 6, 0, "<Control-Shift-e>")
        self.create_button("Show Listbox", self.show_all_entries, 6, 1, "<Control-Shift-o>")
        self.create_button("Clear Listbox", self.clear_listbox, 6, 2, "<Control-Shift-x>")

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
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.c.execute("INSERT INTO times (date, time_elapsed, task) VALUES (?, ?, ?)",
                       (date, self.display_var.get(), task))
        self.conn.commit()
        self.update_db_listbox()

    def reset_timer(self):
        self.stop_timer()
        self.time_elapsed = 0.0
        self.display_var.set("0:00:00.0")

    def clear_listbox(self):
        self.db_textbox.configure(state=tk.NORMAL)
        self.db_textbox.delete(1.0, tk.END)
        self.db_textbox.configure(state=tk.DISABLED)

    def show_all_entries(self):
        self.master.after(0, self._show_all_entries_db)

    def _show_all_entries_db(self):
        self.db_textbox.configure(state=tk.NORMAL)
        self.db_textbox.delete(1.0, tk.END)

        self.c.execute("SELECT * FROM times")
        for row in self.c.fetchall():
            entry = " | ".join(str(item) for item in row)
            self.db_textbox.insert(tk.END, entry + "\n")
        self.db_textbox.configure(state=tk.DISABLED)

    def delete_entry(self):
        try:
            selected_text = self.db_textbox.selection_get()
            if not selected_text:
                return
            confirmation = messagebox.askyesno("Delete Entry", "Are you sure you want to delete the selected entry?")
            if confirmation:
                selected_data = selected_text.split(" | ")
                self.c.execute("DELETE FROM times WHERE date=? AND time_elapsed=? AND task=?",
                               (selected_data[0], selected_data[1], selected_data[2]))
                self.conn.commit()
                self.update_db_listbox()
        except tk.TclError:
            messagebox.showwarning("No Entry Selected", "Please select an entry to delete.")

    def download_csv(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if filepath:
            with open(filepath, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Date", "Time Elapsed", "Task"])
                self.c.execute("SELECT * FROM times")
                for row in self.c.fetchall():
                    writer.writerow(row)

    def update_db_listbox(self):
        today = datetime.now().strftime("%Y-%m-%d")
        self.db_textbox.configure(state=tk.NORMAL)
        self.db_textbox.delete(1.0, tk.END)
        self.c.execute("SELECT * FROM times WHERE date LIKE ?", (f"{today}%",))
        for row in self.c.fetchall():
            entry = " | ".join(str(item) for item in row)
            self.db_textbox.insert(tk.END, entry + "\n")
        self.db_textbox.configure(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = TimerApp(root)
    root.mainloop()
