# EurekaDL

A fresh, Termux-friendly fork of OrpheusDL built for mobile-first music archiving with a preinstalled TIDAL module.

This project keeps the original OrpheusDL architecture, removes the usual friction for Android/Termux usage, and focuses on a cleaner local setup experience.

## Why this project exists

This repo is a practical, modernized version of OrpheusDL for users who want to:

- run it on Android through Termux
- download music from supported services without the usual setup pain
- keep a simpler local workflow with a stable default download path
- use a ready-to-go TIDAL module in the project itself

This is meant as a clean local fork for personal use, not as a replacement for the upstream project issue tracker or module ecosystem.

## Features

- Modular music archiving architecture from OrpheusDL
- TIDAL support included in `modules/tidal`
- Android/Termux-aware default download path
- Ready-to-use config file generation flow
- Direct download/search/URL support

## Quick start

### Prerequisites

- Python 3.9+
- FFmpeg installed
- Git
- Termux users should run:

```bash
termux-setup-storage
```

### Install

```bash
git clone https://github.com/elviragonzalezsantiago2-lab/EurekaDL.git
cd EurekaDL
python -m pip install -r requirements.txt
```

### Run

Run commands using the new entrypoint `eureka.py` (alias for the original `orpheus.py`):

```bash
python eureka.py --help
python eureka.py search tidal track "Adele"
python eureka.py -o "/sdcard/Download/EurekaDL" download tidal track 92265335
python orpheus.py ...   # original entrypoint still available
```

Set a persistent default download directory for future runs:

```bash
python eureka.py --set-download-path "/sdcard/Download/EurekaDL"
python eureka.py settings download_path "/sdcard/Download/EurekaDL"
```

### Default download folder

On desktop (fallback):

```text
./downloads/
```

Android/Termux (auto-detected):

```text
/data/data/com.termux/files/home/storage/shared/EurekaDL
```

## TIDAL usage

From the project root:

```bash
python eureka.py "https://tidal.com/browse/album/92265334"
```

Search:

```bash
python eureka.py search tidal track "darkside"
```

Download by ID:

```bash
python eureka.py download tidal track 92265335
```

## Configuration

The main config file is:

```text
config/settings.json
```

Relevant section:

```json
{
 "global": {
   "general": {
     "download_path": "C:/Users/miria/Music/EurekaDL",
     "download_quality": "hifi",
     "search_limit": 10
   }
 }
}
```

## Known notes

- This project is intentionally streamlined for local use.
- TIDAL auth may be rate-limited or blocked by service-side anti-bot protections.
- The project is designed to work well in Android/Termux, but some upstream module behavior can still depend on the service provider.

## Related project

- Original upstream: https://github.com/OrfiTeam/OrpheusDL

## License

See the repository license files for full licensing terms.

## Acknowledgements

- Original OrpheusDL project
- TIDAL module contributors
- Termux/mobile user community


## Additional streaming modules

This fork provides a recommended workflow to add support for more streaming platforms (YouTube, Spotify, Deezer, SoundCloud, Bandcamp).

Quick steps to add modules:

- Create safe, importable module stubs automatically:

```bash
python scripts/fetch_recommended_modules.py
```

- Stubs are created under `modules/<service>/interface.py`. They are importable and prevent startup errors, but are placeholders that raise NotImplementedError when used. They include guidance on dependencies.

- To implement a working module:
  - For YouTube, install yt-dlp and implement an interface that returns Download URLs using yt-dlp extractors.
  - For Spotify, use spotipy for metadata (requires API keys) and combine with another provider for actual media extraction.
  - Deezer, SoundCloud, Bandcamp: yt-dlp often supports many endpoints; otherwise adapt an existing open-source OrpheusDL module.

Helper scripts:

- `scripts/create_stub_module.py <service>`: creates a minimal module scaffold.
- `scripts/fetch_recommended_modules.py`: creates stubs for recommended services and prints dependency suggestions.


## Installing the global 'eureka' command

Use the included installer to create a small wrapper in a user bin directory:

```bash
bash scripts/install_eureka.sh          # installs to a sensible default for your platform
bash scripts/install_eureka.sh --prefix /usr/local/bin
```

Supports Termux, Linux, macOS, and iOS shells (a-Shell/iSH). After installation, run `eureka --help`.


## Credits and License

EurekaDL is a personal, public fork built from the OrpheusDL project. Full credit to the original OrpheusDL project and its contributors for the modular architecture and many of the module ideas.

- Original upstream: https://github.com/OrfiTeam/OrpheusDL
- TIDAL module contributors and authors

This fork aims to be innovative and user-friendly while preserving attribution to the original project. See LICENSE files for licensing details.


