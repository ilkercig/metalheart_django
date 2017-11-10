from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^callback', views.callback, name='callback'),
    url(r'^login', views.login, name='login'),
    url(r'^artistlist', views.artist_list, name='artist_list'),
    url(r'^albumlist', views.album_list, name='album_list'),
    url(r'^change_thisname', views.change_thisname, name='change_thisname'),
    url(r'^match_test', views.match_test, name='match_test')
]    