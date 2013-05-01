from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
admin.autodiscover()
from django.conf import settings
from django.views.generic.simple import redirect_to
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
     url(r'^score/$', 'www.recordings.views.scores', name='score'),
     url(r'^list/$', 'www.recordings.views.scores_list', name='score_list'),
    (r'^admin/', include(admin.site.urls)),
    (r'^login/$',   'django.contrib.auth.views.login',    {'template_name': 'account/login.html'}),
    (r'^logout/$',  'django.contrib.auth.views.logout',   {'next_page': '/'}),
    (r'^accounts/change_password/$',  'django.contrib.auth.views.password_change', {'post_change_redirect' : '/'}),
    (r'^accounts/change_password/done/$', 'django.contrib.auth.views.password_change_done'),
    (r'^accounts/profile/$', redirect_to, {'url': '/'}),
    (r'^accounts/login/$', redirect_to, {'url': '/login/'}),
    #url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root':settings.STATIC_ROOT}),
)
urlpatterns += staticfiles_urlpatterns()
