import tkinter as tk
from tkinter import messagebox, filedialog
from zxcvbn import zxcvbn
import itertools

BG_MAIN      = "#201133"
ACCENT_PURP  = "#6c41a1"
ACCENT_BLUE  = "#1defff"
ACCENT_GRN   = "#30e67a"
WARN_COLOR   = "#da277a"
OK_COLOR     = "#ffd157"
STRONG_COLOR = "#7aecb8"
FONT_MAIN    = ("Consolas", 12)
FONT_LG      = ("Consolas", 16, "bold")
FONT_TITLE   = ("Consolas", 18, "bold")

ASCII_LOGO = r"""
╔═════════════════════════════════════╗
║        PassDefender ToolKit        ║
╚═════════════════════════════════════╝
"""

common_words = {"password", "qwerty", "letmein", "admin", "welcome"}

def analyze_password():
    pwd = password_entry.get()
    if not pwd:
        messagebox.showerror("Error", "Please enter a password.")
        return
    result = zxcvbn(pwd)
    score = result["score"]
    guesses = result["guesses"]
    feedback = result.get("feedback", {})
    crack_time = result["crack_times_display"]["offline_fast_hashing_1e10_per_second"]

    issues = []
    if score <= 1:
        if len(pwd) < 8: issues.append("Password is too short (<8 chars).")
        if pwd.lower() in common_words: issues.append("Password is a common word.")
        if pwd.isdigit(): issues.append("Password only contains numbers.")
        if pwd.islower(): issues.append("No uppercase letters present.")
        if pwd.isalpha() and pwd.islower(): issues.append("Password contains only lowercase letters.")
        if pwd.isalpha(): issues.append("No digits or special characters used.")
    elif score <= 2:
        if not any(c.isupper() for c in pwd): issues.append("Try adding uppercase letters.")
        if not any(c.isdigit() for c in pwd): issues.append("Consider adding numbers.")
        if not any(not c.isalnum() for c in pwd): issues.append("Try adding special characters (!@# etc).")

    suggestions = []
    if feedback.get("warning"): suggestions.append(feedback["warning"])
    if feedback.get("suggestions"): suggestions += feedback["suggestions"]

    strength_labels = [
        ("Very Weak", WARN_COLOR),
        ("Weak", WARN_COLOR),
        ("Fair", OK_COLOR),
        ("Good", STRONG_COLOR),
        ("Strong", ACCENT_GRN)
    ]
    label, color = strength_labels[score]
    strength_label.config(text=f"Strength: {label}    [Score: {score}/4, Guesses: {guesses:,}]", fg=color)
    details_text.config(state="normal")
    details_text.delete(1.0, tk.END)
    details_text.insert(tk.END, f"Estimated crack time: {crack_time}\n", "main")
    if issues:
        details_text.insert(tk.END, "\nIssues:\n", "warn")
        for iss in issues: details_text.insert(tk.END, f" • {iss}\n", "warn")
    if suggestions:
        details_text.insert(tk.END, "\nSuggestions:\n", "ok")
        for sug in suggestions: details_text.insert(tk.END, f" • {sug}\n", "ok")
    if not issues and not suggestions:
        details_text.insert(tk.END, "\nNo issues detected — This is a strong password!", "strong")
    details_text.config(state="disabled")

def toggle_password():
    if password_entry.cget('show') == '*':
        password_entry.config(show='')
        show_button.config(text='Hide')
    else:
        password_entry.config(show='*')
        show_button.config(text='Show')

def generate_wordlist():
    name = name_entry.get().strip().lower()
    pet = pet_entry.get().strip().lower()
    year = year_entry.get().strip()
    place = place_entry.get().strip().lower()
    number = number_entry.get().strip()
    base = [w for w in [name, pet, year, place, number] if w]

    if not base:
        messagebox.showerror("Error", "Enter at least one field to generate a wordlist.")
        return

    wordlist = set(base)
    suffixes = ["", "123", "!", "?", "@", "_", "2025", "2024"]
    leet_map = {"a": "4", "e": "3", "i": "1", "o": "0", "s": "5"}

    for w in base:
        for suf in suffixes:
            wordlist.add(w + suf)
            wordlist.add(w.capitalize() + suf)
            wordlist.add(w.upper() + suf)
        leet = "".join(leet_map.get(c, c) for c in w)
        wordlist.add(leet)
        wordlist.add(leet.capitalize())
        wordlist.add(w[::-1])

    for n in range(2, min(4, len(base)+1)):
        for combo in itertools.permutations(base, n):
            joined = "".join(combo)
            wordlist.add(joined)
            wordlist.add(joined[::-1])
            for suf in suffixes:
                wordlist.add(joined + suf)

    # Show full wordlist in scrollable box!
    preview_text.config(state="normal")
    preview_text.delete(1.0, tk.END)
    # Sorted for readability
    for word in sorted(wordlist):
        preview_text.insert(tk.END, word + "\n")
    preview_text.insert(tk.END, f"\nTotal combinations: {len(wordlist)}\n", "ok")
    preview_text.config(state="disabled")

def export_wordlist():
    preview_text.config(state="normal")
    contents = preview_text.get(1.0, tk.END).strip().split('\n')
    preview_text.config(state="disabled")
    if len(contents) < 2:
        messagebox.showerror("Error", "No wordlist generated yet!")
        return
    filepath = filedialog.asksaveasfilename(defaultextension=".txt", title="Save Wordlist")
    if filepath:
        with open(filepath, "w") as f:
            for word in contents:
                if word and not word.startswith('Total combinations'):
                    f.write(word + "\n")
        messagebox.showinfo("Saved", f"Wordlist saved to:\n{filepath}")

def clear_analyzer():
    password_entry.delete(0, tk.END)
    strength_label.config(text="Strength:?")
    details_text.config(state="normal")
    details_text.delete(1.0, tk.END)
    details_text.config(state="disabled")

def clear_wordlist():
    for ent in (name_entry, pet_entry, year_entry, place_entry, number_entry):
        ent.delete(0, tk.END)
    preview_text.config(state="normal")
    preview_text.delete(1.0, tk.END)
    preview_text.config(state="disabled")

root = tk.Tk()
root.title("PassDefender ToolKit")
root.config(bg=BG_MAIN)
root.geometry("900x550")

# Small, colored logo
ascii_label = tk.Label(root, text=ASCII_LOGO, bg=BG_MAIN, fg=ACCENT_BLUE, font=FONT_TITLE)
ascii_label.pack(pady=(7, 0))

pw_frame = tk.LabelFrame(root, text="Password Strength Analyzer", font=FONT_LG, bg=BG_MAIN, fg=ACCENT_GRN, bd=2)
pw_frame.pack(fill="x", padx=30, pady=10)

tk.Label(pw_frame, text="Enter Password:", font=FONT_MAIN, bg=BG_MAIN, fg=ACCENT_PURP).grid(row=0, column=0, sticky="e", padx=5, pady=5)
password_entry = tk.Entry(pw_frame, show="*", font=FONT_MAIN, width=38, bg="#381847", fg=ACCENT_GRN, insertbackground=ACCENT_GRN)
password_entry.grid(row=0, column=1, sticky="w", padx=5)

show_button = tk.Button(pw_frame, text="Show", font=FONT_MAIN, command=toggle_password, bg=ACCENT_BLUE, fg=BG_MAIN)
show_button.grid(row=0, column=2, padx=4)

tk.Button(pw_frame, text="Analyze", font=FONT_MAIN, command=analyze_password, bg=ACCENT_GRN, fg=BG_MAIN, activebackground=ACCENT_GRN).grid(row=0, column=3, padx=10)
tk.Button(pw_frame, text="Clear", font=FONT_MAIN, command=clear_analyzer, bg=ACCENT_PURP, fg=ACCENT_GRN, activebackground=ACCENT_PURP).grid(row=0, column=4, padx=5)

strength_label = tk.Label(pw_frame, text="Strength: ?", font=FONT_MAIN, bg=BG_MAIN, fg=ACCENT_GRN)
strength_label.grid(row=1, column=0, columnspan=5, pady=5)

details_text = tk.Text(pw_frame, height=6, width=100, font=("Consolas", 10), bg="#150825", fg=ACCENT_BLUE, wrap="word", cursor="target")
details_text.tag_configure("warn", foreground=WARN_COLOR)
details_text.tag_configure("ok", foreground=OK_COLOR)
details_text.tag_configure("strong", foreground=STRONG_COLOR)
details_text.tag_configure("main", foreground=ACCENT_BLUE)
details_text.config(state="disabled")
details_text.grid(row=2, column=0, columnspan=5, pady=5)

# --- Wordlist Generator ---
wl_frame = tk.LabelFrame(root, text="Custom Wordlist Generator", font=FONT_LG, bg=BG_MAIN, fg=ACCENT_BLUE, bd=2)
wl_frame.pack(fill="x", padx=30, pady=10)

labels = ["Name:", "Pet/Nickname:", "Birth Year:", "Favorite Place:", "Favorite Number:"]
for i, lbl in enumerate(labels):
    tk.Label(wl_frame, text=lbl, font=FONT_MAIN, bg=BG_MAIN, fg=ACCENT_PURP).grid(row=i, column=0, sticky="e", padx=5, pady=3)
name_entry = tk.Entry(wl_frame, font=FONT_MAIN, width=22, bg="#321141", fg=ACCENT_GRN, insertbackground=ACCENT_GRN)
pet_entry = tk.Entry(wl_frame, font=FONT_MAIN, width=22, bg="#321141", fg=ACCENT_GRN, insertbackground=ACCENT_GRN)
year_entry = tk.Entry(wl_frame, font=FONT_MAIN, width=22, bg="#321141", fg=ACCENT_GRN, insertbackground=ACCENT_GRN)
place_entry = tk.Entry(wl_frame, font=FONT_MAIN, width=22, bg="#321141", fg=ACCENT_GRN, insertbackground=ACCENT_GRN)
number_entry = tk.Entry(wl_frame, font=FONT_MAIN, width=22, bg="#321141", fg=ACCENT_GRN, insertbackground=ACCENT_GRN)
ents = [name_entry, pet_entry, year_entry, place_entry, number_entry]
for i, ent in enumerate(ents):
    ent.grid(row=i, column=1, sticky="w", padx=2, pady=3)

tk.Button(wl_frame, text="Generate Wordlist", font=FONT_MAIN, command=generate_wordlist, bg=ACCENT_GRN, fg=BG_MAIN, activebackground=ACCENT_GRN).grid(row=0, column=2, rowspan=2, padx=18)
tk.Button(wl_frame, text="Export Wordlist", font=FONT_MAIN, command=export_wordlist, bg=ACCENT_BLUE, fg=BG_MAIN, activebackground=ACCENT_BLUE).grid(row=1, column=2, rowspan=2, padx=18)
tk.Button(wl_frame, text="Clear", font=FONT_MAIN, command=clear_wordlist, bg=ACCENT_PURP, fg=ACCENT_GRN, activebackground=ACCENT_PURP).grid(row=2, column=2, rowspan=2, padx=18)

# -- Scrollable preview box --
preview_frame = tk.Frame(wl_frame, bg=BG_MAIN)
preview_frame.grid(row=5, column=0, columnspan=3, pady=(6,0))
preview_text = tk.Text(preview_frame, height=9, width=70, font=("Consolas", 10, "bold"), bg="#150825", fg=ACCENT_BLUE, wrap="word")
preview_text.tag_configure("ok", foreground=ACCENT_GRN)
scrollbar = tk.Scrollbar(preview_frame, command=preview_text.yview)
preview_text.configure(yscrollcommand=scrollbar.set)
preview_text.config(state="disabled")
preview_text.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

root.mainloop()
