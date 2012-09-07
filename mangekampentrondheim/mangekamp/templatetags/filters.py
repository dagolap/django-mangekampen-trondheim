from django import template
register = template.Library()

@register.filter("has_user")
def has_user(event, user):
    return user in [p.participant for p in event.participants]
