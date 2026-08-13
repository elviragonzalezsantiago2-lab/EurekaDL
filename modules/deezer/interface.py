import json, subprocess
from utils.models import ModuleInformation, ModuleModes, ModuleFlags, SearchResult, TrackInfo, Tags, TrackDownloadInfo, DownloadEnum, CodecEnum, PlaylistInfo

module_information = ModuleInformation(
    service_name='Deezer',
    module_supported_modes=ModuleModes.download | ModuleModes.playlist,
    global_settings={},
    session_settings={},
    flags=ModuleFlags.hidden,
    netlocation_constant=['deezer.com']
)

class ModuleInterface:
    def __init__(self, controller):
        self.controller = controller

    def _run_yt_dlp_json(self, query_or_url):
        try:
            import yt_dlp as ytdl
            opts = {'quiet': True, 'skip_download': True, 'no_warnings': True}
            with ytdl.YoutubeDL(opts) as y:
                return y.extract_info(query_or_url, download=False)
        except Exception:
            cmd = ['yt-dlp', '-j', query_or_url]
            p = subprocess.run(cmd, capture_output=True, check=True, text=True)
            return json.loads(p.stdout)

    def search(self, media_type, query, limit=10):
        from modules.youtube.interface import ModuleInterface as YT
        return YT(None).search(media_type, query, limit)

    def custom_url_parse(self, url):
        return {'webpage_url': url}

    def get_track_info(self, track_id, quality_tier, codec_options, **kwargs):
        # Use yt-dlp to fetch metadata
        url = track_id if str(track_id).startswith('http') else f'https://www.deezer.com/track/{track_id}'
        data = self._run_yt_dlp_json(url)
        e = data if isinstance(data, dict) else (data.get('entries', [])[0] if isinstance(data, dict) else {})
        return TrackInfo(name=e.get('title') or str(track_id), album=e.get('album') or '', album_id=e.get('album_id') or '', artists=[e.get('uploader') or 'Deezer'], tags=Tags(), codec=CodecEnum.NONE, cover_url=e.get('thumbnail') or '', release_year=0, duration=e.get('duration') or 0, download_extra_kwargs={'webpage_url': e.get('webpage_url') or url})

    def get_track_download(self, webpage_url=None, **kwargs):
        if not webpage_url:
            webpage_url = kwargs.get('webpage_url')
        if not webpage_url:
            raise Exception('No webpage_url provided')
        info = self._run_yt_dlp_json(webpage_url)
        formats = info.get('formats') or []
        audio_formats = [f for f in formats if f.get('vcodec') == 'none']
        if not audio_formats:
            audio_formats = formats
        best = sorted(audio_formats, key=lambda x: ((x.get('abr') or 0), (x.get('filesize') or 0)), reverse=True)[0]
        url = best.get('url')
        headers = best.get('http_headers') or {}
        return TrackDownloadInfo(download_type=DownloadEnum.URL, file_url=url, file_url_headers=headers)

    def get_playlist_info(self, playlist_id, **kwargs):
        url = playlist_id if str(playlist_id).startswith('http') else f'https://www.deezer.com/playlist/{playlist_id}'
        data = self._run_yt_dlp_json(url)
        title = data.get('title') or 'Playlist'
        entries = data.get('entries') or []
        tracks = [e.get('webpage_url') for e in entries if e.get('webpage_url')]
        pi = PlaylistInfo(name=title, creator=data.get('uploader') or 'Deezer', tracks=tracks, release_year=0, duration=sum((e.get('duration') or 0) for e in entries), explicit=False)
        return pi
