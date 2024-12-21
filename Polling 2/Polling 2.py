import tkinter as tk
from tkinter import ttk, StringVar, messagebox
import sqlite3
import matplotlib.pyplot as plt

# Connect to the main SQLite database
conn = sqlite3.connect('polls.db')
cursor = conn.cursor()

# Create a table for storing poll names
cursor.execute("""
CREATE TABLE IF NOT EXISTS poll (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
);
""")
conn.commit()

def create_poll_window():
    def proceed():
        pname = name.get()
        can = cname.get()
        if not pname:
            return messagebox.showerror("Error", "Enter poll name")
        if not can:
            return messagebox.showerror("Error", "Enter candidates")

        # Create a separate database for each poll
        poll_conn = sqlite3.connect(f"{pname}.db")
        poll_cursor = poll_conn.cursor()
        poll_cursor.execute("""
        CREATE TABLE IF NOT EXISTS polling (
            name TEXT,
            votes INTEGER
        );
        """)

        candidates = [c.strip() for c in can.split(",")]
        for candidate in candidates:
            poll_cursor.execute("INSERT INTO polling (name, votes) VALUES (?, ?)", (candidate, 0))
        poll_conn.commit()
        poll_conn.close()

        cursor.execute("INSERT INTO poll (name) VALUES (?);", (pname,))
        conn.commit()

        messagebox.showinfo("Success!", "Poll Created")
        cr.destroy()

    cr = tk.Toplevel(root)
    cr.title("Create Poll")
    cr.geometry("550x300")
    cr.configure(bg="#f0f0f5")

    ttk.Label(cr, text="Enter Poll Name:").grid(row=0, column=0, padx=20, pady=10, sticky="w")
    name = StringVar()
    ttk.Entry(cr, textvariable=name, width=30).grid(row=0, column=1, padx=20, pady=10)

    ttk.Label(cr, text="Enter Candidates (comma-separated):").grid(row=1, column=0, padx=20, pady=10, sticky="w")
    cname = StringVar()
    ttk.Entry(cr, textvariable=cname, width=30).grid(row=1, column=1, padx=20, pady=10)

    ttk.Button(cr, text="Create", command=proceed).grid(row=2, column=1, pady=20)

def vote_window():
    def proceed_to_vote():
        poll_name = poll_choice.get()
        if not poll_name:
            return messagebox.showerror("Error", "Select a poll")

        vote_conn = sqlite3.connect(f"{poll_name}.db")
        vote_cursor = vote_conn.cursor()

        vote_root = tk.Toplevel(root)
        vote_root.title("Vote")
        vote_root.geometry("400x400")
        vote_root.configure(bg="#f0f0f5")

        ttk.Label(vote_root, text=f"Voting for: {poll_name}", font=("Arial", 14)).pack(pady=10)

        def cast_vote(candidate):
            vote_cursor.execute("UPDATE polling SET votes = votes + 1 WHERE name = ?", (candidate,))
            vote_conn.commit()
            messagebox.showinfo("Success", "Your vote has been cast!")
            vote_root.destroy()

        vote_cursor.execute("SELECT name FROM polling")
        candidates = vote_cursor.fetchall()

        for candidate in candidates:
            ttk.Button(vote_root, text=candidate[0], command=lambda c=candidate[0]: cast_vote(c)).pack(pady=5)

        vote_root.protocol("WM_DELETE_WINDOW", lambda: vote_conn.close() or vote_root.destroy())

    polls = cursor.execute("SELECT name FROM poll").fetchall()

    if not polls:
        return messagebox.showerror("Error", "No polls available")

    vote_win = tk.Toplevel(root)
    vote_win.title("Vote")
    vote_win.geometry("400x300")
    vote_win.configure(bg="#f0f0f5")

    ttk.Label(vote_win, text="Select Poll:").pack(pady=10)

    poll_choice = StringVar()
    poll_choice.set("")

    for poll in polls:
        ttk.Radiobutton(vote_win, text=poll[0], value=poll[0], variable=poll_choice).pack(anchor="w", padx=20)

    ttk.Button(vote_win, text="Proceed", command=proceed_to_vote).pack(pady=10)

def show_results_window():
    polls = cursor.execute("SELECT name FROM poll").fetchall()

    if not polls:
        return messagebox.showerror("Error", "No polls available")

    result_win = tk.Toplevel(root)
    result_win.title("Results")
    result_win.geometry("400x300")
    result_win.configure(bg="#f0f0f5")

    ttk.Label(result_win, text="Select Poll:").pack(pady=10)

    poll_choice = StringVar()
    poll_choice.set("")

    for poll in polls:
        ttk.Radiobutton(result_win, text=poll[0], value=poll[0], variable=poll_choice).pack(anchor="w", padx=20)

    def display_results():
        poll_name = poll_choice.get()
        if not poll_name:
            return messagebox.showerror("Error", "Select a poll")

        result_conn = sqlite3.connect(f"{poll_name}.db")
        result_cursor = result_conn.cursor()
        result_cursor.execute("SELECT name, votes FROM polling")
        data = result_cursor.fetchall()
        result_conn.close()

        if not data:
            return messagebox.showerror("Error", "No data available for this poll")

        candidates, votes = zip(*data)
        plt.pie(votes, labels=candidates, autopct="%1.1f%%", colors=plt.cm.Paired.colors)
        plt.title(f"Results for {poll_name}")
        plt.show()

    ttk.Button(result_win, text="Show Results", command=display_results).pack(pady=10)

# Main Window
root = tk.Tk()
root.title("Voting System")
root.geometry("400x250")
root.configure(bg="#e6e6fa")

style = ttk.Style()
style.theme_use("clam")

header_label = ttk.Label(root, text="Welcome to the Voting System", font=("Arial", 16), background="#e6e6fa")
header_label.pack(pady=10)

ttk.Button(root, text="Create Poll", command=create_poll_window).pack(pady=10)
ttk.Button(root, text="Vote", command=vote_window).pack(pady=10)
ttk.Button(root, text="View Results", command=show_results_window).pack(pady=10)

root.mainloop()

# Close the database connection when the application ends
conn.close()
