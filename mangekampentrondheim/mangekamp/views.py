# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.utils.html import mark_safe

import vobject
import datetime

from mangekamp.models import Season, Event, Participation
from mangekamp.forms import UserProfileForm, EmailEventForm

@login_required
def home(request):
    current_season = Season.get_current_season()
    future_events = []
    past_events = []

    if current_season:
        future_events = current_season.get_future_events()
        past_events = current_season.get_past_events()

    if len(future_events) > 3:
        future_events = future_events[:3]
    
    if len(past_events) > 3:
        past_events = past_events[:3]

    context = {
            'future_events':future_events,
            'past_events':past_events,
            'current_season':current_season
            }
 
    if not request.user.first_name or not request.user.last_name:
        messages.add_message(request, messages.WARNING, mark_safe(u'Det ser ikke ut at til du har fyllt ut profilen din. <a href="{0}">Endre i min profil</a>'.format(reverse('userprofile'))))
    return render(request, 'mangekamp/index.html', context)

@csrf_protect
def custom_login(request):
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(request.POST.get('next'))
        return render(request, 'mangekamp/login.html', {'next':request.POST.get('next')})
    else:
        c = {'next':request.GET.get('next')}
        return render(request, 'mangekamp/login.html', c)

@login_required
def toggle_signup(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    participation = Participation.objects.select_related().filter(event=event, participant=request.user)
    if participation:
        try:
            for p in participation:
                p.delete()
            return HttpResponse(u'{0}"event_name":"{1}", "signed_up":{2} {3}'.format("{", event.name, "false", "}"))
        except:
            # TODO: Error message
            return HttpResponse(u'{0}"event_name":"{1}", "signed_up":{2} {3}'.format("{", event.name, "true", "}"))
    else:
        try:
            participation = Participation(event=event, participant=request.user)
            participation.save()
            return HttpResponse(u'{0}"event_name":"{1}", "signed_up":{2} {3}'.format("{", event.name, "true", "}"))
        except:
            # TODO: Error message
            return HttpResponse(u'{0}"event_name":"{1}", "signed_up":{2} {3}'.format("{", event.name, "false", "}"))

@login_required
def results_modal(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    scores = event.get_scores()
    
    context = {'scores':scores, 'event_name':event.name}
    return render(request, 'mangekamp/results_modal.html', context)

@login_required
def activity_board(request, season_id):
    season = get_object_or_404(Season, id=season_id)
    activity = season.get_activity_board()
    if len(activity) > 2:
        activity = activity[:2]

    context = {'scores':activity, 'season_id':season.id}
    return render(request, 'mangekamp/activity_board.html', context)

@login_required
def scoreboard(request, season_id=None, gender="all"):
    context = {}
    if season_id:
        context['season'] = season = get_object_or_404(Season, id=season_id)
    else:
        context['season'] = season = Season.get_current_season()

    if gender=="male":
        gender = 1
    elif gender=="female":
        gender = 2
    else:
        gender == "all"

    all_users = season.scoreboard(gender) if season else None
    context['users'] = all_users[0] if all_users else None
    context['lazy_users'] = all_users[1] if all_users else None

    flattened_events = []
    if season:
        grouped_events = season.scoreboard_events()
        for group in grouped_events:
            for event in group:
                flattened_events.append(event)
    context['events'] = flattened_events

    return render(request, 'mangekamp/full_scoreboard.html', context)


@login_required
def scoreboard_excel(request, season_id):
    import xlwt
    if season_id:
        season = get_object_or_404(Season, id=season_id)
    else:
        season = Season.get_current_season()
    scoreboard = season.scoreboard("all")

    response = HttpResponse(mimetype="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=scoreboard.xls'
    
    doc = xlwt.Workbook()
    sheet = doc.add_sheet('Alle')

    # Write event headers
    grouped_events = season.scoreboard_events()
    flattened_events = []
    for group in grouped_events:
        for event in group:
            flattened_events.append(event)

    champs = scoreboard[0]
    non_champs = scoreboard[1]
    # Set up background color styles
    styles = {1: xlwt.easyxf(
        "pattern:fore_colour 2, pattern solid;"
            ), 
        2: xlwt.easyxf(
        "pattern:fore_colour 3, pattern solid;"
            ),
        3:xlwt.easyxf(
        "pattern:fore_colour 4, pattern solid;"
            ),
        'overskrift':xlwt.easyxf(
        "font:bold True; font:height 280;" 
            ),
        'header':xlwt.easyxf(
        "font:bold True;" 
            ),}
    # Write headers
    sheet.write(0, 0, "Bruker", styles['header'])
    sheet.col(0).width = 6666
    sheet.write(0, 1, "Snittscore", styles['header'])
    sheet.col(1).width = 3000
    sheet.write(0, 2, "Kategorier", styles['header'])
    sheet.col(2).width = 3000
    sheet.write(0, 3, "Arrangement", styles['header'])
    sheet.col(3).width = 4000
    for column, event in enumerate(flattened_events, start=4):
        sheet.write(0, column, event.name, styles['header'])
        sheet.col(column).width = 4000

    # Handle champions
    sheet.write(1, 0, "Mangekjempere", styles['overskrift'])
    i = 2
    for i, champ in enumerate(champs, start=2):
        sheet.write(i, 0, champ[0].get_full_name())
        sheet.write(i, 1, champ[1]['score'])
        sheet.write(i, 2, len(champ[1]['categories']))
        sheet.write(i, 3, champ[1]['attendance'])
        for column, event in enumerate(champ[1]['events'], start=4):
            sheet.write(i, column, champ[1]['events'][event][0], styles[champ[1]['events'][event][1]])

    # Handle non-champions
    sheet.write(i+1, 0, "Resten av deltakerne", styles['overskrift'])
    for i, champ in enumerate(non_champs, start=i+2):
        sheet.write(i, 0, champ[0].get_full_name())
        sheet.write(i, 1, "N/A")
        sheet.write(i, 2, len(champ[1]['categories']))
        sheet.write(i, 3, champ[1]['attendance'])
        for column, event in enumerate(champ[1]['events'], start=4):
            sheet.write(i, column, champ[1]['events'][event][0], styles[champ[1]['events'][event][1]])


    doc.save(response)
    return response


@login_required
def events_listing(request, season_id=None):
    if season_id:
        current_season = get_object_or_404(Season, id=season_id)
    else:
        current_season = Season.get_current_season()

    past_events = current_season.get_past_events() if current_season else []
    future_events = current_season.get_future_events() if current_season else []
    context = {'past_events':past_events,
               'future_events':future_events
              }
    return render(request, 'mangekamp/events_listing.html', context)  

@login_required
def userprofile(request):
    context =  {}
    context['events'] = request.user.userprofile.get_eventscores()
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user.userprofile)
        context['form'] = form
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "Din brukerprofil er oppdatert")
        return render(request, 'mangekamp/userprofile.html', context)
    else:
        context['form'] = UserProfileForm(instance=request.user.userprofile)
        return render(request, 'mangekamp/userprofile.html', context)

@login_required
def email_event(request, event_id):
    context = {}

    if request.method == 'POST':
        form = EmailEventForm(request.POST)
        if form.is_valid():
            # TODO: Send to everyone
            emails = [p.participant.userprofile.get_email() for p in Participation.objects.select_related().filter(event__id=event_id)]
            print emails
            send_mail(form.cleaned_data['title'], form.cleaned_data['body'], 'Mangekampen <Capgemini.Trondheim.MK@gmail.com>', emails, fail_silently=False) 
            messages.add_message(request, messages.SUCCESS, 'Epost ble sendt.')
            # TODO: Better redirect
            return HttpResponseRedirect(reverse('admin:index'))
        else: 
            context['form'] = form
            return render(request, 'mangekamp/event_emailform.html',  context)
    else:
        form = EmailEventForm()
        context['form'] = form
        return render(request, 'mangekamp/event_emailform.html', context)

@login_required
def ical(request, season_id=None):
    cal = vobject.iCalendar()
    cal.add('method').value = 'PUBLISH'  # IE/Outlook needs this
    if not season_id:
        season = Season.get_current_season()
    else:
        season = Season.objects.get(id=season_id)

    for event in season.get_future_events():
        vevent = cal.add('vevent')
        vevent.add('dtstart').value = event.time
        vevent.add('dtend').value = event.time + datetime.timedelta(hours=2)
        vevent.add('summary').value = event.name
        vevent.add('location').value = event.location
        vevent.add('description').value = event.description
    icalstream = cal.serialize()
    response = HttpResponse(icalstream, mimetype='text/calendar')
    response['Filename'] = 'mangekampen.ics'  # IE needs this
    response['Content-Disposition'] = 'attachment; filename=filename.ics'
    return response
