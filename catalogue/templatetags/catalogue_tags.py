from django import template

register = template.Library()


@register.filter
def get_obj_attr(obj, attr):
    return getattr(obj, attr)


@register.filter
def get_dict_attr(dict, attr):
    return dict.get(attr)


@register.simple_tag()
def multiply(x1, x2):
    # you would need to do any localization of the result here
    return "%.2f" % (float(x1) * float(x2))
