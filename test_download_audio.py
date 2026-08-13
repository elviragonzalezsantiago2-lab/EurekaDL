import os, json, shutil
from pathlib import Path

import yt_dlp

# Load settings
cfg = json.load(open('config/settings.json'))
download_path = cfg.get('global', {}).get('general', {}).get('download_path', './downloads')
Path(download_path).mkdir(parents=True, exist_ok=True)

url = 'https://www.youtube.com/watch?v=aqz-KE-bpKQ'  # Big Buck Bunny

ffmpeg_present = shutil.which('ffmpeg') is not None

outtmpl = os.path.join(download_path, '%(title)s.%(ext)s')

ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': outtmpl,
    'quiet': False,
    'no_warnings': True,
}

if ffmpeg_present:
    ydl_opts['postprocessors'] = [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }]
    print('ffmpeg detected: will convert audio to mp3')
else:
    print('ffmpeg not found: will save bestaudio without conversion')

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(url, download=True)
    print('Downloaded:', info.get('title'), '->', info.get('requested_downloads'))
