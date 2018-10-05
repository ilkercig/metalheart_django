from django.db import models
from rest_framework import serializers

class Genre(models.Model):
    name = models.CharField(max_length = 200, unique = True)

class Artist(models.Model):
    spotify_id = models.CharField(primary_key=True, max_length = 50)
    name = models.CharField(max_length = 200)
    metallum_id = models.IntegerField(unique=True)
    genres = models.ManyToManyField(Genre)

class NonMetalArtist(models.Model):
    spotify_id = models.CharField(primary_key=True, max_length = 50)
    name = models.CharField(max_length = 200)

class GenreSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)

class ArtistSerializer(serializers.Serializer):
    spotify_id = serializers.CharField(max_length=50)
    name = serializers.CharField(max_length=200)
    genres = GenreSerializer(many = True)
