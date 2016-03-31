import os
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
admin.autodiscover()
from django.conf import settings
from django.views import static
# from django.views.generic.simple import redirect_to
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from www.recordings import views


snippet_regex = r"(?P<organisation>[\w]+)-(?P<site_code>[\w]+)-(?P<date_time>\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\dZ)-(?P<offset>[\d\.]+)-(?P<duration>[\d\.]+)"

urlpatterns = [
    url(r'^snippet/(?P<id>\d+)/$', views.snippet, name='snippet'),
    url(r'^api/(?P<id>\d+)/(?P<action>[\w-]+)/$', views.api, name='api'),
    url(r'^snippet/%s/$' % snippet_regex, views.snippet, name='snippet_name'),
    url(r'^snippets/(?P<index>\d+)/$', views.snippets, name='snippet_list'),
    url(r'^snippets/$', views.snippets, name='first_snippet'),
    url(r'^tags$', views.tags, name='tags'),
    url(r'^analysis/create$', views.analysis_create, name='analysis_create'),
    url(r'^analysis/$', views.analysis_list, name='analysis_list'),
    url(r'^analysis/(?P<code>[\w-]+)/detail$', views.analysis_detail, name='analysis_detail'),
    url(r'^analysis/(?P<code>[\w-]+)/(?P<snippet_id>\d+)/$', views.analysis_snippet, name='analysis_snippet'),
    url(r'^analysis/(?P<code>[\w-]+)/$', views.analysis_snippet, name='analysis'),
    #url(r'^review/(?P<code>[\w-]+)$', views.review, name='analysis'),
    url(r'^analysis/(?P<code>[\w-]+)/next', views.analysis_next, name='analysis_next'),
    url(r'^summary/$', views.summary, name='summary'),
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/login/$', auth_views.login,    {'template_name': 'account/login.html'}, name="login"),
    url(r'^logout/$', auth_views.logout,   {'next_page': '/'}, name="logout"),
    url(r'^accounts/change_password/$', auth_views.password_change, {'post_change_redirect': '/'}),
    url(r'^accounts/change_password/done/$', auth_views.password_change_done),
    url(r'^$', views.home, name='home'),
    # (r'^accounts/profile/$', redirect_to, {'url': '/'}),
    #(r'^accounts/login/$', redirect_to, {'url': '/login/'}),
    url(r'^sonogram/(?P<id>\d+).jpg', views.get_sonogram, name='sonogram_id'),
    url(r'^sonogram/%s.jpg' % snippet_regex, views.get_sonogram, name='sonogram'),
    url(r'^media/sonograms/(?P<path>.*)$', static.serve, {'document_root': os.path.join(settings.MEDIA_ROOT, settings.SONOGRAM_DIR)}, name='sonogram-media'),
    url(r'^media/snippets/(?P<path>.*)$', static.serve, {'document_root': os.path.join(settings.MEDIA_ROOT, settings.SNIPPET_DIR)}, name='snippet-media'),
    url(r'^media/(?P<path>.*)$', static.serve, {'document_root': settings.MEDIA_ROOT}, name="media"),
    url(r'^play/(?P<id>\d+).wav', views.play_snippet, name='play'),
    url(r'^play/%s.wav' % snippet_regex, views.play_snippet, name='play_name'),
]

urlpatterns += staticfiles_urlpatterns()
