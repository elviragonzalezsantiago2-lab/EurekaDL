from modules.youtube import interface

m = interface.ModuleInterface(None)
url = 'https://www.youtube.com/watch?v=aqz-KE-bpKQ'
print('URL:', url)
print('Fetching track info...')
ti = m.get_track_info(url, None, None)
print('TITLE:', ti.name)
print('ARTISTS:', ti.artists)
print('DURATION:', ti.duration)
print('COVER:', ti.cover_url)
print('\nFetching track download info (no download)...')
td = m.get_track_download(webpage_url=url)
print('DOWNLOAD_TYPE:', td.download_type)
print('FILE_URL:', td.file_url[:200] if td.file_url else None)
print('HEADERS:', td.file_url_headers)
