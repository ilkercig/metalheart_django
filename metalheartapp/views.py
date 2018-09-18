import random
import string
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.utils.decorators import decorator_from_middleware
from .middleware import SpotifySessionMiddleware
from django.template import loader
from . import spotify
from . import finder
from . import artist_controller

from django.template.response import TemplateResponse

AUTH_STATE = ""

def index(request):
    return TemplateResponse(request, 'metalheartapp/index.html', {})

def logout(request):
    del request.session['access_token']
    del request.session['refresh_token']
    del request.session['token_type']
    del request.session['expire_time']
    return HttpResponseRedirect("/")


def render_error_view(request, error=None, status_code=None):
    template = loader.get_template('metalheartapp/error.html')
    context = {'error_message': error, "response_code": status_code}
    return HttpResponse(template.render(context, request))


def callback(request):
    if(request.GET.__contains__('code')):
        code = request.GET['code']
        state = request.GET['state']
        if(AUTH_STATE != state):
            return render_error_view(request, "TODO: put error message", 500)
        spotify_api = spotify.Authorization(request.session)
        result, status_code = spotify_api.get_access_token(code, state)
        if result:
            if 'callback_url' in request.session:
                return HttpResponseRedirect(request.session['callback_url'])
            else:
                return HttpResponseRedirect("/")
        else:
            return render_error_view(request, status_code=status_code)
    else:
        error_msg = request.GET['error']
        return render_error_view(request, error_msg, status_code)


def login(request):
    global AUTH_STATE
    AUTH_STATE = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    auth_url = spotify.get_authorize_url(AUTH_STATE, True)
    return HttpResponseRedirect(auth_url)


def test_FindArtist(request):
    #TODO: Implement a test for unmatching artists
    artist_id = "6toR2I8BssfcGNJWkL2S0W"
    spotify_api = spotify.Authorization(request.session)
    s_artist = spotify_api.get_artist(artist_id)
    x = finder.Finder(s_artist, spotify_api)
    ma_artist = x.find_band()
    return HttpResponse(ma_artist.name)

def test_ArtistAlbums(request):
    spotify_api = spotify.Authorization(request.session)
    album_list = spotify_api.get_artist_all_discography("74ASZWbe4lXaubB36ztrGX")
    return TemplateResponse(request, 'metalheartapp/album_list.html', {'album_list': album_list})


def test_UserArtists(request):
    spotify_api = spotify.Authorization(request.session)
    result = spotify_api.get_users_all_saved_artists()
    genres = artist_controller.get_all_genres()
    return TemplateResponse(request, 'metalheartapp/artist_list.html', {'artist_list': result, "genre_list": genres})

def test_UserAlbums(request):
    spotify_api = spotify.Authorization(request.session)
    result = spotify_api.get_users_all_saved_albums()
    return TemplateResponse(request, 'metalheartapp/album_list.html', {'album_list': result})

def infinite(request):
    spotify_api = spotify.Authorization(request.session)
    offset = request.GET.get('offset', 0)
    artist_list, offset = artist_controller.get_user_saved_metal_artists_and_next_offset(spotify_api, 30, offset)
    artists = MyPage(artist_list, offset)
    return TemplateResponse(request, 'metalheartapp/infinite.html', {'artists': artists})


class MyPage(list):
    def __init__(self, collection, next_offset):
        list.__init__(self, collection)
        self.next_offset = next_offset
    
    def has_next(self):
        return self.next_offset is not None
