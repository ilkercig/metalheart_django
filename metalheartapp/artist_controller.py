from . import persistence
from . import finder
from . import spotify
import urllib.parse as urllibparse


class FinderResult(object):
    def __init__(self):
        self.saved = 0
        self.saved_nonmetal = 0
        self.existing = 0
        self.existing_nonmetal = 0
        self.artist_list = []
        self.genre_list = []
    def add_artist(self,artist):
        self.artist_list.append(artist)
    def add_genre(self, genres):
        self.genre_list.extend([genre for genre in genres.all() if genre not in self.genre_list])

def get_user_saved_metal_artists_and_next_offset(spotify_api, limit , offset):
    artist_list, next_offset = spotify_api.get_user_saved_artists_and_next_offset(limit, offset)
    result = FinderResult()
    for artist in artist_list:
        if persistence.filter_artist(artist.artist_id):
            result.existing += 1
            artist_result = persistence.get_artist(artist.artist_id)
            result.add_artist(artist_result)
            result.add_genre(artist_result.genres)
        elif persistence.filter_nonmetal_artist(artist.artist_id):
            result.existing_nonmetal += 1
        else:
            genre_finder = finder.Finder(artist, spotify_api)
            band = genre_finder.find_band()
            if(band is not None):
                persistence.save_artist(artist, band)
                result.saved += 1
                artist_result = persistence.get_artist(artist.artist_id)
                result.add_artist(artist_result)
                result.add_genre(artist_result.genres)            
            else:
                persistence.save_nonmetal_artist(artist.artist_id ,artist.name)
                result.saved_nonmetal +=1 
    return result.artist_list, result.genre_list, next_offset


def get_all_genres():
    return persistence.get_all_genres()