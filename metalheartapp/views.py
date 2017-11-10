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
    SPOTIFY_API.init_with_session(request.session)
    template = loader.get_template('metalheartapp/index.html')
    if SPOTIFY_API.logged_in:
        context = {'acces_token': SPOTIFY_API.access_token}
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponse(template.render())


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


def album_list(request):
    SPOTIFY_API.init_with_session(request.session)
    template = loader.get_template('metalheartapp/album_list.html')
    album_list = SPOTIFY_API.get_user_albums(request.session, 10)
    context = {'album_list': album_list}
    return HttpResponse(template.render(context, request))


def artist_list(request):
    SPOTIFY_API.init_with_session(request.session)
    template = loader.get_template('metalheartapp/artist_list.html')
    artist_list = SPOTIFY_API.get_users_all_artists(request.session)
    context = {'artist_list': artist_list}
    return HttpResponse(template.render(context, request))


def change_thisname(request):
    SPOTIFY_API.init_with_session(request.session)
    template = loader.get_template('metalheartapp/change_thisname.html')
    artist_list = SPOTIFY_API.get_users_all_artists(request.session)
    finder.find_and_save_artists(SPOTIFY_API, request.session, artist_list)
    context = {'artist': 's'}
    return HttpResponse(template.render(context, request))


def match_test(request):
    #TODO: Implement a test for unmatching artists
    artist_id = "6toR2I8BssfcGNJWkL2S0W"
    SPOTIFY_API.init_with_session(request.session)
    s_artist = SPOTIFY_API.get_artist(request.session,artist_id)
    x = finder.Finder(s_artist, SPOTIFY_API, request.session)
    ma_artist = x.find_artist()
    return HttpResponse(ma_artist.name)
