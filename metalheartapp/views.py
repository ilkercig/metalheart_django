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

SPOTIFY_API = spotify.Authorization()


def index(request):
    SPOTIFY_API.set_token_with_session(request.session)
    template = loader.get_template('metalheartapp/index.html')
    context = {'acces_token': SPOTIFY_API.access_token, 'logged_in' : SPOTIFY_API.logged_in}
    return HttpResponse(template.render(context, request))

def logout(request):
     SPOTIFY_API.clear_session(request.session)
     return HttpResponseRedirect("/")


def render_error_view(request, error=None, status_code=None):
    template = loader.get_template('metalheartapp/error.html')
    context = {'error_message': error, "response_code": status_code}
    return HttpResponse(template.render(context, request))


def callback(request):
    if(request.GET.__contains__('code')):
        code = request.GET['code']
        state = request.GET['state']
        result, status_code = SPOTIFY_API.get_access_token(code, state, request.session)
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
    state = ''.join(random.choices(
        string.ascii_uppercase + string.digits, k=10))
    SPOTIFY_API.clear_session(request.session)
    SPOTIFY_API.state = state
    auth_url = SPOTIFY_API.get_authorize_url()
    return HttpResponseRedirect(auth_url)



def test_FindArtist(request):
    #TODO: Implement a test for unmatching artists
    artist_id = "6toR2I8BssfcGNJWkL2S0W"
    SPOTIFY_API.set_token_with_session(request.session)
    s_artist = SPOTIFY_API.get_artist(request.session,artist_id)
    x = finder.Finder(s_artist, SPOTIFY_API, request.session)
    ma_artist = x.find_artist()
    return HttpResponse(ma_artist.name)

def test_ArtistAlbums(request):
    artist_id = "2nJopqKVXGa0RHy0t3DypB"
    template = loader.get_template('metalheartapp/album_list.html')
    SPOTIFY_API.set_token_with_session(request.session)
    album_list = SPOTIFY_API.get_artist_all_albums(artist_id, request.session)
    context = {'album_list': album_list}
    return HttpResponse(template.render(context, request))

def test_UserArtists(request):
    template = loader.get_template('metalheartapp/artist_list.html')
    SPOTIFY_API.set_token_with_session(request.session)
    artist_list = SPOTIFY_API.get_users_all_artists(request.session)
    context = {'artist_list': artist_list}
    return HttpResponse(template.render(context, request))

def test_UserAlbums(request):
    template = loader.get_template('metalheartapp/album_list.html')
    SPOTIFY_API.set_token_with_session(request.session)
    album_list = SPOTIFY_API.get_users_all_albums(request.session)
    context = {'album_list': album_list}
    return HttpResponse(template.render(context, request))

def Check_And_Save_User_Artists(request):
    template = loader.get_template('metalheartapp/album_list.html')