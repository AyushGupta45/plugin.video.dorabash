# -*- coding: utf-8 -*-
"""
Utility functions for Dora Bash addon
"""

import sys
import xbmc
import xbmcgui
import xbmcaddon

# Log levels
LOGDEBUG = xbmc.LOGDEBUG
LOGINFO = xbmc.LOGINFO
LOGWARNING = xbmc.LOGWARNING
LOGERROR = xbmc.LOGERROR

_addon = xbmcaddon.Addon()
_addon_name = _addon.getAddonInfo('name')


def log(message, level=LOGINFO):
    """Log a message to Kodi log
    
    Args:
        message (str): Message to log
        level (int): Log level (LOGDEBUG, LOGINFO, LOGWARNING, LOGERROR)
    """
    debug_mode = _addon.getSetting('debug_mode') == 'true'
    
    if level == LOGDEBUG and not debug_mode:
        return
    
    try:
        xbmc.log(f'[{_addon_name}] {message}', level)
    except Exception:
        xbmc.log(f'[{_addon_name}] {message}', level)


def notify(message, title=None, icon=None, time=5000):
    """Show a notification to the user
    
    Args:
        message (str): Notification message
        title (str): Notification title (default: addon name)
        icon (str): Icon path (default: addon icon)
        time (int): Display time in milliseconds
    """
    if title is None:
        title = _addon_name
    
    if icon is None:
        icon = _addon.getAddonInfo('icon')
    
    xbmcgui.Dialog().notification(title, message, icon, time)


def build_url(query):
    """Build a plugin URL from a query dictionary
    
    Args:
        query (dict): Dictionary of query parameters
        
    Returns:
        str: Full plugin URL
    """
    base_url = sys.argv[0]
    query_string = '&'.join([f'{key}={value}' for key, value in query.items()])
    return f'{base_url}?{query_string}'


def get_fanart():
    """Get addon fanart path
    
    Returns:
        str: Path to fanart image
    """
    return _addon.getAddonInfo('fanart')


def get_icon():
    """Get addon icon path
    
    Returns:
        str: Path to icon image
    """
    return _addon.getAddonInfo('icon')


def get_setting(setting_id):
    """Get addon setting value
    
    Args:
        setting_id (str): Setting ID
        
    Returns:
        str: Setting value
    """
    return _addon.getSetting(setting_id)


def set_setting(setting_id, value):
    """Set addon setting value
    
    Args:
        setting_id (str): Setting ID
        value (str): Setting value
    """
    _addon.setSetting(setting_id, value)
