from django.contrib import admin

from recordings.models import Organisation, Site, Recorder, Deployment, Score


class OrganisationAdmin(admin.ModelAdmin):
    list_display = ('code', 'name',)
admin.site.register(Organisation, OrganisationAdmin)

class SiteAdmin(admin.ModelAdmin):
    list_display = ('code', 'latitude', 'longitude', 'altitude', 'description',)
admin.site.register(Site, SiteAdmin)

class RecorderAdmin(admin.ModelAdmin):
    list_display = ('code', 'organisation', 'comments',)
admin.site.register(Recorder, RecorderAdmin)

class DeploymentAdmin(admin.ModelAdmin):
    list_display = ('site', 'recorder', 'start', 'end', 'comments',)
    list_filter = ('site', 'recorder',)
admin.site.register(Deployment, DeploymentAdmin)

