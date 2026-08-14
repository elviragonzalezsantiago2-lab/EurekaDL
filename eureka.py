#!/usr/bin/env python3
"""EurekaDL simple CLI wrapper.
Provides minimal download handling for URLs (detects module from URL and delegates to Orpheus core).
This keeps the GUI and simple scripts working without requiring a full CLI implementation.
"""
from __future__ import annotations

import sys
import os
from urllib.parse import urlparse

try:
    from orpheus.core import Orpheus, orpheus_core_download
    from utils.models import MediaIdentification, DownloadTypeEnum
except Exception as e:
    print(f"Error: failed to import internal modules: {e}")
    sys.exit(1)


def print_help():
    print("Usage:\n  python eureka.py download <url> [--output <path>]\n  python eureka.py login <platform> [--mode tv|browser] [--username ...] [--password ...]\n  python eureka.py --help")


def run_tidal_tv_login():
    try:
        from modules.tidal.interface import module_information
        from modules.tidal.tidal_api import TidalTvSession
        settings = getattr(module_information, 'global_settings', {})
        session = TidalTvSession(settings.get('tv_atmos_token'), settings.get('tv_atmos_secret'))
        session.auth()
        print('TIDAL TV login successful. The session is valid for this process.')
        return 0
    except Exception as exc:
        print(f'Error: TIDAL TV login failed: {exc}')
        return 1


def run_platform_login(platform: str, username: str = None, password: str = None, mode: str = 'tv'):
    platform = (platform or '').lower().strip()
    if platform == 'tidal':
        if mode.lower() not in {'tv', 'browser'}:
            mode = 'tv'
        if mode == 'browser':
            print('TIDAL browser login is not available in this lightweight GUI flow; using TV login instead.')
        return run_tidal_tv_login()

    if platform in {'youtube', 'spotify', 'deezer', 'soundcloud', 'bandcamp'}:
        print(f'{platform.title()} login in this project is handled through browser cookies or API credentials, not a simple username/password form.')
        if platform == 'spotify':
            print('Set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET before using Spotify features.')
        elif platform == 'youtube':
            print('Set YTDLP_COOKIESFILE to a valid browser cookies.txt file when YouTube blocks downloads.')
        return 0

    print(f'Unknown platform: {platform}')
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
        username = None
        password = None
        mode = 'tv'

        for i, arg in enumerate(sys.argv[3:]):
            if arg in ('--username', '-u') and i + 3 < len(sys.argv):
                username = sys.argv[3 + i + 1]
            elif arg in ('--password', '-p') and i + 3 < len(sys.argv):
                password = sys.argv[3 + i + 1]
            elif arg in ('--mode', '-m') and i + 3 < len(sys.argv):
                mode = sys.argv[3 + i + 1]

        sys.exit(run_platform_login(platform, username=username, password=password, mode=mode))

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

        if module.lower() == 'tidal':
            print('TIDAL downloads require a TV session login.')
            print('Use: python eureka.py login tidal --mode tv')
            print('Then retry the download command.')
            sys.exit(2)

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
