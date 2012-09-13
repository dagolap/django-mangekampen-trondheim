from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin

from mangekamp.models import Season, Event, Participation, UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    max_num = 1
    can_delete = False

class UserAdmin(AuthUserAdmin):
    inlines = [UserProfileInline]

class ParticipationInline(admin.TabularInline):
    model = Participation
    can_delete = True

class EventAdmin(admin.ModelAdmin):
    inlines = [ParticipationInline]
    list_display = ('name', 'category', 'season')
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
