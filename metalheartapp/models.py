from django.db import models
from rest_framework import serializers

class Genre(models.Model):
    id = models.AutoField(primary_key=True)
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
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=200)

class ArtistSerializer(serializers.Serializer):
    spotify_id = serializers.CharField(max_length=50)
    name = serializers.CharField(max_length=200)
    genres = GenreSerializer(many = True)

class ArtistResultSerializer(serializers.Serializer):
    result = ArtistSerializer(many = True)
    next_offset = serializers.IntegerField()

class ArtistResult():
    def __init__(self, result, next_offset):
        self.result = result
        self.next_offset = next_offset

