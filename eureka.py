#!/usr/bin/env python3
"""EurekaDL simple CLI wrapper.
Provides minimal download handling for URLs (detects module from URL and delegates to Orpheus core).
This keeps the GUI and simple scripts working without requiring a full CLI implementation.
"""
from __future__ import annotations

import sys
import os
import importlib
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
        "  python eureka.py login <platform> [--mode tv]\n"
        "  python eureka.py --help"
    )


PLATFORM_LOGIN_GUIDANCE = {
    "youtube": "YouTube uses browser cookies. Set YTDLP_COOKIESFILE to an exported cookies.txt file.",
    "spotify": "Spotify uses API credentials. Set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET.",
    "applemusic": "Apple Music downloads in this build use yt-dlp; no separate account login is available.",
    "deezer": "Deezer downloads in this build use yt-dlp; no separate account login is available.",
    "soundcloud": "SoundCloud downloads in this build use yt-dlp; no separate account login is available.",
    "bandcamp": "Bandcamp downloads in this build use yt-dlp; no separate account login is available.",
    "qobuz": "Qobuz downloads in this build use yt-dlp; no separate account login is available.",
    "crunchyroll": "Crunchyroll downloads in this build use yt-dlp; no separate account login is available.",
}


def run_tidal_tv_login():
    """Start TIDAL's TV-device authentication when its module is installed."""
    try:
        interface = importlib.import_module("modules.tidal.interface")
        tidal_api = importlib.import_module("modules.tidal.tidal_api")
        session_class = getattr(tidal_api, "TidalTvSession")
    except (ImportError, AttributeError) as error:
        print(f"TIDAL TV login is unavailable: {error}")
        print("Install the TIDAL module before using the TV login button.")
        return 1

    try:
        settings = getattr(interface.module_information, "global_settings", {})
        session = session_class(settings.get("tv_atmos_token"), settings.get("tv_atmos_secret"))
        session.auth()
        print("TIDAL TV authentication completed. Follow any device-code instructions shown above.")
        return 0
    except Exception as error:
        print(f"TIDAL TV login failed: {error}")
        return 1


def run_platform_login(platform, mode="browser"):
    platform = (platform or "").lower().strip()
    if platform == "tidal":
        return run_tidal_tv_login() if mode == "tv" else 1
    if platform in PLATFORM_LOGIN_GUIDANCE:
        print(PLATFORM_LOGIN_GUIDANCE[platform])
        return 0
    print(f"Unknown platform: {platform}")
    return 1


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
    if cmd == 'login':
        if len(sys.argv) < 3:
            print('Error: missing platform name')
            print_help()
            sys.exit(1)
        platform = sys.argv[2]
        mode = 'tv' if '--mode' in sys.argv and sys.argv.index('--mode') + 1 < len(sys.argv) and sys.argv[sys.argv.index('--mode') + 1] == 'tv' else 'browser'
        sys.exit(run_platform_login(platform, mode))

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
