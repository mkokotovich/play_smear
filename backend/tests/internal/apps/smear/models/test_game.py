import pytest
from rest_framework.exceptions import ValidationError

from apps.smear.models import Game, Player
from tests.internal.apps.smear.factories import GameFactory, PlayerFactory
from tests.internal.apps.user.factories import UserFactory


@pytest.mark.django_db()
def test_Game_start_fails_if_not_enough_players():
    num_players = 6
    game = GameFactory(num_players=num_players)
    [Player.objects.create(game=game, user=UserFactory()) for i in range(0, num_players - 1)]

    with pytest.raises(ValidationError):
        game.start_game()


@pytest.mark.django_db()
def test_Game_start_game(mocker):
    num_players = 6
    game = GameFactory(num_players=num_players)
    [Player.objects.create(game=game, user=UserFactory(), seat=i) for i in range(0, num_players)]
    mock_set_seats = mocker.patch.object(game, "set_seats")
    mock_advance_game = mocker.patch.object(game, "advance_game")

    game.start_game()

    assert game.state == Game.NEW_HAND
    assert mock_set_seats.mock_calls == [
        mocker.call(),
    ]
    assert mock_advance_game.mock_calls == [
        mocker.call(),
    ]


@pytest.mark.django_db()
@pytest.mark.parametrize("num_players", [2, 4, 6, 8])
@pytest.mark.parametrize("num_teams", [0, 2, 3, 4])
def test_Game_set_seats(mocker, num_teams, num_players):
    if num_teams != 0 and num_players % num_teams != 0:
        pytest.skip(f"Uneven number of player ({num_players}) for teams ({num_teams})")

    game = GameFactory(num_players=num_players, num_teams=num_teams)
    game.create_initial_teams()
    teams = list(game.teams.all())
    players = [Player.objects.create(game=game, user=UserFactory()) for i in range(0, num_players)]
    if num_teams != 0:
        for player_num, player in enumerate(players):
            player.team = teams[player_num % num_teams]
            player.save()

    game.set_seats()

    for team_num, team in enumerate(teams):
        for player_num, player in enumerate(team.members.all()):
            db_player = Player.objects.get(id=player.id)
            assert db_player in players
            assert db_player.game == game
            assert db_player.seat == team_num + player_num * num_teams

    if num_teams == 0:
        game_players = Player.objects.filter(game=game).order_by("seat")
        for player_num, db_player in enumerate(game_players):
            assert db_player in players
            assert db_player.game == game
            assert db_player.seat == player_num


@pytest.mark.django_db()
@pytest.mark.parametrize("num_players", [2, 4, 6, 8])
@pytest.mark.parametrize("num_teams", [2, 3, 4])
def test_Game_autofill_teams(mocker, num_teams, num_players):
    if num_teams != 0 and num_players % num_teams != 0:
        pytest.skip(f"Uneven number of player ({num_players}) for teams ({num_teams})")

    game = GameFactory(num_players=num_players, num_teams=num_teams)
    game.create_initial_teams()
    players = [Player.objects.create(game=game, user=UserFactory()) for i in range(0, num_players)]

    game.autofill_teams()

    teams = list(game.teams.all())
    total_members = 0
    for team_num, team in enumerate(teams):
        for player_num, player in enumerate(team.members.all()):
            db_player = Player.objects.get(id=player.id)
            assert db_player in players
            assert db_player.game == game
            total_members += 1
    assert total_members == game.num_players


@pytest.mark.django_db
def test_Game_next_player(mocker):
    num_players = 6
    game = GameFactory(num_players=num_players, num_teams=2)
    game.create_initial_teams()
    players = [Player.objects.create(game=game, user=UserFactory()) for i in range(0, num_players)]

    game.autofill_teams()
    game.set_seats()
    game.set_plays_after()

    for player in players:
        player.refresh_from_db()

    in_order = list(Player.objects.filter(game=game).order_by("seat"))

    ids = []
    for idx, p in enumerate(in_order):
        assert p.seat == idx
        ids.append(p.id)

    game.refresh_from_db()
    assert game.player_ids_in_order == ids


# Set the "repeat" range() to a large number to test computer logic more thoroughly
@pytest.mark.django_db()
@pytest.mark.parametrize("repeat", range(1))
def test_Game_play_through_whole_game(mocker, repeat):
    num_players = 6
    num_teams = 3
    game = GameFactory(num_players=num_players, num_teams=num_teams, score_to_play_to=5)
    game.create_initial_teams()
    PlayerFactory.create_batch(num_players, game=game, is_computer=True)
    game.autofill_teams()
    game.state = Game.STARTING
    game.save()

    game.start_game()

    assert game.state == Game.GAME_OVER


@pytest.mark.django_db()
@pytest.mark.skip("queries change based on cards and bids, enable this for debugging")
def test_Game_start_game_queries(mocker, django_assert_num_queries):
    num_players = 6
    num_teams = 3
    game = GameFactory(num_players=num_players, num_teams=num_teams, score_to_play_to=5)
    game.create_initial_teams()
    PlayerFactory(game=game, is_computer=False)
    PlayerFactory.create_batch(num_players - 1, game=game, is_computer=True)

    with django_assert_num_queries(0):
        game.autofill_teams()
        game.state = Game.STARTING
        game.start_game()

    assert game.state == Game.GAME_OVER
