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

admin.site.register(Season)
admin.site.register(Event)
admin.site.register(Participation)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
