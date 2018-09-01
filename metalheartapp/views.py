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

from . import metal_archives
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

def init(request):
    result = {}
    spotify_api = spotify.Authorization(request.session)
    artist_list = spotify_api.get_users_all_artists()
    finder.find_and_save_artists(spotify_api, artist_list, result )



def test_FindArtist(request):
    #TODO: Implement a test for unmatching artists
    artist_id = "6toR2I8BssfcGNJWkL2S0W"
    spotify_api = spotify.Authorization(request.session)
    s_artist = spotify_api.get_artist(artist_id)
    x = finder.Finder(s_artist, spotify_api)
    ma_artist = x.find_artist()
    return HttpResponse(ma_artist.name)

def test_ArtistAlbums(request):
    data = metal_archives.make_search_request('hammer')
    
    # artist_id = "2nJopqKVXGa0RHy0t3DypB"
    # template = loader.get_template('metalheartapp/album_list.html')
    # album_list = SPOTIFY_API.get_artist_all_albums(artist_id, request.session)
    # context = {'album_list': album_list}
    # return HttpResponse(template.render(context, request))

def test_UserArtists(request):
    spotify_api = spotify.Authorization(request.session)
    result = artist_controller.get_user_metal_artists(spotify_api)
    return TemplateResponse(request, 'metalheartapp/artist_list.html', {'artist_list': result})

def test_UserAlbums(request):
    template = loader.get_template('metalheartapp/album_list.html')
    spotify_api = spotify.Authorization(request.session)
    album_list = spotify_api.get_users_all_albums(request.session)
    context = {'album_list': album_list}
    return HttpResponse(template.render(context, request))

def Check_And_Save_User_Artists(request):
    template = loader.get_template('metalheartapp/album_list.html')