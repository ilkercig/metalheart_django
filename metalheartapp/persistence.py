from .models import Artist, Genre, NonMetalArtist
from django.db import IntegrityError, transaction
import logging

def save_artist(s_artist, ma_band):
    try:
        with transaction.atomic():        
            artist = Artist(spotify_id = s_artist.artist_id, name = ma_band.name,
            metallum_id = ma_band.band_id)
            artist.save()
            for item in ma_band.genres :
                if not Genre.objects.filter(name = item) :
                    genre = Genre(name = item)
                    genre.save()
                else:
                    genre = Genre.objects.get(name = item)
                artist.genres.add(genre)
    except IntegrityError as err:
        logging.exception("DB error saving %s" % s_artist.name )


def save_nonmetal_artist(spotify_id, name):
    nonmetal_artist = NonMetalArtist(spotify_id = spotify_id, name = name)
    nonmetal_artist.save()


def get_all_artist():
    return Artist.objects.all()

def get_artist(spotify_id):
    return Artist.objects.filter(spotify_id = spotify_id)

    