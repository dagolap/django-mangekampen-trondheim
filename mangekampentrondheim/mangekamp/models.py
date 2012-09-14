# -*- coding: utf-8 -*-

import operator
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
        all_participations = Participation.objects.filter(event__season__id=season_id, participant=self.user, score__isnull=False)
        num_events = all_participations.count()
        num_categories = len(set([p.event.category for p in all_participations]))

        return num_events >= season.required_events and num_categories >= season.required_categories

    def get_score(self, season_id):
        if not self.is_mangekjemper(season_id):
            return 0;

        participations = Participation.objects.filter(event__season__id=season_id, participant=self.user, score__isnull=False).order_by('event__category', 'score')
        participations = groupby(participations, lambda p: p.event.category)
        scores_list = []
        counting_scores = []
        for key, group in participations:
            scores_list.append(list(group))
       
        flattened_scores = []
        for category in scores_list:
            counting_scores.append(category.pop(0))
            flattened_scores += category

        flattened_scores.sort(key=lambda p: p.score)
        season = Season.objects.get(id=season_id)
        counting_scores += flattened_scores[:season.required_events-len(counting_scores)]
        counting_scores = [p.score for p in counting_scores]

        return float(reduce(operator.add, counting_scores)) / len(counting_scores)

    def get_eventscores(self):
        participations = Participation.objects.filter(participant=self.user, event__season=Season.get_current_season())
        return [(p.event.name, p.score) for p in participations]


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
        return u"{0} / {1} - {2}".format(self.startDate.year, self.endDate.year, self.title)

    class Meta:
        verbose_name="sesong"
        verbose_name_plural="sesonger"

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

    def scoreboard(self):
        active_users = User.objects.filter(is_active=True)
        sorted_events = self.scoreboard_events()
        stat_dict = {}
        for user in active_users:
            stat_dict[user] = OrderedDict()
            stat_dict[user]['attendance'] = 0
            stat_dict[user]['categories'] = []
            stat_dict[user]['events'] = OrderedDict()
            stat_dict[user]['score'] = user.userprofile.get_score(self.id)

        for group in sorted_events:
            for event in group:
                for user in active_users:
                    stat_dict[user]['events'][event.name] = (0, event.category)

                # TODO: Refactor.
                for participation in Participation.objects.filter(event=event, score__isnull=False):
                    participant = participation.participant
                    stat_dict[participant]['events'][event.name] = (participation.score, event.category)
                    stat_dict[participant]['attendance'] += 1
                    if not event.category in stat_dict[participant]['categories']:
                        stat_dict[participant]['categories'].append(event.category)

        mangekjemper_list = []
        lazy_people_list = []
        for user in stat_dict.keys():
            if stat_dict[user]['score'] == 0:
                lazy_people_list.append((user, stat_dict[user]))
            else:
                mangekjemper_list.append((user, stat_dict[user]))

        mangekjemper_list.sort(key=lambda t: t[1]['score'], reverse=False)
        lazy_people_list.sort(key=lambda t: len(t[1]['categories']), reverse=True)
        lazy_people_list = groupby(lazy_people_list, lambda t: len(t[1]['categories']))
        lazy_people_list_2 = []
        for key, group in lazy_people_list:
            sorted_group = sorted(list(group), key=lambda t: t[1]['attendance'], reverse=True)
            lazy_people_list_2.extend(sorted_group)

        #TODO: FIX ALL THE THINGS
        return (mangekjemper_list, lazy_people_list_2)

        

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
    season = models.ForeignKey(Season, verbose_name="sesong")
    category = models.IntegerField("kategori", choices=CATEGORY_CHOICES)
    image = FileBrowseField("bilde", max_length=200, directory="images/", extensions=[".jpg",".jpeg",".png",".gif"], blank=True, null=True)

    def __unicode__(self):
        return u"{0} - {1}".format(self.name, self.season)

    class Meta:
        verbose_name="arrangement"
        verbose_name_plural="arrangement"
    
    def get_scores(self):
        return Participation.objects.filter(event=self).order_by('score')

    @property
    def participants(self):
        return [p.participant for p in Participation.objects.filter(event=self)]


class Participation(models.Model):
    event = models.ForeignKey(Event, verbose_name="arrangement")
    participant = models.ForeignKey(User, verbose_name="deltaker")
    score = models.IntegerField("score", null=True)

    def __unicode__(self):
        return u"{0} ({1}) - {2}({3})".format(self.event.name, self.event.season.title, self.participant, self.score)

    class Meta:
        verbose_name="påmelding"
        verbose_name_plural="påmeldinger"
