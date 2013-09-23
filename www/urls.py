from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()
from django.conf import settings
# from django.views.generic.simple import redirect_to
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

#TODO: ISO 8601 datetime
snippet_regex = r"(?P<organisation>[\w]+)-(?P<site_code>[\w]+)-(?P<date_time>\d+)-(?P<offset>[\d\.]+)-(?P<duration>[\d\.]+)-(?P<recorder_code>[\w]+)"

urlpatterns = patterns(
    '',
    url(r'^browserid/', include('django_browserid.urls')),
    url(r'^snippet/(?P<id>\d+)/$', 'www.recordings.views.snippet', name='snippet'),
    url(r'^snippet/%s/$' % snippet_regex, 'www.recordings.views.snippet', name='snippet_name'),
    url(r'^snippets/$', 'www.recordings.views.snippets', name='snippets_list'),
    url(r'^tags$', 'www.recordings.views.tags', name='tags'),
    url(r'^analysis/create$', 'www.recordings.views.analysis_create', name='analysis_create'),
    url(r'^analysis/$', 'www.recordings.views.analysis_list', name='analysis_list'),
    url(r'^analysis/(?P<code>[\w-]+)/detail$', 'www.recordings.views.analysis_detail', name='analysis_detail'),
    url(r'^analysis/(?P<code>[\w-]+)/(?P<snippet_id>\d+)$', 'www.recordings.views.analysis_snippet', name='analysis_snippet'),
    url(r'^analysis/(?P<code>[\w-]+)$', 'www.recordings.views.analysis', name='analysis'),
    url(r'^analysis/(?P<code>[\w-]+)/next', 'www.recordings.views.analysis_next', name='analysis_next'),
    url(r'^summary/$', 'www.recordings.views.summary', name='summary'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$',   'django.contrib.auth.views.login',    {'template_name': 'account/login.html'}),
    url(r'^logout/$',  'django.contrib.auth.views.logout',   {'next_page': '/'}),
    url(r'^accounts/change_password/$', 'django.contrib.auth.views.password_change', {'post_change_redirect': '/'}),
    url(r'^accounts/change_password/done/$', 'django.contrib.auth.views.password_change_done'),
    url(r'^$', 'www.recordings.views.home', name='home'),
    # (r'^accounts/profile/$', redirect_to, {'url': '/'}),
    #(r'^accounts/login/$', redirect_to, {'url': '/login/'}),
    url(r'^sonogram/(?P<id>\d+).png', 'www.recordings.views.get_sonogram', name='sonogram_id'),
    url(r'^sonogram/%s.png' % snippet_regex, 'www.recordings.views.get_sonogram', name='sonogram'),
    url(r'^media/sonograms/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.SONOGRAM_DIR}, name='sonogram-media'),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    url(r'^play/(?P<id>\d+).wav', 'www.recordings.views.play_snippet', name='play'),
    url(r'^play/%s.wav' % snippet_regex, 'www.recordings.views.play_snippet', name='play_name')
)
urlpatterns += staticfiles_urlpatterns()
