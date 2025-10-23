# 🎬 Dora Bash - Kodi Addon

A Kodi addon that provides a TV-friendly interface to watch Doraemon movies from [dorabash.com](https://dorabash.com).

![Main Menu](resources/media/Screenshot%201.png)

## 📖 Backstory

This addon was born from a simple childhood desire: watching Doraemon movies on TV. When the content wasn't available on YouTube or other mainstream platforms, and the only option was a website that wasn't TV-friendly, this wrapper was created to bring that nostalgic experience to Kodi.

## ✨ Features

- **Hindi Dubbed Movies** - Browse Hindi-dubbed Doraemon movies
- **English Subbed Movies** - Browse English-subbed Doraemon movies  
- **Search Functionality** - Find specific movies quickly
- **Multiple Quality Options** - Choose between 480p, 720p, and 1080p
- **Pagination Support** - Navigate through pages of content
- **Clean TV Interface** - Designed for comfortable viewing from your couch

![Movie List](resources/media/Screenshot%202.png)

## 🛠️ Technical Details

### How It Works

This addon is a **web scraper wrapper** that:
1. Fetches movie listings from dorabash.com tag pages
2. Parses HTML using BeautifulSoup to extract movie information
3. Resolves video streaming URLs from player pages or Blogspot iframes
4. Extracts multiple quality options from `<video><source>` tags
5. Plays the selected stream directly in Kodi


### File Structure

```
plugin.video.dorabash/
├── addon.xml                 # Kodi addon manifest
├── default.py                # Main entry point & routing
├── LICENSE.txt               # License & disclaimer
├── README.md                 # This file
├── changelog.txt             # Version history
├── icon.png                  # Addon icon
├── fanart.jpg                # Background art
└── resources/
    ├── settings.xml          # User configurable settings
    ├── media/                # Screenshots
    │   ├── Screenshot 1.png
    │   └── Screenshot 2.png
    └── lib/
        ├── scraper.py        # Core scraping logic
        └── utils.py          # Helper functions
```

## 📥 Installation

### Method 1: From ZIP (Recommended)

1. Download the repository as a ZIP file
2. Open Kodi
3. Navigate to **Add-ons** → **Install from zip file**
4. Select the downloaded ZIP
5. Wait for "Addon enabled" notification


### Requirements

- **Kodi 19 (Matrix)** or later
- **Python 3** (included with Kodi 19+)
- Active internet connection
- Required dependencies (auto-installed by Kodi):
  - `script.module.requests` (version 2.22.0+)
  - `script.module.beautifulsoup4` (version 4.9.3+)

## 🚀 Usage

1. Open Kodi and navigate to **Add-ons** → **Video Add-ons**
2. Select **Dora Bash**
3. Choose from:
   - **Hindi Dubbed Movies** - Browse paginated list of Hindi-dubbed content
   - **English Subbed Movies** - Browse paginated list of English-subbed content
   - **Search** - Enter keywords to find specific movies
4. Click on a movie to play
5. Video will start in your preferred quality (configurable in settings)

## ⚙️ Settings

Access addon settings by highlighting the addon and pressing **C** (context menu) → **Settings**.

### Playback Settings
- **Preferred Streaming Quality:** Choose default quality (480p / 720p / 1080p)
- **Auto-play videos:** Enable/disable automatic playback

### Advanced
- **Connection Timeout:** Adjust timeout for slow connections (5-30 seconds)
- **Enable Debug Logging:** Turn on verbose logging for troubleshooting


## ⚠️ Important Disclaimers

### Legal & Ethical Notice

- **Personal Use Only:** This addon was created for personal, non-commercial use
- **No Content Ownership:** The author does **not** own, host, or distribute any content
- **Direct Streaming:** All content is streamed directly from dorabash.com servers
- **No Affiliation:** This project is **NOT** affiliated with or endorsed by dorabash.com
- **User Responsibility:** Users are responsible for ensuring their usage complies with local laws and regulations
- **No Warranty:** This software is provided "as-is" without any warranty or support

### Content Removal

If you are the owner of dorabash.com or hold rights to the content and have concerns about this addon, please open an issue on this repository or contact the repository owner to discuss removal.

### Fair Use Statement

This addon is intended for:
- Personal, non-commercial use
- Educational purposes (understanding web scraping and Kodi addon development)
- Accessing content that may not be readily available through official channels in certain regions

Users should respect content creators and copyright holders. If official, legal alternatives exist in your region, please use those instead.

## 🐛 Troubleshooting

### Video Won't Play
- Check your internet connection
- Increase timeout in addon settings (Advanced → Connection Timeout)
- Try a different quality setting
- Check Kodi logs for specific errors

### "No movies found" Error
- The website structure may have changed
- Check if dorabash.com is accessible from your browser
- Enable debug logging to see detailed error messages

### Addon Won't Install
- Ensure you have Kodi 19 (Matrix) or later
- Check that required dependencies are available
- Try installing `script.module.requests` and `script.module.beautifulsoup4` manually first

### Slow Loading
- Decrease connection timeout if you have fast internet
- The website may be experiencing high traffic
- Check your network speed

## 🔍 How to Get Logs

1. Enable debug logging: **Settings** → **System** → **Logging** → Enable "Debug logging"
2. Enable addon debug: Addon Settings → **Advanced** → Enable "Debug Logging"
3. Reproduce the issue
4. Access logs:
   - **Windows:** `%APPDATA%\Kodi\kodi.log`
   - **Linux/Mac:** `~/.kodi/temp/kodi.log`
5. Search for `[Dora Bash]` entries

## 🛣️ Roadmap / Future Ideas

- [ ] Add caching for better performance
- [ ] Implement favorites/watchlist functionality
- [ ] Add support for subtitles (if available)
- [ ] Improve error handling and user feedback
- [ ] Add more filtering options (year, genre, etc.)
- [ ] Support for additional content categories (if they become available)

## 🤝 Contributing

This is a personal project, but contributions are welcome! If you'd like to:
- Report bugs → Open an issue
- Suggest features → Open an issue with the "enhancement" label
- Submit code → Fork, make changes, and submit a pull request

### Development Setup

```bash
# Clone the repository
git clone https://github.com/AyushGupta45/plugin.video.dorabash.git
cd plugin.video.dorabash

# Symlink to your Kodi addons directory for live testing
# Windows (PowerShell as Admin):
New-Item -ItemType SymbolicLink -Path "$env:APPDATA\Kodi\addons\plugin.video.dorabash" -Target "$(Get-Location)"

# Linux/Mac:
ln -s "$(pwd)" ~/.kodi/addons/plugin.video.dorabash

# Restart Kodi to load changes
```

## 📜 License

**PERSONAL USE ONLY**

This Kodi addon was created for personal, non-commercial use. See [LICENSE.txt](LICENSE.txt) for full details.

## 🙏 Acknowledgments

- [dorabash.com](https://dorabash.com) for hosting the content
- The Kodi development team for the excellent media center platform
- BeautifulSoup developers for the HTML parsing library
- All Doraemon fans who just want to relive their childhood 💙

## 📧 Contact

- **Repository:** [github.com/AyushGupta45/plugin.video.dorabash](https://github.com/AyushGupta45/plugin.video.dorabash)
- **Issues:** [github.com/AyushGupta45/plugin.video.dorabash/issues](https://github.com/AyushGupta45/plugin.video.dorabash/issues)

---

**Made with 💙 by a Doraemon fan who just wanted to watch movies on TV**

*Remember: This is just a wrapper to make an existing website more accessible. Always respect content creators and use legal alternatives when available.*
