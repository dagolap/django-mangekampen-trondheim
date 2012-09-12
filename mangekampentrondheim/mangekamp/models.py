# -*- coding: utf-8 -*-

from datetime import datetime
from itertools import chain, groupby
from collections import OrderedDict

from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User

from filebrowser.fields import FileBrowseField

class UserProfile(models.Model):
    GENDER_CHOICES = (
            (1, "Mann"),
            (2, "Kvinne"),
        )

    user = models.OneToOneField(User, editable=False)

    gender = models.IntegerField("kjønn", choices=GENDER_CHOICES, default=1)
    alternative_email = models.EmailField("alternativ epost", null=True)

    def is_mangekjemper(self, season_id):
        season = Season.objects.get(id=season_id)
        all_participations = Participation.objects.filter(event__season__id=season_id, participant=self.user)
        num_events = all_participations.count()
        num_categories = len(set([p.event.category for p in all_participations]))

        print num_events
        print num_categories
        return num_events >= season.required_events and num_categories >= season.required_categories

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)


class Season(models.Model):
    startDate = models.DateField("startdato")
    endDate = models.DateField("sluttdato")
    title = models.CharField("tittel", max_length=50)
    required_categories = models.IntegerField("kategorikrav", default=3)
    required_events = models.IntegerField("arrangementskrav", default=7)

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
        return Event.objects.filter(time__lt=datetime.today(), season=self).order_by("-time")

    def get_future_events(self):
        return Event.objects.filter(time__gte=datetime.today(), season=self).order_by("time")

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

    def get_user_scores(self, season_id):
        for up in UserProfile.objects.filter():
            print "{0} - {1}".format(up.user.username, up.is_mangekjemper(season_id))
        scores = {}
        participations = Participation.objects.filter(event__season__id=season_id).order_by('participant')
#        for p in participations:
#            if scores[p.participant.username]['events']:
#                scores[p.participant.username]['events'] += 1
#            else: 
#                scores[p.participant.username]['events'] = 1

        print participations

    def scoreboard(self):
        active_users = User.objects.filter(is_active=True)
        sorted_events = self.scoreboard_events()
        stat_dict = {}
        for user in active_users:
            stat_dict[user] = OrderedDict()
            stat_dict[user]['attendance'] = 0
            stat_dict[user]['categories'] = []
            stat_dict[user]['events'] = OrderedDict()

        for group in sorted_events:
            for event in group:
                for user in active_users:
                    stat_dict[user]['events'][event.name] = (0, event.category)

                # Refactor.
                for participation in Participation.objects.filter(event=event):
                    participant = participation.participant
                    stat_dict[participant]['events'][event.name] = (participation.score, event.category)
                    stat_dict[participant]['attendance'] += 1
                    if not event.category in stat_dict[participant]['categories']:
                        stat_dict[participant]['categories'].append(event.category)

        return stat_dict
        

class Event(models.Model):
    CATEGORY_CHOICES = (
            (1, "Teknikk"),
            (2, "Utholdenhet"),
            (3, "Ball")
        )

    name = models.CharField("navn", max_length=50)
    description = models.TextField("beskrivelse", null=True)
    time = models.DateTimeField("tid")
    location = models.CharField("sted", null=True, max_length=100)
    location_url = models.URLField("link til kart", null=True, max_length=500)
    finished = models.BooleanField("ferdig")
    season = models.ForeignKey(Season)
    category = models.IntegerField("kategori", choices=CATEGORY_CHOICES)
    image = FileBrowseField("bilde", max_length=200, directory="images/", extensions=[".jpg",".jpeg",".png",".gif"], blank=True, null=True)

    def __unicode__(self):
        return "{0} - {1}".format(self.name, self.season)
    
    def get_scores(self):
        return Participation.objects.filter(event=self).order_by('score')

    @property
    def participants(self):
        return [p.participant for p in Participation.objects.filter(event=self)]


class Participation(models.Model):
    event = models.ForeignKey(Event)
    participant = models.ForeignKey(User)
    score = models.IntegerField("score", null=True)

    def __unicode__(self):
        return "{0} ({1}) - {2}".format(self.event.name, self.event.season.title, self.participant)
