from django.http import HttpResponse
from django.http import HttpResponseRedirect

class SpotifySessionMiddleware(object):
    def __init__(self, get_response = None):
        self.get_response = get_response
        self.restricted_views = ["index", "login","callback" ]

    def __call__(self, request):
        return self.get_response(request)
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        if not view_func.__name__ in self.restricted_views:
            if IsSessionActive(request.session):
                pass
            else:
                request.session['callback_url'] = request.path
                return HttpResponseRedirect("/login")

    def process_template_response(self, request, response):
        if IsSessionActive(request.session):
            response.context_data['acces_token'] = request.session["acces_token"]
            response.context_data['logged_in'] = True
        return response


def IsSessionActive(session):
    if 'acces_token' in session and session["acces_token"] is not None:
        return True
    else:
        return False
