from . import metallum
from . import persistence
import logging
import unidecode
import urllib.parse as urllibparse



class Finder(object):
    """ For finding spotify artist in metal archives"""
    def __init__(self, s_artist, auth):
        self.s_artist = s_artist
        self.auth = auth

    def find_band(self):
        """Finds spotify artist in metal archives """
        ma_band_list = metallum.search_and_filter_band(
            unidecode.unidecode(self.s_artist.name.lower()))
        if not ma_band_list:
            return None
        else:
            if len(ma_band_list) == 1:
                if self._compare_discography(ma_band_list[0].discography):
                    return ma_band_list[0]
                else:
                    return None
            else:
                return self._find_band(ma_band_list)

    def _find_band(self, ma_band_list):
        for ma_band in ma_band_list:
            if self._compare_discography(ma_band.discography):
                return ma_band
        return None

    def _compare_album_names(self, s_name, ma_name):
        return s_name.lower() == ma_name.lower()

    def _compare_discography(self, ma_albums):
        for s_album in self.s_artist.get_discography(self.auth):
            for ma_album in ma_albums:
                if(self._compare_album_names(s_album.name, ma_album)):
                    return True        
        return self._check_next_albums(ma_albums)


    def _check_next_albums(self, ma_albums):
        """ Hardcore optimization """
        while self.s_artist.is_albums_extendable():
            next_albums = self.s_artist.next_albums(self.auth)
            for s_album in next_albums:
                for ma_album in ma_albums:
                    if(self._compare_album_names(s_album.name, ma_album)):
                        return True
        return False
            