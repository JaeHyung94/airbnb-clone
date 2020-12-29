from django import template

register = template.Library()


@register.filter
def hot_capitals(value):
    return value.capitalize()