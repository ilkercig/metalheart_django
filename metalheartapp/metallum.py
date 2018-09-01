import requests
import unidecode
import urllib.parse as urllibparse
from enum import Enum
from . import utility
from bs4 import BeautifulSoup


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
SEARCH_URL = 'https://www.metal-archives.com/search/ajax-advanced/searching/bands'
ALBUM_URL = 'https://www.metal-archives.com/band/discography/id/'
BAND_URL = 'http://em.wemakesites.net/band/'


# def search_band(keyword):
#     """ search for band name in metal archives api """
#     payload = {'api_key': API_KEY}
#     urlparams = urllibparse.urlencode(payload)
#     response = requests.get("%s?%s" % (SEARCH_URL + keyword, urlparams))
#     response = response.json()
#     if response['status'] == 'success' and response['code'] == 200:
#         return response
#     else:
#         return None

def search_band(keyword):
    """ search for band name in metal archives api """
    payload = {'bandName': keyword, 'exactBandMatch': '1'}
    urlparams = urllibparse.urlencode(payload)
    response = requests.get("%s?%s" % (SEARCH_URL, urlparams))
    if response.status_code == 200:
        return(parse_raw_search_results(response))
    else:
        return None


def get_band_albums(id):
    response = requests.get(ALBUM_URL + id + "/tab/main")
    if response.status_code == 200:
        return parse_raw_album_results(response.content)
    else:
        return None

def parse_raw_album_results(data):
    soup = BeautifulSoup(data)
    return [link.text for link in soup.find_all('a') if "/reviews/" not in link.get('href')]



def parse_raw_search_results(data):
    data = data.json()
    # error = data["error"]
    totalRecords = data["iTotalRecords"]
    # totalDisplayRecords = data["iTotalDisplayRecords"]
    # echo = data["sEcho"]
    result = data["aaData"]
    if totalRecords < 0:
        return None
    else:
        resultList = []
        for item in result:
            soup = BeautifulSoup(item[0])
            links = soup.findAll('a')
            link = links[0].get('href')
            name = links[0].text
            genres = item[1]
            country = item[2]
            s = link.split('/')
            resultList.append({"genres": genres, "country": country, "link": link, "id": s[len(s)-1], "name": name })

        data["aaData"] = resultList
        return data

class Album:
    """Represent a discography item """

    def __init__(self, album_id, name, album_type, year):
        self.album_id = album_id
        self.name = utility.remove_redundant_chars(name)
        self.type = album_type
        self.year = year


class Band(object):
    """Represent a band """

    def __init__(self, band_id, name, country, raw_genre, albums):
        self.band_id = band_id
        self.genres = [utility.remove_redundant_chars(item) for item in raw_genre.split(',')]
        self.country = country
        self.name = utility.remove_redundant_chars(name)
        self.discography = []
        self.discography = albums


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
        search_results = data['aaData']
        for item in search_results:
                try:
                    discography = get_band_albums(item["id"])
                    band = Band(item["id"], item["name"],item["country"], item["genres"], discography)
                    band_list.append(band)
                except KeyError as err:
                    print("KeyError for artist: %s in key: %s" % (item['name'], err.args[0]))
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
