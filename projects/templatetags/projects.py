from django import template

register = template.Library()

from projects import models


@register.filter
def comment_is_visible(comment, user):
    assert isinstance(comment, models.ProjectComment)
    return comment.is_visible_to(user)
