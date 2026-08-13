#!/usr/bin/env python3
"""
Simple interactive helper (mini-AI) to build playlists.
- Prompts user for playlist name and search queries
- Uses modules/* module interfaces to search (prefers YouTube/Spotify module if present)
- Writes an M3U playlist to the configured download path and can optionally download tracks
"""
import json
import os
import sys
from importlib import import_module
from utils.models import DownloadTypeEnum, MediaIdentification

CONFIG_PATH = 'config/settings.json'
if not os.path.exists(CONFIG_PATH):
    print('Missing config/settings.json')
    sys.exit(1)

cfg = json.load(open(CONFIG_PATH))
download_path = cfg.get('global', {}).get('general', {}).get('download_path', './downloads')

# Helper to find a module interface
def load_module(name):
    try:
        mod = import_module(f'modules.{name}.interface')
        cls = getattr(mod, 'ModuleInterface', None)
        if cls:
            return cls(None)
    except Exception:
        pass
    return None

# Prefer youtube then spotify
preferred_order = ['youtube', 'spotify', 'deezer', 'qobuz', 'soundcloud', 'bandcamp']
available = []
for name in preferred_order:
    m = load_module(name)
    if m:
        available.append((name, m))

if not available:
    print('No usable modules found (youtube/spotify/etc). Install them first.')
    sys.exit(1)

print('Mini-AI playlist helper')
playlist_name = input('Playlist name: ').strip() or 'My Playlist'
items = []
print('Enter search queries or URLs (empty line to finish). Prefix with module:query to force module (e.g., youtube:Bohemian Rhapsody)')
while True:
    line = input('> ').strip()
    if not line:
        break
    if ':' in line and not line.startswith('http'):
        module_hint, q = line.split(':', 1)
        module_hint = module_hint.strip()
        q = q.strip()
        m = load_module(module_hint)
        if not m:
            print(f'Module {module_hint} not available, skipping')
            continue
        # search tracks
        try:
            results = m.search(DownloadTypeEnum.track, q, limit=5)
        except Exception as e:
            print('Search failed with', e)
            continue
        for r in results[:3]:
            items.append((module_hint, r))
            print('Added:', r.name, '->', module_hint)
    else:
        # try available modules in order
        added = False
        for name, m in available:
            try:
                if line.startswith('http'):
                    # direct URL
                    info = m.custom_url_parse(line)
                    items.append((name, info))
                    print('Added URL for', name)
                    added = True
                    break
                else:
                    results = m.search(DownloadTypeEnum.track, line, limit=5)
                    if results:
                        r = results[0]
                        items.append((name, r))
                        print('Added:', r.name, '->', name)
                        added = True
                        break
            except Exception:
                continue
        if not added:
            print('No match found for query in available modules')

if not items:
    print('No items collected, aborting')
    sys.exit(0)

# Create M3U
m3u_lines = ['#EXTM3U']
for name, item in items:
    if hasattr(item, 'duration'):
        dur = int(item.duration or 0)
    else:
        dur = 0
    title = item.name if hasattr(item, 'name') else (item.get('webpage_url') if isinstance(item, dict) else str(item))
    m3u_lines.append(f'#EXTINF:{dur},{title}')
    # determine playable url
    if hasattr(item, 'extra_kwargs') and item.extra_kwargs.get('webpage_url'):
        m3u_lines.append(item.extra_kwargs.get('webpage_url'))
    elif isinstance(item, dict) and item.get('webpage_url'):
        m3u_lines.append(item.get('webpage_url'))
    else:
        # fallback to module's custom URL
        try:
            mod = load_module(name)
            if hasattr(item, 'result_id'):
                mi = mod.get_track_info(item.result_id, None, None)
                if mi and mi.download_extra_kwargs and mi.download_extra_kwargs.get('webpage_url'):
                    m3u_lines.append(mi.download_extra_kwargs.get('webpage_url'))
                else:
                    m3u_lines.append(str(item.result_id))
            else:
                m3u_lines.append(str(item))
        except Exception:
            m3u_lines.append(str(item))

os.makedirs(download_path, exist_ok=True)
m3u_path = os.path.join(download_path, playlist_name.replace(' ','_') + '.m3u')
open(m3u_path,'w', encoding='utf-8').write('\n'.join(m3u_lines))
print('Playlist written to', m3u_path)

# Optionally download now
resp = input('Download tracks now? (y/N): ').strip().lower()
if resp == 'y':
    from orpheus.music_downloader import orpheus_core_download, Orpheus
    orp = Orpheus(False)
    media_to_download = {}
    for name, item in items:
        if name not in media_to_download:
            media_to_download[name] = []
        if hasattr(item, 'result_id'):
            media_to_download[name].append(MediaIdentification(media_type=DownloadTypeEnum.track, media_id=item.result_id, extra_kwargs=item.extra_kwargs if hasattr(item,'extra_kwargs') else {}))
        elif isinstance(item, dict) and item.get('webpage_url'):
            media_to_download[name].append(MediaIdentification(media_type=DownloadTypeEnum.track, media_id=item.get('webpage_url')))
        else:
            media_to_download[name].append(MediaIdentification(media_type=DownloadTypeEnum.track, media_id=str(item)))
    print('Starting download...')
    orpheus_core_download(orp, media_to_download, { }, 'default', download_path)
    print('Downloads initiated')
