import logging
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.smear.models import Game


LOG = logging.getLogger(__name__)


# Call from CLI via: $ python manage.py cleanup_old_games
class Command(BaseCommand):
    def handle(self, *args, **options):
        older_than = timezone.now() - timedelta(days=90)
        self.find_and_delete_old_games(older_than)

    def find_and_delete_old_games(self, older_than):
        LOG.info(f"Looking for games older than {older_than}")

        old_games = Game.objects.filter(created_at__lte=older_than)
        num_old_games = old_games.count()

        LOG.info(f"Deleting {num_old_games} old games")

        num_objects, results = old_games.delete()

        LOG.info(f"Successfully deleted {num_objects} objects: {results}")
