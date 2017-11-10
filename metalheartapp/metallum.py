import requests
import unidecode
import urllib.parse as urllibparse
from enum import Enum
from . import utility

Restricted_Discogs_Types = ['Video', 'Single']

#TODO: Decide that will this be used
class AlbumType(Enum):
    Demo = 0
    Full_Length = 1
    Ep = 2
    Compilation = 3
    Live_Album = 4
    Boxed_Set = 5


API_KEY = 'f8e5cf5d-88a3-466d-8eb8-6e5f5178b8a6'
SEARCH_URL = 'http://em.wemakesites.net/search/band_name/'
ALBUM_URL = 'http://em.wemakesites.net/album/'
BAND_URL = 'http://em.wemakesites.net/band/'


def search_band(keyword):
    """ search for band name in metal archives api """
    payload = {'api_key': API_KEY}
    urlparams = urllibparse.urlencode(payload)
    response = requests.get("%s?%s" % (SEARCH_URL + keyword, urlparams))
    response = response.json()
    if response['status'] == 'success' and response['code'] == 200:
        return response
    else:
        return None


class Album:
    """Represent a discography item """

    def __init__(self, album_id, name, album_type, year):
        self.album_id = album_id
        self.name = utility.remove_redundant_chars(name)
        self.type = album_type
        self.year = year


class Band(object):
    """Represent a band """

    def __init__(self, band_id, name, raw_album, raw_genre):
        self.band_id = band_id
        self.genres = [utility.remove_redundant_chars(item) for item in raw_genre.split(',')]
        self.country = None
        self.name = utility.remove_redundant_chars(name)
        self.discography = []
        for item in raw_album:
            self.discography.append(
                Album(item['id'], item['title'], item['type'], item['year']))


def get_band(band_id):
    """Get band data from metal archives and create Band object """
    band = None
    payload = {'api_key': API_KEY}
    urlparams = urllibparse.urlencode(payload)
    response = requests.get("%s?%s" % (BAND_URL + band_id, urlparams))
    if response.status_code == 200:
        data = response.json()['data']
        band = Band(data['id'], data['band_name'],
                      data['discography'], data['details']['genre'])
    return band


def search_and_filter_band(name):
    """ """
    data = search_band(name)
    band_list = []
    if(data is not None):
        search_results = data['data']['search_results']
        for item in search_results:
            if compare_artist_name(name, item['name']):
                band = get_band(item['id'])
                band_list.append(band)
    return band_list


def compare_artist_name(s_name, ma_name):
    s_name = s_name.lower()
    ma_name = ma_name.lower()
    if s_name == ma_name:
        return True
    elif unidecode.unidecode(s_name) == unidecode.unidecode(ma_name):
        return True
    else:
        return False
