from django import template

register = template.Library()

@register.filter

def get_subject_mark(value):
    find_value = value.find('-')
    mark=value[find_value+1:]

    return mark