#!/usr/bin/env python3
"""Simple cross-platform Tkinter GUI for EurekaDL.
Provides a minimal URL input, download button and status output.
Runs the existing eureka.py entrypoint in a background thread so the UI stays responsive.
"""
import os
import sys
import threading
import subprocess
import tkinter as tk
from tkinter import messagebox, filedialog

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EUREKA_ENTRY = os.path.join(ROOT_DIR, "eureka.py")


def run_eureka_download(url, outdir, status_var, btn):
    """Run eureka.py in a background thread and update status_var."""
    def _target():
        try:
            status_var.set("Running...")
            btn.config(state="disabled")
            cmd = [sys.executable, EUREKA_ENTRY, "download", url]
            if outdir:
                cmd += ["--output", outdir]
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in proc.stdout:
                status_var.set(line.strip())
            proc.wait()
            if proc.returncode == 0:
                status_var.set("Download finished")
            else:
                status_var.set(f"Failed (code {proc.returncode})")
        except Exception as e:
            status_var.set(f"Error: {e}")
            messagebox.showerror("Eureka GUI", f"Error running download: {e}")
        finally:
            btn.config(state="normal")

    thread = threading.Thread(target=_target, daemon=True)
    thread.start()


def choose_output_dir(entry_out):
    d = filedialog.askdirectory(title="Select download directory")
    if d:
        entry_out.delete(0, tk.END)
        entry_out.insert(0, d)


def build_ui():
    root = tk.Tk()
    root.title("EurekaDL - Simple GUI")
    root.geometry("560x180")

    frm = tk.Frame(root, padx=10, pady=10)
    frm.pack(fill=tk.BOTH, expand=True)

    tk.Label(frm, text="Track / Playlist URL:").grid(row=0, column=0, sticky="w")
    entry_url = tk.Entry(frm, width=60)
    entry_url.grid(row=1, column=0, columnspan=3, sticky="we", pady=6)

    tk.Label(frm, text="Output directory (optional):").grid(row=2, column=0, sticky="w")
    entry_out = tk.Entry(frm, width=48)
    entry_out.grid(row=3, column=0, sticky="w")
    tk.Button(frm, text="Browse", command=lambda: choose_output_dir(entry_out)).grid(row=3, column=1, sticky="w", padx=6)

    status_var = tk.StringVar(value="Idle")
    status_lbl = tk.Label(frm, textvariable=status_var, anchor="w")
    status_lbl.grid(row=4, column=0, columnspan=3, sticky="we", pady=(12, 0))

    def on_download():
        url = entry_url.get().strip()
        outdir = entry_out.get().strip() or None
        if not url:
            messagebox.showinfo("Eureka GUI", "Please enter a URL to download")
            return
        run_eureka_download(url, outdir, status_var, btn)

    btn = tk.Button(frm, text="Download", command=on_download, width=12)
    btn.grid(row=5, column=0, pady=10, sticky="w")

    tk.Button(frm, text="Quit", command=root.destroy, width=12).grid(row=5, column=1, pady=10, sticky="e")

    # make the layout responsive
    frm.columnconfigure(0, weight=1)

    return root


def main():
    # Basic sanity checks
    if not os.path.exists(EUREKA_ENTRY):
        messagebox.showerror("Eureka GUI", f"Cannot find eureka.py entrypoint at {EUREKA_ENTRY}")
        return
    try:
        root = build_ui()
        root.mainloop()
    except Exception as e:
        # Last-resort dialog so the window doesn't just disappear silently
        try:
            messagebox.showerror("Eureka GUI", f"Unhandled error: {e}")
        except Exception:
            print("Unhandled error in GUI:", e, file=sys.stderr)


if __name__ == '__main__':
    main()
