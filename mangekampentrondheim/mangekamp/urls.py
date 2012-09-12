from django.conf.urls import patterns, url

urlpatterns = patterns('mangekamp.views',
    url(r'^$', 'home', name='home'),
    url(r'^login/$', 'custom_login', name='login'),
    url(r'^signup/(?P<event_id>\d+)/$', 'toggle_signup', name='toggle_signup'),
    url(r'^results/(?P<event_id>\d+)/$', 'results_modal', name='results_modal'),
    url(r'^activity_board/(?P<season_id>\d+)/$', 'activity_board', name='activity_board'),
    url(r'^scoreboard/(?P<season_id>\d+)/$', 'scoreboard', name='scoreboard'),
    url(r'^scoreboard/$', 'scoreboard', name='scoreboard'),
    url(r'^event_listing/(?P<season_id>\d+)/$', 'event_listing', name='event_listing'),
    url(r'^event_listing/$', 'event_listing', name='event_listing'),
    url(r'^scoreboard/excel/(?P<season_id>\d+)/$', 'scoreboard_excel', name='scoreboard_excel'),
    url(r'^events_listing/$', 'events_listing', name='events_listing'),
