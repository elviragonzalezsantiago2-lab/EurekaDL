from utils.models import ModuleInformation, ModuleModes, ModuleFlags, ManualEnum

module_information = ModuleInformation(
    service_name='spotify',
    module_supported_modes=ModuleModes.download,
    global_settings={},
    session_settings={},
    flags=ModuleFlags.hidden,
    netlocation_constant='spotify'
)

class ModuleInterface:
    def __init__(self, controller):
        self.controller = controller

    def search(self, media_type, query, limit=10):
        raise NotImplementedError('Search is not implemented for the spotify stub. See modules/spotify/README.md')

    def custom_url_parse(self, url):
        raise NotImplementedError('URL parsing is not implemented for the spotify stub.')

    # Downloader expects download-like methods; implement as needed.
    def download_track(self, track_id, **kwargs):
        raise NotImplementedError('Download not implemented for spotify stub.')
