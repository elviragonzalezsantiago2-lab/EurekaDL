import os
import json
import subprocess

from utils.models import ModuleInformation, ModuleModes, ModuleFlags, ManualEnum, SearchResult, TrackInfo, Tags, TrackDownloadInfo, DownloadEnum, CodecEnum, PlaylistInfo

module_information = ModuleInformation(
    service_name='Crunchyroll',
    module_supported_modes=ModuleModes.download | ModuleModes.playlist,
    global_settings={},
    session_settings={},
    flags=ModuleFlags(0),
    netlocation_constant=['crunchyroll.com']
)

class ModuleInterface:
    def __init__(self, controller):
        self.controller = controller

    def _run_yt_dlp_json(self, url_or_query, ytdlp_args=None):
        try:
            import yt_dlp as ytdl
            opts = {'quiet': True, 'skip_download': True, 'no_warnings': True}
            if ytdlp_args:
                opts.update(ytdlp_args)
            with ytdl.YoutubeDL(opts) as y:
                return y.extract_info(url_or_query, download=False)
        except Exception:
            cmd = ['yt-dlp', '-j', url_or_query]
            try:
                p = subprocess.run(cmd, capture_output=True, check=True, text=True)
                return json.loads(p.stdout)
            except Exception as e:
                raise Exception('yt-dlp not available or failed: ' + str(e))

    def search(self, media_type, query, limit=10, track_info=None):
        q = f"ytsearch{limit}:{query}"
        data = self._run_yt_dlp_json(q)
        entries = data.get('entries', []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
        results = []
        for e in entries:
            sr = SearchResult(result_id=e.get('id') or e.get('url'), name=e.get('title'), artists=[e.get('uploader') or 'Crunchyroll'], year=e.get('release_date'), explicit=False, duration=e.get('duration'), additional=[e.get('webpage_url')], extra_kwargs={'webpage_url': e.get('webpage_url')})
            results.append(sr)
        return results

    def custom_url_parse(self, url):
        return {'webpage_url': url}

    def get_track_info(self, track_id, quality_tier, codec_options, **kwargs):
        url = track_id if str(track_id).startswith('http') else f'https://www.crunchyroll.com/{track_id}'
        info = self._run_yt_dlp_json(url)
        title = info.get('title')
        uploader = info.get('uploader') or 'Crunchyroll'
        duration = info.get('duration')
        thumbnail = info.get('thumbnail') or ''
        ti = TrackInfo(name=title or url, album=info.get('album') or '', album_id=info.get('album_id') or '', artists=[uploader], tags=Tags(), codec=CodecEnum.NONE, cover_url=thumbnail, release_year=info.get('release_year') or 0, duration=duration, download_extra_kwargs={'webpage_url': info.get('webpage_url') or url})
        return ti

    def get_track_download(self, webpage_url=None, **kwargs):
        if not webpage_url:
            webpage_url = kwargs.get('webpage_url')
        if not webpage_url:
            raise Exception('No webpage_url provided to get_track_download')
        info = self._run_yt_dlp_json(webpage_url)
        formats = info.get('formats') or []
        audio_formats = [f for f in formats if f.get('vcodec') == 'none' or (f.get('acodec') and not f.get('vcodec'))]
        if not audio_formats:
            audio_formats = formats
        best = sorted(audio_formats, key=lambda x: ((x.get('abr') or 0), (x.get('filesize') or 0)), reverse=True)[0]
        url = best.get('url')
        headers = best.get('http_headers') or {}
        return TrackDownloadInfo(download_type=DownloadEnum.URL, file_url=url, file_url_headers=headers)

    def get_playlist_info(self, playlist_id, **kwargs):
        url = playlist_id if str(playlist_id).startswith('http') else f'https://www.crunchyroll.com/series/{playlist_id}'
        data = self._run_yt_dlp_json(url)
        title = data.get('title') or 'Crunchyroll Playlist'
        entries = data.get('entries') or []
        tracks = [e.get('webpage_url') for e in entries if e.get('webpage_url')]
        pi = PlaylistInfo(name=title, creator=data.get('uploader') or 'Crunchyroll', tracks=tracks, release_year=0, duration=sum((e.get('duration') or 0) for e in entries), explicit=False)
        return pi
