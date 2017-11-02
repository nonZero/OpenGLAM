import logging

from django.db.models import Q

from student_applications.models import Application
from . import models

logger = logging.getLogger(__name__)


def fix_user(u: models.User):
    u.community_member = True
    try:
        u.community_name = "{} {}".format(
            u.personalinfo.hebrew_first_name,
            u.personalinfo.hebrew_last_name,
        )
        u.community_contact_phone = u.personalinfo.main_phone
        s = u.community_contact_phone.strip()
        if s.isnumeric() and len(s) == len("0501234567"):
            u.community_contact_phone = s[:3] + "-" + s[3:]

    except Exception as e:
        assert "User has no personalinfo" in str(e)
        u.community_name = u.hebrew_display_name

    u.community_email = u.email
    u.save()
    logger.info('fixed user {}'.format(u.email))


def import_community_info():
    status = Application.Status.ACCEPTED_AND_APPROVED
    q = Q(team_member=True) | Q(application__status=status)
    qs = models.User.objects.filter(q, community_name=None)
    for u in qs:
        fix_user(u)
