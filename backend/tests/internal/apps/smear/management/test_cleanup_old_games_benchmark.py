import gc
import os
import time
from collections import defaultdict
from datetime import timedelta

import pytest
from django.utils import timezone

from apps.smear.management.commands.cleanup_old_games import Command as OldCleanupCommand
from apps.smear.management.commands.cleanup_old_games_v2 import Command as NewCleanupCommand
from apps.smear.models import Bid, Game, Hand, Play, Player, Team, Trick
from tests.internal.apps.user.factories import UserFactory

RUN_BENCHMARK = os.getenv("RUN_CLEANUP_BENCHMARK") == "1"
NUM_GAMES = 1000
HANDS_PER_GAME = 6
BIDS_PER_HAND = 4
TRICKS_PER_HAND = 6
RETENTION_DAYS = 90


def create_game_aggregates(num_games, users, created_at):
    games = Game.objects.bulk_create(
        [
            Game(
                owner=users[0],
                name=f"Benchmark game {i}",
                num_players=4,
                num_teams=2,
                score_to_play_to=11,
            )
            for i in range(num_games)
        ]
    )
    Game.objects.filter(pk__in=[game.id for game in games]).update(created_at=created_at)

    teams = []
    for game in games:
        teams.extend(
            [
                Team(game=game, name=f"Team {game.id}-0"),
                Team(game=game, name=f"Team {game.id}-1"),
            ]
        )
    Team.objects.bulk_create(teams)

    players = []
    for game_idx, game in enumerate(games):
        game_teams = teams[game_idx * 2 : game_idx * 2 + 2]
        for seat in range(4):
            players.append(
                Player(
                    game=game,
                    user=users[seat],
                    name=f"Player {game.id}-{seat}",
                    seat=seat,
                    team=game_teams[seat % 2],
                )
            )
    Player.objects.bulk_create(players)

    players_by_game = defaultdict(list)
    players_to_update = []
    for player in players:
        players_by_game[player.game_id].append(player)
        if player.seat:
            player.plays_after = players_by_game[player.game_id][player.seat - 1]
            players_to_update.append(player)
    Player.objects.bulk_update(players_to_update, ["plays_after"])

    for game in games:
        game.next_dealer = players_by_game[game.id][0]
    Game.objects.bulk_update(games, ["next_dealer"])

    hands = []
    for game in games:
        game_players = players_by_game[game.id]
        for hand_num in range(1, HANDS_PER_GAME + 1):
            hands.append(
                Hand(
                    game=game,
                    num=hand_num,
                    dealer=game_players[hand_num % 4],
                    bidder=game_players[(hand_num + 1) % 4],
                )
            )
    Hand.objects.bulk_create(hands)

    bids = []
    high_bids = []
    for hand in hands:
        game_players = players_by_game[hand.game_id]
        hand_bids = [
            Bid(
                hand=hand,
                player=game_players[(bid_num + 1) % 4],
                bid=bid_num + 2,
                trump="spades" if bid_num == BIDS_PER_HAND - 1 else "",
            )
            for bid_num in range(BIDS_PER_HAND)
        ]
        bids.extend(hand_bids)
        high_bids.append(hand_bids[-1])
    Bid.objects.bulk_create(bids)

    for hand, high_bid in zip(hands, high_bids):
        hand.high_bid = high_bid
    Hand.objects.bulk_update(hands, ["high_bid"])

    tricks = []
    for hand in hands:
        game_players = players_by_game[hand.game_id]
        for trick_num in range(1, TRICKS_PER_HAND + 1):
            tricks.append(
                Trick(
                    hand=hand,
                    num=trick_num,
                    active_player=game_players[trick_num % 4],
                    taker=game_players[(trick_num + 1) % 4],
                )
            )
    Trick.objects.bulk_create(tricks)

    plays = []
    for trick in tricks:
        for player in players_by_game[trick.hand.game_id]:
            plays.append(Play(trick=trick, player=player, card="AS"))
    Play.objects.bulk_create(plays)


@pytest.mark.skipif(
    not RUN_BENCHMARK,
    reason="Set RUN_CLEANUP_BENCHMARK=1 to run the 1,000-game cleanup benchmark.",
)
@pytest.mark.django_db(transaction=True)
def test_cleanup_old_games_benchmark(capsys):
    users = [UserFactory() for _ in range(4)]
    cutoff = timezone.now() - timedelta(days=RETENTION_DAYS)
    old_created_at = timezone.now() - timedelta(days=RETENTION_DAYS + 1)

    create_game_aggregates(NUM_GAMES, users, old_created_at)

    assert Game.objects.filter(created_at__lte=cutoff).count() == NUM_GAMES
    gc.collect()
    start = time.perf_counter()
    OldCleanupCommand().find_and_delete_old_games(cutoff)
    old_elapsed = time.perf_counter() - start

    assert not Game.objects.filter(created_at__lte=cutoff).exists()
    assert not Play.objects.exists()
    assert not Trick.objects.exists()
    assert not Bid.objects.exists()
    assert not Hand.objects.exists()
    assert not Player.objects.exists()
    assert not Team.objects.exists()

    create_game_aggregates(NUM_GAMES, users, old_created_at)

    assert Game.objects.filter(created_at__lte=cutoff).count() == NUM_GAMES
    gc.collect()
    start = time.perf_counter()
    new_deleted = NewCleanupCommand().find_and_delete_old_games(cutoff)
    new_elapsed = time.perf_counter() - start

    assert new_deleted == NUM_GAMES
    assert not Game.objects.filter(created_at__lte=cutoff).exists()
    assert not Play.objects.exists()
    assert not Trick.objects.exists()
    assert not Bid.objects.exists()
    assert not Hand.objects.exists()
    assert not Player.objects.exists()
    assert not Team.objects.exists()

    with capsys.disabled():
        print()
        print(f"Cleanup benchmark ({NUM_GAMES} games):")
        print(f"  old command: {old_elapsed:.3f}s")
        print(f"  new command: {new_elapsed:.3f}s")
        print(f"  speedup:     {old_elapsed / new_elapsed:.2f}x")
