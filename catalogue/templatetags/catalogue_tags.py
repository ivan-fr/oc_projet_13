from django import template

register = template.Library()


@register.filter
def get_obj_attr(obj, attr):
    return getattr(obj, attr)


@register.filter
def get_dict_attr(dict, attr):
    return dict.get(attr)


@register.filter
def twodigitcomma(number):
    return "%.2f" % float(number)


@register.filter
def leadingzero(number):
    return f"{number:02d}"


@register.simple_tag()
def multiply(x1, x2, x3=1):
    # you would need to do any localization of the result here
    if x3 is None:
        return "%.2f" % (float(x1) * float(x2))
    else:
        return "%.2f" % (float(x1) * float(x2) * float(x3))


@register.filter
def float_to_str_to_point(value):
    return str(value).replace(",", ".")
