from datetime import datetime

from django.db import models
from django.contrib.auth.models import User

class Season(models.Model):
    startDate = models.DateField()
    endDate = models.DateField()
    title = models.CharField(max_length=50)

    def __unicode__(self):
        return "{0} / {1} - {2}".format(self.startDate.year, self.endDate.year, self.title)

    @staticmethod
    def get_current_season():
        active_seasons = Season.objects.filter(startDate__lte=datetime.today(), endDate__gte=datetime.today())
        if active_seasons:
            return active_seasons[0]
        else:
            pass

    def get_past_events(self):
        return Event.objects.filter(time__lt=datetime.today())

    def get_future_events(self):
        return Event.objects.filter(time__gte=datetime.today())



class Event(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    time = models.DateTimeField()
    location = models.CharField(max_length=100)
    location_url = models.URLField(max_length=500)
    finished = models.BooleanField()
    season = models.ForeignKey(Season)

class Participation(models.Model):
    event = models.ForeignKey(Event)
    participant = models.ForeignKey(User)

class Score(models.Model):
    participation = models.ForeignKey(Participation)
    score = models.IntegerField()
