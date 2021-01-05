from django import template

register = template.Library()


@register.simple_tag
def is_booked(room, day):
    print(room, day)
    return False
