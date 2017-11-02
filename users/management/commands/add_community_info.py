from django.core.management.base import BaseCommand

from users.util import import_community_info


class Command(BaseCommand):
    help = "Add community contact info from personal info"

    def handle(self, *args, **options):
        import_community_info()
