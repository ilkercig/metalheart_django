from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^callback', views.callback, name='callback'),
    url(r'^login', views.login, name='login'),
    url(r'^logout', views.logout, name='logout'),
    url(r'^test_ArtistAlbums', views.test_ArtistAlbums, name='test_ArtistAlbums'),
    url(r'^test_UserArtists', views.test_UserArtists, name='test_UserArtists'),
    url(r'^test_UserAlbums', views.test_UserAlbums, name='test_UserAlbums'),
    url(r'^test_FindArtist', views.test_FindArtist, name='test_FindArtist'),
    url(r'^infinite', views.infinite, name='infinite')

]    