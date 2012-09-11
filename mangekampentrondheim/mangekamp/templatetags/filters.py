from django import template
register = template.Library()

@register.filter("has_user")
def has_user(event, user):
    return user in event.participants

@register.filter("to_mangekjemper_status")
def to_mangekjemper_status(username, values):
    if values['attendance'] >= 7 and values['categories'] == 3:
        return '<img src="/static/img/mangekjemper_done.png" style="width:50px; height:50px;"></img>'
    else:
        #TODO: Else if-statement der man ser om det er mulighet
        return '<img src="/static/img/mangekjemper_done.png" style="width:50px; height:50px;"></img>'
