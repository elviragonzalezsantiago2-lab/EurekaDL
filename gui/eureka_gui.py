#!/usr/bin/env python3
"""Simple cross-platform Tkinter GUI for EurekaDL.
Provides URL input, output directory, login form for supported services,
and a queue-safe download action.
"""
import os
import sys
import threading
import subprocess
import tkinter as tk
from tkinter import messagebox, filedialog

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EUREKA_ENTRY = os.path.join(ROOT_DIR, "eureka.py")

PLATFORMS = [
    "YouTube",
    "Spotify",
    "Deezer",
    "SoundCloud",
    "Bandcamp",
    "TIDAL",
]


def is_tidal_url(url):
    return "tidal.com" in (url or "").lower()


def run_process(cmd, status_var, done_label="Download finished", fail_prefix="Failed", btn=None):
    def _target():
        try:
            status_var.set("Running...")
            if btn is not None:
                btn.config(state="disabled")
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            for line in proc.stdout:
                status_var.set(line.strip())
            proc.wait()
            if proc.returncode == 0:
                status_var.set(done_label)
            else:
                status_var.set(f"{fail_prefix} (code {proc.returncode})")
        except Exception as exc:
            status_var.set(f"Error: {exc}")
            messagebox.showerror("Eureka GUI", f"Error running command: {exc}")
        finally:
            if btn is not None:
                btn.config(state="normal")

    thread = threading.Thread(target=_target, daemon=True)
    thread.start()


def run_eureka_download(url, outdir, status_var, btn):
    """Run eureka.py in a background thread and update status_var."""
    if is_tidal_url(url):
        status_var.set("TIDAL requires TV login in a terminal.")
        messagebox.showinfo(
            "Eureka GUI",
            "TIDAL downloads need interactive TV login. Open a terminal and run:\n\n"
            "python eureka.py login tidal --mode tv\n\n"
            "Then retry the download in this GUI.",
        )
        return

    cmd = [sys.executable, EUREKA_ENTRY, "download", url]
    if outdir:
        cmd += ["--output", outdir]
    run_process(cmd, status_var, done_label="Download finished", fail_prefix="Download failed", btn=btn)


def run_platform_login(platform, username, password, status_var, btn):
    platform_name = (platform or "").lower().strip()
    cmd = [sys.executable, EUREKA_ENTRY, "login", platform_name]
    if username:
        cmd += ["--username", username]
    if password:
        cmd += ["--password", password]
    if platform_name == "tidal":
        cmd += ["--mode", "tv"]
    run_process(cmd, status_var, done_label="Login finished", fail_prefix="Login failed", btn=btn)


def choose_output_dir(entry_out):
    d = filedialog.askdirectory(title="Select download directory")
    if d:
        entry_out.delete(0, tk.END)
        entry_out.insert(0, d)


def build_ui():
    root = tk.Tk()
    root.title("EurekaDL - Simple GUI")
    root.geometry("760x420")
    root.minsize(700, 360)

    frm = tk.Frame(root, padx=14, pady=14)
    frm.pack(fill=tk.BOTH, expand=True)

    tk.Label(frm, text="Track / Playlist URL:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w")
    entry_url = tk.Entry(frm, width=90)
    entry_url.grid(row=1, column=0, columnspan=3, sticky="we", pady=(4, 10))

    tk.Label(frm, text="Output directory (optional):", font=("Segoe UI", 10, "bold")).grid(row=2, column=0, sticky="w")
    entry_out = tk.Entry(frm, width=64)
    entry_out.grid(row=3, column=0, sticky="we")
    tk.Button(frm, text="Browse", command=lambda: choose_output_dir(entry_out), width=12).grid(row=3, column=1, sticky="w", padx=(8, 0))

    tk.Label(frm, text="Platform login:", font=("Segoe UI", 10, "bold")).grid(row=4, column=0, sticky="w", pady=(14, 0))
    platform_var = tk.StringVar(value="YouTube")
    platform_menu = tk.OptionMenu(frm, platform_var, *PLATFORMS)
    platform_menu.grid(row=5, column=0, sticky="w")

    tk.Label(frm, text="Username:").grid(row=5, column=1, sticky="w", padx=(18, 0))
    entry_user = tk.Entry(frm, width=22)
    entry_user.grid(row=5, column=2, sticky="w")

    tk.Label(frm, text="Password / token:").grid(row=6, column=1, sticky="w", padx=(18, 0), pady=(8, 0))
    entry_pass = tk.Entry(frm, width=22, show="*")
    entry_pass.grid(row=6, column=2, sticky="w", pady=(8, 0))

    status_var = tk.StringVar(value="Idle")
    status_lbl = tk.Label(frm, textvariable=status_var, anchor="w", justify="left", wraplength=620)
    status_lbl.grid(row=7, column=0, columnspan=3, sticky="we", pady=(18, 0))

    def on_download():
        url = entry_url.get().strip()
        outdir = entry_out.get().strip() or None
        if not url:
            messagebox.showinfo("Eureka GUI", "Please enter a URL to download")
            return
        run_eureka_download(url, outdir, status_var, btn_download)

    def on_login():
        platform = platform_var.get()
        username = entry_user.get().strip()
        password = entry_pass.get().strip()
        run_platform_login(platform, username, password, status_var, btn_login)

    btn_login = tk.Button(frm, text="Login", command=on_login, width=12)
    btn_login.grid(row=8, column=0, sticky="w", pady=(12, 0))

    btn_download = tk.Button(frm, text="Download", command=on_download, width=12)
    btn_download.grid(row=8, column=1, sticky="w", pady=(12, 0))

    btn_quit = tk.Button(frm, text="Quit", command=root.destroy, width=12)
    btn_quit.grid(row=8, column=2, sticky="w", pady=(12, 0))

    frm.columnconfigure(0, weight=1)
    frm.columnconfigure(1, weight=0)
    frm.columnconfigure(2, weight=0)

    return root


def main():
    if not os.path.exists(EUREKA_ENTRY):
        messagebox.showerror("Eureka GUI", f"Cannot find eureka.py entrypoint at {EUREKA_ENTRY}")
        return
    try:
        root = build_ui()
        root.mainloop()
    except Exception as e:
        try:
            messagebox.showerror("Eureka GUI", f"Unhandled error: {e}")
        except Exception:
            print("Unhandled error in GUI:", e, file=sys.stderr)


if __name__ == '__main__':
    main()
