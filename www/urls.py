from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
admin.autodiscover()
from django.conf import settings
#from django.views.generic.simple import redirect_to
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
     url(r'^snippet/(?P<id>\d+)/$', 'www.recordings.views.snippet', name='snippet'),
     url(r'^scores/(?P<code>[\w-]+)/(?P<version>[0-9\.]+)/$', 'www.recordings.views.scores', name='scores_list'),
     url(r'^tags$', 'www.recordings.views.tags', name='tags'),
     url(r'^analysis/create$', 'www.recordings.views.analysis_create', name='analysis_create'),
    (r'^admin/', include(admin.site.urls)),
    (r'^login/$',   'django.contrib.auth.views.login',    {'template_name': 'account/login.html'}),
    (r'^logout/$',  'django.contrib.auth.views.logout',   {'next_page': '/'}),
    (r'^accounts/change_password/$',  'django.contrib.auth.views.password_change', {'post_change_redirect' : '/'}),
    (r'^accounts/change_password/done/$', 'django.contrib.auth.views.password_change_done'),
    #(r'^accounts/profile/$', redirect_to, {'url': '/'}),
    #(r'^accounts/login/$', redirect_to, {'url': '/login/'}),
    # url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root':settings.MEDIA_ROOT}),
    # url(r'^play/(?P<id>\d+).wav', 'www.recordings.views.play_snippet', name='play')
)
urlpatterns += staticfiles_urlpatterns()
