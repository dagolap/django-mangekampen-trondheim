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
def scoreboard(request, season_id):
    season = get_object_or_404(Season, id=season_id)
    context = {'scores':season.get_activity_board()}
    return render(request, 'mangekamp/scoreboard.html', context)

@login_required
def event_listing(request, season):
    current_season = Season.get_current_season()
    past_events = current_season.get_past_events()
    future_events = current_season.get_future_events()

    context = {
            'future_events':future_events,
            'past_events':past_events,
            'current_season':current_season
            }
            
    
    return render(request, 'mangekamp/eventlisting.html', {'previous_events':previous_events, 'future_events':future_events})

