import logging
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.utils import timezone

LOG = logging.getLogger(__name__)

DEFAULT_DAYS = 90
DEFAULT_BATCH_SIZE = 500


FETCH_GAME_IDS_SQL = """
    SELECT id
    FROM smear_game
    WHERE created_at <= %s
      AND id > %s
    ORDER BY id
    LIMIT %s
"""

# Django implements on_delete in Python, not with database-level cascades. These
# statements break the incoming references first, then delete the game aggregate
# from the leaves up. That avoids loading every related object into Python.
CLEAR_REFERENCES_SQL = (
    """
    UPDATE smear_game
    SET next_dealer_id = NULL
    WHERE id = ANY(%s)
    """,
    """
    UPDATE smear_hand
    SET high_bid_id = NULL
    WHERE game_id = ANY(%s)
    """,
    """
    UPDATE smear_player
    SET plays_after_id = NULL
    WHERE plays_after_id IN (
        SELECT id
        FROM smear_player
        WHERE game_id = ANY(%s)
    )
    """,
)

DELETE_SQL = (
    """
    DELETE FROM smear_play AS p
    USING smear_trick AS t, smear_hand AS h
    WHERE p.trick_id = t.id
      AND t.hand_id = h.id
      AND h.game_id = ANY(%s)
    """,
    """
    DELETE FROM smear_bid AS b
    USING smear_hand AS h
    WHERE b.hand_id = h.id
      AND h.game_id = ANY(%s)
    """,
    """
    DELETE FROM smear_trick AS t
    USING smear_hand AS h
    WHERE t.hand_id = h.id
      AND h.game_id = ANY(%s)
    """,
    "DELETE FROM smear_hand WHERE game_id = ANY(%s)",
    "DELETE FROM smear_player WHERE game_id = ANY(%s)",
    "DELETE FROM smear_team WHERE game_id = ANY(%s)",
    "DELETE FROM smear_game WHERE id = ANY(%s)",
)


class Command(BaseCommand):
    help = "Delete games older than the retention window using set-based SQL."

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=DEFAULT_DAYS,
            help=f"Delete games older than this many days (default: {DEFAULT_DAYS}).",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=DEFAULT_BATCH_SIZE,
            help=f"Number of games to delete per transaction (default: {DEFAULT_BATCH_SIZE}).",
        )

    def handle(self, *args, **options):
        older_than = timezone.now() - timedelta(days=options["days"])
        self.find_and_delete_old_games(older_than, batch_size=options["batch_size"])

    def find_and_delete_old_games(self, older_than, batch_size=DEFAULT_BATCH_SIZE):
        LOG.info("Looking for games older than %s", older_than)

        last_pk = 0
        total_games = 0
        total_rows = 0

        while True:
            with connection.cursor() as cursor:
                cursor.execute(FETCH_GAME_IDS_SQL, [older_than, last_pk, batch_size])
                game_ids = [row[0] for row in cursor.fetchall()]

            if not game_ids:
                break

            last_pk = game_ids[-1]

            with transaction.atomic(), connection.cursor() as cursor:
                for sql in CLEAR_REFERENCES_SQL:
                    cursor.execute(sql, [game_ids])

                batch_rows = 0
                for sql in DELETE_SQL:
                    cursor.execute(sql, [game_ids])
                    batch_rows += cursor.rowcount

            total_games += len(game_ids)
            total_rows += batch_rows
            LOG.info(
                "Deleted %s games and %s related rows (total: %s games, %s rows)",
                len(game_ids),
                batch_rows,
                total_games,
                total_rows,
            )

        LOG.info("Finished. Deleted %s games and %s related rows.", total_games, total_rows)
        return total_games
