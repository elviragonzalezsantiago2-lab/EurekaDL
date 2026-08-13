#!/usr/bin/env python3
"""Create stubs for recommended streaming service modules if they are missing.
Run from repository root: python scripts/fetch_recommended_modules.py
This does NOT fetch external code automatically; it creates safe, importable stubs and prints guidance to obtain real implementations.
"""
import os
from subprocess import run

RECOMMENDED = [
    ('youtube', 'yt-dlp (recommended)'),
    ('spotify', 'spotipy'),
    ('deezer', 'deezer API wrapper or yt-dlp'),
    ('soundcloud', 'soundcloud API or yt-dlp'),
    ('bandcamp', 'yt-dlp or scraping helper')
]

ROOT = os.path.dirname(os.path.dirname(__file__))
SCRIPTS = os.path.join(ROOT, 'scripts')
CREATE = os.path.join(SCRIPTS, 'create_stub_module.py')

print('Scanning modules directory...')
for name, note in RECOMMENDED:
    mod_path = os.path.join(ROOT, 'modules', name)
    if os.path.exists(mod_path) and os.path.exists(os.path.join(mod_path, 'interface.py')):
        print(f'  - {name}: already present')
    else:
        print(f'  - {name}: missing, creating stub (recommended dependency: {note})')
        run(['python', CREATE, name], check=True)

print('\nDone. For full implementations, consider these sources:')
print(' - youtube: use yt-dlp to extract media URLs; wrap it to provide module interface.')
print(" - spotify: spotipy requires client id/secret; it's best used for metadata and then find downloadable sources via other providers.")
print(' - deezer/soundcloud/bandcamp: many can be handled by yt-dlp or by dedicated API wrappers. Search for existing open-source OrpheusDL modules online and adapt their code.')