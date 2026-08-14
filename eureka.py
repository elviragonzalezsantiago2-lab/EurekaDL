#!/usr/bin/env python3
"""EurekaDL simple CLI wrapper.
Provides minimal download handling for URLs (detects module from URL and delegates to Orpheus core).
This keeps the GUI and simple scripts working without requiring a full CLI implementation.
"""
from __future__ import annotations

import sys
import os
import shutil
from pathlib import Path
from urllib.parse import urlparse

try:
    from orpheus.core import Orpheus, orpheus_core_download
    from utils.models import MediaIdentification, DownloadTypeEnum
except Exception as e:
    print(f"Error: failed to import internal modules: {e}")
    sys.exit(1)


def print_help():
    print(
        "Usage:\n"
        "  python eureka.py download <url> [--output <path>]\n"
        "  python eureka.py doctor\n"
        "  python eureka.py --help"
    )


def run_doctor(project_root=None):
    """Print a quick, non-destructive installation diagnostic."""
    root = Path(project_root or Path(__file__).resolve().parent)
    config_path = root / "config" / "settings.json"
    modules_path = root / "modules"
    modules = sorted(
        path.name for path in modules_path.iterdir()
        if path.is_dir() and (path / "interface.py").is_file()
    ) if modules_path.is_dir() else []

    print("EurekaDL diagnostics")
    print(f"Python: {sys.version.split()[0]}")
    print(f"FFmpeg: {'found' if shutil.which('ffmpeg') else 'missing'}")
    print(f"Configuration: {'found' if config_path.is_file() else 'not created yet'}")
    print(f"Modules: {len(modules)}" + (f" ({', '.join(modules)})" if modules else ""))

    if not shutil.which("ffmpeg"):
        print("Tip: install FFmpeg before downloading or converting audio.")
    if not config_path.is_file():
        print("Tip: run a download command once to generate the default configuration.")
    if not modules:
        print("Tip: install at least one module before downloading.")


def detect_module_for_url(orpheus_session: Orpheus, url: str):
    parsed = urlparse(url)
    netloc = parsed.netloc.lower()
    # Try exact netloc mapping
    for constant, module in orpheus_session.module_netloc_constants.items():
        if constant and constant.lower() in netloc:
            return module
    # Fallback: ask each module to parse the URL via custom_url_parse
    for module in orpheus_session.module_list:
        try:
            mod = orpheus_session.load_module(module)
            parser = getattr(mod, 'custom_url_parse', None)
            if parser:
                res = parser(url)
                if res:
                    return module
        except Exception:
            continue
    return None


def main():
    if len(sys.argv) <= 1 or sys.argv[1] in ('-h', '--help', 'help'):
        print_help()
        return

    cmd = sys.argv[1]
    if cmd == 'doctor':
        run_doctor()
        return

    if cmd == 'download':
        if len(sys.argv) < 3:
            print('Error: missing URL')
            print_help()
            sys.exit(1)
        url = sys.argv[2]
        outdir = None
        if '--output' in sys.argv:
            try:
                idx = sys.argv.index('--output')
                outdir = sys.argv[idx + 1]
            except Exception:
                outdir = None

        try:
            orp = Orpheus()
        except Exception as e:
            print(f'Error: could not initialize Orpheus core: {e}')
            sys.exit(1)

        module = detect_module_for_url(orp, url)
        if not module:
            print('Error: could not detect a module for the provided URL')
            sys.exit(1)

        try:
            mod = orp.load_module(module)
            parse_fn = getattr(mod, 'custom_url_parse', None)
            parsed = parse_fn(url) if parse_fn else {'webpage_url': url}
        except Exception:
            parsed = {'webpage_url': url}

        media_id = parsed.get('spotify_id') or parsed.get('webpage_url') or url
        media = MediaIdentification(media_type=DownloadTypeEnum.track, media_id=str(media_id), extra_kwargs=parsed)
        media_to_download = {module: [media]}

        try:
            # third_party_modules should be a mapping (e.g., {ModuleModes.covers: 'youtube'}) — empty dict means no third-party overrides
            orpheus_core_download(orp, media_to_download, third_party_modules={}, separate_download_module='default', output_path=outdir)
        except Exception as e:
            print(f'Error during download: {e}')
            sys.exit(1)
        print('Download completed')
        return

    else:
        print('Unknown command')
        print_help()
        sys.exit(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n\t^C pressed - abort')
        sys.exit(1)
