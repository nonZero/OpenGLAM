import logging

import markdown
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.fields.json import JSONField

from q13es.forms import parse_form, get_pretty_answer
from users.models import generate_code
from utils.mail import send_html_mail

logger = logging.getLogger(__name__)


class Survey(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    email_subject = models.CharField(_('email subject'), max_length=250)
    email_content = models.TextField(_('email content (markdown)'), null=True,
                                     blank=True)
    email_content_html = models.TextField(editable=False, null=True,
                                          blank=True)
    q13e = models.TextField()

    class Meta:
        verbose_name = _("survey")
        verbose_name_plural = _("surveys")

    def __str__(self):
        return self.email_subject

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.email_content_html = markdown.markdown(
            self.email_content) if self.email_content else None
        super().save(force_insert, force_update, using, update_fields)

    def get_form_class(self):
        return parse_form(self.q13e)

    def add_user(self, user):
        return SurveyAnswer.objects.get_or_create(survey=self, user=user)

    def get_absolute_url(self):
        return reverse("surveys:detail", args=(self.pk,))


class SurveyAnswer(models.Model):
    survey = models.ForeignKey(Survey, related_name='answers')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='survey_answers')
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(default=generate_code)
    answered_at = models.DateTimeField(null=True, blank=True)
    is_open = models.BooleanField(_("open"), default=True, db_index=True)
    data = JSONField(null=True, blank=True)

    class Meta:
        ordering = (
            '-is_open',
            '-answered_at',
            '-created_at',
        )
        unique_together = (
            ('survey', 'user'),
        )
        verbose_name = _("survey answer")
        verbose_name_plural = _("survey answers")

    def __str__(self):
        return "%s: %s (%s)" % (self.survey, self.user, self.created_at)

    def get_pretty(self):
        dct = get_pretty_answer(self.survey.get_form_class(), self.data)
        dct['answer'] = self
        return dct

    def get_absolute_url(self):
        return reverse("surveys:answer", args=(self.slug,))

    def send(self, base_url=""):
        """ sends an email to user  """

        context = {'base_url': base_url, 'object': self}

        html_message = render_to_string("surveys/survey_email.html", context)

        logger.info("Sending survey (#%d) for survey #%d to user #%d at %s"
                    % (self.id, self.survey.id, self.user.id, self.user.email))

        send_html_mail(
            self.survey.email_subject,
            html_message,
            self.user.email,
        )

        return True
