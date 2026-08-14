#!/usr/bin/env python3
"""Cross-platform Tkinter interface for EurekaDL."""
import os
import queue
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from urllib.parse import urlparse

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EUREKA_ENTRY = os.path.join(ROOT_DIR, "eureka.py")


def is_supported_url(value):
    """Return whether *value* is a complete HTTP(S) URL."""
    parsed = urlparse(value.strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def build_download_command(url, outdir=None):
    """Build the child-process command without invoking a shell."""
    command = [sys.executable, EUREKA_ENTRY, "download", url]
    if outdir:
        command.extend(["--output", outdir])
    return command


def run_eureka_download(url, outdir, events):
    """Start a worker which sends events back to the Tk main thread."""
    def target():
        events.put(("started", None))
        try:
            process = subprocess.Popen(
                build_download_command(url, outdir), stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace",
            )
            for line in process.stdout:
                events.put(("output", line.rstrip()))
            process.wait()
            events.put(("finished", process.returncode))
        except Exception as error:
            events.put(("error", str(error)))

    threading.Thread(target=target, daemon=True).start()


def choose_output_dir(entry_out):
    directory = filedialog.askdirectory(title="Select download directory")
    if directory:
        entry_out.delete(0, tk.END)
        entry_out.insert(0, directory)


def open_output_directory(path):
    directory = path or os.path.join(ROOT_DIR, "downloads")
    if not os.path.isdir(directory):
        messagebox.showinfo("EurekaDL", f"The output directory does not exist yet:\n{directory}")
        return
    if sys.platform == "win32":
        os.startfile(directory)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", directory])
    else:
        subprocess.Popen(["xdg-open", directory])


def build_ui():
    root = tk.Tk()
    root.title("EurekaDL")
    root.geometry("700x440")
    root.minsize(560, 360)

    frame = ttk.Frame(root, padding=14)
    frame.pack(fill=tk.BOTH, expand=True)
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(6, weight=1)

    ttk.Label(frame, text="EurekaDL", font=("TkDefaultFont", 16, "bold")).grid(row=0, column=0, sticky="w")
    ttk.Label(frame, text="Paste a track or playlist URL to start a download.").grid(row=1, column=0, sticky="w", pady=(0, 12))

    ttk.Label(frame, text="Track / playlist URL").grid(row=2, column=0, sticky="w")
    entry_url = ttk.Entry(frame)
    entry_url.grid(row=3, column=0, sticky="ew", pady=(3, 10))
    entry_url.focus_set()

    ttk.Label(frame, text="Output folder (optional)").grid(row=4, column=0, sticky="w")
    output_row = ttk.Frame(frame)
    output_row.grid(row=5, column=0, sticky="ew", pady=(3, 10))
    output_row.columnconfigure(0, weight=1)
    entry_out = ttk.Entry(output_row)
    entry_out.grid(row=0, column=0, sticky="ew")
    ttk.Button(output_row, text="Browse…", command=lambda: choose_output_dir(entry_out)).grid(row=0, column=1, padx=(8, 0))

    log = scrolledtext.ScrolledText(frame, height=12, state=tk.DISABLED, wrap=tk.WORD, font=("Consolas", 9))
    log.grid(row=6, column=0, sticky="nsew", pady=(0, 10))

    status_var = tk.StringVar(value="Ready")
    ttk.Label(frame, textvariable=status_var).grid(row=7, column=0, sticky="w")

    actions = ttk.Frame(frame)
    actions.grid(row=8, column=0, sticky="ew", pady=(10, 0))
    actions.columnconfigure(3, weight=1)
    events = queue.Queue()

    def append_log(line):
        if line:
            log.config(state=tk.NORMAL)
            log.insert(tk.END, line + "\n")
            log.see(tk.END)
            log.config(state=tk.DISABLED)

    def clear_log():
        log.config(state=tk.NORMAL)
        log.delete("1.0", tk.END)
        log.config(state=tk.DISABLED)

    def poll_events():
        try:
            while True:
                event, value = events.get_nowait()
                if event == "started":
                    status_var.set("Downloading…")
                    download_button.config(state=tk.DISABLED)
                    append_log("Starting EurekaDL…")
                elif event == "output":
                    append_log(value)
                    if value:
                        status_var.set(value)
                elif event == "finished":
                    download_button.config(state=tk.NORMAL)
                    if value == 0:
                        status_var.set("Download finished")
                        append_log("Download finished successfully.")
                    else:
                        status_var.set(f"Download failed (code {value})")
                        append_log(f"Download failed with exit code {value}.")
                elif event == "error":
                    download_button.config(state=tk.NORMAL)
                    status_var.set("Could not start EurekaDL")
                    append_log(f"Error: {value}")
                    messagebox.showerror("EurekaDL", f"Could not start EurekaDL:\n{value}")
        except queue.Empty:
            pass
        root.after(100, poll_events)

    def on_download():
        url = entry_url.get().strip()
        outdir = entry_out.get().strip() or None
        if not is_supported_url(url):
            messagebox.showinfo("EurekaDL", "Enter a complete HTTP or HTTPS track/playlist URL.")
            entry_url.focus_set()
            return
        run_eureka_download(url, outdir, events)

    download_button = ttk.Button(actions, text="Download", command=on_download)
    download_button.grid(row=0, column=0, sticky="w")
    ttk.Button(actions, text="Open folder", command=lambda: open_output_directory(entry_out.get().strip())).grid(row=0, column=1, padx=(8, 0))
    ttk.Button(actions, text="Clear log", command=clear_log).grid(row=0, column=2, padx=(8, 0))
    ttk.Button(actions, text="Quit", command=root.destroy).grid(row=0, column=4, sticky="e")

    poll_events()
    return root


def main():
    if not os.path.exists(EUREKA_ENTRY):
        messagebox.showerror("EurekaDL", f"Cannot find eureka.py at {EUREKA_ENTRY}")
        return
    try:
        build_ui().mainloop()
    except Exception as error:
        try:
            messagebox.showerror("EurekaDL", f"Unhandled error: {error}")
        except Exception:
            print("Unhandled error in GUI:", error, file=sys.stderr)


if __name__ == "__main__":
    main()
