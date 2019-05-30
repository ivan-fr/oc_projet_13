from django import template

register = template.Library()


@register.filter
def thread_check_other_user(main_user, other):
    if main_user == other:
        return True

    return False


@register.filter
def thread_get_other_user(main_user, thread):
    if main_user == thread.first:
        return thread.second
    elif main_user == thread.second:
        return thread.first

    return None
