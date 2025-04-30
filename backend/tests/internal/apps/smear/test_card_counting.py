import pytest

from apps.smear import card_counting
from apps.smear.cards import Card
from apps.smear.models import Play
from tests.internal.apps.smear.factories import GameFactory, PlayerFactory, TeamFactory, TrickFactory


@pytest.mark.django_db
def test_highest_card_still_out_offsuit():
    trick = TrickFactory()
    for card in ("AH", "KH"):
        Play.objects.create(trick=trick, card=card)

    highest_card = card_counting.highest_card_still_out(trick.hand, "hearts")

    assert highest_card.representation == "QH"


@pytest.mark.django_db
def test_highest_card_still_out_trump():
    trick = TrickFactory(hand__trump="hearts")
    for card in ("AH", "KH", "QH", "JH", "JD"):
        Play.objects.create(trick=trick, card=card)

    highest_card = card_counting.highest_card_still_out(trick.hand, "hearts")

    assert highest_card.representation == "0H"


@pytest.mark.django_db
@pytest.mark.parametrize("jick_played", (False, True))
def test_jack_or_jick_still_out(jick_played):
    trick = TrickFactory(hand__trump="hearts")
    Play.objects.create(trick=trick, card="JH")
    if jick_played:
        Play.objects.create(trick=trick, card="JD")

    still_out = card_counting.jack_or_jick_still_out(trick.hand)

    assert still_out is not jick_played


@pytest.mark.django_db
def test_is_teammate_taking_trick_ace_trump():
    game = GameFactory(num_players=4, num_teams=2)
    team1 = TeamFactory(game=game)
    team2 = TeamFactory(game=game)
    p1 = PlayerFactory(user=game.owner, game=game, team=team1, seat=1)
    p2 = PlayerFactory(game=game, team=team2, seat=2)
    p3 = PlayerFactory(game=game, team=team1, seat=3)
    PlayerFactory(game=game, team=team2, seat=4)
    game.set_plays_after()

    trick = TrickFactory(hand__game=game, hand__trump="hearts")
    Play.objects.create(trick=trick, card="AH", player=p1)
    Play.objects.create(trick=trick, card="0H", player=p2)
    current_plays = trick.plays.all()

    is_taking = card_counting.is_teammate_taking_trick(trick.hand, trick, p3, current_plays)

    assert is_taking is True


@pytest.mark.django_db
def test_is_teammate_taking_trick_winning_with_just_me_left():
    game = GameFactory(num_players=4, num_teams=2)
    team1 = TeamFactory(game=game)
    team2 = TeamFactory(game=game)
    p1 = PlayerFactory(user=game.owner, game=game, team=team1, seat=1)
    p2 = PlayerFactory(game=game, team=team2, seat=2)
    p3 = PlayerFactory(game=game, team=team1, seat=3)
    p4 = PlayerFactory(game=game, team=team2, seat=4)
    game.set_plays_after()

    trick = TrickFactory(hand__game=game, hand__trump="hearts")
    Play.objects.create(trick=trick, card="0H", player=p1)
    Play.objects.create(trick=trick, card="JH", player=p2)
    Play.objects.create(trick=trick, card="3H", player=p3)
    current_plays = trick.plays.all()

    is_taking = card_counting.is_teammate_taking_trick(trick.hand, trick, p4, current_plays)

    assert is_taking is True


@pytest.mark.django_db
def test_safe_to_play_with_jack_and_everyone_left_out_of_trump():
    game = GameFactory(num_players=4, num_teams=2)
    team1 = TeamFactory(game=game)
    team2 = TeamFactory(game=game)
    p1 = PlayerFactory(user=game.owner, game=game, team=team1, seat=1)
    p2 = PlayerFactory(game=game, team=team2, seat=2)
    p3 = PlayerFactory(game=game, team=team1, seat=3)
    PlayerFactory(game=game, team=team2, seat=4)
    game.set_plays_after()

    trick = TrickFactory(hand__game=game, hand__trump="hearts")
    trick.hand.players_out_of_suits["hearts"] = [str(p3.id)]

    Play.objects.create(trick=trick, card="0H", player=p1)
    current_plays = trick.plays.all()

    safe = card_counting.safe_to_play(trick.hand, trick, p2, Card(representation="JH"), current_plays)

    assert safe is True
