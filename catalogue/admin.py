from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from catalogue.forms import MeetingForm
from catalogue.models import Meeting, Place, Director, Author, Artist
from swingtime.models import EventType
from swingtime.models import Note


class EventTypeAdmin(TreeAdmin):
    form = movenodeform_factory(EventType)


admin.site.register(EventType, EventTypeAdmin)


class EventNoteInline(GenericTabularInline):
    model = Note
    extra = 1


class MeetingAdmin(admin.ModelAdmin):
    form = MeetingForm
    inlines = [EventNoteInline]


class PlaceAdmin(admin.ModelAdmin):
    pass


class DirectorAdmin(admin.ModelAdmin):
    pass


class AuthorAdmin(admin.ModelAdmin):
    pass


class ArtistAdmin(admin.ModelAdmin):
    pass


# Register the new Group ModelAdmin.
admin.site.register(Meeting, MeetingAdmin)
admin.site.register(Place, PlaceAdmin)
admin.site.register(Director, DirectorAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Artist, ArtistAdmin)
