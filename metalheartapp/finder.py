from . import metallum
from . import spotify
from . import persistence
import logging
import unidecode
import urllib.parse as urllibparse

class FinderResult(object):
    def __init__(self):
        self.saved = 0
        self.saved_nonmetal = 0
        self.existing = 0
        self.existing_nonmetal = 0
        self.artist_list = []
    def add_artist(self,artist):
        self.artist_list.append(artist)

class Finder(object):
    """ For finding spotify artist in metal archives"""
    def __init__(self, s_artist, auth, session):
        self.s_artist = s_artist
        self.auth = auth
        self.s_discography = []
        self.session = session

    def find_artist(self):
        """Finds spotify artist in metal archives """
        ma_band_list = metallum.search_and_filter_band(
            unidecode.unidecode(self.s_artist.name.lower()))
        if not ma_band_list:
            return None
        else:
            self.s_discography = self.s_artist.get_albums(self.session, self.auth)
            if len(ma_band_list) == 1:
                if self._verify_match(ma_band_list[0]):
                    return ma_band_list[0]
            else:
                return self._compare_albums(ma_band_list)

    def _compare_albums(self, ma_band_list):
        for ma_artist in ma_band_list:
            if self._compare_discography(ma_artist.discography):
                return ma_artist
        return None

    def _compare_album_names(self, s_name, ma_name):
        return s_name.lower() == ma_name.lower()

    def _verify_match(self, ma_artist):
        return self._compare_discography(ma_artist.discography)

    def _compare_discography(self, ma_albums):
        for s_album in self.s_discography:
            for ma_album in ma_albums:
                if(self._compare_album_names(s_album.name, ma_album.name)):
                    return True        
        return self._check_next_albums(ma_albums)


    def _check_next_albums(self, ma_albums):
        """ Hardcore optimization """
        while self.s_artist.is_albums_extendable():
            next_albums = self.s_artist.next_albums(self.session, self.auth)
            for s_album in next_albums:
                for ma_album in ma_albums:
                    if(self._compare_album_names(s_album.name, ma_album.name)):
                        return True
        return False
            





def find_and_save_artists(auth, session, s_artist_list, result):
    for s_artist in s_artist_list:
        if persistence.filter_artist(s_artist.artist_id):
            result.existing += 1
            result.add_artist(persistence.get_artist(s_artist.artist_id))
        else:
            if persistence.filter_nonmetal_artist(s_artist.artist_id):
                result.existing_nonmetal += 1
            else:               
                finder = Finder(s_artist, auth, session)
                ma_band = finder.find_artist() 
                if(ma_band is not None):
                    persistence.save_artist(s_artist, ma_band)
                    result.saved += 1
                    result.add_artist( persistence.get_artist(s_artist.artist_id))
                else:
                    persistence.save_nonmetal_artist(s_artist.artist_id ,s_artist.name)
                    result.saved_nonmetal +=1 

def is_exist_in_db(s_artist):
    return persistence.filter_artist(s_artist.artist_id) or persistence.filter_nonmetal_artist(s_artist.artist_id)

def find_artists(auth, session):
    """ da """
    offset = 0
    limit = 50
    artist_list = []
    result = FinderResult()
    artist_list, next_query = auth.get_user_artists_and_next(
        session, limit, offset)
    total = len(artist_list)
    find_and_save_artists(auth, session, artist_list, result)
    print("total artist: ", total)
    while next_query is not None:
        limit, offset = parse_next_query(next_query)
        next_artists, next_query = auth.get_user_artists_and_next(
            session, int(limit), int(offset))
        find_and_save_artists(auth, session, next_artists,result)
        total += len(next_artists)
    return result



def parse_next_query(next_query):
    result = urllibparse.urlparse(next_query)
    params = urllibparse.parse_qs(result.query)
    offset, limit = params['offset'][0], params['limit'][0]
    return limit, offset
    