
import tkinter as tk
from tkinter import messagebox
from database import register_user, login_user
from discovery import PeerDiscovery

# ==============================
# APPLICATION COLORS
# ==============================

BG = "#F5F0EA"
PURPLE = "#580F41"
DARK = "#35102B"
WHITE = "#FFFFFF"
GRAY = "#777777"
LIGHT_PURPLE = "#EFE5ED"
GREEN = "#24845B"
RED = "#B83232"

# ==============================
# GLOBAL VARIABLES
# ==============================

discovery = None
online_peers = {}

peers_listbox = None
status_label = None
count_label = None

# ==============================
# MAIN WINDOW
# ==============================

root = tk.Tk()
root.title("P2P Messaging Platform")
root.geometry("850x650")
root.minsize(750, 550)
root.configure(bg=BG)

main_frame = tk.Frame(root, bg=BG)
main_frame.pack(fill="both", expand=True)

def clear_screen():
    for widget in main_frame.winfo_children():
        widget.destroy()

# ==============================
# DISCOVERY FUNCTIONS
# ==============================

def on_discovery_event(event, peer):
    """
    This callback runs in the discovery background thread.
    root.after() safely transfers UI updates to Tkinter.
    """
    root.after(0, handle_peer_event, event, peer)

def handle_peer_event(event, peer):
    peer_id = peer["peer_id"]

    if event == "online":
        online_peers[peer_id] = peer.copy()

    elif event == "offline":
        online_peers.pop(peer_id, None)

    refresh_peer_list()

def refresh_peer_list():
    if peers_listbox is None:
        return

    if not peers_listbox.winfo_exists():
        return

    peers_listbox.delete(0, tk.END)

    peers = sorted(
        online_peers.values(),
        key=lambda item: item["email"].lower()
    )

    for peer in peers:
        line = (
            f"  {peer['email']}    |    "
            f"IP: {peer['ip']}    |    "
            f"Port: {peer['chat_port']}"
        )
        peers_listbox.insert(tk.END, line)

    if count_label and count_label.winfo_exists():
        count_label.config(
            text=f"Connected users: {len(peers)}"
        )

def start_discovery(email):
    global discovery

    if discovery is not None and discovery.running:
        return

    online_peers.clear()
    refresh_peer_list()

    try:
        discovery = PeerDiscovery(
            email=email,
            callback=on_discovery_event
        )

        discovery.start()

        if status_label and status_label.winfo_exists():
            status_label.config(
                text="● Discovery Running",
                fg=GREEN
            )

        # Display peers already discovered
        for peer in discovery.get_peers():
            online_peers[peer["peer_id"]] = peer

        refresh_peer_list()

    except (RuntimeError, OSError) as error:
        discovery = None

        if status_label and status_label.winfo_exists():
            status_label.config(
                text="● Discovery Stopped",
                fg=RED
            )

        messagebox.showerror(
            "Discovery Error",
            str(error)
        )

def stop_discovery():
    global discovery

    if discovery is not None:
        discovery.stop()
        discovery = None

    online_peers.clear()
    refresh_peer_list()

    if status_label and status_label.winfo_exists():
        status_label.config(
            text="● Discovery Stopped",
            fg=RED
        )

# ==============================
# LOGIN PAGE
# ==============================

def show_login():

    stop_discovery()
    clear_screen()

    card = tk.Frame(
        main_frame,
        bg=WHITE,
        padx=45,
        pady=35
    )
    card.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(
        card,
        text="P2P MESSAGING",
        font=("Arial", 23, "bold"),
        fg=PURPLE,
        bg=WHITE
    ).pack(pady=(0, 8))

    tk.Label(
        card,
        text="Welcome back!",
        font=("Arial", 17, "bold"),
        bg=WHITE,
        fg=DARK
    ).pack(pady=5)

    tk.Label(
        card,
        text="Sign in to continue to your account",
        font=("Arial", 10),
        bg=WHITE,
        fg=GRAY
    ).pack(pady=(0, 25))

    tk.Label(
        card,
        text="Email address",
        bg=WHITE,
        fg=DARK,
        font=("Arial", 10, "bold")
    ).pack(anchor="w")

    email_entry = tk.Entry(
        card,
        width=38,
        font=("Arial", 12),
        bg=BG,
        relief="flat"
    )
    email_entry.pack(ipady=10, pady=(5, 15))

    tk.Label(
        card,
        text="Password",
        bg=WHITE,
        fg=DARK,
        font=("Arial", 10, "bold")
    ).pack(anchor="w")

    password_entry = tk.Entry(
        card,
        width=38,
        font=("Arial", 12),
        bg=BG,
        relief="flat",
        show="*"
    )
    password_entry.pack(ipady=10, pady=(5, 8))

    show_password = tk.BooleanVar(value=False)

    def toggle_password():
        password_entry.config(
            show="" if show_password.get() else "*"
        )

    tk.Checkbutton(
        card,
        text="Show password",
        variable=show_password,
        command=toggle_password,
        bg=WHITE,
        fg=GRAY,
        activebackground=WHITE
    ).pack(anchor="w", pady=(0, 15))

    def login():

        email = email_entry.get().strip()
        password = password_entry.get()

        if not email or not password:
            messagebox.showwarning(
                "Missing information",
                "Please enter your email and password."
            )
            return

        if not login_user(email, password):
            messagebox.showerror(
                "Login failed",
                "Incorrect email or password."
            )
            return

        messagebox.showinfo(
            "Success",
            "Login successful!"
        )

        show_home(email)

    tk.Button(
        card,
        text="LOGIN",
        command=login,
        bg=PURPLE,
        fg=WHITE,
        activebackground=DARK,
        activeforeground=WHITE,
        font=("Arial", 12, "bold"),
        relief="flat",
        cursor="hand2",
        width=34,
        pady=12
    ).pack(pady=10)

    bottom = tk.Frame(card, bg=WHITE)
    bottom.pack(pady=(15, 0))

    tk.Label(
        bottom,
        text="Don't have an account?",
        bg=WHITE,
        fg=GRAY,
        font=("Arial", 10)
    ).pack(side="left")

    tk.Button(
        bottom,
        text="Register",
        command=show_register,
        bg=WHITE,
        fg=PURPLE,
        relief="flat",
        font=("Arial", 10, "bold"),
        cursor="hand2"
    ).pack(side="left")

# ==============================
# REGISTER PAGE
# ==============================

def show_register():

    clear_screen()

    card = tk.Frame(
        main_frame,
        bg=WHITE,
        padx=45,
        pady=30
    )
    card.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(
        card,
        text="CREATE ACCOUNT",
        font=("Arial", 22, "bold"),
        fg=PURPLE,
        bg=WHITE
    ).pack(pady=(0, 8))

    tk.Label(
        card,
        text="Join our P2P messaging platform",
        font=("Arial", 10),
        bg=WHITE,
        fg=GRAY
    ).pack(pady=(0, 20))

    tk.Label(
        card,
        text="Email address",
        bg=WHITE,
        fg=DARK,
        font=("Arial", 10, "bold")
    ).pack(anchor="w")

    email_entry = tk.Entry(
        card,
        width=38,
        font=("Arial", 12),
        bg=BG,
        relief="flat"
    )
    email_entry.pack(ipady=9, pady=(5, 12))

    tk.Label(
        card,
        text="Password (minimum 8 characters)",
        bg=WHITE,
        fg=DARK,
        font=("Arial", 10, "bold")
    ).pack(anchor="w")

    password_entry = tk.Entry(
        card,
        width=38,
        font=("Arial", 12),
        bg=BG,
        relief="flat",
        show="*"
    )
    password_entry.pack(ipady=9, pady=(5, 12))

    tk.Label(
        card,
        text="Confirm password",
        bg=WHITE,
        fg=DARK,
        font=("Arial", 10, "bold")
    ).pack(anchor="w")

    confirm_entry = tk.Entry(
        card,
        width=38,
        font=("Arial", 12),
        bg=BG,
        relief="flat",
        show="*"
    )
    confirm_entry.pack(ipady=9, pady=(5, 12))

    show_password = tk.BooleanVar(value=False)

    def toggle_password():
        visibility = "" if show_password.get() else "*"
        password_entry.config(show=visibility)
        confirm_entry.config(show=visibility)

    tk.Checkbutton(
        card,
        text="Show passwords",
        variable=show_password,
        command=toggle_password,
        bg=WHITE,
        fg=GRAY,
        activebackground=WHITE
    ).pack(anchor="w", pady=(0, 10))

    def register():

        email = email_entry.get().strip()
        password = password_entry.get()
        confirm = confirm_entry.get()

        if not email or not password or not confirm:
            messagebox.showwarning(
                "Missing information",
                "Please complete all fields."
            )
            return

        if "@" not in email or "." not in email.split("@")[-1]:
            messagebox.showwarning(
                "Invalid email",
                "Please enter a valid email address."
            )
            return

        if password != confirm:
            messagebox.showerror(
                "Password error",
                "Passwords do not match."
            )
            return

        success, message = register_user(email, password)

        if success:
            messagebox.showinfo(
                "Registration",
                message
            )
            show_login()
        else:
            messagebox.showerror(
                "Registration failed",
                message
            )

    tk.Button(
        card,
        text="CREATE ACCOUNT",
        command=register,
        bg=PURPLE,
        fg=WHITE,
        activebackground=DARK,
        activeforeground=WHITE,
        font=("Arial", 11, "bold"),
        relief="flat",
        cursor="hand2",
        width=34,
        pady=11
    ).pack(pady=8)

    tk.Button(
        card,
        text="Back to Login",
        command=show_login,
        bg=WHITE,
        fg=PURPLE,
        font=("Arial", 10, "bold"),
        relief="flat",
        cursor="hand2"
    ).pack(pady=5)

# ==============================
# HOME PAGE
# ==============================

def show_home(email):

    global peers_listbox
    global status_label
    global count_label

    clear_screen()

    header = tk.Frame(
        main_frame,
        bg=PURPLE,
        height=85
    )
    header.pack(fill="x")
    header.pack_propagate(False)

    tk.Label(
        header,
        text="P2P MESSAGING PLATFORM",
        bg=PURPLE,
        fg=WHITE,
        font=("Arial", 19, "bold")
    ).pack(side="left", padx=25, pady=25)

    content = tk.Frame(
        main_frame,
        bg=BG,
        padx=35,
        pady=20
    )
    content.pack(expand=True, fill="both")

    tk.Label(
        content,
        text="Welcome!",
        font=("Arial", 25, "bold"),
        bg=BG,
        fg=PURPLE
    ).pack(pady=(5, 5))

    tk.Label(
        content,
        text=email,
        font=("Arial", 11),
        bg=BG,
        fg=GRAY
    ).pack(pady=(0, 15))

    # Discovery status
    status_label = tk.Label(
        content,
        text="● Discovery Starting...",
        font=("Arial", 11, "bold"),
        bg=BG,
        fg=GRAY
    )
    status_label.pack(pady=5)

    # Online users section
    users_frame = tk.Frame(
        content,
        bg=WHITE,
        padx=15,
        pady=12
    )
    users_frame.pack(fill="both", expand=True, pady=12)

    tk.Label(
        users_frame,
        text="ONLINE USERS",
        font=("Arial", 15, "bold"),
        bg=WHITE,
        fg=PURPLE
    ).pack(anchor="w", pady=(0, 5))

    count_label = tk.Label(
        users_frame,
        text="Connected users: 0",
        font=("Arial", 10),
        bg=WHITE,
        fg=GRAY
    )
    count_label.pack(anchor="w", pady=(0, 10))

    list_frame = tk.Frame(users_frame, bg=WHITE)
    list_frame.pack(fill="both", expand=True)

    scrollbar = tk.Scrollbar(list_frame)
    scrollbar.pack(side="right", fill="y")

    peers_listbox = tk.Listbox(
        list_frame,
        font=("Arial", 10),
        bg=BG,
        fg=DARK,
        relief="flat",
        selectbackground=LIGHT_PURPLE,
        yscrollcommand=scrollbar.set,
        height=8
    )
    peers_listbox.pack(side="left", fill="both", expand=True)

    scrollbar.config(command=peers_listbox.yview)

    # Discovery buttons
    buttons_frame = tk.Frame(content, bg=BG)
    buttons_frame.pack(pady=8)

    tk.Button(
        buttons_frame,
        text="START DISCOVERY",
        command=lambda: start_discovery(email),
        bg=GREEN,
        fg=WHITE,
        font=("Arial", 10, "bold"),
        relief="flat",
        cursor="hand2",
        padx=15,
        pady=9
    ).pack(side="left", padx=7)

    tk.Button(
        buttons_frame,
        text="STOP DISCOVERY",
        command=stop_discovery,
        bg=RED,
        fg=WHITE,
        font=("Arial", 10, "bold"),
        relief="flat",
        cursor="hand2",
        padx=15,
        pady=9
    ).pack(side="left", padx=7)

    tk.Button(
        content,
        text="LOG OUT",
        command=show_login,
        bg=PURPLE,
        fg=WHITE,
        font=("Arial", 10, "bold"),
        relief="flat",
        cursor="hand2",
        padx=30,
        pady=9
    ).pack(pady=8)

    # Automatically start discovery after login
    start_discovery(email)

# ==============================
# CLOSE APPLICATION
# ==============================

def close_application():
    stop_discovery()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", close_application)

# ==============================
# START APPLICATION
# ==============================

show_login()
root.mainloop()