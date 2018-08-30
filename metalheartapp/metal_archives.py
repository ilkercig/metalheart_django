import requests
import urllib.parse as urllibparse
from .metallum import Band
from bs4 import BeautifulSoup



BAND_SEARCH_URL = "https://www.metal-archives.com/search/ajax-advanced/searching/bands"

def make_search_request(keyword):
    payload = {'bandName': keyword, 'exactBandMatch': '1'}
    urlparams = urllibparse.urlencode(payload)
    response = requests.get("%s?%s" % (BAND_SEARCH_URL, urlparams))
    if response.status_code == 200:
        return response
    else:
        return None

def parse_raw_search_results(data):
    data = data.json()
    # error = data["error"]
    totalRecords = data["iTotalRecords"]
    # totalDisplayRecords = data["iTotalDisplayRecords"]
    # echo = data["sEcho"]
    result = data["aaData"]
    if totalRecords < 0:
        return None
    elif totalRecords == 1:
        soup = BeautifulSoup(result[0][0])
        for link in soup.findAll('a'):
            return link.get('href')
    else:
        return None

def create_band(band_url):
    """Get band data from metal archives and create Band object """
    band = None
    response = requests.get(band_url)
    if response.status_code == 200:
        print(response.content)
    return band

