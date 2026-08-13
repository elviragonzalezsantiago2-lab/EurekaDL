bandcamp module (stub)

This is a minimal placeholder module for the bandcamp service. It does not implement downloading or searching.

To implement a working module, either:
 - Write a full-featured module that follows the Orpheus/EurekaDL module interface (create modules/bandcamp/interface.py exporting module_information and ModuleInterface).
 - Or integrate an existing library (e.g., yt-dlp, spotipy) and provide wrapper functions for search and downloads.

Recommended dependencies and notes:
 - youtube: use yt-dlp for media extraction
 - spotify: use spotipy (requires Spotify API credentials to access some endpoints)
 - deezer: look for deezer API wrappers or web scraping approaches
 - soundcloud: use soundcloud API or yt-dlp
 - bandcamp: use yt-dlp or scrape album pages

If you want, run scripts/fetch_recommended_modules.py which will create these stubs automatically.
