from django.shortcuts import render_to_response
from mangekamp.models import Season

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
 
    return render_to_response('mangekamp/index.html', context)

def event_listing(request, season):
    current_season = Season.get_current_season()
    past_events = current_season.get_past_events()
    future_events = current_season.get_future_events()

    context = {
            'future_events':future_events,
            'past_events':past_events,
            'current_season':current_season
            }
            
    
    return render_to_response('mangekamp/eventlisting.html', {'previous_events':previous_events, 'future_events':future_events})

