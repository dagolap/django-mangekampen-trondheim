from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from filebrowser.sites import site

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mangekampentrondheim.views.home', name='home'),
    # url(r'^mangekampentrondheim/', include('mangekampentrondheim.foo.urls')),
    url(r'^', include('mangekamp.urls')),
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/filebrowser/', include(site.urls)),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('registration.urls')),
)


if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()

    urlpatterns += patterns('',
            url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
                'document_root': settings.MEDIA_ROOT,
                'show_indexes': True
                })
            )
