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
from .models import ArtistSerializer, GenreSerializer
from rest_framework.response import Response
from rest_framework import status as RestStatus
from rest_framework.decorators import api_view
from rest_framework.renderers import JSONRenderer

import json



from django.template.response import TemplateResponse

from rest_framework.renderers import JSONRenderer

class EmberJSONRenderer(JSONRenderer):

    def render(self, data, accepted_media_type=None, renderer_context=None):
        data = {'next_offset': renderer_context["next_offset"], 'result': data }
        return super(EmberJSONRenderer, self).render(data, accepted_media_type, renderer_context)

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

@api_view(['GET'])
def artist_list(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        spotify_api = spotify.Authorization(request.session)
        offset = request.GET.get('offset', 0)
        limit = request.GET.get('limit', 30)
        artist_list, offset = artist_controller.get_user_saved_metal_artists_and_next_offset(spotify_api, limit, offset)
        content = EmberJSONRenderer().render(ArtistSerializer(artist_list, many=True).data, renderer_context= {"next_offset": offset})
        return Response(content, status = RestStatus.HTTP_200_OK)
    return Response(None, status=RestStatus.HTTP_400_BAD_REQUEST)


def infinite(request):
    spotify_api = spotify.Authorization(request.session)
    offset = request.GET.get('offset', 0)
    artist_list, offset = artist_controller.get_user_saved_metal_artists_and_next_offset(spotify_api, 30, offset)
    artists = MyPage(ArtistSerializer(artist_list, many=True).data, offset)
    return TemplateResponse(request, 'metalheartapp/infinite.html', {'artists': artists, 'genres':genre_list})


class MyPage(list):
    def __init__(self, collection, next_offset):
        list.__init__(self, collection)
        self.next_offset = next_offset
    
    def has_next(self):
        return self.next_offset is not None
