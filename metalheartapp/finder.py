from . import metallum
from . import spotify
from . import persistence
import logging
import unidecode


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
        return False





def find_and_save_artists(auth, session, s_artist_list):
    for s_artist in s_artist_list:
        if not persistence.get_artist(s_artist.artist_id):
            finder = Finder(s_artist, auth, session)
            ma_band = finder.find_artist() 
            if(ma_band is not None):
                persistence.save_artist(s_artist, ma_band)
            else:
                persistence.save_nonmetal_artist(s_artist.artist_id ,s_artist.name)





