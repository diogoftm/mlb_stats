
from django import template


register = template.Library()


@register.filter
def get_item_first(dictionary, key):
    v = dictionary.get(key)
    if v:
        return v[0]
    return key

@register.filter
def get_item_second(dictionary, key):
    v = dictionary.get(key)
    if v:
        return v[1]
    return None