from django.conf.urls import patterns, url

urlpatterns = patterns('mangekamp.views',
    url(r'^$', 'home', name='home'),
    url(r'^login/$', 'custom_login', name='login'),
    url(r'^signup/(?P<event_id>\d+)/$', 'toggle_signup', name='toggle_signup'),
    url(r'^results/(?P<event_id>\d+)/$', 'results_modal', name='results_modal'),
)
