from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models, transaction
from django.utils import timezone
from django_extensions.db.fields.json import JSONField
from django.utils.translation import ugettext_lazy as _

from q13es.forms import get_pretty_answer
from . import consts


class Application(models.Model):
    class Status:
        NA = -1

        NEW = 1
        REGISTERED = 2

        DECIDED_NOT_TO_PARTICIPATE = 5

        UNDER_DISCUSSION = 10
        TO_REJECT = 11

        INVITE_TO_INTERVIEW = 20
        INVITED_TO_INTERVIEW = 21

        DID_NOT_ATTEND_INTERVIEW = 25
        PARTICIPATED_IN_INTERVIEW = 30

        TO_WAITING_LIST = 40
        WAITING_LIST = 41

        TO_ACCEPT = 50
        ACCEPTED = 51

        ACCEPTED_AND_APPROVED = 100

        ACCEPTED_AND_DECLINED = 200
        REJECTED = 201

        choices = (
            (NA, _("n/a")),
            (NEW, _("new (incomplete application)")),
            (REGISTERED, _("registered")),

            (DECIDED_NOT_TO_PARTICIPATE, _("decided not to participate")),

            (UNDER_DISCUSSION, _("under discussion")),
            (TO_REJECT, _("to reject")),
            (INVITE_TO_INTERVIEW, _("invite to interview")),
            (INVITED_TO_INTERVIEW, _("invited to interview")),

            (DID_NOT_ATTEND_INTERVIEW, _("did not attend interview")),
            (PARTICIPATED_IN_INTERVIEW, _("participated in interview")),

            (TO_WAITING_LIST, _("to waiting list")),
            (WAITING_LIST, _("waiting list")),

            (TO_ACCEPT, _("to accept")),
            (ACCEPTED, _("accepted")),

            (ACCEPTED_AND_APPROVED, _("accepted and approved")),
            (ACCEPTED_AND_DECLINED, _("accepted and declined")),

            (REJECTED, _("rejected")),
        )

        passed_interview = (
            TO_WAITING_LIST,
            WAITING_LIST,
            TO_ACCEPT,
            ACCEPTED,
            ACCEPTED_AND_APPROVED,
        )

        labels = dict(choices)

    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    forms_filled = models.IntegerField(default=0, db_index=True)
    last_form_filled = models.DateTimeField(null=True, blank=True,
                                            db_index=True)
    status = models.IntegerField(_("status"), choices=Status.choices,
                                 default=Status.NEW)
    status_changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,
                                          related_name="+")
    status_changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user)

    def get_absolute_url(self):
        return reverse("sa:app_detail", args=(self.id,))

    def set_status(self, value, user):
        self.status = value
        self.status_changed_at = timezone.now()
        self.status_changed_by = user

    def add_status_log(self):
        return self.status_logs.create(
            value=self.status,
            value_changed_by=self.status_changed_by,
            value_changed_at=self.status_changed_at,
        )

    def set_and_log_status(self, value, user):
        with transaction.atomic():
            self.set_status(value, user)
            self.save()
            self.add_status_log()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.id:
            super().save(force_insert, force_update, using, update_fields)
            return

        with transaction.atomic():
            super().save(force_insert, force_update, using, update_fields)
            self.add_status_log()


class ApplicationStatusLog(models.Model):
    application = models.ForeignKey(Application, related_name="status_logs")
    value = models.IntegerField(choices=Application.Status.choices)
    value_changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,
                                         related_name="+")
    value_changed_at = models.DateTimeField()

    class Meta:
        ordering = (
            '-value_changed_at',
        )


class Answer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='answers')
    q13e_slug = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    data = JSONField()

    class Meta:
        unique_together = (
            ('user', 'q13e_slug'),
        )
        ordering = (
            'created_at',
        )

    def __str__(self):
        return "%s: %s (%s)" % (self.user, self.q13e_slug, self.created_at)

    def get_pretty(self):
        form = consts.FORMS[self.q13e_slug]
        return dict(get_pretty_answer(form, self.data), answer=self)


class ApplicationReview(models.Model):
    application = models.ForeignKey(Application, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name="application_reviews")
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    last_edited_at = models.DateTimeField(_("last edited at"),
                                          auto_now_add=True)

    class Level:
        SKIP = None
        TOO_LOW = -1
        AVERAGE = 0
        HIGH = 1
        VERY_HIGH = 2

        choices = (
            ('', _("no answer supplied")),
            (TOO_LOW, _("too low")),
            (AVERAGE, _("average")),
            (HIGH, _("high")),
            (VERY_HIGH, _("very high")),
        )

        fit_choices = (
            ('', _("no answer supplied")),
            (TOO_LOW, _("does not fit")),
            (AVERAGE, _("undecided / neutral")),
            (HIGH, _("fit")),
            (VERY_HIGH, _("highly fits")),
        )

        non_negative_choices = choices[0:1] + choices[2:]

        # labels = dict((
        #     (UNINTERESTED, 'warning'),
        #     (NEUTRAL, 'default'),
        #     (INTERESTED, 'primary'),
        #     (VERY_INTERESTED, 'success'),
        # ))

    programming_exp = models.IntegerField(
        _("programming experience"),
        null=True, blank=True, default=None,
        choices=Level.choices
    )
    webdev_exp = models.IntegerField(
        _("web development experience"),
        null=True, blank=True,
        choices=Level.non_negative_choices
    )
    activism_level = models.IntegerField(
        _("involvement in activism"),
        null=True, blank=True,
        choices=Level.non_negative_choices
    )
    availability = models.IntegerField(
        _("present and future availability"),
        null=True, blank=True,
        choices=Level.choices
    )
    humanism_background = models.IntegerField(
        _("background in humanism"),
        null=True, blank=True,
        choices=Level.non_negative_choices
    )
    comm_skills = models.IntegerField(
        _("communication skills"),
        null=True, blank=True,
        choices=Level.non_negative_choices
    )

    overall_impression = models.IntegerField(
        _("overall_impression"),
        null=True, blank=True,
        choices=Level.fit_choices,
        help_text=_("Does the candidate fit the program?")
    )

    comments = models.TextField(
        _("review comments"),
        blank=True,
        help_text=_("Consider adding a user note instead ")
    )

    class Meta:
        unique_together = (
            ('application', 'user'),
        )
        ordering = (
            '-created_at',
        )
        verbose_name = _("application review")
        verbose_name_plural = _("application reviews")

    detail_fields = (
        'programming_exp',
        'webdev_exp',
        'activism_level',
        'availability',
        'humanism_background',
        'comm_skills',
        'overall_impression',
    )

    def get_details(self):
        return (
            (
                self._meta.get_field(fld).verbose_name,
                getattr(self, "get_{}_display".format(fld))()
            ) for fld in self.detail_fields
            if getattr(self, fld) is not None
        )

#
#
# class Cohort(models.Model):
#     ordinal = models.IntegerField(unique=True)
#     code = models.CharField(max_length=10, unique=True)
#     title = models.CharField(max_length=200)
#     description = models.TextField(null=True, blank=True)
#
#     def __unicode__(self):
#         return self.title
#
#     class Meta:
#         ordering = ['ordinal']
#
#     @models.permalink
#     def get_absolute_url(self):
#         return "cohort", (self.code,)
#
#     def users_in_pipeline(self):
#         return self.users.filter(status__in=UserCohortStatus.PIPELINE)
#
#
# class UserCohortStatus(object):
#     INVITED = 1
#
#     UNAVAILABLE = 2
#
#     AVAILABLE = 10
#
#     INVITED_TO_INTERVIEW = 50
#
#     REJECTED = 99
#     ACCEPTED = 100
#     IN_OTHER_COHORT = 101
#
#     REGISTERED = 110
#     IN_PROCESS = 200
#     GRADUATED = 300
#
#     choices = (
#         (INVITED, _('Invited')),
#         (UNAVAILABLE, _('Unavailable')),
#         (AVAILABLE, _('Available')),
#         (INVITED_TO_INTERVIEW, _('Invited to interview')),
#
#         (REJECTED, _('Rejected')),
#         (ACCEPTED, _('Accepted')),
#         (IN_OTHER_COHORT, _('Accepted to another cohort')),
#
#         (REGISTERED, _('Registered')),
#         (IN_PROCESS, _('In process')),
#         (GRADUATED, _('Graduated')),
#     )
#
#     PIPELINE = [AVAILABLE, INVITED_TO_INTERVIEW, ACCEPTED, REGISTERED,
#                 IN_PROCESS, GRADUATED]
#     IGNORED = [INVITED, UNAVAILABLE, REJECTED, IN_OTHER_COHORT]
#
#
# class UserCohort(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="cohorts")
#     cohort = models.ForeignKey(Cohort, related_name="users")
#     status = models.IntegerField(choices=UserCohortStatus.choices)
#     statuses = UserCohortStatus
#
#     class Meta:
#         unique_together = (
#             ('user', 'cohort'),
#         )
#         ordering = ['cohort', 'status']
#
#
# class TagGroup(object):
#     NEGATIVE = -100
#     NEUTRAL = 0
#     BRONZE = 100
#     SILVER = 200
#     GOLD = 300
#
#     choices = (
#         (NEGATIVE, 'negative'),
#         (NEUTRAL, 'neutral'),
#         (BRONZE, 'bronze'),
#         (SILVER, 'silver'),
#         (GOLD, 'gold'),
#     )
#
#
# class Tag(models.Model):
#     name = models.CharField(max_length=100)
#     group = models.IntegerField(choices=TagGroup.choices,
#                                 default=TagGroup.NEUTRAL)
#
#     class Meta:
#         ordering = ['-group', 'name']
#
#     def __unicode__(self):
#         return self.name
#
#
# class UserTagManager(models.Manager):
#     def tag(self, user, tag, by):
#         with transaction.commit_on_success():
#             o, created = self.get_or_create(user=user, tag=tag, created_by=by)
#             if created:
#                 UserLog.objects.create(user=user, created_by=by,
#                                        content_object=tag,
#                                        operation=UserLogOperation.ADD)
#         return o
#
#     def untag(self, user, tag, by):
#         with transaction.commit_on_success():
#             try:
#                 o = self.get(user=user, tag=tag, created_by=by)
#                 o.delete()
#                 UserLog.objects.create(user=user, created_by=by,
#                                        content_object=tag,
#                                        operation=UserLogOperation.REMOVE)
#                 return True
#             except UserTag.DoesNotExist:
#                 return False
#
#
# class UserTag(models.Model):
#     created_at = models.DateTimeField(auto_now_add=True)
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="tags")
#     tag = models.ForeignKey(Tag, related_name='users')
#     created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
#                                    related_name="tags_created")
#
#     objects = UserTagManager()
#
#     class Meta:
#         unique_together = (
#             ('user', 'tag', 'created_by'),
#         )
