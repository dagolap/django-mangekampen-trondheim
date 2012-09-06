from django.db import models
from django.contrib.auth.models import User

class Season(models.Model):
    startDate = models.DateField()
    endDate = models.DateField()

class Event(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    time = models.DateTimeField()
    location = models.CharField(max_length=100)
    location_url = models.URLField(max_length=500)
    finished = models.BooleanField()

class Participation(models.Model):
    event = models.ForeignKey(Event)
    participant = models.ForeignKey(User)

class Score(models.Model):
    participation = models.ForeignKey(Participation)
    score = models.IntegerField()
