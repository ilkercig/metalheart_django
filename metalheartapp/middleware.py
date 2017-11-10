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

def IsSessionActive(session):
    if not 'acces_token' in session:
        return False
    else:
        return True
