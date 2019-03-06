from django import template

register = template.Library()


@register.filter
def get_obj_attr(obj, attr):
    return getattr(obj, attr)


@register.filter
def get_dict_attr(dict, attr):
    return dict.get(attr)
