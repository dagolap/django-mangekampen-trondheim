from django import template
register = template.Library()

@register.filter("has_user")
def has_user(event, user):
    return user in event.participants
