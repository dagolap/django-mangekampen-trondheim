# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse

from mangekamp.models import Season, Event, Participation, UserProfile

class NiceUserModelAdmin(admin.ModelAdmin):
    """
    In addition to showing a user's username in related fields, show their full
    name too (if they have one and it differs from the username).
    """
    always_show_username = True

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        field = super(NiceUserModelAdmin, self).formfield_for_foreignkey(
                                                db_field, request, **kwargs)
        if db_field.rel.to == User:
            field.label_from_instance = self.get_user_label
        return field

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        field = super(NiceUserModelAdmin, self).formfield_for_manytomany(
                                                db_field, request, **kwargs)
        if db_field.rel.to == User:
            field.label_from_instance = self.get_user_label
        return field

    def get_user_label(self, user):
        name = user.get_full_name()
        username = user.username
        if not self.always_show_username:
            return name or username
        return (name and name != username and '%s (%s)' % (name, username)
                or username)

class NiceUserModelInlineAdmin(admin.TabularInline):
    """
    In addition to showing a user's username in related fields, show their full
    name too (if they have one and it differs from the username).
    """
    always_show_username = True

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        field = super(NiceUserModelInlineAdmin, self).formfield_for_foreignkey(
                                                db_field, request, **kwargs)
        if db_field.rel.to == User:
            field.label_from_instance = self.get_user_label
        return field

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        field = super(NiceUserModelInlineAdmin, self).formfield_for_manytomany(
                                                db_field, request, **kwargs)
        if db_field.rel.to == User:
            field.label_from_instance = self.get_user_label
        return field

    def get_user_label(self, user):
        name = user.get_full_name()
        username = user.username
        if not self.always_show_username:
            return name or username
        return (name and name != username and '%s (%s)' % (name, username)
                or username)        

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    max_num = 1
    can_delete = False

class UserAdmin(AuthUserAdmin):
    inlines = [UserProfileInline]

class ParticipationInline(NiceUserModelInlineAdmin):
    model = Participation
    can_delete = True

class EventAdmin(NiceUserModelAdmin):
    inlines = [ParticipationInline]
    list_display = ('name', 'category', 'season', )
    list_filter = ('category', 'season')

class EventInline(admin.TabularInline):
    model = Event
    can_delete = True
    fields = ('name', 'time', 'category')
    readonly_fields = ('name', 'time', 'category')

    def has_add_permission(self, request):
        return False


class SeasonAdmin(admin.ModelAdmin):
    inlines = [EventInline]
    list_display = ('title', 'startDate', 'endDate', 'required_categories', 'required_events')

admin.site.register(Season, SeasonAdmin)
admin.site.register(Event, EventAdmin)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
