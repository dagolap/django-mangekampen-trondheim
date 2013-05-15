from django.conf.urls import patterns, url

urlpatterns = patterns('mangekamp.views',
    url(r'^$', 'home', name='home'),
    url(r'^login/$', 'custom_login', name='login'),
    url(r'^signup/(?P<event_id>\d+)/$', 'toggle_signup', name='toggle_signup'),
    url(r'^results/(?P<event_id>\d+)/$', 'results_modal', name='results_modal'),
    url(r'^activity_board/(?P<season_id>\d+)/$', 'activity_board', name='activity_board'),
    url(r'^scoreboard/(?P<season_id>\d+)/$', 'scoreboard', name='scoreboard'),
    url(r'^scoreboard/(?P<season_id>\d+)/(?P<gender>\w+)/$', 'scoreboard', name='scoreboard'),
    url(r'^scoreboard/$', 'scoreboard', name='scoreboard'),
    url(r'^scoreboard/excel/(?P<season_id>\d+)/$', 'scoreboard_excel', name='scoreboard_excel'),
    url(r'^event/(?P<event_id>\d+)/$', 'event_details', name='event_details'),
    url(r'^events_listing/$', 'events_listing', name='events_listing'),
    url(r'^userprofile/$', 'userprofile', name='userprofile'),
    url(r'^email_event/(?P<event_id>\d+)$', 'email_event', name='email_event'),
    url(r'^ical/(?P<season_id>\d+)$', 'ical', name='ical'),
)
