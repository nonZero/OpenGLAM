import random

from django import template
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse, NoReverseMatch
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(needs_autoescape=True)
def u(instance, title_attr='__str__', autoescape=None):
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x
    s = getattr(instance, title_attr)
    if callable(s):
        s = s()
    result = '<a href="%s">%s</a>' % (esc(instance.get_absolute_url()),
                                      esc(s))
    return mark_safe(result)


@register.filter
def l(instance):
    return instance.get_absolute_url()


@register.filter
def admin_url(instance):
    try:
        return reverse(
            'admin:%s_%s_change' % (
                instance._meta.app_label, instance._meta.model_name),
            args=[instance.id])
    except NoReverseMatch:
        return ""


@register.filter
def admin_changelist_url(model):
    try:
        return reverse('admin:%s_%s_changelist' % (
            model._meta.app_label, model._meta.model_name))
    except NoReverseMatch:
        return ""


@register.filter
def coords(xy):
    return "{:,.0f}:{:,.0f}".format(*xy)


@register.filter
def upload_doc_url(instance):
    ct = ContentType.objects.get_for_model(instance.__class__)
    return reverse("dms:create", args=(ct.id, instance.id))


@register.filter
def page(request, page):
    d = request.GET.copy()
    d['page'] = page
    return d.urlencode()


@register.filter
def pages_around(paginator, num, margin=3):
    start = max(1, num - margin)
    end = min(paginator.num_pages, num + margin)
    return range(start, end + 1)


@register.filter
def shuffle(arg):
    l = list(arg)
    random.shuffle(l)
    return l
