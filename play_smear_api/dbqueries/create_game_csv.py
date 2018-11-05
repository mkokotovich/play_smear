import datetime
import logging

import csv

from stat_gatherer import StatGatherer


logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(threadName)s %(lineno)d:%(message)s")
LOG = logging.getLogger()
# Get stats for this many games at a time
INTERVAL = 100000


def find_high_score(game):
    scores = [result['final_score'] for result in game['results']]
    return max(scores) if scores else 0


def create_game_stats_csv(stat):
    filename = "game-stats.csv"


    with open(filename, 'w') as f:
        writer = csv.DictWriter(
            f,
            fieldnames=(
                'date_played',
                'num_players',
                'num_teams',
                'num_hands',
                'high_score',
                'points_to_play_to',
                'game_id',
            ),
            extrasaction='ignore'
        )
        writer.writeheader()

        cursor = stat.db.games.find()
        start = 0
        stop = INTERVAL
        total = cursor.count()
        while start < total:
            LOG.info("Processing games " + str(start) + " through " + str(stop) + " out of " + str(total))
            game_stats = [
                {
                    'date_played': game.get('date_played', game.get('date_added')),
                    'num_players': len(game['results']),
                    'num_teams': game['num_teams'],
                    'num_hands': len(game['hands']),
                    'high_score': find_high_score(game),
                    'points_to_play_to': game['points_to_play_to'],
                    'game_id': str(game['_id']),
                }
                for game in cursor[start:stop]
            ]
            writer.writerows(game_stats)
            cursor.rewind()
            start = stop + 1
            stop = stop + INTERVAL if stop + INTERVAL < total else total

    LOG.info("Wrote game stats to " + filename)


if __name__ == '__main__':
    stat = StatGatherer()
    stat.connect_to_db()

    create_game_stats_csv(stat)
