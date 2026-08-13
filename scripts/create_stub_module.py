#!/usr/bin/env python3
"""Create a simple stub module for EurekaDL's modules/<name> that is importable by the loader.
Usage: python scripts/create_stub_module.py <service_name>
This writes modules/<service_name>/interface.py and README.md with guidance to implement a full module.
"""
import os
import sys

TEMPLATE = '''from utils.models import ModuleInformation, ModuleModes, ModuleFlags, ManualEnum

module_information = ModuleInformation(
    service_name='{service_name}',
    module_supported_modes=ModuleModes.download,
    global_settings={{}},
    session_settings={{}},
    flags=ModuleFlags.hidden,
    netlocation_constant='{service_name}'
)

class ModuleInterface:
    def __init__(self, controller):
        self.controller = controller

    def search(self, media_type, query, limit=10):
        raise NotImplementedError('Search is not implemented for the {service_name} stub. See modules/{service_name}/README.md')

    def custom_url_parse(self, url):
        raise NotImplementedError('URL parsing is not implemented for the {service_name} stub.')

    # Downloader expects download-like methods; implement as needed.
    def download_track(self, track_id, **kwargs):
        raise NotImplementedError('Download not implemented for {service_name} stub.')
'''

README = '''{service_name} module (stub)

This is a minimal placeholder module for the {service_name} service. It does not implement downloading or searching.

To implement a working module, either:
 - Write a full-featured module that follows the Orpheus/EurekaDL module interface (create modules/{service_name}/interface.py exporting module_information and ModuleInterface).
 - Or integrate an existing library (e.g., yt-dlp, spotipy) and provide wrapper functions for search and downloads.

Recommended dependencies and notes:
 - youtube: use yt-dlp for media extraction
 - spotify: use spotipy (requires Spotify API credentials to access some endpoints)
 - deezer: look for deezer API wrappers or web scraping approaches
 - soundcloud: use soundcloud API or yt-dlp
 - bandcamp: use yt-dlp or scrape album pages

If you want, run scripts/fetch_recommended_modules.py which will create these stubs automatically.
'''


def main():
    if len(sys.argv) < 2:
        print('Usage: create_stub_module.py <service_name>')
        sys.exit(2)
    name = sys.argv[1].lower()
    mod_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'modules', name)
    os.makedirs(mod_dir, exist_ok=True)
    interface_path = os.path.join(mod_dir, 'interface.py')
    readme_path = os.path.join(mod_dir, 'README.md')
    if os.path.exists(interface_path):
        print('Module already exists at', interface_path)
        return
    with open(interface_path, 'w', encoding='utf8') as f:
        f.write(TEMPLATE.format(service_name=name))
    with open(readme_path, 'w', encoding='utf8') as f:
        f.write(README.format(service_name=name))
    print('Created stub module for', name)

if __name__ == '__main__':
    main()
