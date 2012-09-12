# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import authenticate, login

from mangekamp.models import Season, Event, Participation

@login_required
def home(request):
    current_season = Season.get_current_season()
    future_events = []
    previous_events = []

    if current_season:
        future_events = current_season.get_future_events()
        past_events = current_season.get_past_events()

    current_season.scoreboard()

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
            return HttpResponse('{0}"event_name":"{1}", "signed_up":{2} {3}'.format("{", event.name, "false", "}"))
        except:
            # TODO: Error message
            return HttpResponse('{0}"event_name":"{1}", "signed_up":{2} {3}'.format("{", event.name, "true", "}"))
    else:
        try:
            participation = Participation(event=event, participant=request.user)
            participation.save()
            return HttpResponse('{0}"event_name":"{1}", "signed_up":{2} {3}'.format("{", event.name, "true", "}"))
        except:
            # TODO: Error message
            return HttpResponse('{0}"event_name":"{1}", "signed_up":{2} {3}'.format("{", event.name, "false", "}"))

@login_required
def results_modal(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    scores = event.get_scores()
    
    context = {'scores':scores}
    return render(request, 'mangekamp/results_modal.html', context)

@login_required
def activity_board(request, season_id):
    season = get_object_or_404(Season, id=season_id)
    context = {'scores':season.get_activity_board(), 'season_id':season.id}
    return render(request, 'mangekamp/activity_board.html', context)

@login_required
def scoreboard(request, season_id=None):
    if season_id:
        season = get_object_or_404(Season, id=season_id)
    else:
        season = Season.get_current_season()
    context = {}

    context['users'] = season.scoreboard()
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
    current_season = Season.get_current_season()
    scoreboard = current_season.scoreboard()
    print scoreboard

    response = HttpResponse(mimetype="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=scoreboard.xls'
    
    doc = xlwt.Workbook()
    sheet = doc.add_sheet('Alle')
    sheet.write(0,0,'test test test')
    
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
