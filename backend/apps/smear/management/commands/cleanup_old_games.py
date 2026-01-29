import logging
import gc
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.smear.models import Game


LOG = logging.getLogger(__name__)


def queryset_iterator(qs, batchsize=500, gc_collect=True):
    iterator = qs.values_list('pk', flat=True).order_by('pk').distinct().iterator()
    eof = False
    while not eof:
        primary_key_buffer = []
        try:
            while len(primary_key_buffer) < batchsize:
                primary_key_buffer.append(next(iterator))
        except StopIteration:
            eof = True
        # for obj in qs.filter(pk__in=primary_key_buffer).order_by('pk').iterator():
        #     yield obj
        yield qs.filter(pk__in=primary_key_buffer)
        if gc_collect:
            gc.collect()


# Call from CLI via: $ python manage.py cleanup_old_games
class Command(BaseCommand):
    def handle(self, *args, **options):
        older_than = timezone.now() - timedelta(days=90)
        #older_than = timezone.now() - timedelta(seconds=1)
        self.find_and_delete_old_games(older_than)

    def find_and_delete_old_games(self, older_than):
        LOG.info(f"Looking for games older than {older_than}")

        old_games = Game.objects.filter(created_at__lte=older_than)
        num_old_games = old_games.count()

        LOG.info(f"Deleting {num_old_games} old games")

        total_objects = 0
        for chunk in queryset_iterator(old_games):
            num_objects, results = chunk.delete()
            total_objects += num_objects
            LOG.info(f"Successfully deleted {num_objects} objects: {results}")

        LOG.info(f"Successfully deleted all {total_objects} objects")
