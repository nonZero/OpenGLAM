import logging

from django.apps import AppConfig
from django.db.models import signals

logger = logging.getLogger(__name__)

SLUG = "roles"
YES = "כן"

TAGS = {
    'is_developer',
    'is_ui_expert',
    'is_graphic_designer',
}


class StudentApplicationsConfig(AppConfig):
    name = 'student_applications'

    def ready(self):
        signals.post_save.connect(post_save_answer,
                                  'student_applications.Answer',

                                  )


def post_save_answer(instance, created, **kwargs):
    if created:
        add_tags_from_answer(instance)


def add_tags_from_answer(answer):
    from .models import Answer
    assert isinstance(answer, Answer)
    from users.models import UserTag
    if answer.q13e_slug == SLUG:
        for s in TAGS:
            from users.models import Tag
            t = Tag.objects.get(slug=s)
            if answer.data[s] == YES:
                o, created = UserTag.objects.get_or_create(
                    user=answer.user,
                    tag=t,
                )
                if created:
                    logger.info(
                        f"Created tag {s} for user {answer.user.email}")
