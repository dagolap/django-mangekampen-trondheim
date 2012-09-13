# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import authenticate, login
from django.contrib import messages


from mangekamp.models import Season, Event, Participation
from mangekamp.forms import UserProfileForm

@login_required
def home(request):
    current_season = Season.get_current_season()
    future_events = []
    previous_events = []

    if current_season:
        future_events = current_season.get_future_events()
        past_events = current_season.get_past_events()

    if len(future_events) > 3:
        future_events = future_events[:3]
    
    if len(past_events) > 3:
        past_events = past_events[:3]

    current_season.get_user_scores(current_season.id)
    request.user.userprofile.get_score(current_season.id)

    context = {
            'future_events':future_events,
            'past_events':past_events,
            'current_season':current_season
            }
 
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
    participation = Participation.objects.filter(event=event, participant=request.user)
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
def scoreboard(request, season_id=None):
    if season_id:
        season = get_object_or_404(Season, id=season_id)
    else:
        season = Season.get_current_season()
    context = {}

    all_users = season.scoreboard()
    context['users'] = all_users[0]
    context['lazy_users'] = all_users[1]
    context['season'] = season
    grouped_events = season.scoreboard_events()
    flattened_events = []
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
    scoreboard = season.scoreboard()

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

    current_season = Season.get_current_season()
    past_events = current_season.get_past_events()
    future_events = current_season.get_future_events()
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
