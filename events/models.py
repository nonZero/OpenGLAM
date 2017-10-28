import logging

import markdown
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from users.models import generate_code
from utils.mail import send_html_mail

logger = logging.getLogger(__name__)


class Event(models.Model):
    title = models.CharField(_('title'), max_length=400)
    slug = models.SlugField(validators=[RegexValidator('^[-\w]+$')])
    is_active = models.BooleanField(_("active"), default=True)
    is_open = models.BooleanField(_("invitations open"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   related_name="events_created",
                                   limit_choices_to={'is_staff': True})
    starts_at = models.DateTimeField(_("starts at"))
    ends_at = models.DateTimeField(_("ends at"))
    registration_ends_at = models.DateTimeField(_("registartion ends at"),
                                                null=True, blank=True)
    location = models.CharField(_('location'), max_length=400, null=True)
    description = models.TextField(_('description'), null=True)
    description_html = models.TextField(null=True)

    def __str__(self):
        return self.title

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.description_html = markdown.markdown(
            self.description) if self.description else None
        super().save(force_insert, force_update, using, update_fields)

    def get_absolute_url(self):
        return reverse("events:detail", args=(self.slug,))

    def is_open_for_registration(self, dt=None):

        if dt is None:
            dt = timezone.now()

        if self.registration_ends_at:
            if self.registration_ends_at < dt:
                return False
        else:
            if self.starts_at < dt:
                return False

        return True

    def invite_user(self, user, created_by=None, base_url=None):

        try:
            o = EventInvitation.objects.get(event=self, user=user)
            created = False
        except EventInvitation.DoesNotExist:
            o = EventInvitation.objects.create(event=self, user=user,
                                               created_by=created_by)
            o.send(base_url)
            created = True

        return o, created


class EventInvitationStatus(object):
    NEW = 1
    SENT = 2
    APPROVED = 3
    MAYBE = 4
    DECLINED = 5

    choices = (
        (NEW, _('New invitation')),
        (SENT, _('Invitation sent')),
        (APPROVED, _('Invitation approved')),
        (MAYBE, _('Invitation maybe')),
        (DECLINED, _('Invitation declined')),
    )


class EventInvitationAttendance(object):
    ATTENDED = 1
    PARTIALLY_ATTENDED = 2
    DID_NOT_ATTEND = 3

    choices = (
        (ATTENDED, _('Attended')),
        (PARTIALLY_ATTENDED, _('Partially attended')),
        (DID_NOT_ATTEND, _('Did not attend')),
    )


class EventInvitation(models.Model):
    event = models.ForeignKey(Event, related_name="invitations")
    slug = models.SlugField(default=generate_code)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   related_name="event_invitations_created",
                                   null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name="invitations")
    status = models.IntegerField(_('Status'),
                                 choices=EventInvitationStatus.choices,
                                 default=EventInvitationStatus.NEW)
    note = models.TextField(_('Note'), null=True, blank=True)

    statuses = EventInvitationStatus

    attendance = models.IntegerField(_('Attendance'),
                                     choices=EventInvitationAttendance.choices,
                                     null=True, blank=True)

    class Meta:
        ordering = ['event', 'status', 'created_at']
        unique_together = (
            ('event', 'user'),
        )

    def get_absolute_url(self):
        return reverse("events:invitation", args=(self.slug,))

    def registration_allowed(self, dt=None):
        """ returns True if user is allowed to register or modify her
            registration """

        if self.event.is_open_for_registration(dt):
            # still allowed.
            return True

        if self.status == EventInvitationStatus.APPROVED:
            # approved users can always change their mind.
            return True

        return False

    def send(self, base_url=""):
        """ sends an email to user and updated the invitaiton status """
        assert self.status == EventInvitationStatus.NEW

        context = {'base_url': base_url, 'object': self}

        subject = "{}: {}".format(_("Invitation"), self.event.title)

        html_message = render_to_string("events/emails/invitation.html",
                                        context)

        logger.info("Sending invitation #%d for event #%d to user #%d at %s"
                    % (self.id, self.event.id, self.user.id, self.user.email))

        send_html_mail(subject, html_message, self.user.email)

        self.status = EventInvitationStatus.SENT
        self.save()

        return True
