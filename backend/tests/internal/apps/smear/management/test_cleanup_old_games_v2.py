from datetime import timedelta

import pytest
from django.core.management import call_command
from django.utils import timezone

from apps.smear.models import Bid, Game, Hand, Play, Player, Team, Trick
from tests.internal.apps.smear.factories import GameFactory
from tests.internal.apps.user.factories import UserFactory


def create_game_data(game, num_players=4, num_teams=2):
    teams = [Team.objects.create(game=game, name=f"Team {i}") for i in range(num_teams)]
    users = [UserFactory() for _ in range(num_players)]
    players = [
        Player.objects.create(
            game=game,
            user=users[i],
            team=teams[i % num_teams],
            name=f"Player {i}",
            seat=i,
        )
        for i in range(num_players)
    ]

    # Exercise the self-referencing SET_NULL relationship.
    for i, player in enumerate(players[1:], start=1):
        player.plays_after = players[i - 1]
        player.save(update_fields=["plays_after"])

    game.next_dealer = players[0]
    game.save(update_fields=["next_dealer"])

    for hand_num in (1, 2):
        hand = Hand.objects.create(
            game=game,
            num=hand_num,
            dealer=players[0],
            bidder=players[1],
        )
        high_bid = Bid.objects.create(hand=hand, player=players[1], bid=4, trump="spades")
        Bid.objects.create(hand=hand, player=players[2], bid=3)

        hand.high_bid = high_bid
        hand.winner_high = players[0]
        hand.winner_low = players[1]
        hand.winner_jack = players[2]
        hand.winner_jick = players[3]
        hand.winner_game = players[0]
        hand.save()

        for trick_num in (1, 2):
            trick = Trick.objects.create(
                hand=hand,
                num=trick_num,
                active_player=players[0],
                taker=players[1],
            )
            for player in players:
                Play.objects.create(trick=trick, player=player, card="AS")

    return {"teams": teams, "players": players}


@pytest.mark.django_db
def test_cleanup_old_games_v2_deletes_old_games_and_keeps_recent_ones():
    now = timezone.now()
    old_games = [GameFactory(), GameFactory()]
    recent_game = GameFactory()

    for game in old_games:
        create_game_data(game)
    recent_data = create_game_data(recent_game)

    old_game_ids = [game.id for game in old_games]
    Game.objects.filter(pk__in=old_game_ids).update(created_at=now - timedelta(days=91))
    Game.objects.filter(pk=recent_game.pk).update(created_at=now - timedelta(days=89))

    call_command("cleanup_old_games_v2", days=90, batch_size=1)

    assert not Game.objects.filter(pk__in=old_game_ids).exists()
    assert not Team.objects.filter(game_id__in=old_game_ids).exists()
    assert not Player.objects.filter(game_id__in=old_game_ids).exists()
    assert not Hand.objects.filter(game_id__in=old_game_ids).exists()
    assert not Trick.objects.filter(hand__game_id__in=old_game_ids).exists()
    assert not Bid.objects.filter(hand__game_id__in=old_game_ids).exists()
    assert not Play.objects.filter(trick__hand__game_id__in=old_game_ids).exists()

    assert Game.objects.filter(pk=recent_game.pk).exists()
    assert Team.objects.filter(game=recent_game).count() == 2
    assert Player.objects.filter(game=recent_game).count() == 4
    assert Hand.objects.filter(game=recent_game).count() == 2
    assert Trick.objects.filter(hand__game=recent_game).count() == 4
    assert Bid.objects.filter(hand__game=recent_game).count() == 4
    assert Play.objects.filter(trick__hand__game=recent_game).count() == 16
    assert Hand.objects.filter(game=recent_game, high_bid__isnull=False).count() == 2
    assert Player.objects.filter(game=recent_game, plays_after__isnull=False).count() == 3

    recent_game.refresh_from_db()
    assert recent_game.next_dealer_id == recent_data["players"][0].id
