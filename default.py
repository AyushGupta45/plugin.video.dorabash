# -*- coding: utf-8 -*-
"""
Dora Bash Kodi Addon
Main entry point for the addon
"""

import sys
from urllib.parse import parse_qsl
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

# Import our scraper library
from resources.lib import scraper
from resources.lib import utils

# Get addon handle and info
_addon = xbmcaddon.Addon()
_addon_id = _addon.getAddonInfo('id')
_addon_name = _addon.getAddonInfo('name')
_addon_handle = int(sys.argv[1])


def list_categories():
    """List main categories: Hindi Dubbed Movies, English Subbed Movies, Search"""
    utils.log("Listing main categories")
    
    categories = [
        {
            'name': 'Hindi Dubbed Movies',
            'mode': 'hindi_dubbed_movies',
            'icon': 'DefaultMovies.png',
            'fanart': utils.get_fanart()
        },
        {
            'name': 'English Subbed Movies',
            'mode': 'english_subbed_movies',
            'icon': 'DefaultMovies.png',
            'fanart': utils.get_fanart()
        },
        {
            'name': 'Search',
            'mode': 'search',
            'icon': 'DefaultAddonsSearch.png',
            'fanart': utils.get_fanart()
        }
    ]

    
    for category in categories:
        list_item = xbmcgui.ListItem(label=category['name'])
        list_item.setArt({
            'icon': category['icon'],
            'fanart': category['fanart']
        })
        list_item.setInfo('video', {'title': category['name']})
        
        url = utils.build_url({'mode': category['mode']})
        xbmcplugin.addDirectoryItem(_addon_handle, url, list_item, isFolder=True)
    
    xbmcplugin.endOfDirectory(_addon_handle)


def list_movies(page=1, category='hindi-dubbed-movies'):
    """List movies from DoraBash by category"""
    utils.log(f"Listing {category} - Page {page}")
    
    try:
        movies = scraper.get_movies(page, category)
        
        if not movies:
            utils.notify("No movies found")
            xbmcplugin.endOfDirectory(_addon_handle)
            return
        
        for movie in movies:
            list_item = xbmcgui.ListItem(label=movie['title'])
            
            list_item.setArt({
                'thumb': movie.get('thumbnail', ''),
                'poster': movie.get('thumbnail', ''),
                'fanart': utils.get_fanart()
            })
            
            list_item.setInfo('video', {
                'title': movie['title'],
                'plot': f"Status: {movie.get('status', 'N/A')}\nType: {movie.get('type', 'Movie')}",
                'mediatype': 'movie'
            })
            
            list_item.setProperty('IsPlayable', 'true')
            
            url = utils.build_url({
                'mode': 'play',
                'url': movie['url']
            })
            
            xbmcplugin.addDirectoryItem(_addon_handle, url, list_item, isFolder=False)
        
        # Add "Next Page" option
        next_item = xbmcgui.ListItem(label='Next Page >>')
        mode_name = 'hindi_dubbed_movies' if category == 'hindi-dubbed-movies' else 'english_subbed_movies'
        next_url = utils.build_url({'mode': mode_name, 'page': str(page + 1)})
        xbmcplugin.addDirectoryItem(_addon_handle, next_url, next_item, isFolder=True)
        
        xbmcplugin.addSortMethod(_addon_handle, xbmcplugin.SORT_METHOD_NONE)
        xbmcplugin.setContent(_addon_handle, 'movies')
        xbmcplugin.endOfDirectory(_addon_handle, cacheToDisc=True)
        
    except Exception as e:
        utils.log(f"Error listing movies: {e}", level=xbmc.LOGERROR)
        utils.notify(f"Error loading movies: {str(e)}")
        xbmcplugin.endOfDirectory(_addon_handle, succeeded=False)


def search():
    """Search for content"""
    utils.log("Opening search dialog")
    
    keyboard = xbmcgui.Dialog().input('Search Doraemon', type=xbmcgui.INPUT_ALPHANUM)
    
    if keyboard:
        utils.log(f"Searching for: {keyboard}")
        try:
            results = scraper.search(keyboard)
            
            if not results:
                utils.notify("No results found")
                xbmcplugin.endOfDirectory(_addon_handle)
                return
            
            for result in results:
                list_item = xbmcgui.ListItem(label=result['title'])
                
                list_item.setArt({
                    'thumb': result.get('thumbnail', ''),
                    'poster': result.get('thumbnail', ''),
                    'fanart': utils.get_fanart()
                })
                
                list_item.setInfo('video', {
                    'title': result['title'],
                    'plot': f"Status: {result.get('status', 'N/A')}\nType: {result.get('type', 'N/A')}",
                    'mediatype': 'video'
                })
                
                list_item.setProperty('IsPlayable', 'true')
                
                url = utils.build_url({
                    'mode': 'play',
                    'url': result['url']
                })
                
                xbmcplugin.addDirectoryItem(_addon_handle, url, list_item, isFolder=False)
            
            xbmcplugin.setContent(_addon_handle, 'videos')
            xbmcplugin.endOfDirectory(_addon_handle, cacheToDisc=False)
            
        except Exception as e:
            utils.log(f"Error searching: {e}", level=xbmc.LOGERROR)
            utils.notify(f"Error searching: {str(e)}")
            xbmcplugin.endOfDirectory(_addon_handle, succeeded=False)
    else:
        xbmcplugin.endOfDirectory(_addon_handle)


def play_video(url):
    """Extract and play video from given URL"""
    utils.log(f"Playing video from: {url}")
    
    progress = None
    try:
        # Show progress dialog
        progress = xbmcgui.DialogProgress()
        progress.create('Dora Bash', 'Getting video URL...')
        
        # Get preferred quality from settings
        preferred_quality = _addon.getSetting('preferred_quality')
        utils.log(f"Preferred quality: {preferred_quality}p")
        
        progress.update(30, 'Extracting video sources...')
        
        # ===== CRITICAL: ALL SCRAPING MUST HAPPEN BEFORE PLAYBACK =====
        # Extract video URLs - this does all network requests and parsing
        video_urls = scraper.extract_video_url(url, preferred_quality)
        
        if not video_urls:
            utils.log("Failed to extract video URL", level=xbmc.LOGERROR)
            utils.notify("Could not extract video URL")
            xbmcplugin.setResolvedUrl(_addon_handle, False, xbmcgui.ListItem())
            return  # Exit immediately on failure
        
        # Extract the final video URL - no more network requests after this
        video_url = video_urls['url']
        quality = video_urls['quality']
        
        utils.log(f"Successfully extracted {quality}p video URL")
        progress.update(70, 'Preparing playback...')
        
        # Prepare playable item with all properties set
        play_item = xbmcgui.ListItem(path=video_url)
        play_item.setInfo('video', {
            'title': f"Doraemon - {quality}p",
            'mediatype': 'video'
        })
        play_item.setMimeType('video/mp4')
        play_item.setContentLookup(False)
        play_item.setProperty('inputstream', 'inputstream.ffmpegdirect')
        play_item.setProperty('mimetype', 'video/mp4')
        
        # Add HTTP headers to URL if not already present
        if '|' not in video_url:
            headers = 'User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36&Referer=https://dorabash.com/'
            video_url_with_headers = f"{video_url}|{headers}"
            play_item.setPath(video_url_with_headers)
        
        # ===== CRITICAL: Close progress dialog BEFORE playback =====
        progress.close()
        progress = None
        
        utils.log("Starting playback - exiting addon script")
        
        # ===== CRITICAL: Start playback and EXIT IMMEDIATELY =====
        # setResolvedUrl hands control to Kodi's player
        # The addon script MUST exit right after this call
        xbmcplugin.setResolvedUrl(_addon_handle, True, listitem=play_item)
        
        # ===== EXIT IMMEDIATELY - No code after playback! =====
        return
        
    except Exception as e:
        utils.log(f"Error playing video: {e}", level=xbmc.LOGERROR)
        utils.notify(f"Error playing video: {str(e)}")
        xbmcplugin.setResolvedUrl(_addon_handle, False, xbmcgui.ListItem())
        return  # Exit immediately on error
    finally:
        # Ensure progress dialog is always closed
        if progress is not None:
            try:
                progress.close()
            except:
                pass


def router(paramstring):
    """Route to appropriate function based on parameters"""
    params = dict(parse_qsl(paramstring))
    
    try:
        if not params:
            # Main menu
            list_categories()
        else:
            mode = params.get('mode')
            
            if mode == 'hindi_dubbed_movies':
                page = int(params.get('page', 1))
                list_movies(page, 'hindi-dubbed-movies')
            elif mode == 'english_subbed_movies':
                page = int(params.get('page', 1))
                list_movies(page, 'english-subbed-movies')
            elif mode == 'search':
                search()
            elif mode == 'play':
                # CRITICAL: play_video will handle playback and exit
                play_video(params['url'])
                # Exit immediately after play_video returns
                return
            else:
                list_categories()
    except Exception as e:
        utils.log(f"Router error: {e}", level=xbmc.LOGERROR)
        xbmcplugin.endOfDirectory(_addon_handle, succeeded=False)


if __name__ == '__main__':
    router(sys.argv[2][1:])
    # Script ends here - no code should run after router completes
