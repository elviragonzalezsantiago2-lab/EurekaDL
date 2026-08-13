import os
import json
import subprocess

from utils.models import ModuleInformation, ModuleModes, ModuleFlags, ManualEnum, SearchResult, TrackInfo, Tags, TrackDownloadInfo, DownloadEnum, CodecEnum, PlaylistInfo

module_information = ModuleInformation(
    service_name='spotify',
    module_supported_modes=ModuleModes.download | ModuleModes.playlist,
    global_settings={},
    session_settings={},
    flags=ModuleFlags.hidden,
    netlocation_constant=['spotify.com', 'open.spotify.com']
)

class ModuleInterface:
    def __init__(self, controller):
        self.controller = controller

    def _spotipy_search(self, media_type, query, limit=10):
        try:
            import spotipy
            from spotipy.oauth2 import SpotifyClientCredentials
            client_id = os.environ.get('SPOTIPY_CLIENT_ID')
            client_secret = os.environ.get('SPOTIPY_CLIENT_SECRET')
            if not client_id or not client_secret:
                raise RuntimeError('SPOTIPY credentials not set')
            auth = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
            sp = spotipy.Spotify(client_credentials_manager=auth)
            results = []
            q = query
            if media_type.name == 'track':
                items = sp.search(q=q, type='track', limit=limit).get('tracks', {}).get('items', [])
                for it in items:
                    sr = SearchResult(result_id=it['id'], name=it['name'], artists=[a['name'] for a in it['artists']], year=None, explicit=it.get('explicit', False), duration=int(it.get('duration_ms',0)/1000), additional=[it['external_urls'].get('spotify')], extra_kwargs={'spotify_id': it['id']})
                    results.append(sr)
            else:
                # fallback to generic search
                items = sp.search(q=q, type='artist,album,playlist', limit=limit)
                # Simplified parsing omitted for brevity
            return results
        except Exception:
            return []

    def _yt_dlp_search(self, media_type, query, limit=10):
        # fallback to yt-dlp search on YouTube equivalents
        from modules.youtube.interface import ModuleInterface as YT
        return YT(None).search(media_type, query, limit)

    def search(self, media_type, query, limit=10):
        results = self._spotipy_search(media_type, query, limit=limit)
        if results:
            return results
        return self._yt_dlp_search(media_type, query, limit=limit)

    def custom_url_parse(self, url):
        # open.spotify.com URLs typically contain /track/<id> or /playlist/<id>
        components = url.split('/')
        for i, c in enumerate(components):
            if c in ('track', 'playlist', 'album') and i+1 < len(components):
                return {'spotify_id': components[i+1].split('?')[0], 'webpage_url': url}
        return {'webpage_url': url}

    def get_track_info(self, track_id, quality_tier, codec_options, **kwargs):
        # track_id may be Spotify ID or a url
        sid = track_id if isinstance(track_id, str) and '/' not in track_id else (kwargs.get('spotify_id') or track_id)
        # Try spotipy first
        try:
            import spotipy
            from spotipy.oauth2 import SpotifyClientCredentials
            client_id = os.environ.get('SPOTIPY_CLIENT_ID')
            client_secret = os.environ.get('SPOTIPY_CLIENT_SECRET')
            if client_id and client_secret:
                auth = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
                sp = spotipy.Spotify(client_credentials_manager=auth)
                t = sp.track(sid)
                title = t.get('name')
                artists = [a['name'] for a in t.get('artists', [])]
                duration = int(t.get('duration_ms', 0)/1000)
                album = t.get('album', {}).get('name', '')
                cover = t.get('album', {}).get('images', [{}])[0].get('url', '')
                return TrackInfo(name=title or sid, album=album, album_id=t.get('album', {}).get('id',''), artists=artists, tags=Tags(), codec=CodecEnum.NONE, cover_url=cover, release_year=0, duration=duration, download_extra_kwargs={'spotify_id': sid})
        except Exception:
            pass
        # fallback to yt-dlp via YouTube search
        from modules.youtube.interface import ModuleInterface as YT
        items = YT(None).search(DownloadEnum.track, title := (kwargs.get('query') or sid), limit=1)
        if items:
            si = items[0]
            return TrackInfo(name=si.name, album='', album_id='', artists=si.artists, tags=Tags(), codec=CodecEnum.NONE, cover_url=si.extra_kwargs.get('webpage_url',''), release_year=0, duration=si.duration, download_extra_kwargs=si.extra_kwargs)
        raise Exception('Could not fetch track info for spotify id')

    def get_track_download(self, webpage_url=None, **kwargs):
        # Prefer yt-dlp extraction of YouTube equivalent; if spotify id present, resolve to a YouTube search
        if kwargs.get('spotify_id'):
            query = kwargs['spotify_id']
            # Use yt-dlp to find a likely youtube match
            from modules.youtube.interface import ModuleInterface as YT
            items = YT(None).search(DownloadEnum.track, query, limit=1)
            if items:
                return YT(None).get_track_download(webpage_url=items[0].extra_kwargs.get('webpage_url'))
        if webpage_url:
            # use yt-dlp/youTube fallback
            from modules.youtube.interface import ModuleInterface as YT
            return YT(None).get_track_download(webpage_url=webpage_url)
        raise Exception('No spotify id or webpage_url provided')

    def get_playlist_info(self, playlist_id, **kwargs):
        # Simple fallback: return empty playlist info when not supported
        return PlaylistInfo(name='Spotify Playlist', creator='', tracks=[], release_year=0, duration=0, explicit=False)
