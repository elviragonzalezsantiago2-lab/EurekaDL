#!/usr/bin/env python3
"""Cross-platform Tkinter interface for EurekaDL."""
import os
import queue
import shutil
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from urllib.parse import urlparse

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EUREKA_ENTRY = os.path.join(ROOT_DIR, "eureka.py")
LOGIN_PLATFORMS = (
    ("YouTube", "youtube"), ("Spotify", "spotify"), ("Apple Music", "applemusic"),
    ("Deezer", "deezer"), ("SoundCloud", "soundcloud"), ("Bandcamp", "bandcamp"),
    ("Qobuz", "qobuz"), ("Crunchyroll", "crunchyroll"), ("TIDAL TV", "tidal"),
)
PLATFORM_REQUIREMENTS = {
    "YouTube": "Install yt-dlp and FFmpeg. Export browser cookies only when YouTube asks for verification, age checks, or sign-in.",
    "Spotify": "Set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET. This build uses Spotify metadata and a permitted audio source.",
    "Apple Music": "Install yt-dlp and FFmpeg. Use only media you are entitled to download.",
    "Deezer": "Install yt-dlp and FFmpeg. Use only media you are entitled to download.",
    "SoundCloud": "Install yt-dlp and FFmpeg. Some tracks may be unavailable depending on the uploader's permissions.",
    "Bandcamp": "Install yt-dlp and FFmpeg. Prefer the artist's official download when it is offered.",
    "Qobuz": "Install yt-dlp and FFmpeg. An account alone does not grant download rights for all catalogue items.",
    "Crunchyroll": "Install yt-dlp and FFmpeg. Use only content that you are allowed to save locally.",
    "TIDAL TV": "Install the optional TIDAL module, have an eligible TIDAL account, then use the TV button to complete the device-code flow.",
}


def run_terminal_preflight(input_func=input, output_func=print, executable_lookup=shutil.which):
    """Ask for an informed confirmation before showing the desktop GUI."""
    output_func("\nEurekaDL pre-download checklist")
    output_func("- Download only music you own or are authorized to save.")
    output_func(f"- FFmpeg: {'found' if executable_lookup('ffmpeg') else 'missing'}")
    output_func(f"- yt-dlp: {'found' if executable_lookup('yt-dlp') else 'missing'}")
    output_func("- Open 'Platform setup' in the GUI for service-specific requirements.")
    answer = input_func("Do you meet the requirements and want to open the GUI? [y/N]: ").strip().lower()
    return answer in {"y", "yes", "s", "si", "sí"}


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


def build_login_command(platform):
    """Build a platform setup/login command without exposing credentials to the GUI."""
    command = [sys.executable, EUREKA_ENTRY, "login", platform]
    if platform == "tidal":
        command.extend(["--mode", "tv"])
    return command


def run_eureka_command(command, action, events):
    """Start a worker which sends events back to the Tk main thread."""
    def target():
        events.put(("started", action))
        try:
            process = subprocess.Popen(
                command, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace",
            )
            for line in process.stdout:
                events.put(("output", line.rstrip()))
            process.wait()
            events.put(("finished", (action, process.returncode)))
        except Exception as error:
            events.put(("error", str(error)))

    threading.Thread(target=target, daemon=True).start()


def run_eureka_download(url, outdir, events):
    run_eureka_command(build_download_command(url, outdir), "Download", events)


def run_platform_login(platform, events):
    run_eureka_command(build_login_command(platform), f"{platform.title()} login", events)


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


def show_platform_guide(root, events):
    """Show each platform's prerequisites in a dedicated, always-visible window."""
    guide = tk.Toplevel(root)
    guide.title("EurekaDL platform setup")
    guide.geometry("720x560")
    guide.minsize(560, 420)
    frame = ttk.Frame(guide, padding=14)
    frame.pack(fill=tk.BOTH, expand=True)
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(1, weight=1)
    ttk.Label(frame, text="Platform setup", font=("TkDefaultFont", 14, "bold")).grid(row=0, column=0, sticky="w")

    guide_text = scrolledtext.ScrolledText(frame, state=tk.NORMAL, wrap=tk.WORD, height=16, font=("TkDefaultFont", 10))
    guide_text.grid(row=1, column=0, sticky="nsew", pady=(8, 10))
    guide_text.insert(tk.END, "Before downloading, confirm that you have permission to save the content.\n\n")
    for label, _platform in LOGIN_PLATFORMS:
        guide_text.insert(tk.END, f"{label}\n", ("heading",))
        guide_text.insert(tk.END, f"{PLATFORM_REQUIREMENTS[label]}\n\n")
    guide_text.tag_configure("heading", font=("TkDefaultFont", 10, "bold"))
    guide_text.config(state=tk.DISABLED)

    buttons = ttk.Frame(frame)
    buttons.grid(row=2, column=0, sticky="w")
    for index, (label, platform) in enumerate(LOGIN_PLATFORMS):
        button = ttk.Button(buttons, text=label, command=lambda name=platform: run_platform_login(name, events))
        button.grid(row=index // 5, column=index % 5, padx=(0, 6), pady=(0, 5), sticky="w")


def build_ui():
    root = tk.Tk()
    root.title("EurekaDL")
    root.geometry("740x560")
    root.minsize(600, 440)

    frame = ttk.Frame(root, padding=14)
    frame.pack(fill=tk.BOTH, expand=True)
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(8, weight=1)

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

    ttk.Label(frame, text="Platform sign-in and setup").grid(row=6, column=0, sticky="w")
    platform_row = ttk.Frame(frame)
    platform_row.grid(row=7, column=0, sticky="ew", pady=(4, 10))

    log = scrolledtext.ScrolledText(frame, height=12, state=tk.DISABLED, wrap=tk.WORD, font=("Consolas", 9))
    log.grid(row=8, column=0, sticky="nsew", pady=(0, 10))

    status_var = tk.StringVar(value="Ready")
    ttk.Label(frame, textvariable=status_var).grid(row=9, column=0, sticky="w")

    actions = ttk.Frame(frame)
    actions.grid(row=10, column=0, sticky="ew", pady=(10, 0))
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
                    status_var.set(f"{value} in progress…")
                    download_button.config(state=tk.DISABLED)
                    for button in login_buttons:
                        button.config(state=tk.DISABLED)
                    append_log(f"Starting {value}…")
                elif event == "output":
                    append_log(value)
                    if value:
                        status_var.set(value)
                elif event == "finished":
                    action, returncode = value
                    download_button.config(state=tk.NORMAL)
                    for button in login_buttons:
                        button.config(state=tk.NORMAL)
                    if returncode == 0:
                        status_var.set(f"{action} finished")
                        append_log(f"{action} finished successfully.")
                    else:
                        status_var.set(f"{action} failed (code {returncode})")
                        append_log(f"{action} failed with exit code {returncode}.")
                elif event == "error":
                    download_button.config(state=tk.NORMAL)
                    for button in login_buttons:
                        button.config(state=tk.NORMAL)
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

    login_buttons = []
    for index, (label, platform) in enumerate(LOGIN_PLATFORMS):
        button = ttk.Button(platform_row, text=label, command=lambda name=platform: run_platform_login(name, events))
        button.grid(row=index // 5, column=index % 5, padx=(0, 6), pady=(0, 5), sticky="w")
        login_buttons.append(button)

    download_button = ttk.Button(actions, text="Download", command=on_download)
    download_button.grid(row=0, column=0, sticky="w")
    ttk.Button(actions, text="Open folder", command=lambda: open_output_directory(entry_out.get().strip())).grid(row=0, column=1, padx=(8, 0))
    ttk.Button(actions, text="Clear log", command=clear_log).grid(row=0, column=2, padx=(8, 0))
    ttk.Button(actions, text="Platform setup", command=lambda: show_platform_guide(root, events)).grid(row=0, column=3, padx=(8, 0))
    ttk.Button(actions, text="Quit", command=root.destroy).grid(row=0, column=4, sticky="e")

    poll_events()
    return root


def main():
    if not os.path.exists(EUREKA_ENTRY):
        messagebox.showerror("EurekaDL", f"Cannot find eureka.py at {EUREKA_ENTRY}")
        return
    if sys.stdin.isatty() and not run_terminal_preflight():
        print("GUI not opened. Install the missing tools or review the platform requirements, then try again.")
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
