import json

from django.core.management.base import BaseCommand

from student_applications.models import Answer
from users.models import User

STATS = {
    'programming-langs': [
        'c',
        'java',
        'python',
        'perl',
        'csharp',
        'cpp',
        'functional_languages',
        'ruby'
    ],
    'software-development': [
        'git',
        'dcvs',
        'windows',
        'old_cvs',
        'non_relational_databases',
        'mac',
        'linux',
        'relational_databases'
    ],
    'web-technologies': [
        'html',
        'css',
        'php',
        'javascript',
        'rails',
        'django'
    ],
    'work-experience': [
        'years_of_experience',
        'cs_education'
    ]
}


class Command(BaseCommand):
    help = "Export anonymous stats for programming exercises."

    def handle(self, *args, **options):

        all_users = []

        for u in User.objects.all():
            d = {}
            for k, l in STATS.items():
                try:
                    a = u.answers.get(q13e_slug=k)
                    for x in l:
                        d[x] = a.data[x]
                except Answer.DoesNotExist:
                    pass

            if d:
                all_users.append(d)

        json.dumps(all_users)
