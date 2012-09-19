from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from registration.views import register as registration_register
from filebrowser.sites import site

from mangekamp.forms import MangekampRegistrationForm

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^', include('mangekamp.urls')),
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/filebrowser/', include(site.urls)),


    # TODO: Admin site
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    # Django-registration app, with custom form for signup
    url(r'^accounts/register/', registration_register, 
        {
            'backend':'registration.backends.default.DefaultBackend',
            'form_class':MangekampRegistrationForm
        },
        name='registration_register'),
    url(r'^accounts/', include('registration.urls')),
)

# Custom static media serving when running in debug mode
#if settings.DEBUG:
# We self-host static-files no matter what
urlpatterns += staticfiles_urlpatterns()

urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
            'show_indexes': True
            })
        )
