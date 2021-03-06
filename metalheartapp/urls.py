from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^callback', views.callback, name='callback'),
    url(r'^login', views.login, name='login'),
    url(r'^logout', views.logout, name='logout'),
    url(r'^api/user/artists', views.user_artist_list, name='user_artist_list'),
    url(r'^api/artists', views.artist_list, name='artist_list')
]    