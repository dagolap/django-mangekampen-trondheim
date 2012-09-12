from django import template
register = template.Library()

@register.filter("has_user")
def has_user(event, user):
    return user in event.participants

@register.filter("to_mangekjemper_status")
def to_mangekjemper_status(season, values):
    required_events = season.required_events
    required_categories = season.required_categories
    future_events = season.get_future_events()
    future_categories = set([e.category for e in future_events])
    for c in values['categories']:
        if c not in future_categories:
            future_categories.add(c)

    if values['attendance'] >= required_events and values['categories'] >= required_categories:
        return '<img src="/static/img/mangekjemper_done.png" style="width:50px; height:50px;"></img>'
    if values['attendance'] + len(future_events) >= required_events and len(future_categories) >= required_categories:
        return '<img src="/static/img/mangekjemper_yes.png" style="width:50px; height:50px;"></img>'
    else:
        return '<img src="/static/img/mangekjemper_no.png" style="width:50px; height:50px;"></img>'

@register.filter("category_to_style")
def category_to_style(category):
    if category == 1: return "background-color:#FF668C;"
    if category == 2: return "background-color:#C6FFB3;"
    if category == 3: return "background-color:#809FFF;"
    return ""
