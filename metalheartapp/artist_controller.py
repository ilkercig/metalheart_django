from . import persistence
from . import finder


class FinderResult(object):
    def __init__(self):
        self.saved = 0
        self.saved_nonmetal = 0
        self.existing = 0
        self.existing_nonmetal = 0
        self.artist_list = []
    def add_artist(self,artist):
        self.artist_list.append(artist)

def get_user_metal_artists(spotify_api):
    artist_list = spotify_api.get_users_all_artists()
    result = FinderResult()
    for artist in artist_list:
        if persistence.filter_artist(artist.artist_id):
            result.existing += 1
            result.add_artist(persistence.get_artist(artist.artist_id))
        elif persistence.filter_nonmetal_artist(artist.artist_id):
            result.existing_nonmetal += 1
        else:
            genre_finder = finder.Finder(artist, spotify_api)
            band = genre_finder.find_artist()
            if(band is not None):
                persistence.save_artist(artist, band)
                result.saved += 1
                result.add_artist( persistence.get_artist(artist.artist_id))
            else:
                persistence.save_nonmetal_artist(artist.artist_id ,artist.name)
                result.saved_nonmetal +=1 
    return result.artist_list
            



