import os, subprocess, sys
from pathlib import Path

# Converts any .m4a files in the configured download path to mp3 using ffmpeg.
# If a local tools/ffmpeg-static exists, uses that binary; otherwise relies on ffmpeg on PATH.

import json
cfg = json.load(open('config/settings.json'))
download_path = cfg.get('global', {}).get('general', {}).get('download_path', './downloads')

ffmpeg_bin = None
# Check local tools first — prefer an actual ffmpeg executable (ffmpeg.exe on Windows)
local_ff = Path('tools')
if local_ff.exists():
    # look specifically for ffmpeg.exe or ffmpeg
    for p in local_ff.rglob('*'):
        if p.is_file() and p.name.lower() in ('ffmpeg.exe','ffmpeg'):
            ffmpeg_bin = str(p)
            break

if not ffmpeg_bin:
    # rely on PATH
    from shutil import which
    ffmpeg_bin = which('ffmpeg')

if not ffmpeg_bin:
    print('ffmpeg not found. Run scripts/get_ffmpeg_windows.ps1 or install ffmpeg and retry.')
    sys.exit(2)

print('Using ffmpeg:', ffmpeg_bin)

p = Path(download_path)
if not p.exists():
    print('Download path does not exist:', download_path)
    sys.exit(1)

for m4a in p.glob('*.m4a'):
    mp3 = m4a.with_suffix('.mp3')
    if mp3.exists():
        print('MP3 already exists, skipping:', mp3.name)
        continue
    cmd = [ffmpeg_bin, '-y', '-i', str(m4a), '-vn', '-acodec', 'libmp3lame', '-q:a', '2', str(mp3)]
    print('Converting:', m4a.name, '->', mp3.name)
    subprocess.check_call(cmd)
    print('Converted:', mp3.name)
