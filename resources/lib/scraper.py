# -*- coding: utf-8 -*-
"""
DoraBash Scraper Module
Handles all web scraping operations
"""


import re
import requests
from bs4 import BeautifulSoup
from . import utils


BASE_URL = 'https://dorabash.com'


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Referer': BASE_URL
}


# Create a session for connection pooling and better performance
_session = None



def get_session():
    """Get or create requests session for connection pooling"""
    global _session
    if _session is None:
        _session = requests.Session()
        _session.headers.update(HEADERS)
        # Set max retries and timeouts
        from requests.adapters import HTTPAdapter
        from requests.packages.urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=2,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_maxsize=5)
        _session.mount("http://", adapter)
        _session.mount("https://", adapter)
    return _session



def get_timeout():
    """Get timeout from settings"""
    try:
        import xbmcaddon
        addon = xbmcaddon.Addon()
        return int(addon.getSetting('timeout'))
    except:
        return 15



def get_movies(page=1, category='hindi-dubbed-movies'):
    """Scrape movies from DoraBash by category
    
    Args:
        page (int): Page number to fetch
        category (str): Movie category ('hindi-dubbed-movies' or 'english-subbed-movies')
        
    Returns:
        list: List of movie dictionaries with title, url, thumbnail, etc.
    """
    utils.log(f"Scraping {category} - Page {page}")
    
    url = f'{BASE_URL}/tag/{category}/page/{page}/' if page > 1 else f'{BASE_URL}/tag/{category}/'
    
    try:
        session = get_session()
        response = session.get(url, timeout=get_timeout())
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        cards = soup.find_all('article', class_='bs')
        movies = []
        
        for card in cards:
            try:
                link_tag = card.find('a', class_='tip')
                if not link_tag:
                    continue
                    
                movie_url = link_tag.get('href', '')
                if not movie_url:
                    continue
                
                title_tag = card.find('h2', itemprop='headline')
                title = title_tag.get_text(strip=True) if title_tag else 'Unknown'
                
                img_tag = card.find('img', class_='ts-post-image')
                thumbnail = img_tag.get('src', '') if img_tag else ''
                
                status_tag = card.find('span', class_='epx')
                status = status_tag.get_text(strip=True) if status_tag else 'N/A'
                
                type_tag = card.find('div', class_='typez')
                content_type = type_tag.get_text(strip=True) if type_tag else 'Movie'
                
                movies.append({
                    'title': title,
                    'url': movie_url,
                    'thumbnail': thumbnail,
                    'status': status,
                    'type': content_type
                })
            except Exception as e:
                utils.log(f"Error parsing movie card: {e}", level=utils.LOGERROR)
                continue
        
        utils.log(f"Found {len(movies)} movies")
        return movies
        
    except Exception as e:
        utils.log(f"Error fetching movies: {e}", level=utils.LOGERROR)
        raise



def search(query):
    """Search for content on DoraBash
    
    Args:
        query (str): Search query
        
    Returns:
        list: List of search result dictionaries
    """
    utils.log(f"Searching for: {query}")
    
    search_url = f'{BASE_URL}/?s={query}'
    
    try:
        session = get_session()
        response = session.get(search_url, timeout=get_timeout())
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        cards = soup.find_all('article', class_='bs')
        results = []
        
        for card in cards:
            try:
                link_tag = card.find('a', class_='tip')
                if not link_tag:
                    continue
                    
                result_url = link_tag.get('href', '')
                if not result_url:
                    continue
                
                title_tag = card.find('h2', itemprop='headline')
                title = title_tag.get_text(strip=True) if title_tag else 'Unknown'
                
                img_tag = card.find('img', class_='ts-post-image')
                thumbnail = img_tag.get('src', '') if img_tag else ''
                
                status_tag = card.find('span', class_='epx')
                status = status_tag.get_text(strip=True) if status_tag else 'N/A'
                
                type_tag = card.find('div', class_='typez')
                content_type = type_tag.get_text(strip=True) if type_tag else 'N/A'
                
                results.append({
                    'title': title,
                    'url': result_url,
                    'thumbnail': thumbnail,
                    'status': status,
                    'type': content_type
                })
            except Exception as e:
                utils.log(f"Error parsing search result: {e}", level=utils.LOGERROR)
                continue
        
        utils.log(f"Found {len(results)} search results")
        return results
        
    except Exception as e:
        utils.log(f"Error searching: {e}", level=utils.LOGERROR)
        raise



def extract_video_url(content_url, preferred_quality='720'):
    """Extract video streaming URL from content page"""
    utils.log(f"=== EXTRACTING VIDEO ===", level=utils.LOGERROR)
    utils.log(f"Content URL: {content_url}", level=utils.LOGERROR)
    utils.log(f"Preferred quality: {preferred_quality}p", level=utils.LOGERROR)
    
    session = None
    response = None
    
    try:
        session = get_session()
        timeout = get_timeout()
        
        # ===== STEP 1: Fetch the main content page =====
        utils.log("Fetching content page...", level=utils.LOGERROR)
        response = session.get(content_url, timeout=timeout, allow_redirects=True)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        response.close()
        response = None
        
        player_url = content_url
        
        # ===== STEP 2: Check if this is an info page (has /anime/) =====
        if '/anime/' in content_url:
            utils.log("INFO PAGE detected - constructing player URL", level=utils.LOGERROR)
            player_url = content_url.replace('/anime/', '/')
            utils.log(f"Player URL: {player_url}", level=utils.LOGERROR)
            
            # Fetch player page
            response = session.get(player_url, timeout=timeout, allow_redirects=True)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            response.close()
            response = None
        else:
            utils.log("PLAYER PAGE detected (no /anime/ in URL)", level=utils.LOGERROR)
        
        # ===== STEP 3: Check for direct video tag =====
        utils.log("Looking for direct video tag...", level=utils.LOGERROR)
        video_tag = soup.find('video')
        
        if video_tag:
            utils.log("Found direct video tag!", level=utils.LOGERROR)
            sources = video_tag.find_all('source')
            
            if sources:
                video_urls = {}
                for source in sources:
                    src = source.get('src')
                    quality = source.get('size', 'unknown')
                    if src and quality != 'unknown':
                        if src.startswith('//'):
                            src = 'https:' + src
                        video_urls[quality] = src
                
                if video_urls:
                    utils.log(f"Found direct video qualities: {list(video_urls.keys())}", level=utils.LOGERROR)
                    return _select_quality(video_urls, preferred_quality)
        
        # ===== STEP 4: Look for iframe =====
        utils.log("No direct video - looking for iframe...", level=utils.LOGERROR)
        iframe = soup.find('iframe')
        
        if not iframe:
            utils.log("ERROR: No iframe found!", level=utils.LOGERROR)
            return None
        
        iframe_src = iframe.get('src', '')
        if not iframe_src:
            utils.log("ERROR: Empty iframe src!", level=utils.LOGERROR)
            return None
        
        utils.log(f"Found iframe: {iframe_src}", level=utils.LOGERROR)
        
        # ===== STEP 5: Route to appropriate extractor =====
        if 'blogspot' in iframe_src.lower():
            utils.log(">>> ROUTING TO BLOGSPOT EXTRACTOR", level=utils.LOGERROR)
            return _extract_from_blogspot(iframe_src, player_url, session, timeout, preferred_quality)
        elif 'filemoon' in iframe_src.lower():
            utils.log(">>> ROUTING TO FILEMOON EXTRACTOR", level=utils.LOGERROR)
            return _extract_from_filemoon(iframe_src, player_url, session, timeout, preferred_quality)
        else:
            utils.log(f"ERROR: Unsupported iframe provider: {iframe_src}", level=utils.LOGERROR)
            return None
        
    except requests.exceptions.Timeout:
        utils.log("ERROR: Request timeout!", level=utils.LOGERROR)
        return None
    except requests.exceptions.RequestException as e:
        utils.log(f"ERROR: Request failed: {e}", level=utils.LOGERROR)
        return None
    except Exception as e:
        utils.log(f"ERROR: Exception: {e}", level=utils.LOGERROR)
        import traceback
        utils.log(f"Traceback: {traceback.format_exc()}", level=utils.LOGERROR)
        return None
    finally:
        try:
            if response is not None:
                response.close()
        except:
            pass

def _extract_from_blogspot(iframe_src, player_url, session, timeout, preferred_quality):
    """Extract video from Blogspot iframe (used for Movies)
    
    Args:
        iframe_src (str): Blogspot iframe URL
        player_url (str): The player page URL (for referer)
        session: Requests session
        timeout (int): Request timeout
        preferred_quality (str): Preferred video quality
        
    Returns:
        dict: Video URL info or None
    """
    utils.log("Fetching Blogspot iframe content")
    
    iframe_response = None
    try:
        iframe_headers = HEADERS.copy()
        iframe_headers['Referer'] = player_url
        
        iframe_response = session.get(iframe_src, headers=iframe_headers, timeout=timeout, allow_redirects=True)
        iframe_response.raise_for_status()
        iframe_soup = BeautifulSoup(iframe_response.content, 'html.parser')
        
        iframe_response.close()
        iframe_response = None
        
        video_tag = iframe_soup.find('video')
        if not video_tag:
            utils.log("No video tag in Blogspot iframe", level=utils.LOGERROR)
            return None
        
        sources = video_tag.find_all('source')
        if not sources:
            utils.log("No video sources in Blogspot iframe", level=utils.LOGERROR)
            return None
        
        video_urls = {}
        for source in sources:
            src = source.get('src')
            quality = source.get('size', 'unknown')
            if src and quality != 'unknown':
                if src.startswith('//'):
                    src = 'https:' + src
                video_urls[quality] = src
        
        utils.log(f"Found Blogspot qualities: {list(video_urls.keys())}")
        return _select_quality(video_urls, preferred_quality)
        
    except Exception as e:
        utils.log(f"Error extracting from Blogspot: {e}", level=utils.LOGERROR)
        return None
    finally:
        if iframe_response is not None:
            try:
                iframe_response.close()
            except:
                pass


def _extract_from_filemoon(iframe_src, player_url, session, timeout, preferred_quality):
    """Extract video from Filemoon - find the HLS master.m3u8 URL"""
    utils.log("=== FILEMOON EXTRACTION START ===", level=utils.LOGERROR)
    utils.log(f"Iframe URL: {iframe_src}", level=utils.LOGERROR)
    
    if iframe_src.startswith('//'):
        iframe_src = 'https:' + iframe_src
    
    try:
        import re
        from urllib.parse import urlparse, urljoin
        
        # Fetch the embed page
        filemoon_headers = HEADERS.copy()
        filemoon_headers['Referer'] = player_url
        filemoon_headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        
        utils.log("Fetching Filemoon embed page...", level=utils.LOGERROR)
        response = session.get(iframe_src, headers=filemoon_headers, timeout=timeout, allow_redirects=True)
        response.raise_for_status()
        
        html = response.text
        response.close()
        
        utils.log(f"Page HTML length: {len(html)} chars", level=utils.LOGERROR)
        
        # METHOD 1: Search for master.m3u8 URLs directly in the page
        # These would be the full URLs with tokens
        master_m3u8_pattern = r'(https?://[a-z0-9\.\-]+\.com/hls[0-9]?/[^"\'\s<>]+/master\.m3u8[^"\'\s<>]*)'
        master_matches = re.findall(master_m3u8_pattern, html, re.IGNORECASE)
        
        if master_matches:
            utils.log(f"Found {len(master_matches)} master.m3u8 URL(s) in HTML", level=utils.LOGERROR)
            
            for m3u8_url in master_matches:
                # Clean up the URL
                m3u8_url = m3u8_url.split('\\')[0].split('"')[0].split("'")[0]
                
                utils.log(f"Testing: {m3u8_url[:100]}...", level=utils.LOGERROR)
                
                try:
                    test_headers = HEADERS.copy()
                    test_headers['Referer'] = iframe_src
                    test_headers['Origin'] = 'https://filemoon.in'
                    
                    test_resp = session.get(m3u8_url, headers=test_headers, timeout=5)
                    
                    if test_resp.status_code == 200:
                        content = test_resp.text
                        
                        # Check if it's a valid M3U8 playlist
                        if '#EXTM3U' in content and '#EXT-X-STREAM-INF' in content:
                            utils.log(f"SUCCESS: Valid M3U8 playlist found!", level=utils.LOGERROR)
                            utils.log(f"Full URL: {m3u8_url}", level=utils.LOGERROR)
                            test_resp.close()
                            
                            return {
                                'url': m3u8_url,
                                'quality': 'auto',
                                'type': 'hls'
                            }
                    
                    test_resp.close()
                    utils.log(f"Not valid (status {test_resp.status_code})", level=utils.LOGERROR)
                    
                except Exception as e:
                    utils.log(f"Test failed: {e}", level=utils.LOGERROR)
                    continue
        
        # METHOD 2: Search for ANY .m3u8 URLs (not just master.m3u8)
        utils.log("Searching for any .m3u8 URLs...", level=utils.LOGERROR)
        
        any_m3u8_pattern = r'(https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*)'
        any_matches = re.findall(any_m3u8_pattern, html)
        
        if any_matches:
            utils.log(f"Found {len(any_matches)} .m3u8 URL(s)", level=utils.LOGERROR)
            
            for m3u8_url in any_matches:
                m3u8_url = m3u8_url.split('\\')[0].split('"')[0].split("'")[0]
                
                # Prioritize URLs with query parameters (they likely have auth tokens)
                if '?' in m3u8_url:
                    utils.log(f"Testing (has params): {m3u8_url[:100]}...", level=utils.LOGERROR)
                    
                    try:
                        test_headers = HEADERS.copy()
                        test_headers['Referer'] = iframe_src
                        
                        test_resp = session.get(m3u8_url, headers=test_headers, timeout=5)
                        
                        if test_resp.status_code == 200 and '#EXTM3U' in test_resp.text:
                            utils.log(f"SUCCESS: Working M3U8 with auth!", level=utils.LOGERROR)
                            test_resp.close()
                            
                            return {
                                'url': m3u8_url,
                                'quality': 'auto',
                                'type': 'hls'
                            }
                        
                        test_resp.close()
                    except:
                        continue
        
        # METHOD 3: Fetch JavaScript files and search there
        utils.log("Searching JavaScript files...", level=utils.LOGERROR)
        
        js_urls = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', html)
        
        for js_url in js_urls:
            # Make full URL
            if not js_url.startswith('http'):
                js_url = urljoin(iframe_src, js_url)
            
            utils.log(f"Fetching JS: {js_url[:80]}...", level=utils.LOGERROR)
            
            try:
                js_resp = session.get(js_url, headers=filemoon_headers, timeout=timeout)
                
                if js_resp.status_code == 200:
                    js_content = js_resp.text
                    
                    # Search for M3U8 URLs in JavaScript
                    js_m3u8_matches = re.findall(any_m3u8_pattern, js_content)
                    
                    if js_m3u8_matches:
                        utils.log(f"Found {len(js_m3u8_matches)} M3U8 in JS", level=utils.LOGERROR)
                        
                        for m3u8_url in js_m3u8_matches:
                            m3u8_url = m3u8_url.split('\\')[0].split('"')[0]
                            
                            if '?' in m3u8_url and 'master.m3u8' in m3u8_url:
                                utils.log(f"Found master.m3u8 in JS: {m3u8_url[:100]}", level=utils.LOGERROR)
                                
                                try:
                                    test_resp = session.get(m3u8_url, headers={'Referer': iframe_src}, timeout=5)
                                    if test_resp.status_code == 200 and '#EXTM3U' in test_resp.text:
                                        utils.log("SUCCESS from JS!", level=utils.LOGERROR)
                                        test_resp.close()
                                        js_resp.close()
                                        
                                        return {
                                            'url': m3u8_url,
                                            'quality': 'auto',
                                            'type': 'hls'
                                        }
                                    test_resp.close()
                                except:
                                    continue
                    
                js_resp.close()
                
            except Exception as e:
                utils.log(f"JS fetch failed: {e}", level=utils.LOGERROR)
                continue
        
        # If nothing found, log the page for debugging
        utils.log("FAILED: No M3U8 URL found", level=utils.LOGERROR)
        utils.log(f"Page preview: {html[:1000]}", level=utils.LOGERROR)
        
        return None
        
    except Exception as e:
        utils.log(f"FILEMOON ERROR: {e}", level=utils.LOGERROR)
        import traceback
        utils.log(traceback.format_exc(), level=utils.LOGERROR)
        return None



def _select_quality(video_urls, preferred_quality):
    """Helper function to select video quality from available options
    
    Args:
        video_urls (dict): Dictionary of quality -> url
        preferred_quality (str): Preferred quality
        
    Returns:
        dict: Dictionary with 'url' and 'quality' keys, or None
    """
    if not video_urls:
        utils.log("No valid video URLs found", level=utils.LOGERROR)
        return None
    
    # Try preferred quality
    if preferred_quality in video_urls:
        selected_url = video_urls[preferred_quality]
        utils.log(f"Using preferred quality: {preferred_quality}p")
        return {
            'url': selected_url,
            'quality': preferred_quality
        }
    
    # Try 720p as fallback
    if '720' in video_urls:
        selected_url = video_urls['720']
        utils.log("Preferred quality not available, using 720p")
        return {
            'url': selected_url,
            'quality': '720'
        }
    
    # Use first available quality
    fallback_quality = list(video_urls.keys())[0]
    selected_url = video_urls[fallback_quality]
    utils.log(f"Using fallback quality: {fallback_quality}p")
    return {
        'url': selected_url,
        'quality': fallback_quality
    }
