from __future__ import unicode_literals

import random
from authtools.models import AbstractEmailUser
from django.contrib.auth.hashers import UNUSABLE_PASSWORD_PREFIX
from django.contrib.auth.models import BaseUserManager
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail, mail_managers
from django.core.urlresolvers import reverse
from django.db import models, transaction
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _, pgettext_lazy

from oglam import settings


class UserManager(BaseUserManager):
    @classmethod
    def normalize_email(cls, email):
        """
        Normalize the address by lowercasing it.
        """
        return email.lower()

    def create_user(self, email, password=None, **kwargs):
        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, **kwargs):
        user = self.create_user(**kwargs)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractEmailUser):
    hebrew_display_name = models.CharField(_("display name (Hebrew)"),
                                           max_length=200, null=True,
                                           blank=True)
    english_display_name = models.CharField(_("display name (English)"),
                                            max_length=200, null=True,
                                            blank=True)

    team_member = models.BooleanField(_("team member"), default=False)

    community_member = models.BooleanField(_("community member"),
                                           default=False)
    community_name = models.CharField(
        _("Hebrew name (as seen by community)"),
        max_length=120, null=True, blank=True)
    community_email = models.EmailField(
        _("Email (as seen by other community members)"),
        null=True, blank=True,
        help_text=_("can be left empty."))
    community_contact_phone = models.CharField(
        _("Phone number (as seen by other community members)"),
        max_length=120, null=True, blank=True,
        help_text=_("can be left empty."))
    community_personal_info = models.TextField(
        _("Personal info (as seen by other community members)"), null=True,
        blank=True,
        help_text=_("Share something about yourself!"))

    objects = UserManager()

    class Meta:
        db_table = 'auth_user'
        ordering = (
            '-is_superuser',
            '-is_staff',
            '-last_login',
            'hebrew_display_name',
            'email',
        )

    def get_absolute_url(self):
        return "/users/%d/" % self.id

    def has_password(self):
        return self.password and not self.password.startswith(
            UNUSABLE_PASSWORD_PREFIX)

    def real_hebrew_name(self):
        try:
            if self.personalinfo.hebrew_first_name:
                return "{} {}".format(
                    self.personalinfo.hebrew_first_name,
                    self.personalinfo.hebrew_last_name,
                )
        except PersonalInfo.DoesNotExist:
            return None

    def real_name_or_email(self):
        """Allowing staff members to see the real identity"""
        return self.real_hebrew_name() or self.email

    def anonymous_name(self):
        return "{} #{}".format(_("Anonymous User"), self.id)

    def __str__(self):
        if self.hebrew_display_name:
            return self.hebrew_display_name

        return self.real_hebrew_name() or self.anonymous_name()


class PersonalInfo(models.Model):
    user = models.OneToOneField(User)
    hebrew_first_name = models.CharField(_("first name (Hebrew)"),
                                         max_length=200)
    hebrew_last_name = models.CharField(_("last name (Hebrew)"),
                                        max_length=200)
    english_first_name = models.CharField(_("first name (English)"),
                                          max_length=200)
    english_last_name = models.CharField(_("last name (English)"),
                                         max_length=200)

    FEMALE = 1
    MALE = 2
    NA = 3
    GENDER_CHOICES = (
        (FEMALE, _("female")),
        (MALE, _("male")),
        (NA, _("prefer not to answer")),
    )
    gender = models.IntegerField(
        _("gender"), choices=GENDER_CHOICES, default=NA,
        help_text=_("we would like to create a diverse group."))

    main_phone = models.CharField(_("main phone number"), max_length=50)
    alt_phone = models.CharField(_("alternate phone number"), max_length=50,
                                 null=True, blank=True)
    city = models.CharField(_("city"), max_length=200, null=True, blank=True)
    address = models.TextField(_("address"), null=True, blank=True,
                               help_text=_("street and number"))

    class Meta:
        verbose_name = _("pesronal info")
        verbose_name_plural = _("pesronal infos")


def generate_code(length=32):
    return ''.join(
        [random.choice(
            'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_')
         for i in range(length)])


class CodeManager(models.Manager):
    def generate(self, email):
        return self.create(email=email.lower(), code=generate_code())


class Code(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    email = models.EmailField()
    code = models.CharField(max_length=32, unique=True)
    verified = models.BooleanField(default=False)

    objects = CodeManager()

    def send_validation(self, host_url):
        url = host_url + reverse('users:validate', args=(self.code,), )
        send_mail(
            _('Your OGLAM Login Link'),
            '{}:\n{}'.format(_("To login to OGLAM, click here"), url),
            settings.EMAIL_FROM, [self.email]
        )


class UserLogOperation(object):
    OTHER = 0
    ADD = 1
    CHANGE = 2
    REMOVE = 3

    choices = (
        (OTHER, pgettext_lazy('userlog', 'Other')),
        (ADD, pgettext_lazy('userlog', 'Add')),
        (CHANGE, pgettext_lazy('userlog', 'Change')),
        (REMOVE, pgettext_lazy('userlog', 'Remove')),
    )


class UserLog(models.Model):
    user = models.ForeignKey(User, related_name="logs")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name="logs_created",
                                   null=True)
    message = models.TextField(null=True)
    content_type = models.ForeignKey(ContentType, null=True)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    operation = models.IntegerField(choices=UserLogOperation.choices,
                                    default=UserLogOperation.OTHER)

    class Meta:
        ordering = ['-created_at']


class UserNote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='notes')
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               related_name='notes_authored')
    created_at = models.DateTimeField(auto_now_add=True)
    visible_to_user = models.BooleanField(_("visible to user"), default=False)
    content = models.TextField(_("content"), blank=False)

    sent_to_user_at = models.DateTimeField(null=True, blank=True)
    is_open = models.BooleanField(_("open"))
    closed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,
                                  blank=True, related_name="+")
    closed_at = models.DateTimeField(_("closed at"), null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("user note")
        verbose_name_plural = _("user notes")

    def __str__(self):
        return "[#{}] {} - {}".format(
            self.id,
            self.user,
            self.created_at,
        )

    # def is_visible_to(self, user):
    #     if user.is_staff:
    #         return True
    #     if not self.is_published:
    #         return False
    #     if self.scope == self.Visibility.PUBLIC:
    #         return True
    #     return self.user == user
    #

    def get_absolute_url(self):
        return "{}#note-{}".format(
            self.user.get_absolute_url(),
            self.id,
        )

    def notify_managers(self, base_url, sent_to_user=False):
        subject = "{} {} {} {}".format(
            _("User note posted to"),
            self.user.real_name_or_email(),
            _("By"),
            self.author.real_name_or_email(),
        )
        url = self.get_absolute_url()
        html_message = render_to_string("users/usernote_email.html", {
            'base_url': base_url,
            'managers': True,
            'sent_to_user': sent_to_user,
            'title': subject,
            'note': self,
            'url': url,
        })
        mail_managers(subject, '', html_message=html_message)


class TagGroup(object):
    NEGATIVE = -100
    NEUTRAL = 0
    BRONZE = 100
    SILVER = 200
    GOLD = 300

    choices = (
        (NEGATIVE, _('red')),
        (NEUTRAL, _('gray')),
        (BRONZE, _('bronze')),
        (SILVER, _('silver')),
        (GOLD, _('gold')),
    )


class Tag(models.Model):
    name = models.CharField(_("name"), max_length=100)
    group = models.IntegerField(_("group"), choices=TagGroup.choices,
                                default=TagGroup.NEUTRAL)

    class Meta:
        ordering = ['-group', 'name']
        verbose_name = _("tag")
        verbose_name_plural = _("tags")

    def __str__(self):
        return self.name


class UserTagManager(models.Manager):
    def tag(self, user, tag, by):
        with transaction.atomic():
            o, created = self.get_or_create(user=user, tag=tag,
                                            defaults={'created_by': by})
            if created:
                UserLog.objects.create(user=user, created_by=by,
                                       content_object=tag,
                                       operation=UserLogOperation.ADD)
        return o

    def untag(self, user, tag, by):
        with transaction.atomic():
            try:
                o = self.get(user=user, tag=tag)
                o.delete()
                UserLog.objects.create(user=user, created_by=by,
                                       content_object=tag,
                                       operation=UserLogOperation.REMOVE)
                return True
            except UserTag.DoesNotExist:
                return False


class UserTag(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="tags")
    tag = models.ForeignKey(Tag, related_name='users')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   related_name="tags_created")

    objects = UserTagManager()

    class Meta:
        unique_together = (
            ('user', 'tag'),
        )
