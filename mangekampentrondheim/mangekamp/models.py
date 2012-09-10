# -*- coding: utf-8 -*-

from datetime import datetime
from itertools import chain, groupby
from collections import OrderedDict

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
        return Event.objects.filter(time__lt=datetime.today(), season=self)

    def get_future_events(self):
        return Event.objects.filter(time__gte=datetime.today(), season=self)

    def get_finished_events(self):
        return Event.objects.filter(finished=True, season=self)

    def get_activity_board(self):
        events = self.get_finished_events()
        participants = [e.participants for e in events]
        participants = list(chain(*participants))

        users = User.objects.all()
        scores = [(user, participants.count(user)) for user in users]
        scores.sort(key=lambda u: u[1], reverse=True)
        return scores
    
    def scoreboard_events(self):
        finished_events = self.get_finished_events()
        future_events = self.get_future_events()

        all_events = []
        for event in finished_events:
            all_events.append(event)

        for event in future_events:
            all_events.append(event)

        all_events.sort(key=lambda e: e.category)
        all_events = groupby(all_events, lambda e: e.category)
        sorted_events = [] 
        for key, group in all_events:
            group = list(group)
            group.sort(key=lambda e: e.name)
            sorted_events.append(group)

        return sorted_events

    def scoreboard(self):
        active_users = User.objects.filter(is_active=True)
        sorted_events = self.scoreboard_events()
        stat_dict = {}
        for user in active_users:
            stat_dict[user.username] = OrderedDict()
            stat_dict[user.username]['attendance'] = 0
            stat_dict[user.username]['categories'] = []
            stat_dict[user.username]['events'] = OrderedDict()

        for group in sorted_events:
            for event in group:
                for user in active_users:
                    stat_dict[user.username]['events'][event.name] = 0

                for score in Score.objects.filter(participation__event=event):
                    username = score.participation.participant.username
                    stat_dict[username]['events'][event.name] = score.score
                    stat_dict[username]['attendance'] += 1
                    if not event.category in stat_dict[username]['categories']:
                        stat_dict[username]['categories'].append(event.category)

        print stat_dict


        return stat_dict
        
        




class Event(models.Model):
    CATEGORY_CHOICES = (
            (1, "Teknikk"),
            (2, "Utholdenhet"),
            (3, "Ball")
        )

    name = models.CharField(max_length=50)
    description = models.TextField()
    time = models.DateTimeField()
    location = models.CharField(max_length=100)
    location_url = models.URLField(max_length=500)
    finished = models.BooleanField()
    season = models.ForeignKey(Season)
    category = models.IntegerField(choices=CATEGORY_CHOICES)

    def __unicode__(self):
        return "{0} - {1}".format(self.name, self.season)
    
    def get_scores(self):
        return Score.objects.filter(participation__event=self).order_by('-score')

    @property
    def participants(self):
        return [p.participant for p in Participation.objects.filter(event=self)]


class Participation(models.Model):
    event = models.ForeignKey(Event)
    participant = models.ForeignKey(User)

    def __unicode__(self):
        return "{0} ({1}) - {2}".format(self.event.name, self.event.season.title, self.participant)

class Score(models.Model):
    participation = models.ForeignKey(Participation)
    score = models.IntegerField()

    def __unicode__(self):
        return "{0}: {1} ({2})".format(self.participation.participant, self.score, self.participation.event)
