from django import template

from users import models

register = template.Library()


@register.inclusion_tag('users/_user_tags.html')
def user_tags(user, edit=False):
    assert isinstance(user, models.User)
    return {'u': user, 'edit': edit}
