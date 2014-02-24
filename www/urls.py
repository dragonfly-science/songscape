import os
from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()
from django.conf import settings
# from django.views.generic.simple import redirect_to
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

snippet_regex = r"(?P<organisation>[\w]+)-(?P<site_code>[\w]+)-(?P<date_time>\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\dZ)-(?P<offset>[\d\.]+)-(?P<duration>[\d\.]+)"

urlpatterns = patterns(
    '',
    url(r'^snippet/(?P<id>\d+)/$', 'www.recordings.views.snippet', name='snippet'),
    url(r'^api/(?P<id>\d+)/(?P<action>[\w-]+)/$', 'www.recordings.views.api', name='api'),
    url(r'^snippet/%s/$' % snippet_regex, 'www.recordings.views.snippet', name='snippet_name'),
    url(r'^snippets/(?P<index>\d+)/$', 'www.recordings.views.snippets', name='snippet_list'),
    url(r'^snippets/$', 'www.recordings.views.snippets', name='first_snippet'),
    url(r'^tags$', 'www.recordings.views.tags', name='tags'),
    url(r'^analysis/create$', 'www.recordings.views.analysis_create', name='analysis_create'),
    url(r'^analysis/$', 'www.recordings.views.analysis_list', name='analysis_list'),
    url(r'^analysis/(?P<code>[\w-]+)/detail$', 'www.recordings.views.analysis_detail', name='analysis_detail'),
    url(r'^analysis/(?P<code>[\w-]+)/(?P<snippet_id>\d+)/$', 'www.recordings.views.analysis_snippet', name='analysis_snippet'),
    url(r'^analysis/(?P<code>[\w-]+)/$', 'www.recordings.views.analysis_snippet', name='analysis'),
    #url(r'^review/(?P<code>[\w-]+)$', 'www.recordings.views.review', name='analysis'),
    url(r'^analysis/(?P<code>[\w-]+)/next', 'www.recordings.views.analysis_next', name='analysis_next'),
    url(r'^summary/$', 'www.recordings.views.summary', name='summary'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$',   'django.contrib.auth.views.login',    {'template_name': 'account/login.html'}, name="login"),
    url(r'^logout/$',  'django.contrib.auth.views.logout',   {'next_page': '/'}, name="logout"),
    url(r'^accounts/change_password/$', 'django.contrib.auth.views.password_change', {'post_change_redirect': '/'}),
    url(r'^accounts/change_password/done/$', 'django.contrib.auth.views.password_change_done'),
    url(r'^$', 'www.recordings.views.home', name='home'),
    # (r'^accounts/profile/$', redirect_to, {'url': '/'}),
    #(r'^accounts/login/$', redirect_to, {'url': '/login/'}),
    url(r'^sonogram/(?P<id>\d+).jpg', 'www.recordings.views.get_sonogram', name='sonogram_id'),
    url(r'^sonogram/%s.jpg' % snippet_regex, 'www.recordings.views.get_sonogram', name='sonogram'),
    url(r'^media/sonograms/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(settings.MEDIA_ROOT, settings.SONOGRAM_DIR)}, name='sonogram-media'),
    url(r'^media/snippets/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(settings.MEDIA_ROOT, settings.SNIPPET_DIR)}, name='snippet-media'),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}, name="media"),
    url(r'^play/(?P<id>\d+).wav', 'www.recordings.views.play_snippet', name='play'),
    url(r'^play/%s.wav' % snippet_regex, 'www.recordings.views.play_snippet', name='play_name')
)
urlpatterns += staticfiles_urlpatterns()
