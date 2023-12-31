from django import template

register = template.Library()

@register.filter
def get_subject_id(value):
    find_value=value.find('-')
    subject_id=value[:find_value]


    return subject_id


