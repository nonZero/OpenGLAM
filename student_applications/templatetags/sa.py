from django import template

from student_applications import models

register = template.Library()


@register.inclusion_tag('student_applications/_app_status.html')
def app_status(app, edit=False):
    assert isinstance(app, models.Application)
    return {'app': app, 'edit': edit}
