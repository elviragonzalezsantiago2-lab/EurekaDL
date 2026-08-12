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

```bash
python orpheus.py --help
```

### Default download folder

On desktop:

```text
./downloads/
```

On Termux:

```text
/data/data/com.termux/files/home/storage/shared/OrpheusDL
```

## TIDAL usage

From the project root:

```bash
python orpheus.py "https://tidal.com/browse/album/92265334"
```

Search:

```bash
python orpheus.py search tidal track "darkside"
```

Download by ID:

```bash
python orpheus.py download tidal track 92265335
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
     "download_path": "C:/Users/miria/Music/OrpheusDL",
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
